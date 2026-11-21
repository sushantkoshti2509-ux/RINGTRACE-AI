"""
Feature 2: Explainable AI (XAI) - Model SHAP Explainer.
Computes TreeExplainer Shapley additive feature attributions for trained models
(Random Forest champion and XGBoost), isolating exact numerical risk contributions.
"""

from typing import Dict, Any, List, Optional
import json
import joblib
from pathlib import Path
import numpy as np
import pandas as pd
import shap

import config


class ModelSHAPExplainer:
    """Calculates feature-level SHAP attributions for account and transaction risk scoring."""

    def __init__(self, model: Optional[Any] = None, feature_names: Optional[List[str]] = None):
        if model is None:
            rf_path = config.MODELS_DIR / "random_forest_model.joblib"
            xgb_path = config.MODELS_DIR / "xgboost_model.json"

            if rf_path.exists():
                self.model = joblib.load(rf_path)
            elif xgb_path.exists():
                from xgboost import XGBClassifier
                self.model = XGBClassifier()
                self.model.load_model(str(xgb_path))
            else:
                self.model = None
        else:
            self.model = model

        # Load feature metadata
        meta_path = config.MODELS_DIR / "model_metadata.json"
        if feature_names:
            self.feature_names = feature_names
        elif meta_path.exists():
            with open(meta_path, "r") as f:
                meta = json.load(f)
                self.feature_names = meta.get("feature_names", [])
        else:
            self.feature_names = []

        # Initialize SHAP TreeExplainer
        if self.model is not None:
            self.explainer = shap.TreeExplainer(self.model)
        else:
            self.explainer = None

    def explain_account(
        self,
        account_features: pd.Series,
        top_k: int = 6,
    ) -> Dict[str, Any]:
        """
        Computes SHAP feature importance for a single account row.
        Returns top risk-increasing and risk-decreasing features.
        """
        if self.explainer is None:
            return {"error": "Model not loaded", "top_drivers": []}

        # Vectorize features
        row_dict = {}
        for feat in self.feature_names:
            row_dict[feat] = float(account_features.get(feat, 0.0))

        X_df = pd.DataFrame([row_dict])[self.feature_names]

        # Calculate SHAP values
        raw_shap = self.explainer.shap_values(X_df)

        # Handle different SHAP output formats (binary classification: positive class values)
        if isinstance(raw_shap, list) and len(raw_shap) >= 2:
            vals = raw_shap[1][0]
        elif isinstance(raw_shap, np.ndarray) and raw_shap.ndim == 3:
            vals = raw_shap[0, :, 1]
        elif isinstance(raw_shap, np.ndarray) and raw_shap.ndim == 2:
            vals = raw_shap[0]
        else:
            vals = np.array(raw_shap).flatten()

        # Expected base value
        if hasattr(self.explainer, "expected_value"):
            exp_val = self.explainer.expected_value
            base_val = float(exp_val[1] if isinstance(exp_val, (list, np.ndarray)) else exp_val)
        else:
            base_val = 0.5

        contributions = []
        for feat_name, s_val, actual_val in zip(self.feature_names, vals, X_df.iloc[0]):
            contributions.append({
                "feature": feat_name,
                "shap_value": round(float(s_val), 4),
                "actual_value": round(float(actual_val), 4),
                "direction": "INCREASES_RISK" if s_val > 0 else "DECREASES_RISK",
            })

        # Sort by absolute impact
        contributions.sort(key=lambda x: abs(x["shap_value"]), reverse=True)

        return {
            "base_value": round(base_val, 4),
            "top_drivers": contributions[:top_k],
            "all_contributions": contributions,
        }
