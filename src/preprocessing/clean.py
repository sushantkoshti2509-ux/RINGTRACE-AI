"""
RINGTRACE AI - Data Preprocessing and Cleaning Module.
Cleans raw simulated bank data, handles missing values, formats timestamps,
and prepares consistent account and transaction datasets.
"""

from typing import Tuple, Dict, Any
import pandas as pd
import numpy as np

import config
from src.utils.validation import validate_accounts_dataframe, validate_transactions_dataframe


class DataPreprocessor:
    """Preprocesses and normalizes account and transaction data."""

    def __init__(self):
        pass

    def clean_accounts(self, df: pd.DataFrame) -> pd.DataFrame:
        """Cleans and standardizes accounts dataframe."""
        df = df.copy()
        df["account_id"] = df["account_id"].astype(str).str.strip()
        df["bank_id"] = df["bank_id"].astype(str).str.strip()
        df["canonical_entity_id"] = df["canonical_entity_id"].astype(str).str.strip()
        df["profile_type"] = df["profile_type"].astype(str).str.strip()
        df["account_age_days"] = pd.to_numeric(df["account_age_days"], errors="coerce").fillna(30).astype(int)
        df["initial_balance"] = pd.to_numeric(df["initial_balance"], errors="coerce").fillna(0.0).astype(float)
        df["is_mule"] = pd.to_numeric(df["is_mule"], errors="coerce").fillna(0).astype(int)
        df["ring_id"] = df["ring_id"].fillna("NONE").astype(str).str.strip()
        df["ring_role"] = df["ring_role"].fillna("LEGITIMATE").astype(str).str.strip()

        # Remove duplicate account IDs if any
        df = df.drop_duplicates(subset=["account_id"]).reset_index(drop=True)
        return df

    def clean_transactions(self, df: pd.DataFrame) -> pd.DataFrame:
        """Cleans and standardizes transactions dataframe."""
        df = df.copy()
        df["transaction_id"] = df["transaction_id"].astype(str).str.strip()
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df["sender_account"] = df["sender_account"].astype(str).str.strip()
        df["receiver_account"] = df["receiver_account"].astype(str).str.strip()
        df["sender_bank"] = df["sender_bank"].astype(str).str.strip()
        df["receiver_bank"] = df["receiver_bank"].astype(str).str.strip()
        df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0.0).astype(float)
        df["transaction_type"] = df["transaction_type"].astype(str).str.strip()
        df["is_suspicious"] = pd.to_numeric(df["is_suspicious"], errors="coerce").fillna(0).astype(int)
        df["ring_id"] = df["ring_id"].fillna("NONE").astype(str).str.strip()

        # Drop invalid transactions (non-positive amounts, self-loops)
        df = df[(df["amount"] > 0) & (df["sender_account"] != df["receiver_account"])]
        df = df.drop_duplicates(subset=["transaction_id"]).sort_values("timestamp").reset_index(drop=True)
        return df

    def run_cleaning_pipeline(
        self,
        accounts_raw: pd.DataFrame,
        transactions_raw: pd.DataFrame,
    ) -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, Any]]:
        """Executes end-to-end cleaning and validates output integrity."""
        acc_clean = self.clean_accounts(accounts_raw)
        tx_clean = self.clean_transactions(transactions_raw)

        acc_val = validate_accounts_dataframe(acc_clean)
        tx_val = validate_transactions_dataframe(tx_clean)

        validation_report = {
            "accounts_valid": acc_val["valid"],
            "accounts_issues": acc_val["issues"],
            "accounts_count": acc_val["row_count"],
            "transactions_valid": tx_val["valid"],
            "transactions_issues": tx_val["issues"],
            "transactions_count": tx_val["row_count"],
        }

        return acc_clean, tx_clean, validation_report
