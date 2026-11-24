"""
Unit tests for Multi-Source Data Strategy:
- IBM AMLSim Adapter
- IBM AML-Data Loader
- PaySim Mobile Money Loader
- MultiSourceDataManager
"""

import pytest
import pandas as pd
from src.data_sources.amlsim_loader import AMLSimAdapter
from src.data_sources.ibm_amldata_loader import IBMAMLDataLoader
from src.data_sources.paysim_loader import PaySimLoader
from src.data_sources.manager import MultiSourceDataManager


def test_amlsim_adapter_generation_and_conversion():
    adapter = AMLSimAdapter(seed=42)
    accs, txs, alerts = adapter.generate_amlsim_dataset(num_accounts=50, num_alert_patterns=3)

    assert len(accs) == 50
    assert len(txs) > 0
    assert len(alerts) == 3
    assert "IS_SAR" in txs.columns

    # Standard conversion test
    std_acc, std_tx, std_rings = adapter.convert_to_ringtrace_standard(accs, txs, alerts)
    assert "account_id" in std_acc.columns
    assert "transaction_id" in std_tx.columns
    assert "ring_id" in std_rings.columns
    assert (std_tx["amount"] > 0).all()


def test_ibm_amldata_loader():
    loader = IBMAMLDataLoader(seed=42)
    amldata_df = loader.generate_amldata_dataset(num_accounts=40, num_transactions=200)

    assert len(amldata_df) == 200
    assert "From Bank" in amldata_df.columns
    assert "To Bank" in amldata_df.columns
    assert "Is Laundering" in amldata_df.columns

    # Standard conversion
    std_acc, std_tx, std_rings = loader.convert_to_ringtrace_standard(amldata_df)
    assert len(std_acc) > 0
    assert len(std_tx) == len(amldata_df)
    assert len(std_rings) > 0


def test_paysim_loader():
    loader = PaySimLoader(seed=42)
    paysim_df = loader.generate_paysim_sample(num_transactions=250)

    assert len(paysim_df) == 250
    assert "step" in paysim_df.columns
    assert "type" in paysim_df.columns
    assert "isFraud" in paysim_df.columns

    # Standard conversion
    std_acc, std_tx, std_rings = loader.convert_to_ringtrace_standard(paysim_df)
    assert len(std_acc) > 0
    assert len(std_tx) == len(paysim_df)


def test_multi_source_data_manager():
    manager = MultiSourceDataManager()
    summary = manager.get_source_comparison_summary()

    assert len(summary) == 5
    source_keys = set(summary["Source Key"])
    assert source_keys == {
        "OUR_UPI_SIMULATOR",
        "IBM_AMLSIM",
        "IBM_AMLDATA",
        "PAYSIM",
        "RBIH_NFPC_PHASE_2",
    }
