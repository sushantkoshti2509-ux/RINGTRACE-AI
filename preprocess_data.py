"""
RINGTRACE AI - Step 2: Standalone Data Preprocessing and Standardization CLI.
Cleans, normalizes, validates, and encodes transaction datasets from Bank A, B, and C
using Pandas, NumPy, and Scikit-learn.
"""

import sys
import json
import argparse
from pathlib import Path

# Setup paths
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import config
from src.preprocessing.clean import DataPreprocessor


def main():
    parser = argparse.ArgumentParser(
        description="RINGTRACE AI - Step 2: Preprocess and Standardize Bank Datasets."
    )
    parser.add_argument(
        "--bank",
        type=str,
        default="all",
        choices=["all", "BANK_A", "BANK_B", "BANK_C"],
        help="Specify which bank ledger to preprocess (default: all)",
    )
    parser.add_argument(
        "--export",
        action="store_true",
        default=True,
        help="Export preprocessed clean datasets to data/preprocessed/",
    )

    args = parser.parse_args()

    print("=" * 70)
    print("🧹 RINGTRACE AI - STEP 2: DATA PREPROCESSING & STANDARDIZATION")
    print(f"• Target Scope: {args.bank.upper()}")
    print("• Technologies: Python, Pandas, NumPy, Scikit-learn")
    print("=" * 70)

    preprocessor = DataPreprocessor()
    results = preprocessor.process_all_banks(export_preprocessed=args.export)

    print("\n✅ PREPROCESSING & STANDARDIZATION SUMMARY:")
    for bank_id in config.SIMULATED_BANKS:
        if bank_id in results:
            stats = results[bank_id]["cleaning_stats"]
            is_valid = results[bank_id]["validation_valid"]
            status_symbol = "✓" if is_valid else "✗"
            print(f"\n[{bank_id}] {status_symbol} Standardized & Validated:")
            print(f"  • Initial Ledger Rows: {stats['initial_rows']:,}")
            print(f"  • Clean Standardized Rows: {stats['final_rows']:,}")
            print(f"  • Duplicates Removed: {stats['duplicates_removed']:,}")
            print(f"  • Invalid Amounts Dropped: {stats['invalid_amounts_dropped']}")
            print(f"  • Self-Transfers Filtered: {stats['self_transfers_dropped']}")
            print(f"  • Suspicious Transactions Identified: {stats['suspicious_transactions']}")

    if "ACCOUNTS" in results:
        acc_stats = results["ACCOUNTS"]["cleaning_stats"]
        print(f"\n[ACCOUNTS CATALOG] ✓ Standardized & Validated:")
        print(f"  • Final Clean Accounts: {acc_stats['final_accounts']:,}")
        print(f"  • Mule Accounts Cataloged: {acc_stats['mule_accounts']:,}")

    print("\n📂 Output Artifacts Created in data/preprocessed/:")
    print("  • bank_a_cleaned.csv / .json")
    print("  • bank_b_cleaned.csv / .json")
    print("  • bank_c_cleaned.csv / .json")
    print("  • accounts_cleaned.csv / .json")
    print("  • models/encoders/categorical_encoders.json (Scikit-learn Ordinal Mappings)")
    print("  • reports/preprocessing_report.json")

    print("\n" + "=" * 70)
    print("🎯 STEP 2 COMPLETE: CLEAN STANDARDIZED DATA READY FOR STEP 3 (DATA INTEGRATION)")
    print("=" * 70)


if __name__ == "__main__":
    main()
