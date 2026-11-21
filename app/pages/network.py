"""
RINGTRACE AI - Network & Mule Ring Graph Visualization Page.
Interactive multi-hop transaction graph visualization with clear visual legends,
chronological laundering flow trails, and structural topology analysis.
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
    st.markdown("""
    <div class="top-banner">
        <div class="top-title">
            <span>🕸️ Network & Mule Ring Graph Investigation</span>
            <span class="top-badge">NetworkX + Plotly</span>
        </div>
        <p class="top-desc">
            Visualize coordinated transaction topologies, track multi-hop money laundering chains, and inspect cross-bank hops.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Load candidate rings & data
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

    # Ring Selector Bar
    col_sel, col_stat1, col_stat2 = st.columns([3, 1, 1])

    with col_sel:
        ring_options = [
            f"{r['candidate_ring_id']} • {r['topology_type']} • Risk: {r['ring_risk_score']:.2f} ({len(r['member_accounts'])} Accounts, ₹{r['total_volume']:,.0f})"
            for r in candidate_rings
        ]
        selected_ring_str = st.selectbox("Select Candidate Ring to Inspect:", ring_options)
        selected_ring_id = selected_ring_str.split(" • ")[0]

    ring_data = next((r for r in candidate_rings if r["candidate_ring_id"] == selected_ring_id), None)
    if not ring_data:
        st.error("Ring not found.")
        return

    with col_stat1:
        st.metric("Ring Risk Score", f"{ring_data['ring_risk_score']:.2f}", delta="Critical Alert")

    with col_stat2:
        st.metric("Total Laundered", f"₹{ring_data['total_volume']:,.0f}", delta=f"{ring_data['hop_count']} Hops")

    # Visual Legend Bar
    st.markdown("""
    <div style="background: white; border: 1px solid #E2E8F0; border-radius: 8px; padding: 10px 16px; margin: 12px 0 16px 0; display: flex; gap: 24px; align-items: center; flex-wrap: wrap;">
        <span style="font-size: 0.82rem; font-weight: 700; color: #475569;">INSTITUTION LEGEND:</span>
        <span class="bank-pill-a">🏦 Bank A (Primary)</span>
        <span class="bank-pill-b">🏦 Bank B (Partner)</span>
        <span class="bank-pill-c">🏦 Bank C (Partner)</span>
        <span style="font-size: 0.82rem; font-weight: 700; color: #DC2626;">🔴 Red Outline = Flagged Mule Account</span>
        <span style="font-size: 0.82rem; color: #64748B;">➡️ Gray Lines = Transaction Transfer Path</span>
    </div>
    """, unsafe_allow_html=True)

    # Build Subgraph for the selected candidate ring
    member_set = set(ring_data["member_accounts"])
    builder = TransactionGraphBuilder()
    full_G = builder.build_graph(accounts_df, transactions_df)
    sub_G = full_G.subgraph(member_set)

    # Layout using circular or spring for clarity
    if ring_data["topology_type"] in ["FAN_OUT_SPLITTER", "FAN_IN_COLLECTOR"]:
        pos = nx.spring_layout(sub_G, seed=42, k=1.2)
    elif ring_data["topology_type"] == "CIRCULAR_LAYERING":
        pos = nx.circular_layout(sub_G)
    else:
        pos = nx.spring_layout(sub_G, seed=42, k=1.0)

    # Edge Traces
    edge_x = []
    edge_y = []
    edge_mid_x = []
    edge_mid_y = []
    edge_hover_text = []

    for u, v, d in sub_G.edges(data=True):
        x0, y0 = pos[u]
        x1, y1 = pos[v]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
        
        # Midpoint for transfer amount label
        mx = (x0 + x1) / 2
        my = (y0 + y1) / 2
        edge_mid_x.append(mx)
        edge_mid_y.append(my)
        weight = d.get("weight", 0.0)
        edge_hover_text.append(f"Transfer: ₹{weight:,.2f}")

    edge_trace = go.Scatter(
        x=edge_x,
        y=edge_y,
        line=dict(width=2.5, color="#94A3B8"),
        hoverinfo="none",
        mode="lines",
    )

    edge_label_trace = go.Scatter(
        x=edge_mid_x,
        y=edge_mid_y,
        mode="text",
        text=edge_hover_text,
        textposition="top center",
        hoverinfo="none",
        textfont=dict(size=10, color="#475569"),
    )

    # Node Traces
    node_x = []
    node_y = []
    node_labels = []
    node_hover = []
    node_colors = []
    node_line_colors = []
    node_sizes = []

    bank_color_map = {
        "BANK_A": "#3B82F6",  # Blue
        "BANK_B": "#10B981",  # Green
        "BANK_C": "#F59E0B",  # Orange
    }

    risk_map = dict(zip(risk_scores_df["account_id"], risk_scores_df["risk_score"]))

    for node in sub_G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        
        node_bank = sub_G.nodes[node].get("bank_id", "BANK_A")
        score = risk_map.get(node, 0.5)
        role = sub_G.nodes[node].get("ring_role", "MEMBER").replace("_", " ").title()

        node_labels.append(f"{node}<br>({node_bank})")
        node_colors.append(bank_color_map.get(node_bank, "#64748B"))
        node_sizes.append(38)
        node_line_colors.append("#EF4444" if score >= 0.5 else "#FFFFFF")

        node_hover.append(
            f"<b>{node}</b><br>"
            f"Bank: {node_bank}<br>"
            f"Role: {role}<br>"
            f"Risk Score: {score:.3f}<br>"
            f"Status: FLAGGED MULE"
        )

    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode="markers+text",
        text=node_labels,
        textposition="bottom center",
        hoverinfo="text",
        hovertext=node_hover,
        marker=dict(
            color=node_colors,
            size=node_sizes,
            line=dict(width=3.5, color=node_line_colors),
        ),
        textfont=dict(size=11, color="#0F172A", family="Plus Jakarta Sans"),
    )

    fig = go.Figure(
        data=[edge_trace, edge_label_trace, node_trace],
        layout=go.Layout(
            showlegend=False,
            hovermode="closest",
            margin=dict(b=20, l=20, r=20, t=20),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            height=460,
            paper_bgcolor="#F8FAFC",
            plot_bgcolor="#F8FAFC",
        ),
    )

    st.plotly_chart(fig, use_container_width=True)

    # Detailed Money Trail Timeline (Step-by-Step Flow)
    st.subheader(f"⏱️ Chronological Laundering Money Trail ({selected_ring_id})")
    st.caption("Step-by-step transfer sequencing showing how fast money hopped across institutions:")

    ring_txs = transactions_df[
        (transactions_df["sender_account"].isin(member_set)) &
        (transactions_df["receiver_account"].isin(member_set))
    ].sort_values("timestamp").reset_index(drop=True)

    if not ring_txs.empty:
        # Render visual timeline steps
        steps_cols = st.columns(min(len(ring_txs), 4))
        for idx, row in ring_txs.iterrows():
            col_target = steps_cols[idx % len(steps_cols)]
            with col_target:
                s_bank = row['sender_bank']
                r_bank = row['receiver_bank']
                is_cross = s_bank != r_bank
                cross_tag = '<span class="badge-danger">Cross-Bank</span>' if is_cross else '<span class="badge-info">Internal</span>'

                st.markdown(f"""
                <div style="background: white; border: 1px solid #E2E8F0; border-radius: 8px; padding: 12px; margin-bottom: 10px;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                        <span style="font-size: 0.75rem; font-weight: 700; color: #64748B;">HOP #{idx+1}</span>
                        {cross_tag}
                    </div>
                    <div style="font-size: 1.1rem; font-weight: 800; color: #0F172A;">₹{row['amount']:,.2f}</div>
                    <div style="font-size: 0.8rem; color: #334155; margin-top: 4px;">
                        <b>From:</b> {row['sender_account']} ({s_bank})<br>
                        <b>To:</b> {row['receiver_account']} ({r_bank})
                    </div>
                    <div style="font-size: 0.72rem; color: #64748B; margin-top: 6px;">
                        🕒 {row['timestamp']}
                    </div>
                </div>
                """, unsafe_allow_html=True)

        with st.expander("📄 View Full Transaction Log for This Ring"):
            st.dataframe(
                ring_txs[["timestamp", "transaction_id", "sender_account", "sender_bank", "receiver_account", "receiver_bank", "amount", "transaction_type"]],
                hide_index=True,
                use_container_width=True,
            )
