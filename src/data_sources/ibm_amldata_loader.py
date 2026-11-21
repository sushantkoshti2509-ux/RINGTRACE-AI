"""
RINGTRACE AI - IBM AML-Data Ingestion & Benchmark Adapter.
References: https://github.com/IBM/AML-Data
Ingests and generates synthetic financial transaction data conforming to the
IBM AML-Data format (Timestamp, From Bank, Account, To Bank, Account, Amount Received,
Receiving Currency, Amount Paid, Payment Currency, Payment Format, Is Laundering)
and transforms it into standardized RINGTRACE account and transaction graphs.
"""

from pathlib import Path
from typing import Dict, List, Tuple, Any
import random
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

import config

BENCHMARK_AMLDATA_DIR = config.DATA_DIR / "benchmarks" / "aml_data"
BENCHMARK_AMLDATA_DIR.mkdir(parents=True, exist_ok=True)


class IBMAMLDataLoader:
    """Generates, ingests, and normalizes IBM AML-Data tabular transaction formats."""

    def __init__(self, seed: int = config.RANDOM_SEED):
        self.seed = seed
        random.seed(seed)
        np.random.seed(seed)
        self.start_time = datetime(2026, 11, 14, 8, 30, 0)

    def generate_amldata_dataset(
        self,
        num_accounts: int = 250,
        num_transactions: int = 2000,
        laundering_ratio: float = 0.08,
    ) -> pd.DataFrame:
        """
        Generates native IBM AML-Data formatted DataFrame:
        - Timestamp
        - From Bank
        - Account (Origin)
        - To Bank
        - Account.1 (Destination)
        - Amount Received
        - Receiving Currency
        - Amount Paid
        - Payment Currency
        - Payment Format (e.g. Wire, ACH, Cheque, Credit Card)
        - Is Laundering (0 or 1)
        """
        banks = ["012", "045", "089", "120"]
        account_pool = [f"ACC_{b}_{i+1:05d}" for b in banks for i in range(num_accounts // len(banks))]
        formats = ["Wire", "ACH", "Cheque", "Credit Card", "Reinvestment"]
        currencies = ["USD", "EUR", "INR"]

        laundering_rows = []
        # Generate money-laundering multi-hop pass-through sequences first
        num_laundering_target = max(3, int(num_transactions * laundering_ratio))
        mule_chains = max(1, num_laundering_target // 3)
        for c_idx in range(mule_chains):
            chain_nodes = random.sample(account_pool, k=4)
            stolen = round(random.uniform(80000, 350000), 2)
            t_base = self.start_time + timedelta(seconds=random.randint(3600, 3600 * 24 * 5))

            curr_amt = stolen
            curr_t = t_base
            for step in range(3):
                u = chain_nodes[step]
                v = chain_nodes[step + 1]
                u_b = u.split("_")[1]
                v_b = v.split("_")[1]
                curr_amt = round(curr_amt * random.uniform(0.95, 0.98), 2)
                curr_t += timedelta(minutes=random.randint(4, 20))

                laundering_rows.append({
                    "Timestamp": curr_t.strftime("%Y/%m/%d %H:%M"),
                    "From Bank": u_b,
                    "Account": u,
                    "To Bank": v_b,
                    "Account.1": v,
                    "Amount Received": curr_amt,
                    "Receiving Currency": "INR",
                    "Amount Paid": curr_amt,
                    "Payment Currency": "INR",
                    "Payment Format": "Wire",
                    "Is Laundering": 1,
                })

        # Fill the remainder with normal transactions to match num_transactions exactly
        normal_rows = []
        num_normal = max(1, num_transactions - len(laundering_rows))
        for _ in range(num_normal):
            from_acc = random.choice(account_pool)
            to_acc = random.choice(account_pool)
            while to_acc == from_acc:
                to_acc = random.choice(account_pool)

            from_bank = from_acc.split("_")[1]
            to_bank = to_acc.split("_")[1]
            amt = round(random.uniform(50, 25000), 2)
            curr = random.choice(currencies)
            t = self.start_time + timedelta(seconds=random.randint(0, 3600 * 24 * 7))

            normal_rows.append({
                "Timestamp": t.strftime("%Y/%m/%d %H:%M"),
                "From Bank": from_bank,
                "Account": from_acc,
                "To Bank": to_bank,
                "Account.1": to_acc,
                "Amount Received": amt,
                "Receiving Currency": curr,
                "Amount Paid": amt,
                "Payment Currency": curr,
                "Payment Format": random.choice(formats),
                "Is Laundering": 0,
            })

        rows = normal_rows + laundering_rows

        df = pd.DataFrame(rows).sort_values("Timestamp").reset_index(drop=True)
        # Save native file
        df.to_csv(BENCHMARK_AMLDATA_DIR / "aml_transactions.csv", index=False)
        return df

    def convert_to_ringtrace_standard(
        self,
        aml_df: pd.DataFrame,
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Converts native IBM AML-Data DataFrame into RINGTRACE format."""
        all_accounts = set(aml_df["Account"]).union(set(aml_df["Account.1"]))
        
        # Detect accounts involved in laundering
        laundering_accs = set(aml_df[aml_df["Is Laundering"] == 1]["Account"]).union(
            set(aml_df[aml_df["Is Laundering"] == 1]["Account.1"])
        )

        accounts_list = []
        for acc in all_accounts:
            parts = acc.split("_")
            b_id = f"BANK_{parts[1]}" if len(parts) > 1 else "BANK_01"
            is_mule = int(acc in laundering_accs)
            accounts_list.append({
                "account_id": acc,
                "bank_id": b_id,
                "canonical_entity_id": f"CANONICAL_{acc}",
                "profile_type": "MULE_SUSPECT" if is_mule else "STANDARD_BUSINESS",
                "account_age_days": random.randint(20, 80) if is_mule else random.randint(200, 1500),
                "initial_balance": round(random.uniform(5000, 100000), 2),
                "is_mule": is_mule,
                "ring_id": "AML_DATA_CHAIN" if is_mule else "NONE",
                "ring_role": "MULE_MEMBER" if is_mule else "LEGITIMATE",
            })

        tx_list = []
        for idx, row in aml_df.iterrows():
            tx_list.append({
                "transaction_id": f"AMLDATA_TX_{idx+1:06d}",
                "timestamp": str(row["Timestamp"]),
                "sender_account": str(row["Account"]),
                "receiver_account": str(row["Account.1"]),
                "sender_bank": f"BANK_{row['From Bank']}",
                "receiver_bank": f"BANK_{row['To Bank']}",
                "amount": float(row["Amount Paid"]),
                "transaction_type": str(row["Payment Format"]),
                "is_suspicious": int(row["Is Laundering"]),
                "ring_id": "AML_DATA_CHAIN" if row["Is Laundering"] == 1 else "NONE",
            })

        # Summary of laundering rings in AML-Data
        rings_list = [{
            "ring_id": "AML_DATA_CHAIN",
            "scenario_type": "MULTI_HOP_WIRE_LAYERING",
            "accounts": ";".join(list(laundering_accs)[:12]),
            "total_amount": float(aml_df[aml_df["Is Laundering"] == 1]["Amount Paid"].sum()),
            "hop_count": 3,
            "duration_minutes": 120,
            "cross_bank_count": int((aml_df["From Bank"] != aml_df["To Bank"]).sum()),
        }]

        return (
            pd.DataFrame(accounts_list),
            pd.DataFrame(tx_list),
            pd.DataFrame(rings_list),
        )
