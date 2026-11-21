"""
RINGTRACE AI - Multi-Bank Mule Ring Detection & Investigation Dashboard.
Master Streamlit interface with investigator workflows, interactive graph visualizations,
SHAP explainability, and cryptographic Private Set Intersection demonstration.
"""

import sys
from pathlib import Path
import streamlit as st

# Setup paths
APP_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = APP_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.views import overview, network, account, privacy, investigation, realtime, alerts, monitoring

st.set_page_config(
    page_title="RINGTRACE AI | Cross-Bank Fraud Defense",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Premium Fintech / Cybersecurity Design System Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    /* Top Header Bar */
    .top-banner {
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 20px 24px;
        margin-bottom: 24px;
        color: white;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.08);
    }
    .top-title {
        font-size: 1.85rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .top-badge {
        background: rgba(59, 130, 246, 0.2);
        border: 1px solid #3B82F6;
        color: #93C5FD;
        font-size: 0.75rem;
        font-weight: 600;
        padding: 3px 10px;
        border-radius: 20px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .top-desc {
        color: #94A3B8;
        font-size: 0.95rem;
        margin-top: 6px;
        margin-bottom: 0;
    }

    /* Metric Cards */
    .ring-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 18px 20px;
        box-shadow: 0 2px 6px rgba(15, 23, 42, 0.04);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    .ring-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(15, 23, 42, 0.08);
    }
    .card-title {
        color: #64748B;
        font-size: 0.82rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        margin-bottom: 6px;
    }
    .card-val {
        color: #0F172A;
        font-size: 1.75rem;
        font-weight: 800;
        line-height: 1.2;
    }
    .card-sub {
        font-size: 0.82rem;
        font-weight: 600;
        margin-top: 6px;
    }

    /* Status Badges */
    .badge-danger {
        background: #FEF2F2;
        color: #DC2626;
        border: 1px solid #FCA5A5;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.78rem;
        font-weight: 700;
        display: inline-block;
    }
    .badge-warning {
        background: #FFFBEB;
        color: #D97706;
        border: 1px solid #FDE68A;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.78rem;
        font-weight: 700;
        display: inline-block;
    }
    .badge-success {
        background: #ECFDF5;
        color: #059669;
        border: 1px solid #A7F3D0;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.78rem;
        font-weight: 700;
        display: inline-block;
    }
    .badge-info {
        background: #EFF6FF;
        color: #2563EB;
        border: 1px solid #BFDBFE;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.78rem;
        font-weight: 700;
        display: inline-block;
    }

    /* Bank Pills */
    .bank-pill-a {
        background: #DBEAFE;
        color: #1D4ED8;
        font-weight: 700;
        padding: 2px 8px;
        border-radius: 6px;
        font-size: 0.8rem;
    }
    .bank-pill-b {
        background: #D1FAE5;
        color: #047857;
        font-weight: 700;
        padding: 2px 8px;
        border-radius: 6px;
        font-size: 0.8rem;
    }
    .bank-pill-c {
        background: #FEF3C7;
        color: #B45309;
        font-weight: 700;
        padding: 2px 8px;
        border-radius: 6px;
        font-size: 0.8rem;
    }

    /* Safeguard Banner */
    .safeguard-banner {
        background: #F8FAFC;
        border-left: 4px solid #3B82F6;
        border-top: 1px solid #E2E8F0;
        border-right: 1px solid #E2E8F0;
        border-bottom: 1px solid #E2E8F0;
        padding: 14px 18px;
        border-radius: 8px;
        margin-bottom: 20px;
        font-size: 0.92rem;
        color: #334155;
    }

    /* Explanation Boxes */
    .concept-box {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 16px;
    }
    .concept-title {
        font-size: 0.95rem;
        font-weight: 700;
        color: #0F172A;
        margin-bottom: 6px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .concept-text {
        font-size: 0.88rem;
        color: #475569;
        line-height: 1.5;
        margin: 0;
    }
</style>
""", unsafe_allow_html=True)


def main():
    # Sidebar Branding & Navigation
    with st.sidebar:
        st.markdown("""
        <div style="padding: 10px 0 16px 0;">
            <div style="display: flex; align-items: center; gap: 10px;">
                <span style="font-size: 1.8rem;">🛡️</span>
                <div>
                    <h2 style="font-size: 1.35rem; font-weight: 800; margin: 0; color: #0F172A;">RINGTRACE AI</h2>
                    <span style="font-size: 0.75rem; color: #64748B; font-weight: 600;">Cross-Bank Mule Ring Defense</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div style="background: #F0FDF4; border: 1px solid #BBF7D0; border-radius: 8px; padding: 10px 12px; margin-bottom: 18px;">
            <div style="display: flex; align-items: center; gap: 8px;">
                <span style="height: 9px; width: 9px; background-color: #10B981; border-radius: 50%; display: inline-block;"></span>
                <span style="font-size: 0.82rem; font-weight: 700; color: #166534;">Simulated UPI Network Active</span>
            </div>
            <div style="font-size: 0.74rem; color: #15803D; margin-top: 4px;">
                Bank A • Bank B • Bank C Connected
            </div>
        </div>
        """, unsafe_allow_html=True)

        page = st.radio(
            "EXPLORATION MODULES",
            [
                "📊 Multi-Bank Monitoring Dashboard",
                "🚨 Fraud Alert & Notification Center",
                "⚡ Real-Time Stream Scoring",
                "🏛️ Executive Intelligence & Benchmarks",
                "🕸️ Network & Mule Ring Graph",
                "🔍 Account Deep-Dive & SHAP",
                "🔐 Cross-Bank PSI Privacy",
                "📋 Investigator Case Queue",
            ],
            index=0,
        )

        st.markdown("---")
        st.markdown("""
        <div style="font-size: 0.78rem; color: #64748B; line-height: 1.5;">
            <b>Investigator Context:</b><br>
            • Synthetic Prototype v1.0<br>
            • Privacy: Commutative DH-PSI<br>
            • Engine: NetworkX + XGBoost<br>
            • Ethics: Human-in-the-loop only
        </div>
        """, unsafe_allow_html=True)

    if page == "📊 Multi-Bank Monitoring Dashboard":
        monitoring.render()
    elif page == "🚨 Fraud Alert & Notification Center":
        alerts.render()
    elif page == "⚡ Real-Time Stream Scoring":
        realtime.render()
    elif page == "🏛️ Executive Intelligence & Benchmarks":
        overview.render()
    elif page == "🕸️ Network & Mule Ring Graph":
        network.render()
    elif page == "🔍 Account Deep-Dive & SHAP":
        account.render()
    elif page == "🔐 Cross-Bank PSI Privacy":
        privacy.render()
    elif page == "📋 Investigator Case Queue":
        investigation.render()


if __name__ == "__main__":
    main()
