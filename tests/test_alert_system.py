"""
Unit and integration tests for Step 8: Fraud Alert and Notification System.
Validates:
1. Automatic alert generation from suspicious transactions.
2. Risk level categorization (High, Medium, Low).
3. Duplicate alert prevention (idempotent submission).
4. Status tracking & investigation workflow (Pending -> Under Review -> Escalated -> Resolved).
5. Multi-bank notification dispatching (simulated email / in-app).
6. FastAPI REST API endpoints.
"""

import pytest
from datetime import datetime, timezone
from starlette.testclient import TestClient

from src.alerts.engine import AlertEngine
from src.alerts.notifier import AlertNotifier
from src.integration.db import DatabaseManager
from src.integration.api import app


@pytest.fixture
def alert_engine_instance(tmp_path):
    """Provides isolated AlertEngine instance backed by temporary SQLite DB."""
    test_db_url = f"sqlite:///{tmp_path / 'test_alerts.db'}"
    db = DatabaseManager(db_url=test_db_url)
    notifier = AlertNotifier()
    return AlertEngine(db_manager=db, notifier=notifier)


def test_alert_generation_from_suspicious_transaction(alert_engine_instance):
    """Verifies that suspicious transactions generate structured alerts matching specifications."""
    tx = {
        "transaction_id": "TXN10245",
        "bank_id": "Bank B",
        "sender_account": "BANK_ACC_00102",
        "receiver_account": "BANK_ACC_00551",
        "amount": 85000.0,
        "timestamp": "2026-11-22 02:45:10",
        "fraud_probability": 0.96,
        "risk_level": "High",
        "trigger_reasons": ["RAPID_BURST_FORWARDING", "CROSS_BANK_HIGH_VALUE", "NOCTURNAL_OFF_HOURS"],
    }

    result = alert_engine_instance.generate_alert(tx)

    assert result["transaction_id"] == "TXN10245"
    assert result["bank_id"] == "BANK_B"
    assert result["amount"] == 85000.0
    assert result["fraud_probability"] == 0.96
    assert result["risk_level"] == "High"
    assert result["status"] == "Pending"
    assert result["is_duplicate"] is False
    assert "Suspicious transaction detected" in result["recommendation"]
    assert "Illustrative example" in result["disclaimer"]
    assert len(result["notified_channels"]) > 0
    assert "EMAIL" in result["notified_channels"]


def test_alert_duplicate_prevention(alert_engine_instance):
    """Verifies that submitting the same transaction ID twice does NOT create a duplicate alert."""
    tx = {
        "transaction_id": "TXN_DUP_001",
        "bank_id": "Bank A",
        "amount": 55000.0,
        "fraud_probability": 0.91,
        "risk_level": "High",
    }

    # 1. First submission -> Creates alert
    first_res = alert_engine_instance.generate_alert(tx)
    assert first_res["is_duplicate"] is False
    alert_id = first_res["alert_id"]

    # 2. Duplicate submission -> Catches duplicate, does not duplicate database row
    second_res = alert_engine_instance.generate_alert(tx)
    assert second_res["is_duplicate"] is True
    assert second_res["alert_id"] == alert_id
    assert "Duplicate alert prevented" in second_res["message"]

    # 3. Verify database count is exactly 1
    all_alerts = alert_engine_instance.query_alerts(limit=10)
    matching = [a for a in all_alerts if a["transaction_id"] == "TXN_DUP_001"]
    assert len(matching) == 1


def test_risk_level_categorization(alert_engine_instance):
    """Verifies automatic risk level categorization based on fraud probability thresholds."""
    # High Risk (p >= 0.70)
    tx_high = {"transaction_id": "TX_RISK_HIGH", "bank_id": "Bank B", "amount": 90000.0, "fraud_probability": 0.88}
    res_high = alert_engine_instance.generate_alert(tx_high)
    assert res_high["risk_level"] == "High"

    # Medium Risk (0.35 <= p < 0.70)
    tx_med = {"transaction_id": "TX_RISK_MED", "bank_id": "Bank A", "amount": 25000.0, "fraud_probability": 0.52}
    res_med = alert_engine_instance.generate_alert(tx_med)
    assert res_med["risk_level"] == "Medium"

    # Low Risk (p < 0.35)
    tx_low = {"transaction_id": "TX_RISK_LOW", "bank_id": "Bank C", "amount": 1200.0, "fraud_probability": 0.12}
    res_low = alert_engine_instance.generate_alert(tx_low)
    assert res_low["risk_level"] == "Low"


def test_alert_status_workflow_transitions(alert_engine_instance):
    """Verifies state progression across: Pending -> Under Review -> Escalated -> Resolved."""
    tx = {"transaction_id": "TX_STATUS_TEST", "bank_id": "Bank C", "amount": 60000.0, "fraud_probability": 0.95}
    alert = alert_engine_instance.generate_alert(tx)
    alert_id = alert["alert_id"]

    assert alert["status"] == "Pending"

    # 1. Under Review
    res_review = alert_engine_instance.update_alert_status(
        alert_id=alert_id,
        new_status="Under Review",
        notes="Reviewing cross-bank rapid turnaround with Bank C analyst.",
        updated_by="Officer_01",
    )
    assert res_review["status"] == "Under Review"
    assert res_review["assigned_to"] == "Officer_01"
    assert len(res_review["investigation_notes"]) == 1

    # 2. Escalated
    res_esc = alert_engine_instance.update_alert_status(
        alert_id=alert_id,
        new_status="Escalated",
        notes="Confirmed mule ring hop. Escalating to Inter-Bank Taskforce.",
        updated_by="Supervisor_02",
    )
    assert res_esc["status"] == "Escalated"
    assert len(res_esc["investigation_notes"]) == 2

    # 3. Resolved
    res_res = alert_engine_instance.update_alert_status(
        alert_id=alert_id,
        new_status="Resolved",
        notes="Account flagged across federation; SAR report filed.",
        updated_by="Supervisor_02",
    )
    assert res_res["status"] == "Resolved"
    assert len(res_res["investigation_notes"]) == 3

    # 4. Invalid status should raise ValueError
    with pytest.raises(ValueError):
        alert_engine_instance.update_alert_status(alert_id=alert_id, new_status="INVALID_STATUS")


def test_multi_bank_notification_dispatch(alert_engine_instance):
    """Verifies that multi-bank alerts dispatch properly formatted emails to designated compliance desks."""
    tx_b = {
        "transaction_id": "TXN_NOTIF_B",
        "bank_id": "Bank B",
        "amount": 85000.0,
        "fraud_probability": 0.96,
        "risk_level": "High",
    }
    alert_engine_instance.generate_alert(tx_b)

    history = alert_engine_instance.notifier.get_dispatch_history()
    email_dispatches = [d for d in history if d["channel"] == "EMAIL" and d["alert_id"] == "ALT_NOTIF_B"]
    assert len(email_dispatches) == 1
    email = email_dispatches[0]

    assert email["recipient"] == "fraud-monitoring@bank-b.in"
    assert "HIGH RISK" in email["subject"]
    assert "₹85,000" in email["body"]
    assert "96%" in email["body"]
    assert "Suspicious transaction detected" in email["body"]


def test_fastapi_alert_endpoints():
    """Verifies FastAPI REST API endpoints for alert generation, query, and status update."""
    client = TestClient(app)
    import time
    test_tx_id = f"TX_API_{int(time.time() * 1000)}"

    # 1. Generate alert endpoint
    payload = {
        "transaction_id": test_tx_id,
        "bank_id": "Bank B",
        "sender_account": "ACC_TEST_01",
        "receiver_account": "ACC_TEST_02",
        "amount": 78000.0,
        "fraud_probability": 0.93,
        "risk_level": "High",
        "trigger_reasons": ["RAPID_BURST_FORWARDING"],
    }
    resp = client.post("/api/v1/alerts/generate", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["transaction_id"] == test_tx_id
    assert data["bank_id"] == "BANK_B"
    assert data["status"] == "Pending"
    alert_id = data["alert_id"]

    # 2. Test Duplicate Submission via API
    resp_dup = client.post("/api/v1/alerts/generate", json=payload)
    assert resp_dup.status_code == 200
    data_dup = resp_dup.json()
    assert data_dup["is_duplicate"] is True

    # 3. List Alerts Endpoint with filter
    resp_list = client.get("/api/v1/alerts?bank_id=BANK_B")
    assert resp_list.status_code == 200
    alerts_list = resp_list.json()
    assert len(alerts_list) >= 1
    assert any(a["alert_id"] == alert_id for a in alerts_list)

    # 4. Detail Endpoint
    resp_detail = client.get(f"/api/v1/alerts/{alert_id}")
    assert resp_detail.status_code == 200
    assert resp_detail.json()["alert_id"] == alert_id

    # 5. Status Update Endpoint
    update_payload = {
        "status": "Under Review",
        "notes": "FastAPI integration test investigation note.",
        "updated_by": "TestClient_Officer",
    }
    resp_update = client.patch(f"/api/v1/alerts/{alert_id}/status", json=update_payload)
    assert resp_update.status_code == 200
    assert resp_update.json()["status"] == "Under Review"

    # 6. Stats Endpoint
    resp_stats = client.get("/api/v1/alerts/stats")
    assert resp_stats.status_code == 200
    stats_data = resp_stats.json()
    assert stats_data["total_alerts"] >= 1
    assert "by_bank" in stats_data
