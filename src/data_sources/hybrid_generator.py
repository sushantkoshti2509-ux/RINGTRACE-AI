"""
RINGTRACE AI - Hybrid Synthetic Multi-Bank Dataset Generator.
Combines empirical behavioral patterns from public benchmarks with our multi-bank engine:
1. PaySim: Realistic transaction amount distributions (log-normal), diurnal velocity patterns,
   and customer-merchant transfer dynamics.
2. IBM AMLSim: Known laundering topologies (Cycles, Fan-Out, Fan-In, Bipartite, Multi-Hop Stack),
   sub-minute turnaround velocity, and coordinated mule network structures.
3. Multi-Bank Architecture: Standardized cross-bank ledgers across synthetic institutions
   (Bank A, Bank B, Bank C, Bank D)
   with zero real-world bank names and full DPDP Act 2023 privacy safeguards.
"""

from typing import Dict, List, Tuple, Any, Optional
import random
from datetime import datetime, timedelta
from pathlib import Path
import numpy as np
import pandas as pd
from faker import Faker

import config


class HybridDatasetGenerator:
    """
    Hybrid Synthetic Dataset Generator synthesizing PaySim behavioral dynamics
    and IBM AMLSim graph laundering topologies into a unified multi-bank banking ecosystem.
    """

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

    # -------------------------------------------------------------------------
    # 1. PaySim-Derived Behavioral Distribution Samplers
    # -------------------------------------------------------------------------
    def sample_paysim_amount(self, profile: str) -> float:
        """
        Samples realistic transaction amounts using PaySim-calibrated log-normal distributions.
        """
        if profile == "MERCHANT":
            # Micro to medium retail payments (₹80 - ₹4,500)
            amt = float(np.random.lognormal(mean=6.2, sigma=0.85))
            return max(50.0, min(15000.0, round(amt, 2)))
        elif profile == "GIG_WORKER":
            # Frequent micro-earnings (₹120 - ₹2,800)
            amt = float(np.random.lognormal(mean=5.8, sigma=0.65))
            return max(40.0, min(8000.0, round(amt, 2)))
        elif profile == "HIGH_VALUE":
            # Commercial wires / NEFT (₹80,000 - ₹4,50,000)
            amt = float(np.random.uniform(75000.0, 450000.0))
            return round(amt, 2)
        elif profile == "STUDENT_FIRST_TIME":
            # Small peer transfers (₹30 - ₹1,500)
            amt = float(np.random.lognormal(mean=5.4, sigma=0.75))
            return max(30.0, min(3000.0, round(amt, 2)))
        else:
            # Standard P2P (₹150 - ₹12,000)
            amt = float(np.random.lognormal(mean=6.8, sigma=0.95))
            return max(50.0, min(25000.0, round(amt, 2)))

    def sample_diurnal_timestamp(self, day_base: datetime, is_off_hours: bool = False) -> datetime:
        """
        Samples transaction time respecting realistic circadian payment curves.
        Off-hours transactions model atypical nocturnal behavior (01:00 - 04:30 AM).
        """
        if is_off_hours:
            hour = random.randint(1, 4)
            minute = random.randint(0, 59)
            second = random.randint(0, 59)
        else:
            # PaySim peak hours: 09:00 to 22:00
            hour = int(np.random.choice(
                range(7, 24),
                p=[0.02, 0.04, 0.07, 0.08, 0.09, 0.09, 0.08, 0.08, 0.07, 0.07, 0.08, 0.08, 0.06, 0.05, 0.03, 0.01, 0.00]
            ))
            minute = random.randint(0, 59)
            second = random.randint(0, 59)

        return day_base + timedelta(hours=hour, minutes=minute, seconds=second)

    # -------------------------------------------------------------------------
    # 2. Customer Profile Generation
    # -------------------------------------------------------------------------
    def generate_customer_profile(
        self,
        bank_id: str,
        index: int,
        is_mule: bool = False,
        profile_override: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generates a privacy-preserving synthetic customer profile."""
        prefix = bank_id.replace("BANK_", "BNK_") if "BANK_" in bank_id else bank_id.split("_")[0]
        acc_id = f"{prefix}_MULE_{index:05d}" if is_mule else f"{prefix}_ACC_{index:05d}"
        cust_id = f"CUST_{prefix}_{index:05d}"

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

    # -------------------------------------------------------------------------
    # 3. IBM AMLSim Laundering Ring Synthesizer
    # -------------------------------------------------------------------------
    def generate_all(
        self,
        num_accounts: int = config.TOTAL_ACCOUNTS,
        num_rings: Optional[int] = None,
        fraud_percentage: float = 0.14,
        simulation_days: int = config.SIMULATION_DAYS,
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, Dict[str, pd.DataFrame]]:
        """
        Executes full hybrid synthetic generation:
        - PaySim-calibrated background legitimate and commercial flows
        - IBM AMLSim graph laundering archetypes (Cycles, Fan-Out, Fan-In, Bipartite, Stacks)
        - Multi-bank distribution across the 6 synthetic institutions
        """
        num_mules = max(12, int(num_accounts * fraud_percentage))
        if num_rings is not None:
            num_rings = max(1, num_rings)
        else:
            num_rings = max(4, num_mules // 5)
        mules_per_ring = max(3, num_mules // num_rings)
        actual_mules = num_rings * mules_per_ring
        num_legit = max(10, num_accounts - actual_mules)

        # 1. Generate Legitimate Customer Accounts across Banks
        accounts = []
        canonical_counter = 1000
        for i in range(num_legit):
            b_id = self.banks[i % len(self.banks)]
            acc_data = self.generate_customer_profile(bank_id=b_id, index=i + 1, is_mule=False)
            acc_data["canonical_entity_id"] = f"PAN_CANONICAL_{canonical_counter:06d}"
            canonical_counter += 1
            accounts.append(acc_data)

        # 2. Coordinated Multi-Bank Mule Rings (AMLSim Topologies)
        mule_accounts = []
        ring_transactions = []
        rings_metadata = []
        tx_counter = 1

        amlsim_archetypes = [
            "CIRCULAR_LAYERING",     # AMLSim CYCLE
            "FAN_OUT_SPLITTER",       # AMLSim FAN_OUT
            "FAN_IN_COLLECTOR",       # AMLSim FAN_IN
            "CROSS_BANK_CHAIN",       # AMLSim STACK
            "RAPID_PASS_THROUGH",     # Rapid forwarding
        ]

        for r_idx in range(num_rings):
            ring_id = f"RING_{r_idx+1:03d}"
            archetype = amlsim_archetypes[r_idx % len(amlsim_archetypes)]

            # Cross-bank bank assignment: spans across 3 to all banks
            k_banks = min(len(self.banks), random.randint(3, len(self.banks)))
            ring_bank_selection = random.sample(self.banks, k=k_banks)
            if r_idx < 3:
                ring_bank_selection = list(self.banks)  # Spans across all synthetic banks

            # Shared canonical identity pool
            num_canonical_entities = max(2, mules_per_ring - 2)
            ring_canonical_pool = [f"PAN_CANONICAL_RING_{r_idx+1:02d}_{k+1:02d}" for k in range(num_canonical_entities)]

            current_ring_accs = []
            for m_i in range(mules_per_ring):
                b_id = ring_bank_selection[m_i % len(ring_bank_selection)]
                m_acc_data = self.generate_customer_profile(
                    bank_id=b_id,
                    index=r_idx * mules_per_ring + m_i + 1,
                    is_mule=True,
                )
                m_acc_data["ring_id"] = ring_id

                if m_i == 0:
                    role = "INITIAL_RECIPIENT"
                elif m_i == mules_per_ring - 1:
                    role = "CASHOUT_COLLECTOR"
                else:
                    role = "INTERMEDIATE_LAYER"
                m_acc_data["ring_role"] = role

                if r_idx < 3 and m_i < 3:
                    m_acc_data["canonical_entity_id"] = ring_canonical_pool[0]
                else:
                    m_acc_data["canonical_entity_id"] = ring_canonical_pool[m_i % len(ring_canonical_pool)]

                current_ring_accs.append(m_acc_data)
                mule_accounts.append(m_acc_data)

            # Generate Fraudulent Multi-Bank Transfers
            ring_start_offset = random.randint(3600, 3600 * 24 * (simulation_days - 2))
            t_base = self.start_time + timedelta(seconds=ring_start_offset)
            base_stolen_amount = round(random.uniform(55000, 320000), 2)
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

            else:  # CIRCULAR_LAYERING (AMLSim Cycle)
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

        # 3. PaySim-Calibrated Legitimate Transactions
        legit_transactions = []
        merchants = [a for a in accounts if a["profile_type"] == "MERCHANT"]
        p2p_users = [a for a in accounts if a["profile_type"] != "MERCHANT"]

        for day in range(simulation_days):
            day_base = self.start_time + timedelta(days=day)

            # Pattern A: PaySim Retail Merchant Payments (Log-normal amount)
            for m in merchants:
                num_micro = random.randint(6, 16)
                for _ in range(num_micro):
                    customer = random.choice(p2p_users)
                    amt = self.sample_paysim_amount("MERCHANT")
                    tx_time = self.sample_diurnal_timestamp(day_base, is_off_hours=False)
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
                amt = self.sample_paysim_amount("REGULAR_P2P")
                tx_time = self.sample_diurnal_timestamp(day_base, is_off_hours=False)
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

            # Pattern C: High-Value Commercial Transactions
            num_high_val = max(2, len(accounts) // 50)
            for _ in range(num_high_val):
                sender, receiver = random.sample(accounts, 2)
                amt = self.sample_paysim_amount("HIGH_VALUE")
                tx_time = self.sample_diurnal_timestamp(day_base, is_off_hours=False)
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

            # Pattern D: Abnormal Off-Hours Transactions (Legitimate anomalies)
            num_abnormal = max(1, len(accounts) // 100)
            for _ in range(num_abnormal):
                sender, receiver = random.sample(p2p_users, 2)
                amt = self.sample_paysim_amount("REGULAR_P2P")
                tx_time = self.sample_diurnal_timestamp(day_base, is_off_hours=True)
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

        # 4. Bank-isolated ledgers for all synthetic institutions
        bank_ledgers = {}
        for b_id in self.banks:
            b_tx = transactions_df[
                (transactions_df["sender_bank"] == b_id) | (transactions_df["receiver_bank"] == b_id)
            ].copy()
            bank_ledgers[b_id] = b_tx

        return accounts_df, transactions_df, mule_rings_df, bank_ledgers
