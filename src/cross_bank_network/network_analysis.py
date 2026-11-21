"""
Feature 1: Cross-Bank Network Analysis.
Computes in-degree, out-degree, cycle detection, betweenness centrality,
community detection, and temporal turnaround velocity.
"""

from typing import Dict, Any, List, Set, Tuple
import networkx as nx
import pandas as pd
from datetime import datetime


class CrossBankNetworkAnalyzer:
    """Extracts graph topological and behavioral indicators from multi-bank networks."""

    def __init__(self, graph: nx.DiGraph):
        self.G = graph

    def get_degree_metrics(self) -> Dict[str, Dict[str, int]]:
        """Calculates in-degree and out-degree for every account in the network."""
        metrics = {}
        for node in self.G.nodes():
            metrics[node] = {
                "in_degree": int(self.G.in_degree(node)),
                "out_degree": int(self.G.out_degree(node)),
                "total_degree": int(self.G.degree(node)),
            }
        return metrics

    def detect_cycles(self, max_length: int = 6) -> List[List[str]]:
        """
        Detects circular transaction patterns (layering loops) across accounts.
        Returns distinct directed cycles.
        """
        cycles = []
        try:
            # nx.simple_cycles generates all elementary directed circuits
            for cycle in nx.simple_cycles(self.G):
                if 2 <= len(cycle) <= max_length:
                    cycles.append(cycle)
                if len(cycles) >= 50:
                    break
        except Exception:
            pass
        return cycles

    def compute_betweenness_centrality(self) -> Dict[str, float]:
        """Calculates betweenness centrality to identify intermediary money mule bridges."""
        if len(self.G) == 0:
            return {}
        raw = nx.betweenness_centrality(self.G, weight="amount")
        return {k: round(float(v), 5) for k, v in raw.items()}

    def detect_communities(self) -> List[Dict[str, Any]]:
        """
        Identifies suspicious clusters and interconnected groups of accounts
        across Bank A, Bank B, and Bank C.
        """
        if len(self.G) == 0:
            return []

        # Convert to undirected for community partitioning
        undirected_G = self.G.to_undirected()
        communities = []

        try:
            from networkx.algorithms.community import greedy_modularity_communities
            raw_comms = list(greedy_modularity_communities(undirected_G))
            for idx, comm in enumerate(raw_comms):
                if len(comm) >= 2:
                    banks_in_comm = {self.G.nodes[n].get("bank_id", "UNKNOWN") for n in comm if n in self.G.nodes}
                    communities.append({
                        "community_id": f"COMM_{idx+1:03d}",
                        "size": len(comm),
                        "members": sorted(list(comm)),
                        "banks_involved": sorted(list(banks_in_comm)),
                        "is_cross_bank": len(banks_in_comm) > 1,
                    })
        except Exception:
            # Fallback to connected components
            for idx, comp in enumerate(nx.connected_components(undirected_G)):
                if len(comp) >= 2:
                    banks_in_comp = {self.G.nodes[n].get("bank_id", "UNKNOWN") for n in comp if n in self.G.nodes}
                    communities.append({
                        "community_id": f"COMP_{idx+1:03d}",
                        "size": len(comp),
                        "members": sorted(list(comp)),
                        "banks_involved": sorted(list(banks_in_comp)),
                        "is_cross_bank": len(banks_in_comp) > 1,
                    })

        communities.sort(key=lambda x: (x["is_cross_bank"], x["size"]), reverse=True)
        return communities

    def analyze_temporal_turnaround(self, turnaround_threshold_sec: float = 600.0) -> List[Dict[str, Any]]:
        """
        Identifies rapid money movement where an account receives funds and forwards
        a substantial portion to another account within the threshold window.
        """
        rapid_transfers = []
        for node in self.G.nodes():
            in_edges = list(self.G.in_edges(node, data=True))
            out_edges = list(self.G.out_edges(node, data=True))

            if not in_edges or not out_edges:
                continue

            for u, _, in_data in in_edges:
                in_ts_str = in_data.get("timestamp")
                in_amt = in_data.get("amount", 0.0)

                for _, v, out_data in out_edges:
                    out_ts_str = out_data.get("timestamp")
                    out_amt = out_data.get("amount", 0.0)

                    try:
                        t_in = pd.to_datetime(in_ts_str).timestamp()
                        t_out = pd.to_datetime(out_ts_str).timestamp()
                        diff = t_out - t_in

                        if 0.0 <= diff <= turnaround_threshold_sec:
                            rapid_transfers.append({
                                "intermediary_account": node,
                                "source_account": u,
                                "destination_account": v,
                                "amount_in": in_amt,
                                "amount_out": out_amt,
                                "time_gap_seconds": round(diff, 1),
                                "pass_through_ratio": round(out_amt / in_amt, 3) if in_amt > 0 else 0.0,
                            })
                    except Exception:
                        continue
        return rapid_transfers
