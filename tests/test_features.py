"""
Unit and integration tests for Step 4: Feature Engineering & Transaction Pattern Analysis.
Validates transaction-level features, account-level network metrics, temporal velocity,
and strict data leakage prevention safeguards.
"""

import pytest
import pandas as pd
import numpy as np

import config
from src.simulator.generator import UPISimulator
from src.features.transaction_features import TransactionFeatureEngine
from src.features.account_features import AccountFeatureEngine
from src.features.pipeline import FeatureEngineeringPipeline
from src.graph.builder import TransactionGraphBuilder
from src.graph.features import GraphFeatureEngine


@pytest.fixture
def sample_feature_data():
    """Generates synthetic test transactions and accounts with known patterns."""
    accounts = pd.DataFrame([
        {
            "account_id": "ACC_TEST_01",
            "bank_id": "BANK_A",
            "canonical_entity_id": "ENT_01",
            "profile_type": "REGULAR_P2P",
            "account_age_days": 120,
            "initial_balance": 5000.0,
            "is_mule": 1,
            "ring_id": "RING_01",
            "ring_role": "MULE_HOP",
        },
        {
            "account_id": "ACC_TEST_02",
            "bank_id": "BANK_B",
            "canonical_entity_id": "ENT_02",
            "profile_type": "STUDENT_FIRST_TIME",
            "account_age_days": 45,
            "initial_balance": 1000.0,
            "is_mule": 0,
            "ring_id": "NONE",
            "ring_role": "LEGITIMATE",
        },
    ])

    # ACC_TEST_01 receives ₹50,000 at 02:00 (off-hours), and forwards ₹49,000 at 02:03 (rapid burst, 3 mins)
    transactions = pd.DataFrame([
        {
            "transaction_id": "TX_F_001",
            "customer_id": "CUST_01",
            "sender_account": "ACC_TEST_02",
            "receiver_account": "ACC_TEST_01",
            "sender_bank": "BANK_B",
            "receiver_bank": "BANK_A",
            "amount": 50000.0,
            "timestamp": "2026-11-14 02:00:00",  # Off-hours & High value
            "transaction_type": "UPI_P2P",
            "transaction_status": "SUCCESS",
            "is_suspicious": 1,
            "ring_id": "RING_01",
            "pattern_type": "RAPID_PASS_THROUGH",
        },
        {
            "transaction_id": "TX_F_002",
            "customer_id": "CUST_02",
            "sender_account": "ACC_TEST_01",
            "receiver_account": "ACC_TEST_02",
            "sender_bank": "BANK_A",
            "receiver_bank": "BANK_B",
            "amount": 49000.0,
            "timestamp": "2026-11-14 02:03:00",  # 180 seconds later (rapid burst)
            "transaction_type": "UPI_P2P",
            "transaction_status": "SUCCESS",
            "is_suspicious": 1,
            "ring_id": "RING_01",
            "pattern_type": "RAPID_PASS_THROUGH",
        },
    ])

    return accounts, transactions


def test_transaction_feature_engine(sample_feature_data):
    """Verifies transaction-level feature engineering calculations."""
    _, txs = sample_feature_data
    engine = TransactionFeatureEngine()
    df_tx = engine.extract_transaction_features(txs)

    # 1. Verify off-hours detection (02:00 AM is in {23, 0..5})
    assert df_tx.loc[0, "is_off_hours"] == 1
    assert df_tx.loc[1, "is_off_hours"] == 1

    # 2. Verify high-value detection (50,000 >= threshold)
    assert df_tx.loc[0, "is_high_value"] == 1

    # 3. Verify cross-bank detection (BANK_B -> BANK_A)
    assert df_tx.loc[0, "is_cross_bank"] == 1

    # 4. Verify time gap and rapid burst
    assert df_tx.loc[0, "time_gap_seconds"] > 300  # First transaction has default gap
    assert df_tx.loc[1, "time_gap_seconds"] == 180.0  # 3 minutes = 180s
    assert df_tx.loc[1, "rapid_burst_flag"] == 1

    # 5. Verify risk score bounds
    assert 0.0 <= df_tx.loc[1, "velocity_score"] <= 1.0
    assert 0.0 <= df_tx.loc[1, "transaction_risk_indicator"] <= 1.0


def test_account_feature_engine(sample_feature_data):
    """Verifies account-level feature engineering and turnaround time calculations."""
    accounts, txs = sample_feature_data
    builder = TransactionGraphBuilder()
    G = builder.build_graph(accounts, txs)

    engine = AccountFeatureEngine()
    df_acc = engine.extract_features(G, txs)

    assert len(df_acc) == 2
    acc_1 = df_acc[df_acc["account_id"] == "ACC_TEST_01"].iloc[0]

    # Inflow: 50,000, Outflow: 49,000
    assert acc_1["total_amount_in"] == 50000.0
    assert acc_1["total_amount_out"] == 49000.0

    # Pass-through ratio = 49000 / 50000 = 0.98
    assert abs(acc_1["pass_through_ratio"] - 0.98) < 0.01

    # Turnaround time: received at 02:00, sent at 02:03 = 180s
    assert acc_1["min_turnaround_time_sec"] == 180.0

    # Off-hours ratio: both transactions were nocturnal
    assert acc_1["off_hours_tx_ratio"] == 1.0

    # Behavioral risk score should be elevated for pass-through mule
    assert acc_1["behavioral_risk_score"] > 0.50


def test_data_leakage_safeguards(sample_feature_data, tmp_path):
    """CRITICAL TEST: Ensures input features matrix strictly excludes ground-truth targets."""
    accounts, txs = sample_feature_data
    pipeline = FeatureEngineeringPipeline()

    _, df_account_features, metadata = pipeline.run_pipeline(
        accounts_df=accounts,
        transactions_df=txs,
        export_artifacts=False,
    )

    # Isolated X matrix
    LEAKAGE_TARGETS = {"is_mule", "ring_id", "ring_role", "is_suspicious", "canonical_entity_id"}
    X_cols = [c for c in df_account_features.columns if c not in LEAKAGE_TARGETS and c != "account_id"]

    for col in X_cols:
        assert col not in LEAKAGE_TARGETS, f"Data leakage detected! Column {col} should not be in X"

    # Confirm metadata documents leakage isolation
    assert metadata["data_leakage_safeguards"]["ground_truth_isolated"] is True


def test_graph_feature_engine_compatibility(sample_feature_data):
    """Verifies GraphFeatureEngine backwards compatibility."""
    accounts, txs = sample_feature_data
    builder = TransactionGraphBuilder()
    G = builder.build_graph(accounts, txs)

    engine = GraphFeatureEngine()
    df_features = engine.extract_features(G, txs)

    # Check key columns
    assert "tx_frequency_total" in df_features.columns
    assert "pass_through_ratio" in df_features.columns
    assert "min_turnaround_time_sec" in df_features.columns
    assert "behavioral_risk_score" in df_features.columns
    assert "velocity_score" in df_features.columns
