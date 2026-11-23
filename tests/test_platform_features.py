"""
Unit and integration tests for the Three Core Platform Intelligence Features:
1. Feature 1: Cross-Bank Fraud Network Detection (NetworkX, cycles, communities, turnaround)
2. Feature 2: Explainable AI (SHAP TreeExplainer & human template reason generator)
3. Feature 3: Fraud Investigation Assistant (Case manager, checklist, feedback & PDF generator)
"""

import pytest
import pandas as pd
import networkx as nx

from src.adapter.detection_adapter import DetectionAdapter
from src.cross_bank_network.graph_builder import CrossBankGraphBuilder
from src.cross_bank_network.network_analysis import CrossBankNetworkAnalyzer
from src.explainable_ai.shap_explainer import ModelSHAPExplainer
from src.explainable_ai.reason_generator import HumanExplanationGenerator
from src.investigation_assistant.case_manager import CaseManager
from src.investigation_assistant.report_generator import InvestigationReportGenerator
from src.integration.db import DatabaseManager


# -----------------------------------------------------------------------------
# Feature 1: Cross-Bank Fraud Network Tests
# -----------------------------------------------------------------------------
def test_cross_bank_graph_builder_and_metrics():
    """Verifies bank-qualified node generation and edge attributes."""
    transactions = pd.DataFrame([
        {"sender_account": "A101", "receiver_account": "B201", "sender_bank": "BANK_A", "receiver_bank": "BANK_B", "amount": 50000.0, "timestamp": "2026-11-22 01:00:00", "transaction_id": "TX_01"},
        {"sender_account": "B201", "receiver_account": "C301", "sender_bank": "BANK_B", "receiver_bank": "BANK_C", "amount": 45000.0, "timestamp": "2026-11-22 01:03:00", "transaction_id": "TX_02"},
        {"sender_account": "C301", "receiver_account": "A102", "sender_bank": "BANK_C", "receiver_bank": "BANK_A", "amount": 40000.0, "timestamp": "2026-11-22 01:06:00", "transaction_id": "TX_03"},
        {"sender_account": "A102", "receiver_account": "B202", "sender_bank": "BANK_A", "receiver_bank": "BANK_B", "amount": 35000.0, "timestamp": "2026-11-22 01:09:00", "transaction_id": "TX_04"},
        {"sender_account": "B202", "receiver_account": "B201", "sender_bank": "BANK_B", "receiver_bank": "BANK_B", "amount": 30000.0, "timestamp": "2026-11-22 01:12:00", "transaction_id": "TX_05"},
    ])

    builder = CrossBankGraphBuilder()
    G = builder.build_network_graph(transactions, use_qualified_ids=True)

    assert G.number_of_nodes() == 5
    assert G.number_of_edges() == 5
    assert "BANK_A:A101" in G.nodes
    assert "BANK_B:B201" in G.nodes

    # Verify edge data
    edge_data = G.get_edge_data("BANK_A:A101", "BANK_B:B201")
    assert edge_data["amount"] == 50000.0
    assert edge_data["is_cross_bank"] is True

    # Test Network Analysis
    analyzer = CrossBankNetworkAnalyzer(G)
    degrees = analyzer.get_degree_metrics()
    assert degrees["BANK_B:B201"]["in_degree"] == 2  # Receives from A101 and B202
    assert degrees["BANK_B:B201"]["out_degree"] == 1 # Sends to C301

    # Cycle Detection: B201 -> C301 -> A102 -> B202 -> B201 is a cycle!
    cycles = analyzer.detect_cycles()
    assert len(cycles) >= 1
    cycle_nodes = cycles[0]
    assert "BANK_B:B201" in cycle_nodes

    # Temporal rapid turnaround (B201 receives at 01:00:00, sends at 01:03:00 -> 180s < 600s)
    rapid = analyzer.analyze_temporal_turnaround(turnaround_threshold_sec=600.0)
    assert len(rapid) >= 1
    b201_rapid = [r for r in rapid if r["intermediary_account"] == "BANK_B:B201"]
    assert len(b201_rapid) >= 1
    assert b201_rapid[0]["time_gap_seconds"] == 180.0


# -----------------------------------------------------------------------------
# Feature 2: Explainable AI (XAI) Tests
# -----------------------------------------------------------------------------
def test_explainable_ai_shap_and_reasons():
    """Verifies SHAP attribution computation and human template explanation synthesis."""
    explainer = ModelSHAPExplainer()
    generator = HumanExplanationGenerator()

    sample_features = pd.Series({
        "account_age_days": 15.0,
        "in_degree": 8.0,
        "out_degree": 9.0,
        "fan_in_distinct": 6.0,
        "fan_out_distinct": 7.0,
        "pass_through_ratio": 0.94,
        "min_turnaround_time_sec": 120.0,
        "avg_turnaround_time_sec": 180.0,
        "velocity_1h_max": 6.0,
        "velocity_24h_max": 18.0,
        "velocity_score": 0.85,
        "cross_bank_tx_ratio": 0.75,
        "total_amount_in": 85000.0,
        "total_amount_out": 82000.0,
        "avg_amount_in": 10625.0,
        "avg_amount_out": 9111.0,
        "avg_amount_total": 9868.0,
        "high_value_tx_count": 3.0,
        "high_value_ratio": 0.35,
        "off_hours_tx_ratio": 0.50,
        "behavioral_risk_score": 0.88,
        "pagerank": 0.005,
        "clustering_coeff": 0.15,
        "net_flow_ratio": -0.03,
        "turnover_rate": 0.95,
        "min_time_gap_sec": 45.0,
        "tx_frequency_total": 17.0,
        "profile_type_MERCHANT": 0.0,
        "profile_type_REGULAR_P2P": 1.0,
        "profile_type_SALARIED": 0.0,
        "profile_type_STUDENT": 0.0,
        "bank_id_BANK_A": 0.0,
        "bank_id_BANK_B": 1.0,
        "bank_id_BANK_C": 0.0,
    })

    # 1. SHAP Explanation
    shap_res = explainer.explain_account(sample_features, top_k=5)
    assert "top_drivers" in shap_res
    assert len(shap_res["top_drivers"]) > 0
    top_driver = shap_res["top_drivers"][0]
    assert "feature" in top_driver
    assert "shap_value" in top_driver
    assert "direction" in top_driver

    # 2. Human Explanation Generator
    explanation = generator.generate_explanation(
        account_id="ACC_MULE_TEST",
        shap_explanation=shap_res,
        risk_tier="High",
    )
    assert explanation["account_id"] == "ACC_MULE_TEST"
    assert explanation["risk_tier"] == "High"
    assert len(explanation["bullet_reasons"]) >= 3
    assert "potential money mule activity" in explanation["ai_summary"]


# -----------------------------------------------------------------------------
# Feature 3: Fraud Investigation Assistant Tests
# -----------------------------------------------------------------------------
def test_investigation_case_manager_and_pdf(tmp_path):
    """Verifies case creation, checklist updates, feedback capture, and PDF generation."""
    test_db = f"sqlite:///{tmp_path / 'test_cases.db'}"
    db = DatabaseManager(db_url=test_db)
    manager = CaseManager(db_manager=db)
    report_gen = InvestigationReportGenerator()

    # 1. Create Case
    case_payload = {
        "case_id": "CASE-MR-001",
        "candidate_ring_id": "RING_001",
        "title": "Investigation Case #MR-001 - Cross-Bank Ring",
        "risk_score": 92.0,
        "risk_tier": "HIGH",
        "status": "Pending",
        "connected_accounts_count": 5,
        "banks_involved": "BANK_A,BANK_B,BANK_C",
        "total_volume": 200000.0,
        "transactions_count": 24,
        "detected_patterns": ["RAPID_PASS_THROUGH", "CIRCULAR_LAYERING"],
        "member_accounts": ["A101", "B201", "C301", "A102", "B202"],
        "ai_summary": "Five accounts across three banks demonstrate repeated rapid fund forwarding.",
    }
    saved_case, is_created = db.save_investigation_case(case_payload)
    assert is_created is True
    assert saved_case["case_id"] == "CASE-MR-001"

    # 2. Update Checklist
    up_chk = manager.update_checklist("CASE-MR-001", "step_1", True)
    assert up_chk["checklist_state"]["step_1"] is True

    # 3. Update Status
    up_stat = manager.update_status(
        case_id="CASE-MR-001",
        new_status="Under Review",
        notes="Reviewing evidence with Bank B officer.",
        updated_by="Officer_01",
    )
    assert up_stat["status"] == "Under Review"
    assert len(up_stat["case_notes"]) == 1

    # 4. Record Feedback
    up_feed = manager.record_feedback(
        case_id="CASE-MR-001",
        decision="CONFIRMED_FRAUD",
        reason="Mule ring confirmed across Bank A, B, and C. SAR filed.",
        reviewed_by="Supervisor_01",
    )
    assert up_feed["status"] == "Resolved"
    assert up_feed["feedback"]["decision"] == "CONFIRMED_FRAUD"

    # 5. Generate PDF Report
    pdf_bytes = report_gen.generate_case_pdf(up_feed)
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 1000
    assert pdf_bytes.startswith(b"%PDF")  # Valid PDF header magic bytes!


def test_platform_assistant_and_advanced_analytics_endpoints():
    """Verifies FastAPI endpoints for AI Investigation Assistant and Advanced Analytics."""
    from starlette.testclient import TestClient
    from src.integration.api import app

    client = TestClient(app)

    # 1. Test AI Assistant Query
    resp_ai = client.post(
        "/api/v1/platform/investigation/assistant/query",
        json={"case_id": "CASE_001", "query": "Generate official SAR report narrative draft"},
    )
    assert resp_ai.status_code == 200
    ai_data = resp_ai.json()
    assert "reply" in ai_data
    assert "(SAR) Narrative" in ai_data["reply"]
    assert len(ai_data["suggested_actions"]) > 0

    # 2. Test Advanced Analytics Endpoint
    resp_ana = client.get("/api/v1/platform/analytics/advanced")
    assert resp_ana.status_code == 200
    ana_data = resp_ana.json()
    assert "bank_metrics" in ana_data
    assert "topology_distribution" in ana_data
    assert "velocity_histogram" in ana_data
    assert "cross_bank_flows" in ana_data
    assert ana_data["graph_kpis"]["rings_detected"] >= 28
