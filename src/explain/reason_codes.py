"""
RINGTRACE AI - Multi-Modal Reason Codes and Evidence Generator.
Synthesizes SHAP machine learning feature contributions with independent
deterministic graph and temporal evidence into investigator-ready alerts.
"""

from typing import Dict, Any, List
import pandas as pd
import networkx as nx


class ReasonCodeGenerator:
    """Generates plain-language reason codes combining SHAP and graph evidence."""

    def __init__(self):
        pass

    def generate_account_evidence(
        self,
        account_id: str,
        features_row: Any,
        shap_explanation: Dict[str, Any],
        G: nx.DiGraph,
    ) -> Dict[str, Any]:
        """
        Synthesizes SHAP explanations and graph metrics into plain-language reason codes.
        Distinguishes strictly between Model Feature Attribution and Graph Structural Evidence.
        """
        if isinstance(features_row, pd.Series):
            feat_dict = features_row.to_dict()
        elif isinstance(features_row, dict):
            feat_dict = features_row
        else:
            feat_dict = dict(features_row)

        risk_val = feat_dict.get("risk_score", 0.0)
        risk_score = float(risk_val.iloc[0] if isinstance(risk_val, pd.Series) else risk_val)
        
        tier_val = feat_dict.get("risk_tier", "LOW")
        tier = str(tier_val.iloc[0] if isinstance(tier_val, pd.Series) else tier_val)
        
        bank_val = feat_dict.get("bank_id", "UNKNOWN")
        bank = str(bank_val.iloc[0] if isinstance(bank_val, pd.Series) else bank_val)
        
        prof_val = feat_dict.get("profile_type", "UNKNOWN")
        profile = str(prof_val.iloc[0] if isinstance(prof_val, pd.Series) else prof_val)

        # 1. SHAP-Derived Reasons (Why the Machine Learning Model Flagged It)
        shap_reasons = []
        for driver in shap_explanation.get("top_drivers", []):
            feat = driver["feature"]
            val = driver["actual_value"]
            s_val = driver["shap_value"]

            if driver["direction"] == "INCREASES_RISK":
                if "pass_through_ratio" in feat:
                    shap_reasons.append(f"Elevated pass-through ratio ({val:.1%}) indicates quick fund redirection.")
                elif "min_turnaround_time" in feat:
                    mins = val / 60.0
                    shap_reasons.append(f"Rapid turnaround velocity: forwarded received funds in {mins:.1f} minutes.")
                elif "cross_bank_tx_ratio" in feat:
                    shap_reasons.append(f"High cross-bank activity ({val:.1%}) indicates multi-institution fund movement.")
                elif "velocity_1h_max" in feat:
                    shap_reasons.append(f"Transaction burst: {int(val)} transactions executed within a single 1-hour window.")
                elif "fan_out_distinct" in feat:
                    shap_reasons.append(f"High fan-out: distributed money to {int(val)} distinct receiver accounts.")
                elif "fan_in_distinct" in feat:
                    shap_reasons.append(f"High fan-in: pooled money from {int(val)} distinct sender accounts.")
                elif "account_age_days" in feat:
                    shap_reasons.append(f"New account maturity: opened only {int(val)} days ago.")
                else:
                    shap_reasons.append(f"Feature '{feat}' value ({val}) contributed +{s_val:.3f} to risk score.")

        # 2. Graph & Transaction Path Evidence (Independently Verified Flow)
        graph_evidence = {
            "in_degree": int(features_row.get("in_degree", 0)),
            "out_degree": int(features_row.get("out_degree", 0)),
            "total_in": float(features_row.get("total_amount_in", 0.0)),
            "total_out": float(features_row.get("total_amount_out", 0.0)),
            "pass_through_ratio": float(features_row.get("pass_through_ratio", 0.0)),
            "min_turnaround_seconds": float(features_row.get("min_turnaround_time_sec", 0.0)),
            "cross_bank_ratio": float(features_row.get("cross_bank_tx_ratio", 0.0)),
        }

        # Immediate Counterparty Details
        inbound_senders = []
        if account_id in G:
            for u, _, d in G.in_edges(account_id, data=True):
                inbound_senders.append({
                    "sender": u,
                    "sender_bank": G.nodes[u].get("bank_id", "UNKNOWN"),
                    "amount": round(d.get("weight", 0.0), 2),
                    "tx_count": d.get("tx_count", 1),
                })

        outbound_receivers = []
        if account_id in G:
            for _, v, d in G.out_edges(account_id, data=True):
                outbound_receivers.append({
                    "receiver": v,
                    "receiver_bank": G.nodes[v].get("bank_id", "UNKNOWN"),
                    "amount": round(d.get("weight", 0.0), 2),
                    "tx_count": d.get("tx_count", 1),
                })

        # Plain Language Executive Summary
        if tier == "HIGH":
            turnaround_min = graph_evidence["min_turnaround_seconds"] / 60.0
            summary = (
                f"Account {account_id} ({bank}) is flagged for HIGH-RISK review (Score: {risk_score:.2f}). "
                f"Graph analysis reveals {account_id} received ₹{graph_evidence['total_in']:,.2f} "
                f"from {len(inbound_senders)} sources and forwarded ₹{graph_evidence['total_out']:,.2f} "
                f"(pass-through: {graph_evidence['pass_through_ratio']:.1%}) within {turnaround_min:.1f} minutes "
                f"across {len(outbound_receivers)} destinations. {graph_evidence['cross_bank_ratio']:.0%} "
                f"of activity involves cross-bank transfers."
            )
        elif tier == "MEDIUM":
            summary = (
                f"Account {account_id} ({bank}) exhibits moderate anomalies (Score: {risk_score:.2f}). "
                f"Received ₹{graph_evidence['total_in']:,.2f} with {graph_evidence['out_degree']} outbound transfers. "
                f"Investigate counterparties and verify profile activity against baseline."
            )
        else:
            summary = f"Account {account_id} is within normal behavioral boundaries (Score: {risk_score:.2f})."

        return {
            "account_id": account_id,
            "bank_id": bank,
            "risk_score": risk_score,
            "risk_tier": tier,
            "profile_type": profile,
            "executive_summary": summary,
            "shap_reasons": shap_reasons,
            "graph_evidence": graph_evidence,
            "inbound_counterparties": inbound_senders,
            "outbound_counterparties": outbound_receivers,
        }
