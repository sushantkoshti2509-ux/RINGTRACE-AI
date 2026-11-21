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

from app.pages import overview, network, account, privacy, investigation

st.set_page_config(
    page_title="RINGTRACE AI | Fraud Investigation Platform",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling
st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        color: #1E293B;
        margin-bottom: 0px;
    }
    .sub-title {
        font-size: 1.05rem;
        color: #64748B;
        margin-bottom: 20px;
    }
    .metric-card {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 16px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .safeguard-banner {
        background-color: #EFF6FF;
        border-left: 4px solid #3B82F6;
        padding: 12px 16px;
        border-radius: 4px;
        margin-bottom: 20px;
        font-size: 0.95rem;
    }
</style>
""", unsafe_allow_html=True)


def main():
    st.sidebar.title("🛡️ RINGTRACE AI")
    st.sidebar.caption("Privacy-Preserving Cross-Bank Mule Intelligence")

    st.sidebar.markdown("---")
    page = st.sidebar.radio(
        "Navigation",
        [
            "📊 Executive Overview",
            "🕸️ Network & Ring Graph",
            "🔍 Account Deep-Dive & SHAP",
            "🔐 Cross-Bank PSI Privacy",
            "📋 Investigator Case Queue",
        ],
        index=0,
    )

    st.sidebar.markdown("---")
    st.sidebar.info(
        "**Simulated Institutions:**\n"
        "- 🏦 Bank A (Primary)\n"
        "- 🏦 Bank B (Partner)\n"
        "- 🏦 Bank C (Partner)\n\n"
        "**Framework Version:** v1.0 MVP"
    )

    if page == "📊 Executive Overview":
        overview.render()
    elif page == "🕸️ Network & Ring Graph":
        network.render()
    elif page == "🔍 Account Deep-Dive & SHAP":
        account.render()
    elif page == "🔐 Cross-Bank PSI Privacy":
        privacy.render()
    elif page == "📋 Investigator Case Queue":
        investigation.render()


if __name__ == "__main__":
    main()
