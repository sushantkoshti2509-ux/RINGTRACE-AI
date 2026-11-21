"""
RINGTRACE AI - Directed Transaction Graph Builder.
Constructs NetworkX directed graphs from transaction and account ledgers.
Supports both unified cross-bank graphs and isolated single-bank views.
"""

from typing import Optional, List
import pandas as pd
import networkx as nx


class TransactionGraphBuilder:
    """Builds and manages directed financial transaction graphs using NetworkX."""

    def __init__(self):
        pass

    def build_graph(
        self,
        accounts_df: pd.DataFrame,
        transactions_df: pd.DataFrame,
        bank_filter: Optional[str] = None,
    ) -> nx.DiGraph:
        """
        Builds a directed graph.
        If bank_filter is provided (e.g. 'BANK_A'), only transactions where
        sender_bank == bank_filter OR receiver_bank == bank_filter are included.
        """
        G = nx.DiGraph()

        # Filter transactions if an isolated bank perspective is requested
        if bank_filter:
            tx_subset = transactions_df[
                (transactions_df["sender_bank"] == bank_filter) |
                (transactions_df["receiver_bank"] == bank_filter)
            ].copy()
        else:
            tx_subset = transactions_df.copy()

        # Add Nodes from accounts
        # Create dictionary for quick attribute lookup
        account_attrs = {}
        for _, row in accounts_df.iterrows():
            acc_id = str(row["account_id"])
            account_attrs[acc_id] = {
                "bank_id": str(row["bank_id"]),
                "canonical_entity_id": str(row["canonical_entity_id"]),
                "profile_type": str(row["profile_type"]),
                "account_age_days": int(row["account_age_days"]),
                "initial_balance": float(row["initial_balance"]),
                "is_mule": int(row["is_mule"]),
                "ring_id": str(row["ring_id"]),
                "ring_role": str(row["ring_role"]),
            }

        # Add edges and ensure nodes exist
        for _, tx in tx_subset.iterrows():
            u = str(tx["sender_account"])
            v = str(tx["receiver_account"])
            amt = float(tx["amount"])
            ts = pd.to_datetime(tx["timestamp"])
            s_bank = str(tx["sender_bank"])
            r_bank = str(tx["receiver_bank"])
            is_cross = int(s_bank != r_bank)

            # Ensure node attributes are attached
            if u not in G:
                attrs = account_attrs.get(u, {
                    "bank_id": s_bank,
                    "canonical_entity_id": "UNKNOWN",
                    "profile_type": "UNKNOWN",
                    "account_age_days": 30,
                    "initial_balance": 0.0,
                    "is_mule": 0,
                    "ring_id": "NONE",
                    "ring_role": "UNKNOWN",
                })
                G.add_node(u, **attrs)

            if v not in G:
                attrs = account_attrs.get(v, {
                    "bank_id": r_bank,
                    "canonical_entity_id": "UNKNOWN",
                    "profile_type": "UNKNOWN",
                    "account_age_days": 30,
                    "initial_balance": 0.0,
                    "is_mule": 0,
                    "ring_id": "NONE",
                    "ring_role": "UNKNOWN",
                })
                G.add_node(v, **attrs)

            # In DiGraph, if multiple edges exist between u and v, we track aggregated amount
            # and list of individual transaction events
            if G.has_edge(u, v):
                G[u][v]["weight"] += amt
                G[u][v]["tx_count"] += 1
                G[u][v]["transactions"].append({
                    "tx_id": str(tx["transaction_id"]),
                    "amount": amt,
                    "timestamp": ts,
                    "is_suspicious": int(tx["is_suspicious"]),
                    "is_cross_bank": is_cross,
                })
            else:
                G.add_edge(
                    u,
                    v,
                    weight=amt,
                    tx_count=1,
                    is_cross_bank=is_cross,
                    transactions=[{
                        "tx_id": str(tx["transaction_id"]),
                        "amount": amt,
                        "timestamp": ts,
                        "is_suspicious": int(tx["is_suspicious"]),
                        "is_cross_bank": is_cross,
                    }],
                )

        # Ensure all accounts from accounts_df are in G even if zero transactions in current slice
        for acc_id, attrs in account_attrs.items():
            if acc_id not in G:
                G.add_node(acc_id, **attrs)

        return G
