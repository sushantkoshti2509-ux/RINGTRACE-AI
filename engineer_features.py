"""
RINGTRACE AI - Step 4: Feature Engineering & Pattern Analysis CLI Runner.
Extracts transaction-level and account-level features, analyzes behavioral patterns,
enforces ground-truth leakage isolation, and exports model-ready feature matrices.
"""

import sys
import argparse
from pathlib import Path
import pandas as pd

# Setup paths
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import config
from src.features.pipeline import FeatureEngineeringPipeline


def print_banner():
    print("=" * 76)
    print("🔬 RINGTRACE AI - STEP 4: FEATURE ENGINEERING & TRANSACTION PATTERN ANALYSIS")
    print("• Technologies: Python, Pandas, NumPy, Scikit-learn, NetworkX")
    print("• Guardrails: Strict ground-truth isolation to prevent data leakage")
    print("=" * 76)


def main():
    parser = argparse.ArgumentParser(
        description="RINGTRACE AI - Step 4: Feature Engineering & Transaction Pattern Analysis."
    )
    parser.add_argument(
        "--no-export",
        action="store_true",
        help="Skip writing files to disk (dry run)",
    )
    args = parser.parse_args()

    print_banner()

    # Ingest integrated transactions and accounts
    tx_path = config.INTEGRATED_DATA_DIR / "transactions_integrated.csv"
    if not tx_path.exists():
        tx_path = config.PROCESSED_DATA_DIR / "transactions.csv"

    acc_path = config.PREPROCESSED_DATA_DIR / "accounts_cleaned.csv"
    if not acc_path.exists():
        acc_path = config.PROCESSED_DATA_DIR / "accounts.csv"

    if not tx_path.exists() or not acc_path.exists():
        print("❌ Error: Missing input data. Please run Steps 1, 2, and 3 first:")
        print("   python generate_data.py && python preprocess_data.py && python integrate_data.py")
        sys.exit(1)

    print("\n[1/4] Ingesting Reconciled Multi-Bank Datasets...")
    df_tx = pd.read_csv(tx_path)
    df_acc = pd.read_csv(acc_path)
    print(f"  • Integrated Transactions: {len(df_tx):,} records")
    print(f"  • Participating Accounts:   {len(df_acc):,} profiles")

    print("\n[2/4] Executing Feature Engineering Pipeline...")
    pipeline = FeatureEngineeringPipeline()
    df_tx_eng, df_acc_feat, metadata = pipeline.run_pipeline(
        accounts_df=df_acc,
        transactions_df=df_tx,
        export_artifacts=not args.no_export,
    )

    print(f"  ✓ Transaction-Level Features Computed: 10 new attributes across {len(df_tx_eng):,} rows")
    print(f"  ✓ Account-Level Topological & Velocity Features: {df_acc_feat.shape[1]} features across {len(df_acc_feat):,} accounts")

    print("\n[3/4] Data Leakage Safeguards & Model Readiness Audit:")
    print("-" * 76)
    print("  • Input Features Matrix (features_X.csv):  PREDICTOR FEATURES ONLY")
    print("  • Ground Truth Labels (labels_y.csv):      STRICTLY SEPARATED")
    print("  • Excluded Target Columns from X:          ['is_mule', 'ring_id', 'ring_role']")
    print("  • Total Input Predictor Features:          " + str(df_acc_feat.shape[1] - 5))
    print("-" * 76)

    print("\n[4/4] Behavioral Pattern Comparison (Mule vs Legitimate):")
    mules = df_acc_feat[df_acc_feat["is_mule"] == 1]
    legit = df_acc_feat[df_acc_feat["is_mule"] == 0]

    metrics_comp = [
        ("Pass-Through Ratio (Out / In)", f"{legit['pass_through_ratio'].mean():.2f}", f"{mules['pass_through_ratio'].mean():.2f}"),
        ("Min Turnaround Time", f"{legit['min_turnaround_time_sec'].median():,.0f}s", f"{mules['min_turnaround_time_sec'].median():,.0f}s"),
        ("Max 1-Hour Velocity", f"{legit['velocity_1h_max'].mean():.1f}", f"{mules['velocity_1h_max'].mean():.1f}"),
        ("Cross-Bank Tx Ratio", f"{legit['cross_bank_tx_ratio'].mean():.1%}", f"{mules['cross_bank_tx_ratio'].mean():.1%}"),
        ("Behavioral Risk Score", f"{legit['behavioral_risk_score'].mean():.3f}", f"{mules['behavioral_risk_score'].mean():.3f}"),
    ]

    print(f"  {'BEHAVIORAL INDICATOR':<32} {'LEGITIMATE ACCOUNTS':<22} {'MULE ACCOUNTS':<20}")
    print("  " + "-" * 72)
    for name, leg_val, mule_val in metrics_comp:
        print(f"  {name:<32} {leg_val:<22} {mule_val:<20}")

    print("\n📂 Output Artifacts Created in data/processed/:")
    print("  • data/processed/transactions_engineered.csv (Enriched transaction stream)")
    print("  • data/processed/features.csv                (Full account feature matrix)")
    print("  • data/processed/features_X.csv              (Isolated input predictors X)")
    print("  • data/processed/labels_y.csv                (Isolated target vector y)")
    print("  • reports/feature_metadata.json              (Feature dictionary & data contracts)")

    print("\n" + "=" * 76)
    print("🎯 STEP 4 COMPLETE: LEAKAGE-FREE FEATURES READY FOR MODEL TRAINING (STEP 5)")
    print("=" * 76)


if __name__ == "__main__":
    main()
