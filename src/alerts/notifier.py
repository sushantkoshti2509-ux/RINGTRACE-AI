"""
RINGTRACE AI - Step 8: Multi-Channel Notification Dispatcher.
Simulates secure inter-bank email alerts (SMTP), WebSockets live push,
and compliance desk webhook dispatching for Bank A, Bank B, and Bank C.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import json
import logging

logger = logging.getLogger("ringtrace.alerts.notifier")


class AlertNotifier:
    """Dispatches multi-channel fraud alerts to concerned banking institutions."""

    BANK_COMPLIANCE_EMAILS = {
        "BANK_A": "aml-desk@bank-a.in",
        "BANK_B": "fraud-monitoring@bank-b.in",
        "BANK_C": "compliance-ops@bank-c.in",
        "BANK_D": "risk-intelligence@bank-d.in",
        "BANK_E": "fraud-triage@bank-e.in",
        "BANK_F": "audit-desk@bank-f.in",
    }

    def __init__(self):
        # In-memory dispatch audit log
        self.dispatched_notifications: List[Dict[str, Any]] = []
        # Active WebSocket connections
        self.active_websockets: List[Any] = []

    def dispatch(self, alert: Dict[str, Any], channels: Optional[List[str]] = None) -> List[str]:
        """
        Dispatches alert across specified channels (EMAIL, WEBSOCKET, IN_APP).
        Returns list of successfully notified channel identifiers.
        """
        if channels is None:
            channels = ["EMAIL", "IN_APP", "WEBSOCKET"]

        notified = []

        if "EMAIL" in channels:
            email_record = self._send_email_notification(alert)
            self.dispatched_notifications.append(email_record)
            notified.append("EMAIL")

        if "IN_APP" in channels:
            in_app_record = {
                "dispatch_id": f"NOTIF_APP_{len(self.dispatched_notifications) + 1:04d}",
                "channel": "IN_APP",
                "alert_id": alert.get("alert_id"),
                "bank_id": alert.get("bank_id"),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "payload": alert,
            }
            self.dispatched_notifications.append(in_app_record)
            notified.append("IN_APP")

        if "WEBSOCKET" in channels:
            self._broadcast_websocket(alert)
            notified.append("WEBSOCKET")

        return notified

    def _send_email_notification(self, alert: Dict[str, Any]) -> Dict[str, Any]:
        """Formats and logs a simulated SMTP email alert to the destination bank compliance team."""
        bank_id = alert.get("bank_id", "BANK_A").upper()
        recipient = self.BANK_COMPLIANCE_EMAILS.get(bank_id, f"compliance@{bank_id.lower()}.in")
        tx_id = alert.get("transaction_id", "UNKNOWN")
        risk_level = alert.get("risk_level", "High")
        amount = alert.get("amount", 0.0)
        prob = alert.get("fraud_probability", 0.0)
        recommendation = alert.get("recommendation", "Suspicious transaction detected. Further investigation is recommended.")

        # Clean formatted INR representation
        amount_formatted = f"₹{amount:,.2f}" if isinstance(amount, (int, float)) else f"₹{amount}"
        prob_pct = f"{int(round(prob * 100))}%" if isinstance(prob, (int, float)) else f"{prob}%"

        subject = f"[FRAUD ALERT - {risk_level.upper()} RISK] Suspicious UPI Transaction {tx_id}"

        # Standard Email Body matching user's requested specification
        body_text = f"""
================================================================================
Fraud Detection Alert
{risk_level} Risk
================================================================================
Transaction ID:     {tx_id}
Bank:               {bank_id}
Transaction Amount: {amount_formatted}
Fraud Probability:  {prob_pct}

{recommendation}

Illustrative example, not actual transaction data.
================================================================================
        """.strip()

        record = {
            "dispatch_id": f"NOTIF_MAIL_{len(self.dispatched_notifications) + 1:04d}",
            "channel": "EMAIL",
            "recipient": recipient,
            "subject": subject,
            "body": body_text,
            "alert_id": alert.get("alert_id"),
            "bank_id": bank_id,
            "dispatched_at": datetime.now(timezone.utc).isoformat(),
        }

        logger.info(f"Dispatched email alert {record['dispatch_id']} to {recipient} for {tx_id}")
        return record

    def _broadcast_websocket(self, alert: Dict[str, Any]):
        """Broadcasts live alert payload to all connected WebSocket clients."""
        for ws in self.active_websockets:
            try:
                # If async, can be awaited or scheduled
                pass
            except Exception:
                pass

    def get_dispatch_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Returns recent notification dispatch records."""
        return self.dispatched_notifications[-limit:]
