"""
FastAPI REST API router for Mule Ring Interception & ROI Simulation.
Provides endpoints for topology exploration, choke point bottleneck analysis,
and graduated countermeasure simulation.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Query, HTTPException, status
from pydantic import BaseModel
import networkx as nx

from src.interception.interception_engine import MuleInterceptionEngine

router = APIRouter(prefix="/api/v1/interception", tags=["Interception & ROI Simulation"])

engine = MuleInterceptionEngine()


class InterceptionRequest(BaseModel):
    ring_id: str
    target_node: str
    strategy_key: str = "COOLING_OFF_DELAY"
    delay_minutes: int = 60
    officer_id: str = "COMPLIANCE-OFFICER-402"


@router.get("/rings", summary="List discovered mule rings for interception")
def get_candidate_rings():
    rings = engine.get_candidate_rings()
    summaries = []
    for r in rings:
        summaries.append({
            "ring_id": r.get("candidate_ring_id"),
            "mule_count": r.get("mule_count", len(r.get("member_accounts", []))),
            "total_volume": float(r.get("total_volume", 0.0)),
            "risk_score": float(r.get("composite_risk_score", 0.85)),
            "pattern_type": r.get("pattern_type", "Rapid Dispersion Ring"),
            "primary_bank": r.get("primary_bank", "BANK_A"),
        })
    return {"rings": summaries}


@router.get("/strategies", summary="List regulatory disruption strategies")
def get_strategies():
    return {"strategies": engine.STRATEGIES}


@router.get("/topology", summary="Get directed graph topology for a mule ring or unified 4-bank ecosystem")
def get_ring_topology(
    ring_id: Optional[str] = Query(None, description="Candidate Ring ID, or omit/'UNIFIED_ECOSYSTEM' for full 4-bank unified network"),
    mode: Optional[str] = Query(None, description="'unified' or 'ring'"),
):
    # If explicitly requesting unified ecosystem or no ring_id specified (and not mode=='ring')
    is_unified = (
        mode == "unified"
        or ring_id in [None, "", "UNIFIED_ECOSYSTEM", "ALL", "ECOSYSTEM"]
    )

    if is_unified:
        G, ecosystem_txs, metadata = engine.build_unified_ecosystem_graph()
        bottlenecks = engine.analyze_bottlenecks(G)
        bottleneck_map = {b["node_id"]: b for b in bottlenecks}

        nodes = []
        for node in G.nodes():
            b_info = bottleneck_map.get(node, {})
            node_data = G.nodes[node]
            bank = node_data.get("bank_id", "BANK_A")
            role = node_data.get("role") or b_info.get("role", "Transit Relay Account")
            pat_type = node_data.get("pattern_type", "INTERBANK_CLEARING")
            is_mule = int(node_data.get("is_mule", 0))

            nodes.append({
                "id": node,
                "masked_id": engine.mask_account_id(node),
                "bank": bank,
                "role": role,
                "pattern_type": pat_type,
                "is_mule": is_mule,
                "tier": 0 if bank == "BANK_A" else (1 if bank == "BANK_B" else (2 if bank == "BANK_C" else 3)),
                "in_degree": G.in_degree(node),
                "out_degree": G.out_degree(node),
                "strategic_score": b_info.get("strategic_score", 0.5),
                "betweenness": b_info.get("betweenness_centrality", 0.0),
                "inbound_volume": b_info.get("inbound_volume", 0.0),
                "outbound_volume": b_info.get("outbound_volume", 0.0),
            })

        edges = []
        for u, v, data in G.edges(data=True):
            edges.append({
                "id": f"{u}->{v}",
                "source": u,
                "target": v,
                "amount": float(data.get("amount", 0.0)),
                "timestamp": str(data.get("timestamp", "")),
                "transaction_id": str(data.get("transaction_id", "")),
                "is_cross_bank": bool(data.get("is_cross_bank", False)),
                "sender_bank": str(data.get("sender_bank", "")),
                "receiver_bank": str(data.get("receiver_bank", "")),
                "is_suspicious": int(data.get("is_suspicious", 0)),
                "pattern_type": str(data.get("pattern_type", "")),
                "channel": str(data.get("channel", "UPI_P2P")),
            })

        return {
            "ring_id": "UNIFIED_ECOSYSTEM",
            "is_unified": True,
            "title": metadata["title"],
            "banks_involved": metadata["banks_involved"],
            "total_volume": metadata["total_volume"],
            "suspicious_volume": metadata["suspicious_volume"],
            "risk_score": 0.88,
            "detected_patterns": metadata.get("detected_patterns", []),
            "nodes": nodes,
            "edges": edges,
            "bottlenecks": bottlenecks,
        }

    # Otherwise, handle specific candidate ring
    rings = engine.get_candidate_rings()
    selected_ring = None
    if ring_id:
        for r in rings:
            if r.get("candidate_ring_id") == ring_id:
                selected_ring = r
                break
    if not selected_ring and rings:
        selected_ring = rings[0]

    if not selected_ring:
        raise HTTPException(status_code=404, detail="No mule ring candidates available")

    G, ring_txs = engine.build_ring_subgraph(selected_ring)
    bottlenecks = engine.analyze_bottlenecks(G)
    bottleneck_map = {b["node_id"]: b for b in bottlenecks}

    # Assign topological rank or fallback
    try:
        topo_order = list(nx.topological_sort(G))
        node_tiers = {n: idx for idx, n in enumerate(topo_order)}
    except Exception:
        node_tiers = {n: i for i, n in enumerate(G.nodes())}

    nodes = []
    for node in G.nodes():
        b_info = bottleneck_map.get(node, {})
        bank = G.nodes[node].get("bank_id", "BANK_A")
        role = b_info.get("role", "Transit Relay Account")
        tier = node_tiers.get(node, 0)

        nodes.append({
            "id": node,
            "masked_id": engine.mask_account_id(node),
            "bank": bank,
            "role": role,
            "tier": tier,
            "in_degree": G.in_degree(node),
            "out_degree": G.out_degree(node),
            "strategic_score": b_info.get("strategic_score", 0.5),
            "betweenness": b_info.get("betweenness_centrality", 0.0),
            "inbound_volume": b_info.get("inbound_volume", 0.0),
            "outbound_volume": b_info.get("outbound_volume", 0.0),
        })

    edges = []
    for u, v, data in G.edges(data=True):
        edges.append({
            "id": f"{u}->{v}",
            "source": u,
            "target": v,
            "amount": float(data.get("amount", 0.0)),
            "timestamp": str(data.get("timestamp", "")),
            "transaction_id": str(data.get("transaction_id", "")),
            "is_cross_bank": bool(data.get("is_cross_bank", False)),
            "sender_bank": str(data.get("sender_bank", "")),
            "receiver_bank": str(data.get("receiver_bank", "")),
            "is_suspicious": 1,
            "pattern_type": selected_ring.get("topology_type", "CIRCULAR_LAYERING"),
            "channel": "IMPS_INSTANT",
        })

    return {
        "ring_id": selected_ring.get("candidate_ring_id"),
        "is_unified": False,
        "total_volume": float(selected_ring.get("total_volume", 0.0)),
        "risk_score": float(selected_ring.get("composite_risk_score", 0.85)),
        "nodes": nodes,
        "edges": edges,
        "bottlenecks": bottlenecks,
    }


@router.get("/ecosystem", summary="Get full 4-bank unified financial clearing and mule detection ecosystem")
def get_unified_ecosystem():
    return get_ring_topology(ring_id="UNIFIED_ECOSYSTEM", mode="unified")


@router.post("/simulate", summary="Simulate targeted interception countermeasure")
def simulate_countermeasure(payload: InterceptionRequest):
    rings = engine.get_candidate_rings()
    selected_ring = None
    for r in rings:
        if r.get("candidate_ring_id") == payload.ring_id:
            selected_ring = r
            break
    if not selected_ring and rings:
        selected_ring = rings[0]

    if not selected_ring:
        raise HTTPException(status_code=404, detail="Mule ring candidate not found")

    result = engine.simulate_interception(
        ring=selected_ring,
        target_node=payload.target_node,
        strategy_key=payload.strategy_key,
        delay_minutes=payload.delay_minutes,
        officer_id=payload.officer_id,
    )

    # Clean any internal sensitive keys if present
    if "audit_trail" in result and "rbi_directive_citation" in result["audit_trail"]:
        del result["audit_trail"]["rbi_directive_citation"]
    if "audit_trail" in result and "central_directive_citation" in result["audit_trail"]:
        del result["audit_trail"]["central_directive_citation"]

    return result
