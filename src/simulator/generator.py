"""
RINGTRACE AI - Realistic Multi-Bank Synthetic Banking Transaction Generator.
Simulates controllable, realistic, and privacy-preserving financial ecosystems for
Bank A, Bank B, and Bank C using Faker, Pandas, and NumPy.

Key Capabilities:
1. Multi-Bank simulation with consistent data formats across Bank A, B, and C.
2. Controllable transaction volumes, amount distributions, and fraud percentages.
3. Realistic behavioral patterns:
   - Normal transactions (P2P, merchant payments, salary deposits)
   - High-value transactions (business wire / commercial transfers)
   - Frequent micro-transactions (merchants, gig-economy workers)
   - Abnormal transactions (off-hours spikes, atypical volumes)
   - Suspicious & fraudulent rings (rapid pass-throughs, smurfing, cross-bank chains, cycles)
4. Strict data privacy: Zero real customer information used (synthetic Indian profiles via Faker).
5. Dual export formats: CSV and JSON.
"""

import sys
import json
import random
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any, Optional

import numpy as np
import pandas as pd
from faker import Faker

import config


class SyntheticBankingGenerator:
    """Configurable synthetic transaction generator for Bank A, Bank B, and Bank C."""

    def __init__(
        self,
        seed: int = config.RANDOM_SEED,
        banks: Optional[List[str]] = None,
        locale: str = "en_IN",
    ):
        self.seed = seed
        self.banks = banks or config.SIMULATED_BANKS
        random.seed(seed)
        np.random.seed(seed)
        self.fake = Faker(locale)
        self.fake.seed_instance(seed)
        self.start_time = datetime(2026, 11, 14, 8, 0, 0)

    def generate_customer_profile(
        self,
        bank_id: str,
        index: int,
        is_mule: bool = False,
        profile_override: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generates a privacy-preserving synthetic customer profile."""
        prefix = bank_id.split("_")[0]
        acc_id = f"{prefix}_MULE_{index:05d}" if is_mule else f"{prefix}_ACC_{index:05d}"
        cust_id = f"CUST_{prefix}_{index:05d}"

        # Generate realistic synthetic Indian identity
        full_name = self.fake.name()
        city = self.fake.city()

        if is_mule:
            profile = "MULE_SUSPECT"
            age_days = random.randint(7, 90)
            initial_balance = round(random.uniform(200, 2000), 2)
        else:
            profile = profile_override or random.choices(
                config.LEGITIMATE_PROFILES,
                weights=[0.30, 0.20, 0.20, 0.15, 0.15],
                k=1,
            )[0]

            if profile == "STUDENT_FIRST_TIME":
                age_days = random.randint(10, 60)
                initial_balance = round(random.uniform(500, 5000), 2)
            elif profile == "MERCHANT":
                age_days = random.randint(180, 1500)
                initial_balance = round(random.uniform(50000, 350000), 2)
            else:
                age_days = random.randint(90, 1800)
                initial_balance = round(random.uniform(10000, 120000), 2)

        return {
            "account_id": acc_id,
            "customer_id": cust_id,
            "customer_name": full_name,
            "city": city,
            "bank_id": bank_id,
            "profile_type": profile,
            "account_age_days": age_days,
            "initial_balance": initial_balance,
            "is_mule": int(is_mule),
            "ring_id": "NONE",
            "ring_role": "LEGITIMATE",
        }

    def generate_all(
        self,
        num_accounts: int = config.TOTAL_ACCOUNTS,
        num_rings: Optional[int] = None,
        fraud_percentage: float = 0.14,
        simulation_days: int = config.SIMULATION_DAYS,
        **kwargs,
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, Dict[str, pd.DataFrame]]:
        """
        Executes hybrid multi-bank synthetic generation combining:
        - PaySim lognormal payment distributions & diurnal activity curves
        - IBM AMLSim graph laundering topologies (Cycles, Fan-Out, Fan-In, Bipartite, Multi-Hop Stack)
        - Multi-Bank Architecture across realistic synthetic financial institutions
        """
        from src.data_sources.hybrid_generator import HybridDatasetGenerator
        hybrid = HybridDatasetGenerator(
            seed=self.seed,
            banks=self.banks,
        )
        return hybrid.generate_all(
            num_accounts=num_accounts,
            num_rings=num_rings,
            fraud_percentage=fraud_percentage,
            simulation_days=simulation_days,
        )

    def export_datasets(
        self,
        accounts_df: pd.DataFrame,
        transactions_df: pd.DataFrame,
        mule_rings_df: pd.DataFrame,
        bank_ledgers: Dict[str, pd.DataFrame],
        output_format: str = "both",  # "csv", "json", or "both"
        output_dir: Optional[Path] = None,
    ) -> Dict[str, List[Path]]:
        """Exports generated datasets in CSV and/or JSON formats."""
        out_root = output_dir or config.DATA_DIR
        raw_dir = out_root / "raw"
        proc_dir = out_root / "processed"
        synth_dir = out_root / "synthetic"

        raw_dir.mkdir(parents=True, exist_ok=True)
        proc_dir.mkdir(parents=True, exist_ok=True)
        synth_dir.mkdir(parents=True, exist_ok=True)

        exported_files: Dict[str, List[Path]] = {"csv": [], "json": []}

        # CSV Export
        if output_format in ["csv", "both"]:
            p_acc = proc_dir / "accounts.csv"
            p_tx = proc_dir / "transactions.csv"
            p_rings = synth_dir / "mule_rings.csv"

            accounts_df.to_csv(p_acc, index=False)
            transactions_df.to_csv(p_tx, index=False)
            mule_rings_df.to_csv(p_rings, index=False)

            exported_files["csv"].extend([p_acc, p_tx, p_rings])

            for b_id, b_df in bank_ledgers.items():
                p_bank = raw_dir / f"{b_id.lower()}.csv"
                b_df.to_csv(p_bank, index=False)
                exported_files["csv"].append(p_bank)

        # JSON Export
        if output_format in ["json", "both"]:
            pj_acc = proc_dir / "accounts.json"
            pj_tx = proc_dir / "transactions.json"
            pj_rings = synth_dir / "mule_rings.json"

            accounts_df.to_json(pj_acc, orient="records", indent=2)
            transactions_df.to_json(pj_tx, orient="records", indent=2)
            mule_rings_df.to_json(pj_rings, orient="records", indent=2)

            exported_files["json"].extend([pj_acc, pj_tx, pj_rings])

            for b_id, b_df in bank_ledgers.items():
                pj_bank = raw_dir / f"{b_id.lower()}.json"
                b_df.to_json(pj_bank, orient="records", indent=2)
                exported_files["json"].append(pj_bank)

        return exported_files


# Backward compatibility adapter for run_pipeline.py
def run_simulation(
    save_files: bool = True,
    output_format: str = "both",
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, Dict[str, pd.DataFrame]]:
    """Runs data simulation and saves files in CSV and JSON."""
    sim = SyntheticBankingGenerator()
    accs, txs, rings, ledgers = sim.generate_all()
    if save_files:
        sim.export_datasets(accs, txs, rings, ledgers, output_format=output_format)
    return accs, txs, rings, ledgers


# Reusable alias
UPISimulator = SyntheticBankingGenerator


def main():
    parser = argparse.ArgumentParser(
        description="RINGTRACE AI - Step 1: Synthetic Banking Data Generator for Bank A, B, and C."
    )
    parser.add_argument("--accounts", type=int, default=config.TOTAL_ACCOUNTS, help="Number of synthetic accounts")
    parser.add_argument("--fraud-pct", type=float, default=0.14, help="Percentage of mule/fraud accounts (0.0 to 1.0)")
    parser.add_argument("--days", type=int, default=config.SIMULATION_DAYS, help="Number of simulation days")
    parser.add_argument("--format", type=str, choices=["csv", "json", "both"], default="both", help="Export format")
    parser.add_argument("--seed", type=int, default=config.RANDOM_SEED, help="Random reproducibility seed")

    args = parser.parse_args()

    print("=" * 70)
    print("🚀 RINGTRACE AI - STEP 1: SYNTHETIC DATA GENERATOR")
    print(f"• Target Banks: Bank A, Bank B, Bank C")
    print(f"• Total Accounts: {args.accounts:,}")
    print(f"• Fraud / Mule Ratio: {args.fraud_pct:.1%}")
    print(f"• Simulation Duration: {args.days} days")
    print(f"• Export Format: {args.format.upper()}")
    print("=" * 70)

    sim = SyntheticBankingGenerator(seed=args.seed)
    accs, txs, rings, ledgers = sim.generate_all(
        num_accounts=args.accounts,
        fraud_percentage=args.fraud_pct,
        simulation_days=args.days,
    )

    exports = sim.export_datasets(accs, txs, rings, ledgers, output_format=args.format)

    print(f"\n✅ Generation complete:")
    print(f"  • Accounts: {len(accs):,} ({accs['is_mule'].sum()} mules)")
    print(f"  • Transactions: {len(txs):,} ({txs['is_suspicious'].sum()} suspicious)")
    print(f"  • Ground-Truth Rings: {len(rings)}")
    for b_id, ldf in ledgers.items():
        print(f"  • {b_id} Isolated Ledger: {len(ldf):,} transactions")

    print(f"\n📂 Exported files:")
    for fmt, file_list in exports.items():
        print(f"  [{fmt.upper()}] {len(file_list)} files generated in data/")

    print("=" * 70)


if __name__ == "__main__":
    main()
