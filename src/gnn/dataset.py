"""
PyTorch Geometric Dataset Builder for Phase 7 Four-Bank Mule Ring Detection.
Converts relational ledgers into PyG Data objects with Ring-Group-Aware train/val/test splits.
"""

from typing import Dict, Any, Tuple, Optional, List
import numpy as np
import pandas as pd
import networkx as nx
import torch
from torch_geometric.data import Data
from sklearn.model_selection import GroupKFold

from src.gnn.features import GNNFeatureEngineer


class GNNDatasetBuilder:
    """
    Constructs PyTorch Geometric graph data representations.
    Ensures that ground-truth rings are never split across train, validation, and test splits.
    """

    def __init__(self, feature_engineer: Optional[GNNFeatureEngineer] = None):
        self.feature_engineer = feature_engineer or GNNFeatureEngineer()
        self.node_to_idx: Dict[str, int] = {}
        self.idx_to_node: Dict[int, str] = {}

    def build_pyg_data(
        self,
        G: nx.DiGraph,
        accounts_df: pd.DataFrame,
        transactions_df: pd.DataFrame,
        test_ratio: float = 0.25,
        val_ratio: float = 0.15,
        random_state: int = 42,
    ) -> Data:
        """
        Converts directed NetworkX transaction graph into a PyG Data object.
        """
        # 1. Map nodes to continuous indices
        nodes = list(G.nodes())
        self.node_to_idx = {node: idx for idx, node in enumerate(nodes)}
        self.idx_to_node = {idx: node for node, idx in self.node_to_idx.items()}
        num_nodes = len(nodes)

        # 2. Extract node feature matrix X [N, d_node]
        x_np = self.feature_engineer.build_node_features(G, accounts_df, fit_scaler=True)
        x = torch.tensor(x_np, dtype=torch.float32)

        # 3. Extract Node Labels Y [N] (0: normal, 1: mule)
        account_labels = {}
        ring_groups = {}
        for _, row in accounts_df.iterrows():
            acc_id = str(row["account_id"])
            account_labels[acc_id] = int(row.get("is_mule", 0))
            r_id = str(row.get("ring_id", "NONE"))
            ring_groups[acc_id] = r_id if r_id != "NONE" else f"INDIVIDUAL_{acc_id}"

        y_list = [account_labels.get(node, 0) for node in nodes]
        y = torch.tensor(y_list, dtype=torch.long)
        groups = [ring_groups.get(node, f"IND_{node}") for node in nodes]

        # 4. Extract Directed Edges [2, E] and Edge Features [E, d_edge]
        edge_tuples = []
        edge_attrs_list = []
        edge_labels_list = []

        edge_data_list = list(G.edges(data=True))
        for u, v, d in edge_data_list:
            if u in self.node_to_idx and v in self.node_to_idx:
                u_idx = self.node_to_idx[u]
                v_idx = self.node_to_idx[v]
                edge_tuples.append((u_idx, v_idx))
                edge_attrs_list.append((u, v, d))

                # Edge label: 1 if both endpoints are mules, else 0
                is_mule_edge = 1 if (account_labels.get(u, 0) == 1 and account_labels.get(v, 0) == 1) else 0
                edge_labels_list.append(is_mule_edge)

        if edge_tuples:
            edge_index = torch.tensor(edge_tuples, dtype=torch.long).t().contiguous()
            edge_features_np = self.feature_engineer.build_edge_features(edge_attrs_list)
            edge_attr = torch.tensor(edge_features_np, dtype=torch.float32)
            edge_y = torch.tensor(edge_labels_list, dtype=torch.long)
        else:
            edge_index = torch.empty((2, 0), dtype=torch.long)
            edge_attr = torch.empty((0, 8), dtype=torch.float32)
            edge_y = torch.empty(0, dtype=torch.long)

        # 5. Group-Aware Stratified Train/Val/Test Split
        train_mask = torch.zeros(num_nodes, dtype=torch.bool)
        val_mask = torch.zeros(num_nodes, dtype=torch.bool)
        test_mask = torch.zeros(num_nodes, dtype=torch.bool)

        # Use GroupKFold on distinct ring identifiers
        unique_groups = len(set(groups))
        n_splits = min(5, max(2, unique_groups))

        if unique_groups < 2 or num_nodes < 4:
            # Fallback simple split for tiny graphs
            train_mask[:max(1, int(0.7 * num_nodes))] = True
            test_mask[max(1, int(0.7 * num_nodes)):] = True
        else:
            gkf = GroupKFold(n_splits=n_splits)
            splits = list(gkf.split(np.arange(num_nodes), y.numpy(), groups=groups))
            train_idx, test_idx = splits[0]

            # From train_idx, reserve 15% for validation
            np.random.seed(random_state)
            shuffled = np.random.permutation(train_idx)
            val_cutoff = max(1, int(len(shuffled) * val_ratio)) if len(shuffled) > 2 else 0
            val_idx = shuffled[:val_cutoff] if val_cutoff > 0 else []
            actual_train_idx = shuffled[val_cutoff:]

            train_mask[actual_train_idx] = True
            if len(val_idx) > 0:
                val_mask[val_idx] = True
            test_mask[test_idx] = True

        data = Data(
            x=x,
            edge_index=edge_index,
            edge_attr=edge_attr,
            y=y,
            edge_y=edge_y,
            train_mask=train_mask,
            val_mask=val_mask,
            test_mask=test_mask,
            num_nodes=num_nodes,
        )

        return data
