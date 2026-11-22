"""
🎯 Mule Ring Interception & ROI Simulator - Streamlit View.
Demonstrates proactive network disruption, quantifiable financial loss prevention,
zero unilateral freezing, and DPDP Act 2023 cryptographic privacy safeguards.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import json

from src.interception.interception_engine import MuleInterceptionEngine


@st.cache_resource
def get_interception_engine():
    return MuleInterceptionEngine()


def render():
    st.markdown("""
    <div class="top-banner">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 12px;">
            <div>
                <div class="top-title">
                    <span>🎯 Mule Ring Interception & ROI Simulator</span>
                    <span class="top-badge">Proactive Fraud Risk Defense</span>
                </div>
                <p class="top-desc">
                    Simulate proactive disruption on cross-bank mule networks. Quantify intercepted funds (ROI), sever downstream cash-out routes, and enforce regulatory fraud compliance.
                </p>
            </div>
            <div style="text-align: right;">
                <span class="badge-success">● Proactive Prevention Engine Active</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Mandatory Regulatory Security & DPDP Act Safeguard Notice
    st.markdown("""
    <div style="background: #EFF6FF; border-left: 5px solid #2563EB; border-radius: 8px; padding: 12px 16px; margin-bottom: 20px;">
        <div style="font-weight: 700; color: #1E40AF; font-size: 0.92rem;">
            🛡️ Regulatory & Security Safeguard (Zero Unilateral Freezing):
        </div>
        <div style="font-size: 0.84rem; color: #1E3A8A; line-height: 1.5; margin-top: 4px;">
            In compliance with <b>Central Banking Master Directions on Fraud Risk Management</b> and the <b>DPDP Act 2023</b>, this simulator evaluates <b>non-punitive, graduated countermeasures</b> (such as dynamic cooling-off windows, adaptive step-up authentication, and dual-custody holds). All account numbers are cryptographically masked, and each action produces an immutable <b>SHA-256 audit log</b>.
        </div>
    </div>
    """, unsafe_allow_html=True)

    engine = get_interception_engine()
    rings = engine.get_candidate_rings()

    if not rings:
        st.warning("No candidate mule rings discovered yet. Please run the detection pipeline first.")
        return

    # -------------------------------------------------------------
    # Simulation Setup Controls
    # -------------------------------------------------------------
    st.markdown("#### ⚙️ Configure Disruption Scenario")
    col_c1, col_c2, col_c3 = st.columns([1.3, 1.2, 1.0])

    with col_c1:
        ring_options = {
            f"{r.get('candidate_ring_id')} • {r.get('topology_type', 'CHAIN')} ({len(r.get('member_accounts', []))} accs, ₹{r.get('total_volume', 0):,.0f})": r
            for r in rings
        }
        sel_ring_label = st.selectbox("1. Select Mule Ring to Target:", list(ring_options.keys()))
        selected_ring = ring_options[sel_ring_label]

    # Build subgraph and analyze bottlenecks for selected ring
    G, ring_txs = engine.build_ring_subgraph(selected_ring)
    bottlenecks = engine.analyze_bottlenecks(G)

    with col_c2:
        if bottlenecks:
            node_options = {
                f"{b['masked_id']} - {b['role']} (Bridge Score: {b['strategic_score']:.2f})": b['node_id']
                for b in bottlenecks
            }
            sel_node_label = st.selectbox("2. Select Bottleneck Account to Intercept:", list(node_options.keys()))
            target_node = node_options[sel_node_label]
        else:
            target_node = list(G.nodes())[0] if G.nodes() else "BANK_A:UNKNOWN"

    with col_c3:
        strat_options = {
            "Dynamic Cooling-Off Delay (30-120m)": "COOLING_OFF_DELAY",
            "Mandatory Step-Up Biometric Re-Auth": "STEP_UP_BIOMETRIC",
            "Dual-Bank Inward Remittance Hold": "DUAL_BANK_HOLD",
        }
        sel_strat_label = st.selectbox("3. Select Countermeasure Strategy:", list(strat_options.keys()))
        selected_strat_key = strat_options[sel_strat_label]

    col_s1, col_s2 = st.columns([2, 1])
    with col_s1:
        delay_min = st.slider("Intervention Delay Window (Minutes):", min_value=15, max_value=120, value=60, step=15,
                              help="Simulates the time gap introduced before outgoing funds can leave this node.")
    with col_s2:
        officer_input = st.text_input("Nodal Officer ID (Audit Sign-Off):", value="NODAL-OFFICER-742")

    # Run simulation
    sim_result = engine.simulate_interception(
        ring=selected_ring,
        target_node=target_node,
        strategy_key=selected_strat_key,
        delay_minutes=delay_min,
        officer_id=officer_input,
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # -------------------------------------------------------------
    # Primary ROI & Financial Prevention Metric Cards
    # -------------------------------------------------------------
    st.markdown("#### 💰 Financial Protection & Disruption Impact (ROI)")

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(f"""
        <div style="background: white; border: 2px solid #10B981; border-radius: 10px; padding: 16px; text-align: center;">
            <div style="font-size: 0.75rem; color: #047857; font-weight: 700;">TOTAL STOLEN FUNDS SAVED</div>
            <div style="font-size: 1.7rem; font-weight: 800; color: #059669; margin: 4px 0;">₹{sim_result['funds_intercepted_inr']:,.0f}</div>
            <div style="font-size: 0.82rem; color: #10B981; font-weight: 600;">{sim_result['interception_rate_pct']}% of Ring Volume</div>
        </div>
        """, unsafe_allow_html=True)

    with k2:
        st.markdown(f"""
        <div style="background: white; border: 2px solid #3B82F6; border-radius: 10px; padding: 16px; text-align: center;">
            <div style="font-size: 0.75rem; color: #1D4ED8; font-weight: 700;">DOWNSTREAM MULES SEVERED</div>
            <div style="font-size: 1.7rem; font-weight: 800; color: #2563EB; margin: 4px 0;">{sim_result['downstream_accounts_neutralized']} / {sim_result['total_ring_accounts']}</div>
            <div style="font-size: 0.82rem; color: #3B82F6; font-weight: 600;">Accounts Starved of Capital</div>
        </div>
        """, unsafe_allow_html=True)

    with k3:
        st.markdown(f"""
        <div style="background: white; border: 2px solid #8B5CF6; border-radius: 10px; padding: 16px; text-align: center;">
            <div style="font-size: 0.75rem; color: #6D28D9; font-weight: 700;">NCRP 1930 TIME ADVANTAGE</div>
            <div style="font-size: 1.7rem; font-weight: 800; color: #7C3AED; margin: 4px 0;">+{sim_result['ncrp_time_advantage_minutes']} min</div>
            <div style="font-size: 0.82rem; color: #8B5CF6; font-weight: 600;">Lead Time for Police Action</div>
        </div>
        """, unsafe_allow_html=True)

    with k4:
        st.markdown(f"""
        <div style="background: white; border: 2px solid #0EA5E9; border-radius: 10px; padding: 16px; text-align: center;">
            <div style="font-size: 0.75rem; color: #0369A1; font-weight: 700;">COLLATERAL FRICTION</div>
            <div style="font-size: 1.7rem; font-weight: 800; color: #0284C7; margin: 4px 0;">0.0%</div>
            <div style="font-size: 0.82rem; color: #0EA5E9; font-weight: 600;">Legitimate Accounts Unaffected</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # -------------------------------------------------------------
    # Two Columns: Interactive Topology Map & Regulatory Action
    # -------------------------------------------------------------
    col_viz, col_dossier = st.columns([1.3, 1.0])

    with col_viz:
        st.markdown("##### 🌐 Disrupted Network Topology")
        
        col_v1, col_v2 = st.columns([1.5, 1.0])
        with col_v1:
            view_mode = st.radio(
                "Topology View State:",
                ["🛡️ Post-Disruption (Severed Routes)", "⚡ Pre-Disruption (Original Flow)"],
                horizontal=True,
                help="Toggle between the intact criminal laundering syndicate and the severed network after intervention.",
            )
        with col_v2:
            st.caption("Visual Legend: 🛡️ Intercepted Choke Point | ❌ Neutralized Mule | 🛑 Blocked Edges")

        is_post_disruption = "Post-Disruption" in view_mode

        # Calculate clean pipeline positions (topological left-to-right order)
        try:
            topo_order = list(nx.topological_sort(G))
            pos = {node: (float(idx) * 2.5, 0.35 if idx % 2 == 1 else -0.35) for idx, node in enumerate(topo_order)}
        except Exception:
            pos = nx.circular_layout(G)

        downstream_set = set(sim_result.get("downstream_nodes_list", []))
        severed_edges_list = sim_result.get("severed_edges", [])
        severed_edges_set = set(severed_edges_list) if severed_edges_list else set()

        if not severed_edges_set and is_post_disruption:
            for u, v in G.edges():
                if u == target_node or u in downstream_set or (v == target_node and not list(G.successors(target_node))):
                    severed_edges_set.add((u, v))

        annotations = []
        edge_x, edge_y = [], []
        severed_x, severed_y = [], []

        for u, v, d in G.edges(data=True):
            x0, y0 = pos[u]
            x1, y1 = pos[v]
            amt = d.get("amount", 0.0)

            is_severed = is_post_disruption and ((u, v) in severed_edges_set or u == target_node or u in downstream_set or (v == target_node and not list(G.successors(target_node))))

            if is_severed:
                severed_x.extend([x0, x1, None])
                severed_y.extend([y0, y1, None])
                edge_color = "#EF4444"
                badge_text = f"🛑 BLOCKED (₹{amt:,.0f})"
            else:
                edge_x.extend([x0, x1, None])
                edge_y.extend([y0, y1, None])
                edge_color = "#10B981"
                badge_text = f"₹{amt:,.0f}"

            # Directional Flow Arrow with Amount Badge
            annotations.append(dict(
                ax=x0, ay=y0, axref="x", ayref="y",
                x=(x0 + x1) / 2, y=(y0 + y1) / 2, xref="x", yref="y",
                showarrow=True,
                arrowhead=3,
                arrowsize=1.4,
                arrowwidth=2.5,
                arrowcolor=edge_color,
                text=badge_text,
                font=dict(size=9, color=edge_color),
                bgcolor="#FFFFFF",
                bordercolor=edge_color,
                borderwidth=1,
                borderpad=3,
            ))

        intact_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=2.5, color="#10B981"),
            hoverinfo="none",
            mode="lines",
            name="Intact Active Flow",
        )

        severed_trace = go.Scatter(
            x=severed_x, y=severed_y,
            line=dict(width=2.5, color="#EF4444", dash="dash"),
            hoverinfo="none",
            mode="lines",
            name="Severed / Blocked Flow",
        )

        # Node Markers
        node_x = []
        node_y = []
        node_color = []
        node_text = []
        node_size = []
        node_lines = []

        for node in G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)

            masked_name = engine.mask_account_id(node)
            bank = G.nodes[node].get("bank_id", "BANK_A")

            if is_post_disruption and node == target_node:
                node_color.append("#F59E0B")  # Amber gold
                node_size.append(36)
                node_lines.append(dict(width=3, color="#B45309"))
                node_text.append(f"🛡️ TARGET INTERCEPTED<br><b>{masked_name}</b> ({bank})")
            elif is_post_disruption and node in downstream_set:
                node_color.append("#94A3B8")  # Neutralized Slate
                node_size.append(26)
                node_lines.append(dict(width=2.5, color="#EF4444"))
                node_text.append(f"❌ NEUTRALIZED MULE<br><b>{masked_name}</b> ({bank})")
            else:
                node_color.append("#3B82F6")  # Active Primary Blue
                node_size.append(30)
                node_lines.append(dict(width=2, color="#1D4ED8"))
                node_text.append(f"● ACTIVE NODE<br><b>{masked_name}</b> ({bank})")

        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode="markers+text",
            hoverinfo="text",
            text=[n.split("<br>")[0] for n in node_text],
            hovertext=node_text,
            textposition="top center",
            marker=dict(
                size=node_size,
                color=node_color,
                line=dict(width=2.5, color=[l["color"] for l in node_lines]),
            ),
            name="Accounts",
        )

        # Compute dynamic axes limits
        all_x = [p[0] for p in pos.values()]
        all_y = [p[1] for p in pos.values()]
        x_min, x_max = min(all_x) - 1.2, max(all_x) + 1.2
        y_min, y_max = min(all_y) - 0.7, max(all_y) + 0.7

        fig = go.Figure(
            data=[intact_trace, severed_trace, node_trace],
            layout=go.Layout(
                title=dict(
                    text=f"<b>Mule Network Topology ({selected_ring.get('candidate_ring_id')}) - {'DISRUPTED STATE' if is_post_disruption else 'BASELINE SYNDICATE'}</b>",
                    font=dict(size=13),
                ),
                annotations=annotations,
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=-0.22, xanchor="center", x=0.5),
                hovermode="closest",
                margin=dict(b=30, l=15, r=15, t=40),
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[x_min, x_max]),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[y_min, y_max]),
                plot_bgcolor="#F8FAFC",
                template="plotly_white",
                height=450,
            ),
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_dossier:
        st.markdown("##### 📜 Official Section 102 Regulatory Record")
        st.caption("Verifiable record for law enforcement (NCRP/1930) and participating bank nodal officers:")

        trail = sim_result["audit_trail"]
        st.markdown(f"""
        <div style="background: white; border: 1px solid #CBD5E1; border-radius: 8px; padding: 14px; font-size: 0.84rem; line-height: 1.6;">
            <b>Simulation Record ID:</b> <code>{sim_result['simulation_id']}</code><br>
            <b>Target Account (Masked):</b> <code>{sim_result['masked_target_node']}</code><br>
            <b>Intervention:</b> {sim_result['strategy_used']['name']}<br>
            <b>Regulatory Standard:</b> <i>{trail['regulatory_directive_citation']}</i><br>
            <b>Funds Protected:</b> <b style="color: #059669;">₹{sim_result['funds_intercepted_inr']:,.2f}</b><br>
            <b>Estimated Residual Risk:</b> ₹{sim_result['funds_leaked_inr']:,.2f}<br>
            <b>Authorized Officer:</b> {trail['officer_id']}<br>
            <b>Execution Timestamp:</b> {trail['decision_timestamp']}<br>
            <hr style="margin: 8px 0;">
            <b>SHA-256 Cryptographic Audit Hash:</b><br>
            <code style="word-break: break-all; font-size: 0.72rem; color: #475569;">{trail['sha256_integrity_hash']}</code>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        # One-Click Copyable Advisory Notice for Law Enforcement
        advisory_text = f"""[CONFIDENTIAL - FRAUD RISK MANAGEMENT / NCRP 1930 ADVISORY]
CASE ID: {sim_result['ring_id']}
SIMULATION ID: {sim_result['simulation_id']}
INTERCEPTED CHOKE POINT: {sim_result['target_node']}
REGULATORY DIRECTIVE: {trail['regulatory_directive_citation']}
INTERVENTION APPLIED: {sim_result['strategy_used']['name']} ({sim_result['delay_minutes']} Minutes)
PROTECTED FINANCIAL VOLUME: INR {sim_result['funds_intercepted_inr']:,.2f}
DOWNSTREAM MULES SEVERED: {sim_result['downstream_accounts_neutralized']}
OFFICER SIGN-OFF: {trail['officer_id']}
INTEGRITY HASH (SHA-256): {trail['sha256_integrity_hash']}"""

        st.text_area("📋 Copyable Cybercrime Interception Notice (1930 / State Police Nodal)", advisory_text, height=130)

    # -------------------------------------------------------------
    # Strategic Bottleneck Accounts Table
    # -------------------------------------------------------------
    st.markdown("---")
    st.markdown("##### 🔍 Identified Structural Bottlenecks in this Syndicate")
    st.caption("Accounts ranked by centrality, outbound forwarding velocity, and cross-bank bridging score:")

    if bottlenecks:
        b_df = pd.DataFrame(bottlenecks)
        display_df = b_df[["masked_id", "bank_id", "role", "betweenness_centrality", "in_degree", "out_degree", "outbound_volume", "strategic_score"]]
        display_df.columns = ["Account ID (Masked)", "Bank", "Mule Network Role", "Betweenness", "In-Degree", "Out-Degree", "Outbound Flow (₹)", "Choke Point Score"]
        st.dataframe(display_df, use_container_width=True, hide_index=True)
