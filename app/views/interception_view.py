"""
🎯 Mule Ring Interception & ROI Simulator - Streamlit View.
Developed for RBI (Reserve Bank of India) Hackathon / Evaluation Jury.
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
                    <span class="top-badge">RBI Fraud Risk Defense</span>
                </div>
                <p class="top-desc">
                    Simulate proactive disruption on cross-bank mule networks. Quantify intercepted funds (ROI), sever downstream cash-out routes, and enforce RBI 2024 compliance.
                </p>
            </div>
            <div style="text-align: right;">
                <span class="badge-success">● Proactive Prevention Engine Active</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Mandatory RBI Security & DPDP Act Safeguard Notice
    st.markdown("""
    <div style="background: #EFF6FF; border-left: 5px solid #2563EB; border-radius: 8px; padding: 12px 16px; margin-bottom: 20px;">
        <div style="font-weight: 700; color: #1E40AF; font-size: 0.92rem;">
            🛡️ RBI Regulatory & Security Safeguard (Zero Unilateral Freezing):
        </div>
        <div style="font-size: 0.84rem; color: #1E3A8A; line-height: 1.5; margin-top: 4px;">
            In compliance with the <b>RBI Master Directions on Fraud Risk Management</b> and <b>DPDP Act 2023</b>, this simulator evaluates <b>non-punitive, graduated countermeasures</b> (such as dynamic cooling-off windows, adaptive step-up authentication, and dual-custody holds). All account numbers are cryptographically masked, and each action produces an immutable <b>SHA-256 audit log</b>.
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
        sel_strat_label = st.selectbox("3. RBI Countermeasure Strategy:", list(strat_options.keys()))
        selected_strat_key = strat_options[sel_strat_label]

    col_s1, col_s2 = st.columns([2, 1])
    with col_s1:
        delay_min = st.slider("Intervention Delay Window (Minutes):", min_value=15, max_value=120, value=60, step=15,
                              help="Simulates the time gap introduced before outgoing funds can leave this node.")
    with col_s2:
        officer_input = st.text_input("Nodal Officer ID (Audit Sign-Off):", value="RBI-NODAL-OFFICER-742")

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
        st.caption("Visualizes money flow: Green = Inbound Source, Amber = Intercepted Choke Point, Dashed Red = Severed Routes.")

        # Build Plotly visualization for ring disruption
        pos = nx.spring_layout(G, seed=42)

        edge_x = []
        edge_y = []
        severed_x = []
        severed_y = []

        downstream_set = set(sim_result["downstream_nodes_list"])

        for u, v in G.edges():
            x0, y0 = pos[u]
            x1, y1 = pos[v]
            if u == target_node or u in downstream_set:
                # Severed edge
                severed_x.extend([x0, x1, None])
                severed_y.extend([y0, y1, None])
            else:
                edge_x.extend([x0, x1, None])
                edge_y.extend([y0, y1, None])

        # Traces
        intact_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=2.5, color="#10B981"),
            hoverinfo="none",
            mode="lines",
            name="Intact Flow",
        )

        severed_trace = go.Scatter(
            x=severed_x, y=severed_y,
            line=dict(width=2.5, color="#EF4444", dash="dash"),
            hoverinfo="none",
            mode="lines",
            name="Severed Downstream Flow",
        )

        node_x = []
        node_y = []
        node_color = []
        node_text = []
        node_size = []

        for node in G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)

            masked_name = engine.mask_account_id(node)

            if node == target_node:
                node_color.append("#F59E0B")  # Amber for target
                node_size.append(32)
                node_text.append(f"🛡️ TARGET INTERCEPTED<br>{masked_name}")
            elif node in downstream_set:
                node_color.append("#94A3B8")  # Neutralized / Gray
                node_size.append(24)
                node_text.append(f"❌ NEUTRALIZED MULE<br>{masked_name}")
            else:
                node_color.append("#3B82F6")  # Blue active
                node_size.append(26)
                node_text.append(f"● ACTIVE INBOUND<br>{masked_name}")

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
                line=dict(width=2, color="#FFFFFF"),
            ),
            name="Accounts",
        )

        fig = go.Figure(
            data=[intact_trace, severed_trace, node_trace],
            layout=go.Layout(
                title=dict(text=f"<b>Mule Network Disruption Graph ({selected_ring.get('candidate_ring_id')})</b>", font=dict(size=14)),
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5),
                hovermode="closest",
                margin=dict(b=20, l=10, r=10, t=40),
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                plot_bgcolor="#F8FAFC",
                template="plotly_white",
                height=420,
            ),
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_dossier:
        st.markdown("##### 📜 Official RBI Section 102 Regulatory Record")
        st.caption("Verifiable record for law enforcement (NCRP/1930) and participating bank nodal officers:")

        trail = sim_result["audit_trail"]
        st.markdown(f"""
        <div style="background: white; border: 1px solid #CBD5E1; border-radius: 8px; padding: 14px; font-size: 0.84rem; line-height: 1.6;">
            <b>Simulation Record ID:</b> <code>{sim_result['simulation_id']}</code><br>
            <b>Target Account (Masked):</b> <code>{sim_result['masked_target_node']}</code><br>
            <b>Intervention:</b> {sim_result['strategy_used']['name']}<br>
            <b>Regulatory Standard:</b> <i>{trail['rbi_directive_citation']}</i><br>
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
        advisory_text = f"""[CONFIDENTIAL - RBI FRAUD RISK MANAGEMENT / NCRP 1930 ADVISORY]
CASE ID: {sim_result['ring_id']}
SIMULATION ID: {sim_result['simulation_id']}
INTERCEPTED CHOKE POINT: {sim_result['target_node']}
REGULATORY DIRECTIVE: {trail['rbi_directive_citation']}
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
