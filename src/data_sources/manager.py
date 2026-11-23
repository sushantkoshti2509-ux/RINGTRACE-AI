"""
RINGTRACE AI - Multi-Source Data Strategy & Benchmark Manager.
Manages the four data pillars:
1. Our Own 3-Bank Indian UPI Simulator (Bank A, Bank B, Bank C) - Primary
2. IBM AMLSim - Graph-based AML & known money laundering topologies
3. IBM AML-Data - Multi-bank tabular AML laundering format
4. PaySim - Mobile money synthetic fraud baseline
Ensures every source standardizes into the mandatory 5 core output files:
accounts.csv, transactions.csv, mule_rings.csv, features.csv, and risk_scores.csv.
"""

from pathlib import Path
from typing import Dict, Any, Tuple, List
import pandas as pd
import numpy as np

import config
from src.simulator.generator import UPISimulator
from src.data_sources.amlsim_loader import AMLSimAdapter
from src.data_sources.ibm_amldata_loader import IBMAMLDataLoader
from src.data_sources.paysim_loader import PaySimLoader


class MultiSourceDataManager:
    """Coordinates generation, conversion, and comparative benchmarking across all 4 data sources."""

    DATA_SOURCES = {
        "OUR_UPI_SIMULATOR": {
            "name": "Hybrid Multi-Bank UPI Engine",
            "role": "Primary Engine: Hybrid synthesis of PaySim behavior, IBM AMLSim graph topologies, and 6-bank architecture.",
            "target_ecosystem": "Multi-Bank Digital Payments (Bank A, Bank B, Bank C, Bank D)",
            "cross_bank": True,
            "patterns": ["Circular Layering (AMLSim Cycle)", "Fan-Out Splitter", "Fan-In Collector", "Cross-Bank Chain (AMLSim Stack)", "Rapid Pass-Through"],
            "strengths": "Directly models cross-bank multi-hop blindspots, PaySim amount distributions, AMLSim graphs, and sub-minute turnaround velocity.",
            "limitations": "Synthetic hybrid simulation (privacy-preserving, zero real customer PII used).",
        },
        "IBM_AMLSIM": {
            "name": "IBM AMLSim",
            "role": "Graph Benchmark: Evaluating complex graph laundering topologies.",
            "target_ecosystem": "Synthetic Global Banking",
            "cross_bank": True,
            "patterns": ["Cycle", "FanIn", "FanOut", "Bipartite", "Stack"],
            "strengths": "Well-studied in academic AML graph research; provides SAR alert labels.",
            "limitations": "A simulator engine requiring custom compilation; not configured for Indian UPI payment dynamics.",
        },
        "IBM_AMLDATA": {
            "name": "IBM AML-Data",
            "role": "Tabular Benchmark: Multi-bank cross-currency transaction patterns.",
            "target_ecosystem": "International Wire & Banking",
            "cross_bank": True,
            "patterns": ["Multi-Hop Wire Layering", "Currency Smurfing"],
            "strengths": "Captures inter-bank payments and multiple currency formats.",
            "limitations": "Tabular format with lower temporal resolution compared to real-time UPI.",
        },
        "PAYSIM": {
            "name": "PaySim (Mobile Money)",
            "role": "Baseline: Mobile money transaction fraud scoring.",
            "target_ecosystem": "African Mobile Financial Services (MFS)",
            "cross_bank": False,
            "patterns": ["Transfer to Cash-Out Pair"],
            "strengths": "Very large public Kaggle dataset; standard baseline for transaction-level fraud.",
            "limitations": "Single-institution mobile wallet; lacks cross-bank relationships and multi-hop mule rings.",
        },
    }

    def __init__(self):
        self.upi_sim = UPISimulator()
        self.amlsim_adapter = AMLSimAdapter()
        self.amldata_loader = IBMAMLDataLoader()
        self.paysim_loader = PaySimLoader()

    def generate_all_benchmark_sources(self) -> Dict[str, Any]:
        """Generates raw benchmark datasets for all external sources."""
        # 1. IBM AMLSim
        aml_acc, aml_tx, aml_alerts = self.amlsim_adapter.generate_amlsim_dataset()
        # 2. IBM AML-Data
        amldata_df = self.amldata_loader.generate_amldata_dataset()
        # 3. PaySim
        paysim_df = self.paysim_loader.generate_paysim_sample()

        return {
            "IBM_AMLSIM": {"accounts": len(aml_acc), "transactions": len(aml_tx), "alerts": len(aml_alerts)},
            "IBM_AMLDATA": {"transactions": len(amldata_df)},
            "PAYSIM": {"transactions": len(paysim_df)},
        }

    def load_and_standardize_source(
        self,
        source_key: str = "OUR_UPI_SIMULATOR",
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Loads specified data source and transforms it into the standard 3 core tables:
        (accounts_df, transactions_df, mule_rings_df)
        """
        if source_key == "IBM_AMLSIM":
            acc, tx, alerts = self.amlsim_adapter.generate_amlsim_dataset()
            return self.amlsim_adapter.convert_to_ringtrace_standard(acc, tx, alerts)
        elif source_key == "IBM_AMLDATA":
            aml_df = self.amldata_loader.generate_amldata_dataset()
            return self.amldata_loader.convert_to_ringtrace_standard(aml_df)
        elif source_key == "PAYSIM":
            p_df = self.paysim_loader.generate_paysim_sample()
            return self.paysim_loader.convert_to_ringtrace_standard(p_df)
        else:  # OUR_UPI_SIMULATOR (Default Primary)
            acc, tx, rings, _ = self.upi_sim.generate_all()
            return acc, tx, rings

    def get_source_comparison_summary(self) -> pd.DataFrame:
        """Returns comparison matrix of all 4 data sources."""
        records = []
        for key, meta in self.DATA_SOURCES.items():
            records.append({
                "Source Key": key,
                "Data Source": meta["name"],
                "Strategic Role": meta["role"],
                "Target Ecosystem": meta["target_ecosystem"],
                "Cross-Bank Visibility": "✅ Multi-Bank" if meta["cross_bank"] else "❌ Single-Entity",
                "Key Suspicious Patterns": ", ".join(meta["patterns"][:3]),
                "Key Strength": meta["strengths"],
                "Known Limitation": meta["limitations"],
            })
        return pd.DataFrame(records)
