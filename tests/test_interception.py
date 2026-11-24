"""
Unit & Integration Tests for Feature: Mule Ring Interception & ROI Simulator (RBI Defense).
Verifies:
- Bottleneck node identification (Betweenness centrality & choke points)
- Interception loss prevention ROI calculation (INR saved)
- DPDP Act 2023 account masking and privacy protection
- SHA-256 cryptographic audit trail integrity
"""

import pytest
import hashlib
from src.interception.interception_engine import MuleInterceptionEngine


@pytest.fixture
def interception_engine():
    return MuleInterceptionEngine()


def test_interception_engine_initialization_and_rings(interception_engine):
    """Verifies that discovered candidate rings are loaded properly."""
    rings = interception_engine.get_candidate_rings()
    assert isinstance(rings, list)
    assert len(rings) > 0, "Candidate rings should be present for simulation"


def test_ring_subgraph_and_bottleneck_detection(interception_engine):
    """Verifies graph creation, betweenness centrality, and bottleneck ranking."""
    rings = interception_engine.get_candidate_rings()
    ring = rings[0]

    G, txs = interception_engine.build_ring_subgraph(ring)
    assert G.number_of_nodes() >= 2
    assert G.number_of_edges() >= 1

    bottlenecks = interception_engine.analyze_bottlenecks(G)
    assert len(bottlenecks) == G.number_of_nodes()
    assert "strategic_score" in bottlenecks[0]
    assert "betweenness_centrality" in bottlenecks[0]
    assert bottlenecks[0]["strategic_score"] >= bottlenecks[-1]["strategic_score"]


def test_interception_roi_calculation_and_loss_prevention(interception_engine):
    """Verifies financial loss prevented (ROI), severed nodes, and balance equality."""
    rings = interception_engine.get_candidate_rings()
    ring = rings[0]

    G, _ = interception_engine.build_ring_subgraph(ring)
    bottlenecks = interception_engine.analyze_bottlenecks(G)
    target_node = bottlenecks[0]["node_id"]

    sim_res = interception_engine.simulate_interception(
        ring=ring,
        target_node=target_node,
        strategy_key="COOLING_OFF_DELAY",
        delay_minutes=60,
        officer_id="RBI-NODAL-OFFICER-TEST",
    )

    assert sim_res["funds_intercepted_inr"] > 0
    assert sim_res["interception_rate_pct"] > 0
    assert sim_res["interception_rate_pct"] <= 100.0
    assert abs((sim_res["funds_intercepted_inr"] + sim_res["funds_leaked_inr"]) - sim_res["total_volume_at_risk_inr"]) < 1.0
    assert sim_res["ncrp_time_advantage_minutes"] > 0


def test_security_dpdp_privacy_masking_and_sha256_hash(interception_engine):
    """Verifies DPDP Act 2023 account masking and SHA-256 audit integrity."""
    # Test Masking
    masked = interception_engine.mask_account_id("BANK_A:BANK_ACC_00099")
    assert masked == "BANK_A:••••0099"
    assert "BANK_ACC" not in masked

    rings = interception_engine.get_candidate_rings()
    ring = rings[0]
    G, _ = interception_engine.build_ring_subgraph(ring)
    target = list(G.nodes())[0]

    sim_res = interception_engine.simulate_interception(
        ring=ring,
        target_node=target,
        strategy_key="STEP_UP_BIOMETRIC",
        delay_minutes=90,
        officer_id="NODAL-OFFICER-999",
    )

    audit = sim_res["audit_trail"]
    assert "sha256_integrity_hash" in audit
    assert len(audit["sha256_integrity_hash"]) == 64
    assert audit["officer_id"] == "NODAL-OFFICER-999"
    assert "Direction" in audit["regulatory_directive_citation"]


def test_all_regulatory_countermeasure_strategies(interception_engine):
    """Verifies execution across all three regulatory strategies."""
    rings = interception_engine.get_candidate_rings()
    ring = rings[0]
    G, _ = interception_engine.build_ring_subgraph(ring)
    target = list(G.nodes())[0]

    for strat_key in ["COOLING_OFF_DELAY", "STEP_UP_BIOMETRIC", "DUAL_BANK_HOLD"]:
        res = interception_engine.simulate_interception(
            ring=ring,
            target_node=target,
            strategy_key=strat_key,
            delay_minutes=45,
        )
        assert res["strategy_used"]["code"].startswith("STRAT_REG_")
        assert res["interception_rate_pct"] > 0


def test_unified_four_bank_ecosystem_topology(interception_engine):
    """Verifies that the unified 4-bank interconnected banking ecosystem combines all 4 banks in one directed graph."""
    from src.interception.api import get_unified_ecosystem

    # 1. Engine graph construction
    G, txs, metadata = interception_engine.build_unified_ecosystem_graph()
    assert G.number_of_nodes() > 20
    assert G.number_of_edges() > 20

    banks_in_graph = {G.nodes[n].get("bank_id") for n in G.nodes()}
    assert banks_in_graph == {"BANK_A", "BANK_B", "BANK_C", "BANK_D"}

    # Verify presence of cross-bank edges connecting banks
    cross_bank_edges = [(u, v) for u, v, d in G.edges(data=True) if d.get("is_cross_bank")]
    assert len(cross_bank_edges) > 10

    # Verify suspicious pattern presence
    patterns = {d.get("pattern_type") for _, _, d in G.edges(data=True)}
    assert any("CIRCULAR" in p for p in patterns)
    assert any("FAN" in p for p in patterns)
    assert "INTERBANK_CLEARING" in patterns

    # 2. REST API endpoint output
    resp = get_unified_ecosystem()
    assert resp["is_unified"] is True
    assert set(resp["banks_involved"]) == {"BANK_A", "BANK_B", "BANK_C", "BANK_D"}
    assert len(resp["nodes"]) > 20
    assert len(resp["edges"]) > 20
