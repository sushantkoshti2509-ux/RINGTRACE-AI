"""
RINGTRACE AI - Account Deep-Dive and SHAP Explainability Page.
Inspect individual account telemetry, SHAP risk drivers, and transaction counterparties.
"""

import json
from pathlib import Path
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

import config


def render():
    st.markdown('<h1 class="main-title">🔍 Account Deep-Dive & SHAP Explainability</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Detailed audit trail, machine learning feature attribution, and graph counterparty evidence</p>', unsafe_allow_html=True)

    risk_path = config.PROCESSED_DATA_DIR / "risk_scores.csv"
    feat_path = config.PROCESSED_DATA_DIR / "features.csv"
    alerts_path = config.REPORTS_DIR / "alerts.json"
    tx_path = config.PROCESSED_DATA_DIR / "transactions.csv"

    if not risk_path.exists() or not feat_path.exists():
        st.warning("Please run `python run_pipeline.py` first.")
        return

    risk_df = pd.read_csv(risk_path)
    feat_df = pd.read_csv(feat_path)
    tx_df = pd.read_csv(tx_path)

    alerts_data = []
    if alerts_path.exists():
        with open(alerts_path, "r") as f:
            alerts_data = json.load(f)
    alerts_lookup = {a["account_id"]: a for a in alerts_data}

    # Selection controls
    col_s1, col_s2 = st.columns([3, 1])
    with col_s1:
        # Prioritize flagged accounts at top of selector
        flagged_list = risk_df[risk_df["alert_flag"] == 1]["account_id"].tolist()
        all_list = risk_df["account_id"].tolist()
        # Combine with flagged first
        ordered_accounts = flagged_list + [a for a in all_list if a not in set(flagged_list)]

        def format_acc(acc_id):
            row = risk_df[risk_df["account_id"] == acc_id].iloc[0]
            tier_emoji = "🔴" if row["risk_tier"] == "HIGH" else ("🟡" if row["risk_tier"] == "MEDIUM" else "🟢")
            return f"{tier_emoji} {acc_id} | Score: {row['risk_score']:.3f} | {row['bank_id']} | {row['profile_type']}"

        selected_account = st.selectbox(
            "Select Account to Inspect:",
            ordered_accounts,
            format_func=format_acc,
        )

    # Fetch Account Info
    acc_risk = risk_df[risk_df["account_id"] == selected_account].iloc[0]
    acc_feat = feat_df[feat_df["account_id"] == selected_account].iloc[0]
    evidence = alerts_lookup.get(selected_account, None)

    # Risk Score Gauge and Overview Banner
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    col_m1.metric("Risk Score", f"{acc_risk['risk_score']:.3f}", delta=acc_risk["risk_tier"])
    col_m2.metric("Simulated Bank", acc_risk["bank_id"])
    col_m3.metric("Customer Profile", acc_risk["profile_type"])
    col_m4.metric("Account Age", f"{int(acc_feat['account_age_days'])} days")

    st.markdown("---")

    # Plain Language Multi-Modal Reason Codes
    if evidence:
        st.subheader("💡 Multi-Modal Investigation Reason Codes")
        st.info(f"**Executive Alert Summary:**\n\n{evidence['executive_summary']}")

        col_r1, col_r2 = st.columns(2)
        with col_r1:
            st.markdown("**🤖 Model Attribution Reasons (SHAP):**")
            for r in evidence.get("shap_reasons", []):
                st.markdown(f"- {r}")

        with col_r2:
            st.markdown("**📐 Deterministic Graph & Temporal Telemetry:**")
            gev = evidence.get("graph_evidence", {})
            st.write(f"- **Pass-Through Ratio:** {gev.get('pass_through_ratio', 0.0):.1%}")
            st.write(f"- **Turnaround Velocity:** {gev.get('min_turnaround_seconds', 0.0)/60:.1f} mins to forward funds")
            st.write(f"- **Total Inbound:** ₹{gev.get('total_in', 0.0):,.2f} ({gev.get('in_degree', 0)} transfers)")
            st.write(f"- **Total Outbound:** ₹{gev.get('total_out', 0.0):,.2f} ({gev.get('out_degree', 0)} transfers)")
            st.write(f"- **Cross-Bank Transaction Ratio:** {gev.get('cross_bank_ratio', 0.0):.1%}")

    st.markdown("---")

    # Transaction Counterparty Ledger
    st.subheader("💳 Transaction Counterparty Ledgers")
    inbound_tx = tx_df[tx_df["receiver_account"] == selected_account].sort_values("timestamp")
    outbound_tx = tx_df[tx_df["sender_account"] == selected_account].sort_values("timestamp")

    tab1, tab2 = st.tabs([f"Inbound Transfers ({len(inbound_tx)})", f"Outbound Transfers ({len(outbound_tx)})"])
    
    with tab1:
        if not inbound_tx.empty:
            st.dataframe(
                inbound_tx[["timestamp", "transaction_id", "sender_account", "sender_bank", "amount", "transaction_type", "is_suspicious"]],
                hide_index=True,
                use_container_width=True,
            )
        else:
            st.write("No inbound transactions recorded.")

    with tab2:
        if not outbound_tx.empty:
            st.dataframe(
                outbound_tx[["timestamp", "transaction_id", "receiver_account", "receiver_bank", "amount", "transaction_type", "is_suspicious"]],
                hide_index=True,
                use_container_width=True,
            )
        else:
            st.write("No outbound transactions recorded.")
