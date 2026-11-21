"""
Account-Level Feature Engineering Engine for RINGTRACE AI.
Extracts network topological metrics, transactional frequencies, temporal velocities,
turnaround times, pass-through ratios, and behavioral anomaly indicators.
"""

from typing import Dict, List, Any, Optional
import numpy as np
import pandas as pd
import networkx as nx

import config


class AccountFeatureEngine:
    """Computes comprehensive account-level features from graphs and transaction ledgers."""

    def __init__(self):
        pass

    def extract_features(
        self,
        G: nx.DiGraph,
        transactions_df: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Calculates all node-level network, velocity, monetary, and temporal features
        for each account in G. Returns a DataFrame indexed by account_id.
        """
        # 1. Precompute graph-wide topology metrics
        try:
            pagerank = nx.pagerank(G, weight="weight")
        except Exception:
            pagerank = {node: 1.0 / len(G) for node in G.nodes()}

        G_undirected = G.to_undirected()
        clustering = nx.clustering(G_undirected)

        # 2. Pre-process transactions with datetime index
        tx_df = transactions_df.copy()
        tx_df["timestamp_dt"] = pd.to_datetime(tx_df["timestamp"])
        tx_df["is_cross_bank_val"] = (tx_df["sender_bank"] != tx_df["receiver_bank"]).astype(int)
        tx_df["is_off_hours_val"] = tx_df["timestamp_dt"].dt.hour.isin({23, 0, 1, 2, 3, 4, 5}).astype(int)
        tx_df["is_high_val"] = (tx_df["amount"] >= 50000.0).astype(int)

        tx_by_sender = {k: v.sort_values("timestamp_dt") for k, v in tx_df.groupby("sender_account")}
        tx_by_receiver = {k: v.sort_values("timestamp_dt") for k, v in tx_df.groupby("receiver_account")}

        features_list = []

        # 3. Iterate through all accounts / nodes in the interaction graph
        for node, data in G.nodes(data=True):
            in_edges = list(G.in_edges(node, data=True))
            out_edges = list(G.out_edges(node, data=True))

            # Degree & Fan counts
            fan_in_distinct = len(in_edges)
            fan_out_distinct = len(out_edges)
            in_degree = sum(e[2].get("tx_count", 1) for e in in_edges)
            out_degree = sum(e[2].get("tx_count", 1) for e in out_edges)
            tx_frequency_total = in_degree + out_degree

            # Amounts
            total_in = sum(e[2].get("weight", 0.0) for e in in_edges)
            total_out = sum(e[2].get("weight", 0.0) for e in out_edges)
            avg_in = (total_in / in_degree) if in_degree > 0 else 0.0
            avg_out = (total_out / out_degree) if out_degree > 0 else 0.0
            avg_total = ((total_in + total_out) / tx_frequency_total) if tx_frequency_total > 0 else 0.0

            # Pass-through & Flow ratios
            pass_through = (total_out / total_in) if total_in > 0 else 0.0
            denom_flow = total_out + total_in + 1e-5
            net_flow = (total_out - total_in) / denom_flow

            init_bal = data.get("initial_balance", 0.0)
            turnover = (total_in + total_out) / (init_bal + total_in + 1e-5)

            # Node transaction subsets
            node_in_tx = tx_by_receiver.get(node, pd.DataFrame())
            node_out_tx = tx_by_sender.get(node, pd.DataFrame())

            # Temporal analysis: turnaround time between incoming and outgoing funds
            turnaround_times_sec = []
            if not node_in_tx.empty and not node_out_tx.empty:
                out_times = node_out_tx["timestamp_dt"].values
                for in_time in node_in_tx["timestamp_dt"]:
                    subsequent = out_times[out_times > in_time]
                    if len(subsequent) > 0:
                        delta_sec = float((subsequent[0] - in_time) / np.timedelta64(1, "s"))
                        turnaround_times_sec.append(delta_sec)

            if turnaround_times_sec:
                min_turnaround = float(np.min(turnaround_times_sec))
                avg_turnaround = float(np.mean(turnaround_times_sec))
            else:
                min_turnaround = 86400.0 * 7
                avg_turnaround = 86400.0 * 7

            # Transaction velocity & minimum time gap
            node_all_times = []
            high_val_count = 0
            off_hours_count = 0

            if not node_in_tx.empty:
                node_all_times.extend(node_in_tx["timestamp_dt"].tolist())
                high_val_count += int(node_in_tx["is_high_val"].sum())
                off_hours_count += int(node_in_tx["is_off_hours_val"].sum())

            if not node_out_tx.empty:
                node_all_times.extend(node_out_tx["timestamp_dt"].tolist())
                high_val_count += int(node_out_tx["is_high_val"].sum())
                off_hours_count += int(node_out_tx["is_off_hours_val"].sum())

            node_all_times.sort()

            vel_1h_max = 0
            vel_24h_max = 0
            min_time_gap = 86400.0 * 7

            if node_all_times:
                times_series = pd.Series(1, index=pd.DatetimeIndex(node_all_times))
                vel_1h_max = int(times_series.rolling("1h").count().max())
                vel_24h_max = int(times_series.rolling("24h").count().max())

                if len(node_all_times) > 1:
                    deltas = np.diff(node_all_times).astype("timedelta64[s]").astype(float)
                    min_time_gap = float(np.min(deltas))

            # Normalized velocity score
            vel_score = float(np.clip((vel_1h_max / 5.0) * 0.6 + (vel_24h_max / 20.0) * 0.4, 0.0, 1.0))

            # Cross-bank ratio
            cross_bank_tx = 0
            for _, _, e_data in in_edges:
                cross_bank_tx += sum(t.get("is_cross_bank", 0) for t in e_data.get("transactions", []))
            for _, _, e_data in out_edges:
                cross_bank_tx += sum(t.get("is_cross_bank", 0) for t in e_data.get("transactions", []))
            cross_bank_ratio = (cross_bank_tx / tx_frequency_total) if tx_frequency_total > 0 else 0.0

            # High value & off hours ratios
            high_value_ratio = (high_val_count / tx_frequency_total) if tx_frequency_total > 0 else 0.0
            off_hours_ratio = (off_hours_count / tx_frequency_total) if tx_frequency_total > 0 else 0.0

            # Heuristic Behavioral Risk Score (0.0 to 1.0)
            # Higher when: rapid turnaround (< 10m), high pass-through (~1.0), high velocity, high cross-bank ratio
            pass_through_risk = 1.0 if (0.80 <= pass_through <= 1.20 and total_in > 5000) else 0.0
            turnaround_risk = np.clip((3600.0 - min_turnaround) / 3600.0, 0.0, 1.0)
            burst_risk = vel_score
            cross_risk = cross_bank_ratio

            behavioral_risk = float(np.round(
                0.35 * pass_through_risk
                + 0.25 * turnaround_risk
                + 0.20 * burst_risk
                + 0.20 * cross_risk,
                4,
            ))

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
                "tx_frequency_total": tx_frequency_total,
                "total_amount_in": round(total_in, 2),
                "total_amount_out": round(total_out, 2),
                "avg_amount_in": round(avg_in, 2),
                "avg_amount_out": round(avg_out, 2),
                "avg_amount_total": round(avg_total, 2),
                "high_value_tx_count": high_val_count,
                "high_value_ratio": round(high_value_ratio, 4),
                "off_hours_tx_ratio": round(off_hours_ratio, 4),
                "pass_through_ratio": round(pass_through, 4),
                "net_flow_ratio": round(net_flow, 4),
                "turnover_rate": round(turnover, 4),
                "avg_turnaround_time_sec": round(avg_turnaround, 2),
                "min_turnaround_time_sec": round(min_turnaround, 2),
                "min_time_gap_sec": round(min_time_gap, 2),
                "velocity_1h_max": vel_1h_max,
                "velocity_24h_max": vel_24h_max,
                "velocity_score": round(vel_score, 4),
                "cross_bank_tx_ratio": round(cross_bank_ratio, 4),
                "pagerank": round(pagerank.get(node, 0.0), 6),
                "clustering_coeff": round(clustering.get(node, 0.0), 6),
                "behavioral_risk_score": behavioral_risk,
                # Ground truth columns (strictly isolated from model feature space)
                "ring_id": data.get("ring_id", "NONE"),
                "ring_role": data.get("ring_role", "LEGITIMATE"),
                "is_mule": int(data.get("is_mule", 0)),
            })

        return pd.DataFrame(features_list)
