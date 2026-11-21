"""
RINGTRACE AI - Graph & Temporal Feature Extraction Engine.
Extracts account-level network topology and time-series behavioral features
including fan-in, fan-out, pass-through ratio, transfer velocity, and turnaround time.
"""

from typing import Dict, List, Any
import numpy as np
import pandas as pd
import networkx as nx

import config


class GraphFeatureEngine:
    """Computes graph topology and temporal behavioral features from transaction graphs."""

    def __init__(self):
        pass

    def extract_features(
        self,
        G: nx.DiGraph,
        transactions_df: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Calculates all node-level network and temporal features for each account in G.
        Returns a DataFrame indexed by account_id with feature columns and target label.
        """
        # Precompute graph metrics
        try:
            pagerank = nx.pagerank(G, weight="weight")
        except Exception:
            pagerank = {node: 1.0 / len(G) for node in G.nodes()}

        # Undirected view for clustering coefficient
        G_undirected = G.to_undirected()
        clustering = nx.clustering(G_undirected)

        # Pre-group transactions by sender and receiver for fast temporal calculations
        tx_df = transactions_df.copy()
        tx_df["timestamp"] = pd.to_datetime(tx_df["timestamp"])
        tx_by_sender = {k: v.sort_values("timestamp") for k, v in tx_df.groupby("sender_account")}
        tx_by_receiver = {k: v.sort_values("timestamp") for k, v in tx_df.groupby("receiver_account")}

        features_list = []

        for node, data in G.nodes(data=True):
            # Inbound edges and out-bound edges
            in_edges = list(G.in_edges(node, data=True))
            out_edges = list(G.out_edges(node, data=True))

            # Degree & Fan counts
            fan_in_distinct = len(in_edges)
            fan_out_distinct = len(out_edges)
            in_degree = sum(e[2].get("tx_count", 1) for e in in_edges)
            out_degree = sum(e[2].get("tx_count", 1) for e in out_edges)

            # Amounts
            total_in = sum(e[2].get("weight", 0.0) for e in in_edges)
            total_out = sum(e[2].get("weight", 0.0) for e in out_edges)
            avg_in = (total_in / in_degree) if in_degree > 0 else 0.0
            avg_out = (total_out / out_degree) if out_degree > 0 else 0.0

            # Pass-through & Flow ratios
            pass_through = total_out / (total_in + 1e-5)
            denom_flow = total_out + total_in + 1e-5
            net_flow = (total_out - total_in) / denom_flow

            init_bal = data.get("initial_balance", 0.0)
            turnover = (total_in + total_out) / (init_bal + total_in + 1e-5)

            # Temporal analysis: turnaround time between incoming and outgoing
            # Mule behavior: receives money and forwards it within minutes
            node_in_tx = tx_by_receiver.get(node, pd.DataFrame())
            node_out_tx = tx_by_sender.get(node, pd.DataFrame())

            turnaround_times_sec = []
            if not node_in_tx.empty and not node_out_tx.empty:
                out_times = node_out_tx["timestamp"].values
                for in_time in node_in_tx["timestamp"]:
                    # Find subsequent outgoing transactions
                    subsequent = out_times[out_times > in_time]
                    if len(subsequent) > 0:
                        delta_sec = (subsequent[0] - in_time) / np.timedelta64(1, "s")
                        turnaround_times_sec.append(delta_sec)

            if turnaround_times_sec:
                min_turnaround = float(np.min(turnaround_times_sec))
                avg_turnaround = float(np.mean(turnaround_times_sec))
            else:
                # Default large time (e.g. 7 days in seconds) if no pass-through sequence
                min_turnaround = 86400.0 * 7
                avg_turnaround = 86400.0 * 7

            # Transaction velocity (sliding window over all node transactions)
            node_all_tx_times = []
            if not node_in_tx.empty:
                node_all_tx_times.extend(node_in_tx["timestamp"].tolist())
            if not node_out_tx.empty:
                node_all_tx_times.extend(node_out_tx["timestamp"].tolist())
            node_all_tx_times.sort()

            vel_1h_max = 0
            vel_24h_max = 0
            if node_all_tx_times:
                times_series = pd.Series(1, index=pd.DatetimeIndex(node_all_tx_times))
                # Rolling count in 1H and 24H
                rolling_1h = times_series.rolling("1h").count()
                rolling_24h = times_series.rolling("24h").count()
                vel_1h_max = int(rolling_1h.max())
                vel_24h_max = int(rolling_24h.max())

            # Cross-bank ratio
            cross_bank_tx = 0
            total_node_tx = in_degree + out_degree
            for _, _, e_data in in_edges:
                cross_bank_tx += sum(t.get("is_cross_bank", 0) for t in e_data.get("transactions", []))
            for _, _, e_data in out_edges:
                cross_bank_tx += sum(t.get("is_cross_bank", 0) for t in e_data.get("transactions", []))
            cross_bank_ratio = (cross_bank_tx / total_node_tx) if total_node_tx > 0 else 0.0

            features_list.append({
                "account_id": node,
                "bank_id": data.get("bank_id", "UNKNOWN"),
                "canonical_entity_id": data.get("canonical_entity_id", "UNKNOWN"),
                "profile_type": data.get("profile_type", "UNKNOWN"),
                "account_age_days": data.get("account_age_days", 30),
                "in_degree": in_degree,
                "out_degree": out_degree,
                "fan_in_distinct": fan_in_distinct,
                "fan_out_distinct": fan_out_distinct,
                "total_amount_in": round(total_in, 2),
                "total_amount_out": round(total_out, 2),
                "avg_amount_in": round(avg_in, 2),
                "avg_amount_out": round(avg_out, 2),
                "pass_through_ratio": round(pass_through, 4),
                "net_flow_ratio": round(net_flow, 4),
                "turnover_rate": round(turnover, 4),
                "avg_turnaround_time_sec": round(avg_turnaround, 2),
                "min_turnaround_time_sec": round(min_turnaround, 2),
                "velocity_1h_max": vel_1h_max,
                "velocity_24h_max": vel_24h_max,
                "cross_bank_tx_ratio": round(cross_bank_ratio, 4),
                "pagerank": round(pagerank.get(node, 0.0), 6),
                "clustering_coeff": round(clustering.get(node, 0.0), 6),
                "ring_id": data.get("ring_id", "NONE"),
                "ring_role": data.get("ring_role", "LEGITIMATE"),
                "is_mule": int(data.get("is_mule", 0)),
            })

        features_df = pd.DataFrame(features_list)
        return features_df
