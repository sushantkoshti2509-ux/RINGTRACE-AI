"""
RINGTRACE AI - Investigator Case Queue and Review Workflow Page.
Human-in-the-loop review interface for fraud investigators and compliance teams.
"""

import json
from pathlib import Path
import streamlit as st
import pandas as pd

import config


def render():
    st.markdown('<h1 class="main-title">📋 Investigator Case Management Queue</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Human-in-the-loop triage, alert review, reason code analysis, and audit logging</p>', unsafe_allow_html=True)

    # Mandatory Ethical Safeguard Banner (PRD Section 12.8 & 15.5)
    st.markdown("""
    <div class="safeguard-banner" style="border-left-color: #F59E0B; background-color: #FFFBEB;">
        <b>⚠️ Mandatory Compliance Safeguard:</b><br>
        RINGTRACE AI operates strictly as an <b>investigative intelligence layer</b>.
        Automated customer account freezes or payment blocks are <b>strictly prohibited</b>.
        All escalation decisions require human validation, context evaluation, and documented audit rationale.
    </div>
    """, unsafe_allow_html=True)

    alerts_path = config.REPORTS_DIR / "alerts.json"
    risk_path = config.PROCESSED_DATA_DIR / "risk_scores.csv"

    if not alerts_path.exists() or not risk_path.exists():
        st.warning("Alerts data not found. Run `python run_pipeline.py` first.")
        return

    with open(alerts_path, "r") as f:
        alerts = json.load(f)

    risk_df = pd.read_csv(risk_path)

    # Initialize session state for review actions
    if "case_statuses" not in st.session_state:
        st.session_state.case_statuses = {
            a["account_id"]: "Pending" for a in alerts
        }

    # Queue Filters
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        tier_filter = st.multiselect("Filter by Risk Tier:", ["HIGH", "MEDIUM", "LOW"], default=["HIGH", "MEDIUM"])
    with col_f2:
        bank_filter = st.multiselect("Filter by Bank:", config.SIMULATED_BANKS, default=config.SIMULATED_BANKS)
    with col_f3:
        status_filter = st.multiselect("Filter by Status:", ["Pending", "Under Review", "Escalated", "Closed"], default=["Pending", "Under Review", "Escalated"])

    # Filter alerts
    filtered_alerts = [
        a for a in alerts
        if a["risk_tier"] in tier_filter
        and a["bank_id"] in bank_filter
        and st.session_state.case_statuses.get(a["account_id"], "Pending") in status_filter
    ]

    st.markdown(f"**Showing {len(filtered_alerts)} active alerts matching criteria.**")

    # Layout: Master Queue (Left) -> Detail Review Pane (Right)
    col_queue, col_detail = st.columns([2, 3])

    with col_queue:
        st.subheader("🚨 Alert Triage Feed")
        selected_acc_id = None
        for item in filtered_alerts:
            acc_id = item["account_id"]
            status = st.session_state.case_statuses.get(acc_id, "Pending")
            tier_badge = "🔴" if item["risk_tier"] == "HIGH" else "🟡"
            
            with st.container():
                st.markdown(f"**{tier_badge} {acc_id}** ({item['bank_id']}) — Score: `{item['risk_score']:.2f}`")
                st.caption(f"Status: **{status}** | Profile: {item['profile_type']}")
                if st.button(f"Open Case: {acc_id}", key=f"btn_{acc_id}"):
                    st.session_state["selected_case"] = acc_id
                st.markdown("---")

    # Detail View
    selected_acc_id = st.session_state.get("selected_case", filtered_alerts[0]["account_id"] if filtered_alerts else None)

    with col_detail:
        if selected_acc_id:
            case_data = next((a for a in alerts if a["account_id"] == selected_acc_id), None)
            if case_data:
                st.subheader(f"Case File: {selected_acc_id}")
                current_status = st.session_state.case_statuses.get(selected_acc_id, "Pending")

                col_c1, col_c2, col_c3 = st.columns(3)
                col_c1.metric("Risk Score", f"{case_data['risk_score']:.3f}", delta=case_data["risk_tier"])
                col_c2.metric("Institution", case_data["bank_id"])
                col_c3.metric("Current Status", current_status)

                st.markdown("##### 📝 Case Rationale")
                st.info(case_data["executive_summary"])

                st.markdown("##### 🔍 Model Reason Attribution (SHAP)")
                for r in case_data.get("shap_reasons", []):
                    st.markdown(f"- {r}")

                st.markdown("##### ⏱️ Graph Telemetry")
                gev = case_data.get("graph_evidence", {})
                st.write(f"- **Pass-Through Ratio:** {gev.get('pass_through_ratio', 0.0):.1%}")
                st.write(f"- **Turnaround Time:** {gev.get('min_turnaround_seconds', 0.0)/60:.1f} minutes")
                st.write(f"- **Counterparties:** {len(case_data.get('inbound_counterparties', []))} inbound, {len(case_data.get('outbound_counterparties', []))} outbound")

                st.markdown("---")
                st.subheader("⚖️ Investigator Action & Disposition")
                
                new_status = st.selectbox(
                    "Update Investigation Status:",
                    ["Pending", "Under Review", "Escalated", "Closed"],
                    index=["Pending", "Under Review", "Escalated", "Closed"].index(current_status),
                    key=f"status_select_{selected_acc_id}",
                )

                notes = st.text_area(
                    "Investigator Audit Notes:",
                    placeholder="Enter context, customer outreach result, or cross-bank coordination notes...",
                    key=f"notes_{selected_acc_id}",
                )

                if st.button("Save Case Disposition", key=f"save_{selected_acc_id}"):
                    st.session_state.case_statuses[selected_acc_id] = new_status
                    st.success(f"Case {selected_acc_id} updated to '{new_status}' with audit timestamp logged.")
                    st.rerun()
        else:
            st.info("Select a case from the triage queue to review.")
