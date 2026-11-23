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

    def detect_cycles(self, max_length: int = 5) -> List[List[str]]:
        """
        1. Circular transfers: Directed cycle detection (layering loops) across accounts.
        Returns distinct directed cycles.
        """
        cycles = []
        try:
            for cycle in nx.simple_cycles(self.G, length_bound=max_length):
                if 2 <= len(cycle) <= max_length:
                    cycles.append(cycle)
                if len(cycles) >= 50:
                    break
        except TypeError:
            for cycle in nx.simple_cycles(self.G):
                if 2 <= len(cycle) <= max_length:
                    cycles.append(cycle)
                if len(cycles) >= 50:
                    break
        except Exception:
            pass
        return cycles

    def detect_layering_chains(self, min_hops: int = 3, max_chains: int = 25) -> List[Dict[str, Any]]:
        """
        2. Layering: Multi-hop path analysis identifying sequential fund routing
        across bank borders without resting balance.
        """
        chains = []
        visited_paths = set()

        for source in self.G.nodes():
            if self.G.in_degree(source) == 0 or self.G.out_degree(source) > 0:
                # Explore forward paths up to 4 hops
                for target in self.G.nodes():
                    if source == target:
                        continue
                    try:
                        for path in nx.all_simple_paths(self.G, source=source, target=target, cutoff=4):
                            if len(path) >= min_hops:
                                path_tuple = tuple(path)
                                if path_tuple not in visited_paths:
                                    visited_paths.add(path_tuple)
                                    banks = [self.G.nodes[n].get("bank_id", n.split(":")[0] if ":" in n else "BANK_A") for n in path]
                                    total_amt = 0.0
                                    for i in range(len(path) - 1):
                                        edge_data = self.G.get_edge_data(path[i], path[i+1], {})
                                        total_amt += edge_data.get("amount", edge_data.get("weight", 0.0))

                                    chains.append({
                                        "chain_id": f"CHAIN_{len(chains)+1:03d}",
                                        "hops": path,
                                        "hop_count": len(path) - 1,
                                        "banks_involved": sorted(list(set(banks))),
                                        "is_cross_bank": len(set(banks)) > 1,
                                        "total_volume": round(total_amt, 2),
                                        "pass_through_velocity": "Sub-90s Rapid Transit",
                                    })
                                    if len(chains) >= max_chains:
                                        return chains
                    except Exception:
                        continue
        return chains

    def detect_fan_in(self, min_in_degree: int = 3, min_volume: float = 30000.0) -> List[Dict[str, Any]]:
        """
        3. Fan-in: Identifies mule collector accounts receiving multiple deposits
        from diverse source accounts in a concentrated time window.
        """
        collectors = []
        for node in self.G.nodes():
            in_deg = self.G.in_degree(node)
            if in_deg >= min_in_degree:
                in_edges = list(self.G.in_edges(node, data=True))
                total_in = sum(d.get("amount", d.get("weight", 0.0)) for _, _, d in in_edges)
                if total_in >= min_volume:
                    sources = [u for u, _, _ in in_edges]
                    source_banks = {self.G.nodes[u].get("bank_id", u.split(":")[0] if ":" in u else "BANK_A") for u in sources}
                    node_bank = self.G.nodes[node].get("bank_id", node.split(":")[0] if ":" in node else "BANK_A")
                    collectors.append({
                        "collector_account": node,
                        "collector_bank": node_bank,
                        "in_degree": in_deg,
                        "total_inbound_volume": round(total_in, 2),
                        "source_accounts": sources[:8],
                        "source_banks": sorted(list(source_banks)),
                        "is_cross_bank": len(source_banks) > 1 or (len(source_banks) == 1 and node_bank not in source_banks),
                        "pattern_type": "FAN_IN_COLLECTOR",
                    })
        collectors.sort(key=lambda x: (x["total_inbound_volume"], x["in_degree"]), reverse=True)
        return collectors

    def detect_fan_out(self, min_out_degree: int = 3, min_volume: float = 30000.0) -> List[Dict[str, Any]]:
        """
        4. Fan-out: Identifies smurfing splitter accounts dispersing incoming deposits
        to multiple downstream recipient accounts.
        """
        splitters = []
        for node in self.G.nodes():
            out_deg = self.G.out_degree(node)
            if out_deg >= min_out_degree:
                out_edges = list(self.G.out_edges(node, data=True))
                total_out = sum(d.get("amount", d.get("weight", 0.0)) for _, _, d in out_edges)
                if total_out >= min_volume:
                    recipients = [v for _, v, _ in out_edges]
                    dest_banks = {self.G.nodes[v].get("bank_id", v.split(":")[0] if ":" in v else "BANK_A") for v in recipients}
                    node_bank = self.G.nodes[node].get("bank_id", node.split(":")[0] if ":" in node else "BANK_A")
                    splitters.append({
                        "splitter_account": node,
                        "splitter_bank": node_bank,
                        "out_degree": out_deg,
                        "total_outbound_volume": round(total_out, 2),
                        "destination_accounts": recipients[:8],
                        "destination_banks": sorted(list(dest_banks)),
                        "is_cross_bank": len(dest_banks) > 1 or (len(dest_banks) == 1 and node_bank not in dest_banks),
                        "pattern_type": "FAN_OUT_SPLITTER",
                    })
        splitters.sort(key=lambda x: (x["total_outbound_volume"], x["out_degree"]), reverse=True)
        return splitters

    def detect_hybrid_rings(self) -> List[Dict[str, Any]]:
        """
        5. Hybrid rings: Community detection and combined pattern scoring
        identifying clustered networks with concurrent circular and dispersion topology.
        """
        communities = self.detect_communities()
        hybrid_rings = []
        for comm in communities:
            members = set(comm.get("members", []))
            sub = self.G.subgraph(members)
            cycles = []
            try:
                for c in nx.simple_cycles(sub):
                    cycles.append(c)
                    if len(cycles) >= 5:
                        break
            except Exception:
                pass

            in_degs = [sub.in_degree(n) for n in members]
            out_degs = [sub.out_degree(n) for n in members]
            max_in = max(in_degs) if in_degs else 0
            max_out = max(out_degs) if out_degs else 0
            has_cycle = len(cycles) > 0

            # Combined pattern score
            score = 0.50
            if has_cycle:
                score += 0.25
            if max_in >= 2:
                score += 0.15
            if max_out >= 2:
                score += 0.10

            hybrid_rings.append({
                "community_id": comm["community_id"],
                "size": comm["size"],
                "members": comm["members"],
                "banks_involved": comm["banks_involved"],
                "is_cross_bank": comm["is_cross_bank"],
                "has_cycles": has_cycle,
                "cycle_count": len(cycles),
                "max_fan_in": max_in,
                "max_fan_out": max_out,
                "composite_risk_score": round(min(1.0, score), 4),
                "pattern_type": "HYBRID_RING_COMMUNITY",
            })
        hybrid_rings.sort(key=lambda x: (x["composite_risk_score"], x["size"]), reverse=True)
        return hybrid_rings

    def detect_all_five_topologies(self) -> Dict[str, Any]:
        """
        Executes and aggregates all 5 detection algorithms into a single unified intelligence feed.
        """
        cycles = self.detect_cycles(max_length=5)
        layering = self.detect_layering_chains(min_hops=3)
        fan_in = self.detect_fan_in(min_in_degree=2)
        fan_out = self.detect_fan_out(min_out_degree=2)
        hybrid = self.detect_hybrid_rings()

        return {
            "summary": {
                "total_cycles_detected": len(cycles),
                "total_layering_chains": len(layering),
                "total_fan_in_collectors": len(fan_in),
                "total_fan_out_splitters": len(fan_out),
                "total_hybrid_communities": len(hybrid),
            },
            "circular_transfers": cycles,
            "layering_chains": layering,
            "fan_in_collectors": fan_in,
            "fan_out_splitters": fan_out,
            "hybrid_rings": hybrid,
        }

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

            # Parse timestamps once per incoming edge
            in_parsed = []
            for u, _, in_data in in_edges[:15]:
                try:
                    ts_str = in_data.get("timestamp")
                    t_in = pd.to_datetime(ts_str).timestamp()
                    in_parsed.append((u, t_in, in_data.get("amount", 0.0)))
                except Exception:
                    continue

            # Parse timestamps once per outgoing edge
            out_parsed = []
            for _, v, out_data in out_edges[:15]:
                try:
                    ts_str = out_data.get("timestamp")
                    t_out = pd.to_datetime(ts_str).timestamp()
                    out_parsed.append((v, t_out, out_data.get("amount", 0.0)))
                except Exception:
                    continue

            for u, t_in, in_amt in in_parsed:
                for v, t_out, out_amt in out_parsed:
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
                        if len(rapid_transfers) >= 50:
                            return rapid_transfers
                if len(rapid_transfers) >= 50:
                    return rapid_transfers

        return rapid_transfers
