"""
Unit and integration tests for RBIH NFPC Phase 2 Dataset Ingestion and Standardization.
Validates:
1. RBIH NFPC schema generation and field definitions.
2. Conversion to 4-bank qualified RINGTRACE AI standard tables.
3. MultiSourceDataManager integration with RBIH_NFPC_PHASE_2 data pillar.
"""

import pytest
import pandas as pd
from pathlib import Path

from src.data_sources.rbih_nfpc_loader import RBIHNFPCDataLoader
from src.data_sources.manager import MultiSourceDataManager


def test_rbih_nfpc_sample_generation():
    """Verifies that synthetic RBIH NFPC benchmark conforms to the competition schema."""
    loader = RBIHNFPCDataLoader()
    acc_df, tx_df, lbl_df, cust_df = loader.generate_rbih_nfpc_sample(
        num_accounts=100,
        num_transactions=500,
        mule_ratio=0.10,
    )

    # Accounts Table Schema
    assert len(acc_df) == 100
    assert "account_id" in acc_df.columns
    assert "branch_code" in acc_df.columns
    assert "scheme_code" in acc_df.columns
    assert "kyc_compliant" in acc_df.columns
    assert acc_df["account_id"].iloc[0].startswith("ACCT_")

    # Labels Table Schema
    assert len(lbl_df) == 100
    assert "account_id" in lbl_df.columns
    assert "is_mule" in lbl_df.columns
    assert lbl_df["is_mule"].sum() > 0

    # Transactions Table Schema
    assert len(tx_df) > 0
    assert "transaction_id" in tx_df.columns
    assert "account_id" in tx_df.columns
    assert "txn_type" in tx_df.columns
    assert "channel" in tx_df.columns
    assert "counterparty_id" in tx_df.columns
    assert set(tx_df["txn_type"].unique()).issubset({"D", "C"})

    # Customers Table Schema
    assert len(cust_df) == 100
    assert "customer_id" in cust_df.columns
    assert "pan_available" in cust_df.columns


def test_rbih_conversion_to_ringtrace_standard():
    """Verifies standard 4-bank transformation from RBIH NFPC schema."""
    loader = RBIHNFPCDataLoader()
    acc_df, tx_df, lbl_df, _ = loader.generate_rbih_nfpc_sample(
        num_accounts=60,
        num_transactions=300,
        mule_ratio=0.15,
    )

    std_acc, std_tx, std_rings = loader.convert_to_ringtrace_standard(acc_df, tx_df, lbl_df)

    # Standard Accounts
    assert len(std_acc) == 60
    assert "account_id" in std_acc.columns
    assert "bank_id" in std_acc.columns
    assert "is_mule" in std_acc.columns
    assert all(":" in a for a in std_acc["account_id"])

    # Verify 4-bank presence
    banks = set(std_acc["bank_id"].unique())
    assert len(banks) > 1

    # Standard Directed Transactions
    assert len(std_tx) > 0
    assert "sender_account" in std_tx.columns
    assert "receiver_account" in std_tx.columns
    assert "amount" in std_tx.columns
    assert "transaction_type" in std_tx.columns
    assert "is_suspicious" in std_tx.columns

    # Standard Rings
    assert len(std_rings) > 0
    assert "ring_id" in std_rings.columns
    assert "member_accounts" in std_rings.columns


def test_multisource_data_manager_rbih():
    """Verifies that MultiSourceDataManager includes and standardizes RBIH NFPC Phase 2."""
    manager = MultiSourceDataManager()
    assert "RBIH_NFPC_PHASE_2" in manager.DATA_SOURCES

    summary_df = manager.get_source_comparison_summary()
    assert "RBIH_NFPC_PHASE_2" in summary_df["Source Key"].values

    # Load and standardize through manager interface
    acc_df, tx_df, rings_df = manager.load_and_standardize_source("RBIH_NFPC_PHASE_2")
    assert len(acc_df) > 0
    assert len(tx_df) > 0
    assert len(rings_df) > 0
