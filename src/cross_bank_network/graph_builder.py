"""
Feature 1: Cross-Bank Fraud Network Detection - Graph Builder.
Constructs NetworkX directed graphs where:
- Each bank account is a node with bank identity metadata.
- Each financial transaction is a directed edge with amount and timestamp.
- Accounts are bank-qualified (e.g. BANK_A:A101, BANK_B:B201).
"""

from typing import Dict, Any, List, Optional
import networkx as nx
import pandas as pd


class CrossBankGraphBuilder:
    """Builds multi-bank transaction graphs with bank-qualified node identifiers."""

    def __init__(self):
        pass

    def build_network_graph(
        self,
        transactions_df: pd.DataFrame,
        accounts_df: Optional[pd.DataFrame] = None,
        use_qualified_ids: bool = True,
    ) -> nx.DiGraph:
        """
        Builds a NetworkX directed graph from transaction records.
        Stores amount, timestamp, and transaction_id on edges.
        Stores bank_id, is_mule, and risk attributes on nodes.
        """
        G = nx.DiGraph()

        if transactions_df.empty:
            return G

        account_meta = {}
        if accounts_df is not None and not accounts_df.empty:
            for _, row in accounts_df.iterrows():
                acc = str(row.get("account_id", ""))
                account_meta[acc] = {
                    "bank_id": str(row.get("bank_id", "BANK_A")),
                    "is_mule": int(row.get("is_mule", 0)),
                    "profile_type": str(row.get("profile_type", "UNKNOWN")),
                    "risk_tier": str(row.get("risk_tier", "LOW")),
                }

        for _, tx in transactions_df.iterrows():
            sender = str(tx.get("sender_account", ""))
            receiver = str(tx.get("receiver_account", ""))
            s_bank = str(tx.get("sender_bank", "BANK_A"))
            r_bank = str(tx.get("receiver_bank", "BANK_B"))
            amt = float(tx.get("amount", 0.0))
            ts = str(tx.get("timestamp", ""))
            tx_id = str(tx.get("transaction_id", ""))

            u = f"{s_bank}:{sender}" if use_qualified_ids else sender
            v = f"{r_bank}:{receiver}" if use_qualified_ids else receiver

            # Add node attributes
            if u not in G:
                meta_u = account_meta.get(sender, {"bank_id": s_bank, "is_mule": 0, "profile_type": "REGULAR_P2P", "risk_tier": "LOW"})
                G.add_node(u, account_id=sender, **meta_u)

            if v not in G:
                meta_v = account_meta.get(receiver, {"bank_id": r_bank, "is_mule": 0, "profile_type": "REGULAR_P2P", "risk_tier": "LOW"})
                G.add_node(v, account_id=receiver, **meta_v)

            # Add directed edge with transaction metadata
            G.add_edge(
                u,
                v,
                amount=amt,
                timestamp=ts,
                transaction_id=tx_id,
                is_cross_bank=(s_bank != r_bank),
                sender_bank=s_bank,
                receiver_bank=r_bank,
            )

        return G
