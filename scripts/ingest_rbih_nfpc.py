#!/usr/bin/env python3
"""
RINGTRACE AI - CLI Ingestion Tool for RBIH NFPC Phase 2 Dataset.
References: https://www.kaggle.com/datasets/abhyudayrbih/rbih-nfpc-phase-2/

Usage:
    # 1. Automatic scan of data/benchmarks/rbih_nfpc or ~/Downloads:
    python scripts/ingest_rbih_nfpc.py

    # 2. Ingest directly from custom downloaded folder:
    python scripts/ingest_rbih_nfpc.py --source /path/to/rbih-nfpc-phase-2

    # 3. Ingest and synchronize with live central ledger database:
    python scripts/ingest_rbih_nfpc.py --sync-db
"""

import sys
import argparse
from pathlib import Path
import pandas as pd

# Add repo root to path
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

import config
from src.data_sources.rbih_nfpc_loader import RBIHNFPCDataLoader
from src.integration.db import DatabaseManager, IntegratedTransactionModel, FraudAlertModel


def main():
    parser = argparse.ArgumentParser(description="Ingest RBIH NFPC Phase 2 Parquet/CSV dataset into RINGTRACE AI.")
    parser.add_argument("--source", type=str, default=None, help="Directory containing downloaded RBIH NFPC parquet/csv files.")
    parser.add_argument("--sync-db", action="store_true", help="Sync converted transactions into the central SQLite database.")
    parser.add_argument("--limit-tx", type=int, default=50000, help="Maximum transactions to ingest into active memory.")
    args = parser.parse_args()

    source_dir = Path(args.source) if args.source else None
    loader = RBIHNFPCDataLoader(data_dir=source_dir)

    print("=" * 70)
    print("  RINGTRACE AI: RBIH NFPC Phase 2 Ingestion Pipeline")
    print("  National Fraud Prevention Challenge (Reserve Bank Innovation Hub)")
    print("=" * 70)

    local_files = loader.find_local_dataset()
    print("\nScanning local storage for RBIH NFPC dataset files...")
    for k, v in local_files.items():
        status_str = f"Found: {v}" if v else "Not found (will use high-fidelity benchmark synthesis)"
        print(f"  • {k.ljust(15)}: {status_str}")

    acc_df, tx_df, lbl_df, cust_df = loader.load_or_generate_dataset()
    print(f"\n[+] Raw dataset loaded successfully:")
    print(f"    - Accounts:     {len(acc_df):,} records")
    print(f"    - Transactions: {len(tx_df):,} records")
    print(f"    - Train Labels: {len(lbl_df):,} records ({lbl_df['is_mule'].sum():,} flagged mules)")
    if not cust_df.empty:
        print(f"    - Customers:    {len(cust_df):,} records")

    print("\n[+] Converting to unified RINGTRACE AI 4-bank standard schema...")
    std_acc, std_tx, std_rings = loader.convert_to_ringtrace_standard(acc_df, tx_df, lbl_df)
    print(f"    - Standardized Accounts:     {len(std_acc):,} (across Bank A, B, C, D)")
    print(f"    - Standardized Directed TX:  {len(std_tx):,} records")
    print(f"    - Discovered Mule Rings:     {len(std_rings):,} topology groups")

    if args.sync_db:
        print("\n[+] Syncing standardized transactions to active database...")
        db = DatabaseManager()
        with db.get_session() as session:
            count = 0
            for _, row in std_tx.head(args.limit_tx).iterrows():
                # Avoid duplicate insertion
                existing = session.query(IntegratedTransactionModel).filter(
                    IntegratedTransactionModel.transaction_id == row["transaction_id"]
                ).first()
                if not existing:
                    cust_id = str(row.get("customer_id") or f"CUST_{row['sender_account']}")
                    session.add(IntegratedTransactionModel(
                        transaction_id=row["transaction_id"],
                        customer_id=cust_id,
                        sender_account=row["sender_account"],
                        receiver_account=row["receiver_account"],
                        sender_bank=row["sender_bank"],
                        receiver_bank=row["receiver_bank"],
                        amount=row["amount"],
                        timestamp=row["timestamp"],
                        transaction_type=row["transaction_type"],
                        is_suspicious=row["is_suspicious"],
                        is_cross_bank=row["sender_bank"] != row["receiver_bank"],
                        pattern_type="RAPID_DISPERSION" if row["is_suspicious"] == 1 else "NORMAL_P2P",
                        participating_banks=f"{row['sender_bank']},{row['receiver_bank']}",
                        primary_source_bank=row["sender_bank"],
                    ))
                    count += 1
            session.commit()
            print(f"    [OK] Successfully inserted {count:,} RBIH transactions into database!")

    print("\n" + "=" * 70)
    print("  RBIH NFPC Phase 2 Ingestion Completed Successfully!")
    print("=" * 70)


if __name__ == "__main__":
    main()
