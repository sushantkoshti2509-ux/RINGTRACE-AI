"""
RINGTRACE AI - Private Set Intersection (PSI) Privacy Demonstration Page.
Interactive visual cryptographic pipeline, disclosure guarantees, and multi-bank matches.
"""

import json
from pathlib import Path
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

import config


def render():
    st.markdown("""
    <div class="top-banner">
        <div class="top-title">
            <span>🔐 Cryptographic Private Set Intersection (PSI)</span>
            <span class="top-badge">RFC 3526 Commutative DH</span>
        </div>
        <p class="top-desc">
            How Bank A, Bank B, and Bank C uncover common mule syndicates across institutions without disclosing raw transaction records or customer data.
        </p>
    </div>
    """, unsafe_allow_html=True)

    psi_path = config.REPORTS_DIR / "psi_results.json"
    if not psi_path.exists():
        st.warning("PSI results not found. Please execute `python run_pipeline.py`.")
        return

    with open(psi_path, "r") as f:
        psi = json.load(f)

    # 3-Step Interactive Privacy Pipeline Explanation
    st.subheader("💡 How Private Set Intersection (PSI) Protects Customer Privacy")
    st.caption("How banks discover shared criminals without ever seeing each other's innocent customer databases:")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""
        <div class="concept-box" style="border-top: 3px solid #3B82F6;">
            <div class="concept-title">1️⃣ Salted Tokenization</div>
            <p class="concept-text">
                Each bank identifies internal suspect accounts and converts their canonical tax ID (PAN) into a salted cryptographic token: <code>HMAC-SHA256(PAN)</code>. Raw IDs are never transmitted.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown("""
        <div class="concept-box" style="border-top: 3px solid #8B5CF6;">
            <div class="concept-title">2️⃣ Commutative Exponentiation</div>
            <p class="concept-text">
                Bank A and Bank B exchange blinded mathematical elements: <code>(H(x)^ka)^kb mod p</code>. Because multiplication is commutative (<code>ka*kb == kb*ka</code>), matching items yield identical values.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown("""
        <div class="concept-box" style="border-top: 3px solid #10B981;">
            <div class="concept-title">3️⃣ Zero-Knowledge Match</div>
            <p class="concept-text">
                Only the exact overlapping tokens match. Neither bank learns anything about the candidate suspects that did <b>not</b> match, preserving 100% data secrecy.
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Metrics Overview Row
    c_m1, c_m2, c_m3, c_m4 = st.columns(4)
    c_m1.metric("Bank A Suspect Inputs", f"{psi['bank_a_candidates']}")
    c_m2.metric("Bank B Suspect Inputs", f"{psi['bank_b_candidates']}")
    c_m3.metric("Bank C Suspect Inputs", f"{psi['bank_c_candidates']}")
    c_m4.metric("3-Way Common Syndicates", f"{psi['three_way_intersection_count']}", delta="High-Confidence")

    st.markdown("<br>", unsafe_allow_html=True)

    # Visual Intersection Bar & Data Protection Matrix
    col_chart, col_matrix = st.columns([3, 2])

    with col_chart:
        pairs = psi["pairwise_matches"]
        cats = ["Bank A ∩ Bank B", "Bank B ∩ Bank C", "Bank A ∩ Bank C", "3-Way Common (A ∩ B ∩ C)"]
        vals = [
            pairs["BANK_A_x_BANK_B"],
            pairs["BANK_B_x_BANK_C"],
            pairs["BANK_A_x_BANK_C"],
            psi["three_way_intersection_count"],
        ]

        fig_bar = go.Figure(go.Bar(
            x=cats,
            y=vals,
            text=vals,
            textposition="auto",
            marker_color=["#3B82F6", "#10B981", "#F59E0B", "#DC2626"],
        ))
        fig_bar.update_layout(
            title="<b>Matched Cross-Bank Syndicate Entities</b>",
            yaxis=dict(title="Entity Count"),
            height=300,
            margin=dict(l=10, r=10, t=30, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_matrix:
        st.markdown("""
        <div style="background: white; border: 1px solid #E2E8F0; border-radius: 8px; padding: 14px;">
            <div style="font-size: 0.88rem; font-weight: 700; color: #0F172A; margin-bottom: 8px;">
                🛡️ DATA PRIVACY AUDIT GUARANTEE
            </div>
            <div style="font-size: 0.8rem; line-height: 1.6; color: #334155;">
                • <b>Account Numbers:</b> <span class="badge-success">100% Hidden</span><br>
                • <b>Transaction Ledgers:</b> <span class="badge-success">Never Shared</span><br>
                • <b>Account Balances:</b> <span class="badge-success">Never Shared</span><br>
                • <b>Non-Matching Customers:</b> <span class="badge-success">Math-Locked (DLP)</span><br>
                • <b>Overlapping Tokens:</b> <span class="badge-info">Revealed for Action</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Discovered 3-Way Syndicate Cards
    st.subheader("🎯 Discovered Multi-Bank Mule Syndicates (Operating Across All 3 Banks)")
    st.caption("These entities were caught maintaining coordinated suspect accounts simultaneously at Bank A, Bank B, and Bank C:")

    three_way_list = psi.get("three_way_entities", [])
    if three_way_list:
        for idx, entity in enumerate(three_way_list):
            tok_short = entity["canonical_token"][:12] + "..." + entity["canonical_token"][-6:]
            st.markdown(f"""
            <div style="background: white; border: 1px solid #E2E8F0; border-radius: 10px; padding: 16px; margin-bottom: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.04);">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                    <div>
                        <span style="font-weight: 800; font-size: 1.05rem; color: #DC2626;">🚨 Cross-Bank Syndicate #{idx+1}</span>
                        <span style="font-size: 0.78rem; color: #64748B; font-family: monospace; margin-left: 10px;">Token: {tok_short}</span>
                    </div>
                    <span class="badge-danger">Active in Bank A, B & C</span>
                </div>
                <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 12px;">
                    <div style="background: #EFF6FF; border: 1px solid #BFDBFE; border-radius: 6px; padding: 10px;">
                        <span class="bank-pill-a">Bank A Account</span>
                        <div style="font-size: 0.95rem; font-weight: 700; color: #1E40AF; margin-top: 6px;">{entity['BANK_A_account']}</div>
                    </div>
                    <div style="background: #ECFDF5; border: 1px solid #A7F3D0; border-radius: 6px; padding: 10px;">
                        <span class="bank-pill-b">Bank B Account</span>
                        <div style="font-size: 0.95rem; font-weight: 700; color: #065F46; margin-top: 6px;">{entity['BANK_B_account']}</div>
                    </div>
                    <div style="background: #FFFBEB; border: 1px solid #FDE68A; border-radius: 6px; padding: 10px;">
                        <span class="bank-pill-c">Bank C Account</span>
                        <div style="font-size: 0.95rem; font-weight: 700; color: #92400E; margin-top: 6px;">{entity['BANK_C_account']}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No 3-way syndicate accounts detected for this threshold.")
