"""
RINGTRACE AI - Synthetic UPI-like Transaction and Mule Ring Generator.
Simulates realistic banking ecosystems across three simulated banks (Bank A, Bank B, Bank C)
with legitimate behavioral archetypes (salaried, gig-workers, merchants, first-time users, P2P)
and coordinated mule-ring fraud scenarios (rapid pass-through, splitting, cross-bank chains, cycles).
"""

import random
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import pandas as pd
import numpy as np

import config


class UPISimulator:
    """Generates synthetic accounts and transactions for Bank A, Bank B, and Bank C."""

    def __init__(self, seed: int = config.RANDOM_SEED):
        self.seed = seed
        random.seed(seed)
        np.random.seed(seed)
        self.banks = config.SIMULATED_BANKS
        self.start_time = datetime(2026, 11, 14, 8, 0, 0)  # 7-day window

    def generate_all(
        self,
        num_accounts: int = config.TOTAL_ACCOUNTS,
        num_rings: int = config.NUM_MULE_RINGS,
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, Dict[str, pd.DataFrame]]:
        """
        Generates full synthetic environment:
        Returns:
            accounts_df: Full accounts catalog with labels
            transactions_df: Combined transaction ledger
            mule_rings_df: Mule ring ground-truth metadata
            bank_ledgers: Dict mapping 'BANK_A', 'BANK_B', 'BANK_C' to their isolated ledger
        """
        accounts = []
        canonical_counter = 1000

        # 1. Generate Legitimate Accounts
        # Reserve ~80% of accounts for legitimate archetypes
        num_legit = int(num_accounts * 0.85)
        for i in range(num_legit):
            bank_id = random.choice(self.banks)
            acc_id = f"{bank_id[:4]}_ACC_{i+1:05d}"
            canonical_entity = f"PAN_CANONICAL_{canonical_counter:06d}"
            canonical_counter += 1
            
            profile = random.choices(
                config.LEGITIMATE_PROFILES,
                weights=[0.30, 0.20, 0.20, 0.15, 0.15],
                k=1,
            )[0]
            
            # Account age varies by profile
            if profile == "STUDENT_FIRST_TIME":
                age = random.randint(5, 60)
                init_bal = round(random.uniform(500, 5000), 2)
            elif profile == "MERCHANT":
                age = random.randint(180, 1500)
                init_bal = round(random.uniform(50000, 300000), 2)
            else:
                age = random.randint(90, 1800)
                init_bal = round(random.uniform(10000, 100000), 2)

            accounts.append({
                "account_id": acc_id,
                "bank_id": bank_id,
                "canonical_entity_id": canonical_entity,
                "profile_type": profile,
                "account_age_days": age,
                "initial_balance": init_bal,
                "is_mule": 0,
                "ring_id": "NONE",
                "ring_role": "LEGITIMATE",
            })

        # 2. Generate Mule Rings and Member Accounts
        rings_metadata = []
        mule_accounts = []
        ring_transactions = []
        tx_counter = 1

        ring_archetypes = config.RING_ARCHETYPES
        for r_idx in range(num_rings):
            ring_id = f"RING_{r_idx+1:03d}"
            archetype = ring_archetypes[r_idx % len(ring_archetypes)]
            
            # Cross-bank distribution for each ring
            # A ring spans at least 2 or all 3 banks to simulate real cross-bank blindspots
            ring_bank_selection = random.sample(self.banks, k=min(len(self.banks), random.randint(2, 3)))
            
            # Number of members in ring
            if archetype == "FAN_OUT_SPLITTER":
                m_count = random.randint(4, 7)
            elif archetype == "FAN_IN_COLLECTOR":
                m_count = random.randint(4, 6)
            elif archetype == "CROSS_BANK_CHAIN":
                m_count = random.randint(3, 5)
            elif archetype == "CIRCULAR_LAYERING":
                m_count = random.randint(4, 6)
            else:  # RAPID_PASS_THROUGH
                m_count = random.randint(3, 5)

            # Cross-bank canonical identity sharing (syndicate operators maintaining accounts across multiple banks)
            num_unique_entities = max(2, m_count - 2)
            ring_canonical_pool = [f"PAN_CANONICAL_RING_{r_idx+1:02d}_{k+1:02d}" for k in range(num_unique_entities)]

            # For the first 3 rings, force a master syndicate entity spanning Bank A, Bank B, and Bank C
            if r_idx < 3:
                ring_bank_selection = ["BANK_A", "BANK_B", "BANK_C"]

            current_ring_accs = []
            for m_i in range(m_count):
                b_id = ring_bank_selection[m_i % len(ring_bank_selection)]
                m_acc_id = f"{b_id[:4]}_MULE_{r_idx+1:02d}_{m_i+1:02d}"
                # In master syndicate rings, first 3 accounts across Bank A, Bank B, Bank C share canonical entity 0
                if r_idx < 3 and m_i < 3:
                    canonical_entity = ring_canonical_pool[0]
                else:
                    canonical_entity = ring_canonical_pool[m_i % len(ring_canonical_pool)]

                # Mule accounts are often newly opened (10 to 90 days)
                age = random.randint(7, 90)
                init_bal = round(random.uniform(100, 1500), 2)

                role = "MULE_MEMBER"
                if m_i == 0:
                    role = "INITIAL_RECIPIENT"
                elif m_i == m_count - 1:
                    role = "CASHOUT_COLLECTOR"
                else:
                    role = "INTERMEDIATE_LAYER"

                acc_dict = {
                    "account_id": m_acc_id,
                    "bank_id": b_id,
                    "canonical_entity_id": canonical_entity,
                    "profile_type": "MULE_SUSPECT",
                    "account_age_days": age,
                    "initial_balance": init_bal,
                    "is_mule": 1,
                    "ring_id": ring_id,
                    "ring_role": role,
                }
                current_ring_accs.append(acc_dict)
                mule_accounts.append(acc_dict)

            # Generate Fraud Scenarios and Fast Money Movement
            # Fraud transfers happen rapidly (within minutes or a few hours)
            ring_start_offset = random.randint(3600, 3600 * 24 * 5)
            t_base = self.start_time + timedelta(seconds=ring_start_offset)
            base_stolen_amount = round(random.uniform(40000, 250000), 2)
            total_transferred = 0.0

            if archetype == "RAPID_PASS_THROUGH":
                # Linear fast chain: Acc0 -> Acc1 -> Acc2 -> Acc3
                curr_t = t_base
                curr_amt = base_stolen_amount
                for step in range(len(current_ring_accs) - 1):
                    sender = current_ring_accs[step]
                    receiver = current_ring_accs[step + 1]
                    # Cut 2-5% fee per hop (mule commission)
                    fee_cut = curr_amt * random.uniform(0.02, 0.05)
                    hop_amt = round(curr_amt - fee_cut, 2)
                    curr_amt = hop_amt
                    # Rapid turnaround: 3 to 20 minutes
                    delay_min = random.randint(3, 20)
                    curr_t += timedelta(minutes=delay_min)

                    ring_transactions.append({
                        "transaction_id": f"TX_{tx_counter:07d}",
                        "timestamp": curr_t.strftime("%Y-%m-%d %H:%M:%S"),
                        "sender_account": sender["account_id"],
                        "receiver_account": receiver["account_id"],
                        "sender_bank": sender["bank_id"],
                        "receiver_bank": receiver["bank_id"],
                        "amount": hop_amt,
                        "transaction_type": "UPI_P2P",
                        "is_suspicious": 1,
                        "ring_id": ring_id,
                    })
                    tx_counter += 1
                    total_transferred += hop_amt

            elif archetype == "FAN_OUT_SPLITTER":
                # 1 initial recipient splits funds among 3-5 sub-mules rapidly
                sender = current_ring_accs[0]
                receivers = current_ring_accs[1:]
                portion = base_stolen_amount / len(receivers)
                curr_t = t_base
                for rec in receivers:
                    jitter = random.uniform(-0.1, 0.1)
                    amt = round(portion * (1 + jitter), 2)
                    curr_t += timedelta(minutes=random.randint(1, 8))
                    ring_transactions.append({
                        "transaction_id": f"TX_{tx_counter:07d}",
                        "timestamp": curr_t.strftime("%Y-%m-%d %H:%M:%S"),
                        "sender_account": sender["account_id"],
                        "receiver_account": rec["account_id"],
                        "sender_bank": sender["bank_id"],
                        "receiver_bank": rec["bank_id"],
                        "amount": amt,
                        "transaction_type": "UPI_P2P",
                        "is_suspicious": 1,
                        "ring_id": ring_id,
                    })
                    tx_counter += 1
                    total_transferred += amt

            elif archetype == "FAN_IN_COLLECTOR":
                # Multiple intermediate mules send funds to a central cashout account
                senders = current_ring_accs[:-1]
                collector = current_ring_accs[-1]
                curr_t = t_base
                portion = base_stolen_amount / len(senders)
                for snd in senders:
                    jitter = random.uniform(-0.08, 0.08)
                    amt = round(portion * (1 + jitter), 2)
                    curr_t += timedelta(minutes=random.randint(2, 12))
                    ring_transactions.append({
                        "transaction_id": f"TX_{tx_counter:07d}",
                        "timestamp": curr_t.strftime("%Y-%m-%d %H:%M:%S"),
                        "sender_account": snd["account_id"],
                        "receiver_account": collector["account_id"],
                        "sender_bank": snd["bank_id"],
                        "receiver_bank": collector["bank_id"],
                        "amount": amt,
                        "transaction_type": "UPI_P2P",
                        "is_suspicious": 1,
                        "ring_id": ring_id,
                    })
                    tx_counter += 1
                    total_transferred += amt

            elif archetype == "CROSS_BANK_CHAIN":
                # Bank A -> Bank B -> Bank C multi-hop chain
                curr_t = t_base
                curr_amt = base_stolen_amount
                for step in range(len(current_ring_accs) - 1):
                    sender = current_ring_accs[step]
                    receiver = current_ring_accs[step + 1]
                    hop_amt = round(curr_amt * random.uniform(0.93, 0.98), 2)
                    curr_amt = hop_amt
                    curr_t += timedelta(minutes=random.randint(4, 25))
                    ring_transactions.append({
                        "transaction_id": f"TX_{tx_counter:07d}",
                        "timestamp": curr_t.strftime("%Y-%m-%d %H:%M:%S"),
                        "sender_account": sender["account_id"],
                        "receiver_account": receiver["account_id"],
                        "sender_bank": sender["bank_id"],
                        "receiver_bank": receiver["bank_id"],
                        "amount": hop_amt,
                        "transaction_type": "UPI_CROSS_BANK",
                        "is_suspicious": 1,
                        "ring_id": ring_id,
                    })
                    tx_counter += 1
                    total_transferred += hop_amt

            else:  # CIRCULAR_LAYERING
                # Money cycles through multiple accounts before final exit
                curr_t = t_base
                curr_amt = base_stolen_amount
                for step in range(len(current_ring_accs)):
                    sender = current_ring_accs[step]
                    receiver = current_ring_accs[(step + 1) % len(current_ring_accs)]
                    hop_amt = round(curr_amt * random.uniform(0.95, 0.99), 2)
                    curr_amt = hop_amt
                    curr_t += timedelta(minutes=random.randint(5, 30))
                    ring_transactions.append({
                        "transaction_id": f"TX_{tx_counter:07d}",
                        "timestamp": curr_t.strftime("%Y-%m-%d %H:%M:%S"),
                        "sender_account": sender["account_id"],
                        "receiver_account": receiver["account_id"],
                        "sender_bank": sender["bank_id"],
                        "receiver_bank": receiver["bank_id"],
                        "amount": hop_amt,
                        "transaction_type": "UPI_P2P",
                        "is_suspicious": 1,
                        "ring_id": ring_id,
                    })
                    tx_counter += 1
                    total_transferred += hop_amt

            # Record Ring Ground-truth metadata
            member_ids = [a["account_id"] for a in current_ring_accs]
            cross_bank_c = sum(
                1 for tx in ring_transactions if tx["ring_id"] == ring_id and tx["sender_bank"] != tx["receiver_bank"]
            )
            rings_metadata.append({
                "ring_id": ring_id,
                "scenario_type": archetype,
                "accounts": ";".join(member_ids),
                "total_amount": round(total_transferred, 2),
                "hop_count": len(current_ring_accs) - 1,
                "duration_minutes": random.randint(15, 180),
                "cross_bank_count": cross_bank_c,
            })

        # 3. Generate Legitimate Background Transactions
        all_accounts = accounts + mule_accounts
        legit_acc_pool = accounts
        merchants = [a for a in legit_acc_pool if a["profile_type"] == "MERCHANT"]
        p2p_users = [a for a in legit_acc_pool if a["profile_type"] != "MERCHANT"]
        legit_transactions = []

        # Generate realistic routine transactions across 7 days
        for day in range(config.SIMULATION_DAYS):
            day_date = self.start_time + timedelta(days=day)
            
            # Merchant payments (many P2P users paying merchants)
            for m in merchants:
                num_tx = random.randint(4, 15)
                for _ in range(num_tx):
                    customer = random.choice(p2p_users)
                    amt = round(random.uniform(50, 2500), 2)
                    tx_time = day_date + timedelta(
                        hours=random.randint(9, 21),
                        minutes=random.randint(0, 59),
                        seconds=random.randint(0, 59),
                    )
                    legit_transactions.append({
                        "transaction_id": f"TX_{tx_counter:07d}",
                        "timestamp": tx_time.strftime("%Y-%m-%d %H:%M:%S"),
                        "sender_account": customer["account_id"],
                        "receiver_account": m["account_id"],
                        "sender_bank": customer["bank_id"],
                        "receiver_bank": m["bank_id"],
                        "amount": amt,
                        "transaction_type": "UPI_MERCHANT",
                        "is_suspicious": 0,
                        "ring_id": "NONE",
                    })
                    tx_counter += 1

            # Routine P2P transfers
            num_p2p = len(p2p_users) * 2
            for _ in range(num_p2p):
                sender, receiver = random.sample(p2p_users, 2)
                amt = round(random.uniform(100, 8000), 2)
                tx_time = day_date + timedelta(
                    hours=random.randint(7, 23),
                    minutes=random.randint(0, 59),
                    seconds=random.randint(0, 59),
                )
                legit_transactions.append({
                    "transaction_id": f"TX_{tx_counter:07d}",
                    "timestamp": tx_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "sender_account": sender["account_id"],
                    "receiver_account": receiver["account_id"],
                    "sender_bank": sender["bank_id"],
                    "receiver_bank": receiver["bank_id"],
                    "amount": amt,
                    "transaction_type": "UPI_P2P",
                    "is_suspicious": 0,
                    "ring_id": "NONE",
                })
                tx_counter += 1

        # Combine all transactions and sort chronologically
        all_transactions = legit_transactions + ring_transactions
        all_transactions.sort(key=lambda x: x["timestamp"])

        accounts_df = pd.DataFrame(all_accounts)
        transactions_df = pd.DataFrame(all_transactions)
        mule_rings_df = pd.DataFrame(rings_metadata)

        # 4. Generate Bank-isolated ledgers (Bank A, Bank B, Bank C)
        bank_ledgers = {}
        for b_id in self.banks:
            # Each bank only sees transactions where it is sender_bank or receiver_bank
            b_tx = transactions_df[
                (transactions_df["sender_bank"] == b_id) | (transactions_df["receiver_bank"] == b_id)
            ].copy()
            bank_ledgers[b_id] = b_tx

        return accounts_df, transactions_df, mule_rings_df, bank_ledgers


def run_simulation(
    save_files: bool = True,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, Dict[str, pd.DataFrame]]:
    """Runs data simulation and optionally saves files to disk."""
    simulator = UPISimulator()
    accounts_df, transactions_df, mule_rings_df, bank_ledgers = simulator.generate_all()

    if save_files:
        accounts_df.to_csv(config.PROCESSED_DATA_DIR / "accounts.csv", index=False)
        transactions_df.to_csv(config.PROCESSED_DATA_DIR / "transactions.csv", index=False)
        mule_rings_df.to_csv(config.SYNTHETIC_DATA_DIR / "mule_rings.csv", index=False)
        
        # Save raw bank-specific ledgers
        bank_ledgers["BANK_A"].to_csv(config.RAW_DATA_DIR / "bank_a.csv", index=False)
        bank_ledgers["BANK_B"].to_csv(config.RAW_DATA_DIR / "bank_b.csv", index=False)
        bank_ledgers["BANK_C"].to_csv(config.RAW_DATA_DIR / "bank_c.csv", index=False)

    return accounts_df, transactions_df, mule_rings_df, bank_ledgers


if __name__ == "__main__":
    print("Generating simulated UPI data for Bank A, Bank B, and Bank C...")
    accs, txs, rings, ledgers = run_simulation(save_files=True)
    print(f"Generated {len(accs)} accounts ({accs['is_mule'].sum()} mules).")
    print(f"Generated {len(txs)} transactions across 7 days.")
    print(f"Generated {len(rings)} ground-truth mule rings.")
    for b_id, ldf in ledgers.items():
        print(f"  - {b_id} ledger: {len(ldf)} visible transactions.")
