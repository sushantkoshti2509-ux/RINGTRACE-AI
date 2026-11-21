"""
RINGTRACE AI - Account Risk Scoring and Prediction Engine.
Loads trained XGBoost model, calculates risk probabilities, applies calibrated
alert thresholds, and categorizes accounts into operational risk tiers.
"""

from typing import Dict, Any, List
import json
import pandas as pd
import numpy as np
from xgboost import XGBClassifier

import config


class RiskPredictor:
    """Computes account-level risk scores and generates alerts."""

    def __init__(self, model_path: str = None, metadata_path: str = None):
        self.model_path = model_path or str(config.MODELS_DIR / "xgboost_model.json")
        self.metadata_path = metadata_path or str(config.MODELS_DIR / "model_metadata.json")
        self.model = XGBClassifier()
        self.model.load_model(self.model_path)

        with open(self.metadata_path, "r") as f:
            meta = json.load(f)
            self.feature_names: List[str] = meta["feature_names"]
            self.threshold: float = float(meta.get("optimal_threshold", config.DEFAULT_ALERT_THRESHOLD))

    def predict_risk_scores(self, features_df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculates risk scores for accounts in features_df.
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

        # Compute probabilities
        probs = self.model.predict_proba(X)[:, 1]
        
        # Risk classification
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
