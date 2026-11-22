"""
Streamlit Community Cloud root entry point for RINGTRACE AI.
Delegates directly to app/dashboard.py for seamless 1-click cloud deployment.
"""
import sys
from pathlib import Path

# Add project root to sys.path
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.dashboard import main

if __name__ == "__main__":
    main()
