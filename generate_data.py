"""
RINGTRACE AI - Step 1: Standalone Synthetic Banking Transaction Generator CLI.
Generates realistic multi-bank transaction ledgers for Bank A, Bank B, and Bank C
with controllable volume, amounts, fraud rates, and dual CSV/JSON export.
"""

import sys
from pathlib import Path

# Setup paths
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.simulator.generator import main

if __name__ == "__main__":
    main()
