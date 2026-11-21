"""
Validation utility module for RINGTRACE AI.
Verifies data schemas, integrity, non-negative amounts, timestamp consistency,
and prevents duplicate IDs across the three simulated banks.
"""

from typing import Dict, Any, List
import pandas as pd

REQUIRED_ACCOUNT_COLUMNS = [
    "account_id",
    "bank_id",
    "canonical_entity_id",
    "profile_type",
    "account_age_days",
    "initial_balance",
    "is_mule",
    "ring_id",
    "ring_role",
]

REQUIRED_TRANSACTION_COLUMNS = [
    "transaction_id",
    "timestamp",
    "sender_account",
    "receiver_account",
    "sender_bank",
    "receiver_bank",
    "amount",
    "transaction_type",
    "is_suspicious",
    "ring_id",
]

REQUIRED_RING_COLUMNS = [
    "ring_id",
    "scenario_type",
    "accounts",
    "total_amount",
    "hop_count",
    "duration_minutes",
    "cross_bank_count",
]


def validate_accounts_dataframe(df: pd.DataFrame) -> Dict[str, Any]:
    """Validates the structure and integrity of accounts DataFrame."""
    issues: List[str] = []
    
    # Check missing columns
    missing = [c for c in REQUIRED_ACCOUNT_COLUMNS if c not in df.columns]
    if missing:
        issues.append(f"Missing required account columns: {missing}")
        return {"valid": False, "issues": issues, "row_count": len(df)}

    # Check duplicates
    if df["account_id"].duplicated().any():
        dup_count = int(df["account_id"].duplicated().sum())
        issues.append(f"Found {dup_count} duplicate account_ids.")

    # Check nulls in critical columns
    for col in ["account_id", "bank_id", "canonical_entity_id", "is_mule"]:
        if df[col].isnull().any():
            issues.append(f"Null values present in critical column '{col}'.")

    # Check non-negative balances
    if (df["initial_balance"] < 0).any():
        issues.append("Found negative initial_balance in accounts.")

    # Check account age
    if (df["account_age_days"] < 0).any():
        issues.append("Found negative account_age_days in accounts.")

    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "row_count": len(df),
        "mule_count": int(df["is_mule"].sum()) if "is_mule" in df.columns else 0,
    }


def validate_transactions_dataframe(df: pd.DataFrame) -> Dict[str, Any]:
    """Validates the structure and integrity of transactions DataFrame."""
    issues: List[str] = []

    missing = [c for c in REQUIRED_TRANSACTION_COLUMNS if c not in df.columns]
    if missing:
        issues.append(f"Missing required transaction columns: {missing}")
        return {"valid": False, "issues": issues, "row_count": len(df)}

    # Check duplicate transaction IDs
    if df["transaction_id"].duplicated().any():
        dup_count = int(df["transaction_id"].duplicated().sum())
        issues.append(f"Found {dup_count} duplicate transaction_ids.")

    # Check non-positive amounts
    if (df["amount"] <= 0).any():
        issues.append("Transactions must have strictly positive amounts (amount > 0).")

    # Check self transfers
    if (df["sender_account"] == df["receiver_account"]).any():
        issues.append("Found self-transfers (sender_account == receiver_account).")

    # Check timestamp parseability
    try:
        pd.to_datetime(df["timestamp"])
    except Exception as e:
        issues.append(f"Failed to parse timestamp column: {str(e)}")

    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "row_count": len(df),
        "suspicious_count": int(df["is_suspicious"].sum()) if "is_suspicious" in df.columns else 0,
    }
