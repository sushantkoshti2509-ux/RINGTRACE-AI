"""
Unit and integration tests for Step 6: Model Evaluation and Validation.
Validates metric calculations, confusion matrices, customer profile FPR,
bank slices, cost-based threshold optimization, and plot generation.
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path

import config
from src.models.evaluate import SystemEvaluator


@pytest.fixture
def sample_evaluation_df():
    """Generates synthetic predictions with known true positives, false positives, etc."""
    return pd.DataFrame([
        # True Negatives (Legitimate correctly cleared)
        {"account_id": "ACC_001", "bank_id": "BANK_A", "profile_type": "SALARIED", "is_mule_ground_truth": 0, "risk_score": 0.05, "alert_flag": 0},
        {"account_id": "ACC_002", "bank_id": "BANK_A", "profile_type": "GIG_WORKER", "is_mule_ground_truth": 0, "risk_score": 0.15, "alert_flag": 0},
        {"account_id": "ACC_003", "bank_id": "BANK_B", "profile_type": "MERCHANT", "is_mule_ground_truth": 0, "risk_score": 0.20, "alert_flag": 0},
        {"account_id": "ACC_004", "bank_id": "BANK_C", "profile_type": "STUDENT_FIRST_TIME", "is_mule_ground_truth": 0, "risk_score": 0.10, "alert_flag": 0},

        # False Positive (Legitimate mistakenly flagged)
        {"account_id": "ACC_005", "bank_id": "BANK_B", "profile_type": "MERCHANT", "is_mule_ground_truth": 0, "risk_score": 0.85, "alert_flag": 1},

        # True Positives (Mules correctly detected)
        {"account_id": "ACC_006", "bank_id": "BANK_A", "profile_type": "REGULAR_P2P", "is_mule_ground_truth": 1, "risk_score": 0.95, "alert_flag": 1},
        {"account_id": "ACC_007", "bank_id": "BANK_B", "profile_type": "REGULAR_P2P", "is_mule_ground_truth": 1, "risk_score": 0.92, "alert_flag": 1},
        {"account_id": "ACC_008", "bank_id": "BANK_C", "profile_type": "STUDENT_FIRST_TIME", "is_mule_ground_truth": 1, "risk_score": 0.88, "alert_flag": 1},

        # False Negative (Mule missed)
        {"account_id": "ACC_009", "bank_id": "BANK_C", "profile_type": "SALARIED", "is_mule_ground_truth": 1, "risk_score": 0.30, "alert_flag": 0},
    ])


def test_evaluate_predictions_metrics(sample_evaluation_df):
    """Verifies that accuracy, precision, recall, F1, and confusion matrix are calculated correctly."""
    evaluator = SystemEvaluator()
    metrics = evaluator.evaluate_predictions(
        y_true=sample_evaluation_df["is_mule_ground_truth"],
        y_probs=sample_evaluation_df["risk_score"],
        threshold=0.50,
    )

    # In sample_evaluation_df:
    # 5 legitimate (4 TN, 1 FP)
    # 4 mules (3 TP, 1 FN)
    cm = metrics["confusion_matrix"]
    assert cm["TN"] == 4
    assert cm["FP"] == 1
    assert cm["FN"] == 1
    assert cm["TP"] == 3

    assert metrics["precision"] == 3 / (3 + 1)  # 0.75
    assert metrics["recall"] == 3 / (3 + 1)     # 0.75
    assert metrics["f1_score"] == 0.75
    assert metrics["false_positive_rate"] == 1 / (1 + 4)  # 0.20
    assert metrics["false_negative_rate"] == 1 / (1 + 3)  # 0.25
    assert abs(metrics["accuracy"] - 7 / 9) < 1e-3


def test_evaluate_by_profile(sample_evaluation_df):
    """Verifies profile-wise False Positive Rate segregation."""
    evaluator = SystemEvaluator()
    prof_metrics = evaluator.evaluate_by_profile(sample_evaluation_df)

    assert "MERCHANT" in prof_metrics
    assert "GIG_WORKER" in prof_metrics
    assert "SALARIED" in prof_metrics

    # Merchant has 2 legitimate accounts, 1 false positive -> FPR = 0.50
    assert prof_metrics["MERCHANT"]["legitimate_count"] == 2
    assert prof_metrics["MERCHANT"]["false_positives"] == 1
    assert prof_metrics["MERCHANT"]["profile_fpr"] == 0.50

    # Gig worker has 1 legitimate account, 0 false positive -> FPR = 0.00
    assert prof_metrics["GIG_WORKER"]["profile_fpr"] == 0.00


def test_evaluate_by_bank(sample_evaluation_df):
    """Verifies bank slice performance breakdown."""
    evaluator = SystemEvaluator()
    bank_metrics = evaluator.evaluate_by_bank(sample_evaluation_df)

    assert "BANK_A" in bank_metrics
    assert "BANK_B" in bank_metrics
    assert "BANK_C" in bank_metrics

    # In Bank A: ACC_001 (TN), ACC_002 (TN), ACC_006 (TP) -> 100% precision and recall
    assert bank_metrics["BANK_A"]["precision"] == 1.0
    assert bank_metrics["BANK_A"]["recall"] == 1.0
    assert bank_metrics["BANK_A"]["false_positive_rate"] == 0.0


def test_error_analysis(sample_evaluation_df):
    """Verifies error profiling identifies False Positives and False Negatives."""
    evaluator = SystemEvaluator()
    features_dummy = pd.DataFrame({"account_id": sample_evaluation_df["account_id"]})
    errs = evaluator.analyze_errors(sample_evaluation_df, features_dummy)

    assert errs["false_positive_count"] == 1
    assert errs["false_negative_count"] == 1
    assert errs["false_positives"][0]["account_id"] == "ACC_005"
    assert errs["false_negatives"][0]["account_id"] == "ACC_009"


def test_threshold_optimization(sample_evaluation_df):
    """Verifies cost-based threshold optimization sweeps."""
    evaluator = SystemEvaluator()
    opt = evaluator.optimize_threshold(
        y_true=sample_evaluation_df["is_mule_ground_truth"],
        y_probs=sample_evaluation_df["risk_score"],
        cost_fp=1.0,
        cost_fn=5.0,
    )

    assert "optimal_cost_threshold" in opt
    assert "optimal_f1_score" in opt
    assert 0.10 <= opt["optimal_cost_threshold"] <= 0.90


def test_plot_generation(sample_evaluation_df, tmp_path):
    """Verifies that all 5 publication-ready PNG figures are properly created on disk."""
    evaluator = SystemEvaluator()
    saved_plots = evaluator.generate_evaluation_plots(
        y_true=sample_evaluation_df["is_mule_ground_truth"],
        y_probs=sample_evaluation_df["risk_score"],
        results_df=sample_evaluation_df,
        output_dir=tmp_path,
    )

    assert len(saved_plots) == 5
    for p in saved_plots:
        path = Path(p)
        assert path.exists()
        assert path.stat().st_size > 1000  # Non-empty valid image
