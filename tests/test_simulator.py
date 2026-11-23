"""
Unit tests for RINGTRACE AI Simulator and Data Preprocessing.
"""

import pytest
import pandas as pd
import config
from src.simulator.generator import UPISimulator
from src.preprocessing.clean import DataPreprocessor
from src.utils.validation import validate_accounts_dataframe, validate_transactions_dataframe


def test_upi_simulator_generation():
    sim = UPISimulator(seed=123)
    accounts_df, transactions_df, mule_rings_df, bank_ledgers = sim.generate_all(
        num_accounts=100, num_rings=4
    )

    assert len(accounts_df) >= 100
    assert len(transactions_df) > 0
    assert len(mule_rings_df) == 4
    assert set(bank_ledgers.keys()) == set(config.SIMULATED_BANKS)

    # Ensure mule accounts exist
    assert accounts_df["is_mule"].sum() > 0

    # Ensure all transactions have positive amounts
    assert (transactions_df["amount"] > 0).all()

    # Ensure no self-transfers
    assert (transactions_df["sender_account"] != transactions_df["receiver_account"]).all()


def test_data_preprocessor_and_validation():
    sim = UPISimulator(seed=42)
    accounts_df, transactions_df, _, _ = sim.generate_all(num_accounts=80, num_rings=3)

    cleaner = DataPreprocessor()
    acc_clean, tx_clean, val_report = cleaner.run_cleaning_pipeline(accounts_df, transactions_df)

    assert val_report["accounts_valid"] is True
    assert val_report["transactions_valid"] is True
    assert len(acc_clean) == len(accounts_df)
    assert len(tx_clean) == len(transactions_df)
