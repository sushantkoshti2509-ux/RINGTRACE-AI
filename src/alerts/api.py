"""
FastAPI Endpoints for Step 8: Fraud Alert and Notification System.
Provides inter-bank alert generation, query filtering, state transitions,
and WebSocket broadcast channels.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Query, status, WebSocket, WebSocketDisconnect
from datetime import datetime, timezone
import json

from src.alerts.engine import AlertEngine
from src.alerts.schemas import (
    AlertGenerateRequest,
    AlertResponse,
    AlertStatusUpdateRequest,
)

router = APIRouter(prefix="/api/v1/alerts", tags=["Step 8: Fraud Alerts & Notification"])

# Shared engine instance
alert_engine = AlertEngine()


@router.post(
    "/generate",
    response_model=AlertResponse,
    summary="Generate a multi-bank fraud alert",
    description="Processes suspicious transaction risk scoring, prevents duplicates, and dispatches multi-channel notifications.",
)
def generate_fraud_alert(payload: AlertGenerateRequest):
    try:
        alert_dict = payload.model_dump()
        result = alert_engine.generate_alert(alert_dict)
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Alert generation failed: {str(e)}")


@router.get(
    "",
    response_model=List[AlertResponse],
    summary="Query centralized multi-bank alerts",
    description="Retrieves alert records across Bank A, Bank B, and Bank C with optional bank, risk, and status filtering.",
)
def list_alerts(
    bank_id: Optional[str] = Query(None, description="Filter by bank ID (BANK_A, BANK_B, BANK_C)"),
    risk_level: Optional[str] = Query(None, description="Filter by risk tier (High, Medium, Low)"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status (Pending, Under Review, Resolved, Escalated)"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    return alert_engine.query_alerts(
        bank_id=bank_id,
        risk_level=risk_level,
        status=status_filter,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/stats",
    summary="Get multi-bank alert metrics",
    description="Returns aggregate counts grouped by risk level, bank ID, and workflow status.",
)
def get_alert_stats():
    return alert_engine.get_stats()


@router.get(
    "/{alert_id}",
    response_model=AlertResponse,
    summary="Get alert details by ID",
)
def get_alert_detail(alert_id: str):
    res = alert_engine.get_alert(alert_id)
    if not res:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Alert {alert_id} not found.")
    return res


@router.patch(
    "/{alert_id}/status",
    response_model=AlertResponse,
    summary="Update alert investigation status",
    description="Transitions status (Pending, Under Review, Resolved, Escalated) and appends investigator notes.",
)
def update_status(alert_id: str, payload: AlertStatusUpdateRequest):
    try:
        res = alert_engine.update_alert_status(
            alert_id=alert_id,
            new_status=payload.status,
            notes=payload.notes,
            updated_by=payload.updated_by,
        )
        return res
    except KeyError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post(
    "/seed-demo",
    summary="Seed illustrative demo alerts",
    description="Populates sample alerts for Bank A, Bank B, and Bank C (including user's illustrative example).",
)
def seed_demo_alerts():
    demo_samples = [
        {
            "transaction_id": "TXN10245",
            "bank_id": "BANK_B",
            "sender_account": "BNK_B_ACC_00102",
            "receiver_account": "BNK_A_ACC_00551",
            "amount": 85000.0,
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d 02:45:10"),
            "fraud_probability": 0.96,
            "risk_level": "High",
            "status": "Pending",
            "trigger_reasons": ["RAPID_BURST_FORWARDING", "CROSS_BANK_HIGH_VALUE", "NOCTURNAL_OFF_HOURS"],
            "recommendation": "Suspicious transaction detected. Further investigation is recommended.",
        },
        {
            "transaction_id": "TXN10246",
            "bank_id": "BANK_A",
            "sender_account": "BNK_A_ACC_00280",
            "receiver_account": "BNK_C_ACC_00330",
            "amount": 42000.0,
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d 11:15:22"),
            "fraud_probability": 0.58,
            "risk_level": "Medium",
            "status": "Under Review",
            "trigger_reasons": ["HIGH_VELOCITY_SPIKE"],
            "recommendation": "Unusual transaction pattern observed. Compliance review required.",
        },
        {
            "transaction_id": "TXN10247",
            "bank_id": "BANK_C",
            "sender_account": "BNK_C_ACC_00889",
            "receiver_account": "BNK_D_ACC_00912",
            "amount": 92000.0,
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d 03:02:44"),
            "fraud_probability": 0.94,
            "risk_level": "High",
            "status": "Pending",
            "trigger_reasons": ["RAPID_BURST_FORWARDING", "HIGH_PASS_THROUGH_MULE_RATIO"],
            "recommendation": "Suspicious transaction detected. Further investigation is recommended.",
        },
        {
            "transaction_id": "TXN10248",
            "bank_id": "BANK_D",
            "sender_account": "BNK_D_ACC_00450",
            "receiver_account": "BNK_A_ACC_00670",
            "amount": 78000.0,
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d 01:22:15"),
            "fraud_probability": 0.91,
            "risk_level": "High",
            "status": "Pending",
            "trigger_reasons": ["CROSS_BANK_CHAIN_HOP", "RAPID_TURNOVER"],
            "recommendation": "Multi-bank hop detected. Counterparty verification recommended.",
        },
    ]

    results = []
    for s in demo_samples:
        res = alert_engine.generate_alert(s)
        results.append(res)
    return {"status": "success", "seeded_count": len(results), "alerts": results}


@router.websocket("/ws")
async def alert_websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time live alert streaming to browser clients."""
    await websocket.accept()
    alert_engine.notifier.active_websockets.append(websocket)
    try:
        while True:
            # Keep-alive loop
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        alert_engine.notifier.active_websockets.remove(websocket)
    except Exception:
        if websocket in alert_engine.notifier.active_websockets:
            alert_engine.notifier.active_websockets.remove(websocket)
