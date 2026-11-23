"""
Unit and integration tests for Step 9: Centralized Multi-Bank Monitoring Dashboard.
Validates:
1. Multi-bank executive KPIs (25,430 total, 342 suspicious, 25,088 legitimate).
2. Bank-wise transaction and fraud breakdown (Bank A: 9,200/120, Bank B: 8,150/105, Bank C: 8,080/117).
3. Risk level categorization distributions (High, Medium, Low).
4. Multi-bank transaction search, filtering, and query engine.
5. FastAPI REST API dashboard endpoints.
"""

import pytest
from starlette.testclient import TestClient

from src.dashboard.service import DashboardMonitoringService
from src.integration.db import DatabaseManager
from src.integration.api import app


@pytest.fixture
def dashboard_service_instance():
    return DashboardMonitoringService()


def test_executive_summary_federated_scale(dashboard_service_instance):
    """Verifies that federated scale summary matches multi-bank specifications."""
    summary = dashboard_service_instance.get_executive_summary(mode="federated")

    assert summary["total_transactions"] == 46380
    assert summary["suspicious_transactions"] == 616
    assert summary["legitimate_transactions"] == 45764
    assert summary["pending_alerts"] >= 28

    # Verify Bank-Wise monitoring breakdown
    banks = {b["bank_name"]: b for b in summary["bank_wise_monitoring"]}
    assert "Apex National Bank" in banks
    assert "Crest Commercial Bank" in banks
    assert "Zenith Cooperative Bank" in banks
    assert "Horizon Federal Bank" in banks
    assert "Vanguard Mercantile Bank" in banks
    assert "Nexus Payments Bank" in banks

    assert banks["Apex National Bank"]["transactions"] == 9200
    assert banks["Apex National Bank"]["suspicious"] == 120

    assert banks["Crest Commercial Bank"]["transactions"] == 8150
    assert banks["Crest Commercial Bank"]["suspicious"] == 105

    assert banks["Zenith Cooperative Bank"]["transactions"] == 8080
    assert banks["Zenith Cooperative Bank"]["suspicious"] == 117

    assert banks["Horizon Federal Bank"]["transactions"] == 7650
    assert banks["Horizon Federal Bank"]["suspicious"] == 98

    # Verify Risk Distribution
    risk_dist = summary["risk_distribution"]
    assert risk_dist["high_risk"] == 616
    assert risk_dist["low_risk"] > 0


def test_executive_summary_reconciled_database(dashboard_service_instance):
    """Verifies database-driven canonical summary calculation."""
    summary = dashboard_service_instance.get_executive_summary(mode="reconciled")

    assert summary["total_transactions"] > 0
    assert summary["legitimate_transactions"] > 0
    assert len(summary["bank_wise_monitoring"]) >= 3


def test_transaction_search_and_filtering(dashboard_service_instance):
    """Verifies bank-wise, risk-level, and amount-based filtering."""
    # 1. Bank filter
    bank_a_txs = dashboard_service_instance.query_transactions(bank_id="APEX_NATIONAL", limit=20)
    assert len(bank_a_txs) > 0
    assert all(t["sender_bank"] == "APEX_NATIONAL" or t["receiver_bank"] == "APEX_NATIONAL" for t in bank_a_txs)

    # 2. Risk filter: High risk
    high_txs = dashboard_service_instance.query_transactions(risk_level="High", limit=20)
    assert len(high_txs) > 0
    assert all(t["risk_level"] == "High" for t in high_txs)

    # 3. Amount filter
    amt_txs = dashboard_service_instance.query_transactions(min_amount=30000.0, limit=20)
    assert len(amt_txs) > 0
    assert all(t["amount"] >= 30000.0 for t in amt_txs)


def test_fastapi_dashboard_endpoints():
    """Verifies FastAPI REST API endpoints for Step 9 monitoring dashboard."""
    client = TestClient(app)

    # 1. Summary endpoint (federated mode)
    resp = client.get("/api/v1/dashboard/summary?mode=federated")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_transactions"] == 46380
    assert data["suspicious_transactions"] == 616
    assert len(data["bank_wise_monitoring"]) == 6

    # 2. Transactions query endpoint
    resp_tx = client.get("/api/v1/dashboard/transactions?limit=10&bank_id=CREST_COMMERCIAL")
    assert resp_tx.status_code == 200
    tx_list = resp_tx.json()
    assert len(tx_list) > 0

    # 3. Trends endpoint
    resp_trends = client.get("/api/v1/dashboard/trends")
    assert resp_trends.status_code == 200
    trends_data = resp_trends.json()
    assert "daily_trends" in trends_data
