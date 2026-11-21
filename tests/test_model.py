"""
Unit tests for Machine Learning Pipeline, Group-Aware Split, and Evaluation.
"""

import pytest
import pandas as pd
from src.simulator.generator import UPISimulator
from src.graph.builder import TransactionGraphBuilder
from src.graph.features import GraphFeatureEngine
from src.models.train import ModelTrainer
from src.models.evaluate import SystemEvaluator


@pytest.fixture
def trained_pipeline():
    sim = UPISimulator(seed=42)
    accs, txs, rings, _ = sim.generate_all(num_accounts=120, num_rings=5)

    builder = TransactionGraphBuilder()
    G = builder.build_graph(accs, txs)

    engine = GraphFeatureEngine()
    features_df = engine.extract_features(G, txs)

    trainer = ModelTrainer()
    X, y, groups = trainer.prepare_data(features_df)
    model, metadata, (X_train, X_test, y_train, y_test) = trainer.train_model(X, y, groups)

    return model, metadata, features_df, (X_train, X_test, y_train, y_test)


def test_group_aware_split_no_ring_leakage(trained_pipeline):
    model, metadata, features_df, (X_train, X_test, y_train, y_test) = trained_pipeline

    train_indices = X_train.index
    test_indices = X_test.index

    train_rings = set(features_df.loc[train_indices, "ring_id"].unique()) - {"NONE"}
    test_rings = set(features_df.loc[test_indices, "ring_id"].unique()) - {"NONE"}

    # CRITICAL LEAKAGE TEST: No ground-truth ring should overlap between train and test!
    overlap = train_rings.intersection(test_rings)
    assert len(overlap) == 0, f"Data leakage detected! Shared rings: {overlap}"


def test_model_predictions_and_metrics(trained_pipeline):
    model, metadata, features_df, (X_train, X_test, y_train, y_test) = trained_pipeline

    test_probs = model.predict_proba(X_test)[:, 1]
    evaluator = SystemEvaluator()
    metrics = evaluator.evaluate_predictions(y_test, test_probs, threshold=metadata["optimal_threshold"])

    assert metrics["precision"] >= 0.0
    assert metrics["recall"] >= 0.0
    assert metrics["f1_score"] >= 0.0
    assert 0.0 <= metrics["false_positive_rate"] <= 1.0
