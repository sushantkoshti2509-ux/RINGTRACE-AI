"""
RINGTRACE AI - Multi-Tier Risk Scoring and Prediction Engine.
Computes calibrated continuous risk probabilities for accounts and transactions,
assigns operational alert tiers (LOW, MEDIUM, HIGH), and supports both
champion XGBoost and baseline Random Forest models.
"""

from typing import Dict, Any, List, Optional
import json
from pathlib import Path
import joblib
import pandas as pd
import numpy as np
from xgboost import XGBClassifier

import config


class RiskPredictor:
    """Computes account-level and transaction-level risk scores and generates alerts."""

    def __init__(
        self,
        model_type: str = "xgboost",
        model_path: Optional[str] = None,
        metadata_path: Optional[str] = None,
    ):
        self.model_type = model_type.lower()
        self.metadata_path = metadata_path or str(config.MODELS_DIR / "model_metadata.json")

        with open(self.metadata_path, "r") as f:
            meta = json.load(f)
            self.feature_names: List[str] = meta["feature_names"]
            self.threshold: float = float(meta.get("optimal_threshold", config.DEFAULT_ALERT_THRESHOLD))

        if self.model_type == "random_forest":
            rf_path = model_path or str(config.MODELS_DIR / "random_forest_model.joblib")
            self.model = joblib.load(rf_path)
        else:
            xgb_path = model_path or str(config.MODELS_DIR / "xgboost_model.json")
            self.model = XGBClassifier()
            self.model.load_model(xgb_path)

    def predict_risk_scores(self, features_df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculates account-level risk scores for accounts in features_df.
        Returns a DataFrame with account_id, risk_score, alert_flag, and risk_tier.
        """
        df = features_df.copy()

        # One-hot encode categoricals to match model features
        df_encoded = pd.get_dummies(
            df,
            columns=config.CATEGORICAL_FEATURES,
            drop_first=False,
            dtype=float,
        )

        # Align with model feature columns
        for col in self.feature_names:
            if col not in df_encoded.columns:
                df_encoded[col] = 0.0

        X = df_encoded[self.feature_names].fillna(0.0)

        # Compute risk probabilities
        probs = self.model.predict_proba(X)[:, 1]
        alerts = (probs >= self.threshold).astype(int)

        def assign_tier(score: float) -> str:
            if score >= 0.70:
                return "HIGH"
            elif score >= 0.35:
                return "MEDIUM"
            else:
                return "LOW"

        tiers = [assign_tier(s) for s in probs]

        results_df = pd.DataFrame({
            "account_id": df["account_id"].values,
            "bank_id": df["bank_id"].values,
            "profile_type": df["profile_type"].values,
            "risk_score": np.round(probs, 4),
            "alert_flag": alerts,
            "risk_tier": tiers,
            "is_mule_ground_truth": df[config.TARGET_COLUMN].values if config.TARGET_COLUMN in df.columns else None,
            "ring_id": df["ring_id"].values if "ring_id" in df.columns else "NONE",
            "ring_role": df["ring_role"].values if "ring_role" in df.columns else "UNKNOWN",
        })

        results_df = results_df.sort_values("risk_score", ascending=False).reset_index(drop=True)
        return results_df

    def predict_transaction_risk_scores(
        self,
        transactions_df: pd.DataFrame,
        account_risk_df: Optional[pd.DataFrame] = None,
    ) -> pd.DataFrame:
        """
        Calculates transaction-level fraud risk scores by synthesizing
        sender account risk, receiver account risk, and transaction behavioral indicators.
        """
        df_tx = transactions_df.copy()

        # Build account risk lookup dictionary
        acc_risk_map = {}
        if account_risk_df is not None and not account_risk_df.empty:
            acc_risk_map = dict(zip(account_risk_df["account_id"], account_risk_df["risk_score"]))

        sender_scores = df_tx["sender_account"].map(lambda a: acc_risk_map.get(a, 0.10)).values
        receiver_scores = df_tx["receiver_account"].map(lambda a: acc_risk_map.get(a, 0.10)).values

        # Behavioral heuristics from transaction features
        tx_ind = df_tx.get("transaction_risk_indicator", pd.Series(0.1, index=df_tx.index)).values
        vel_score = df_tx.get("velocity_score", pd.Series(0.1, index=df_tx.index)).values
        is_cross = df_tx.get("is_cross_bank", pd.Series(0, index=df_tx.index)).values
        is_off = df_tx.get("is_off_hours", pd.Series(0, index=df_tx.index)).values

        # Multi-factor transaction risk synthesis:
        # 45% sender account network risk + 25% receiver account network risk + 30% transaction pattern
        tx_pattern_factor = 0.4 * tx_ind + 0.3 * vel_score + 0.15 * is_cross + 0.15 * is_off
        combined_scores = 0.45 * sender_scores + 0.25 * receiver_scores + 0.30 * tx_pattern_factor
        combined_scores = np.clip(np.round(combined_scores, 4), 0.0, 1.0)

        # Flagged transaction status
        tx_alerts = (combined_scores >= self.threshold).astype(int)

        def assign_tx_tier(score: float) -> str:
            if score >= 0.70:
                return "CRITICAL_FRAUD_RISK"
            elif score >= 0.40:
                return "ELEVATED_SUSPICION"
            else:
                return "STANDARD_LEGITIMATE"

        df_tx_scored = df_tx.copy()
        df_tx_scored["transaction_risk_score"] = combined_scores
        df_tx_scored["fraud_alert_flag"] = tx_alerts
        df_tx_scored["risk_category"] = [assign_tx_tier(s) for s in combined_scores]

        # Save to processed directory if path exists
        config.PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
        df_tx_scored.to_csv(config.PROCESSED_DATA_DIR / "transaction_risk_scores.csv", index=False)
        df_tx_scored.to_json(config.PROCESSED_DATA_DIR / "transaction_risk_scores.json", orient="records", indent=2)

        return df_tx_scored
