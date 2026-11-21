"""
Unit and integration tests for Step 5: Machine Learning Model Development & Benchmarking.
Validates multi-model training (Random Forest, XGBoost, Logistic Regression, Isolation Forest),
group-aware split, confusion matrices, risk scoring, and model serialization.
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path

import config
from src.simulator.generator import UPISimulator
from src.graph.builder import TransactionGraphBuilder
from src.features.account_features import AccountFeatureEngine
from src.models.train import ModelTrainer
from src.models.predict import RiskPredictor


@pytest.fixture
def sample_ml_data():
    """Generates synthetic features dataset with ground-truth mule rings."""
    sim = UPISimulator(seed=42)
    accounts, transactions, rings, _ = sim.generate_all(num_accounts=120, num_rings=5)

    builder = TransactionGraphBuilder()
    G = builder.build_graph(accounts, transactions)

    engine = AccountFeatureEngine()
    features_df = engine.extract_features(G, transactions)

    return features_df, transactions


def test_multi_model_training_and_comparison(sample_ml_data):
    """Verifies that Random Forest, XGBoost, Logistic Regression, and Isolation Forest all train and evaluate."""
    features_df, _ = sample_ml_data
    trainer = ModelTrainer()
    X, y, groups = trainer.prepare_data(features_df)

    # Run multi-model benchmark
    comparison = trainer.compare_all_models(X, y, groups, test_size=0.25)

    # 1. Verify all 4 recommended models exist in evaluation
    assert "Random Forest" in comparison["models"]
    assert "XGBoost" in comparison["models"]
    assert "Logistic Regression" in comparison["models"]
    assert "Isolation Forest" in comparison["models"]

    # 2. Check metrics structure for each model
    for model_name, metrics in comparison["models"].items():
        assert "accuracy" in metrics
        assert "precision" in metrics
        assert "recall" in metrics
        assert "f1_score" in metrics
        assert "confusion_matrix" in metrics
        cm = metrics["confusion_matrix"]
        assert all(k in cm for k in ["TN", "FP", "FN", "TP"])
        assert sum(cm.values()) == comparison["test_samples"]

    # 3. Verify champion model is chosen
    assert comparison["champion_model"] in ["XGBoost", "Random Forest"]


def test_group_aware_split_prevents_leakage(sample_ml_data):
    """CRITICAL TEST: Ensures no ground-truth mule ring is shared between train and test sets."""
    features_df, _ = sample_ml_data
    trainer = ModelTrainer()
    X, y, groups = trainer.prepare_data(features_df)
    X_train, X_test, y_train, y_test = trainer.split_data(X, y, groups, test_size=0.25)

    train_rings = set(features_df.loc[X_train.index, "ring_id"].unique()) - {"NONE"}
    test_rings = set(features_df.loc[X_test.index, "ring_id"].unique()) - {"NONE"}

    assert len(train_rings.intersection(test_rings)) == 0, "Data leakage detected: ring shared between train and test!"


def test_random_forest_classification(sample_ml_data):
    """Verifies user-recommended Random Forest baseline training and predictions."""
    features_df, _ = sample_ml_data
    trainer = ModelTrainer()
    X, y, groups = trainer.prepare_data(features_df)
    X_train, X_test, y_train, y_test = trainer.split_data(X, y, groups, test_size=0.25)

    rf, metrics = trainer.train_random_forest(X_train, y_train, X_test, y_test)

    assert rf is not None
    assert metrics["precision"] >= 0.0
    assert metrics["recall"] >= 0.0
    assert metrics["f1_score"] >= 0.0
    assert metrics["confusion_matrix"]["TP"] >= 0


def test_isolation_forest_anomaly_detection(sample_ml_data):
    """Verifies Isolation Forest unsupervised anomaly score generation."""
    features_df, _ = sample_ml_data
    trainer = ModelTrainer()
    X, y, groups = trainer.prepare_data(features_df)
    X_train, X_test, y_train, y_test = trainer.split_data(X, y, groups, test_size=0.25)

    iforest, metrics = trainer.train_isolation_forest(X_train, y_train, X_test, y_test)

    assert iforest is not None
    assert 0.0 <= metrics["accuracy"] <= 1.0
    assert "contamination" in metrics


def test_risk_predictor_account_and_transaction(sample_ml_data):
    """Verifies account-level and transaction-level risk scoring and tier generation."""
    features_df, transactions = sample_ml_data
    trainer = ModelTrainer()
    X, y, groups = trainer.prepare_data(features_df)
    trainer.train_model(X, y, groups)

    predictor = RiskPredictor(model_type="xgboost")
    account_risks = predictor.predict_risk_scores(features_df)

    # Account-level checks
    assert len(account_risks) == len(features_df)
    assert "risk_score" in account_risks.columns
    assert "alert_flag" in account_risks.columns
    assert "risk_tier" in account_risks.columns
    assert account_risks["risk_score"].between(0.0, 1.0).all()
    assert set(account_risks["risk_tier"].unique()).issubset({"LOW", "MEDIUM", "HIGH"})

    # Transaction-level checks
    tx_risks = predictor.predict_transaction_risk_scores(transactions, account_risk_df=account_risks)
    assert len(tx_risks) == len(transactions)
    assert "transaction_risk_score" in tx_risks.columns
    assert "fraud_alert_flag" in tx_risks.columns
    assert "risk_category" in tx_risks.columns
    assert tx_risks["transaction_risk_score"].between(0.0, 1.0).all()
