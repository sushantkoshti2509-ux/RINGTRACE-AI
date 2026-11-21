"""
RINGTRACE AI - SHAP Explainability Engine.
Calculates Shapley additive feature attributions for XGBoost model predictions
to reveal exact risk drivers behind flagged suspicious accounts.
"""

from typing import Dict, Any, List, Optional
import json
import numpy as np
import pandas as pd
from xgboost import XGBClassifier
import shap

import config


class ExplainabilityEngine:
    """Computes SHAP feature importance and local explanations for accounts."""

    def __init__(self, model: Optional[XGBClassifier] = None, metadata_path: str = None):
        self.metadata_path = metadata_path or str(config.MODELS_DIR / "model_metadata.json")
        
        if model is None:
            self.model = XGBClassifier()
            self.model.load_model(str(config.MODELS_DIR / "xgboost_model.json"))
        else:
            self.model = model

        with open(self.metadata_path, "r") as f:
            meta = json.load(f)
            self.feature_names: List[str] = meta["feature_names"]

        # Initialize TreeExplainer
        self.explainer = shap.TreeExplainer(self.model)

    def explain_account(
        self,
        account_features: pd.Series,
        top_k: int = 5,
    ) -> Dict[str, Any]:
        """
        Computes SHAP values for a single account.
        Returns top positive and negative contributing features.
        """
        # Ensure row has all required columns
        row_dict = {}
        for col in self.feature_names:
            row_dict[col] = float(account_features.get(col, 0.0))

        row_df = pd.DataFrame([row_dict], columns=self.feature_names)
        
        # Calculate SHAP values
        shap_values = self.explainer.shap_values(row_df)
        
        # If binary classification returns list or 2D array
        if isinstance(shap_values, list):
            vals = shap_values[1][0]
        elif len(shap_values.shape) == 2:
            vals = shap_values[0]
        else:
            vals = shap_values

        base_val = float(self.explainer.expected_value) if not isinstance(self.explainer.expected_value, list) else float(self.explainer.expected_value[1])

        contributions = []
        for feat_name, s_val, actual_val in zip(self.feature_names, vals, row_df.iloc[0]):
            contributions.append({
                "feature": feat_name,
                "shap_value": round(float(s_val), 4),
                "actual_value": round(float(actual_val), 4),
                "direction": "INCREASES_RISK" if s_val > 0 else "DECREASES_RISK",
            })

        # Sort by magnitude of SHAP contribution
        contributions.sort(key=lambda x: abs(x["shap_value"]), reverse=True)

        return {
            "base_value": round(base_val, 4),
            "top_drivers": contributions[:top_k],
            "all_contributions": contributions,
        }

    def explain_global_importance(self, X_sample: pd.DataFrame) -> List[Dict[str, Any]]:
        """Computes global feature importance across a sample of accounts."""
        X_aligned = pd.DataFrame(0.0, index=X_sample.index, columns=self.feature_names)
        for col in self.feature_names:
            if col in X_sample.columns:
                X_aligned[col] = X_sample[col].astype(float)

        shap_vals = self.explainer.shap_values(X_aligned)
        if isinstance(shap_vals, list):
            vals = shap_vals[1]
        else:
            vals = shap_vals

        mean_abs_shap = np.mean(np.abs(vals), axis=0)
        
        importance_list = [
            {"feature": feat, "mean_abs_shap": round(float(score), 4)}
            for feat, score in zip(self.feature_names, mean_abs_shap)
        ]
        importance_list.sort(key=lambda x: x["mean_abs_shap"], reverse=True)
        return importance_list
