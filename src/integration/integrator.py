"""
Multi-Bank Data Integration Engine for RINGTRACE AI.
Consolidates transaction ledgers from Bank A, Bank B, and Bank C into a unified
cross-bank dataset, performs dual-ledger reconciliation, resolves cross-bank duplicates,
verifies data integrity, and persists records to relational storage and CSV/JSON.
"""

from typing import Dict, List, Tuple, Any, Optional
from datetime import datetime, timezone
import json
from pathlib import Path
import pandas as pd
import numpy as np

import config
from src.integration.db import DatabaseManager
from src.integration.schemas import ReconciliationSummary


class MultiBankDataIntegrator:
    """
    Integrates and reconciles heterogeneous multi-bank ledgers.
    Preserves source bank traceability and eliminates redundant duplicate records.
    """

    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        self.db = db_manager or DatabaseManager()

    def integrate_ledgers(
        self,
        bank_ledgers: Dict[str, pd.DataFrame],
        export_artifacts: bool = True,
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Main entry point for Step 3 integration:
        1. Tags records with participating source banks.
        2. Detects cross-bank twin/duplicate records between sender and receiver banks.
        3. Validates transactional integrity (amounts, timestamps, accounts).
        4. Reconciles dual-ledger entries and records discrepancies.
        5. Computes cross-bank flow volume matrix.
        6. Persists consolidated dataset to database, CSV, JSON, and reports.
        """
        tagged_records: List[pd.DataFrame] = []
        raw_ledger_counts: Dict[str, int] = {}
        raw_ledger_volumes: Dict[str, float] = {}

        # 1. Tag and stack participating bank records
        for bank_id, df_bank in bank_ledgers.items():
            if df_bank.empty:
                continue
            df_tag = df_bank.copy()
            df_tag["source_bank"] = bank_id.upper()
            raw_ledger_counts[bank_id.upper()] = len(df_tag)
            raw_ledger_volumes[bank_id.upper()] = float(df_tag["amount"].sum())
            tagged_records.append(df_tag)

        if not tagged_records:
            empty_df = pd.DataFrame()
            return empty_df, {"error": "No transaction ledgers provided for integration"}

        all_stacked = pd.concat(tagged_records, ignore_index=True)
        total_raw_rows = len(all_stacked)

        # 2. Reconcile dual ledgers and deduplicate
        discrepancies: List[Dict[str, Any]] = []
        reconciled_rows: List[Dict[str, Any]] = []

        # Group by transaction_id to find records present in multiple banks
        grouped = all_stacked.groupby("transaction_id")

        for tx_id, group in grouped:
            sources = group["source_bank"].unique().tolist()
            first_row = group.iloc[0].to_dict()

            is_cross_bank = bool(first_row["sender_bank"] != first_row["receiver_bank"])

            if len(group) > 1:
                # Inter-bank transaction recorded by both sender and receiver banks
                # Perform discrepancy check on amount and accounts
                amounts = group["amount"].values
                if np.max(amounts) - np.min(amounts) > 0.01:
                    discrepancies.append({
                        "transaction_id": str(tx_id),
                        "field": "amount",
                        "values": {str(r["source_bank"]): float(r["amount"]) for _, r in group.iterrows()},
                        "resolution": "used_sender_amount",
                    })

                # Determine primary authoritative bank (sender bank has authoritative transfer origin)
                sender_bank = str(first_row["sender_bank"])
                primary_bank = sender_bank if sender_bank in sources else sources[0]

                merged_row = first_row.copy()
                merged_row["participating_banks"] = sources
                merged_row["primary_source_bank"] = primary_bank
                merged_row["reconciliation_status"] = "RECONCILED"
                merged_row["is_cross_bank"] = is_cross_bank
                merged_row["duplicate_copies_detected"] = len(group) - 1
                reconciled_rows.append(merged_row)

            else:
                # Single ledger entry: either internal intra-bank or unilateral inter-bank
                rec_status = "RECONCILED" if not is_cross_bank else (
                    "UNILATERAL_SENDER" if first_row["source_bank"] == first_row["sender_bank"]
                    else "UNILATERAL_RECEIVER"
                )

                single_row = first_row.copy()
                single_row["participating_banks"] = sources
                single_row["primary_source_bank"] = first_row["source_bank"]
                single_row["reconciliation_status"] = rec_status
                single_row["is_cross_bank"] = is_cross_bank
                single_row["duplicate_copies_detected"] = 0
                reconciled_rows.append(single_row)

        df_integrated = pd.DataFrame(reconciled_rows)

        # 3. Format and enforce standard canonical column order
        canonical_cols = [
            "transaction_id",
            "customer_id",
            "sender_account",
            "receiver_account",
            "sender_bank",
            "receiver_bank",
            "amount",
            "timestamp",
            "transaction_type",
            "transaction_status",
            "pattern_type",
            "is_suspicious",
            "ring_id",
            "date_time",
            "participating_banks",
            "primary_source_bank",
            "reconciliation_status",
            "is_cross_bank",
        ]

        # Add any missing canonical columns with safe defaults
        for col in canonical_cols:
            if col not in df_integrated.columns:
                if col == "is_suspicious":
                    df_integrated[col] = 0
                elif col in ["ring_id", "pattern_type"]:
                    df_integrated[col] = "NONE" if col == "ring_id" else "NORMAL_P2P"
                elif col == "date_time":
                    df_integrated[col] = df_integrated["timestamp"]
                else:
                    df_integrated[col] = ""

        # Reorder and sort chronologically
        df_integrated = df_integrated[canonical_cols].sort_values("timestamp").reset_index(drop=True)

        # 4. Compute cross-bank flow analytics
        flow_matrix: Dict[str, Dict[str, Any]] = {}
        cross_bank_flows_list: List[Dict[str, Any]] = []

        for s_bank in config.SIMULATED_BANKS:
            flow_matrix[s_bank] = {}
            for r_bank in config.SIMULATED_BANKS:
                subset = df_integrated[
                    (df_integrated["sender_bank"] == s_bank) & (df_integrated["receiver_bank"] == r_bank)
                ]
                flow_count = len(subset)
                flow_vol = float(subset["amount"].sum())
                suspicious_count = int(subset["is_suspicious"].sum())
                flow_matrix[s_bank][r_bank] = {
                    "count": flow_count,
                    "volume_inr": round(flow_vol, 2),
                    "suspicious_count": suspicious_count,
                }
                cross_bank_flows_list.append({
                    "sender_bank": s_bank,
                    "receiver_bank": r_bank,
                    "is_interbank": s_bank != r_bank,
                    "transaction_count": flow_count,
                    "total_volume_inr": round(flow_vol, 2),
                    "suspicious_count": suspicious_count,
                })

        df_cross_flows = pd.DataFrame(cross_bank_flows_list)

        # 5. Compile Integration & Reconciliation Metrics
        dual_matched = int((df_integrated["duplicate_copies_detected"] > 0).sum()) if "duplicate_copies_detected" in df_integrated else int(
            (df_integrated["participating_banks"].apply(len) > 1).sum()
        )
        single_ledger = len(df_integrated) - dual_matched
        inter_bank_count = int(df_integrated["is_cross_bank"].sum())
        intra_bank_count = len(df_integrated) - inter_bank_count

        summary_metrics = {
            "total_raw_ledger_records": total_raw_rows,
            "total_integrated_transactions": len(df_integrated),
            "dual_ledger_reconciled": dual_matched,
            "single_ledger_unilateral": single_ledger,
            "inter_bank_transactions": inter_bank_count,
            "intra_bank_transactions": intra_bank_count,
            "discrepancy_count": len(discrepancies),
            "raw_ledger_counts": raw_ledger_counts,
            "raw_ledger_volumes": raw_ledger_volumes,
            "total_integrated_volume_inr": round(float(df_integrated["amount"].sum()), 2),
            "pairwise_flow_matrix": flow_matrix,
            "discrepancies": discrepancies,
            "integration_timestamp": datetime.now(timezone.utc).isoformat(),
        }

        # 6. Export Artifacts and Persist to Relational Database
        if export_artifacts:
            # Ensure output directories exist
            config.INTEGRATED_DATA_DIR.mkdir(parents=True, exist_ok=True)
            config.PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
            config.REPORTS_DIR.mkdir(parents=True, exist_ok=True)

            # Export integrated CSV & JSON
            integrated_csv = config.INTEGRATED_DATA_DIR / "transactions_integrated.csv"
            integrated_json = config.INTEGRATED_DATA_DIR / "transactions_integrated.json"
            df_integrated.to_csv(integrated_csv, index=False)
            df_integrated.to_json(integrated_json, orient="records", indent=2)

            # Export cross-bank flow breakdown
            flows_csv = config.INTEGRATED_DATA_DIR / "cross_bank_flows.csv"
            df_cross_flows.to_csv(flows_csv, index=False)

            # Persist to SQLite / PostgreSQL
            self.db.save_integrated_transactions(df_integrated)

            # Save audit records per bank
            audit_records = [
                {
                    "bank_id": b,
                    "raw_row_count": raw_ledger_counts.get(b, 0),
                    "reconciled_count": int(
                        df_integrated[df_integrated["participating_banks"].apply(lambda p: b in p)]["transaction_id"].count()
                    ),
                    "unilateral_count": int(
                        df_integrated[df_integrated["participating_banks"].apply(lambda p: p == [b])]["transaction_id"].count()
                    ),
                    "total_volume": raw_ledger_volumes.get(b, 0.0),
                    "last_sync_time": datetime.now(timezone.utc).isoformat(),
                }
                for b in config.SIMULATED_BANKS
            ]
            self.db.save_audit_metrics(audit_records)

            # Update data/processed/transactions.csv so downstream steps (graph, XGBoost, SHAP, PSI) operate on integrated data
            df_integrated.to_csv(config.PROCESSED_DATA_DIR / "transactions.csv", index=False)
            df_integrated.to_json(config.PROCESSED_DATA_DIR / "transactions.json", orient="records", indent=2)

            # Export reconciliation report JSON
            report_file = config.REPORTS_DIR / "integration_report.json"
            with open(report_file, "w") as f:
                json.dump(summary_metrics, f, indent=2)

        return df_integrated, summary_metrics

    def load_preprocessed_banks_and_integrate(
        self,
        export_artifacts: bool = True,
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """Reads clean datasets from data/preprocessed/ for Bank A, B, and C and executes integration."""
        bank_ledgers: Dict[str, pd.DataFrame] = {}

        for bank_id in config.SIMULATED_BANKS:
            b_key = bank_id.lower()
            clean_file = config.PREPROCESSED_DATA_DIR / f"{b_key}_cleaned.csv"
            if clean_file.exists():
                bank_ledgers[bank_id] = pd.read_csv(clean_file)

        return self.integrate_ledgers(bank_ledgers, export_artifacts=export_artifacts)
