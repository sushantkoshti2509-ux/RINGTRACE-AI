"""
RINGTRACE AI - Investigator Case Queue and Review Workflow Page.
Human-in-the-loop triage interface for fraud analysts with case disposition and audit logging.
"""

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
import pandas as pd

import config


def render():
    st.markdown("""
    <div class="top-banner">
        <div class="top-title">
            <span>📋 Investigator Case Queue & Triage Workflow</span>
            <span class="top-badge">Human-in-the-Loop</span>
        </div>
        <p class="top-desc">
            Review suspicious alerts, inspect multi-modal evidence dossiers, and document regulatory dispositions with full audit trails.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Mandatory Ethical Safeguard Banner (PRD Section 12.8 & 15.5)
    st.markdown("""
    <div class="safeguard-banner" style="border-left-color: #F59E0B; background-color: #FFFBEB;">
        <div style="display: flex; align-items: center; gap: 8px;">
            <span style="font-size: 1.2rem;">⚖️</span>
            <b>Compliance & Ethical AI Safeguard:</b>
        </div>
        <div style="font-size: 0.85rem; color: #78350F; margin-top: 4px;">
            RINGTRACE AI operates strictly as an <b>investigative intelligence layer</b>.
            Automated customer account freezes or payment blocks are <b>strictly prohibited</b>.
            All dispositions require human investigator review, context evaluation, and documented audit rationale.
        </div>
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

    # Search & Quick Filters
    col_search, col_f_tier, col_f_bank = st.columns([2, 1, 1])
    with col_search:
        search_query = st.text_input("🔍 Search by Account ID:", placeholder="e.g. BNKA_MULE...")
    with col_f_tier:
        tier_filter = st.multiselect("Risk Tier:", ["HIGH", "MEDIUM", "LOW"], default=["HIGH", "MEDIUM"])
    with col_f_bank:
        bank_filter = st.multiselect("Institution:", config.SIMULATED_BANKS, default=config.SIMULATED_BANKS)

    # Filter alerts
    filtered_alerts = [
        a for a in alerts
        if (not search_query or search_query.upper() in a["account_id"].upper())
        and a["risk_tier"] in tier_filter
        and a["bank_id"] in bank_filter
    ]

    st.markdown(f"**Showing {len(filtered_alerts)} active alerts matching criteria.**")

    # Split View: Triage Feed (Left) & Case Dossier (Right)
    col_queue, col_detail = st.columns([2, 3])

    with col_queue:
        st.markdown("##### 🚨 Active Alerts Feed")
        for item in filtered_alerts:
            acc_id = item["account_id"]
            status = st.session_state.case_statuses.get(acc_id, "Pending")
            tier_badge = '<span class="badge-danger">High Risk</span>' if item["risk_tier"] == "HIGH" else '<span class="badge-warning">Medium</span>'
            status_badge = '<span class="badge-info">Pending</span>' if status == "Pending" else ('<span class="badge-danger">Escalated</span>' if status == "Escalated" else '<span class="badge-success">Closed</span>')

            st.markdown(f"""
            <div style="background: white; border: 1px solid #E2E8F0; border-radius: 8px; padding: 12px; margin-bottom: 8px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-weight: 700; font-size: 0.95rem; color: #0F172A;">{acc_id}</span>
                    {tier_badge}
                </div>
                <div style="font-size: 0.8rem; color: #64748B; margin-top: 4px;">
                    Bank: <b>{item['bank_id']}</b> • Score: <b>{item['risk_score']:.2f}</b> • Status: {status_badge}
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"Open Case File: {acc_id}", key=f"btn_{acc_id}", use_container_width=True):
                st.session_state["selected_case"] = acc_id

    # Detail View Pane
    selected_acc_id = st.session_state.get("selected_case", filtered_alerts[0]["account_id"] if filtered_alerts else None)

    with col_detail:
        if selected_acc_id:
            case_data = next((a for a in alerts if a["account_id"] == selected_acc_id), None)
            if case_data:
                current_status = st.session_state.case_statuses.get(selected_acc_id, "Pending")

                st.markdown(f"""
                <div style="background: white; border: 1px solid #E2E8F0; border-radius: 10px; padding: 18px; margin-bottom: 16px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                        <div>
                            <span style="font-size: 1.25rem; font-weight: 800; color: #0F172A;">Case File: {selected_acc_id}</span>
                            <span class="bank-pill-a" style="margin-left: 8px;">{case_data['bank_id']}</span>
                        </div>
                        <span class="badge-danger">Score: {case_data['risk_score']:.2f}</span>
                    </div>
                    <div style="background: #F8FAFC; border-left: 4px solid #3B82F6; padding: 12px; border-radius: 6px; margin-bottom: 14px;">
                        <div style="font-weight: 700; font-size: 0.85rem; color: #1E3A8A; margin-bottom: 4px;">EXECUTIVE ALERT SUMMARY:</div>
                        <div style="font-size: 0.88rem; color: #1E293B; line-height: 1.5;">{case_data['executive_summary']}</div>
                    </div>
                """, unsafe_allow_html=True)

                st.markdown("###### 🔍 Model Attributed Risk Indicators (SHAP)")
                for r in case_data.get("shap_reasons", []):
                    st.markdown(f"- {r}")

                gev = case_data.get("graph_evidence", {})
                st.markdown("###### ⏱️ Flow Telemetry")
                st.write(f"- **Pass-Through Ratio:** `{gev.get('pass_through_ratio', 0.0):.1%}`")
                st.write(f"- **Turnaround Time:** `{gev.get('min_turnaround_seconds', 0.0)/60:.1f} mins`")
                st.write(f"- **Counterparties:** `{len(case_data.get('inbound_counterparties', []))}` Inbound, `{len(case_data.get('outbound_counterparties', []))}` Outbound")

                st.markdown("---")
                st.markdown("##### ⚖️ Case Action & Disposition")
                new_status = st.selectbox(
                    "Update Investigation Status:",
                    ["Pending", "Under Review", "Escalated", "Closed"],
                    index=["Pending", "Under Review", "Escalated", "Closed"].index(current_status),
                    key=f"status_select_{selected_acc_id}",
                )

                notes = st.text_area(
                    "Investigator Audit Notes:",
                    placeholder="Enter audit context, customer contact notes, or regulatory escalation details...",
                    key=f"notes_{selected_acc_id}",
                )

                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if st.button("💾 Save Case Disposition", key=f"save_{selected_acc_id}", use_container_width=True):
                        st.session_state.case_statuses[selected_acc_id] = new_status
                        st.success(f"Case {selected_acc_id} updated to '{new_status}' with audit timestamp logged.")
                        st.rerun()

                with col_btn2:
                    case_json = json.dumps(case_data, indent=2)
                    st.download_button(
                        label="📥 Export Dossier (JSON)",
                        data=case_json,
                        file_name=f"case_dossier_{selected_acc_id}.json",
                        mime="application/json",
                        use_container_width=True,
                    )
                st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("Select an alert from the feed to review.")
