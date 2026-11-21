"""
RINGTRACE AI - Step 3: Multi-Bank Data Integration Module.
Provides centralized schema normalization, dual-ledger cross-bank reconciliation,
PostgreSQL/SQLite database persistence, and secure REST APIs for Bank A, B, and C.
"""

from src.integration.schemas import (
    TransactionRecord,
    TransactionCreate,
    BankSubmissionRequest,
    ReconciliationSummary,
)
from src.integration.db import DatabaseManager, IntegratedTransactionModel
from src.integration.integrator import MultiBankDataIntegrator

__all__ = [
    "TransactionRecord",
    "TransactionCreate",
    "BankSubmissionRequest",
    "ReconciliationSummary",
    "DatabaseManager",
    "IntegratedTransactionModel",
    "MultiBankDataIntegrator",
]
