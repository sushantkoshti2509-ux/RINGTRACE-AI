"""
RINGTRACE AI - Master End-to-End Execution Pipeline.
Orchestrates:
1. Multi-bank synthetic transaction simulation (Bank A, Bank B, Bank C)
2. Data cleaning, integrity validation, and ledger standardization
3. Directed transaction graph construction with NetworkX
4. Graph topology and temporal velocity feature extraction
5. Group-aware XGBoost model training and threshold calibration
6. Account risk scoring and operational risk tiering
7. Candidate mule ring detection and network topology classification
8. SHAP feature attribution and multi-modal reason code synthesis
9. Private Set Intersection (PSI) cross-bank matching demonstration
10. Comprehensive model benchmarking and comparative baseline evaluation (A vs B vs C)
"""

import sys
import json
import time
from pathlib import Path
import pandas as pd
import numpy as np

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

import config
from src.simulator.generator import run_simulation
from src.preprocessing.clean import DataPreprocessor
from src.graph.builder import TransactionGraphBuilder
from src.graph.features import GraphFeatureEngine
from src.graph.ring_detection import RingDetectionEngine
from src.models.train import ModelTrainer
from src.models.predict import RiskPredictor
from src.models.evaluate import SystemEvaluator
from src.explain.shap_explainer import ExplainabilityEngine
from src.explain.reason_codes import ReasonCodeGenerator
from src.privacy.psi_demo import PSICoordinator


def run_full_pipeline(verbose: bool = True):
    """Executes the complete RINGTRACE AI pipeline from end to end."""
    start_time = time.time()
    print("=" * 75)
    print("🚀 STARTING RINGTRACE AI END-TO-END PIPELINE")
    print("=" * 75)

    # ---------------------------------------------------------
    # Step 1: Synthetic Data Generation
    # ---------------------------------------------------------
    print("\n[Step 1/10] Simulating 3-Bank UPI Ecosystem (Bank A, Bank B, Bank C)...")
    accounts_df, transactions_df, mule_rings_df, bank_ledgers = run_simulation(save_files=True)
    print(f"  ✓ Created {len(accounts_df)} accounts ({accounts_df['is_mule'].sum()} synthetic mules).")
    print(f"  ✓ Created {len(transactions_df)} transactions across 7 days.")
    print(f"  ✓ Created {len(mule_rings_df)} ground-truth mule rings.")

    # ---------------------------------------------------------
    # Step 2: Preprocessing and Validation
    # ---------------------------------------------------------
    print("\n[Step 2/10] Cleaning and Validating Data...")
    cleaner = DataPreprocessor()
    accounts_clean, transactions_clean, val_report = cleaner.run_cleaning_pipeline(
        accounts_df, transactions_df
    )
    print(f"  ✓ Accounts schema valid: {val_report['accounts_valid']}")
    print(f"  ✓ Transactions schema valid: {val_report['transactions_valid']}")

    # ---------------------------------------------------------
    # Step 3: Directed Graph Construction
    # ---------------------------------------------------------
    print("\n[Step 3/10] Constructing Directed Transaction Graph (NetworkX)...")
    graph_builder = TransactionGraphBuilder()
    G = graph_builder.build_graph(accounts_clean, transactions_clean)
    print(f"  ✓ Graph Nodes: {G.number_of_nodes()}, Directed Edges: {G.number_of_edges()}")

    # ---------------------------------------------------------
    # Step 4: Graph & Temporal Feature Extraction
    # ---------------------------------------------------------
    print("\n[Step 4/10] Extracting Network Topology & Temporal Features...")
    feature_engine = GraphFeatureEngine()
    features_df = feature_engine.extract_features(G, transactions_clean)
    features_path = config.PROCESSED_DATA_DIR / "features.csv"
    features_df.to_csv(features_path, index=False)
    print(f"  ✓ Computed {features_df.shape[1]} features for {len(features_df)} accounts.")
    print(f"  ✓ Saved features to: {features_path}")

    # ---------------------------------------------------------
    # Step 5: Model Training with Group-Aware Split
    # ---------------------------------------------------------
    print("\n[Step 5/10] Training XGBoost with Ring Group-Aware Stratification...")
    trainer = ModelTrainer()
    X, y, groups = trainer.prepare_data(features_df)
    model, train_meta, (X_train, X_test, y_train, y_test) = trainer.train_model(X, y, groups)
    trainer.save(model)
    print(f"  ✓ Trained XGBoost on {len(X_train)} accounts, held-out test: {len(X_test)} accounts.")
    print(f"  ✓ Handled class imbalance with scale_pos_weight = {train_meta['scale_pos_weight']}.")
    print(f"  ✓ Calibrated alert decision threshold: {train_meta['optimal_threshold']:.4f}")

    # ---------------------------------------------------------
    # Step 6: Account Risk Scoring
    # ---------------------------------------------------------
    print("\n[Step 6/10] Generating Account Risk Scores and Operational Tiers...")
    predictor = RiskPredictor()
    risk_scores_df = predictor.predict_risk_scores(features_df)
    risk_scores_path = config.PROCESSED_DATA_DIR / "risk_scores.csv"
    risk_scores_df.to_csv(risk_scores_path, index=False)

    flagged_count = (risk_scores_df["alert_flag"] == 1).sum()
    high_count = (risk_scores_df["risk_tier"] == "HIGH").sum()
    medium_count = (risk_scores_df["risk_tier"] == "MEDIUM").sum()
    print(f"  ✓ Total Flagged Accounts (Alerts): {flagged_count}")
    print(f"    - HIGH Risk Tiers: {high_count}")
    print(f"    - MEDIUM Risk Tiers: {medium_count}")
    print(f"  ✓ Saved risk scores to: {risk_scores_path}")

    # ---------------------------------------------------------
    # Step 7: Candidate Mule Ring Detection
    # ---------------------------------------------------------
    print("\n[Step 7/10] Discovering Candidate Suspicious Networks (Rings)...")
    ring_engine = RingDetectionEngine(risk_threshold=train_meta["optimal_threshold"] * 0.8)
    candidate_rings = ring_engine.discover_candidate_rings(G, risk_scores_df)
    ring_eval = ring_engine.evaluate_detected_rings(candidate_rings, mule_rings_df)
    
    # Save candidate rings
    with open(config.REPORTS_DIR / "candidate_rings.json", "w") as f:
        json.dump(candidate_rings, f, indent=2)

    print(f"  ✓ Discovered {len(candidate_rings)} candidate mule rings.")
    print(f"  ✓ Matched Ground Truth Rings: {ring_eval['matched_ground_truth_rings']}/{ring_eval['total_ground_truth_rings']}")
    print(f"  ✓ Ring-Level Precision: {ring_eval['ring_precision']:.4f}, Recall: {ring_eval['ring_recall']:.4f}, F1: {ring_eval['ring_f1']:.4f}")

    # ---------------------------------------------------------
    # Step 8: SHAP Explainability & Multi-Modal Reason Codes
    # ---------------------------------------------------------
    print("\n[Step 8/10] Computing SHAP Explanations & Plain-Language Reason Codes...")
    explainer = ExplainabilityEngine(model=model)
    reason_gen = ReasonCodeGenerator()

    # Pre-align features for fast lookup
    feat_lookup = features_df.set_index("account_id")
    risk_lookup = risk_scores_df.set_index("account_id")

    alerts_list = []
    # Generate explanations for all flagged accounts
    flagged_ids = risk_scores_df[risk_scores_df["alert_flag"] == 1]["account_id"].tolist()
    for acc_id in flagged_ids:
        row_feat = feat_lookup.loc[acc_id]
        row_risk = risk_lookup.loc[acc_id]
        shap_res = explainer.explain_account(row_feat, top_k=4)
        evidence = reason_gen.generate_account_evidence(
            account_id=acc_id,
            features_row={**row_feat.to_dict(), **row_risk.to_dict()},
            shap_explanation=shap_res,
            G=G,
        )
        alerts_list.append(evidence)

    alerts_path = config.REPORTS_DIR / "alerts.json"
    with open(alerts_path, "w") as f:
        json.dump(alerts_list, f, indent=2)
    print(f"  ✓ Generated SHAP & Graph evidence explanations for {len(alerts_list)} alerts.")
    print(f"  ✓ Saved alerts to: {alerts_path}")

    # ---------------------------------------------------------
    # Step 9: Private Set Intersection (PSI) Demonstration
    # ---------------------------------------------------------
    print("\n[Step 9/10] Running Private Set Intersection (PSI) Protocol across 3 Banks...")
    psi_coordinator = PSICoordinator()
    psi_results = psi_coordinator.run_three_bank_psi(
        risk_scores_df=risk_scores_df,
        accounts_df=accounts_clean,
        threshold=train_meta["optimal_threshold"],
    )
    psi_path = config.REPORTS_DIR / "psi_results.json"
    with open(psi_path, "w") as f:
        json.dump(psi_results, f, indent=2)

    print(f"  ✓ Bank A Candidate Suspects: {psi_results['bank_a_candidates']}")
    print(f"  ✓ Bank B Candidate Suspects: {psi_results['bank_b_candidates']}")
    print(f"  ✓ Bank C Candidate Suspects: {psi_results['bank_c_candidates']}")
    print(f"  ✓ Pairwise Matches: {psi_results['pairwise_matches']}")
    print(f"  ✓ 3-Way Common Suspicious Entities: {psi_results['three_way_intersection_count']}")

    # ---------------------------------------------------------
    # Step 10: Evaluation & Benchmarking (Experiments A vs B vs C)
    # ---------------------------------------------------------
    print("\n[Step 10/10] Executing Evaluation & Comparative Baselines (A vs B vs C)...")
    evaluator = SystemEvaluator()
    overall_metrics = evaluator.evaluate_predictions(
        y_true=risk_scores_df["is_mule_ground_truth"],
        y_probs=risk_scores_df["risk_score"],
        threshold=train_meta["optimal_threshold"],
    )
    profile_metrics = evaluator.evaluate_by_profile(risk_scores_df)
    comparative_results = evaluator.run_comparative_experiments(
        accounts_df=accounts_clean,
        transactions_df=transactions_clean,
        features_df=features_df,
        risk_scores_df=risk_scores_df,
    )

    # Save metrics JSON
    full_metrics = {
        "overall_performance": overall_metrics,
        "ring_level_detection": ring_eval,
        "profile_false_positive_analysis": profile_metrics,
        "comparative_experiments": comparative_results,
        "pipeline_execution_time_sec": round(time.time() - start_time, 2),
    }
    with open(config.REPORTS_DIR / "metrics.json", "w") as f:
        json.dump(full_metrics, f, indent=2)

    # Generate and save Markdown Report
    report_md = evaluator.generate_markdown_report(
        overall_metrics=overall_metrics,
        profile_metrics=profile_metrics,
        comparative_results=comparative_results,
        ring_metrics=ring_eval,
    )
    with open(config.REPORTS_DIR / "evaluation_report.md", "w") as f:
        f.write(report_md)

    print(f"  ✓ Precision: {overall_metrics['precision']:.4f}, Recall: {overall_metrics['recall']:.4f}, F1: {overall_metrics['f1_score']:.4f}")
    print(f"  ✓ False Positive Rate (FPR): {overall_metrics['false_positive_rate']:.4f}")
    print(f"  ✓ PR-AUC: {overall_metrics['pr_auc']:.4f}, ROC-AUC: {overall_metrics['roc_auc']:.4f}")
    print(f"  ✓ Generated evaluation report at: {config.REPORTS_DIR / 'evaluation_report.md'}")

    elapsed = time.time() - start_time
    print("\n" + "=" * 75)
    print(f"✅ PIPELINE SUCCESSFULLY COMPLETED IN {elapsed:.2f} SECONDS")
    print("=" * 75)


if __name__ == "__main__":
    run_full_pipeline()
