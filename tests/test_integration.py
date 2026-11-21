"""
Unit and integration tests for Step 3: Multi-Bank Data Integration.
Validates centralized schema mapping, dual-ledger cross-bank reconciliation,
discrepancy handling, database persistence, and FastAPI REST endpoints.
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
from starlette.testclient import TestClient

import config
from src.integration.schemas import TransactionCreate, BankSubmissionRequest
from src.integration.db import DatabaseManager, IntegratedTransactionModel
from src.integration.integrator import MultiBankDataIntegrator
from src.integration.api import app


@pytest.fixture
def mock_bank_ledgers():
    """Generates controlled synthetic ledgers for Bank A and Bank B with known dual matches."""
    # Bank A's ledger contains:
    # 1. TX_INT_001 (Bank A -> Bank B, inter-bank, debited at Bank A)
    # 2. TX_INT_002 (Bank A -> Bank A, intra-bank internal transfer)
    # 3. TX_INT_003 (Bank A -> Bank B, but with an amount discrepancy in Bank B)
    df_bank_a = pd.DataFrame([
        {
            "transaction_id": "TX_INT_001",
            "customer_id": "CUST_A_001",
            "sender_account": "ACC_A_001",
            "receiver_account": "ACC_B_001",
            "sender_bank": "BANK_A",
            "receiver_bank": "BANK_B",
            "amount": 25000.0,
            "timestamp": "2026-11-14 10:00:00",
            "transaction_type": "UPI_P2P",
            "transaction_status": "SUCCESS",
            "is_suspicious": 0,
            "ring_id": "NONE",
            "pattern_type": "NORMAL_P2P",
        },
        {
            "transaction_id": "TX_INT_002",
            "customer_id": "CUST_A_002",
            "sender_account": "ACC_A_002",
            "receiver_account": "ACC_A_003",
            "sender_bank": "BANK_A",
            "receiver_bank": "BANK_A",
            "amount": 1200.0,
            "timestamp": "2026-11-14 10:05:00",
            "transaction_type": "UPI_P2P",
            "transaction_status": "SUCCESS",
            "is_suspicious": 0,
            "ring_id": "NONE",
            "pattern_type": "NORMAL_P2P",
        },
        {
            "transaction_id": "TX_INT_003",
            "customer_id": "CUST_A_003",
            "sender_account": "ACC_A_004",
            "receiver_account": "ACC_B_002",
            "sender_bank": "BANK_A",
            "receiver_bank": "BANK_B",
            "amount": 5000.0,  # Bank A logs ₹5,000
            "timestamp": "2026-11-14 10:10:00",
            "transaction_type": "UPI_P2P",
            "transaction_status": "SUCCESS",
            "is_suspicious": 1,
            "ring_id": "RING_TEST_01",
            "pattern_type": "RAPID_PASS_THROUGH",
        },
    ])

    # Bank B's ledger contains:
    # 1. TX_INT_001 (Bank A -> Bank B, credited at Bank B - perfect dual match)
    # 2. TX_INT_003 (Bank A -> Bank B, with discrepancy: amount 4990.0)
    # 3. TX_INT_004 (Bank B -> Bank C, unilateral from Bank B's perspective)
    df_bank_b = pd.DataFrame([
        {
            "transaction_id": "TX_INT_001",
            "customer_id": "CUST_B_001",
            "sender_account": "ACC_A_001",
            "receiver_account": "ACC_B_001",
            "sender_bank": "BANK_A",
            "receiver_bank": "BANK_B",
            "amount": 25000.0,
            "timestamp": "2026-11-14 10:00:00",
            "transaction_type": "UPI_P2P",
            "transaction_status": "SUCCESS",
            "is_suspicious": 0,
            "ring_id": "NONE",
            "pattern_type": "NORMAL_P2P",
        },
        {
            "transaction_id": "TX_INT_003",
            "customer_id": "CUST_B_002",
            "sender_account": "ACC_A_004",
            "receiver_account": "ACC_B_002",
            "sender_bank": "BANK_A",
            "receiver_bank": "BANK_B",
            "amount": 4990.0,  # Bank B logs ₹4,990 (fee deduction or discrepancy)
            "timestamp": "2026-11-14 10:10:00",
            "transaction_type": "UPI_P2P",
            "transaction_status": "SUCCESS",
            "is_suspicious": 1,
            "ring_id": "RING_TEST_01",
            "pattern_type": "RAPID_PASS_THROUGH",
        },
        {
            "transaction_id": "TX_INT_004",
            "customer_id": "CUST_B_003",
            "sender_account": "ACC_B_003",
            "receiver_account": "ACC_C_001",
            "sender_bank": "BANK_B",
            "receiver_bank": "BANK_C",
            "amount": 8000.0,
            "timestamp": "2026-11-14 10:15:00",
            "transaction_type": "IMPS",
            "transaction_status": "SUCCESS",
            "is_suspicious": 0,
            "ring_id": "NONE",
            "pattern_type": "NORMAL_P2P",
        },
    ])

    return {"BANK_A": df_bank_a, "BANK_B": df_bank_b}


def test_dual_ledger_reconciliation(mock_bank_ledgers, tmp_path):
    """Verifies that inter-bank twins are identified, reconciled, and deduplicated."""
    test_db_url = f"sqlite:///{tmp_path / 'test_integration.db'}"
    db = DatabaseManager(db_url=test_db_url)
    integrator = MultiBankDataIntegrator(db_manager=db)

    df_integrated, metrics = integrator.integrate_ledgers(mock_bank_ledgers, export_artifacts=False)

    # 3 rows from A + 3 rows from B = 6 raw rows
    assert metrics["total_raw_ledger_records"] == 6

    # TX_INT_001 and TX_INT_003 are present in both banks (2 dual matches)
    # TX_INT_002 and TX_INT_004 are single ledger entries
    # Total unique integrated transactions must be exactly 4!
    assert len(df_integrated) == 4
    assert metrics["total_integrated_transactions"] == 4
    assert metrics["dual_ledger_reconciled"] == 2
    assert metrics["single_ledger_unilateral"] == 2

    # Verify TX_INT_001 reconciliation details
    row_001 = df_integrated[df_integrated["transaction_id"] == "TX_INT_001"].iloc[0]
    assert row_001["reconciliation_status"] == "RECONCILED"
    assert set(row_001["participating_banks"]) == {"BANK_A", "BANK_B"}
    assert row_001["primary_source_bank"] == "BANK_A"
    assert bool(row_001["is_cross_bank"]) is True


def test_discrepancy_detection(mock_bank_ledgers, tmp_path):
    """Verifies that amount mismatches between two bank records are logged as discrepancies."""
    test_db_url = f"sqlite:///{tmp_path / 'test_discrepancy.db'}"
    db = DatabaseManager(db_url=test_db_url)
    integrator = MultiBankDataIntegrator(db_manager=db)

    _, metrics = integrator.integrate_ledgers(mock_bank_ledgers, export_artifacts=False)

    # TX_INT_003 had ₹5,000 at Bank A and ₹4,990 at Bank B
    assert metrics["discrepancy_count"] == 1
    disc = metrics["discrepancies"][0]
    assert disc["transaction_id"] == "TX_INT_003"
    assert disc["field"] == "amount"
    assert disc["values"]["BANK_A"] == 5000.0
    assert disc["values"]["BANK_B"] == 4990.0


def test_database_persistence_and_query(mock_bank_ledgers, tmp_path):
    """Verifies SQLAlchemy persistence into SQLite database and querying."""
    test_db_url = f"sqlite:///{tmp_path / 'test_query.db'}"
    db = DatabaseManager(db_url=test_db_url)
    integrator = MultiBankDataIntegrator(db_manager=db)

    df_integrated, _ = integrator.integrate_ledgers(mock_bank_ledgers, export_artifacts=False)
    inserted = db.save_integrated_transactions(df_integrated)
    assert inserted == 4

    # Query all
    results_all = db.query_transactions()
    assert len(results_all) == 4

    # Query filtered by bank
    results_a = db.query_transactions(bank_id="BANK_A")
    # In mock, TX_INT_001 (A->B), TX_INT_002 (A->A), TX_INT_003 (A->B) involve Bank A = 3
    assert len(results_a) == 3

    # Query filtered by suspicion
    suspicious = db.query_transactions(is_suspicious=1)
    assert len(suspicious) == 1
    assert suspicious[0]["transaction_id"] == "TX_INT_003"


def test_full_pipeline_multi_bank_integration():
    """Verifies full multi-bank integration using actual preprocessed bank files."""
    integrator = MultiBankDataIntegrator()
    df_integrated, metrics = integrator.load_preprocessed_banks_and_integrate(export_artifacts=True)

    assert not df_integrated.empty
    assert metrics["total_raw_ledger_records"] > 20000
    assert metrics["total_integrated_transactions"] > 10000
    assert metrics["dual_ledger_reconciled"] > 8000
    assert metrics["discrepancy_count"] == 0

    # Verify generated artifact files exist
    assert (config.INTEGRATED_DATA_DIR / "transactions_integrated.csv").exists()
    assert (config.INTEGRATED_DATA_DIR / "transactions_integrated.json").exists()
    assert (config.INTEGRATED_DATA_DIR / "cross_bank_flows.csv").exists()
    assert (config.REPORTS_DIR / "integration_report.json").exists()
    assert (config.PROCESSED_DATA_DIR / "transactions.csv").exists()


def test_fastapi_endpoints():
    """Verifies FastAPI REST API endpoints using TestClient."""
    client = TestClient(app)

    # 1. Health endpoint
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "HEALTHY"

    # 2. Root info endpoint
    resp_root = client.get("/")
    assert resp_root.status_code == 200
    assert "BANK_A" in resp_root.json()["participating_banks"]

    # 3. Query transactions
    resp_tx = client.get("/api/v1/transactions?limit=10")
    assert resp_tx.status_code == 200
    data = resp_tx.json()
    assert "transactions" in data
    assert len(data["transactions"]) <= 10

    # 4. Cross-bank flows
    resp_flows = client.get("/api/v1/cross-bank-flows")
    assert resp_flows.status_code == 200
    assert "flows" in resp_flows.json()

    # 5. Reconciliation summary
    resp_recon = client.get("/api/v1/reconciliation/summary")
    assert resp_recon.status_code == 200
    assert "total_integrated_transactions" in resp_recon.json()
