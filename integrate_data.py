"""
RINGTRACE AI - Step 3: Multi-Bank Data Integration CLI Runner.
Combines transaction records from Bank A, Bank B, and Bank C into a unified,
reconciled dataset, stores records in SQLite/PostgreSQL, and optionally launches
the secure FastAPI inter-bank exchange API.
"""

import sys
import argparse
from pathlib import Path

# Setup paths
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import config
from src.integration.db import DatabaseManager
from src.integration.integrator import MultiBankDataIntegrator


def print_banner():
    print("=" * 76)
    print("🏛️  RINGTRACE AI - STEP 3: MULTI-BANK DATA INTEGRATION")
    print("• Scope: Bank A, Bank B, and Bank C Multi-Ledger Reconciliation")
    print("• Technologies: Python, Pandas, SQLAlchemy, FastAPI, PostgreSQL/SQLite")
    print("=" * 76)


def run_integration(db_url: str = None, export_artifacts: bool = True):
    print("\n[1/4] Connecting to Relational Database & Ingesting Bank Ledgers...")
    db = DatabaseManager(db_url=db_url)
    integrator = MultiBankDataIntegrator(db_manager=db)

    print(f"  • Database Backend: {db.db_url}")
    print("  • Reading preprocessed ledgers from data/preprocessed/...")

    df_integrated, metrics = integrator.load_preprocessed_banks_and_integrate(
        export_artifacts=export_artifacts
    )

    if df_integrated.empty:
        print("❌ Error: No preprocessed bank data found in data/preprocessed/!")
        print("   Please run 'python preprocess_data.py' first.")
        return

    print("\n[2/4] Cross-Bank Ledger Reconciliation Summary:")
    print("-" * 76)
    print(f"  • Total Ingested Ledger Entries (A + B + C):  {metrics['total_raw_ledger_records']:,}")
    print(f"  • Dual-Ledger Cross-Bank Twins Reconciled:   {metrics['dual_ledger_reconciled']:,}")
    print(f"  • Single-Ledger Intra-Bank Transfers:        {metrics['single_ledger_unilateral']:,}")
    print(f"  • Discrepancies / Amount Collisions:         {metrics['discrepancy_count']}")
    print(f"  • Consolidated Integrated Unique Transactions:{metrics['total_integrated_transactions']:,}")
    print(f"  • Total Transacted Volume (INR):             ₹{metrics['total_integrated_volume_inr']:,.2f}")
    print("-" * 76)

    print("\n[3/4] Ingestion Breakdown by Participating Bank:")
    for bank_id, count in metrics["raw_ledger_counts"].items():
        vol = metrics["raw_ledger_volumes"].get(bank_id, 0.0)
        print(f"  • [{bank_id}] Raw Ledger Rows: {count:,} | Volume: ₹{vol:,.2f}")

    print("\n[4/4] Cross-Bank Flow Volume Matrix:")
    matrix = metrics["pairwise_flow_matrix"]
    banks = config.SIMULATED_BANKS
    header = f"  {'FROM / TO':<14}" + "".join([f"{b:>18}" for b in banks])
    print(header)
    print("  " + "-" * (14 + 18 * len(banks)))
    for s_bank in banks:
        row_str = f"  {s_bank:<14}"
        for r_bank in banks:
            flow_info = matrix.get(s_bank, {}).get(r_bank, {})
            cnt = flow_info.get("count", 0)
            vol = flow_info.get("volume_inr", 0.0)
            cell = f"{cnt:,} (₹{vol/1e5:,.1f}L)"
            row_str += f"{cell:>18}"
        print(row_str)

    print("\n📂 Output Artifacts Created:")
    print(f"  • CSV:  {config.INTEGRATED_DATA_DIR / 'transactions_integrated.csv'}")
    print(f"  • JSON: {config.INTEGRATED_DATA_DIR / 'transactions_integrated.json'}")
    print(f"  • Matrix Flow: {config.INTEGRATED_DATA_DIR / 'cross_bank_flows.csv'}")
    print(f"  • Database: {config.INTEGRATED_DATA_DIR / 'ringtrace_integrated.db'}")
    print(f"  • Audit Report: {config.REPORTS_DIR / 'integration_report.json'}")
    print(f"  • Central Canonical: {config.PROCESSED_DATA_DIR / 'transactions.csv'}")

    print("\n" + "=" * 76)
    print("🎯 STEP 3 COMPLETE: UNIFIED MULTI-BANK DATASET READY FOR FEATURE ENGINEERING")
    print("=" * 76)


def main():
    parser = argparse.ArgumentParser(
        description="RINGTRACE AI - Step 3: Multi-Bank Data Integration & Reconciliation."
    )
    parser.add_argument(
        "--db-url",
        type=str,
        default=None,
        help="Custom SQLAlchemy database URL (defaults to SQLite: data/integrated/ringtrace_integrated.db)",
    )
    parser.add_argument(
        "--no-export",
        action="store_true",
        help="Skip writing files to disk (dry run)",
    )
    parser.add_argument(
        "--serve",
        action="store_true",
        help="Start the FastAPI inter-bank data exchange REST API server",
    )
    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Host address for FastAPI server (default: 0.0.0.0)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port number for FastAPI server (default: 8000)",
    )

    args = parser.parse_args()

    print_banner()
    run_integration(db_url=args.db_url, export_artifacts=not args.no_export)

    if args.serve:
        print(f"\n🚀 Launching FastAPI REST API on http://{args.host}:{args.port}...")
        import uvicorn
        from src.integration.api import app
        uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
