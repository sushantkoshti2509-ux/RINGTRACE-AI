"""
Unit tests for Directed Graph Builder, Feature Engine, and Ring Detection.
"""

import pytest
import pandas as pd
from src.simulator.generator import UPISimulator
from src.graph.builder import TransactionGraphBuilder
from src.graph.features import GraphFeatureEngine
from src.graph.ring_detection import RingDetectionEngine


@pytest.fixture
def sample_data():
    sim = UPISimulator(seed=99)
    accs, txs, rings, _ = sim.generate_all(num_accounts=100, num_rings=4)
    return accs, txs, rings


def test_graph_builder(sample_data):
    accs, txs, _ = sample_data
    builder = TransactionGraphBuilder()
    G = builder.build_graph(accs, txs)

    assert G.number_of_nodes() >= len(accs)
    assert G.number_of_edges() > 0

    # Test bank filter isolation
    G_bank_a = builder.build_graph(accs, txs, bank_filter="BANK_A")
    for u, v, d in G_bank_a.edges(data=True):
        # Must involve BANK_A
        tx_list = d.get("transactions", [])
        assert any(
            t["is_cross_bank"] or G_bank_a.nodes[u].get("bank_id") == "BANK_A" or G_bank_a.nodes[v].get("bank_id") == "BANK_A"
            for t in tx_list
        )


def test_feature_extraction(sample_data):
    accs, txs, _ = sample_data
    builder = TransactionGraphBuilder()
    G = builder.build_graph(accs, txs)

    engine = GraphFeatureEngine()
    features_df = engine.extract_features(G, txs)

    assert len(features_df) == G.number_of_nodes()
    assert "pass_through_ratio" in features_df.columns
    assert "min_turnaround_time_sec" in features_df.columns
    assert "fan_in_distinct" in features_df.columns
    assert "fan_out_distinct" in features_df.columns
    assert (features_df["pass_through_ratio"] >= 0).all()


def test_ring_detection(sample_data):
    accs, txs, rings = sample_data
    builder = TransactionGraphBuilder()
    G = builder.build_graph(accs, txs)

    engine = GraphFeatureEngine()
    features_df = engine.extract_features(G, txs)

    # Synthetic risk score mapping
    risk_df = pd.DataFrame({
        "account_id": features_df["account_id"],
        "risk_score": features_df["is_mule"].apply(lambda x: 0.90 if x == 1 else 0.10),
    })

    ring_engine = RingDetectionEngine(risk_threshold=0.50)
    candidate_rings = ring_engine.discover_candidate_rings(G, risk_df)

    assert len(candidate_rings) > 0
    first_ring = candidate_rings[0]
    assert "topology_type" in first_ring
    assert "ring_risk_score" in first_ring
    assert first_ring["size"] >= 2

    # Ring evaluation
    eval_res = ring_engine.evaluate_detected_rings(candidate_rings, rings)
    assert eval_res["total_ground_truth_rings"] == len(rings)
    assert eval_res["ring_recall"] > 0
