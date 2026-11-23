"""
PyTorch Geometric Graph Neural Network Architectures for Phase 7 Fraud Intelligence.
Includes:
1. EdgeAwareGNN (Baseline: GraphSAGE / GINE with edge feature modulation)
2. GATv2Net (Experimental Comparison: Dynamic Multi-Head Graph Attention)
Multi-task prediction heads: Account node classification, Transaction edge classification, and Ring graph readout.
"""

from typing import Dict, Any, Tuple, Optional
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.nn import GINEConv, GATv2Conv, global_mean_pool, global_max_pool


class EdgeAwareGNN(nn.Module):
    """
    Baseline Edge-Aware GNN (GINE architecture).
    Propagates messages where transaction edge features (amount, corridor, status)
    modulate node embedding transitions across Bank A, Bank B, Bank C, and Bank D.
    """

    def __init__(
        self,
        node_in_dim: int = 16,
        edge_in_dim: int = 8,
        hidden_dim: int = 64,
        num_classes: int = 2,
        dropout: float = 0.2,
    ):
        super().__init__()
        self.node_in_dim = node_in_dim
        self.edge_in_dim = edge_in_dim
        self.hidden_dim = hidden_dim
        self.dropout = dropout

        # Linear projection for initial node and edge features
        self.node_proj = nn.Linear(node_in_dim, hidden_dim)
        self.edge_proj1 = nn.Linear(edge_in_dim, hidden_dim)
        self.edge_proj2 = nn.Linear(edge_in_dim, hidden_dim)

        # Layer 1 GINE Conv
        mlp1 = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim),
            nn.BatchNorm1d(hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
        )
        self.conv1 = GINEConv(mlp1, edge_dim=hidden_dim)
        self.bn1 = nn.BatchNorm1d(hidden_dim)

        # Layer 2 GINE Conv
        mlp2 = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim),
            nn.BatchNorm1d(hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
        )
        self.conv2 = GINEConv(mlp2, edge_dim=hidden_dim)
        self.bn2 = nn.BatchNorm1d(hidden_dim)

        # Head 1: Account Node Classifier (Mule vs Normal)
        self.node_head = nn.Sequential(
            nn.Linear(hidden_dim, 32),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(32, num_classes),
        )

        # Head 2: Transaction Edge Classifier (Laundering vs Normal Transaction)
        self.edge_head = nn.Sequential(
            nn.Linear(hidden_dim * 2 + edge_in_dim, 32),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(32, num_classes),
        )

        # Head 3: Subgraph / Network Threat Scorer
        self.network_head = nn.Sequential(
            nn.Linear(hidden_dim * 2, 32),
            nn.ReLU(),
            nn.Linear(32, 1),
            nn.Sigmoid(),
        )

    def forward(
        self,
        x: torch.Tensor,
        edge_index: torch.Tensor,
        edge_attr: torch.Tensor,
        batch: Optional[torch.Tensor] = None,
    ) -> Dict[str, torch.Tensor]:
        """
        Forward pass computing node embeddings, edge representations, and network readouts.
        """
        # Node projection
        h = self.node_proj(x)

        # Edge feature projections matching hidden_dim
        e1 = F.relu(self.edge_proj1(edge_attr))
        e2 = F.relu(self.edge_proj2(edge_attr))

        # Message passing layers with residual connections
        h1 = self.conv1(h, edge_index, edge_attr=e1)
        h1 = self.bn1(h1)
        h1 = F.relu(h1)
        h1 = F.dropout(h1, p=self.dropout, training=self.training)

        h2 = self.conv2(h1, edge_index, edge_attr=e2)
        h2 = self.bn2(h2)
        h2 = F.relu(h2)
        h_final = h1 + h2  # Residual jump connection

        # Node Predictions [N, num_classes]
        node_logits = self.node_head(h_final)

        # Edge Predictions [E, num_classes]
        if edge_index.size(1) > 0:
            src_nodes = h_final[edge_index[0]]
            dst_nodes = h_final[edge_index[1]]
            edge_concat = torch.cat([src_nodes, dst_nodes, edge_attr], dim=-1)
            edge_logits = self.edge_head(edge_concat)
        else:
            edge_logits = torch.empty((0, 2), device=x.device)

        # Subgraph / Network Score
        if batch is None:
            batch = torch.zeros(x.size(0), dtype=torch.long, device=x.device)
        g_mean = global_mean_pool(h_final, batch)
        g_max = global_max_pool(h_final, batch)
        network_score = self.network_head(torch.cat([g_mean, g_max], dim=-1))

        return {
            "node_embeddings": h_final,
            "node_logits": node_logits,
            "node_probs": F.softmax(node_logits, dim=-1)[:, 1],
            "edge_logits": edge_logits,
            "edge_probs": F.softmax(edge_logits, dim=-1)[:, 1] if edge_logits.size(0) > 0 else torch.empty(0),
            "network_score": network_score.squeeze(-1),
        }


class GATv2Net(nn.Module):
    """
    Experimental Comparison Model: GATv2 (Graph Attention Network v2).
    Computes dynamic multi-head attention coefficients over counterparty connections.
    """

    def __init__(
        self,
        node_in_dim: int = 16,
        edge_in_dim: int = 8,
        hidden_dim: int = 32,
        heads: int = 4,
        num_classes: int = 2,
        dropout: float = 0.2,
    ):
        super().__init__()
        self.node_in_dim = node_in_dim
        self.edge_in_dim = edge_in_dim
        self.hidden_dim = hidden_dim
        self.heads = heads
        self.dropout = dropout
        total_hidden = hidden_dim * heads

        # GATv2 Layer 1 with edge features
        self.conv1 = GATv2Conv(
            in_channels=node_in_dim,
            out_channels=hidden_dim,
            heads=heads,
            edge_dim=edge_in_dim,
            dropout=dropout,
        )

        # GATv2 Layer 2
        self.conv2 = GATv2Conv(
            in_channels=total_hidden,
            out_channels=hidden_dim,
            heads=heads,
            edge_dim=edge_in_dim,
            dropout=dropout,
        )

        self.bn1 = nn.BatchNorm1d(total_hidden)
        self.bn2 = nn.BatchNorm1d(total_hidden)

        # Prediction Heads
        self.node_head = nn.Sequential(
            nn.Linear(total_hidden, 32),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(32, num_classes),
        )

        self.edge_head = nn.Sequential(
            nn.Linear(total_hidden * 2 + edge_in_dim, 32),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(32, num_classes),
        )

        self.network_head = nn.Sequential(
            nn.Linear(total_hidden * 2, 32),
            nn.ReLU(),
            nn.Linear(32, 1),
            nn.Sigmoid(),
        )

    def forward(
        self,
        x: torch.Tensor,
        edge_index: torch.Tensor,
        edge_attr: torch.Tensor,
        batch: Optional[torch.Tensor] = None,
    ) -> Dict[str, torch.Tensor]:
        h1 = self.conv1(x, edge_index, edge_attr=edge_attr)
        h1 = self.bn1(h1)
        h1 = F.elu(h1)
        h1 = F.dropout(h1, p=self.dropout, training=self.training)

        h2 = self.conv2(h1, edge_index, edge_attr=edge_attr)
        h2 = self.bn2(h2)
        h2 = F.elu(h2)
        h_final = h1 + h2

        node_logits = self.node_head(h_final)

        if edge_index.size(1) > 0:
            src_nodes = h_final[edge_index[0]]
            dst_nodes = h_final[edge_index[1]]
            edge_concat = torch.cat([src_nodes, dst_nodes, edge_attr], dim=-1)
            edge_logits = self.edge_head(edge_concat)
        else:
            edge_logits = torch.empty((0, 2), device=x.device)

        if batch is None:
            batch = torch.zeros(x.size(0), dtype=torch.long, device=x.device)
        g_mean = global_mean_pool(h_final, batch)
        g_max = global_max_pool(h_final, batch)
        network_score = self.network_head(torch.cat([g_mean, g_max], dim=-1))

        return {
            "node_embeddings": h_final,
            "node_logits": node_logits,
            "node_probs": F.softmax(node_logits, dim=-1)[:, 1],
            "edge_logits": edge_logits,
            "edge_probs": F.softmax(edge_logits, dim=-1)[:, 1] if edge_logits.size(0) > 0 else torch.empty(0),
            "network_score": network_score.squeeze(-1),
        }
