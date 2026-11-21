#!/usr/bin/env python3
"""
RINGTRACE AI - Step 8: Fraud Alert & Notification System CLI Runner.
Demonstrates:
1. Automatic alert generation from suspicious transactions.
2. Risk level categorization (High, Medium, Low).
3. Duplicate alert prevention (idempotent tracking).
4. Multi-channel email & webhook notification dispatching for Bank A, Bank B, and Bank C.
5. Investigation status tracking (Pending -> Under Review -> Escalated -> Resolved).
"""

import sys
import argparse
from datetime import datetime, timezone
import json

from src.alerts.engine import AlertEngine
from src.alerts.notifier import AlertNotifier
from src.integration.db import DatabaseManager


def print_banner():
    print("=" * 80)
    print("🚨 RINGTRACE AI - STEP 8: FRAUD ALERT & NOTIFICATION SYSTEM")
    print("• Scope: Automated Inter-Bank Fraud Alerts & Notification Dispatch")
    print("• Multi-Bank Federation: Bank A, Bank B, and Bank C")
    print("• Safeguard: Automated transaction blocking disabled (Human-in-the-loop triage)")
    print("=" * 80)


def print_alert_card(alert: dict):
    """Prints alert card in the user's exact requested illustrative format."""
    amount_str = f"₹{alert['amount']:,.0f}" if isinstance(alert['amount'], (int, float)) else str(alert['amount'])
    prob_str = f"{int(round(alert['fraud_probability'] * 100))}%"

    print("\n" + "─" * 45)
    print("Fraud Detection Alert")
    print(f"{alert['risk_level']} Risk")
    print("\nTransaction ID")
    print(f"**{alert['transaction_id']}**")
    print("\nBank")
    print(f"**{alert['bank_id']}**")
    print("\nTransaction Amount")
    print(f"**{amount_str}**")
    print("\nFraud Probability")
    print(f"**{prob_str}**")
    print(f"\n{alert.get('recommendation', 'Suspicious transaction detected. Further investigation is recommended.')}")
    print(f"\n{alert.get('disclaimer', 'Illustrative example, not actual transaction data.')}")
    print("─" * 45)


def run_demo():
    print_banner()
    db = DatabaseManager()
    notifier = AlertNotifier()
    engine = AlertEngine(db_manager=db, notifier=notifier)

    # -------------------------------------------------------------------------
    # 1. Generate Illustrative Alert (Matching User Example)
    # -------------------------------------------------------------------------
    print("\n[1/5] Generating Primary High-Risk Fraud Alert (User Illustrative Example)...")
    sample_txn = {
        "transaction_id": "TXN10245",
        "bank_id": "Bank B",
        "sender_account": "BANK_ACC_00102",
        "receiver_account": "BANK_ACC_00551",
        "amount": 85000.0,
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d 02:45:10"),
        "fraud_probability": 0.96,
        "risk_level": "High",
        "trigger_reasons": ["RAPID_BURST_FORWARDING", "CROSS_BANK_HIGH_VALUE", "NOCTURNAL_OFF_HOURS"],
        "recommendation": "Suspicious transaction detected. Further investigation is recommended.",
    }

    alert_1 = engine.generate_alert(sample_txn)
    print_alert_card(alert_1)
    print(f"  ✓ Alert ID Assigned:    {alert_1['alert_id']}")
    print(f"  ✓ Initial Status:       {alert_1['status']}")
    print(f"  ✓ Channels Notified:    {', '.join(alert_1.get('notified_channels', []))}")

    # -------------------------------------------------------------------------
    # 2. Duplicate Alert Prevention Test
    # -------------------------------------------------------------------------
    print("\n[2/5] Testing Duplicate Alert Prevention...")
    print(f"  • Attempting to re-submit transaction '{sample_txn['transaction_id']}'...")
    dup_result = engine.generate_alert(sample_txn)

    if dup_result.get("is_duplicate"):
        print(f"  🛡️ DUPLICATE PREVENTED: {dup_result['message']}")
        print(f"  ✓ Retained Existing Alert ID: {dup_result['alert_id']} (No duplicate created, no spam notifications sent)")
    else:
        print("  ❌ Duplicate prevention failed!")

    # -------------------------------------------------------------------------
    # 3. Multi-Bank & Multi-Risk Categorization Demo
    # -------------------------------------------------------------------------
    print("\n[3/5] Ingesting Multi-Bank Transaction Alerts (Bank A, B, C)...")
    multi_samples = [
        {
            "transaction_id": "TXN10246",
            "bank_id": "Bank A",
            "sender_account": "BANK_ACC_00280",
            "receiver_account": "BANK_ACC_00330",
            "amount": 42000.0,
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d 11:15:22"),
            "fraud_probability": 0.58,
            "risk_level": "Medium",
            "trigger_reasons": ["HIGH_VELOCITY_SPIKE"],
            "recommendation": "Unusual transaction pattern observed. Compliance review required.",
        },
        {
            "transaction_id": "TXN10247",
            "bank_id": "Bank C",
            "sender_account": "BANK_ACC_00889",
            "receiver_account": "BANK_ACC_00912",
            "amount": 92000.0,
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d 03:02:44"),
            "fraud_probability": 0.94,
            "risk_level": "High",
            "trigger_reasons": ["RAPID_BURST_FORWARDING", "HIGH_PASS_THROUGH_MULE_RATIO"],
            "recommendation": "Suspicious transaction detected. Further investigation is recommended.",
        },
    ]

    for s in multi_samples:
        res = engine.generate_alert(s)
        print(f"  • [{res['bank_id']}] {res['alert_id']} (TX: {res['transaction_id']}) -> {res['risk_level']} Risk ({int(res['fraud_probability']*100)}% prob) | Status: {res['status']}")

    # -------------------------------------------------------------------------
    # 4. Status Progression & Investigation Workflow
    # -------------------------------------------------------------------------
    print("\n[4/5] Executing Alert Lifecycle Transitions...")
    target_alert_id = alert_1["alert_id"]

    # Step A: Assign & mark Under Review
    print(f"  • Step A: Compliance Officer opens case for {target_alert_id}...")
    res_review = engine.update_alert_status(
        alert_id=target_alert_id,
        new_status="Under Review",
        notes="Reviewing nocturnal cross-bank pattern with Bank B fraud analyst.",
        updated_by="Officer_BankB_01",
    )
    print(f"    ✓ Status changed to: '{res_review['status']}' by {res_review['assigned_to']}")

    # Step B: Escalate for Mule Ring Inspection
    print(f"  • Step B: Cross-referencing mule ring topology -> Escalating...")
    res_escalated = engine.update_alert_status(
        alert_id=target_alert_id,
        new_status="Escalated",
        notes="Confirmed 120s rapid pass-through linking Bank B to Bank C. Escalated to Inter-Bank Taskforce.",
        updated_by="Supervisor_AML",
    )
    print(f"    ✓ Status changed to: '{res_escalated['status']}'")
    print(f"    ✓ Investigation Notes Logged: {len(res_escalated['investigation_notes'])} entries")

    # -------------------------------------------------------------------------
    # 5. Summary Statistics & Centralized Alert History
    # -------------------------------------------------------------------------
    print("\n[5/5] Centralized Multi-Bank Alert Statistics:")
    stats = engine.get_stats()
    print("=" * 60)
    print(f"  • Total Alerts Logged:       {stats['total_alerts']}")
    print(f"  • High Risk (Suspicious):    {stats['high_risk']}")
    print(f"  • Medium Risk (Review Req):  {stats['medium_risk']}")
    print(f"  • Low Risk (Normal):         {stats['low_risk']}")
    print(f"  • Pending Triage:            {stats['pending']}")
    print(f"  • Under Review:              {stats['under_review']}")
    print(f"  • Escalated Cases:           {stats['escalated']}")
    print(f"  • Resolved Cases:            {stats['resolved']}")
    print(f"  • Distribution by Bank:      Bank A: {stats['by_bank']['BANK_A']} | Bank B: {stats['by_bank']['BANK_B']} | Bank C: {stats['by_bank']['BANK_C']}")
    print("=" * 60)
    print("\n✅ Step 8 Demonstration Completed Successfully.\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="RINGTRACE AI Alert System CLI")
    parser.add_argument("--demo", action="store_true", default=True, help="Run end-to-end alert workflow demo")
    args = parser.parse_args()
    run_demo()
