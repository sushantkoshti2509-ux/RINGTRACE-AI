"""
RINGTRACE AI - PaySim Mobile Money Ingestion & Benchmark Adapter.
References: https://www.kaggle.com/datasets/ealaxi/paysim1
Ingests and generates PaySim synthetic mobile-money format (step, type, amount,
nameOrig, nameDest, oldbalanceOrg, newbalanceOrig, oldbalanceDest, newbalanceDest, isFraud)
and adapts it for comparative baseline evaluations against Indian UPI transaction graphs.
"""

from pathlib import Path
from typing import Dict, List, Tuple, Any
import random
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

import config

BENCHMARK_PAYSIM_DIR = config.DATA_DIR / "benchmarks" / "paysim"
BENCHMARK_PAYSIM_DIR.mkdir(parents=True, exist_ok=True)


class PaySimLoader:
    """Generates, parses, and adapts PaySim mobile-money fraud datasets."""

    def __init__(self, seed: int = config.RANDOM_SEED):
        self.seed = seed
        random.seed(seed)
        np.random.seed(seed)
        self.start_time = datetime(2026, 11, 14, 8, 0, 0)

    def generate_paysim_sample(
        self,
        num_transactions: int = 2500,
        fraud_ratio: float = 0.05,
    ) -> pd.DataFrame:
        """
        Generates native PaySim formatted DataFrame:
        - step (1 step = 1 hour)
        - type (CASH_OUT, TRANSFER, PAYMENT, CASH_IN, DEBIT)
        - amount
        - nameOrig (e.g. C123456789)
        - oldbalanceOrg
        - newbalanceOrig
        - nameDest (e.g. M987654321 for merchant, C567890123 for customer)
        - oldbalanceDest
        - newbalanceDest
        - isFraud (0 or 1)
        - isFlaggedFraud (0 or 1)
        """
        customers = [f"C{i+1:08d}" for i in range(350)]
        merchants = [f"M{i+1:08d}" for i in range(50)]

        rows = []
        num_fraud = int(num_transactions * fraud_ratio)
        num_legit = num_transactions - num_fraud

        # 1. Normal transactions
        for _ in range(num_legit):
            step = random.randint(1, 168)  # 1 week = 168 hours
            tx_type = random.choices(
                ["PAYMENT", "TRANSFER", "CASH_OUT", "CASH_IN", "DEBIT"],
                weights=[0.40, 0.20, 0.25, 0.10, 0.05],
                k=1,
            )[0]
            amt = round(random.uniform(20, 15000), 2)
            c_orig = random.choice(customers)
            c_dest = random.choice(merchants) if tx_type == "PAYMENT" else random.choice(customers)
            while c_dest == c_orig:
                c_dest = random.choice(customers)

            old_org = round(random.uniform(amt, amt + 50000), 2)
            new_org = round(old_org - amt, 2)
            old_dst = round(random.uniform(500, 20000), 2)
            new_dst = round(old_dst + amt, 2)

            rows.append({
                "step": step,
                "type": tx_type,
                "amount": amt,
                "nameOrig": c_orig,
                "oldbalanceOrg": old_org,
                "newbalanceOrig": new_org,
                "nameDest": c_dest,
                "oldbalanceDest": old_dst,
                "newbalanceDest": new_dst,
                "isFraud": 0,
                "isFlaggedFraud": 0,
            })

        # 2. PaySim Fraud Pattern (Compromised account executes TRANSFER, followed by immediate CASH_OUT)
        fraud_pairs = num_fraud // 2
        for _ in range(fraud_pairs):
            step = random.randint(10, 150)
            victim = random.choice(customers)
            mule = random.choice(customers)
            while mule == victim:
                mule = random.choice(customers)

            stolen_amt = round(random.uniform(60000, 250000), 2)

            # Step A: Transfer from victim to mule
            rows.append({
                "step": step,
                "type": "TRANSFER",
                "amount": stolen_amt,
                "nameOrig": victim,
                "oldbalanceOrg": stolen_amt,
                "newbalanceOrig": 0.0,
                "nameDest": mule,
                "oldbalanceDest": 0.0,
                "newbalanceDest": stolen_amt,
                "isFraud": 1,
                "isFlaggedFraud": int(stolen_amt > 200000),
            })

            # Step B: Immediate Cash-Out by mule
            rows.append({
                "step": step + 1,
                "type": "CASH_OUT",
                "amount": stolen_amt,
                "nameOrig": mule,
                "oldbalanceOrg": stolen_amt,
                "newbalanceOrig": 0.0,
                "nameDest": f"M{random.randint(100, 999):08d}",
                "oldbalanceDest": 10000.0,
                "newbalanceDest": 10000.0 + stolen_amt,
                "isFraud": 1,
                "isFlaggedFraud": int(stolen_amt > 200000),
            })

        df = pd.DataFrame(rows).sort_values("step").reset_index(drop=True)
        # Save native file
        df.to_csv(BENCHMARK_PAYSIM_DIR / "paysim_sample.csv", index=False)
        return df

    def convert_to_ringtrace_standard(
        self,
        paysim_df: pd.DataFrame,
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Converts native PaySim schema into RINGTRACE standard tables."""
        all_entities = set(paysim_df["nameOrig"]).union(set(paysim_df["nameDest"]))
        fraud_entities = set(paysim_df[paysim_df["isFraud"] == 1]["nameOrig"]).union(
            set(paysim_df[paysim_df["isFraud"] == 1]["nameDest"])
        )

        accounts_list = []
        for ent in all_entities:
            is_mule = int(ent in fraud_entities)
            is_merchant = ent.startswith("M")
            accounts_list.append({
                "account_id": ent,
                "bank_id": "PAYSIM_PROVIDER",
                "canonical_entity_id": f"CANONICAL_{ent}",
                "profile_type": "MERCHANT" if is_merchant else ("MULE_SUSPECT" if is_mule else "MOBILE_WALLET_USER"),
                "account_age_days": random.randint(10, 60) if is_mule else random.randint(100, 800),
                "initial_balance": 1000.0,
                "is_mule": is_mule,
                "ring_id": "PAYSIM_CASHOUT_RING" if is_mule else "NONE",
                "ring_role": "MULE_MEMBER" if is_mule else "LEGITIMATE",
            })

        tx_list = []
        for idx, row in paysim_df.iterrows():
            t_sim = self.start_time + timedelta(hours=int(row["step"]))
            tx_list.append({
                "transaction_id": f"PAYSIM_TX_{idx+1:06d}",
                "timestamp": t_sim.strftime("%Y-%m-%d %H:%M:%S"),
                "sender_account": str(row["nameOrig"]),
                "receiver_account": str(row["nameDest"]),
                "sender_bank": "PAYSIM_PROVIDER",
                "receiver_bank": "PAYSIM_PROVIDER",
                "amount": float(row["amount"]),
                "transaction_type": str(row["type"]),
                "is_suspicious": int(row["isFraud"]),
                "ring_id": "PAYSIM_CASHOUT_RING" if row["isFraud"] == 1 else "NONE",
            })

        rings_list = [{
            "ring_id": "PAYSIM_CASHOUT_RING",
            "scenario_type": "TRANSFER_TO_CASHOUT_PAIR",
            "accounts": ";".join(list(fraud_entities)[:12]),
            "total_amount": float(paysim_df[paysim_df["isFraud"] == 1]["amount"].sum()),
            "hop_count": 2,
            "duration_minutes": 60,
            "cross_bank_count": 0,
        }]

        return (
            pd.DataFrame(accounts_list),
            pd.DataFrame(tx_list),
            pd.DataFrame(rings_list),
        )
