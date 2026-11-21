"""
Real-Time Fraud Detection Engine for RINGTRACE AI.
Processes incoming transactions from Bank A, Bank B, and Bank C in low-latency runtime,
updates in-memory account states, extracts real-time features, predicts fraud probability,
assigns multi-tier risk levels (Low, Medium, High), and logs detection history.
"""

from typing import Dict, List, Any, Optional, Tuple, Generator
import json
import time
from datetime import datetime, timezone
from collections import deque
import joblib
import numpy as np
import pandas as pd
from xgboost import XGBClassifier

import config
from src.integration.db import DatabaseManager


class RealtimeFraudDetector:
    """
    Stateful real-time fraud detection engine for continuous multi-bank transaction streams.
    Processes transactions in < 10ms with dynamic feature updating and risk tiering.
    """

    OFF_HOURS_SET = {23, 0, 1, 2, 3, 4, 5}

    def __init__(
        self,
        model_type: Optional[str] = None,
        db_manager: Optional[DatabaseManager] = None,
    ):
        self.db = db_manager or DatabaseManager()
        self.metadata_path = config.MODELS_DIR / "model_metadata.json"

        # Load metadata and feature columns
        with open(self.metadata_path, "r") as f:
            self.metadata = json.load(f)
            self.feature_names: List[str] = self.metadata["feature_names"]
            self.optimal_threshold: float = float(self.metadata.get("optimal_threshold", 0.75))
            champ = self.metadata.get("champion_model", "Random Forest")
            self.model_type = (model_type or champ).lower()

        # Load model weights
        if "random" in self.model_type or "forest" in self.model_type:
            rf_path = config.MODELS_DIR / "random_forest_model.joblib"
            self.model = joblib.load(rf_path)
            self.active_model_name = "Random Forest"
        else:
            xgb_path = config.MODELS_DIR / "xgboost_model.json"
            self.model = XGBClassifier()
            self.model.load_model(str(xgb_path))
            self.active_model_name = "XGBoost"

        # In-memory fast state caches
        self.account_profiles: Dict[str, Dict[str, Any]] = {}
        self.account_sliding_windows: Dict[str, deque] = {}
        self.account_last_seen: Dict[str, float] = {}
        self.account_last_received: Dict[str, float] = {}
        self.detection_history: List[Dict[str, Any]] = []

        # Bootstrap state from features.csv if present
        self._bootstrap_state()

    def _bootstrap_state(self):
        """Preloads known account topologies into memory for zero-cold-start inference."""
        feat_path = config.PROCESSED_DATA_DIR / "features.csv"
        if feat_path.exists():
            df_feat = pd.read_csv(feat_path)
            for _, row in df_feat.iterrows():
                acc_id = str(row["account_id"])
                self.account_profiles[acc_id] = {
                    "account_age_days": float(row.get("account_age_days", 30)),
                    "in_degree": float(row.get("in_degree", 0)),
                    "out_degree": float(row.get("out_degree", 0)),
                    "fan_in_distinct": float(row.get("fan_in_distinct", 0)),
                    "fan_out_distinct": float(row.get("fan_out_distinct", 0)),
                    "tx_frequency_total": float(row.get("tx_frequency_total", 0)),
                    "total_amount_in": float(row.get("total_amount_in", 0.0)),
                    "total_amount_out": float(row.get("total_amount_out", 0.0)),
                    "avg_amount_in": float(row.get("avg_amount_in", 0.0)),
                    "avg_amount_out": float(row.get("avg_amount_out", 0.0)),
                    "avg_amount_total": float(row.get("avg_amount_total", 0.0)),
                    "high_value_tx_count": float(row.get("high_value_tx_count", 0)),
                    "high_value_ratio": float(row.get("high_value_ratio", 0.0)),
                    "off_hours_tx_ratio": float(row.get("off_hours_tx_ratio", 0.0)),
                    "pass_through_ratio": float(row.get("pass_through_ratio", 0.0)),
                    "net_flow_ratio": float(row.get("net_flow_ratio", 0.0)),
                    "turnover_rate": float(row.get("turnover_rate", 0.0)),
                    "avg_turnaround_time_sec": float(row.get("avg_turnaround_time_sec", 604800.0)),
                    "min_turnaround_time_sec": float(row.get("min_turnaround_time_sec", 604800.0)),
                    "min_time_gap_sec": float(row.get("min_time_gap_sec", 604800.0)),
                    "velocity_1h_max": float(row.get("velocity_1h_max", 0)),
                    "velocity_24h_max": float(row.get("velocity_24h_max", 0)),
                    "velocity_score": float(row.get("velocity_score", 0.0)),
                    "cross_bank_tx_ratio": float(row.get("cross_bank_tx_ratio", 0.0)),
                    "pagerank": float(row.get("pagerank", 0.001)),
                    "clustering_coeff": float(row.get("clustering_coeff", 0.0)),
                    "behavioral_risk_score": float(row.get("behavioral_risk_score", 0.1)),
                    "profile_type": str(row.get("profile_type", "REGULAR_P2P")),
                    "bank_id": str(row.get("bank_id", "BANK_A")),
                }
                self.account_sliding_windows[acc_id] = deque(maxlen=200)

    def process_transaction(self, tx: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processes a single transaction event in real time:
        1. Extracts behavioral and temporal features.
        2. Evaluates model fraud probability.
        3. Assigns risk level (Low, Medium, High) and status (Normal, Review Required, Suspicious).
        4. Synthesizes trigger reason codes.
        5. Logs detection to SQLite/PostgreSQL audit database.
        """
        start_time = time.perf_counter()

        tx_id = str(tx.get("transaction_id", f"TX_RT_{int(time.time() * 1000)}"))
        sender = str(tx.get("sender_account", "UNKNOWN_SENDER")).upper()
        receiver = str(tx.get("receiver_account", "UNKNOWN_RECEIVER")).upper()
        sender_bank = str(tx.get("sender_bank", "BANK_A")).upper()
        receiver_bank = str(tx.get("receiver_bank", "BANK_B")).upper()
        amount = float(tx.get("amount", 0.0))
        ts_str = str(tx.get("timestamp", datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")))

        # Parse timestamp to unix seconds
        try:
            ts_dt = pd.to_datetime(ts_str)
            ts_sec = ts_dt.timestamp()
            hour = ts_dt.hour
        except Exception:
            ts_sec = time.time()
            hour = 12

        # 1. Feature extraction in real time
        is_off_hours = int(hour in self.OFF_HOURS_SET)
        is_cross_bank = int(sender_bank != receiver_bank)
        is_high_value = int(amount >= 50000.0)

        # Retrieve or initialize sender profile state
        if sender not in self.account_profiles:
            self.account_profiles[sender] = {
                "account_age_days": 180.0,
                "in_degree": 12.0,
                "out_degree": 10.0,
                "fan_in_distinct": 6.0,
                "fan_out_distinct": 5.0,
                "tx_frequency_total": 22.0,
                "total_amount_in": 35000.0,
                "total_amount_out": 28000.0,
                "avg_amount_in": 2900.0,
                "avg_amount_out": 2800.0,
                "avg_amount_total": 2850.0,
                "high_value_tx_count": 0.0,
                "high_value_ratio": 0.0,
                "off_hours_tx_ratio": 0.0,
                "pass_through_ratio": 0.8,
                "net_flow_ratio": -0.1,
                "turnover_rate": 0.5,
                "avg_turnaround_time_sec": 604800.0,
                "min_turnaround_time_sec": 604800.0,
                "min_time_gap_sec": 604800.0,
                "velocity_1h_max": 0.0,
                "velocity_24h_max": 0.0,
                "velocity_score": 0.0,
                "cross_bank_tx_ratio": 0.0,
                "pagerank": 0.001,
                "clustering_coeff": 0.0,
                "behavioral_risk_score": 0.0,
                "profile_type": "REGULAR_P2P",
                "bank_id": sender_bank,
            }
            self.account_sliding_windows[sender] = deque(maxlen=200)

        sender_state = self.account_profiles[sender]

        # Calculate time gap
        if sender in self.account_last_seen:
            time_gap_sec = max(0.0, ts_sec - self.account_last_seen[sender])
        else:
            time_gap_sec = 604800.0

        # Calculate turnaround time if sender previously received funds
        if sender in self.account_last_received:
            turnaround_sec = max(0.0, ts_sec - self.account_last_received[sender])
            sender_state["min_turnaround_time_sec"] = min(sender_state["min_turnaround_time_sec"], turnaround_sec)
            sender_state["avg_turnaround_time_sec"] = turnaround_sec
        else:
            turnaround_sec = sender_state["min_turnaround_time_sec"]

        # Update sliding window for 1h and 24h velocity
        s_window = self.account_sliding_windows[sender]
        s_window.append(ts_sec)
        cutoff_24h = ts_sec - 86400.0
        cutoff_1h = ts_sec - 3600.0

        vel_24h = sum(1 for t in s_window if t >= cutoff_24h)
        vel_1h = sum(1 for t in s_window if t >= cutoff_1h)

        sender_state["velocity_1h_max"] = max(sender_state["velocity_1h_max"], vel_1h)
        sender_state["velocity_24h_max"] = max(sender_state["velocity_24h_max"], vel_24h)
        sender_state["velocity_score"] = float(np.clip(
            (sender_state["velocity_1h_max"] / 5.0) * 0.6 + (sender_state["velocity_24h_max"] / 20.0) * 0.4, 0.0, 1.0
        ))

        # Update flow totals for sender
        sender_state["out_degree"] += 1.0
        sender_state["tx_frequency_total"] += 1.0
        sender_state["total_amount_out"] += amount
        sender_state["avg_amount_out"] = sender_state["total_amount_out"] / sender_state["out_degree"]
        sender_state["pass_through_ratio"] = (sender_state["total_amount_out"] / sender_state["total_amount_in"]) if sender_state["total_amount_in"] > 0 else 0.0
        sender_state["min_time_gap_sec"] = min(sender_state["min_time_gap_sec"], time_gap_sec)

        # Update timestamps
        self.account_last_seen[sender] = ts_sec
        self.account_last_seen[receiver] = ts_sec
        self.account_last_received[receiver] = ts_sec

        # Update receiver profile if present or initialize
        if receiver not in self.account_profiles:
            self.account_profiles[receiver] = {
                "account_age_days": 180.0,
                "in_degree": 0.0,
                "out_degree": 0.0,
                "fan_in_distinct": 0.0,
                "fan_out_distinct": 0.0,
                "tx_frequency_total": 0.0,
                "total_amount_in": 0.0,
                "total_amount_out": 0.0,
                "avg_amount_in": 0.0,
                "avg_amount_out": 0.0,
                "avg_amount_total": 0.0,
                "high_value_tx_count": 0.0,
                "high_value_ratio": 0.0,
                "off_hours_tx_ratio": 0.0,
                "pass_through_ratio": 0.0,
                "net_flow_ratio": 0.0,
                "turnover_rate": 0.0,
                "avg_turnaround_time_sec": 604800.0,
                "min_turnaround_time_sec": 604800.0,
                "min_time_gap_sec": 604800.0,
                "velocity_1h_max": 0.0,
                "velocity_24h_max": 0.0,
                "velocity_score": 0.0,
                "cross_bank_tx_ratio": 0.0,
                "pagerank": 0.001,
                "clustering_coeff": 0.0,
                "behavioral_risk_score": 0.0,
                "profile_type": "REGULAR_P2P",
                "bank_id": receiver_bank,
            }
            self.account_sliding_windows[receiver] = deque(maxlen=200)

        recv_state = self.account_profiles[receiver]
        recv_state["in_degree"] += 1.0
        recv_state["fan_in_distinct"] += 1.0
        recv_state["tx_frequency_total"] += 1.0
        recv_state["total_amount_in"] += amount
        recv_state["avg_amount_in"] = recv_state["total_amount_in"] / recv_state["in_degree"]

        # 2. Vectorize features for model prediction
        vector = {}
        for feat in self.feature_names:
            if feat.startswith("profile_type_"):
                p_val = feat.replace("profile_type_", "")
                vector[feat] = 1.0 if sender_state.get("profile_type") == p_val else 0.0
            elif feat.startswith("bank_id_"):
                b_val = feat.replace("bank_id_", "")
                vector[feat] = 1.0 if sender_state.get("bank_id") == b_val else 0.0
            else:
                vector[feat] = float(sender_state.get(feat, 0.0))

        X_realtime = pd.DataFrame([vector])[self.feature_names]

        # 3. Model Inference
        probs = self.model.predict_proba(X_realtime)[0, 1]
        fraud_prob = float(np.clip(round(probs, 4), 0.0, 1.0))

        # 4. Reason Code Synthesis & Hybrid Rule Engine
        triggers = []
        if turnaround_sec <= 300.0:
            triggers.append("RAPID_BURST_FORWARDING")
        if vel_1h >= 3:
            triggers.append("HIGH_VELOCITY_SPIKE")
        if is_cross_bank and amount >= 30000.0:
            triggers.append("CROSS_BANK_HIGH_VALUE")
        if is_off_hours:
            triggers.append("NOCTURNAL_OFF_HOURS")
        if 0.85 <= sender_state["pass_through_ratio"] <= 1.15 and sender_state["total_amount_out"] >= 20000.0:
            triggers.append("HIGH_PASS_THROUGH_MULE_RATIO")

        # Hybrid Decision Logic: If clear composite mule ring indicators fire
        if ("RAPID_BURST_FORWARDING" in triggers and "NOCTURNAL_OFF_HOURS" in triggers) or (
            "RAPID_BURST_FORWARDING" in triggers and "HIGH_PASS_THROUGH_MULE_RATIO" in triggers
        ) or (
            "RAPID_BURST_FORWARDING" in triggers and "CROSS_BANK_HIGH_VALUE" in triggers
        ):
            fraud_prob = max(fraud_prob, 0.88)

        # 5. Multi-Tier Risk Categorization
        if fraud_prob >= 0.70:
            risk_level = "High"
            status = "Suspicious"
        elif fraud_prob >= 0.35:
            risk_level = "Medium"
            status = "Review Required"
        else:
            risk_level = "Low"
            status = "Normal"

        if not triggers and status != "Normal":
            triggers.append("ELEVATED_RISK_SCORE")

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        result = {
            "transaction_id": tx_id,
            "bank_id": sender_bank,
            "sender_account": sender,
            "receiver_account": receiver,
            "amount": round(amount, 2),
            "timestamp": ts_str,
            "fraud_probability": fraud_prob,
            "risk_level": risk_level,
            "status": status,
            "trigger_reasons": triggers,
            "latency_ms": round(elapsed_ms, 2),
            "model_used": self.active_model_name,
        }

        # 6. Log detection history and persist to database
        self.detection_history.append(result)
        self.db.save_realtime_log(result)

        return result

    def simulate_stream(
        self,
        transactions: List[Dict[str, Any]],
        delay_sec: float = 0.0,
        yield_results: bool = True,
    ) -> Generator[Dict[str, Any], None, None]:
        """Streams synthetic transactions through real-time detection pipeline."""
        for tx in transactions:
            res = self.process_transaction(tx)
            if delay_sec > 0:
                time.sleep(delay_sec)
            if yield_results:
                yield res

    def get_summary_stats(self) -> Dict[str, Any]:
        """Returns runtime performance statistics of real-time detector."""
        total = len(self.detection_history)
        if total == 0:
            return {"total_transactions": 0}

        high_count = sum(1 for d in self.detection_history if d["risk_level"] == "High")
        med_count = sum(1 for d in self.detection_history if d["risk_level"] == "Medium")
        low_count = sum(1 for d in self.detection_history if d["risk_level"] == "Low")
        avg_lat = float(np.mean([d["latency_ms"] for d in self.detection_history]))

        return {
            "total_processed": total,
            "high_risk_suspicious": high_count,
            "medium_risk_review": med_count,
            "low_risk_normal": low_count,
            "fraud_rate": round(high_count / total, 4),
            "avg_latency_ms": round(avg_lat, 2),
            "active_model": self.active_model_name,
        }
