"""
RINGTRACE AI - Private Set Intersection (PSI) Privacy Demonstration Page.
Demonstrates multi-bank privacy-preserving entity correlation using Commutative Diffie-Hellman.
"""

import json
from pathlib import Path
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

import config


def render():
    st.markdown('<h1 class="main-title">🔐 Cryptographic Private Set Intersection (PSI)</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Privacy-Preserving Cross-Bank Entity Matching Without Exchanging Customer Ledgers</p>', unsafe_allow_html=True)

    psi_path = config.REPORTS_DIR / "psi_results.json"
    if not psi_path.exists():
        st.warning("PSI results not found. Please execute `python run_pipeline.py`.")
        return

    with open(psi_path, "r") as f:
        psi = json.load(f)

    # Privacy Guarantee Alert Banner
    st.markdown("""
    <div class="safeguard-banner">
        <b>🔒 Zero-Knowledge Data Minimization Guarantee:</b><br>
        Participating banks (Bank A, Bank B, Bank C) execute a 2-round commutative Diffie-Hellman exponentiation protocol over RFC 3526 2048-bit MODP groups.
        <b>Only candidate canonical entities present in multiple institutions are uncovered.</b>
        Neither bank ever learns the non-intersecting candidate accounts, balances, or transaction details of partner banks.
    </div>
    """, unsafe_allow_html=True)

    # Candidate Volumes Row
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Bank A Flagged Candidates", f"{psi['bank_a_candidates']}")
    col2.metric("Bank B Flagged Candidates", f"{psi['bank_b_candidates']}")
    col3.metric("Bank C Flagged Candidates", f"{psi['bank_c_candidates']}")
    col4.metric("3-Way Common Mule Entities", f"{psi['three_way_intersection_count']}", delta="High Confidence Rings")

    st.markdown("---")

    # Section 1: Pairwise vs 3-Way Intersection Visualizer
    col_chart, col_details = st.columns([3, 2])

    with col_chart:
        pairs = psi["pairwise_matches"]
        categories = ["Bank A ∩ Bank B", "Bank B ∩ Bank C", "Bank A ∩ Bank C", "Bank A ∩ B ∩ C (3-Way)"]
        values = [
            pairs["BANK_A_x_BANK_B"],
            pairs["BANK_B_x_BANK_C"],
            pairs["BANK_A_x_BANK_C"],
            psi["three_way_intersection_count"],
        ]

        fig_psi = go.Figure(data=[
            go.Bar(
                x=categories,
                y=values,
                text=values,
                textposition="auto",
                marker_color=["#3B82F6", "#10B981", "#F59E0B", "#EF4444"],
            )
        ])
        fig_psi.update_layout(
            title="Cross-Bank Candidate Entity Intersections",
            yaxis=dict(title="Matched Canonical Entities"),
            height=340,
            margin=dict(l=20, r=20, t=40, b=20),
        )
        st.plotly_chart(fig_psi, use_container_width=True)

    with col_details:
        st.subheader("🛡️ Disclosure & Secrecy Audit")
        st.markdown("""
        | Data Element | Status | Protection Mechanism |
        |---|---|---|
        | **Raw Account Numbers** | 🛡️ Secret | Local to each institution |
        | **Transaction Ledgers** | 🛡️ Secret | Kept strictly on-premise |
        | **Balances & Amounts** | 🛡️ Secret | Not shared during PSI |
        | **Non-Matching Candidates** | 🛡️ Secret | Discrete log hardness ($H(x)^{k_a}$) |
        | **Intersecting Entities** | 🔍 Revealed | Shared Canonical Pseudonym |
        """)

    st.markdown("---")

    # Section 2: Detailed Matched Canonical Entities Ledger
    st.subheader("🔗 Discovered Cross-Bank Entities (3-Way Intersection)")
    st.caption("These canonical entities represent coordinated mule operators maintaining high-risk accounts across all three institutions simultaneously.")

    three_way_list = psi.get("three_way_entities", [])
    if three_way_list:
        df_3way = pd.DataFrame(three_way_list)
        df_3way["canonical_token"] = df_3way["canonical_token"].apply(lambda t: t[:16] + "..." + t[-8:])
        st.dataframe(df_3way, hide_index=True, use_container_width=True)
    else:
        st.write("No 3-way intersecting accounts detected for the current threshold.")

    # Pairwise Expander
    with st.expander("🔎 View Pairwise Intersections (Bank A x Bank B, Bank B x Bank C, Bank A x Bank C)"):
        p_details = psi.get("pairwise_details", {})
        
        tab_ab, tab_bc, tab_ac = st.tabs(["Bank A ∩ Bank B", "Bank B ∩ Bank C", "Bank A ∩ Bank C"])
        with tab_ab:
            if p_details.get("A_B"):
                df_ab = pd.DataFrame(p_details["A_B"])
                df_ab["canonical_token"] = df_ab["canonical_token"].apply(lambda t: t[:16] + "..." + t[-8:])
                st.dataframe(df_ab, hide_index=True, use_container_width=True)
            else:
                st.write("None")
        with tab_bc:
            if p_details.get("B_C"):
                df_bc = pd.DataFrame(p_details["B_C"])
                df_bc["canonical_token"] = df_bc["canonical_token"].apply(lambda t: t[:16] + "..." + t[-8:])
                st.dataframe(df_bc, hide_index=True, use_container_width=True)
            else:
                st.write("None")
        with tab_ac:
            if p_details.get("A_C"):
                df_ac = pd.DataFrame(p_details["A_C"])
                df_ac["canonical_token"] = df_ac["canonical_token"].apply(lambda t: t[:16] + "..." + t[-8:])
                st.dataframe(df_ac, hide_index=True, use_container_width=True)
            else:
                st.write("None")
