"""
RINGTRACE AI - Account Deep-Dive and SHAP Explainability Page.
Visual risk meters, human-translated SHAP risk factor bars, and flow telemetry.
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
            <span>🔍 Account Deep-Dive & SHAP Explainability</span>
            <span class="top-badge">XGBoost + SHAP</span>
        </div>
        <p class="top-desc">
            Granular behavioral breakdown, risk score gauges, and transparent explainable AI feature attribution.
        </p>
    </div>
    """, unsafe_allow_html=True)

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

    # Selection controls with filter options
    col_filter, col_acc_sel = st.columns([1, 2])
    with col_filter:
        view_filter = st.selectbox(
            "Account Category:",
            ["🔴 Flagged Mule Accounts (High Risk)", "🟢 Legitimate Accounts (Merchants, Gig Workers, P2P)", "All Monitored Accounts"]
        )

    with col_acc_sel:
        if "Flagged Mule" in view_filter:
            target_ids = risk_df[risk_df["alert_flag"] == 1]["account_id"].tolist()
        elif "Legitimate" in view_filter:
            target_ids = risk_df[risk_df["alert_flag"] == 0]["account_id"].tolist()
        else:
            target_ids = risk_df["account_id"].tolist()

        def format_acc(acc_id):
            row = risk_df[risk_df["account_id"] == acc_id].iloc[0]
            tier_badge = "🔴 High Risk" if row["risk_tier"] == "HIGH" else ("🟡 Med" if row["risk_tier"] == "MEDIUM" else "🟢 Low")
            return f"{acc_id} • {tier_badge} (Score: {row['risk_score']:.2f}) • {row['bank_id']}"

        selected_account = st.selectbox("Select Account to Inspect:", target_ids, format_func=format_acc)

    acc_risk = risk_df[risk_df["account_id"] == selected_account].iloc[0]
    acc_feat = feat_df[feat_df["account_id"] == selected_account].iloc[0]
    evidence = alerts_lookup.get(selected_account, None)

    st.markdown("---")

    # Top Section: Gauge & Telemetry Summary
    col_gauge, col_telemetry = st.columns([2, 3])

    with col_gauge:
        score_val = float(acc_risk["risk_score"]) * 100
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=score_val,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "<b>Risk Severity Score</b>", 'font': {'size': 16, 'color': '#0F172A'}},
            number={'suffix': "%", 'font': {'size': 32, 'color': '#DC2626' if score_val >= 50 else '#059669'}},
            gauge={
                'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#94A3B8"},
                'bar': {'color': "#DC2626" if score_val >= 50 else "#10B981"},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "#E2E8F0",
                'steps': [
                    {'range': [0, 35], 'color': '#ECFDF5'},
                    {'range': [35, 70], 'color': '#FFFBEB'},
                    {'range': [70, 100], 'color': '#FEF2F2'},
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 75
                }
            }
        ))
        fig_gauge.update_layout(height=260, margin=dict(l=20, r=20, t=30, b=10))
        st.plotly_chart(fig_gauge, use_container_width=True)

    with col_telemetry:
        st.markdown(f"""
        <div style="background: white; border: 1px solid #E2E8F0; border-radius: 10px; padding: 16px; margin-top: 10px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                <span style="font-size: 1.15rem; font-weight: 800; color: #0F172A;">Account: {selected_account}</span>
                <span class="bank-pill-a">{acc_risk['bank_id']}</span>
            </div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
                <div style="background: #F8FAFC; padding: 10px; border-radius: 6px;">
                    <div style="font-size: 0.75rem; color: #64748B; font-weight: 600;">CUSTOMER PROFILE</div>
                    <div style="font-size: 0.95rem; font-weight: 700; color: #0F172A;">{acc_risk['profile_type'].replace('_', ' ')}</div>
                </div>
                <div style="background: #F8FAFC; padding: 10px; border-radius: 6px;">
                    <div style="font-size: 0.75rem; color: #64748B; font-weight: 600;">ACCOUNT MATURITY</div>
                    <div style="font-size: 0.95rem; font-weight: 700; color: #0F172A;">{int(acc_feat['account_age_days'])} Days Active</div>
                </div>
                <div style="background: #F8FAFC; padding: 10px; border-radius: 6px;">
                    <div style="font-size: 0.75rem; color: #64748B; font-weight: 600;">TOTAL INBOUND FLOW</div>
                    <div style="font-size: 0.95rem; font-weight: 700; color: #2563EB;">₹{acc_feat['total_amount_in']:,.2f}</div>
                </div>
                <div style="background: #F8FAFC; padding: 10px; border-radius: 6px;">
                    <div style="font-size: 0.75rem; color: #64748B; font-weight: 600;">TOTAL OUTBOUND FLOW</div>
                    <div style="font-size: 0.95rem; font-weight: 700; color: #DC2626;">₹{acc_feat['total_amount_out']:,.2f}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Section 2: Transparent Explainable AI (SHAP Factors)
    st.subheader("💡 Explainable AI: Key Factors Driving the Risk Score")
    st.caption("Human-translated SHAP model attributions showing why the AI flagged this account:")

    if evidence and evidence.get("shap_reasons"):
        col_reasons, col_evidence = st.columns([3, 2])
        with col_reasons:
            st.markdown("""
            <div style="background: #FFFBEB; border-left: 4px solid #F59E0B; padding: 12px 16px; border-radius: 6px; margin-bottom: 14px;">
                <b>Investigator Summary:</b><br>
            """ + evidence["executive_summary"] + "</div>", unsafe_allow_html=True)

            st.markdown("**Core Risk Indicators:**")
            for reason in evidence["shap_reasons"]:
                st.markdown(f"• **{reason}**")

        with col_evidence:
            gev = evidence.get("graph_evidence", {})
            st.markdown("""
            <div style="background: white; border: 1px solid #E2E8F0; border-radius: 8px; padding: 14px;">
                <div style="font-weight: 700; font-size: 0.88rem; color: #0F172A; margin-bottom: 8px;">VERIFIED GRAPH METRICS:</div>
            """, unsafe_allow_html=True)
            st.write(f"- **Pass-Through Ratio:** `{gev.get('pass_through_ratio', 0.0):.1%}`")
            st.write(f"- **Turnaround Delay:** `{gev.get('min_turnaround_seconds', 0.0)/60:.1f} mins`")
            st.write(f"- **Cross-Bank Transaction Ratio:** `{gev.get('cross_bank_ratio', 0.0):.1%}`")
            st.write(f"- **Distinct Inbound Senders:** `{gev.get('in_degree', 0)}`")
            st.write(f"- **Distinct Outbound Receivers:** `{gev.get('out_degree', 0)}`")
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.success("✅ This account does not exhibit anomalous pass-through or velocity patterns. All transactions align with normal customer behavior.")

    st.markdown("---")

    # Section 3: Inbound & Outbound Counterparty Records
    st.subheader("💳 Counterparty Transaction Ledger")
    inbound = tx_df[tx_df["receiver_account"] == selected_account].sort_values("timestamp", ascending=False)
    outbound = tx_df[tx_df["sender_account"] == selected_account].sort_values("timestamp", ascending=False)

    tab_in, tab_out = st.tabs([f"Inbound Deposits ({len(inbound)})", f"Outbound Transfers ({len(outbound)})"])
    with tab_in:
        if not inbound.empty:
            st.dataframe(
                inbound[["timestamp", "transaction_id", "sender_account", "sender_bank", "amount", "transaction_type", "is_suspicious"]],
                hide_index=True,
                use_container_width=True,
            )
        else:
            st.info("No inbound transactions recorded.")

    with tab_out:
        if not outbound.empty:
            st.dataframe(
                outbound[["timestamp", "transaction_id", "receiver_account", "receiver_bank", "amount", "transaction_type", "is_suspicious"]],
                hide_index=True,
                use_container_width=True,
            )
        else:
            st.info("No outbound transactions recorded.")
