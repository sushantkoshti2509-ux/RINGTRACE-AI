"""
RINGTRACE AI - XGBoost Model Training Pipeline.
Implements group-aware data splitting by ring_id, class imbalance mitigation
via scale_pos_weight, and threshold calibration for mule account detection.
"""

from typing import Tuple, Dict, Any, List
import json
import numpy as np
import pandas as pd
from sklearn.model_selection import GroupShuffleSplit
from sklearn.metrics import precision_recall_curve, f1_score
from xgboost import XGBClassifier

import config


class ModelTrainer:
    """Trains and calibrates XGBoost classifier for account-level mule detection."""

    def __init__(self, params: Dict[str, Any] = None):
        self.params = params or config.XGBOOST_PARAMS.copy()
        self.feature_columns: List[str] = []
        self.optimal_threshold: float = config.DEFAULT_ALERT_THRESHOLD

    def prepare_data(
        self,
        features_df: pd.DataFrame,
    ) -> Tuple[pd.DataFrame, pd.Series, pd.Series]:
        """
        Prepares features (X), labels (y), and grouping vector (groups)
        to prevent data leakage across train and test splits.
        """
        df = features_df.copy()

        # Encode categorical variables
        df_encoded = pd.get_dummies(
            df,
            columns=config.CATEGORICAL_FEATURES,
            drop_first=False,
            dtype=float,
        )

        # Retain numerical features and newly generated one-hot encoded columns
        encoded_cols = [c for c in df_encoded.columns if any(c.startswith(cat + "_") for cat in config.CATEGORICAL_FEATURES)]
        self.feature_columns = config.NUMERICAL_FEATURES + encoded_cols

        X = df_encoded[self.feature_columns].copy().fillna(0.0)
        y = df_encoded[config.TARGET_COLUMN].astype(int)

        # Grouping vector: Ring members must stay together
        # Legitimate accounts (ring_id == 'NONE') receive individual unique group IDs
        groups = df_encoded["ring_id"].copy()
        none_mask = groups == "NONE"
        groups[none_mask] = [f"LEGIT_GROUP_{i}" for i in range(none_mask.sum())]

        return X, y, groups

    def train_model(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        groups: pd.Series,
        test_size: float = 0.25,
    ) -> Tuple[XGBClassifier, Dict[str, Any], Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]]:
        """
        Executes group-aware split, handles class imbalance, trains XGBoost,
        and calibrates decision threshold on held-out validation data.
        """
        gss = GroupShuffleSplit(n_splits=1, test_size=test_size, random_state=config.RANDOM_SEED)
        train_idx, test_idx = next(gss.split(X, y, groups=groups))

        X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
        y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

        # Calculate scale_pos_weight to handle class imbalance
        num_neg = (y_train == 0).sum()
        num_pos = (y_train == 1).sum()
        scale_pos = float(num_neg / max(1, num_pos))
        
        train_params = self.params.copy()
        train_params["scale_pos_weight"] = scale_pos

        model = XGBClassifier(**train_params)
        model.fit(X_train, y_train)

        # Calibrate optimal decision threshold on train predictions using PR curve
        train_probs = model.predict_proba(X_train)[:, 1]
        precisions, recalls, thresholds = precision_recall_curve(y_train, train_probs)
        
        f1_scores = []
        for p, r in zip(precisions[:-1], recalls[:-1]):
            score = (2 * p * r) / (p + r) if (p + r) > 0 else 0.0
            f1_scores.append(score)

        if len(f1_scores) > 0:
            best_idx = int(np.argmax(f1_scores))
            self.optimal_threshold = float(thresholds[best_idx])
        else:
            self.optimal_threshold = config.DEFAULT_ALERT_THRESHOLD

        # Clamp threshold to sensible operational bounds [0.30, 0.75]
        self.optimal_threshold = float(np.clip(self.optimal_threshold, 0.30, 0.75))

        metadata = {
            "num_features": len(self.feature_columns),
            "feature_names": self.feature_columns,
            "scale_pos_weight": round(scale_pos, 3),
            "optimal_threshold": round(self.optimal_threshold, 4),
            "train_samples": len(X_train),
            "test_samples": len(X_test),
            "train_mules": int(y_train.sum()),
            "test_mules": int(y_test.sum()),
        }

        return model, metadata, (X_train, X_test, y_train, y_test)

    def save(self, model: XGBClassifier, filepath: str = None) -> str:
        """Saves trained model and feature metadata to disk."""
        target_path = filepath or str(config.MODELS_DIR / "xgboost_model.json")
        model.save_model(target_path)
        
        # Save metadata alongside model
        meta_path = config.MODELS_DIR / "model_metadata.json"
        with open(meta_path, "w") as f:
            json.dump({
                "feature_names": self.feature_columns,
                "optimal_threshold": self.optimal_threshold,
                "params": self.params,
            }, f, indent=2)

        return target_path
