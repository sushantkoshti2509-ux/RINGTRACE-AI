"""
Feature Engineering Pipeline Coordinator for RINGTRACE AI.
Executes both transaction-level and account-level feature engineering, validates
data contracts, enforces strict ground-truth leakage isolation, and outputs
audited feature matrices and metadata reports.
"""

from typing import Dict, List, Tuple, Any, Optional
import json
from pathlib import Path
import pandas as pd
import numpy as np
import networkx as nx

import config
from src.features.transaction_features import TransactionFeatureEngine
from src.features.account_features import AccountFeatureEngine
from src.graph.builder import TransactionGraphBuilder


class FeatureEngineeringPipeline:
    """End-to-end feature engineering workflow with data leakage prevention."""

    def __init__(self):
        self.tx_engine = TransactionFeatureEngine()
        self.acc_engine = AccountFeatureEngine()
        self.graph_builder = TransactionGraphBuilder()

    def run_pipeline(
        self,
        accounts_df: pd.DataFrame,
        transactions_df: pd.DataFrame,
        export_artifacts: bool = True,
    ) -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, Any]]:
        """
        Executes complete Step 4 feature extraction:
        1. Generates enriched transaction-level features.
        2. Constructs directed transaction interaction graph.
        3. Computes multi-dimensional account-level features.
        4. Isolates input features (X) from ground truth labels (y) to prevent data leakage.
        5. Exports artifacts and comprehensive data dictionary report.
        """
        # 1. Transaction-level feature engineering
        df_tx_engineered = self.tx_engine.extract_transaction_features(transactions_df)

        # 2. Build graph for network topology
        G = self.graph_builder.build_graph(accounts_df, df_tx_engineered)

        # 3. Account-level feature extraction
        df_account_features = self.acc_engine.extract_features(G, df_tx_engineered)

        # 4. Enforce Data Leakage Separation
        # Columns strictly forbidden from entering input feature matrix X:
        LEAKAGE_TARGET_COLS = [
            "is_mule",
            "is_suspicious",
            "ring_id",
            "ring_role",
            "canonical_entity_id",
        ]

        # Feature matrix X (Predictors only)
        feature_cols = [
            col for col in df_account_features.columns
            if col not in LEAKAGE_TARGET_COLS and col != "account_id"
        ]
        df_X = df_account_features[["account_id"] + feature_cols].copy()

        # Target labels y (Separated)
        df_y = df_account_features[["account_id", "is_mule"]].copy()

        # 5. Compile Feature Metadata & Data Dictionary
        feature_metadata = self._compile_feature_metadata(df_account_features, df_tx_engineered)

        # 6. Export Artifacts
        if export_artifacts:
            config.PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
            config.REPORTS_DIR.mkdir(parents=True, exist_ok=True)

            # Export transaction-level enriched dataset
            tx_out_csv = config.PROCESSED_DATA_DIR / "transactions_engineered.csv"
            tx_out_json = config.PROCESSED_DATA_DIR / "transactions_engineered.json"
            df_tx_engineered.to_csv(tx_out_csv, index=False)
            df_tx_engineered.to_json(tx_out_json, orient="records", indent=2)

            # Export full account features
            feat_out_csv = config.PROCESSED_DATA_DIR / "features.csv"
            df_account_features.to_csv(feat_out_csv, index=False)

            # Export isolated X and y datasets (Leakage-free)
            df_X.to_csv(config.PROCESSED_DATA_DIR / "features_X.csv", index=False)
            df_y.to_csv(config.PROCESSED_DATA_DIR / "labels_y.csv", index=False)

            # Export feature metadata report
            meta_path = config.REPORTS_DIR / "feature_metadata.json"
            with open(meta_path, "w") as f:
                json.dump(feature_metadata, f, indent=2)

        return df_tx_engineered, df_account_features, feature_metadata

    def _compile_feature_metadata(
        self,
        df_acc: pd.DataFrame,
        df_tx: pd.DataFrame,
    ) -> Dict[str, Any]:
        """Compiles data dictionary and summary statistics for all engineered features."""
        metadata = {
            "pipeline_stage": "Step 4: Feature Engineering and Transaction Pattern Analysis",
            "total_accounts_profiled": len(df_acc),
            "total_transactions_enriched": len(df_tx),
            "data_leakage_safeguards": {
                "ground_truth_isolated": True,
                "isolated_columns": ["is_mule", "ring_id", "ring_role"],
                "exported_feature_matrix": "features_X.csv",
                "exported_target_labels": "labels_y.csv",
            },
            "engineered_features_catalog": {
                # Transaction-Level Features
                "time_gap_seconds": {
                    "level": "transaction",
                    "category": "Temporal Pattern",
                    "description": "Seconds elapsed since sender previous transaction",
                    "mean": float(df_tx["time_gap_seconds"].mean()),
                    "median": float(df_tx["time_gap_seconds"].median()),
                },
                "is_off_hours": {
                    "level": "transaction",
                    "category": "Temporal Pattern",
                    "description": "Binary flag for transactions between 11:00 PM and 5:59 AM",
                    "rate": float(df_tx["is_off_hours"].mean()),
                },
                "is_high_value": {
                    "level": "transaction",
                    "category": "Monetary Anomaly",
                    "description": "Binary flag for unusually large transactions (>= ₹50,000 or 2.5x historical)",
                    "rate": float(df_tx["is_high_value"].mean()),
                },
                "is_cross_bank": {
                    "level": "transaction",
                    "category": "Inter-Bank Flow",
                    "description": "Binary flag for inter-bank transactions",
                    "rate": float(df_tx["is_cross_bank"].mean()),
                },
                "velocity_score": {
                    "level": "transaction",
                    "category": "Velocity Metric",
                    "description": "Normalized speed score combining frequency and short time gaps",
                    "mean": float(df_tx["velocity_score"].mean()),
                },
                "transaction_risk_indicator": {
                    "level": "transaction",
                    "category": "Behavioral Risk",
                    "description": "Composite heuristic score for transaction suspicion",
                    "mean": float(df_tx["transaction_risk_indicator"].mean()),
                },
                # Account-Level Features
                "tx_frequency_total": {
                    "level": "account",
                    "category": "Volume",
                    "description": "Total combined inbound and outbound transactions",
                    "mean": float(df_acc["tx_frequency_total"].mean()),
                    "max": int(df_acc["tx_frequency_total"].max()),
                },
                "pass_through_ratio": {
                    "level": "account",
                    "category": "Mule Indicator",
                    "description": "Ratio of total money forwarded to total money received",
                    "mean": float(df_acc["pass_through_ratio"].mean()),
                    "mule_mean": float(df_acc[df_acc["is_mule"] == 1]["pass_through_ratio"].mean()) if (df_acc["is_mule"] == 1).any() else 0.0,
                },
                "min_turnaround_time_sec": {
                    "level": "account",
                    "category": "Temporal Velocity",
                    "description": "Minimum seconds between credit receipt and debit transfer",
                    "median": float(df_acc["min_turnaround_time_sec"].median()),
                    "mule_median": float(df_acc[df_acc["is_mule"] == 1]["min_turnaround_time_sec"].median()) if (df_acc["is_mule"] == 1).any() else 0.0,
                },
                "cross_bank_tx_ratio": {
                    "level": "account",
                    "category": "Inter-Bank Flow",
                    "description": "Fraction of account transactions crossing bank boundaries",
                    "mean": float(df_acc["cross_bank_tx_ratio"].mean()),
                },
                "behavioral_risk_score": {
                    "level": "account",
                    "category": "Behavioral Risk",
                    "description": "Composite heuristic anomaly score",
                    "mean": float(df_acc["behavioral_risk_score"].mean()),
                    "mule_mean": float(df_acc[df_acc["is_mule"] == 1]["behavioral_risk_score"].mean()) if (df_acc["is_mule"] == 1).any() else 0.0,
                },
            },
        }
        return metadata
