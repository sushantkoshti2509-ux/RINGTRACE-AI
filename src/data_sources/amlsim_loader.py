"""
RINGTRACE AI - IBM AMLSim Ingestion & Benchmark Adapter.
References: https://github.com/IBM/AMLSim
Generates and parses IBM AMLSim synthetic banking transaction graphs with known
money laundering alert patterns: Cycle, FanIn, FanOut, Bipartite, and Stack.
Converts AMLSim schema into RINGTRACE standard multi-bank format.
"""

from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
import random
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

import config

BENCHMARK_AMLSIM_DIR = config.DATA_DIR / "benchmarks" / "amlsim"
BENCHMARK_AMLSIM_DIR.mkdir(parents=True, exist_ok=True)


class AMLSimAdapter:
    """Generates, ingests, and adapts IBM AMLSim synthetic transaction topologies."""

    def __init__(self, seed: int = config.RANDOM_SEED):
        self.seed = seed
        random.seed(seed)
        np.random.seed(seed)
        self.start_time = datetime(2026, 11, 14, 9, 0, 0)

    def generate_amlsim_dataset(
        self,
        num_accounts: int = 300,
        num_alert_patterns: int = 12,
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Generates synthetic data matching native IBM AMLSim schema:
        - accounts.csv: ACCOUNT_ID,CUSTOMER_ID,INIT_BALANCE,START_DATE,END_DATE,BANK_ID,IS_SAR,TX_BEHAVIOR_ID
        - transactions.csv: TX_ID,SENDER_ACCOUNT_ID,RECEIVER_ACCOUNT_ID,TX_TYPE,TX_AMOUNT,TIMESTAMP,IS_SAR,ALERT_ID
        - alertPatterns.csv: ALERT_ID,ALERT_TYPE,IS_SAR,MODEL_ID,SCHEDULE_ID,START_STEP,END_STEP,TOTAL_AMOUNT,COUNT
        """
        banks = ["AML_BANK_01", "AML_BANK_02", "AML_BANK_03"]
        accounts = []
        transactions = []
        alert_patterns = []

        # 1. Normal Accounts
        for i in range(num_accounts):
            acc_id = f"AML_ACC_{i+1:05d}"
            b_id = random.choice(banks)
            init_bal = round(random.uniform(5000, 200000), 2)
            accounts.append({
                "ACCOUNT_ID": acc_id,
                "CUSTOMER_ID": f"CUST_{i+1:05d}",
                "INIT_BALANCE": init_bal,
                "START_DATE": "2026-01-01",
                "END_DATE": "2026-12-31",
                "BANK_ID": b_id,
                "IS_SAR": False,
                "TX_BEHAVIOR_ID": "NORMAL_P2P",
            })

        tx_id_counter = 1
        account_df = pd.DataFrame(accounts)
        acc_ids = account_df["ACCOUNT_ID"].tolist()

        # 2. Normal Background Transactions
        for _ in range(num_accounts * 8):
            src, dst = random.sample(acc_ids, 2)
            amt = round(random.uniform(100, 15000), 2)
            step_offset = random.randint(0, 3600 * 24 * 7)
            t = self.start_time + timedelta(seconds=step_offset)

            transactions.append({
                "TX_ID": f"AML_TX_{tx_id_counter:07d}",
                "SENDER_ACCOUNT_ID": src,
                "RECEIVER_ACCOUNT_ID": dst,
                "TX_TYPE": "TRANSFER",
                "TX_AMOUNT": amt,
                "TIMESTAMP": t.strftime("%Y-%m-%d %H:%M:%S"),
                "IS_SAR": False,
                "ALERT_ID": -1,
            })
            tx_id_counter += 1

        # 3. Known AMLSim Laundering Patterns (SAR = Suspicious Activity Report)
        pattern_types = ["CYCLE", "FAN_IN", "FAN_OUT", "BIPARTITE", "STACK"]
        sar_account_ids = set()

        for a_idx in range(num_alert_patterns):
            alert_id = a_idx + 1
            p_type = pattern_types[a_idx % len(pattern_types)]
            pattern_accs = random.sample(acc_ids, k=random.randint(3, 6))
            sar_account_ids.update(pattern_accs)
            
            p_start_offset = random.randint(3600, 3600 * 24 * 4)
            curr_t = self.start_time + timedelta(seconds=p_start_offset)
            base_amt = round(random.uniform(50000, 300000), 2)
            total_amt = 0.0
            tx_count = 0

            if p_type == "CYCLE":
                # A -> B -> C -> A
                for s in range(len(pattern_accs)):
                    u = pattern_accs[s]
                    v = pattern_accs[(s + 1) % len(pattern_accs)]
                    hop_amt = round(base_amt * random.uniform(0.95, 0.99), 2)
                    curr_t += timedelta(minutes=random.randint(5, 30))
                    transactions.append({
                        "TX_ID": f"AML_TX_{tx_id_counter:07d}",
                        "SENDER_ACCOUNT_ID": u,
                        "RECEIVER_ACCOUNT_ID": v,
                        "TX_TYPE": "TRANSFER",
                        "TX_AMOUNT": hop_amt,
                        "TIMESTAMP": curr_t.strftime("%Y-%m-%d %H:%M:%S"),
                        "IS_SAR": True,
                        "ALERT_ID": alert_id,
                    })
                    tx_id_counter += 1
                    total_amt += hop_amt
                    tx_count += 1

            elif p_type == "FAN_OUT":
                # 1 Sender -> Multiple Receivers
                src = pattern_accs[0]
                receivers = pattern_accs[1:]
                portion = base_amt / len(receivers)
                for rec in receivers:
                    amt = round(portion * random.uniform(0.90, 1.10), 2)
                    curr_t += timedelta(minutes=random.randint(2, 10))
                    transactions.append({
                        "TX_ID": f"AML_TX_{tx_id_counter:07d}",
                        "SENDER_ACCOUNT_ID": src,
                        "RECEIVER_ACCOUNT_ID": rec,
                        "TX_TYPE": "TRANSFER",
                        "TX_AMOUNT": amt,
                        "TIMESTAMP": curr_t.strftime("%Y-%m-%d %H:%M:%S"),
                        "IS_SAR": True,
                        "ALERT_ID": alert_id,
                    })
                    tx_id_counter += 1
                    total_amt += amt
                    tx_count += 1

            elif p_type == "FAN_IN":
                # Multiple Senders -> 1 Receiver
                dst = pattern_accs[-1]
                senders = pattern_accs[:-1]
                portion = base_amt / len(senders)
                for snd in senders:
                    amt = round(portion * random.uniform(0.90, 1.10), 2)
                    curr_t += timedelta(minutes=random.randint(2, 10))
                    transactions.append({
                        "TX_ID": f"AML_TX_{tx_id_counter:07d}",
                        "SENDER_ACCOUNT_ID": snd,
                        "RECEIVER_ACCOUNT_ID": dst,
                        "TX_TYPE": "TRANSFER",
                        "TX_AMOUNT": amt,
                        "TIMESTAMP": curr_t.strftime("%Y-%m-%d %H:%M:%S"),
                        "IS_SAR": True,
                        "ALERT_ID": alert_id,
                    })
                    tx_id_counter += 1
                    total_amt += amt
                    tx_count += 1

            else:  # STACK / BIPARTITE
                # Multi-hop layering chain
                curr_amt = base_amt
                for s in range(len(pattern_accs) - 1):
                    u = pattern_accs[s]
                    v = pattern_accs[s + 1]
                    curr_amt = round(curr_amt * random.uniform(0.93, 0.98), 2)
                    curr_t += timedelta(minutes=random.randint(5, 25))
                    transactions.append({
                        "TX_ID": f"AML_TX_{tx_id_counter:07d}",
                        "SENDER_ACCOUNT_ID": u,
                        "RECEIVER_ACCOUNT_ID": v,
                        "TX_TYPE": "TRANSFER",
                        "TX_AMOUNT": curr_amt,
                        "TIMESTAMP": curr_t.strftime("%Y-%m-%d %H:%M:%S"),
                        "IS_SAR": True,
                        "ALERT_ID": alert_id,
                    })
                    tx_id_counter += 1
                    total_amt += curr_amt
                    tx_count += 1

            alert_patterns.append({
                "ALERT_ID": alert_id,
                "ALERT_TYPE": p_type,
                "IS_SAR": True,
                "MODEL_ID": f"MODEL_{p_type}",
                "SCHEDULE_ID": 1,
                "START_STEP": p_start_offset,
                "END_STEP": p_start_offset + (tx_count * 1800),
                "TOTAL_AMOUNT": round(total_amt, 2),
                "COUNT": tx_count,
                "ACCOUNTS": ";".join(pattern_accs),
            })

        # Update IS_SAR in accounts
        for acc in accounts:
            if acc["ACCOUNT_ID"] in sar_account_ids:
                acc["IS_SAR"] = True
                acc["TX_BEHAVIOR_ID"] = "AML_SAR_SUSPECT"

        amlsim_accs = pd.DataFrame(accounts)
        amlsim_txs = pd.DataFrame(transactions).sort_values("TIMESTAMP").reset_index(drop=True)
        amlsim_alerts = pd.DataFrame(alert_patterns)

        # Save native AMLSim files
        amlsim_accs.to_csv(BENCHMARK_AMLSIM_DIR / "accounts.csv", index=False)
        amlsim_txs.to_csv(BENCHMARK_AMLSIM_DIR / "transactions.csv", index=False)
        amlsim_alerts.to_csv(BENCHMARK_AMLSIM_DIR / "alertPatterns.csv", index=False)

        return amlsim_accs, amlsim_txs, amlsim_alerts

    def convert_to_ringtrace_standard(
        self,
        amlsim_accs: pd.DataFrame,
        amlsim_txs: pd.DataFrame,
        amlsim_alerts: pd.DataFrame,
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Converts native IBM AMLSim schema into RINGTRACE standard:
        - accounts.csv
        - transactions.csv
        - mule_rings.csv
        """
        # Bank mapping
        bank_map = dict(zip(amlsim_accs["ACCOUNT_ID"], amlsim_accs["BANK_ID"]))

        # Convert accounts
        ringtrace_accs = []
        for _, row in amlsim_accs.iterrows():
            is_sar = int(row["IS_SAR"])
            ringtrace_accs.append({
                "account_id": str(row["ACCOUNT_ID"]),
                "bank_id": str(row["BANK_ID"]),
                "canonical_entity_id": f"CANONICAL_{row['CUSTOMER_ID']}",
                "profile_type": "MULE_SUSPECT" if is_sar else "NORMAL_P2P",
                "account_age_days": random.randint(15, 60) if is_sar else random.randint(180, 1200),
                "initial_balance": float(row["INIT_BALANCE"]),
                "is_mule": is_sar,
                "ring_id": f"AML_PATTERN_{row['ALERT_ID']}" if "ALERT_ID" in row and row["ALERT_ID"] != -1 else "NONE",
                "ring_role": "MULE_MEMBER" if is_sar else "LEGITIMATE",
            })

        # Convert transactions
        ringtrace_txs = []
        for _, row in amlsim_txs.iterrows():
            src = str(row["SENDER_ACCOUNT_ID"])
            dst = str(row["RECEIVER_ACCOUNT_ID"])
            ringtrace_txs.append({
                "transaction_id": str(row["TX_ID"]),
                "timestamp": str(row["TIMESTAMP"]),
                "sender_account": src,
                "receiver_account": dst,
                "sender_bank": bank_map.get(src, "AML_BANK_01"),
                "receiver_bank": bank_map.get(dst, "AML_BANK_02"),
                "amount": float(row["TX_AMOUNT"]),
                "transaction_type": str(row["TX_TYPE"]),
                "is_suspicious": int(row["IS_SAR"]),
                "ring_id": f"AML_PATTERN_{row['ALERT_ID']}" if row["ALERT_ID"] != -1 else "NONE",
            })

        # Convert alertPatterns into mule_rings
        ringtrace_rings = []
        for _, row in amlsim_alerts.iterrows():
            ringtrace_rings.append({
                "ring_id": f"AML_PATTERN_{row['ALERT_ID']}",
                "scenario_type": f"AML_{row['ALERT_TYPE']}",
                "accounts": str(row["ACCOUNTS"]),
                "total_amount": float(row["TOTAL_AMOUNT"]),
                "hop_count": int(row["COUNT"]) - 1,
                "duration_minutes": int((row["END_STEP"] - row["START_STEP"]) / 60),
                "cross_bank_count": int(row["COUNT"]) - 1,
            })

        return (
            pd.DataFrame(ringtrace_accs),
            pd.DataFrame(ringtrace_txs),
            pd.DataFrame(ringtrace_rings),
        )
