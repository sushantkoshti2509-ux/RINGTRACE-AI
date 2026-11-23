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


@router.get("/topology", summary="Get directed graph topology for a mule ring")
def get_ring_topology(ring_id: Optional[str] = Query(None)):
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

    # Assign topological rank or left-to-right layer for visual clarity
    try:
        topo_order = list(nx.topological_sort(G))
        node_tiers = {n: idx for idx, n in enumerate(topo_order)}
    except Exception:
        # Fallback if cycles exist
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
        })

    return {
        "ring_id": selected_ring.get("candidate_ring_id"),
        "total_volume": float(selected_ring.get("total_volume", 0.0)),
        "risk_score": float(selected_ring.get("composite_risk_score", 0.85)),
        "nodes": nodes,
        "edges": edges,
        "bottlenecks": bottlenecks,
    }


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

    return result
