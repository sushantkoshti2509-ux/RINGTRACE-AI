"""
FastAPI REST API Router for Real-Time Fraud Detection in RINGTRACE AI.
Provides low-latency transaction processing endpoints for Bank A, Bank B, and Bank C,
risk tier categorization, and historical query interfaces.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field

from src.realtime.detector import RealtimeFraudDetector
from src.integration.db import DatabaseManager

router = APIRouter(prefix="/api/v1/realtime", tags=["Real-Time Fraud Detection"])

# Shared detector instance
db_manager = DatabaseManager()
detector = RealtimeFraudDetector(db_manager=db_manager)


class RealtimeTransactionRequest(BaseModel):
    """Schema for incoming transaction events streamed from participating banks."""
    transaction_id: Optional[str] = Field(default=None, description="Unique transaction ID")
    bank_id: str = Field(..., description="Reporting bank code: BANK_A, BANK_B, or BANK_C")
    sender_account: str = Field(..., description="Source account identifier")
    receiver_account: str = Field(..., description="Destination account identifier")
    amount: float = Field(..., gt=0, description="Amount in INR")
    timestamp: Optional[str] = Field(default=None, description="ISO 8601 timestamp YYYY-MM-DD HH:MM:SS")
    transaction_type: Optional[str] = Field(default="UPI_P2P", description="UPI_P2P, IMPS, NEFT, etc.")


class RealtimeDetectionResponse(BaseModel):
    """Real-time detection result returned to the bank within milliseconds."""
    transaction_id: str
    bank_id: str
    sender_account: str
    receiver_account: str
    amount: float
    timestamp: str
    fraud_probability: float
    risk_level: str
    status: str
    trigger_reasons: List[str]
    latency_ms: float
    model_used: str


@router.post("/transaction", response_model=RealtimeDetectionResponse)
def detect_transaction_fraud(tx: RealtimeTransactionRequest):
    """
    Analyzes an incoming transaction in real time (< 10ms), predicts fraud probability,
    assigns risk level (Low, Medium, High), and logs result to audit database.
    """
    res = detector.process_transaction(tx.model_dump())
    return RealtimeDetectionResponse(**res)


@router.post("/batch", response_model=List[RealtimeDetectionResponse])
def detect_batch_stream(transactions: List[RealtimeTransactionRequest]):
    """Processes a micro-batch of incoming stream transactions with minimal latency."""
    results = [detector.process_transaction(t.model_dump()) for t in transactions]
    return [RealtimeDetectionResponse(**r) for r in results]


@router.get("/history")
def get_detection_history(
    bank_id: Optional[str] = Query(None, description="Filter by reporting bank"),
    risk_level: Optional[str] = Query(None, description="Low, Medium, or High"),
    status_filter: Optional[str] = Query(None, alias="status", description="Normal, Review Required, Suspicious"),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    """Queries detection history logs from the persistent relational database."""
    logs = db_manager.query_realtime_logs(
        bank_id=bank_id,
        risk_level=risk_level,
        status=status_filter,
        limit=limit,
        offset=offset,
    )
    return {
        "count": len(logs),
        "offset": offset,
        "limit": limit,
        "logs": logs,
    }


@router.get("/stats")
def get_realtime_stats():
    """Returns runtime performance statistics, fraud rates, and average latency."""
    return detector.get_summary_stats()
