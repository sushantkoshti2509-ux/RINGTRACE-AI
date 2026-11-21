"""
RINGTRACE AI - Ring Identification and Network Intelligence Engine.
Discovers coordinated mule rings by combining account-level risk scores,
graph connectivity, multi-hop path tracing, and cross-bank flow patterns.
"""

from typing import List, Dict, Any, Set, Tuple
import networkx as nx
import pandas as pd
import numpy as np


class RingDetectionEngine:
    """Discovers and scores candidate suspicious account networks (rings)."""

    def __init__(self, risk_threshold: float = 0.40):
        self.risk_threshold = risk_threshold

    def discover_candidate_rings(
        self,
        G: nx.DiGraph,
        risk_scores_df: pd.DataFrame,
    ) -> List[Dict[str, Any]]:
        """
        Groups suspicious connected accounts into candidate rings and calculates
        network-level risk scores and structural evidence.
        """
        # Create map of account -> risk_score
        score_map = dict(zip(risk_scores_df["account_id"], risk_scores_df["risk_score"]))
        
        # Identify suspicious accounts (above candidate threshold)
        suspicious_nodes = {
            node for node, score in score_map.items()
            if score >= self.risk_threshold and node in G
        }

        if not suspicious_nodes:
            return []

        # Build induced subgraph of suspicious accounts
        subgraph = G.subgraph(suspicious_nodes)
        
        # Identify weakly connected components as candidate rings
        components = list(nx.weakly_connected_components(subgraph))
        
        # We focus on components with >= 2 connected members
        candidate_rings = []
        ring_idx = 1

        for comp in components:
            if len(comp) < 2:
                continue

            comp_nodes = list(comp)
            comp_sub = subgraph.subgraph(comp_nodes)

            # Collect internal transactions within component
            internal_txs = []
            banks_involved = set()
            total_volume = 0.0
            cross_bank_tx_count = 0

            for u, v, d in comp_sub.edges(data=True):
                u_bank = G.nodes[u].get("bank_id", "UNKNOWN")
                v_bank = G.nodes[v].get("bank_id", "UNKNOWN")
                banks_involved.add(u_bank)
                banks_involved.add(v_bank)
                total_volume += d.get("weight", 0.0)
                
                for tx in d.get("transactions", []):
                    internal_txs.append(tx)
                    if tx.get("is_cross_bank", 0):
                        cross_bank_tx_count += 1

            # Account risk metrics
            member_scores = [score_map.get(node, 0.0) for node in comp_nodes]
            avg_risk = float(np.mean(member_scores))
            max_risk = float(np.max(member_scores))

            # Topology & Hop Count
            # Calculate longest simple path or DAG depth if acyclic
            try:
                cycles = list(nx.simple_cycles(comp_sub))
                has_cycle = len(cycles) > 0
            except Exception:
                has_cycle = False

            # Longest shortest path in component
            try:
                comp_undirected = comp_sub.to_undirected()
                diameter = nx.diameter(comp_undirected)
            except Exception:
                diameter = len(comp_nodes) - 1

            # Determine dominant flow topology
            in_degrees = [comp_sub.in_degree(n) for n in comp_nodes]
            out_degrees = [comp_sub.out_degree(n) for n in comp_nodes]
            
            max_in = max(in_degrees) if in_degrees else 0
            max_out = max(out_degrees) if out_degrees else 0

            if has_cycle:
                topology_type = "CIRCULAR_LAYERING"
            elif max_out >= 3 and max_out > max_in:
                topology_type = "FAN_OUT_SPLITTER"
            elif max_in >= 3 and max_in > max_out:
                topology_type = "FAN_IN_COLLECTOR"
            elif len(banks_involved) > 1 and diameter >= 2:
                topology_type = "CROSS_BANK_CHAIN"
            else:
                topology_type = "RAPID_PASS_THROUGH"

            # Ring Risk Score formula combining:
            # 1. Member mean risk score (40%)
            # 2. Cross-bank footprint (20%)
            # 3. Path depth / diameter (20%)
            # 4. Ring size & volume factor (20%)
            cross_bank_factor = min(1.0, (len(banks_involved) - 1) * 0.5)
            hop_factor = min(1.0, diameter / 4.0)
            size_factor = min(1.0, len(comp_nodes) / 6.0)

            ring_risk = (
                0.40 * avg_risk +
                0.20 * cross_bank_factor +
                0.20 * hop_factor +
                0.20 * size_factor
            )
            ring_risk = min(1.0, max(0.0, ring_risk))

            candidate_rings.append({
                "candidate_ring_id": f"CANDIDATE_RING_{ring_idx:02d}",
                "topology_type": topology_type,
                "size": len(comp_nodes),
                "member_accounts": comp_nodes,
                "banks_involved": sorted(list(banks_involved)),
                "is_cross_bank": len(banks_involved) > 1,
                "cross_bank_tx_count": cross_bank_tx_count,
                "avg_account_risk": round(avg_risk, 4),
                "max_account_risk": round(max_risk, 4),
                "ring_risk_score": round(ring_risk, 4),
                "total_volume": round(total_volume, 2),
                "hop_count": diameter,
                "has_cycles": has_cycle,
                "internal_tx_count": len(internal_txs),
            })
            ring_idx += 1

        # Sort candidate rings by ring_risk_score descending
        candidate_rings.sort(key=lambda r: r["ring_risk_score"], reverse=True)
        return candidate_rings

    def evaluate_detected_rings(
        self,
        candidate_rings: List[Dict[str, Any]],
        ground_truth_rings_df: pd.DataFrame,
    ) -> Dict[str, Any]:
        """
        Evaluates detected candidate rings against ground truth mule rings.
        Computes ring-level precision, recall, and member overlap (Jaccard).
        """
        gt_rings = []
        for _, row in ground_truth_rings_df.iterrows():
            acc_set = set(str(row["accounts"]).split(";"))
            gt_rings.append({
                "ring_id": str(row["ring_id"]),
                "scenario_type": str(row["scenario_type"]),
                "accounts": acc_set,
            })

        matched_gt = set()
        matched_candidates = 0
        jaccard_scores = []

        for cand in candidate_rings:
            cand_set = set(cand["member_accounts"])
            best_jaccard = 0.0
            best_gt_id = None

            for gt in gt_rings:
                gt_set = gt["accounts"]
                intersection = len(cand_set.intersection(gt_set))
                union = len(cand_set.union(gt_set))
                jaccard = intersection / union if union > 0 else 0.0

                if jaccard > best_jaccard:
                    best_jaccard = jaccard
                    best_gt_id = gt["ring_id"]

            jaccard_scores.append(best_jaccard)
            # A candidate ring is considered a true positive if Jaccard >= 0.50 with a ground truth ring
            if best_jaccard >= 0.50 and best_gt_id:
                matched_candidates += 1
                matched_gt.add(best_gt_id)

        total_gt = len(gt_rings)
        total_candidates = len(candidate_rings)

        ring_precision = (matched_candidates / total_candidates) if total_candidates > 0 else 0.0
        ring_recall = (len(matched_gt) / total_gt) if total_gt > 0 else 0.0
        ring_f1 = (
            (2 * ring_precision * ring_recall) / (ring_precision + ring_recall)
            if (ring_precision + ring_recall) > 0 else 0.0
        )
        avg_jaccard = float(np.mean(jaccard_scores)) if jaccard_scores else 0.0

        return {
            "total_ground_truth_rings": total_gt,
            "total_candidate_rings_detected": total_candidates,
            "matched_ground_truth_rings": len(matched_gt),
            "ring_precision": round(ring_precision, 4),
            "ring_recall": round(ring_recall, 4),
            "ring_f1": round(ring_f1, 4),
            "avg_member_jaccard": round(avg_jaccard, 4),
        }
