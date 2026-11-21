"""
Feature 1: Interactive Network Visualizer using Plotly.
Visualizes bank-wise account nodes, connections between suspicious accounts,
transaction amount on each connection, direction, and identified clusters.
"""

from typing import Dict, Any, List, Optional
import networkx as nx
import plotly.graph_objects as go
import numpy as np


class CrossBankNetworkVisualizer:
    """Generates publication-quality interactive network graphs for Streamlit and web UI."""

    BANK_COLORS = {
        "BANK_A": "#3B82F6",  # Blue
        "BANK_B": "#10B981",  # Green
        "BANK_C": "#8B5CF6",  # Purple
        "SUSPICIOUS_MULE": "#EF4444",  # Red
    }

    def create_plotly_network(
        self,
        graph: nx.DiGraph,
        highlight_nodes: Optional[List[str]] = None,
        title: str = "Cross-Bank Fraud Network Topology",
    ) -> go.Figure:
        """Constructs an interactive 2D node-link graph with edge directional annotations."""
        if len(graph) == 0:
            fig = go.Figure()
            fig.update_layout(title="No transactions or accounts in selected network.")
            return fig

        highlight_set = set(highlight_nodes or [])

        # Compute Spring Layout
        pos = nx.spring_layout(graph, k=0.45, iterations=50, seed=42)

        # 1. Prepare Edge Traces
        edge_x = []
        edge_y = []
        edge_hover = []

        for u, v, data in graph.edges(data=True):
            if u not in pos or v not in pos:
                continue
            x0, y0 = pos[u]
            x1, y1 = pos[v]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
            amt = data.get("amount", 0.0)
            ts = data.get("timestamp", "")
            edge_hover.append(f"{u} ➔ {v}<br>Amount: ₹{amt:,.2f}<br>Time: {ts}")

        edge_trace = go.Scatter(
            x=edge_x,
            y=edge_y,
            line=dict(width=1.5, color="#94A3B8"),
            hoverinfo="none",
            mode="lines",
        )

        # 2. Prepare Node Traces
        node_x = []
        node_y = []
        node_colors = []
        node_sizes = []
        node_hover = []
        node_text = []

        for node in graph.nodes():
            if node not in pos:
                continue
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)

            attrs = graph.nodes[node]
            bank = attrs.get("bank_id", "BANK_A")
            is_mule = attrs.get("is_mule", 0) or (node in highlight_set)
            in_deg = graph.in_degree(node)
            out_deg = graph.out_degree(node)

            # Node Color & Size
            if is_mule or node in highlight_set:
                node_colors.append(self.BANK_COLORS["SUSPICIOUS_MULE"])
                node_sizes.append(22)
            else:
                node_colors.append(self.BANK_COLORS.get(bank, "#64748B"))
                node_sizes.append(14)

            node_text.append(node.split(":")[-1] if ":" in node else node)
            node_hover.append(
                f"<b>Account: {node}</b><br>"
                f"Bank: {bank}<br>"
                f"Incoming Transfers (In-Degree): {in_deg}<br>"
                f"Outgoing Transfers (Out-Degree): {out_deg}<br>"
                f"Status: {'🚨 SUSPICIOUS MULE' if is_mule else '✅ Clean Profile'}"
            )

        node_trace = go.Scatter(
            x=node_x,
            y=node_y,
            mode="markers+text",
            text=node_text,
            textposition="top center",
            hovertext=node_hover,
            hoverinfo="text",
            marker=dict(
                size=node_sizes,
                color=node_colors,
                line=dict(width=2, color="#FFFFFF"),
            ),
        )

        # Assemble layout
        fig = go.Figure(
            data=[edge_trace, node_trace],
            layout=go.Layout(
                title=f"<b>{title}</b>",
                titlefont_size=16,
                showlegend=False,
                hovermode="closest",
                margin=dict(b=20, l=20, r=20, t=50),
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                plot_bgcolor="#F8FAFC",
                template="plotly_white",
                height=520,
            ),
        )

        return fig
