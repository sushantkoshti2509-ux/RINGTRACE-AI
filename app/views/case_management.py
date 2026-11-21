"""
Feature 3: Fraud Investigation Assistant Dashboard View.
Interactive case management interface for banking compliance officers:
- Investigation case overview & AI summary
- Interactive evidence inspection
- Step-by-step investigation checklist
- Employee notes & disposition feedback (Confirmed vs Cleared)
- Official PDF Investigation Dossier export
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timezone
import json

from src.investigation_assistant.case_manager import CaseManager
from src.investigation_assistant.report_generator import InvestigationReportGenerator


@st.cache_resource
def get_case_components():
    manager = CaseManager()
    manager.sync_cases_from_detected_rings()
    report_gen = InvestigationReportGenerator()
    return manager, report_gen


def render():
    st.markdown("""
    <div class="top-banner">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 12px;">
            <div>
                <div class="top-title">
                    <span>🕵️ Fraud Investigation Assistant</span>
                    <span class="top-badge">Feature 3: Intelligent Case Management</span>
                </div>
                <p class="top-desc">
                    Assists banking compliance teams in reviewing evidence, tracking investigation steps, documenting decisions, and exporting regulatory dossiers.
                </p>
            </div>
            <div style="text-align: right;">
                <span class="badge-success">● Human-in-the-Loop Triage</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Mandatory Ethical Safeguard Banner
    st.warning("⚠️ **Compliance & Ethical Safeguard:** Automated account freezing or transaction blocking is strictly disabled. All enforcement decisions require human investigator review and recorded justification.")

    case_mgr, report_gen = get_case_components()

    # Load Cases
    all_cases = case_mgr.list_cases(limit=50)
    if not all_cases:
        st.info("No active investigation cases. Synchronizing from detected rings...")
        all_cases = case_mgr.sync_cases_from_detected_rings()

    if not all_cases:
        st.warning("No candidate mule rings discovered yet. Please run the detection pipeline.")
        return

    # Top Case Statistics Row
    stats = case_mgr.get_stats()
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.metric("Total Cases", stats.get("total_cases", 0))
    with c2:
        st.metric("Pending Triage", stats.get("pending", 0))
    with c3:
        st.metric("Under Review", stats.get("under_review", 0))
    with c4:
        st.metric("Escalated", stats.get("escalated", 0))
    with c5:
        st.metric("Resolved / Closed", stats.get("resolved", 0) + stats.get("closed", 0))

    st.markdown("<br>", unsafe_allow_html=True)

    # Case Selector
    case_options = {
        f"{c['case_id']} • {c['title']} ({c['connected_accounts_count']} accs, Risk: {c['risk_score']:.0f}/100, Status: {c['status']})": c['case_id']
        for c in all_cases
    }
    sel_label = st.selectbox("Select Investigation Case to Review:", list(case_options.keys()))
    active_case_id = case_options[sel_label]
    active_case = case_mgr.get_case(active_case_id)

    if not active_case:
        st.error("Case not found.")
        return

    # -------------------------------------------------------------
    # Case Header Card (Matching User Example Screen)
    # -------------------------------------------------------------
    status_color = "#D97706" if active_case["status"] == "Pending" else ("#0284C7" if active_case["status"] == "Under Review" else ("#DC2626" if active_case["status"] == "Escalated" else "#16A34A"))
    status_bg = "#FEF3C7" if active_case["status"] == "Pending" else ("#E0F2FE" if active_case["status"] == "Under Review" else ("#FEE2E2" if active_case["status"] == "Escalated" else "#DCFCE7"))

    st.markdown(f"""
    <div style="background: white; border: 2px solid #E2E8F0; border-radius: 12px; padding: 22px; box-shadow: 0 4px 14px rgba(0,0,0,0.06); margin-bottom: 24px;">
        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #E2E8F0; padding-bottom: 12px; margin-bottom: 16px;">
            <div>
                <h3 style="margin: 0; font-size: 1.45rem; font-weight: 800; color: #0F172A;">
                    Investigation Case #{active_case['case_id'].replace('CASE-', '')}
                </h3>
                <span style="font-size: 0.85rem; color: #64748B;">{active_case['title']}</span>
            </div>
            <div style="display: flex; gap: 8px;">
                <span style="background: #FEE2E2; color: #991B1B; font-weight: 700; padding: 4px 12px; border-radius: 6px; font-size: 0.82rem;">
                    {active_case['risk_tier']} RISK
                </span>
                <span style="background: {status_bg}; color: {status_color}; font-weight: 700; padding: 4px 12px; border-radius: 6px; font-size: 0.82rem;">
                    Status: {active_case['status']}
                </span>
            </div>
        </div>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 14px; margin-bottom: 18px;">
            <div>
                <div style="font-size: 0.78rem; color: #64748B; font-weight: 600; text-transform: uppercase;">Connected accounts</div>
                <div style="font-size: 1.4rem; font-weight: 800; color: #0F172A; margin-top: 2px;">{active_case['connected_accounts_count']}</div>
            </div>
            <div>
                <div style="font-size: 0.78rem; color: #64748B; font-weight: 600; text-transform: uppercase;">Banks involved</div>
                <div style="font-size: 1.4rem; font-weight: 800; color: #2563EB; margin-top: 2px;">{len(active_case['banks_involved'])}</div>
                <div style="font-size: 0.72rem; color: #64748B;">{', '.join(active_case['banks_involved'])}</div>
            </div>
            <div>
                <div style="font-size: 0.78rem; color: #64748B; font-weight: 600; text-transform: uppercase;">Transactions</div>
                <div style="font-size: 1.4rem; font-weight: 800; color: #0F172A; margin-top: 2px;">{active_case['transactions_count']}</div>
            </div>
            <div>
                <div style="font-size: 0.78rem; color: #64748B; font-weight: 600; text-transform: uppercase;">Total Volume</div>
                <div style="font-size: 1.4rem; font-weight: 800; color: #0F172A; margin-top: 2px;">₹{active_case['total_volume']:,.0f}</div>
            </div>
            <div>
                <div style="font-size: 0.78rem; color: #64748B; font-weight: 600; text-transform: uppercase;">Risk score</div>
                <div style="font-size: 1.4rem; font-weight: 800; color: #DC2626; margin-top: 2px;">{active_case['risk_score']:.0f}/100</div>
            </div>
        </div>
        <div style="background: #F8FAFC; border-left: 4px solid #2563EB; border-radius: 4px; padding: 14px 16px;">
            <div style="font-size: 0.85rem; font-weight: 700; color: #1E40AF; margin-bottom: 4px;">AI-GENERATED CASE SUMMARY</div>
            <div style="font-size: 0.94rem; color: #1E293B; line-height: 1.6;">
                {active_case['ai_summary']}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # -------------------------------------------------------------
    # Investigation Workspace: Evidence, Checklist, Notes & Report
    # -------------------------------------------------------------
    tab_chk, tab_ev, tab_disp, tab_pdf = st.tabs([
        "✅ Investigation Checklist",
        "📑 Case Evidence & Member Accounts",
        "⚖️ Compliance Disposition & Notes",
        "📄 Export Official PDF Report",
    ])

    # TAB 1: Checklist
    with tab_chk:
        st.markdown("##### 📋 Step-by-Step Compliance Checklist")
        st.caption("Guide compliance officers systematically through multi-bank verification procedures.")

        chk_state = active_case.get("checklist_state", {})
        cols = st.columns(2)
        for idx, item in enumerate(CaseManager.DEFAULT_CHECKLIST):
            c_target = cols[idx % 2]
            with c_target:
                curr_val = chk_state.get(item["id"], False)
                new_val = st.checkbox(
                    f"**Step {idx+1}:** {item['task']}",
                    value=curr_val,
                    key=f"chk_{active_case_id}_{item['id']}",
                )
                if new_val != curr_val:
                    case_mgr.update_checklist(active_case_id, item["id"], new_val)
                    st.rerun()

    # TAB 2: Evidence Viewer
    with tab_ev:
        st.markdown("##### 👥 Connected Suspect Accounts in Network")
        members = active_case.get("member_accounts", [])
        if members:
            df_m = pd.DataFrame([
                {"Account ID": m, "Assigned Role": "Mule Connector" if idx == 0 else "Layering Node", "Bank Routing": "Cross-Bank Intermediary"}
                for idx, m in enumerate(members)
            ])
            st.dataframe(df_m, use_container_width=True, hide_index=True)

        st.markdown("##### 🚩 Detected Laundering Patterns")
        for pat in active_case.get("detected_patterns", []):
            st.markdown(f"• **`{pat}`**: Coordinated funds movement meeting algorithmic threshold criteria.")

    # TAB 3: Disposition & Notes
    with tab_disp:
        st.markdown("##### ⚖️ Case Status & Regulatory Disposition")
        c_u1, c_u2 = st.columns([1, 2])
        with c_u1:
            new_st = st.selectbox("Set Case Status", ["Pending", "Under Review", "Escalated", "Resolved", "Closed"], index=1)
            officer = st.text_input("Investigator Identity", value="Compliance_Analyst_01")
        with c_u2:
            note_text = st.text_area("Investigation Note / Regulatory Audit Finding", placeholder="E.g. Cross-referenced transaction timestamps with Bank B. Coordinated layering confirmed.")
            if st.button("💾 Save Status & Append Note", type="primary"):
                if note_text.strip():
                    case_mgr.update_status(active_case_id, new_st, notes=note_text, updated_by=officer)
                    st.success("Case status and notes successfully committed.")
                    st.rerun()
                else:
                    st.error("Please enter a note describing the rationale for the status update.")

        st.markdown("---")
        st.markdown("##### 📝 Formal Regulatory Decision Feedback (Confirmed vs. Cleared)")
        f_col1, f_col2 = st.columns([1, 2])
        with f_col1:
            disp_decision = st.radio("Final Case Finding:", ["Confirmed Fraud (SAR Required)", "Cleared (Legitimate / False Positive)"])
        with f_col2:
            disp_reason = st.text_area("Decision Justification:", placeholder="E.g., All counterparties validated as legitimate commercial clearing partners; cleared.")
            if st.button("⚖️ Commit Final Regulatory Disposition", type="secondary"):
                if disp_reason.strip():
                    dec_key = "CONFIRMED_FRAUD" if "Confirmed" in disp_decision else "CLEARED_FALSE_POSITIVE"
                    case_mgr.record_feedback(active_case_id, dec_key, disp_reason, reviewed_by=officer)
                    st.success(f"Disposition recorded as {dec_key}!")
                    st.rerun()
                else:
                    st.error("Justification reason is required for audit trails.")

        # Display Notes History
        case_notes = active_case.get("case_notes", [])
        if case_notes:
            st.markdown("##### 📜 Case Audit Log Trail")
            for n in reversed(case_notes):
                st.markdown(f"""
                <div style="background: #F1F5F9; border-radius: 6px; padding: 8px 12px; margin-bottom: 6px; font-size: 0.88rem;">
                    <b>{n.get('author')}</b> set status to <b>{n.get('status_change')}</b> at <i>{n.get('timestamp')}</i>:<br>
                    {n.get('note')}
                </div>
                """, unsafe_allow_html=True)

    # TAB 4: PDF Export
    with tab_pdf:
        st.markdown("##### 📄 Generate & Download Official Investigation Report (PDF)")
        st.caption("Produces an audit-ready regulatory document containing the AI summary, member account topology, checklist progress, and compliance sign-off blocks.")

        pdf_bytes = report_gen.generate_case_pdf(active_case)

        st.download_button(
            label=f"📥 Download Investigation Report ({active_case_id}.pdf)",
            data=pdf_bytes,
            file_name=f"RINGTRACE_Investigation_{active_case_id}.pdf",
            mime="application/pdf",
            use_container_width=True,
            type="primary",
        )
