"""
FastAPI REST API router for Step 9: Centralized Multi-Bank Monitoring Dashboard.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Query, status, Response

from src.dashboard.service import DashboardMonitoringService

router = APIRouter(prefix="/api/v1/dashboard", tags=["Step 9: Centralized Monitoring Dashboard"])

dashboard_service = DashboardMonitoringService()


@router.get(
    "/summary",
    summary="Get multi-bank dashboard executive summary",
    description="Returns high-level KPI metrics: Total Transactions, Suspicious, Legitimate, Pending Alerts, and Bank-wise table.",
)
def get_dashboard_summary(
    mode: str = Query("federated", pattern="^(federated|reconciled)$", description="Mode: 'federated' (25,430 scale) or 'reconciled' (canonical DB)")
):
    return dashboard_service.get_executive_summary(mode=mode)


@router.get(
    "/transactions",
    summary="Search and filter multi-bank transactions",
    description="Allows authorized users to search, filter, and inspect transaction details across Bank A, Bank B, and Bank C.",
)
def search_transactions(
    response: Response,
    bank_id: Optional[str] = Query(None, description="Bank filter: Bank A, Bank B, Bank C, or ALL"),
    risk_level: Optional[str] = Query(None, description="Risk filter: High, Low, or ALL"),
    min_amount: Optional[float] = Query(None, ge=0.0, description="Minimum transaction amount"),
    max_amount: Optional[float] = Query(None, ge=0.0, description="Maximum transaction amount"),
    search_query: Optional[str] = Query(None, description="Search term for Transaction ID, Account ID, or Customer ID"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    results = dashboard_service.query_transactions(
        bank_id=bank_id,
        risk_level=risk_level,
        min_amount=min_amount,
        max_amount=max_amount,
        search_query=search_query,
        limit=limit,
        offset=offset,
    )
    total_matched = dashboard_service.count_transactions(
        bank_id=bank_id,
        risk_level=risk_level,
        min_amount=min_amount,
        max_amount=max_amount,
        search_query=search_query,
    )
    response.headers["X-Total-Count"] = str(total_matched)
    return results


@router.get(
    "/trends",
    summary="Get temporal transaction and fraud trends",
    description="Returns time-series series data for analytical charts.",
)
def get_trends():
    return dashboard_service.get_time_series_trends()
