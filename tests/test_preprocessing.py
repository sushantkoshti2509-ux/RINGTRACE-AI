"""
Unit and integration tests for Step 2: Data Preprocessing and Standardization Pipeline.
Validates deduplication, invalid data rejection, schema normalization,
timestamp formatting, categorical encoding, and multi-bank preprocessing.
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import json

from src.preprocessing.clean import (
    BankSchemaStandardizer,
    CategoricalFeatureEncoder,
    DataPreprocessor,
    COLUMN_ALIASES,
)
import config


@pytest.fixture
def sample_raw_transactions():
    """Returns sample transactions with various anomalies to clean."""
    return pd.DataFrame([
        # Valid transaction
        {
            "tx_id": "TX_TEST_001",
            "from_acc": "ACC_A_001",
            "to_acc": "ACC_B_001",
            "src_bank": "BANK_A",
            "dest_bank": "BANK_B",
            "txn_amount": 15000.50,
            "date_time": "2026-11-14 10:30:00",
            "tx_type": "UPI_P2P",
            "status": "SUCCESS",
            "is_fraud": 0,
        },
        # Duplicate of TX_TEST_001
        {
            "tx_id": "TX_TEST_001",
            "from_acc": "ACC_A_001",
            "to_acc": "ACC_B_001",
            "src_bank": "BANK_A",
            "dest_bank": "BANK_B",
            "txn_amount": 15000.50,
            "date_time": "2026-11-14 10:30:00",
            "tx_type": "UPI_P2P",
            "status": "SUCCESS",
            "is_fraud": 0,
        },
        # Self-transfer (should be dropped)
        {
            "tx_id": "TX_TEST_002",
            "from_acc": "ACC_A_002",
            "to_acc": "ACC_A_002",
            "src_bank": "BANK_A",
            "dest_bank": "BANK_A",
            "txn_amount": 5000.0,
            "date_time": "2026-11-14 11:00:00",
            "tx_type": "SELF_TRANSFER",
            "status": "SUCCESS",
            "is_fraud": 0,
        },
        # Non-positive amount (should be dropped)
        {
            "tx_id": "TX_TEST_003",
            "from_acc": "ACC_A_003",
            "to_acc": "ACC_B_002",
            "src_bank": "BANK_A",
            "dest_bank": "BANK_B",
            "txn_amount": -100.0,
            "date_time": "2026-11-14 11:30:00",
            "tx_type": "UPI_P2P",
            "status": "FAILED",
            "is_fraud": 0,
        },
        # Zero amount (should be dropped)
        {
            "tx_id": "TX_TEST_004",
            "from_acc": "ACC_A_004",
            "to_acc": "ACC_C_001",
            "src_bank": "BANK_A",
            "dest_bank": "BANK_C",
            "txn_amount": 0.0,
            "date_time": "2026-11-14 12:00:00",
            "tx_type": "UPI_P2P",
            "status": "SUCCESS",
            "is_fraud": 0,
        },
        # Valid transaction with different date format
        {
            "tx_id": "TX_TEST_005",
            "from_acc": "ACC_B_003",
            "to_acc": "ACC_C_002",
            "src_bank": "BANK_B",
            "dest_bank": "BANK_C",
            "txn_amount": 45000.758,
            "date_time": "14/11/2026 14:45",
            "tx_type": "IMPS",
            "status": "SUCCESS",
            "is_fraud": 1,
            "pattern": "RAPID_PASS_THROUGH",
        },
    ])


@pytest.fixture
def sample_raw_accounts():
    """Returns sample accounts with duplicates and missing values."""
    return pd.DataFrame([
        {
            "account_id": "ACC_A_001",
            "bank_id": "BANK_A",
            "profile": "STUDENT",
            "account_age_days": 120,
            "initial_balance": 5000.0,
            "is_mule": 0,
        },
        # Duplicate
        {
            "account_id": "ACC_A_001",
            "bank_id": "BANK_A",
            "profile": "STUDENT",
            "account_age_days": 120,
            "initial_balance": 5000.0,
            "is_mule": 0,
        },
        {
            "account_id": "ACC_B_001",
            "bank_id": "BANK_B",
            "profile": "BUSINESS",
            "account_age_days": 450,
            "initial_balance": 150000.0,
            "is_mule": 1,
            "ring_id": "RING_001",
            "ring_role": "AGGREGATOR",
        },
    ])


def test_schema_standardizer_alias_mapping():
    """Verifies that heterogeneous bank column names are properly mapped."""
    df_raw = pd.DataFrame({
        "tx_id": ["T1"],
        "from_acc": ["A1"],
        "to_acc": ["B1"],
        "src_bank": ["BANK_A"],
        "dest_bank": ["BANK_B"],
        "txn_amount": [100.0],
        "date_time": ["2026-11-14 10:00:00"],
        "tx_type": ["UPI_P2P"],
        "status": ["SUCCESS"],
        "is_fraud": [0],
    })
    standardizer = BankSchemaStandardizer()
    df_mapped = standardizer.standardize_column_names(df_raw)

    assert "transaction_id" in df_mapped.columns
    assert "sender_account" in df_mapped.columns
    assert "receiver_account" in df_mapped.columns
    assert "sender_bank" in df_mapped.columns
    assert "receiver_bank" in df_mapped.columns
    assert "amount" in df_mapped.columns
    assert "timestamp" in df_mapped.columns
    assert "transaction_type" in df_mapped.columns
    assert "transaction_status" in df_mapped.columns
    assert "is_suspicious" in df_mapped.columns


def test_schema_standardizer_no_duplicate_target_columns():
    """Verifies that having both alias and target in input DataFrame doesn't create duplicate columns."""
    df_raw = pd.DataFrame({
        "timestamp": ["2026-11-14 10:00:00"],
        "date_time": ["2026-11-14 10:00:00"],
        "tx_id": ["T1"],
    })
    standardizer = BankSchemaStandardizer()
    df_mapped = standardizer.standardize_column_names(df_raw)

    # df_mapped must not have duplicate 'timestamp' column names
    assert list(df_mapped.columns).count("timestamp") == 1
    assert "transaction_id" in df_mapped.columns


def test_clean_transactions_deduplication(sample_raw_transactions):
    """Verifies duplicate transactions are identified and eliminated."""
    preprocessor = DataPreprocessor()
    df_clean, stats = preprocessor.clean_transactions(sample_raw_transactions)

    assert stats["duplicates_removed"] == 1
    assert "TX_TEST_001" in df_clean["transaction_id"].values
    assert (df_clean["transaction_id"] == "TX_TEST_001").sum() == 1


def test_clean_transactions_invalid_handling(sample_raw_transactions):
    """Verifies zero/negative amounts and self-transfers are discarded."""
    preprocessor = DataPreprocessor()
    df_clean, stats = preprocessor.clean_transactions(sample_raw_transactions)

    # TX_TEST_002 is self-transfer
    assert "TX_TEST_002" not in df_clean["transaction_id"].values
    assert stats["self_transfers_dropped"] == 1

    # TX_TEST_003 is negative (-100), TX_TEST_004 is zero (0)
    assert "TX_TEST_003" not in df_clean["transaction_id"].values
    assert "TX_TEST_004" not in df_clean["transaction_id"].values
    assert stats["invalid_amounts_dropped"] == 2

    # Amount should be rounded to 2 decimal places (45000.758 -> 45000.76)
    row_5 = df_clean[df_clean["transaction_id"] == "TX_TEST_005"].iloc[0]
    assert row_5["amount"] == 45000.76


def test_clean_transactions_timestamp_normalization(sample_raw_transactions):
    """Verifies timestamps are standardized into ISO 8601 YYYY-MM-DD HH:MM:SS."""
    preprocessor = DataPreprocessor()
    df_clean, _ = preprocessor.clean_transactions(sample_raw_transactions)

    for ts in df_clean["timestamp"]:
        # Verify format matches YYYY-MM-DD HH:MM:SS
        assert len(ts) == 19
        assert ts[4] == "-" and ts[7] == "-" and ts[10] == " " and ts[13] == ":" and ts[16] == ":"


def test_categorical_feature_encoder():
    """Verifies Scikit-learn OrdinalEncoder operates properly and saves mappings."""
    encoder = CategoricalFeatureEncoder()
    df_sample = pd.DataFrame({
        "transaction_type": ["UPI_P2P", "IMPS", "UPI_MERCHANT", "UPI_P2P"],
        "transaction_status": ["SUCCESS", "FAILED", "SUCCESS", "PENDING"],
        "sender_bank": ["BANK_A", "BANK_B", "BANK_C", "BANK_A"],
        "receiver_bank": ["BANK_B", "BANK_C", "BANK_A", "BANK_B"],
        "pattern_type": ["NORMAL_P2P", "RAPID_PASS_THROUGH", "NORMAL_P2P", "FAN_OUT_SMURFING"],
    })

    df_encoded = encoder.fit_transform(df_sample)

    assert "transaction_type_code" in df_encoded.columns
    assert "transaction_status_code" in df_encoded.columns
    assert "sender_bank_code" in df_encoded.columns
    assert "receiver_bank_code" in df_encoded.columns
    assert "pattern_type_code" in df_encoded.columns

    # Verify repeatable codes
    assert df_encoded.loc[0, "transaction_type_code"] == df_encoded.loc[3, "transaction_type_code"]

    # Verify transform on new dataframe
    df_new = pd.DataFrame({
        "transaction_type": ["UPI_P2P"],
        "transaction_status": ["SUCCESS"],
        "sender_bank": ["BANK_A"],
        "receiver_bank": ["BANK_B"],
        "pattern_type": ["NORMAL_P2P"],
    })
    df_transformed = encoder.transform(df_new)
    assert df_transformed.loc[0, "transaction_type_code"] == df_encoded.loc[0, "transaction_type_code"]


def test_clean_accounts(sample_raw_accounts):
    """Verifies accounts catalog cleaning and deduplication."""
    preprocessor = DataPreprocessor()
    acc_clean, stats = preprocessor.clean_accounts(sample_raw_accounts)

    assert stats["duplicates_removed"] == 1
    assert len(acc_clean) == 2
    assert "ACC_A_001" in acc_clean["account_id"].values
    assert "ACC_B_001" in acc_clean["account_id"].values
    assert stats["mule_accounts"] == 1


def test_process_all_banks_execution():
    """Verifies multi-bank batch execution and output artifacts."""
    preprocessor = DataPreprocessor()
    results = preprocessor.process_all_banks(export_preprocessed=True)

    # Check bank ledger processing
    for bank_id in config.SIMULATED_BANKS:
        assert bank_id in results
        assert results[bank_id]["validation_valid"] is True
        b_key = bank_id.lower()
        csv_path = config.PREPROCESSED_DATA_DIR / f"{b_key}_cleaned.csv"
        json_path = config.PREPROCESSED_DATA_DIR / f"{b_key}_cleaned.json"
        assert csv_path.exists()
        assert json_path.exists()
        assert csv_path.stat().st_size > 0

    # Check accounts catalog
    assert "ACCOUNTS" in results
    assert (config.PREPROCESSED_DATA_DIR / "accounts_cleaned.csv").exists()
    assert (config.PREPROCESSED_DATA_DIR / "accounts_cleaned.json").exists()

    # Check categorical mappings file and report
    assert (config.MODELS_DIR / "encoders" / "categorical_encoders.json").exists()
    assert (config.REPORTS_DIR / "preprocessing_report.json").exists()
