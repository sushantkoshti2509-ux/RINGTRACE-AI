"""
RINGTRACE AI - Step 8: Fraud Alert & Notification System Core Engine.
Automates multi-bank alert generation, risk categorization, duplicate prevention,
investigation workflow state tracking, and multi-channel notification dispatch.
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timezone
import json
import logging

import config
from src.integration.db import DatabaseManager
from src.alerts.notifier import AlertNotifier

logger = logging.getLogger("ringtrace.alerts.engine")


class AlertEngine:
    """Core alert orchestration engine for Bank A, Bank B, and Bank C."""

    VALID_STATUSES = {"Pending", "Under Review", "Resolved", "Escalated"}
    VALID_RISK_LEVELS = {"Low", "Medium", "High"}

    def __init__(self, db_manager: Optional[DatabaseManager] = None, notifier: Optional[AlertNotifier] = None):
        self.db = db_manager or DatabaseManager()
        self.notifier = notifier or AlertNotifier()

    def generate_alert(
        self,
        tx_data: Dict[str, Any],
        force_dispatch: bool = False,
    ) -> Dict[str, Any]:
        """
        Generates an automatic fraud alert from transaction detection results.
        Enforces idempotency and duplicate prevention: If an alert for tx_data['transaction_id']
        already exists, returns the existing alert with `is_duplicate=True` without re-dispatching.
        """
        tx_id = str(tx_data.get("transaction_id", "")).strip()
        if not tx_id:
            raise ValueError("transaction_id is required to generate an alert.")

        # 1. Determine risk level and fraud probability
        prob = float(tx_data.get("fraud_probability", 0.0))
        risk_level = tx_data.get("risk_level")

        if not risk_level:
            if prob >= 0.70:
                risk_level = "High"
            elif prob >= 0.35:
                risk_level = "Medium"
            else:
                risk_level = "Low"

        # 2. Synthesize contextual recommendation
        recommendation = tx_data.get("recommendation")
        if not recommendation:
            if risk_level == "High":
                recommendation = "Suspicious transaction detected. Further investigation is recommended."
            elif risk_level == "Medium":
                recommendation = "Unusual transaction pattern observed. Compliance review required."
            else:
                recommendation = "Low risk transaction. Retained in audit log for baseline profiling."

        # 3. Construct unique alert ID
        clean_id = tx_id
        for prefix in ["TXN_", "TX_", "TXN", "TX"]:
            if clean_id.startswith(prefix):
                clean_id = clean_id[len(prefix):]
                break
        alert_id = f"ALT_{clean_id}"

        # Normalize bank ID (e.g. "Bank B" -> "BANK_B")
        raw_bank = str(tx_data.get("bank_id", tx_data.get("sender_bank", "BANK_A"))).strip().upper()
        norm_bank = raw_bank.replace(" ", "_")

        alert_payload = {
            "alert_id": alert_id,
            "transaction_id": tx_id,
            "bank_id": norm_bank,
            "sender_account": str(tx_data.get("sender_account", "UNKNOWN")),
            "receiver_account": str(tx_data.get("receiver_account", "UNKNOWN")),
            "amount": float(tx_data.get("amount", 0.0)),
            "timestamp": str(tx_data.get("timestamp", datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"))),
            "fraud_probability": round(prob, 4),
            "risk_level": risk_level,
            "status": tx_data.get("status", "Pending"),
            "trigger_reasons": tx_data.get("trigger_reasons", []),
            "recommendation": recommendation,
            "assigned_to": tx_data.get("assigned_to"),
            "investigation_notes": [],
            "notified_channels": [],
        }

        # 4. Save to database with duplicate prevention
        saved_record, is_created = self.db.save_alert(alert_payload)

        if not is_created:
            logger.warning(f"Duplicate alert prevented for transaction {tx_id}. Existing alert {saved_record['alert_id']} retained.")
            saved_record["is_duplicate"] = True
            saved_record["message"] = f"Duplicate alert prevented: Transaction {tx_id} already exists under Alert {saved_record['alert_id']}."
            return saved_record

        # 5. Multi-channel notification dispatching for High and Medium risk alerts
        notified_channels = []
        if risk_level in ["High", "Medium"] or force_dispatch:
            notified_channels = self.notifier.dispatch(saved_record)

        saved_record["notified_channels"] = notified_channels
        saved_record["is_duplicate"] = False
        saved_record["message"] = f"Alert {saved_record['alert_id']} generated and dispatched to {saved_record['bank_id']} compliance desk."
        return saved_record

    def update_alert_status(
        self,
        alert_id: str,
        new_status: str,
        notes: Optional[str] = None,
        updated_by: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Transitions alert status across: Pending -> Under Review -> Resolved / Escalated.
        Appends an immutable audit log entry to investigation_notes.
        """
        if new_status not in self.VALID_STATUSES:
            raise ValueError(f"Invalid status '{new_status}'. Allowed statuses: {sorted(list(self.VALID_STATUSES))}")

        updated_record = self.db.update_alert_status(
            alert_id=alert_id,
            new_status=new_status,
            notes=notes,
            updated_by=updated_by,
        )

        if not updated_record:
            raise KeyError(f"Alert with ID '{alert_id}' not found.")

        logger.info(f"Alert {alert_id} status updated to {new_status} by {updated_by or 'System'}")
        return updated_record

    def get_alert(self, alert_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves details of a single alert by ID."""
        return self.db.get_alert(alert_id)

    def query_alerts(
        self,
        bank_id: Optional[str] = None,
        risk_level: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """Queries multi-bank alerts with optional bank, risk, and status filters."""
        return self.db.query_alerts(
            bank_id=bank_id,
            risk_level=risk_level,
            status=status,
            limit=limit,
            offset=offset,
        )

    def get_stats(self) -> Dict[str, Any]:
        """Returns aggregated alert count metrics."""
        return self.db.get_alert_stats()
