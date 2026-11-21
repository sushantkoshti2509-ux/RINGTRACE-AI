"""
Pydantic schemas for Step 8: Fraud Alert and Notification System API.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class AlertGenerateRequest(BaseModel):
    transaction_id: str = Field(..., description="Unique transaction ID, e.g. TXN10245")
    bank_id: str = Field(..., description="Bank name, e.g. Bank B or BANK_B")
    sender_account: Optional[str] = Field("UNKNOWN", description="Sender account identifier")
    receiver_account: Optional[str] = Field("UNKNOWN", description="Receiver account identifier")
    amount: float = Field(..., ge=0.0, description="Transaction amount in INR")
    timestamp: Optional[str] = Field(None, description="Timestamp YYYY-MM-DD HH:MM:SS")
    fraud_probability: float = Field(..., ge=0.0, le=1.0, description="Predicted fraud probability 0.0 - 1.0")
    risk_level: Optional[str] = Field(None, description="Low, Medium, or High")
    status: Optional[str] = Field("Pending", description="Pending, Under Review, Resolved, Escalated")
    trigger_reasons: Optional[List[str]] = Field(default_factory=list, description="List of rule/model trigger codes")
    recommendation: Optional[str] = Field(None, description="Action recommendation for investigator")
    assigned_to: Optional[str] = Field(None, description="Assigned investigator username or ID")


class AlertStatusUpdateRequest(BaseModel):
    status: str = Field(..., description="New status: Pending, Under Review, Resolved, Escalated")
    notes: Optional[str] = Field(None, description="Investigator note to append")
    updated_by: Optional[str] = Field("Investigator", description="Officer identity updating the alert")


class AlertResponse(BaseModel):
    alert_id: str
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
    recommendation: str
    disclaimer: str
    assigned_to: Optional[str] = None
    investigation_notes: List[Dict[str, Any]] = Field(default_factory=list)
    notified_channels: List[str] = Field(default_factory=list)
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    is_duplicate: Optional[bool] = False
    message: Optional[str] = None
