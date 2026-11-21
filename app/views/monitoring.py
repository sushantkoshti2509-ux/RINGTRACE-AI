"""
RINGTRACE AI - Step 9: Centralized Multi-Bank Monitoring Dashboard.
Common interface for authorized bank officials and administrators to monitor
transaction activities, analyze fraud patterns, track alerts, and inspect
suspicious banking records across Bank A, Bank B, and Bank C.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timezone
import json

from src.dashboard.service import DashboardMonitoringService
from src.alerts.engine import AlertEngine


@st.cache_resource
def get_dashboard_service():
    return DashboardMonitoringService()


@st.cache_resource
def get_alert_engine():
    return AlertEngine()


def render():
    service = get_dashboard_service()
    alert_engine = get_alert_engine()

    # Mode Selector in Header
    c_head1, c_head2 = st.columns([3, 1])
    with c_head1:
        st.markdown("""
        <div class="top-banner" style="margin-bottom: 16px;">
            <div class="top-title">
                <span>🛡️ Multi-Bank Fraud Monitoring Dashboard</span>
                <span class="top-badge">Step 9 Centralized Command</span>
            </div>
            <p class="top-desc">
                Unified cross-bank transaction surveillance, risk analytics, and fraud alert tracking across Bank A, Bank B, and Bank C.
            </p>
        </div>
        """, unsafe_allow_html=True)
    with c_head2:
        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
        view_mode = st.radio(
            "SURVEILLANCE MODE",
            ["Federated Scale (25,430)", "Canonical Database (13,975)"],
            index=0,
            horizontal=False,
        )

    mode_key = "federated" if "Federated" in view_mode else "reconciled"
    summary = service.get_executive_summary(mode=mode_key)

    # -------------------------------------------------------------------------
    # 1. Primary Top KPI Cards (Matching User Layout Specifications)
    # -------------------------------------------------------------------------
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f"""
        <div class="ring-card" style="border-top: 4px solid #3B82F6;">
            <div class="card-title">TOTAL TRANSACTIONS</div>
            <div class="card-val" style="color: #0F172A;">{summary['total_transactions']:,}</div>
            <div class="card-sub" style="color: #64748B;">Bank A + Bank B + Bank C</div>
        </div>
        """, unsafe_allow_html=True)
    with m2:
        st.markdown(f"""
        <div class="ring-card" style="border-top: 4px solid #EF4444;">
            <div class="card-title">SUSPICIOUS TRANSACTIONS</div>
            <div class="card-val" style="color: #DC2626;">{summary['suspicious_transactions']:,}</div>
            <div class="card-sub" style="color: #DC2626; font-weight: 600;">Flagged for AML / Mule Review</div>
        </div>
        """, unsafe_allow_html=True)
    with m3:
        st.markdown(f"""
        <div class="ring-card" style="border-top: 4px solid #10B981;">
            <div class="card-title">LEGITIMATE TRANSACTIONS</div>
            <div class="card-val" style="color: #16A34A;">{summary['legitimate_transactions']:,}</div>
            <div class="card-sub" style="color: #16A34A; font-weight: 600;">Frictionless Normal P2P / Merchant</div>
        </div>
        """, unsafe_allow_html=True)
    with m4:
        st.markdown(f"""
        <div class="ring-card" style="border-top: 4px solid #F59E0B;">
            <div class="card-title">PENDING ALERTS</div>
            <div class="card-val" style="color: #D97706;">{summary['pending_alerts']}</div>
            <div class="card-sub" style="color: #D97706; font-weight: 600;">Awaiting Compliance Triage</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # 2. Bank-Wise Transaction Monitoring Table (Exact Requested Format)
    # -------------------------------------------------------------------------
    st.markdown("#### 🏦 Bank-Wise Transaction Monitoring")
    bank_df = pd.DataFrame(summary["bank_wise_monitoring"])

    # Format for display table matching user layout
    display_df = pd.DataFrame({
        "Bank": bank_df["bank_name"],
        "Transactions": bank_df["transactions"].apply(lambda x: f"{x:,}"),
        "Suspicious": bank_df["suspicious"].apply(lambda x: f"{x:,}"),
        "Fraud Rate": bank_df["fraud_rate"].apply(lambda x: f"{x:.2f}%"),
        "Monitored Volume": bank_df["volume_inr"].apply(lambda x: f"₹{x/10000000:.2f} Cr" if x >= 10000000 else f"₹{x:,.0f}"),
    })

    st.dataframe(display_df, use_container_width=True, hide_index=True)
    st.caption(f"_{summary['disclaimer']}_")

    st.markdown("<br>", unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # 3. Interactive Graphical Reports and Analytical Charts
    # -------------------------------------------------------------------------
    st.markdown("#### 📈 Cross-Bank Analytical Visualizations")
    c_chart1, c_chart2 = st.columns(2)

    with c_chart1:
        # Bank-wise comparison bar chart
        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(
            name="Legitimate Transactions",
            x=bank_df["bank_name"],
            y=bank_df["transactions"] - bank_df["suspicious"],
            marker_color="#3B82F6",
        ))
        fig_bar.add_trace(go.Bar(
            name="Suspicious Transactions",
            x=bank_df["bank_name"],
            y=bank_df["suspicious"],
            marker_color="#EF4444",
        ))
        fig_bar.update_layout(
            title="<b>Transaction Volume & Suspicious Activity by Bank</b>",
            barmode="stack",
            xaxis_title="Participating Institution",
            yaxis_title="Transaction Count",
            template="plotly_white",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            height=320,
            margin=dict(l=20, r=20, t=50, b=20),
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with c_chart2:
        # Risk Tier Distribution Donut Chart
        risk_dist = summary["risk_distribution"]
        labels = ["Low Risk (Normal)", "Medium Risk (Review)", "High Risk (Suspicious)"]
        values = [risk_dist["low_risk"], risk_dist["medium_risk"], risk_dist["high_risk"]]
        colors = ["#10B981", "#F59E0B", "#EF4444"]

        fig_donut = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=0.55,
            marker_colors=colors,
            textinfo="label+percent",
            insidetextorientation="radial",
        )])
        fig_donut.update_layout(
            title="<b>Multi-Bank Risk Tier Distribution</b>",
            template="plotly_white",
            showlegend=False,
            height=320,
            margin=dict(l=20, r=20, t=50, b=20),
        )
        st.plotly_chart(fig_donut, use_container_width=True)

    # -------------------------------------------------------------------------
    # 4. Interactive Transaction Search, Filter, and Investigation Table
    # -------------------------------------------------------------------------
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### 🔍 Interactive Transaction Search & Live Investigation")

    with st.expander("🛠️ Filter & Search Controls", expanded=True):
        f_col1, f_col2, f_col3, f_col4 = st.columns(4)
        with f_col1:
            filt_bank = st.selectbox("Filter Bank", ["All Banks", "Bank A", "Bank B", "Bank C"], index=0)
        with f_col2:
            filt_risk = st.selectbox("Risk Level Tier", ["All Tiers", "High", "Low"], index=0)
        with f_col3:
            filt_amount_min = st.number_input("Min Amount (₹)", min_value=0.0, value=0.0, step=1000.0)
        with f_col4:
            filt_search = st.text_input("Search ID / Account", placeholder="e.g. TX_0000005, ACC_001")

    # Fetch filtered transactions from database
    tx_results = service.query_transactions(
        bank_id=filt_bank,
        risk_level=filt_risk,
        min_amount=filt_amount_min if filt_amount_min > 0 else None,
        search_query=filt_search if filt_search else None,
        limit=30,
    )

    if tx_results:
        df_tx = pd.DataFrame(tx_results)
        display_tx_cols = ["transaction_id", "sender_bank", "receiver_bank", "amount", "timestamp", "risk_level", "status", "pattern_type"]

        st.markdown(f"Displaying **{len(df_tx)}** filtered transactions:")

        # Style risk column
        def style_tx_risk(val):
            if val == "High":
                return "background-color: #FEE2E2; color: #991B1B; font-weight: bold;"
            elif val == "Medium":
                return "background-color: #FEF3C7; color: #92400E; font-weight: bold;"
            else:
                return "background-color: #DCFCE7; color: #166534; font-weight: bold;"

        st.dataframe(
            df_tx[display_tx_cols].style.map(style_tx_risk, subset=["risk_level"]),
            use_container_width=True,
            hide_index=True,
        )

        # Single Transaction Deep-Dive Inspector
        st.markdown("##### 🕵️ Transaction Inspector & Rapid Action")
        tx_options = {f"{t['transaction_id']} ({t['sender_bank']} -> {t['receiver_bank']}, ₹{t['amount']:,.0f}, {t['risk_level']} Risk)": t['transaction_id'] for t in tx_results}
        selected_tx_key = st.selectbox("Select Transaction to Inspect", list(tx_options.keys()))
        selected_tx_id = tx_options[selected_tx_key]

        selected_tx = next(t for t in tx_results if t["transaction_id"] == selected_tx_id)

        col_ins1, col_ins2 = st.columns([2, 1])
        with col_ins1:
            st.json({
                "transaction_id": selected_tx["transaction_id"],
                "customer_id": selected_tx["customer_id"],
                "sender_account": selected_tx["sender_account"],
                "receiver_account": selected_tx["receiver_account"],
                "route": f"{selected_tx['sender_bank']} ➔ {selected_tx['receiver_bank']}",
                "amount_inr": f"₹{selected_tx['amount']:,.2f}",
                "timestamp": selected_tx["timestamp"],
                "pattern_type": selected_tx["pattern_type"],
                "is_cross_bank": selected_tx["is_cross_bank"],
            })
        with col_ins2:
            st.markdown(f"""
            <div style="background: white; border: 2px solid {'#DC2626' if selected_tx['risk_level'] == 'High' else '#16A34A'}; border-radius: 10px; padding: 16px; text-align: center;">
                <div style="font-size: 0.8rem; color: #64748B;">RISK EVALUATION</div>
                <div style="font-size: 1.5rem; font-weight: 800; color: {'#DC2626' if selected_tx['risk_level'] == 'High' else '#16A34A'}; margin: 6px 0;">{selected_tx['risk_level'].upper()} RISK</div>
                <div style="font-size: 0.85rem; color: #475569;">Status: <b>{selected_tx['status']}</b></div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
            if selected_tx["risk_level"] == "High":
                if st.button("🚨 Escalate to Alert Center", type="primary", use_container_width=True):
                    alert_res = alert_engine.generate_alert({
                        "transaction_id": selected_tx["transaction_id"],
                        "bank_id": selected_tx["sender_bank"],
                        "sender_account": selected_tx["sender_account"],
                        "receiver_account": selected_tx["receiver_account"],
                        "amount": selected_tx["amount"],
                        "fraud_probability": 0.95,
                        "risk_level": "High",
                        "trigger_reasons": ["MANUAL_INSPECTOR_ESCALATION", "CROSS_BANK_MULE_SUSPICION"],
                        "recommendation": "Flagged manually by compliance supervisor from Step 9 Centralized Dashboard.",
                    })
                    st.success(f"✅ Alert **{alert_res.get('alert_id')}** created in Step 8 Alert System!")
    else:
        st.info("No transactions found matching the filter criteria.")

    # -------------------------------------------------------------------------
    # 5. Alert Status Tracking Strip (Pending, Under Review, Resolved)
    # -------------------------------------------------------------------------
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### 🚨 Centralized Alert Status Surveillance")
    alert_stats = alert_engine.get_stats()

    a1, a2, a3, a4 = st.columns(4)
    with a1:
        st.metric("Pending Triage", alert_stats.get("pending", 0))
    with a2:
        st.metric("Under Review", alert_stats.get("under_review", 0))
    with a3:
        st.metric("Escalated Cases", alert_stats.get("escalated", 0))
    with a4:
        st.metric("Resolved Cases", alert_stats.get("resolved", 0))
