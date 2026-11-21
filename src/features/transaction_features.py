"""
Transaction-Level Feature Engineering Engine for RINGTRACE AI.
Enriches raw transaction records with fine-grained temporal gaps, off-hours flags,
relative high-value deviations, cross-bank identifiers, and burst velocity scores.
"""

from typing import Dict, List, Any, Optional
import numpy as np
import pandas as pd


class TransactionFeatureEngine:
    """Computes fine-grained behavioral features on individual transaction rows."""

    HIGH_VALUE_ABSOLUTE_THRESHOLD = 50000.0  # INR 50,000
    OFF_HOURS_SET = {23, 0, 1, 2, 3, 4, 5}  # 11:00 PM to 5:59 AM
    RAPID_BURST_GAP_SEC = 300.0              # 5 minutes

    def __init__(self, high_value_threshold: float = HIGH_VALUE_ABSOLUTE_THRESHOLD):
        self.high_value_threshold = high_value_threshold

    def extract_transaction_features(self, transactions_df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculates transaction-level features across all records:
        1. time_gap_seconds: Time since previous transaction by same sender.
        2. is_off_hours: Flag for nocturnal / unusual transaction timing.
        3. is_high_value: Flag for unusually large transactions.
        4. is_cross_bank: Cross-bank transfer flag.
        5. sender_tx_frequency_24h: Rolling 24-hour transaction frequency of sender.
        6. sender_avg_amount_historical: Expanding average amount sent by sender.
        7. amount_to_avg_ratio: Current amount relative to sender historical average.
        8. rapid_burst_flag: Flag indicating transaction is within rapid burst (< 5m).
        9. velocity_score: Normalized rapid-activity velocity score.
        10. transaction_risk_indicator: Multi-factor composite heuristic risk indicator.
        """
        df = transactions_df.copy()

        # Parse timestamp
        df["timestamp_dt"] = pd.to_datetime(df["timestamp"])
        df = df.sort_values("timestamp_dt").reset_index(drop=True)

        # 1. Temporal & Off-Hours analysis
        hours = df["timestamp_dt"].dt.hour
        df["is_off_hours"] = hours.isin(self.OFF_HOURS_SET).astype(int)

        # 2. Cross-bank flag
        if "is_cross_bank" not in df.columns:
            df["is_cross_bank"] = (df["sender_bank"] != df["receiver_bank"]).astype(int)
        else:
            df["is_cross_bank"] = df["is_cross_bank"].astype(int)

        # 3. High-value absolute flag
        df["is_high_value"] = (df["amount"] >= self.high_value_threshold).astype(int)

        # 4. Sequential time gap tracking and rolling sender metrics
        # Pre-allocate feature columns
        df["time_gap_seconds"] = 86400.0 * 7  # default 7 days in seconds
        df["sender_avg_amount_historical"] = df["amount"]
        df["sender_tx_frequency_24h"] = 1

        # Track account last-activity timestamp (inflow or outflow) to capture rapid pass-through gaps
        account_last_time: Dict[str, Any] = {}
        time_gaps = []

        for idx, row in df.iterrows():
            sender = row["sender_account"]
            curr_time = row["timestamp_dt"]

            if sender in account_last_time:
                delta_sec = float((curr_time - account_last_time[sender]) / np.timedelta64(1, "s"))
                time_gaps.append(max(0.0, delta_sec))
            else:
                time_gaps.append(86400.0 * 7)

            # Record activity for both sender and receiver to capture pass-through latency
            account_last_time[sender] = curr_time
            account_last_time[row["receiver_account"]] = curr_time

        df["time_gap_seconds"] = time_gaps

        # Group by sender for expanding average amount and rolling 24h frequency
        grouped = df.groupby("sender_account", sort=False)
        for sender, group in grouped:
            indices = group.index
            times = group["timestamp_dt"].values
            amounts = group["amount"].values

            # Expanding historical average amount
            expanding_mean = pd.Series(amounts).expanding().mean().values
            df.loc[indices, "sender_avg_amount_historical"] = np.round(expanding_mean, 2)

            # Rolling 24-hour count per sender
            ts_series = pd.Series(1, index=pd.DatetimeIndex(times))
            rolling_counts = ts_series.rolling("24h").count().values
            df.loc[indices, "sender_tx_frequency_24h"] = rolling_counts.astype(int)

        # 5. Relative Amount Ratio
        denom = df["sender_avg_amount_historical"].replace(0.0, 1.0)
        df["amount_to_avg_ratio"] = np.round(df["amount"] / denom, 2)

        # Update high-value flag if amount is > 2.5x historical average and > 10,000
        relative_high = (df["amount_to_avg_ratio"] >= 2.5) & (df["amount"] >= 10000.0)
        df["is_high_value"] = (df["is_high_value"] | relative_high).astype(int)

        # 6. Rapid Burst Flag (< 5 minutes from previous transaction by same sender)
        df["rapid_burst_flag"] = (df["time_gap_seconds"] <= self.RAPID_BURST_GAP_SEC).astype(int)

        # 7. Velocity Score (combines frequency and short time gap into a 0.0 - 1.0 scale)
        freq_norm = np.clip(df["sender_tx_frequency_24h"] / 10.0, 0.0, 1.0)
        gap_factor = np.exp(-df["time_gap_seconds"] / 1800.0)  # decays over 30 mins
        df["velocity_score"] = np.round(0.5 * freq_norm + 0.5 * gap_factor, 4)

        # 8. Composite Transaction Risk Indicator (0.0 to 1.0 rule-based heuristic)
        # Weights: Rapid burst (0.30) + Cross bank (0.25) + High value (0.25) + Off hours (0.20)
        risk_ind = (
            0.30 * df["rapid_burst_flag"]
            + 0.25 * df["is_cross_bank"]
            + 0.25 * df["is_high_value"]
            + 0.20 * df["is_off_hours"]
        )
        df["transaction_risk_indicator"] = np.round(risk_ind, 4)

        # Cleanup intermediate column
        df = df.drop(columns=["timestamp_dt"])
        return df
