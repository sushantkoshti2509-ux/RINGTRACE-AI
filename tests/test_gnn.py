"""
Unit and integration tests for Phase 7: Graph Neural Network (GNN) Integration.
Tests:
1. GNNFeatureEngineer (16-dim node features, 8-dim edge features, one-hot bank encodings)
2. GNNDatasetBuilder (PyG Data object, Group-Aware ring-level train/val/test splits)
3. EdgeAwareGNN & GATv2Net models (multi-task predictions: node, edge, network readout)
4. GNNInferenceService (Model loading, fallback handling, prediction interfaces)
5. GNNSubGraphExplainer (2-hop neighborhood, influential neighbors, critical edges)
6. FastAPI REST Endpoints (/api/v1/gnn/*)
"""

import pytest
import torch
import numpy as np
import pandas as pd
import networkx as nx
from fastapi.testclient import TestClient

from src.integration.api import app
from src.gnn.features import GNNFeatureEngineer
from src.gnn.dataset import GNNDatasetBuilder
from src.gnn.models import EdgeAwareGNN, GATv2Net
from src.gnn.inference import GNNInferenceService
from src.gnn.explainer import GNNSubGraphExplainer


@pytest.fixture
def sample_graph_data():
    """Builds a small 4-bank test graph with 6 accounts and 6 transactions."""
    G = nx.DiGraph()
    G.add_node("BANK_A:A101", bank_id="BANK_A", is_mule=1)
    G.add_node("BANK_B:B201", bank_id="BANK_B", is_mule=1)
    G.add_node("BANK_C:C301", bank_id="BANK_C", is_mule=1)
    G.add_node("BANK_D:D401", bank_id="BANK_D", is_mule=0)
    G.add_node("BANK_A:A102", bank_id="BANK_A", is_mule=0)
    G.add_node("BANK_B:B202", bank_id="BANK_B", is_mule=0)

    # Circular mule path across A -> B -> C -> A
    G.add_edge("BANK_A:A101", "BANK_B:B201", amount=50000.0, weight=50000.0, timestamp="2026-11-20 10:00:00", sender_bank="BANK_A", receiver_bank="BANK_B", transaction_type="IMPS", status="SUCCESS")
    G.add_edge("BANK_B:B201", "BANK_C:C301", amount=48000.0, weight=48000.0, timestamp="2026-11-20 10:05:00", sender_bank="BANK_B", receiver_bank="BANK_C", transaction_type="IMPS", status="SUCCESS")
    G.add_edge("BANK_C:C301", "BANK_A:A101", amount=46000.0, weight=46000.0, timestamp="2026-11-20 10:10:00", sender_bank="BANK_C", receiver_bank="BANK_A", transaction_type="IMPS", status="SUCCESS")

    # Legitimate cross-bank transfers
    G.add_edge("BANK_D:D401", "BANK_A:A102", amount=1200.0, weight=1200.0, timestamp="2026-11-20 14:00:00", sender_bank="BANK_D", receiver_bank="BANK_A", transaction_type="NEFT", status="SUCCESS")
    G.add_edge("BANK_A:A102", "BANK_B:B202", amount=850.0, weight=850.0, timestamp="2026-11-20 15:30:00", sender_bank="BANK_A", receiver_bank="BANK_B", transaction_type="UPI_P2P", status="SUCCESS")

    accounts_df = pd.DataFrame([
        {"account_id": "BANK_A:A101", "is_mule": 1, "ring_id": "RING_01", "account_age_days": 45, "initial_balance": 500.0},
        {"account_id": "BANK_B:B201", "is_mule": 1, "ring_id": "RING_01", "account_age_days": 30, "initial_balance": 1000.0},
        {"account_id": "BANK_C:C301", "is_mule": 1, "ring_id": "RING_01", "account_age_days": 15, "initial_balance": 250.0},
        {"account_id": "BANK_D:D401", "is_mule": 0, "ring_id": "NONE", "account_age_days": 800, "initial_balance": 75000.0},
        {"account_id": "BANK_A:A102", "is_mule": 0, "ring_id": "NONE", "account_age_days": 540, "initial_balance": 32000.0},
        {"account_id": "BANK_B:B202", "is_mule": 0, "ring_id": "NONE", "account_age_days": 365, "initial_balance": 18000.0},
    ])

    transactions_df = pd.DataFrame([
        {"transaction_id": "TX_01", "sender_account": "BANK_A:A101", "receiver_account": "BANK_B:B201", "amount": 50000.0, "timestamp": "2026-11-20 10:00:00", "sender_bank": "BANK_A", "receiver_bank": "BANK_B", "transaction_type": "IMPS", "status": "SUCCESS"},
        {"transaction_id": "TX_02", "sender_account": "BANK_B:B201", "receiver_account": "BANK_C:C301", "amount": 48000.0, "timestamp": "2026-11-20 10:05:00", "sender_bank": "BANK_B", "receiver_bank": "BANK_C", "transaction_type": "IMPS", "status": "SUCCESS"},
        {"transaction_id": "TX_03", "sender_account": "BANK_C:C301", "receiver_account": "BANK_A:A101", "amount": 46000.0, "timestamp": "2026-11-20 10:10:00", "sender_bank": "BANK_C", "receiver_bank": "BANK_A", "transaction_type": "IMPS", "status": "SUCCESS"},
        {"transaction_id": "TX_04", "sender_account": "BANK_D:D401", "receiver_account": "BANK_A:A102", "amount": 1200.0, "timestamp": "2026-11-20 14:00:00", "sender_bank": "BANK_D", "receiver_bank": "BANK_A", "transaction_type": "NEFT", "status": "SUCCESS"},
        {"transaction_id": "TX_05", "sender_account": "BANK_A:A102", "receiver_account": "BANK_B:B202", "amount": 850.0, "timestamp": "2026-11-20 15:30:00", "sender_bank": "BANK_A", "receiver_bank": "BANK_B", "transaction_type": "UPI_P2P", "status": "SUCCESS"},
    ])

    return G, accounts_df, transactions_df


# -----------------------------------------------------------------------------
# 1. Feature Engineering Tests
# -----------------------------------------------------------------------------
def test_gnn_feature_engineer(sample_graph_data):
    """Verifies 16-dim node feature matrix and 8-dim edge feature matrix."""
    G, accounts_df, _ = sample_graph_data
    engineer = GNNFeatureEngineer()

    # Node features
    node_features = engineer.build_node_features(G, accounts_df)
    assert node_features.shape == (6, 16)
    assert not np.isnan(node_features).any()
    assert not np.isinf(node_features).any()

    # Edge features
    edges = list(G.edges(data=True))
    edge_features = engineer.build_edge_features(edges)
    assert edge_features.shape == (5, 8)
    assert not np.isnan(edge_features).any()
    assert not np.isinf(edge_features).any()


# -----------------------------------------------------------------------------
# 2. PyG Dataset Builder Tests
# -----------------------------------------------------------------------------
def test_gnn_dataset_builder(sample_graph_data):
    """Verifies PyG Data construction and mask generation."""
    G, accounts_df, transactions_df = sample_graph_data
    builder = GNNDatasetBuilder()
    data = builder.build_pyg_data(G, accounts_df, transactions_df)

    assert data.x.shape == (6, 16)
    assert data.edge_index.shape[0] == 2
    assert data.edge_index.shape[1] == 5
    assert data.edge_attr.shape == (5, 8)
    assert data.y.shape == (6,)
    assert data.train_mask.shape == (6,)
    assert data.val_mask.shape == (6,)
    assert data.test_mask.shape == (6,)

    # Zero leakage check: Disjoint masks
    overlap = (data.train_mask & data.val_mask) | (data.train_mask & data.test_mask) | (data.val_mask & data.test_mask)
    assert overlap.sum().item() == 0


# -----------------------------------------------------------------------------
# 3. Model Architecture Forward Pass Tests
# -----------------------------------------------------------------------------
def test_edge_aware_gnn_forward():
    """Tests EdgeAwareGNN multi-task output heads."""
    num_nodes = 8
    num_edges = 12
    x = torch.randn((num_nodes, 16))
    edge_index = torch.randint(0, num_nodes, (2, num_edges))
    edge_attr = torch.randn((num_edges, 8))

    model = EdgeAwareGNN(node_in_dim=16, edge_in_dim=8, hidden_dim=32)
    model.eval()

    with torch.no_grad():
        out = model(x, edge_index, edge_attr)

    assert "node_embeddings" in out
    assert "node_logits" in out
    assert "node_probs" in out
    assert "edge_probs" in out
    assert "network_score" in out

    assert out["node_embeddings"].shape == (num_nodes, 32)
    assert out["node_logits"].shape == (num_nodes, 2)
    assert out["node_probs"].shape == (num_nodes,)
    assert (out["node_probs"] >= 0.0).all() and (out["node_probs"] <= 1.0).all()
    assert out["edge_probs"].shape == (num_edges,)
    assert (out["edge_probs"] >= 0.0).all() and (out["edge_probs"] <= 1.0).all()
    assert out["network_score"].shape == (1,)


def test_gatv2_net_forward():
    """Tests GATv2Net multi-head attention forward pass."""
    num_nodes = 8
    num_edges = 12
    x = torch.randn((num_nodes, 16))
    edge_index = torch.randint(0, num_nodes, (2, num_edges))
    edge_attr = torch.randn((num_edges, 8))

    model = GATv2Net(node_in_dim=16, edge_in_dim=8, hidden_dim=16, heads=4)
    model.eval()

    with torch.no_grad():
        out = model(x, edge_index, edge_attr)

    assert out["node_embeddings"].shape == (num_nodes, 64)
    assert out["node_probs"].shape == (num_nodes,)
    assert (out["node_probs"] >= 0.0).all() and (out["node_probs"] <= 1.0).all()
    assert out["edge_probs"].shape == (num_edges,)


# -----------------------------------------------------------------------------
# 4. GNN Inference Service & Explainer Tests
# -----------------------------------------------------------------------------
def test_gnn_inference_service():
    """Verifies inference service predictions across accounts, transactions, and networks."""
    service = GNNInferenceService()
    meta = service.get_metadata()
    assert meta["status"] == "ACTIVE_SERVING"
    assert "supported_banks" in meta
    assert "BANK_D" in meta["supported_banks"]

    acc_preds = service.predict_accounts(limit=10)
    assert len(acc_preds) > 0
    first_acc = acc_preds[0]
    assert "account_id" in first_acc
    assert "masked_id" in first_acc
    assert "gnn_score" in first_acc
    assert "risk_tier" in first_acc
    assert 0.0 <= first_acc["gnn_score"] <= 1.0

    tx_preds = service.predict_transactions(limit=10)
    assert len(tx_preds) > 0
    first_tx = tx_preds[0]
    assert "transaction_id" in first_tx
    assert "gnn_fraud_prob" in first_tx
    assert "is_cross_bank" in first_tx

    net_preds = service.predict_networks()
    assert len(net_preds) > 0
    first_net = net_preds[0]
    assert "network_id" in first_net
    assert "gnn_threat_score" in first_net


def test_gnn_subgraph_explainer():
    """Verifies 2-hop neighborhood extraction and attribution features."""
    service = GNNInferenceService()
    explainer = GNNSubGraphExplainer(service)

    accs = service.predict_accounts(limit=5)
    target = accs[0]["account_id"]

    explanation = explainer.explain_account(target)
    assert explanation["account_id"] == target
    assert "gnn_prediction_score" in explanation
    assert "subgraph" in explanation
    assert "top_feature_attributions" in explanation
    assert "critical_edges" in explanation
    assert "investigator_summary" in explanation

    subgraph = explanation["subgraph"]
    assert "nodes" in subgraph
    assert "edges" in subgraph
    assert len(subgraph["nodes"]) > 0


# -----------------------------------------------------------------------------
# 5. FastAPI REST API Endpoint Tests
# -----------------------------------------------------------------------------
def test_gnn_api_endpoints():
    """Tests all GNN endpoints via FastAPI TestClient."""
    client = TestClient(app)

    # 1. Metadata
    res = client.get("/api/v1/gnn/metadata")
    assert res.status_code == 200
    meta = res.json()
    assert meta["status"] == "ACTIVE_SERVING"

    # 2. Metrics
    res = client.get("/api/v1/gnn/metrics")
    assert res.status_code == 200
    metrics = res.json()
    assert metrics["status"] == "SUCCESS"
    assert "baseline_edge_aware_gnn" in metrics

    # 3. Model Comparison
    res = client.get("/api/v1/gnn/comparison")
    assert res.status_code == 200
    comp = res.json()
    assert "paradigms" in comp
    assert len(comp["paradigms"]) == 3

    # 4. Account Predictions
    res = client.get("/api/v1/gnn/predictions/accounts?limit=10")
    assert res.status_code == 200
    acc_data = res.json()
    assert "predictions" in acc_data
    assert len(acc_data["predictions"]) == 10

    # 5. Transaction Predictions
    res = client.get("/api/v1/gnn/predictions/transactions?limit=10")
    assert res.status_code == 200
    tx_data = res.json()
    assert "predictions" in tx_data
    assert len(tx_data["predictions"]) == 10

    # 6. Network Predictions
    res = client.get("/api/v1/gnn/predictions/networks")
    assert res.status_code == 200
    net_data = res.json()
    assert "networks" in net_data

    # 7. Explain Endpoint
    top_acc = acc_data["predictions"][0]["account_id"]
    res = client.post("/api/v1/gnn/explain", json={"account_id": top_acc})
    assert res.status_code == 200
    exp_data = res.json()
    assert exp_data["account_id"] == top_acc
    assert "subgraph" in exp_data

    # 8. Single Account Predict
    res = client.post("/api/v1/gnn/predict/account", json={"account_id": top_acc})
    assert res.status_code == 200
    pred_data = res.json()
    assert pred_data["account_id"] == top_acc
    assert "gnn_score" in pred_data
