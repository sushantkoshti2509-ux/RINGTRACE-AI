"""
Feature 3: Fraud Investigation Assistant - Case Manager.
Automates investigation case creation, evidence assembly, workflow status transitions,
and audit trail management for detected mule rings.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import json
import logging

import config
from src.integration.db import DatabaseManager
from src.adapter.detection_adapter import DetectionAdapter
from src.explainable_ai.reason_generator import HumanExplanationGenerator

logger = logging.getLogger("ringtrace.investigation.case_manager")


class CaseManager:
    """Manages full lifecycle of multi-bank mule ring investigation cases."""

    DEFAULT_CHECKLIST = [
        {"id": "step_1", "task": "Verify transaction velocity and rapid pass-through ratios", "completed": False},
        {"id": "step_2", "task": "Cross-reference counterparty accounts across Bank A, B, and C", "completed": False},
        {"id": "step_3", "task": "Examine nocturnal timestamps and high-value transfer bursts", "completed": False},
        {"id": "step_4", "task": "Check for circular transaction loops (layering evidence)", "completed": False},
        {"id": "step_5", "task": "Coordinate with counterparty bank compliance desks", "completed": False},
        {"id": "step_6", "task": "File regulatory SAR (Suspicious Activity Report) if confirmed", "completed": False},
    ]

    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        self.db = db_manager or DatabaseManager()
        self.adapter = DetectionAdapter()
        self.reason_gen = HumanExplanationGenerator()

    def sync_cases_from_detected_rings(self) -> List[Dict[str, Any]]:
        """
        Reads candidate mule rings from the existing detection pipeline
        and automatically creates investigation cases in the database if not present.
        """
        rings = self.adapter.get_standardized_rings()
        created_cases = []

        for idx, ring in enumerate(rings):
            case_id = f"CASE-MR-{idx+1:03d}"
            existing = self.db.get_investigation_case(case_id)
            if existing:
                created_cases.append(existing)
                continue

            members = ring.get("member_accounts", [])
            banks = ring.get("banks_involved", ["BANK_A", "BANK_B", "BANK_C"])
            vol = ring.get("total_volume", 0.0)
            topology = ring.get("topology_type", "MULTI_HOP_CHAIN")
            risk = ring.get("risk_score", 92.0)

            # Synthesize AI-generated case summary
            ai_summary = (
                f"{len(members)} accounts across {len(banks)} banks demonstrate repeated incoming and outgoing "
                f"transactions, rapid fund forwarding, and {topology.lower().replace('_', ' ')} patterns. "
                f"These indicators suggest a potentially coordinated mule network operating across institutions."
            )

            case_payload = {
                "case_id": case_id,
                "candidate_ring_id": ring.get("candidate_ring_id", f"RING_{idx+1:03d}"),
                "title": f"Investigation Case #{case_id.replace('CASE-', '')} - {topology}",
                "risk_score": risk,
                "risk_tier": ring.get("risk_tier", "HIGH"),
                "status": "Pending",
                "connected_accounts_count": len(members),
                "banks_involved": ",".join(banks),
                "total_volume": vol,
                "transactions_count": ring.get("transactions_count", len(members) * 4),
                "detected_patterns": ring.get("detected_patterns", [topology]),
                "member_accounts": members,
                "ai_summary": ai_summary,
                "checklist_state": {item["id"]: False for item in self.DEFAULT_CHECKLIST},
                "feedback": {},
                "assigned_to": None,
                "case_notes": [],
            }

            saved_case, _ = self.db.save_investigation_case(case_payload)
            created_cases.append(saved_case)

        return created_cases

    def get_case(self, case_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves investigation case by ID."""
        return self.db.get_investigation_case(case_id)

    def update_status(
        self,
        case_id: str,
        new_status: str,
        notes: Optional[str] = None,
        updated_by: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Updates case status (Pending, Under Review, Escalated, Resolved, Closed)."""
        valid_statuses = {"Pending", "Under Review", "Escalated", "Resolved", "Closed"}
        if new_status not in valid_statuses:
            raise ValueError(f"Invalid status '{new_status}'. Allowed: {sorted(list(valid_statuses))}")

        return self.db.update_case_status(
            case_id=case_id,
            new_status=new_status,
            notes=notes,
            updated_by=updated_by,
        )

    def update_checklist(self, case_id: str, step_id: str, completed: bool) -> Optional[Dict[str, Any]]:
        """Updates completion status for a specific checklist step."""
        case = self.db.get_investigation_case(case_id)
        if not case:
            return None

        chk = case.get("checklist_state", {})
        chk[step_id] = completed
        return self.db.update_case_checklist(case_id, chk)

    def record_feedback(
        self,
        case_id: str,
        decision: str,  # "CONFIRMED_FRAUD" or "CLEARED_FALSE_POSITIVE"
        reason: str,
        reviewed_by: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Records human compliance decision (Confirmed Fraud vs. Cleared False Positive)
        and transitions the case to Resolved or Closed.
        """
        return self.db.record_case_feedback(
            case_id=case_id,
            feedback_status=decision,
            reason=reason,
            reviewed_by=reviewed_by,
        )

    def list_cases(
        self,
        status: Optional[str] = None,
        risk_tier: Optional[str] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Lists cases with optional status and risk tier filtering."""
        return self.db.query_investigation_cases(
            status=status,
            risk_tier=risk_tier,
            limit=limit,
        )

    def get_stats(self) -> Dict[str, Any]:
        """Returns case counts by workflow state."""
        return self.db.get_investigation_case_stats()
