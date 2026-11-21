"""
Feature 1: Fraud Network Explorer Dashboard View.
Interactive graph exploration showing bank-wise accounts, directional connections,
transaction amounts, cycle detection, and identified suspicious clusters.
"""

import streamlit as st
import pandas as pd
import networkx as nx
import plotly.graph_objects as go

import config
from src.adapter.detection_adapter import DetectionAdapter
from src.cross_bank_network.graph_builder import CrossBankGraphBuilder
from src.cross_bank_network.network_analysis import CrossBankNetworkAnalyzer
from src.cross_bank_network.ring_visualization import CrossBankNetworkVisualizer


@st.cache_resource
def load_network_data():
    adapter = DetectionAdapter()
    accounts, transactions, risk_scores, rings, _ = adapter.load_data()
    builder = CrossBankGraphBuilder()
    graph = builder.build_network_graph(transactions, accounts, use_qualified_ids=True)
    analyzer = CrossBankNetworkAnalyzer(graph)
    visualizer = CrossBankNetworkVisualizer()
    return accounts, transactions, rings, graph, analyzer, visualizer


def render():
    st.markdown("""
    <div class="top-banner">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 12px;">
            <div>
                <div class="top-title">
                    <span>🕸️ Fraud Network Explorer</span>
                    <span class="top-badge">Feature 1: Cross-Bank Network Intelligence</span>
                </div>
                <p class="top-desc">
                    Uncover coordinated mule rings connecting Bank A, Bank B, and Bank C through transaction graphs, cycle detection, and clustering.
                </p>
            </div>
            <div style="text-align: right;">
                <span class="badge-success">● NetworkX Graph Engine Active</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    accounts, transactions, rings, graph, analyzer, visualizer = load_network_data()

    if graph.number_of_nodes() == 0:
        st.warning("No network graph data available. Please generate transactions first.")
        return

    # Top KPI Metrics Row
    m1, m2, m3, m4, m5 = st.columns(5)
    with m1:
        st.metric("Graph Nodes", f"{graph.number_of_nodes():,}")
    with m2:
        st.metric("Directed Edges", f"{graph.number_of_edges():,}")
    with m3:
        communities = analyzer.detect_communities()
        st.metric("Detected Clusters", len(communities))
    with m4:
        cycles = analyzer.detect_cycles()
        st.metric("Circular Loops", len(cycles))
    with m5:
        rapid_hops = analyzer.analyze_temporal_turnaround()
        st.metric("Rapid Forwards (<10m)", len(rapid_hops))

    st.markdown("<br>", unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs([
        "🌐 Interactive Network Topology",
        "🔄 Circular Pattern / Cycle Detector",
        "⚡ Rapid Forwarding Velocity (< 10 min)",
        "👥 Interconnected Mule Clusters",
    ])

    # TAB 1: Network Graph
    with tab1:
        st.markdown("##### 🔍 Subgraph Filter & Visualization")
        col_f1, col_f2 = st.columns([2, 1])

        with col_f1:
            ring_options = ["All Candidate Mule Rings"] + [
                f"{r.get('candidate_ring_id')} - {r.get('topology_type', 'CHAIN')} ({len(r.get('member_accounts', []))} accs, ₹{r.get('total_volume', 0):,.0f})"
                for r in rings
            ]
            selected_ring_str = st.selectbox("Focus on Mule Ring Subgraph", ring_options)

        # Extract focused nodes
        if selected_ring_str != "All Candidate Mule Rings":
            ring_id = selected_ring_str.split(" - ")[0]
            selected_ring = next((r for r in rings if r.get("candidate_ring_id") == ring_id), None)
            members = selected_ring.get("member_accounts", []) if selected_ring else []

            # Find matching node names in graph
            focus_nodes = []
            for n in graph.nodes():
                raw_id = n.split(":")[-1] if ":" in n else n
                if raw_id in members or n in members:
                    focus_nodes.append(n)

            # Extract 1-hop neighborhood of ring members
            sub_nodes = set(focus_nodes)
            for fn in focus_nodes:
                sub_nodes.update(graph.predecessors(fn))
                sub_nodes.update(graph.successors(fn))
            subgraph = graph.subgraph(list(sub_nodes)[:40])
            highlight = focus_nodes
        else:
            # Show top connected core nodes
            top_nodes = sorted(graph.nodes(), key=lambda n: graph.degree(n), reverse=True)[:35]
            subgraph = graph.subgraph(top_nodes)
            highlight = []

        # Render Plotly interactive graph
        fig = visualizer.create_plotly_network(
            subgraph,
            highlight_nodes=highlight,
            title="Cross-Bank Transaction Network (Bank A • Bank B • Bank C)",
        )
        st.plotly_chart(fig, use_container_width=True)

        # Visual Legend Guide
        st.markdown("""
        <div style="background: white; border: 1px solid #E2E8F0; border-radius: 8px; padding: 10px 16px; display: flex; gap: 20px; align-items: center; flex-wrap: wrap;">
            <span style="font-size: 0.85rem; font-weight: 700; color: #475569;">LEGEND:</span>
            <span><span style="color: #3B82F6; font-size: 1.2rem;">●</span> Bank A Account</span>
            <span><span style="color: #10B981; font-size: 1.2rem;">●</span> Bank B Account</span>
            <span><span style="color: #8B5CF6; font-size: 1.2rem;">●</span> Bank C Account</span>
            <span><span style="color: #EF4444; font-size: 1.2rem;">●</span> High-Risk Mule Node</span>
        </div>
        """, unsafe_allow_html=True)

    # TAB 2: Cycles Detector
    with tab2:
        st.markdown("##### 🔄 Identified Circular Laundering Patterns (Layering Cycles)")
        st.caption("Cycles represent funds transferred through a chain of accounts and returning to the originator or colluding node.")
        if cycles:
            cycle_data = []
            for idx, c in enumerate(cycles[:15]):
                banks_in_c = [n.split(":")[0] if ":" in n else "BANK_A" for n in c]
                cycle_data.append({
                    "Cycle ID": f"CYCLE_{idx+1:02d}",
                    "Hop Count": len(c),
                    "Account Path": " ➔ ".join(c) + f" ➔ {c[0]}",
                    "Banks Involved": ", ".join(sorted(set(banks_in_c))),
                    "Is Cross-Bank": "✅ Yes" if len(set(banks_in_c)) > 1 else "No (Internal)",
                })
            st.dataframe(pd.DataFrame(cycle_data), use_container_width=True, hide_index=True)
        else:
            st.info("No elementary transaction cycles detected in the current ledger subset.")

    # TAB 3: Rapid Turnaround
    with tab3:
        st.markdown("##### ⚡ Rapid Fund Forwarding (< 10 Minutes)")
        st.caption("Identifies accounts that receive payment transfers and forward them almost immediately to down-stream destinations.")
        if rapid_hops:
            rapid_df = pd.DataFrame(rapid_hops[:20])
            st.dataframe(rapid_df, use_container_width=True, hide_index=True)
        else:
            st.info("No rapid turnaround instances detected under 600s threshold.")

    # TAB 4: Interconnected Clusters
    with tab4:
        st.markdown("##### 👥 Interconnected Suspicious Account Communities")
        if communities:
            comm_rows = []
            for c in communities[:10]:
                comm_rows.append({
                    "Cluster ID": c["community_id"],
                    "Account Count": c["size"],
                    "Banks Involved": ", ".join(c["banks_involved"]),
                    "Cross-Bank Syndicate": "🚩 High Alert" if c["is_cross_bank"] else "Single-Bank",
                    "Member Accounts Preview": ", ".join(c["members"][:5]) + ("..." if len(c["members"]) > 5 else ""),
                })
            st.dataframe(pd.DataFrame(comm_rows), use_container_width=True, hide_index=True)
        else:
            st.info("No multi-account communities identified.")
