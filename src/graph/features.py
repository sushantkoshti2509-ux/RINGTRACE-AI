"""
RINGTRACE AI - Graph & Temporal Feature Extraction Engine.
Extracts account-level network topology, flow balance, and temporal behavioral features.
Wraps the unified AccountFeatureEngine to maintain full backwards compatibility.
"""

from typing import Dict, List, Any
import pandas as pd
import networkx as nx

from src.features.account_features import AccountFeatureEngine


class GraphFeatureEngine:
    """Computes graph topology and temporal behavioral features from transaction graphs."""

    def __init__(self):
        self.engine = AccountFeatureEngine()

    def extract_features(
        self,
        G: nx.DiGraph,
        transactions_df: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Calculates all node-level network and temporal features for each account in G.
        Returns a DataFrame indexed by account_id with feature columns and target label.
        """
        return self.engine.extract_features(G, transactions_df)
