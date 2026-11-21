"""
Feature 2: Explainable AI (XAI) Dashboard View.
Provides SHAP waterfall explanations, feature attribution breakdowns,
and human-understandable reason generators for compliance officers.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import json

import config
from src.explainable_ai.shap_explainer import ModelSHAPExplainer
from src.explainable_ai.reason_generator import HumanExplanationGenerator
from src.adapter.detection_adapter import DetectionAdapter


@st.cache_resource
def load_xai_components():
    adapter = DetectionAdapter()
    accounts, transactions, risk_scores, _, _ = adapter.load_data()
    explainer = ModelSHAPExplainer()
    generator = HumanExplanationGenerator()
    return accounts, transactions, risk_scores, explainer, generator


def render():
    st.markdown("""
    <div class="top-banner">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 12px;">
            <div>
                <div class="top-title">
                    <span>💡 Explainable AI (XAI) Intelligence</span>
                    <span class="top-badge">Feature 2: SHAP Feature Attribution</span>
                </div>
                <p class="top-desc">
                    Understand why accounts are flagged using Shapley additive explanations and deterministic flow evidence.
                </p>
            </div>
            <div style="text-align: right;">
                <span class="badge-success">● TreeExplainer Active</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    accounts, transactions, risk_scores, explainer, generator = load_xai_components()

    if accounts.empty or risk_scores.empty:
        st.warning("Account or risk score data not found. Please run the data pipeline first.")
        return

    # Merge features with risk scores for deep-dive
    merged = accounts.merge(risk_scores[["account_id", "risk_score", "risk_tier"]], on="account_id", how="left")

    col_s1, col_s2 = st.columns([2, 1])
    with col_s1:
        # Filter suspect or high risk accounts
        high_risk_accs = merged[merged["risk_tier"] == "HIGH"]["account_id"].tolist()
        if not high_risk_accs:
            high_risk_accs = merged["account_id"].head(20).tolist()

        sel_acc_id = st.selectbox(
            "Select Account to Explain:",
            high_risk_accs,
            index=0,
            help="Choose an account to inspect its SHAP feature attributions and compliance explanation.",
        )

    acc_row = merged[merged["account_id"] == sel_acc_id].iloc[0]
    risk_score = float(acc_row.get("risk_score", 0.92))
    risk_tier = str(acc_row.get("risk_tier", "HIGH")).capitalize()
    bank_id = str(acc_row.get("bank_id", "BANK_B"))

    # Compute SHAP explanation
    shap_res = explainer.explain_account(acc_row, top_k=8)
    exp_summary = generator.generate_explanation(
        account_id=sel_acc_id,
        shap_explanation=shap_res,
        risk_tier=risk_tier,
    )

    with col_s2:
        st.markdown(f"""
        <div style="background: white; border: 2px solid {'#DC2626' if risk_tier == 'High' else '#16A34A'}; border-radius: 10px; padding: 14px; text-align: center; margin-top: 4px;">
            <div style="font-size: 0.8rem; color: #64748B; font-weight: 600;">PREDICTED RISK ASSESSMENT</div>
            <div style="font-size: 1.6rem; font-weight: 800; color: {'#DC2626' if risk_tier == 'High' else '#16A34A'}; margin: 4px 0;">{risk_tier.upper()} RISK</div>
            <div style="font-size: 0.95rem; font-weight: 700; color: #1E293B;">Probability Score: {int(risk_score * 100)}%</div>
            <div style="font-size: 0.75rem; color: #64748B; margin-top: 4px;">Institution: <b>{bank_id}</b></div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # -------------------------------------------------------------
    # Human-Readable Explanation Card (Matching User Example)
    # -------------------------------------------------------------
    border_c = "#DC2626" if risk_tier == "High" else "#16A34A"
    st.markdown(f"""
    <div style="background: white; border-left: 6px solid {border_c}; border-radius: 8px; padding: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); margin-bottom: 24px;">
        <div style="font-size: 1.25rem; font-weight: 800; color: #0F172A; margin-bottom: 8px;">
            Why was this account flagged?
        </div>
        <div style="display: flex; gap: 8px; margin-bottom: 14px;">
            <span style="background: #FEE2E2; color: #991B1B; font-size: 0.8rem; font-weight: 700; padding: 3px 10px; border-radius: 4px;">
                {risk_tier} Risk ({int(risk_score*100)}%)
            </span>
            <span style="background: #F1F5F9; color: #334155; font-size: 0.8rem; font-weight: 600; padding: 3px 10px; border-radius: 4px;">
                Account: {sel_acc_id}
            </span>
        </div>
        <div style="color: #334155; font-size: 0.95rem; line-height: 1.7; margin-bottom: 16px;">
    """, unsafe_allow_html=True)

    for reason in exp_summary["bullet_reasons"]:
        st.markdown(f"• **{reason}**")

    st.markdown(f"""
        </div>
        <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 6px; padding: 12px 16px;">
            <div style="font-size: 0.85rem; font-weight: 700; color: #1E40AF; margin-bottom: 4px;">AI EXPLANATION</div>
            <div style="font-size: 0.92rem; color: #1E293B; line-height: 1.5;">
                {exp_summary['ai_summary']}
            </div>
        </div>
        <div style="font-size: 0.75rem; color: #94A3B8; margin-top: 10px;">
            <i>{exp_summary['evidence_basis']}</i>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # -------------------------------------------------------------
    # SHAP Numerical Contribution Waterfall / Bar Chart
    # -------------------------------------------------------------
    st.markdown("#### 📊 SHAP Feature Attribution Analysis")
    st.caption("Shows how individual mathematical features pushed the risk probability higher (red) or lower (green) from the baseline expected value.")

    drivers = shap_res.get("top_drivers", [])
    if drivers:
        feats = [d["feature"] for d in drivers]
        shap_vals = [d["shap_value"] for d in drivers]
        bar_colors = ["#EF4444" if v > 0 else "#10B981" for v in shap_vals]

        fig = go.Figure(go.Bar(
            x=shap_vals,
            y=feats,
            orientation="h",
            marker_color=bar_colors,
            text=[f"{v:+.4f}" for v in shap_vals],
            textposition="auto",
        ))
        fig.update_layout(
            title=f"<b>Top Feature Contributions to Risk Score ({sel_acc_id})</b>",
            xaxis_title="SHAP Value (Impact on Model Fraud Probability)",
            yaxis=dict(autorange="reversed"),
            template="plotly_white",
            height=360,
            margin=dict(l=20, r=20, t=50, b=20),
        )
        st.plotly_chart(fig, use_container_width=True)

        # Feature Attribution Table
        df_drivers = pd.DataFrame(drivers)
        st.dataframe(df_drivers, use_container_width=True, hide_index=True)
    else:
        st.info("No feature drivers available for the selected profile.")
