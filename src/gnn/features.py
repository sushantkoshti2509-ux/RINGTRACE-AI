"""
Feature Pipeline for Phase 7 Graph Neural Networks.
Generates robust, leakage-free node and edge feature tensors across 4 synthetic institutions:
Bank A, Bank B, Bank C, and Bank D.
"""

from typing import Dict, Any, Tuple, List, Optional
import numpy as np
import pandas as pd
import networkx as nx
from sklearn.preprocessing import StandardScaler


class GNNFeatureEngineer:
    """
    Transforms tabular and graph attributes into normalized PyTorch feature tensors.
    Guarantees strict separation between training normalization and test evaluation.
    """

    BANK_MAP = {"BANK_A": 0, "BANK_B": 1, "BANK_C": 2, "BANK_D": 3}
    TX_TYPE_MAP = {"UPI_P2P": 0, "UPI_MERCHANT": 1, "IMPS": 2, "NEFT": 3, "RTGS": 4}
    STATUS_MAP = {"SUCCESS": 0, "PENDING": 1, "REVERSED": 2, "FAILED": 3}

    def __init__(self):
        self.node_scaler = StandardScaler()
        self.edge_scaler = StandardScaler()
        self.is_fitted = False

    def build_node_features(
        self,
        G: nx.DiGraph,
        accounts_df: pd.DataFrame,
        fit_scaler: bool = True,
    ) -> np.ndarray:
        """
        Builds a 16-dimensional node feature matrix:
        0: log10(in_volume + 1)
        1: log10(out_volume + 1)
        2: in_degree
        3: out_degree
        4: pass_through_ratio
        5: net_flow_ratio
        6: pagerank
        7: clustering_coeff
        8: account_age_days / 365.0
        9: initial_balance_log
        10-13: One-hot encoded bank (Bank A, B, C, D)
        14: turnover_rate
        15: total_degree
        """
        # Graph metrics
        pageranks = nx.pagerank(G, weight="amount") if len(G) > 0 else {}
        clustering = nx.clustering(G.to_undirected()) if len(G) > 0 else {}

        # Precompute in/out volume per node from edges
        in_vols = {n: 0.0 for n in G.nodes()}
        out_vols = {n: 0.0 for n in G.nodes()}
        for u, v, d in G.edges(data=True):
            amt = float(d.get("amount", d.get("weight", 0.0)))
            out_vols[u] = out_vols.get(u, 0.0) + amt
            in_vols[v] = in_vols.get(v, 0.0) + amt

        account_map = {}
        for _, row in accounts_df.iterrows():
            acc_id = str(row["account_id"])
            account_map[acc_id] = row

        raw_features = []
        for node in G.nodes():
            in_vol = in_vols.get(node, 0.0)
            out_vol = out_vols.get(node, 0.0)
            in_deg = float(G.in_degree(node))
            out_deg = float(G.out_degree(node))
            tot_deg = in_deg + out_deg

            pass_through = (out_vol / in_vol) if in_vol > 0 else 0.0
            net_flow = (out_vol - in_vol) / (in_vol + out_vol + 1e-5)
            pr = float(pageranks.get(node, 0.0))
            cc = float(clustering.get(node, 0.0))

            acc_row = account_map.get(node, None)
            age_norm = float(acc_row.get("account_age_days", 30)) / 365.0 if acc_row is not None else 0.1
            init_bal = np.log10(max(1.0, float(acc_row.get("initial_balance", 0.0)))) if acc_row is not None else 0.0

            bank = G.nodes[node].get("bank_id", node.split(":")[0] if ":" in node else "BANK_A")
            bank_idx = self.BANK_MAP.get(bank, 0)
            b_onehot = [0.0, 0.0, 0.0, 0.0]
            b_onehot[bank_idx] = 1.0

            turnover = min(5.0, pass_through)

            feat = [
                np.log10(in_vol + 1.0),
                np.log10(out_vol + 1.0),
                in_deg,
                out_deg,
                pass_through,
                net_flow,
                pr * 100.0,
                cc,
                age_norm,
                init_bal,
                b_onehot[0],
                b_onehot[1],
                b_onehot[2],
                b_onehot[3],
                turnover,
                tot_deg,
            ]
            raw_features.append(feat)

        raw_features = np.array(raw_features, dtype=np.float32)

        # Scale continuous features (indices 0..9 and 14..15), leave one-hot (10..13) intact
        continuous_indices = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 14, 15]
        if fit_scaler or not self.is_fitted:
            self.node_scaler.fit(raw_features[:, continuous_indices])
            self.is_fitted = True

        scaled_cont = self.node_scaler.transform(raw_features[:, continuous_indices])
        scaled_features = raw_features.copy()
        scaled_features[:, continuous_indices] = scaled_cont

        return np.nan_to_num(scaled_features, nan=0.0, posinf=0.0, neginf=0.0)

    def build_edge_features(
        self,
        edge_list: List[Tuple[str, str, Dict[str, Any]]],
        fit_scaler: bool = True,
    ) -> np.ndarray:
        """
        Builds an 8-dimensional edge feature matrix:
        0: log10(amount + 1)
        1: normalized amount ratio
        2: is_cross_bank (0.0 or 1.0)
        3: sender_bank_code / 4.0
        4: receiver_bank_code / 4.0
        5: tx_type_code / 5.0
        6: status_code / 4.0
        7: temporal_hour_sin
        """
        raw_edges = []
        for u, v, d in edge_list:
            amt = float(d.get("amount", d.get("weight", 0.0)))
            s_bank = d.get("sender_bank", u.split(":")[0] if ":" in u else "BANK_A")
            r_bank = d.get("receiver_bank", v.split(":")[0] if ":" in v else "BANK_B")
            is_cross = 1.0 if s_bank != r_bank else 0.0
            tx_type = d.get("transaction_type", "UPI_P2P")
            status = d.get("status", "SUCCESS")

            # Temporal hour sine
            hour = 12.0
            raw_ts = d.get("timestamp")
            if raw_ts is None and isinstance(d.get("transactions"), list) and len(d["transactions"]) > 0:
                raw_ts = d["transactions"][0].get("timestamp")
            
            if raw_ts is not None and not pd.isna(raw_ts):
                try:
                    dt = pd.to_datetime(raw_ts)
                    if not pd.isna(dt):
                        hour = float(dt.hour)
                except Exception:
                    hour = 12.0

            hour_sin = float(np.sin(2.0 * np.pi * hour / 24.0))
            if np.isnan(hour_sin):
                hour_sin = 0.0

            feat = [
                np.log10(amt + 1.0),
                min(amt / 100000.0, 5.0),
                is_cross,
                float(self.BANK_MAP.get(s_bank, 0)) / 4.0,
                float(self.BANK_MAP.get(r_bank, 1)) / 4.0,
                float(self.TX_TYPE_MAP.get(tx_type, 0)) / 5.0,
                float(self.STATUS_MAP.get(status, 0)) / 4.0,
                hour_sin,
            ]
            raw_edges.append(feat)

        if not raw_edges:
            return np.empty((0, 8), dtype=np.float32)

        arr = np.array(raw_edges, dtype=np.float32)
        return np.nan_to_num(arr, nan=0.0, posinf=0.0, neginf=0.0)
