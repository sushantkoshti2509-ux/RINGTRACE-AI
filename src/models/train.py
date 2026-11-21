"""
RINGTRACE AI - Multi-Model Machine Learning Training & Benchmarking Pipeline.
Trains, evaluates, and compares multiple fraud detection algorithms:
1. Random Forest (User-recommended classification baseline)
2. XGBoost (High-performance gradient boosted decision trees)
3. Logistic Regression (Interpretable linear baseline)
4. Isolation Forest (Unsupervised tree-based anomaly detection)

Implements ring-group aware data splitting to prevent data leakage, handles
class imbalance, calibrates decision thresholds, and crowns the Champion Model.
"""

from typing import Tuple, Dict, Any, List, Optional
import json
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import GroupShuffleSplit
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    average_precision_score,
    confusion_matrix,
    precision_recall_curve,
)
from xgboost import XGBClassifier

import config


class ModelTrainer:
    """Trains, calibrates, and benchmarks multiple fraud detection models."""

    def __init__(self, params: Dict[str, Any] = None):
        self.params = params or config.XGBOOST_PARAMS.copy()
        self.feature_columns: List[str] = []
        self.optimal_threshold: float = config.DEFAULT_ALERT_THRESHOLD
        self.trained_models: Dict[str, Any] = {}
        self.model_metrics: Dict[str, Dict[str, Any]] = {}
        self.champion_name: str = "XGBoost"

    def prepare_data(
        self,
        features_df: pd.DataFrame,
    ) -> Tuple[pd.DataFrame, pd.Series, pd.Series]:
        """
        Prepares features (X), labels (y), and grouping vector (groups)
        to prevent data leakage across train and test splits.
        """
        df = features_df.copy()

        # One-hot encode categorical variables (e.g. profile_type, bank_id)
        df_encoded = pd.get_dummies(
            df,
            columns=config.CATEGORICAL_FEATURES,
            drop_first=False,
            dtype=float,
        )

        # Retain numerical features and newly generated one-hot encoded columns
        encoded_cols = [
            c for c in df_encoded.columns
            if any(c.startswith(cat + "_") for cat in config.CATEGORICAL_FEATURES)
        ]
        self.feature_columns = config.NUMERICAL_FEATURES + encoded_cols

        # Filter features to those present
        self.feature_columns = [c for c in self.feature_columns if c in df_encoded.columns]

        X = df_encoded[self.feature_columns].copy().fillna(0.0)
        y = df_encoded[config.TARGET_COLUMN].astype(int)

        # Grouping vector: Ring members must stay together to avoid test data leakage
        # Legitimate accounts receive individual unique group IDs
        groups = df_encoded["ring_id"].copy() if "ring_id" in df_encoded.columns else pd.Series("NONE", index=df.index)
        none_mask = groups == "NONE"
        groups[none_mask] = [f"LEGIT_GROUP_{i}" for i in range(none_mask.sum())]

        return X, y, groups

    def split_data(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        groups: pd.Series,
        test_size: float = 0.25,
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
        """Performs ring-group aware train/test split without data leakage."""
        gss = GroupShuffleSplit(n_splits=1, test_size=test_size, random_state=config.RANDOM_SEED)
        train_idx, test_idx = next(gss.split(X, y, groups=groups))
        return X.iloc[train_idx], X.iloc[test_idx], y.iloc[train_idx], y.iloc[test_idx]

    def calibrate_threshold(self, y_true: pd.Series, y_probs: np.ndarray) -> float:
        """Calibrates optimal decision threshold on training predictions using F1 score."""
        precisions, recalls, thresholds = precision_recall_curve(y_true, y_probs)
        f1_scores = []
        for p, r in zip(precisions[:-1], recalls[:-1]):
            score = (2 * p * r) / (p + r) if (p + r) > 0 else 0.0
            f1_scores.append(score)

        if len(f1_scores) > 0:
            best_idx = int(np.argmax(f1_scores))
            opt_thresh = float(thresholds[best_idx])
        else:
            opt_thresh = config.DEFAULT_ALERT_THRESHOLD

        return float(np.clip(opt_thresh, 0.30, 0.75))

    def evaluate_model_predictions(
        self,
        y_true: pd.Series,
        y_probs: np.ndarray,
        threshold: float,
        model_name: str,
    ) -> Dict[str, Any]:
        """Calculates standard fraud detection metrics and confusion matrix."""
        y_pred = (y_probs >= threshold).astype(int)

        acc = float(accuracy_score(y_true, y_pred))
        prec = float(precision_score(y_true, y_pred, zero_division=0))
        rec = float(recall_score(y_true, y_pred, zero_division=0))
        f1 = float(f1_score(y_true, y_pred, zero_division=0))

        try:
            roc_auc = float(roc_auc_score(y_true, y_probs))
        except Exception:
            roc_auc = 0.5

        try:
            pr_auc = float(average_precision_score(y_true, y_probs))
        except Exception:
            pr_auc = float(y_true.mean())

        cm = confusion_matrix(y_true, y_pred)
        if cm.shape == (2, 2):
            tn, fp, fn, tp = cm.ravel()
        else:
            tn, fp, fn, tp = int(cm[0, 0]), 0, 0, 0

        fpr = float(fp / max(1, fp + tn))

        return {
            "model_name": model_name,
            "threshold": round(threshold, 4),
            "accuracy": round(acc, 4),
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1_score": round(f1, 4),
            "pr_auc": round(pr_auc, 4),
            "roc_auc": round(roc_auc, 4),
            "false_positive_rate": round(fpr, 4),
            "confusion_matrix": {
                "TN": int(tn),
                "FP": int(fp),
                "FN": int(fn),
                "TP": int(tp),
            },
        }

    # -------------------------------------------------------------
    # 1. Random Forest Classifier (Recommended Baseline)
    # -------------------------------------------------------------
    def train_random_forest(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        X_test: pd.DataFrame,
        y_test: pd.Series,
    ) -> Tuple[RandomForestClassifier, Dict[str, Any]]:
        """Trains Random Forest ensemble with balanced class weights."""
        rf = RandomForestClassifier(
            n_estimators=100,
            max_depth=8,
            min_samples_split=4,
            class_weight="balanced",
            random_state=config.RANDOM_SEED,
            n_jobs=-1,
        )
        rf.fit(X_train, y_train)

        train_probs = rf.predict_proba(X_train)[:, 1]
        thresh = self.calibrate_threshold(y_train, train_probs)

        test_probs = rf.predict_proba(X_test)[:, 1]
        metrics = self.evaluate_model_predictions(y_test, test_probs, thresh, "Random Forest")

        self.trained_models["Random Forest"] = rf
        self.model_metrics["Random Forest"] = metrics
        return rf, metrics

    # -------------------------------------------------------------
    # 2. XGBoost Classifier (Champion Gradient Boosting)
    # -------------------------------------------------------------
    def train_xgboost(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        X_test: pd.DataFrame,
        y_test: pd.Series,
    ) -> Tuple[XGBClassifier, Dict[str, Any]]:
        """Trains XGBoost gradient boosted trees with scale_pos_weight."""
        num_neg = (y_train == 0).sum()
        num_pos = (y_train == 1).sum()
        scale_pos = float(num_neg / max(1, num_pos))

        train_params = self.params.copy()
        train_params["scale_pos_weight"] = scale_pos

        xgb = XGBClassifier(**train_params)
        xgb.fit(X_train, y_train)

        train_probs = xgb.predict_proba(X_train)[:, 1]
        thresh = self.calibrate_threshold(y_train, train_probs)
        self.optimal_threshold = thresh

        test_probs = xgb.predict_proba(X_test)[:, 1]
        metrics = self.evaluate_model_predictions(y_test, test_probs, thresh, "XGBoost")
        metrics["scale_pos_weight"] = round(scale_pos, 3)

        self.trained_models["XGBoost"] = xgb
        self.model_metrics["XGBoost"] = metrics
        return xgb, metrics

    # -------------------------------------------------------------
    # 3. Logistic Regression (Linear Benchmark)
    # -------------------------------------------------------------
    def train_logistic_regression(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        X_test: pd.DataFrame,
        y_test: pd.Series,
    ) -> Tuple[Pipeline, Dict[str, Any]]:
        """Trains scaled Logistic Regression with L2 regularization."""
        lr_pipe = Pipeline([
            ("scaler", StandardScaler()),
            ("lr", LogisticRegression(
                C=1.0,
                class_weight="balanced",
                max_iter=1000,
                random_state=config.RANDOM_SEED,
            )),
        ])
        lr_pipe.fit(X_train, y_train)

        train_probs = lr_pipe.predict_proba(X_train)[:, 1]
        thresh = self.calibrate_threshold(y_train, train_probs)

        test_probs = lr_pipe.predict_proba(X_test)[:, 1]
        metrics = self.evaluate_model_predictions(y_test, test_probs, thresh, "Logistic Regression")

        self.trained_models["Logistic Regression"] = lr_pipe
        self.model_metrics["Logistic Regression"] = metrics
        return lr_pipe, metrics

    # -------------------------------------------------------------
    # 4. Isolation Forest (Unsupervised Anomaly Detection)
    # -------------------------------------------------------------
    def train_isolation_forest(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        X_test: pd.DataFrame,
        y_test: pd.Series,
    ) -> Tuple[IsolationForest, Dict[str, Any]]:
        """Trains unsupervised Isolation Forest for anomaly discovery."""
        contamination = float(np.clip(y_train.mean(), 0.05, 0.25))
        iforest = IsolationForest(
            n_estimators=100,
            contamination=contamination,
            random_state=config.RANDOM_SEED,
            n_jobs=-1,
        )
        iforest.fit(X_train)

        # Decision function: negative values indicate anomalies
        train_scores = -iforest.decision_function(X_train)
        min_s, max_s = float(train_scores.min()), float(train_scores.max())
        norm_train = (train_scores - min_s) / max(1e-5, (max_s - min_s))
        thresh = self.calibrate_threshold(y_train, norm_train)

        test_scores = -iforest.decision_function(X_test)
        norm_test = (test_scores - min_s) / max(1e-5, (max_s - min_s))
        norm_test = np.clip(norm_test, 0.0, 1.0)

        metrics = self.evaluate_model_predictions(y_test, norm_test, thresh, "Isolation Forest")
        metrics["contamination"] = round(contamination, 3)

        self.trained_models["Isolation Forest"] = iforest
        self.model_metrics["Isolation Forest"] = metrics
        return iforest, metrics

    # -------------------------------------------------------------
    # Multi-Model Benchmark & Comparison
    # -------------------------------------------------------------
    def compare_all_models(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        groups: pd.Series,
        test_size: float = 0.25,
    ) -> Dict[str, Any]:
        """
        Trains and compares Random Forest, XGBoost, Logistic Regression,
        and Isolation Forest, then selects the Champion Model.
        """
        X_train, X_test, y_train, y_test = self.split_data(X, y, groups, test_size=test_size)

        # 1. Train Random Forest (baseline classifier)
        self.train_random_forest(X_train, y_train, X_test, y_test)

        # 2. Train XGBoost (champion classifier)
        self.train_xgboost(X_train, y_train, X_test, y_test)

        # 3. Train Logistic Regression (linear baseline)
        self.train_logistic_regression(X_train, y_train, X_test, y_test)

        # 4. Train Isolation Forest (unsupervised anomaly detector)
        self.train_isolation_forest(X_train, y_train, X_test, y_test)

        # Determine Champion Model based on F1-score and Precision/Recall trade-off
        ranked_models = sorted(
            self.model_metrics.items(),
            key=lambda item: (item[1]["f1_score"], item[1]["recall"], item[1]["precision"]),
            reverse=True,
        )
        self.champion_name = ranked_models[0][0]

        comparison_report = {
            "train_samples": len(X_train),
            "test_samples": len(X_test),
            "train_mules": int(y_train.sum()),
            "test_mules": int(y_test.sum()),
            "champion_model": self.champion_name,
            "models": self.model_metrics,
            "ranked_by_f1": [name for name, _ in ranked_models],
        }

        # Save model comparison reports
        self.save_model_comparison(comparison_report)

        return comparison_report

    def save_model_comparison(self, report: Dict[str, Any]):
        """Exports comparison report in both JSON and Markdown formats."""
        config.REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        config.MODELS_DIR.mkdir(parents=True, exist_ok=True)

        # JSON Report
        json_path = config.REPORTS_DIR / "model_comparison.json"
        with open(json_path, "w") as f:
            json.dump(report, f, indent=2)

        # Markdown Report
        md_lines = [
            "# RINGTRACE AI - Model Comparison and Benchmarking Report",
            f"**Evaluation Split:** {report['train_samples']} Train Samples ({report['train_mules']} mules) | {report['test_samples']} Test Samples ({report['test_mules']} mules)",
            f"**Crown Champion Model:** `{report['champion_model']}`",
            "",
            "## 1. Performance Comparison Matrix",
            "",
            "| Algorithm | Accuracy | Precision | Recall | F1-Score | PR-AUC | ROC-AUC | FPR | Status |",
            "|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|",
        ]

        for model_name, m in report["models"].items():
            is_champ = "🏆 Champion" if model_name == report["champion_model"] else "Baseline"
            md_lines.append(
                f"| **{model_name}** | {m['accuracy']:.4f} | {m['precision']:.4f} | {m['recall']:.4f} | "
                f"**{m['f1_score']:.4f}** | {m['pr_auc']:.4f} | {m['roc_auc']:.4f} | {m['false_positive_rate']:.4f} | {is_champ} |"
            )

        md_lines.extend([
            "",
            "## 2. Confusion Matrices",
            "",
        ])

        for model_name, m in report["models"].items():
            cm = m["confusion_matrix"]
            md_lines.extend([
                f"### {model_name}",
                f"- **True Negatives (Legitimate Correct):** {cm['TN']:,}",
                f"- **False Positives (False Alarms):** {cm['FP']:,}",
                f"- **False Negatives (Missed Mules):** {cm['FN']:,}",
                f"- **True Positives (Mules Detected):** {cm['TP']:,}",
                "",
            ])

        md_path = config.REPORTS_DIR / "model_comparison.md"
        with open(md_path, "w") as f:
            f.write("\n".join(md_lines))

    # -------------------------------------------------------------
    # Backwards-compatible train_model method
    # -------------------------------------------------------------
    def train_model(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        groups: pd.Series,
        test_size: float = 0.25,
    ) -> Tuple[XGBClassifier, Dict[str, Any], Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]]:
        """
        Backwards-compatible training method called by existing pipeline.
        Trains XGBoost, runs multi-model comparison, and saves champion model.
        """
        X_train, X_test, y_train, y_test = self.split_data(X, y, groups, test_size=test_size)

        # Run multi-model comparison suite
        self.compare_all_models(X, y, groups, test_size=test_size)

        # Return XGBoost model and its metadata for pipeline consistency
        xgb_model = self.trained_models["XGBoost"]
        metadata = {
            "num_features": len(self.feature_columns),
            "feature_names": self.feature_columns,
            "scale_pos_weight": self.model_metrics["XGBoost"].get("scale_pos_weight", 1.0),
            "optimal_threshold": self.optimal_threshold,
            "train_samples": len(X_train),
            "test_samples": len(X_test),
            "train_mules": int(y_train.sum()),
            "test_mules": int(y_test.sum()),
            "champion_model": self.champion_name,
        }

        # Save all trained models
        self.save_all_models()

        return xgb_model, metadata, (X_train, X_test, y_train, y_test)

    def save_all_models(self):
        """Persists trained model files to models/ directory."""
        config.MODELS_DIR.mkdir(parents=True, exist_ok=True)

        if "XGBoost" in self.trained_models:
            self.trained_models["XGBoost"].save_model(str(config.MODELS_DIR / "xgboost_model.json"))

        if "Random Forest" in self.trained_models:
            joblib.dump(self.trained_models["Random Forest"], config.MODELS_DIR / "random_forest_model.joblib")

        if "Logistic Regression" in self.trained_models:
            joblib.dump(self.trained_models["Logistic Regression"], config.MODELS_DIR / "logistic_regression.joblib")

        if "Isolation Forest" in self.trained_models:
            joblib.dump(self.trained_models["Isolation Forest"], config.MODELS_DIR / "isolation_forest.joblib")

        # Save comprehensive metadata
        with open(config.MODELS_DIR / "model_metadata.json", "w") as f:
            json.dump({
                "feature_names": self.feature_columns,
                "optimal_threshold": self.optimal_threshold,
                "champion_model": self.champion_name,
                "metrics": self.model_metrics,
            }, f, indent=2)

    def save(self, model: XGBClassifier, filepath: str = None) -> str:
        """Saves XGBoost model to disk (backwards compatible)."""
        target_path = filepath or str(config.MODELS_DIR / "xgboost_model.json")
        model.save_model(target_path)
        return target_path
