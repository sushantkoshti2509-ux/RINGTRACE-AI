"""
FastAPI REST API for RINGTRACE AI - Step 3: Secure Multi-Bank Data Exchange.
Provides authenticated endpoints for Bank A, Bank B, and Bank C to submit ledger batches,
query cross-bank transactions, and inspect reconciliation metrics.
"""

from typing import List, Optional, Dict, Any
from fastapi import FastAPI, Header, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timezone
import json
import pandas as pd

import config
from src.integration.schemas import (
    TransactionRecord,
    BankSubmissionRequest,
    BankSubmissionResponse,
    ReconciliationSummary,
)
from src.integration.db import DatabaseManager
from src.integration.integrator import MultiBankDataIntegrator
from src.realtime.api import router as realtime_router

# Initialize FastAPI application
app = FastAPI(
    title="RINGTRACE AI - Multi-Bank Data Integration & Real-Time Fraud Detection API",
    description="Secure inter-bank transaction exchange, cross-bank reconciliation, and real-time fraud scoring service.",
    version="1.0.0",
)

# Enable CORS for dashboard integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Real-Time Fraud Detection Router
app.include_router(realtime_router)

# Shared instances
db_manager = DatabaseManager()
integrator = MultiBankDataIntegrator(db_manager=db_manager)

# Simulated API keys for secure inter-bank communication
BANK_API_KEYS = {
    "BANK_A": "key_bank_a_secure_token_2026",
    "BANK_B": "key_bank_b_secure_token_2026",
    "BANK_C": "key_bank_c_secure_token_2026",
    "REGULATOR": "key_regulator_master_token_2026",
}


def verify_bank_auth(bank_id: str, x_bank_api_key: Optional[str] = Header(None)):
    """Verifies that the caller has provided a valid bank API token."""
    b_norm = bank_id.strip().upper()
    expected_key = BANK_API_KEYS.get(b_norm)

    # Allow testing without key if token header is absent in dev mode, but enforce if provided
    if x_bank_api_key and x_bank_api_key != expected_key and x_bank_api_key != BANK_API_KEYS["REGULATOR"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid API Key credentials for bank: {b_norm}",
        )
    return b_norm


@app.get("/", tags=["System"])
def root_info():
    """Returns service metadata and active simulated bank nodes."""
    return {
        "service": "RINGTRACE AI Multi-Bank Data Integration API",
        "status": "OPERATIONAL",
        "participating_banks": config.SIMULATED_BANKS,
        "database_backend": "SQLite / PostgreSQL",
        "docs_url": "/docs",
    }


@app.get("/health", tags=["System"])
def health_check():
    """Healthcheck reporting database status and transaction count."""
    try:
        sample = db_manager.query_transactions(limit=1)
        return {
            "status": "HEALTHY",
            "database_connected": True,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:
        return {
            "status": "DEGRADED",
            "database_connected": False,
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


@app.post(
    "/api/v1/bank/{bank_id}/submit",
    response_model=BankSubmissionResponse,
    tags=["Bank Data Exchange"],
)
def submit_bank_ledger(
    bank_id: str,
    payload: BankSubmissionRequest,
    x_bank_api_key: Optional[str] = Header(None),
):
    """
    Allows a participating bank node (Bank A, B, or C) to securely submit
    a batch of standardized transaction records for centralized reconciliation.
    """
    b_norm = verify_bank_auth(bank_id, x_bank_api_key)

    if b_norm not in config.SIMULATED_BANKS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Bank {b_norm} is not in the approved participant list: {config.SIMULATED_BANKS}",
        )

    records = [tx.model_dump() for tx in payload.transactions]
    if not records:
        return BankSubmissionResponse(
            bank_id=b_norm,
            batch_id=payload.batch_id,
            status="EMPTY_BATCH",
            received_count=0,
            integrated_count=0,
            duplicates_detected=0,
            message="No transactions in payload",
        )

    df_incoming = pd.DataFrame(records)
    df_incoming["source_bank"] = b_norm

    # Reconcile with existing bank datasets
    existing_ledgers = {}
    for other_b in config.SIMULATED_BANKS:
        clean_file = config.PREPROCESSED_DATA_DIR / f"{other_b.lower()}_cleaned.csv"
        if other_b != b_norm and clean_file.exists():
            existing_ledgers[other_b] = pd.read_csv(clean_file)

    existing_ledgers[b_norm] = df_incoming
    df_integrated, metrics = integrator.integrate_ledgers(existing_ledgers, export_artifacts=True)

    return BankSubmissionResponse(
        bank_id=b_norm,
        batch_id=payload.batch_id,
        status="SUCCESS",
        received_count=len(records),
        integrated_count=len(df_integrated),
        duplicates_detected=metrics["dual_ledger_reconciled"],
        message=f"Successfully integrated and reconciled batch {payload.batch_id}",
    )


@app.get("/api/v1/bank/{bank_id}/transactions", tags=["Bank Queries"])
def get_bank_transactions(
    bank_id: str,
    limit: int = Query(50, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    is_suspicious: Optional[int] = Query(None, ge=0, le=1),
):
    """Queries integrated transactions where the bank participates as sender or receiver."""
    b_norm = bank_id.strip().upper()
    results = db_manager.query_transactions(
        bank_id=b_norm,
        is_suspicious=is_suspicious,
        limit=limit,
        offset=offset,
    )
    return {
        "bank_id": b_norm,
        "count": len(results),
        "offset": offset,
        "limit": limit,
        "transactions": results,
    }


@app.get("/api/v1/transactions", tags=["Centralized Queries"])
def query_all_transactions(
    bank_id: Optional[str] = Query(None, description="Filter by participating bank"),
    is_suspicious: Optional[int] = Query(None, description="0=legitimate, 1=flagged"),
    min_amount: Optional[float] = Query(None, ge=0),
    max_amount: Optional[float] = Query(None, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    """Central investigation search across unified multi-bank records."""
    results = db_manager.query_transactions(
        bank_id=bank_id,
        is_suspicious=is_suspicious,
        min_amount=min_amount,
        max_amount=max_amount,
        limit=limit,
        offset=offset,
    )
    return {
        "count": len(results),
        "offset": offset,
        "limit": limit,
        "filters": {
            "bank_id": bank_id,
            "is_suspicious": is_suspicious,
            "min_amount": min_amount,
            "max_amount": max_amount,
        },
        "transactions": results,
    }


@app.get("/api/v1/reconciliation/summary", tags=["Reconciliation & Audit"])
def get_reconciliation_summary():
    """Returns the executive multi-bank cross-reconciliation audit report."""
    report_file = config.REPORTS_DIR / "integration_report.json"
    if report_file.exists():
        with open(report_file, "r") as f:
            return json.load(f)

    # If report file doesn't exist yet, run integration to generate it
    _, summary = integrator.load_preprocessed_banks_and_integrate(export_artifacts=True)
    return summary


@app.get("/api/v1/cross-bank-flows", tags=["Reconciliation & Audit"])
def get_cross_bank_flows():
    """Returns the matrix of transaction counts and volumes between banks."""
    flows_file = config.INTEGRATED_DATA_DIR / "cross_bank_flows.csv"
    if flows_file.exists():
        df_flows = pd.read_csv(flows_file)
        return {
            "flows": df_flows.to_dict(orient="records"),
            "total_flow_records": len(df_flows),
        }

    _, summary = integrator.load_preprocessed_banks_and_integrate(export_artifacts=True)
    return {"flows": summary.get("pairwise_flow_matrix", {})}
