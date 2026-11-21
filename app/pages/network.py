"""
RINGTRACE AI - Network & Mule Ring Graph Visualization Page.
Interactive multi-hop transaction graph visualization using Plotly & NetworkX.
"""

import json
from pathlib import Path
import streamlit as st
import pandas as pd
import numpy as np
import networkx as nx
import plotly.graph_objects as go

import config
from src.graph.builder import TransactionGraphBuilder


def render():
    st.markdown('<h1 class="main-title">🕸️ Network & Mule Ring Graph Investigation</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Explore coordinated cross-bank transaction paths, topologies, and multi-hop fund flows</p>', unsafe_allow_html=True)

    # Load candidate rings
    rings_path = config.REPORTS_DIR / "candidate_rings.json"
    acc_path = config.PROCESSED_DATA_DIR / "accounts.csv"
    tx_path = config.PROCESSED_DATA_DIR / "transactions.csv"
    risk_path = config.PROCESSED_DATA_DIR / "risk_scores.csv"

    if not rings_path.exists() or not tx_path.exists():
        st.warning("Data not found. Please run `python run_pipeline.py` first.")
        return

    with open(rings_path, "r") as f:
        candidate_rings = json.load(f)

    accounts_df = pd.read_csv(acc_path)
    transactions_df = pd.read_csv(tx_path)
    risk_scores_df = pd.read_csv(risk_path)

    # Controls
    col_ctrl1, col_ctrl2, col_ctrl3 = st.columns([2, 2, 2])
    
    with col_ctrl1:
        ring_options = [
            f"{r['candidate_ring_id']} | Risk: {r['ring_risk_score']:.2f} | {r['topology_type']} ({len(r['member_accounts'])} accs)"
            for r in candidate_rings
        ]
        selected_ring_str = st.selectbox("Select Candidate Ring to Inspect:", ring_options)
        selected_ring_id = selected_ring_str.split(" | ")[0]

    # Find the selected ring dict
    ring_data = next((r for r in candidate_rings if r["candidate_ring_id"] == selected_ring_id), None)
    if not ring_data:
        st.error("Ring not found.")
        return

    with col_ctrl2:
        st.metric("Ring Risk Score", f"{ring_data['ring_risk_score']:.3f}", delta=ring_data["topology_type"])

    with col_ctrl3:
        banks_str = ", ".join(ring_data["banks_involved"])
        st.metric("Institutions Involved", banks_str, delta=f"Cross-Bank: {ring_data['is_cross_bank']}")

    # Build Subgraph of the candidate ring
    member_set = set(ring_data["member_accounts"])
    builder = TransactionGraphBuilder()
    full_G = builder.build_graph(accounts_df, transactions_df)
    sub_G = full_G.subgraph(member_set)

    # Graph Layout using spring layout
    pos = nx.spring_layout(sub_G, seed=42, k=0.8)

    # Prepare Plotly Edge Traces
    edge_x = []
    edge_y = []
    edge_text = []

    for u, v, d in sub_G.edges(data=True):
        x0, y0 = pos[u]
        x1, y1 = pos[v]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
        weight = d.get("weight", 0.0)
        edge_text.append(f"₹{weight:,.2f}")

    edge_trace = go.Scatter(
        x=edge_x,
        y=edge_y,
        line=dict(width=2, color="#94A3B8"),
        hoverinfo="none",
        mode="lines",
    )

    # Prepare Node Traces
    node_x = []
    node_y = []
    node_text = []
    node_colors = []
    node_sizes = []

    bank_color_map = {
        "BANK_A": "#3B82F6",  # Blue
        "BANK_B": "#10B981",  # Green
        "BANK_C": "#F59E0B",  # Orange
    }

    # Get risk score lookup
    risk_map = dict(zip(risk_scores_df["account_id"], risk_scores_df["risk_score"]))

    for node in sub_G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        
        node_bank = sub_G.nodes[node].get("bank_id", "BANK_A")
        score = risk_map.get(node, 0.5)
        role = sub_G.nodes[node].get("ring_role", "MEMBER")

        node_colors.append(bank_color_map.get(node_bank, "#64748B"))
        node_sizes.append(25 + int(score * 20))
        node_text.append(
            f"<b>{node}</b><br>"
            f"Bank: {node_bank}<br>"
            f"Role: {role}<br>"
            f"Risk Score: {score:.3f}"
        )

    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode="markers+text",
        text=[n for n in sub_G.nodes()],
        textposition="top center",
        hoverinfo="text",
        hovertext=node_text,
        marker=dict(
            color=node_colors,
            size=node_sizes,
            line=dict(width=2, color="#FFFFFF"),
        ),
    )

    fig = go.Figure(
        data=[edge_trace, node_trace],
        layout=go.Layout(
            title=f"<b>Interactive Network Graph — {selected_ring_id}</b> ({ring_data['topology_type']})",
            showlegend=False,
            hovermode="closest",
            margin=dict(b=20, l=20, r=20, t=40),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            height=500,
            paper_bgcolor="#F8FAFC",
            plot_bgcolor="#F8FAFC",
        ),
    )

    st.plotly_chart(fig, use_container_width=True)

    # Detailed Member Breakdown Table
    st.subheader(f"📋 Member Accounts & Roles in {selected_ring_id}")
    
    # Filter transactions inside this ring
    ring_txs = transactions_df[
        (transactions_df["sender_account"].isin(member_set)) &
        (transactions_df["receiver_account"].isin(member_set))
    ].sort_values("timestamp")

    col_t1, col_t2 = st.columns([3, 2])
    with col_t1:
        st.markdown("**Internal Transaction Flow Sequence:**")
        st.dataframe(
            ring_txs[["timestamp", "sender_account", "sender_bank", "receiver_account", "receiver_bank", "amount", "transaction_type"]],
            hide_index=True,
            use_container_width=True,
        )

    with col_t2:
        st.markdown("**Network Structural Summary:**")
        st.write(f"- **Total Flow Volume:** ₹{ring_data['total_volume']:,.2f}")
        st.write(f"- **Longest Hop Depth:** {ring_data['hop_count']} hops")
        st.write(f"- **Cross-Bank Transaction Count:** {ring_data['cross_bank_tx_count']}")
        st.write(f"- **Cycle / Loop Detected:** {'Yes' if ring_data['has_cycles'] else 'No'}")
        st.write(f"- **Banks Spanned:** {', '.join(ring_data['banks_involved'])}")
