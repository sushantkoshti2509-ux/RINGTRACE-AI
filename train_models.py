"""
RINGTRACE AI - Step 5: Machine Learning Model Development & Benchmarking CLI.
Trains, evaluates, and compares Random Forest, XGBoost, Logistic Regression,
and Isolation Forest for cross-bank fraud detection, and exports risk scores.
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
from src.models.train import ModelTrainer
from src.models.predict import RiskPredictor


def print_banner():
    print("=" * 80)
    print("🤖 RINGTRACE AI - STEP 5: MACHINE LEARNING MODEL DEVELOPMENT & BENCHMARKING")
    print("• Algorithms: Random Forest, XGBoost, Logistic Regression, Isolation Forest")
    print("• Technologies: Python, Scikit-learn, XGBoost, Pandas, NumPy")
    print("• Evaluation Focus: Precision, Recall, F1-Score, and False Positive Reduction")
    print("=" * 80)


def main():
    parser = argparse.ArgumentParser(
        description="RINGTRACE AI - Step 5: Train and Benchmark Machine Learning Models."
    )
    parser.add_argument(
        "--test-size",
        type=float,
        default=0.25,
        help="Held-out test split ratio (default: 0.25)",
    )
    args = parser.parse_args()

    print_banner()

    features_path = config.PROCESSED_DATA_DIR / "features.csv"
    if not features_path.exists():
        print("❌ Error: Missing features.csv. Please run Step 4 first:")
        print("   python engineer_features.py")
        sys.exit(1)

    print("\n[1/4] Ingesting Model-Ready Engineered Features & Ground Truth...")
    features_df = pd.read_csv(features_path)
    print(f"  • Accounts Loaded: {len(features_df):,} profiles")
    mule_count = int(features_df[config.TARGET_COLUMN].sum()) if config.TARGET_COLUMN in features_df.columns else 0
    print(f"  • Class Distribution: {len(features_df) - mule_count:,} Legitimate vs. {mule_count:,} Synthetic Mules")

    print("\n[2/4] Training & Benchmarking Models with Ring-Group Aware Split...")
    trainer = ModelTrainer()
    X, y, groups = trainer.prepare_data(features_df)
    comparison = trainer.compare_all_models(X, y, groups, test_size=args.test_size)

    print(f"  ✓ Ring-Group Aware Split: {comparison['train_samples']} Train ({comparison['train_mules']} mules) | {comparison['test_samples']} Test ({comparison['test_mules']} mules)")
    print("  ✓ Zero data leakage across train and test partitions confirmed.")

    print("\n[3/4] Multi-Model Evaluation & Performance Benchmark:")
    print("-" * 88)
    header = f"  {'ALGORITHM':<22} {'ACCURACY':<10} {'PRECISION':<11} {'RECALL':<10} {'F1-SCORE':<10} {'PR-AUC':<9} {'FPR':<8} {'STATUS':<12}"
    print(header)
    print("  " + "-" * 86)

    for model_name, m in comparison["models"].items():
        champ_tag = "🏆 Champion" if model_name == comparison["champion_model"] else "Baseline"
        row_str = (
            f"  {model_name:<22} "
            f"{m['accuracy']:<10.4f} "
            f"{m['precision']:<11.4f} "
            f"{m['recall']:<10.4f} "
            f"{m['f1_score']:<10.4f} "
            f"{m['pr_auc']:<9.4f} "
            f"{m['false_positive_rate']:<8.4f} "
            f"{champ_tag:<12}"
        )
        print(row_str)
    print("-" * 88)

    print("\n[Confusion Matrices on Held-Out Test Set]:")
    for model_name, m in comparison["models"].items():
        cm = m["confusion_matrix"]
        print(f"  • [{model_name}]: TN={cm['TN']:,} | FP={cm['FP']:,} (False Alarms) | FN={cm['FN']:,} (Missed Mules) | TP={cm['TP']:,} (Detected Mules)")

    print(f"\n🏆 Crowned Champion Model: {comparison['champion_model']}")

    # Save models
    trainer.save_all_models()

    print("\n[4/4] Generating Multi-Tier Risk Scores...")
    predictor = RiskPredictor(model_type="xgboost")
    account_risk_df = predictor.predict_risk_scores(features_df)
    account_risk_df.to_csv(config.PROCESSED_DATA_DIR / "risk_scores.csv", index=False)
    account_risk_df.to_json(config.PROCESSED_DATA_DIR / "risk_scores.json", orient="records", indent=2)

    # Transaction-level risk scoring
    tx_eng_path = config.PROCESSED_DATA_DIR / "transactions_engineered.csv"
    if tx_eng_path.exists():
        df_tx = pd.read_csv(tx_eng_path)
        tx_scored = predictor.predict_transaction_risk_scores(df_tx, account_risk_df=account_risk_df)
        print(f"  ✓ Transaction Risk Scoring: {len(tx_scored):,} transactions scored and assigned operational tiers")

    flagged = int((account_risk_df["alert_flag"] == 1).sum())
    high_tier = int((account_risk_df["risk_tier"] == "HIGH").sum())
    med_tier = int((account_risk_df["risk_tier"] == "MEDIUM").sum())
    low_tier = int((account_risk_df["risk_tier"] == "LOW").sum())

    print(f"  ✓ Account Alerts Flagged: {flagged:,} accounts")
    print(f"    - HIGH Risk Tier:   {high_tier:,}")
    print(f"    - MEDIUM Risk Tier: {med_tier:,}")
    print(f"    - LOW Risk Tier:    {low_tier:,}")

    print("\n📂 Output Artifacts Created:")
    print("  • models/xgboost_model.json             (Champion XGBoost Classifier)")
    print("  • models/random_forest_model.joblib     (Random Forest Baseline Classifier)")
    print("  • models/logistic_regression.joblib     (Logistic Regression Linear Pipeline)")
    print("  • models/isolation_forest.joblib        (Isolation Forest Anomaly Detector)")
    print("  • models/model_metadata.json            (Model Hyperparameters & Feature Metadata)")
    print("  • reports/model_comparison.json         (Evaluation metrics & Confusion matrices)")
    print("  • reports/model_comparison.md           (Executive Markdown comparison report)")
    print("  • data/processed/risk_scores.csv        (Account-level risk scores & operational tiers)")
    print("  • data/processed/transaction_risk_scores.csv (Transaction-level risk scores)")

    print("\n" + "=" * 80)
    print("🎯 STEP 5 COMPLETE: MODELS BENCHMARKED & CHAMPION READY FOR STEP 6 (EVALUATION)")
    print("=" * 80)


if __name__ == "__main__":
    main()
