"""
Pydantic data schemas for RINGTRACE AI Step 3: Multi-Bank Data Integration.
Establishes a uniform data contract across Bank A, Bank B, and Bank C.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator


class TransactionBase(BaseModel):
    """Core transaction schema common to all participating banks."""
    transaction_id: str = Field(..., description="Unique transaction reference across banks")
    customer_id: str = Field(..., description="Customer identifier within origin bank")
    sender_account: str = Field(..., description="Originating account number / VPA")
    receiver_account: str = Field(..., description="Destination account number / VPA")
    sender_bank: str = Field(..., description="Origin bank code, e.g. BANK_A")
    receiver_bank: str = Field(..., description="Destination bank code, e.g. BANK_B")
    amount: float = Field(..., gt=0, description="Transaction amount in INR")
    timestamp: str = Field(..., description="ISO 8601 timestamp YYYY-MM-DD HH:MM:SS")
    transaction_type: str = Field(default="UPI_P2P", description="UPI_P2P, UPI_MERCHANT, NEFT, IMPS")
    transaction_status: str = Field(default="SUCCESS", description="SUCCESS, FAILED, PENDING")
    is_suspicious: int = Field(default=0, ge=0, le=1, description="Binary suspicion flag")
    ring_id: Optional[str] = Field(default="NONE", description="Mule ring identifier if flagged")
    pattern_type: Optional[str] = Field(default="NORMAL_P2P", description="Behavioral pattern tag")

    @field_validator("sender_account", "receiver_account", "sender_bank", "receiver_bank")
    @classmethod
    def normalize_strings(cls, v: str) -> str:
        return str(v).strip().upper()

    @field_validator("amount")
    @classmethod
    def round_amount(cls, v: float) -> float:
        return round(float(v), 2)


class TransactionCreate(TransactionBase):
    """Payload for submitting single transactions into the integration exchange."""
    source_bank: Optional[str] = Field(default=None, description="Bank logging this ledger row")


class TransactionRecord(TransactionBase):
    """Consolidated, reconciled multi-bank transaction record."""
    participating_banks: List[str] = Field(
        default_factory=list,
        description="List of banks that reported this transaction in their ledgers",
    )
    primary_source_bank: str = Field(
        ...,
        description="Authoritative bank originating the transfer",
    )
    reconciliation_status: str = Field(
        default="RECONCILED",
        description="RECONCILED (dual-ledger matched), UNILATERAL_SENDER, or UNILATERAL_RECEIVER",
    )
    is_cross_bank: bool = Field(
        ...,
        description="True if sender_bank != receiver_bank",
    )
    date_time: Optional[str] = Field(
        default=None,
        description="Mirror of timestamp for downstream compatibility",
    )


class BankSubmissionRequest(BaseModel):
    """Batch payload submitted by a bank node to the central integration engine."""
    bank_id: str = Field(..., description="Identifier of submitting bank (BANK_A, BANK_B, BANK_C)")
    batch_id: str = Field(..., description="Unique batch transmission ID")
    submission_timestamp: Optional[str] = Field(default=None, description="Transmission timestamp")
    records_count: int = Field(..., ge=0, description="Declared record count in batch")
    transactions: List[TransactionCreate] = Field(..., description="Array of transaction records")


class BankSubmissionResponse(BaseModel):
    """Acknowledgment returned to bank node after batch integration."""
    bank_id: str
    batch_id: str
    status: str
    received_count: int
    integrated_count: int
    duplicates_detected: int
    message: str


class DiscrepancyRecord(BaseModel):
    """Details of any discrepancies detected between bank ledger entries."""
    transaction_id: str
    field_name: str
    bank_values: Dict[str, Any]
    resolution: str


class ReconciliationSummary(BaseModel):
    """Executive summary of multi-bank cross-reconciliation."""
    total_raw_ledger_records: int
    total_integrated_transactions: int
    dual_ledger_reconciled: int
    single_ledger_unilateral: int
    inter_bank_transactions: int
    intra_bank_transactions: int
    discrepancy_count: int
    pairwise_flow_matrix: Dict[str, Dict[str, float]]
    bank_participation_counts: Dict[str, int]
