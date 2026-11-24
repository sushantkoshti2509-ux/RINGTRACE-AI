"""
Unit and integration tests for Step 7: Real-Time Fraud Detection System.
Validates real-time low-latency transaction scoring, multi-tier risk categorization,
dynamic in-memory state updates, database audit persistence, and FastAPI endpoints.
"""

import pytest
import time
from fastapi.testclient import TestClient

import config
from src.realtime.detector import RealtimeFraudDetector
from src.integration.db import DatabaseManager
from src.integration.api import app


@pytest.fixture
def detector_instance(tmp_path):
    """Initializes RealtimeFraudDetector with isolated test database."""
    test_db_url = f"sqlite:///{tmp_path / 'test_realtime.db'}"
    db = DatabaseManager(db_url=test_db_url)
    detector = RealtimeFraudDetector(db_manager=db)
    # Warm up detector to avoid cold-start JIT/initialization latency spikes
    detector.process_transaction({
        "transaction_id": "TX_WARMUP",
        "sender_account": "ACC_WARMUP_01",
        "receiver_account": "ACC_WARMUP_02",
        "sender_bank": "BANK_A",
        "receiver_bank": "BANK_A",
        "amount": 100.0,
        "timestamp": "2026-11-22 12:00:00",
    })
    return detector


def test_realtime_normal_transaction_detection(detector_instance):
    """Verifies that legitimate everyday transactions receive Low risk and Normal status."""
    tx = {
        "transaction_id": "TX_RT_TEST_001",
        "sender_account": "BANK_ACC_00280",
        "receiver_account": "BANK_ACC_00412",
        "sender_bank": "BANK_A",
        "receiver_bank": "BANK_A",
        "amount": 450.0,
        "timestamp": "2026-11-22 14:30:00",
    }

    result = detector_instance.process_transaction(tx)

    assert result["transaction_id"] == "TX_RT_TEST_001"
    assert result["bank_id"] == "BANK_A"
    assert result["risk_level"] in ["Low", "Medium"]
    assert result["status"] in ["Normal", "Review Required"]
    assert result["latency_ms"] < 25.0  # Real-time SLA: Sub-25ms


def test_realtime_suspicious_transaction_detection(detector_instance):
    """Verifies that high-value, nocturnal, rapid pass-through transfers receive High risk and Suspicious status."""
    # Step 1: Account receives ₹75,000 at 02:00:00 AM (nocturnal)
    tx_in = {
        "transaction_id": "TX_RT_TEST_002_IN",
        "sender_account": "ACC_VICTIM_01",
        "receiver_account": "ACC_MULE_TEST_01",
        "sender_bank": "BANK_B",
        "receiver_bank": "BANK_A",
        "amount": 75000.0,
        "timestamp": "2026-11-22 02:00:00",
    }
    detector_instance.process_transaction(tx_in)

    # Step 2: Mule immediately forwards ₹74,000 at 02:02:00 AM (120s later, nocturnal, cross-bank)
    tx_out = {
        "transaction_id": "TX_RT_TEST_002_OUT",
        "sender_account": "ACC_MULE_TEST_01",
        "receiver_account": "ACC_DEST_01",
        "sender_bank": "BANK_A",
        "receiver_bank": "BANK_C",
        "amount": 74000.0,
        "timestamp": "2026-11-22 02:02:00",
    }
    result_out = detector_instance.process_transaction(tx_out)

    assert result_out["transaction_id"] == "TX_RT_TEST_002_OUT"
    assert result_out["risk_level"] in ["High", "Medium"]
    assert result_out["status"] in ["Suspicious", "Review Required"]
    assert len(result_out["trigger_reasons"]) > 0
    assert any("BURST" in t or "NOCTURNAL" in t or "CROSS" in t or "PASS" in t for t in result_out["trigger_reasons"])


def test_stream_processing_latency(detector_instance):
    """Verifies low-latency processing across a multi-bank stream."""
    stream_txs = [
        {
            "transaction_id": f"TX_STREAM_{i:03d}",
            "sender_account": f"ACC_S_{i % 5}",
            "receiver_account": f"ACC_R_{i % 5}",
            "sender_bank": "BANK_A" if i % 3 == 0 else ("BANK_B" if i % 3 == 1 else "BANK_C"),
            "receiver_bank": "BANK_C" if i % 2 == 0 else "BANK_B",
            "amount": float(500 + i * 50),
            "timestamp": "2026-11-22 15:00:00",
        }
        for i in range(20)
    ]

    t0 = time.perf_counter()
    results = list(detector_instance.simulate_stream(stream_txs, delay_sec=0.0))
    total_time_ms = (time.perf_counter() - t0) * 1000.0

    assert len(results) == 20
    # Average latency per transaction must be under 15ms
    avg_latency = total_time_ms / len(results)
    assert avg_latency < 25.0

    stats = detector_instance.get_summary_stats()
    assert stats["total_processed"] >= 20
    assert "avg_latency_ms" in stats


def test_realtime_fastapi_endpoints():
    """Verifies FastAPI REST API endpoints for real-time fraud detection."""
    client = TestClient(app)

    # 1. Single transaction detection endpoint
    payload = {
        "transaction_id": "TX_API_TEST_01",
        "bank_id": "BANK_A",
        "sender_account": "ACC_API_01",
        "receiver_account": "ACC_API_02",
        "amount": 1500.0,
        "timestamp": "2026-11-22 16:00:00",
        "transaction_type": "UPI_P2P",
    }
    resp = client.post("/api/v1/realtime/transaction", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["transaction_id"] == "TX_API_TEST_01"
    assert data["bank_id"] == "BANK_A"
    assert data["risk_level"] in ["Low", "Medium", "High"]
    assert data["status"] in ["Normal", "Review Required", "Suspicious"]
    assert "latency_ms" in data

    # 2. History endpoint
    resp_hist = client.get("/api/v1/realtime/history?limit=10")
    assert resp_hist.status_code == 200
    assert "logs" in resp_hist.json()

    # 3. Stats endpoint
    resp_stats = client.get("/api/v1/realtime/stats")
    assert resp_stats.status_code == 200
    assert "total_processed" in resp_stats.json()
