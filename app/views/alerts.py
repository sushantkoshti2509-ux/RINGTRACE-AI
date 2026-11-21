"""
RINGTRACE AI - Step 8: Centralized Fraud Alert & Notification Center.
Features:
- Real-time alert feed across Bank A, Bank B, and Bank C
- Card rendering matching exact user-specified illustrative format
- Investigation workflow transitions (Pending, Under Review, Escalated, Resolved)
- Real-time alert triggering sandbox with duplicate prevention
- Multi-channel notification inspection (simulated email / webhooks)
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timezone
import json

from src.alerts.engine import AlertEngine
from src.alerts.notifier import AlertNotifier
from src.integration.db import DatabaseManager


@st.cache_resource
def get_alert_engine():
    """Initializes and caches the AlertEngine with database manager."""
    db = DatabaseManager()
    notifier = AlertNotifier()
    return AlertEngine(db_manager=db, notifier=notifier)


def render_alert_card(alert: dict):
    """Renders a single alert card matching the user's exact required format."""
    risk = alert.get("risk_level", "High")
    prob_pct = f"{int(round(float(alert.get('fraud_probability', 0.0)) * 100))}%"
    amount = float(alert.get("amount", 0.0))
    amount_str = f"₹{amount:,.0f}" if amount >= 1.0 else f"₹{amount}"

    border_color = "#DC2626" if risk == "High" else ("#D97706" if risk == "Medium" else "#16A34A")
    badge_bg = "#FEE2E2" if risk == "High" else ("#FEF3C7" if risk == "Medium" else "#DCFCE7")
    badge_text = "#991B1B" if risk == "High" else ("#92400E" if risk == "Medium" else "#166534")

    status_val = alert.get("status", "Pending")
    status_bg = "#E0F2FE" if status_val == "Under Review" else ("#FEE2E2" if status_val == "Escalated" else ("#DCFCE7" if status_val == "Resolved" else "#FEF3C7"))
    status_color = "#0369A1" if status_val == "Under Review" else ("#991B1B" if status_val == "Escalated" else ("#166534" if status_val == "Resolved" else "#92400E"))

    st.markdown(f"""
    <div style="background: white; border: 2px solid {border_color}; border-radius: 12px; padding: 20px; margin-bottom: 20px; box-shadow: 0 4px 14px rgba(0, 0, 0, 0.06);">
        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #E2E8F0; padding-bottom: 12px; margin-bottom: 14px;">
            <div style="font-size: 1.25rem; font-weight: 800; color: #0F172A; display: flex; align-items: center; gap: 8px;">
                <span>🚨 Fraud Detection Alert</span>
            </div>
            <div style="display: flex; gap: 8px;">
                <span style="background: {badge_bg}; color: {badge_text}; font-size: 0.8rem; font-weight: 700; padding: 4px 10px; border-radius: 6px;">
                    {risk} Risk
                </span>
                <span style="background: {status_bg}; color: {status_color}; font-size: 0.8rem; font-weight: 700; padding: 4px 10px; border-radius: 6px;">
                    {status_val}
                </span>
            </div>
        </div>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 14px; margin-bottom: 16px;">
            <div>
                <div style="font-size: 0.78rem; color: #64748B; font-weight: 600; text-transform: uppercase;">Transaction ID</div>
                <div style="font-size: 1.15rem; font-weight: 800; color: #0F172A; margin-top: 2px;">{alert.get('transaction_id')}</div>
            </div>
            <div>
                <div style="font-size: 0.78rem; color: #64748B; font-weight: 600; text-transform: uppercase;">Bank</div>
                <div style="font-size: 1.15rem; font-weight: 800; color: #1E40AF; margin-top: 2px;">{alert.get('bank_id')}</div>
            </div>
            <div>
                <div style="font-size: 0.78rem; color: #64748B; font-weight: 600; text-transform: uppercase;">Transaction Amount</div>
                <div style="font-size: 1.15rem; font-weight: 800; color: #0F172A; margin-top: 2px;">{amount_str}</div>
            </div>
            <div>
                <div style="font-size: 0.78rem; color: #64748B; font-weight: 600; text-transform: uppercase;">Fraud Probability</div>
                <div style="font-size: 1.15rem; font-weight: 800; color: {border_color}; margin-top: 2px;">{prob_pct}</div>
            </div>
        </div>
        <div style="background: #F8FAFC; border-left: 4px solid {border_color}; padding: 12px 14px; border-radius: 4px; font-size: 0.92rem; color: #334155; margin-bottom: 10px;">
            <b>Recommendation:</b> {alert.get('recommendation', 'Suspicious transaction detected. Further investigation is recommended.')}
        </div>
        <div style="display: flex; justify-content: space-between; align-items: center; font-size: 0.78rem; color: #94A3B8; margin-top: 10px;">
            <span><i>{alert.get('disclaimer', 'Illustrative example, not actual transaction data.')}</i></span>
            <span>Alert ID: <b>{alert.get('alert_id')}</b> | Time: {alert.get('timestamp')}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render():
    st.markdown("""
    <div class="top-banner">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 12px;">
            <div>
                <div class="top-title">
                    <span>🚨 Multi-Bank Fraud Alert & Notification System</span>
                    <span class="top-badge">Step 8 Active</span>
                </div>
                <p class="top-desc">
                    Centralized alert generation, risk categorization, duplicate prevention, and multi-channel compliance dispatching for Bank A, Bank B, and Bank C.
                </p>
            </div>
            <div style="text-align: right;">
                <span style="display: inline-block; padding: 4px 10px; background: rgba(59, 130, 246, 0.15); border: 1px solid #3B82F6; border-radius: 6px; color: #93C5FD; font-size: 0.8rem; font-weight: 700;">
                    INTER-BANK FEDERATION ACTIVE
                </span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Safeguard Notice
    st.warning("⚠️ **Prototype Safeguard:** Automated transaction blocking is deliberately disabled in this prototype. All suspicious activities are routed to human investigators for compliance review.")

    engine = get_alert_engine()

    # Pre-seed sample alerts if table is empty
    existing_alerts = engine.query_alerts(limit=5)
    if not existing_alerts:
        # Seed illustrative default alerts
        engine.generate_alert({
            "transaction_id": "TXN10245",
            "bank_id": "Bank B",
            "sender_account": "BANK_ACC_00102",
            "receiver_account": "BANK_ACC_00551",
            "amount": 85000.0,
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d 02:45:10"),
            "fraud_probability": 0.96,
            "risk_level": "High",
            "status": "Pending",
            "trigger_reasons": ["RAPID_BURST_FORWARDING", "CROSS_BANK_HIGH_VALUE", "NOCTURNAL_OFF_HOURS"],
            "recommendation": "Suspicious transaction detected. Further investigation is recommended.",
        })
        engine.generate_alert({
            "transaction_id": "TXN10246",
            "bank_id": "Bank A",
            "sender_account": "BANK_ACC_00280",
            "receiver_account": "BANK_ACC_00330",
            "amount": 42000.0,
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d 11:15:22"),
            "fraud_probability": 0.58,
            "risk_level": "Medium",
            "status": "Under Review",
            "trigger_reasons": ["HIGH_VELOCITY_SPIKE"],
            "recommendation": "Unusual transaction pattern observed. Compliance review required.",
        })
        engine.generate_alert({
            "transaction_id": "TXN10247",
            "bank_id": "Bank C",
            "sender_account": "BANK_ACC_00889",
            "receiver_account": "BANK_ACC_00912",
            "amount": 92000.0,
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d 03:02:44"),
            "fraud_probability": 0.94,
            "risk_level": "High",
            "status": "Pending",
            "trigger_reasons": ["RAPID_BURST_FORWARDING", "HIGH_PASS_THROUGH_MULE_RATIO"],
            "recommendation": "Suspicious transaction detected. Further investigation is recommended.",
        })

    # Summary KPI Stats Row
    stats = engine.get_stats()
    k1, k2, k3, k4, k5 = st.columns(5)
    with k1:
        st.metric("Total Alerts", stats.get("total_alerts", 0))
    with k2:
        st.metric("🚨 High Risk", stats.get("high_risk", 0))
    with k3:
        st.metric("⚠️ Medium Risk", stats.get("medium_risk", 0))
    with k4:
        st.metric("⏳ Pending Action", stats.get("pending", 0))
    with k5:
        st.metric("🔍 Under Review / Esc", stats.get("under_review", 0) + stats.get("escalated", 0))

    st.markdown("<br>", unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs([
        "📋 Centralized Alert Feed",
        "⚡ Trigger Alert Sandbox (Live Demo)",
        "🔍 Investigator Case Action",
        "📧 Dispatched Notification Logs",
    ])

    # -------------------------------------------------------------
    # TAB 1: Centralized Alert Feed
    # -------------------------------------------------------------
    with tab1:
        st.markdown("##### 🔎 Filter Alerts Across Participating Banks")
        f1, f2, f3 = st.columns(3)
        with f1:
            sel_bank = st.selectbox("Select Institution", ["All Banks", "Bank A", "Bank B", "Bank C"], index=0)
        with f2:
            sel_risk = st.selectbox("Risk Categorization", ["All Risk Tiers", "High", "Medium", "Low"], index=0)
        with f3:
            sel_status = st.selectbox("Workflow Status", ["All Statuses", "Pending", "Under Review", "Escalated", "Resolved"], index=0)

        # Normalize query arguments
        query_bank = None if sel_bank == "All Banks" else sel_bank.replace(" ", "_").upper()
        query_risk = None if sel_risk == "All Risk Tiers" else sel_risk
        query_status = None if sel_status == "All Statuses" else sel_status

        alerts = engine.query_alerts(
            bank_id=query_bank,
            risk_level=query_risk,
            status=query_status,
            limit=50,
        )

        st.markdown(f"Showing **{len(alerts)}** matching alert records:")
        if alerts:
            for alt in alerts:
                render_alert_card(alt)
        else:
            st.info("No alert records match the selected filters.")

    # -------------------------------------------------------------
    # TAB 2: Trigger Alert Sandbox (Live Demo & Duplicate Prevention)
    # -------------------------------------------------------------
    with tab2:
        st.markdown("""
        <div class="concept-box">
            <div class="concept-title">⚡ Real-Time Alert Ingestion & Duplicate Prevention Sandbox</div>
            <div class="concept-text">
                Simulate a suspicious transaction from Bank A, Bank B, or Bank C to immediately watch it appear in the alert center.
                If you submit the same Transaction ID again, the system's <b>idempotent deduplication engine</b> prevents duplicate alerts and avoids spamming compliance desks.
            </div>
        </div>
        """, unsafe_allow_html=True)

        with st.form("trigger_alert_form"):
            s1, s2 = st.columns(2)
            with s1:
                in_tx_id = st.text_input("Transaction ID", value="TXN10245")
                in_bank = st.selectbox("Originating Bank", ["Bank B", "Bank A", "Bank C"], index=0)
                in_amount = st.number_input("Transaction Amount (INR)", min_value=100.0, max_value=1000000.0, value=85000.0, step=5000.0)
                in_prob = st.slider("Fraud Probability Score", min_value=0.0, max_value=1.0, value=0.96, step=0.01)

            with s2:
                in_sender = st.text_input("Sender Account", value="BANK_ACC_00102")
                in_receiver = st.text_input("Receiver Account", value="BANK_ACC_00551")
                in_reasons = st.multiselect(
                    "Detected Trigger Reasons",
                    ["RAPID_BURST_FORWARDING", "CROSS_BANK_HIGH_VALUE", "NOCTURNAL_OFF_HOURS", "HIGH_PASS_THROUGH_MULE_RATIO", "HIGH_VELOCITY_SPIKE"],
                    default=["RAPID_BURST_FORWARDING", "CROSS_BANK_HIGH_VALUE", "NOCTURNAL_OFF_HOURS"],
                )
                in_submit = st.form_submit_button("🚨 Generate & Dispatch Alert", type="primary", use_container_width=True)

        if in_submit:
            tx_payload = {
                "transaction_id": in_tx_id,
                "bank_id": in_bank,
                "sender_account": in_sender,
                "receiver_account": in_receiver,
                "amount": in_amount,
                "fraud_probability": in_prob,
                "trigger_reasons": in_reasons,
                "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
            }

            result = engine.generate_alert(tx_payload)

            if result.get("is_duplicate"):
                st.warning(f"🛡️ **DUPLICATE PREVENTED:** {result.get('message')}")
                st.info(f"Existing Alert ID **{result.get('alert_id')}** was retained. No new duplicate alert created, and no redundant notifications dispatched.")
            else:
                st.success(f"✅ **ALERT CREATED & DISPATCHED:** New alert **{result.get('alert_id')}** generated for {in_bank}!")
                st.markdown(f"**Notified Channels:** `{', '.join(result.get('notified_channels', []))}`")

            st.markdown("##### Generated Alert Preview:")
            render_alert_card(result)

    # -------------------------------------------------------------
    # TAB 3: Investigator Case Action & State Transitions
    # -------------------------------------------------------------
    with tab3:
        st.markdown("##### 🔍 Investigation Action Drawer")
        all_alerts_for_action = engine.query_alerts(limit=50)

        if all_alerts_for_action:
            alert_options = {f"{a['alert_id']} - {a['bank_id']} (TX: {a['transaction_id']}, {a['risk_level']} Risk, Status: {a['status']})": a['alert_id'] for a in all_alerts_for_action}
            selected_label = st.selectbox("Select Alert to Investigate", list(alert_options.keys()))
            selected_alert_id = alert_options[selected_label]
            active_alert = engine.get_alert(selected_alert_id)

            if active_alert:
                render_alert_card(active_alert)

                st.markdown("---")
                st.markdown("##### 📝 Update Investigation Status")
                u1, u2 = st.columns([1, 2])
                with u1:
                    new_status = st.selectbox("Transition Status To", ["Under Review", "Escalated", "Resolved", "Pending"], index=0)
                    officer_id = st.text_input("Investigator Identity", value="Compliance_Officer_01")
                with u2:
                    case_notes = st.text_area("Investigation Notes / Evidence Summary", placeholder="E.g., Verified rapid pass-through linking Bank B to Bank C mule node. Contacted branch compliance.")
                    update_btn = st.button("💾 Commit Status Transition & Save Notes", type="primary")

                if update_btn:
                    if not case_notes.strip():
                        st.error("Please provide investigation notes explaining the status update.")
                    else:
                        updated = engine.update_alert_status(
                            alert_id=selected_alert_id,
                            new_status=new_status,
                            notes=case_notes,
                            updated_by=officer_id,
                        )
                        st.success(f"✅ Alert **{selected_alert_id}** status successfully changed to **{new_status}**!")
                        st.rerun()

                # Display existing case notes audit trail
                notes_history = active_alert.get("investigation_notes", [])
                if notes_history:
                    st.markdown("##### 📜 Case Investigation Audit Trail")
                    for n in reversed(notes_history):
                        st.markdown(f"""
                        <div style="background: #F1F5F9; border-radius: 6px; padding: 10px 14px; margin-bottom: 8px; font-size: 0.88rem;">
                            <b>{n.get('author')}</b> set status to <span style="font-weight: 700; color: #1E40AF;">{n.get('status_change')}</span> at <i>{n.get('timestamp')}</i>:<br>
                            <span style="color: #334155;">{n.get('note')}</span>
                        </div>
                        """, unsafe_allow_html=True)
        else:
            st.info("No active alerts to investigate.")

    # -------------------------------------------------------------
    # TAB 4: Dispatched Notification Logs
    # -------------------------------------------------------------
    with tab4:
        st.markdown("##### 📧 Inter-Bank Notification Dispatch Log")
        dispatches = engine.notifier.get_dispatch_history(limit=25)

        if dispatches:
            for d in reversed(dispatches):
                if d.get("channel") == "EMAIL":
                    st.markdown(f"""
                    <div style="background: white; border: 1px solid #CBD5E1; border-radius: 8px; padding: 16px; margin-bottom: 14px;">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                            <span style="background: #EEF2FF; color: #4338CA; font-weight: 700; font-size: 0.8rem; padding: 2px 8px; border-radius: 4px;">SMTP EMAIL ALERT</span>
                            <span style="font-size: 0.78rem; color: #64748B;">{d.get('dispatched_at')}</span>
                        </div>
                        <div style="font-size: 0.88rem; color: #1E293B; margin-bottom: 4px;"><b>To:</b> {d.get('recipient')}</div>
                        <div style="font-size: 0.88rem; color: #1E293B; margin-bottom: 8px;"><b>Subject:</b> {d.get('subject')}</div>
                        <pre style="background: #F8FAFC; border: 1px solid #E2E8F0; padding: 10px; border-radius: 6px; font-size: 0.82rem; color: #334155; white-space: pre-wrap;">{d.get('body')}</pre>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 10px 14px; margin-bottom: 10px; font-size: 0.85rem;">
                        <b>Channel:</b> {d.get('channel')} | <b>Alert:</b> {d.get('alert_id')} | <b>Time:</b> {d.get('timestamp')}
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("No notification dispatches recorded yet.")
