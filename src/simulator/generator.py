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
        prefix = bank_id[:4]
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
        min_normal_amount: float = 50.0,
        max_normal_amount: float = 12000.0,
        high_value_min: float = 100000.0,
        high_value_max: float = 500000.0,
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, Dict[str, pd.DataFrame]]:
        """
        Executes full controllable synthetic generation:
        - Bank A, Bank B, Bank C account catalogs
        - Unified transaction ledger with normal, high-value, frequent, abnormal, and fraudulent patterns
        - Mule rings metadata
        - Isolated bank views for Bank A, B, and C
        """
        # 1. Calculate mules and rings sizing
        num_mules = max(10, int(num_accounts * fraud_percentage))
        if num_rings is not None:
            num_rings = max(1, num_rings)
        else:
            num_rings = max(3, num_mules // 5)
        mules_per_ring = max(2, num_mules // num_rings)
        actual_mules = num_rings * mules_per_ring
        num_legit = max(5, num_accounts - actual_mules)

        # Generate Legitimate Customer Accounts across Banks
        accounts = []
        canonical_counter = 1000
        for i in range(num_legit):
            b_id = self.banks[i % len(self.banks)]
            acc_data = self.generate_customer_profile(bank_id=b_id, index=i + 1, is_mule=False)
            acc_data["canonical_entity_id"] = f"PAN_CANONICAL_{canonical_counter:06d}"
            canonical_counter += 1
            accounts.append(acc_data)

        # 2. Generate Coordinated Mule Accounts and Fraud Rings
        # Organize mules into coordinated rings
        mule_accounts = []
        ring_transactions = []
        rings_metadata = []
        tx_counter = 1

        for r_idx in range(num_rings):
            ring_id = f"RING_{r_idx+1:03d}"
            archetype = config.RING_ARCHETYPES[r_idx % len(config.RING_ARCHETYPES)]

            # Cross-bank bank assignment: ring spans at least 2 or all 3 banks
            ring_bank_selection = random.sample(self.banks, k=min(len(self.banks), random.randint(2, 3)))
            if r_idx < 3:
                ring_bank_selection = ["BANK_A", "BANK_B", "BANK_C"]

            # Shared canonical identity pool (syndicate operators maintaining multi-bank accounts)
            num_canonical_entities = max(2, mules_per_ring - 2)
            ring_canonical_pool = [f"PAN_CANONICAL_RING_{r_idx+1:02d}_{k+1:02d}" for k in range(num_canonical_entities)]

            current_ring_accs = []
            for m_i in range(mules_per_ring):
                b_id = ring_bank_selection[m_i % len(ring_bank_selection)]
                m_acc_data = self.generate_customer_profile(bank_id=b_id, index=r_idx * mules_per_ring + m_i + 1, is_mule=True)
                m_acc_data["ring_id"] = ring_id

                # Assign roles in ring
                if m_i == 0:
                    role = "INITIAL_RECIPIENT"
                elif m_i == mules_per_ring - 1:
                    role = "CASHOUT_COLLECTOR"
                else:
                    role = "INTERMEDIATE_LAYER"
                m_acc_data["ring_role"] = role

                # Multi-bank identity linkage
                if r_idx < 3 and m_i < 3:
                    m_acc_data["canonical_entity_id"] = ring_canonical_pool[0]
                else:
                    m_acc_data["canonical_entity_id"] = ring_canonical_pool[m_i % len(ring_canonical_pool)]

                current_ring_accs.append(m_acc_data)
                mule_accounts.append(m_acc_data)

            # Generate Fraudulent Rapid Transfer Scenarios
            ring_start_offset = random.randint(3600, 3600 * 24 * (simulation_days - 2))
            t_base = self.start_time + timedelta(seconds=ring_start_offset)
            base_stolen_amount = round(random.uniform(45000, 280000), 2)
            total_transferred = 0.0

            if archetype == "RAPID_PASS_THROUGH":
                curr_t = t_base
                curr_amt = base_stolen_amount
                for step in range(len(current_ring_accs) - 1):
                    sender = current_ring_accs[step]
                    receiver = current_ring_accs[step + 1]
                    hop_amt = round(curr_amt * random.uniform(0.95, 0.98), 2)
                    curr_amt = hop_amt
                    delay_mins = random.randint(3, 18)
                    curr_t += timedelta(minutes=delay_mins)

                    ring_transactions.append({
                        "transaction_id": f"TX_{tx_counter:07d}",
                        "customer_id": sender["customer_id"],
                        "sender_account": sender["account_id"],
                        "receiver_account": receiver["account_id"],
                        "sender_bank": sender["bank_id"],
                        "receiver_bank": receiver["bank_id"],
                        "amount": hop_amt,
                        "date_time": curr_t.strftime("%Y-%m-%d %H:%M:%S"),
                        "timestamp": curr_t.strftime("%Y-%m-%d %H:%M:%S"),
                        "transaction_type": "UPI_P2P",
                        "transaction_status": "FLAGGED_SUSPICIOUS",
                        "pattern_type": "SUSPICIOUS_RAPID_PASS_THROUGH",
                        "is_suspicious": 1,
                        "ring_id": ring_id,
                    })
                    tx_counter += 1
                    total_transferred += hop_amt

            elif archetype == "FAN_OUT_SPLITTER":
                sender = current_ring_accs[0]
                receivers = current_ring_accs[1:]
                portion = base_stolen_amount / len(receivers)
                curr_t = t_base
                for rec in receivers:
                    amt = round(portion * random.uniform(0.92, 1.08), 2)
                    curr_t += timedelta(minutes=random.randint(1, 8))
                    ring_transactions.append({
                        "transaction_id": f"TX_{tx_counter:07d}",
                        "customer_id": sender["customer_id"],
                        "sender_account": sender["account_id"],
                        "receiver_account": rec["account_id"],
                        "sender_bank": sender["bank_id"],
                        "receiver_bank": rec["bank_id"],
                        "amount": amt,
                        "date_time": curr_t.strftime("%Y-%m-%d %H:%M:%S"),
                        "timestamp": curr_t.strftime("%Y-%m-%d %H:%M:%S"),
                        "transaction_type": "UPI_P2P",
                        "transaction_status": "FLAGGED_SUSPICIOUS",
                        "pattern_type": "SUSPICIOUS_FAN_OUT_SPLITTER",
                        "is_suspicious": 1,
                        "ring_id": ring_id,
                    })
                    tx_counter += 1
                    total_transferred += amt

            elif archetype == "FAN_IN_COLLECTOR":
                senders = current_ring_accs[:-1]
                collector = current_ring_accs[-1]
                portion = base_stolen_amount / len(senders)
                curr_t = t_base
                for snd in senders:
                    amt = round(portion * random.uniform(0.92, 1.08), 2)
                    curr_t += timedelta(minutes=random.randint(2, 12))
                    ring_transactions.append({
                        "transaction_id": f"TX_{tx_counter:07d}",
                        "customer_id": snd["customer_id"],
                        "sender_account": snd["account_id"],
                        "receiver_account": collector["account_id"],
                        "sender_bank": snd["bank_id"],
                        "receiver_bank": collector["bank_id"],
                        "amount": amt,
                        "date_time": curr_t.strftime("%Y-%m-%d %H:%M:%S"),
                        "timestamp": curr_t.strftime("%Y-%m-%d %H:%M:%S"),
                        "transaction_type": "UPI_P2P",
                        "transaction_status": "FLAGGED_SUSPICIOUS",
                        "pattern_type": "SUSPICIOUS_FAN_IN_COLLECTOR",
                        "is_suspicious": 1,
                        "ring_id": ring_id,
                    })
                    tx_counter += 1
                    total_transferred += amt

            elif archetype == "CROSS_BANK_CHAIN":
                curr_t = t_base
                curr_amt = base_stolen_amount
                for step in range(len(current_ring_accs) - 1):
                    sender = current_ring_accs[step]
                    receiver = current_ring_accs[step + 1]
                    hop_amt = round(curr_amt * random.uniform(0.94, 0.98), 2)
                    curr_amt = hop_amt
                    curr_t += timedelta(minutes=random.randint(4, 22))
                    ring_transactions.append({
                        "transaction_id": f"TX_{tx_counter:07d}",
                        "customer_id": sender["customer_id"],
                        "sender_account": sender["account_id"],
                        "receiver_account": receiver["account_id"],
                        "sender_bank": sender["bank_id"],
                        "receiver_bank": receiver["bank_id"],
                        "amount": hop_amt,
                        "date_time": curr_t.strftime("%Y-%m-%d %H:%M:%S"),
                        "timestamp": curr_t.strftime("%Y-%m-%d %H:%M:%S"),
                        "transaction_type": "UPI_CROSS_BANK",
                        "transaction_status": "FLAGGED_SUSPICIOUS",
                        "pattern_type": "SUSPICIOUS_CROSS_BANK_CHAIN",
                        "is_suspicious": 1,
                        "ring_id": ring_id,
                    })
                    tx_counter += 1
                    total_transferred += hop_amt

            else:  # CIRCULAR_LAYERING
                curr_t = t_base
                curr_amt = base_stolen_amount
                for step in range(len(current_ring_accs)):
                    sender = current_ring_accs[step]
                    receiver = current_ring_accs[(step + 1) % len(current_ring_accs)]
                    hop_amt = round(curr_amt * random.uniform(0.95, 0.99), 2)
                    curr_amt = hop_amt
                    curr_t += timedelta(minutes=random.randint(5, 28))
                    ring_transactions.append({
                        "transaction_id": f"TX_{tx_counter:07d}",
                        "customer_id": sender["customer_id"],
                        "sender_account": sender["account_id"],
                        "receiver_account": receiver["account_id"],
                        "sender_bank": sender["bank_id"],
                        "receiver_bank": receiver["bank_id"],
                        "amount": hop_amt,
                        "date_time": curr_t.strftime("%Y-%m-%d %H:%M:%S"),
                        "timestamp": curr_t.strftime("%Y-%m-%d %H:%M:%S"),
                        "transaction_type": "UPI_P2P",
                        "transaction_status": "FLAGGED_SUSPICIOUS",
                        "pattern_type": "SUSPICIOUS_CIRCULAR_LAYERING",
                        "is_suspicious": 1,
                        "ring_id": ring_id,
                    })
                    tx_counter += 1
                    total_transferred += hop_amt

            member_ids = [a["account_id"] for a in current_ring_accs]
            rings_metadata.append({
                "ring_id": ring_id,
                "scenario_type": archetype,
                "accounts": ";".join(member_ids),
                "total_amount": round(total_transferred, 2),
                "hop_count": len(current_ring_accs) - 1,
                "duration_minutes": random.randint(15, 180),
                "cross_bank_count": len(ring_bank_selection),
            })

        # 3. Generate Legitimate Background Patterns
        legit_transactions = []
        merchants = [a for a in accounts if a["profile_type"] == "MERCHANT"]
        p2p_users = [a for a in accounts if a["profile_type"] != "MERCHANT"]

        for day in range(simulation_days):
            day_base = self.start_time + timedelta(days=day)

            # Pattern A: Frequent Micro-Transactions (Digital Merchants & Gig Platforms)
            for m in merchants:
                num_micro = random.randint(6, 16)
                for _ in range(num_micro):
                    customer = random.choice(p2p_users)
                    amt = round(random.uniform(min_normal_amount, 2200.0), 2)
                    tx_time = day_base + timedelta(
                        hours=random.randint(9, 21),
                        minutes=random.randint(0, 59),
                        seconds=random.randint(0, 59),
                    )
                    legit_transactions.append({
                        "transaction_id": f"TX_{tx_counter:07d}",
                        "customer_id": customer["customer_id"],
                        "sender_account": customer["account_id"],
                        "receiver_account": m["account_id"],
                        "sender_bank": customer["bank_id"],
                        "receiver_bank": m["bank_id"],
                        "amount": amt,
                        "date_time": tx_time.strftime("%Y-%m-%d %H:%M:%S"),
                        "timestamp": tx_time.strftime("%Y-%m-%d %H:%M:%S"),
                        "transaction_type": "UPI_MERCHANT",
                        "transaction_status": "SUCCESS",
                        "pattern_type": "FREQUENT_MICRO_PAYMENT",
                        "is_suspicious": 0,
                        "ring_id": "NONE",
                    })
                    tx_counter += 1

            # Pattern B: Normal Peer-to-Peer Transfers
            num_p2p = len(p2p_users) * 2
            for _ in range(num_p2p):
                sender, receiver = random.sample(p2p_users, 2)
                amt = round(random.uniform(min_normal_amount, max_normal_amount), 2)
                tx_time = day_base + timedelta(
                    hours=random.randint(7, 23),
                    minutes=random.randint(0, 59),
                    seconds=random.randint(0, 59),
                )
                legit_transactions.append({
                    "transaction_id": f"TX_{tx_counter:07d}",
                    "customer_id": sender["customer_id"],
                    "sender_account": sender["account_id"],
                    "receiver_account": receiver["account_id"],
                    "sender_bank": sender["bank_id"],
                    "receiver_bank": receiver["bank_id"],
                    "amount": amt,
                    "date_time": tx_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "timestamp": tx_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "transaction_type": "UPI_P2P",
                    "transaction_status": "SUCCESS",
                    "pattern_type": "NORMAL_P2P",
                    "is_suspicious": 0,
                    "ring_id": "NONE",
                })
                tx_counter += 1

            # Pattern C: High-Value Commercial Transactions (Legitimate High-Volume)
            num_high_val = max(2, len(accounts) // 50)
            for _ in range(num_high_val):
                sender, receiver = random.sample(accounts, 2)
                amt = round(random.uniform(high_value_min, high_value_max), 2)
                tx_time = day_base + timedelta(
                    hours=random.randint(10, 16),
                    minutes=random.randint(0, 59),
                )
                legit_transactions.append({
                    "transaction_id": f"TX_{tx_counter:07d}",
                    "customer_id": sender["customer_id"],
                    "sender_account": sender["account_id"],
                    "receiver_account": receiver["account_id"],
                    "sender_bank": sender["bank_id"],
                    "receiver_bank": receiver["bank_id"],
                    "amount": amt,
                    "date_time": tx_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "timestamp": tx_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "transaction_type": "HIGH_VALUE_NEFT",
                    "transaction_status": "SUCCESS",
                    "pattern_type": "HIGH_VALUE_COMMERCIAL",
                    "is_suspicious": 0,
                    "ring_id": "NONE",
                })
                tx_counter += 1

            # Pattern D: Abnormal Off-Hours Transactions (Simulating non-fraudulent anomalies)
            num_abnormal = max(1, len(accounts) // 100)
            for _ in range(num_abnormal):
                sender, receiver = random.sample(p2p_users, 2)
                amt = round(random.uniform(500, 7500), 2)
                # Night-time off-hours: 2 AM to 4:30 AM
                tx_time = day_base + timedelta(
                    hours=random.randint(2, 4),
                    minutes=random.randint(0, 59),
                )
                legit_transactions.append({
                    "transaction_id": f"TX_{tx_counter:07d}",
                    "customer_id": sender["customer_id"],
                    "sender_account": sender["account_id"],
                    "receiver_account": receiver["account_id"],
                    "sender_bank": sender["bank_id"],
                    "receiver_bank": receiver["bank_id"],
                    "amount": amt,
                    "date_time": tx_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "timestamp": tx_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "transaction_type": "UPI_P2P",
                    "transaction_status": "SUCCESS",
                    "pattern_type": "ABNORMAL_OFF_HOURS",
                    "is_suspicious": 0,
                    "ring_id": "NONE",
                })
                tx_counter += 1

        all_accounts = accounts + mule_accounts
        all_transactions = legit_transactions + ring_transactions
        all_transactions.sort(key=lambda x: x["timestamp"])

        accounts_df = pd.DataFrame(all_accounts)
        transactions_df = pd.DataFrame(all_transactions)
        mule_rings_df = pd.DataFrame(rings_metadata)

        # 4. Bank-isolated ledgers for Bank A, Bank B, and Bank C
        bank_ledgers = {}
        for b_id in self.banks:
            b_tx = transactions_df[
                (transactions_df["sender_bank"] == b_id) | (transactions_df["receiver_bank"] == b_id)
            ].copy()
            bank_ledgers[b_id] = b_tx

        return accounts_df, transactions_df, mule_rings_df, bank_ledgers

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
