"""
RINGTRACE AI - Central Configuration Module
Defines system paths, simulation constants, feature lists, model parameters,
and privacy configuration for cross-bank mule ring detection.
"""

from pathlib import Path

# Base Paths
PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PREPROCESSED_DATA_DIR = DATA_DIR / "preprocessed"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
SYNTHETIC_DATA_DIR = DATA_DIR / "synthetic"
MODELS_DIR = PROJECT_ROOT / "models"
REPORTS_DIR = PROJECT_ROOT / "reports"
DOCS_DIR = PROJECT_ROOT / "docs"

# Ensure all primary directories exist
for directory in [
    RAW_DATA_DIR,
    PREPROCESSED_DATA_DIR,
    PROCESSED_DATA_DIR,
    SYNTHETIC_DATA_DIR,
    MODELS_DIR,
    REPORTS_DIR,
    DOCS_DIR,
]:
    directory.mkdir(parents=True, exist_ok=True)

# Simulation Constants
RANDOM_SEED = 42
SIMULATED_BANKS = ["BANK_A", "BANK_B", "BANK_C"]

# Synthetic Data Sizing
TOTAL_ACCOUNTS = 600
NUM_MULE_RINGS = 18
SIMULATION_DAYS = 7

# Legitimate customer profile distribution
LEGITIMATE_PROFILES = [
    "SALARIED",
    "GIG_WORKER",
    "MERCHANT",
    "STUDENT_FIRST_TIME",
    "REGULAR_P2P",
]

# Mule ring archetypes
RING_ARCHETYPES = [
    "RAPID_PASS_THROUGH",
    "FAN_OUT_SPLITTER",
    "FAN_IN_COLLECTOR",
    "CROSS_BANK_CHAIN",
    "CIRCULAR_LAYERING",
]

# Machine Learning Feature Set
NUMERICAL_FEATURES = [
    "account_age_days",
    "in_degree",
    "out_degree",
    "fan_in_distinct",
    "fan_out_distinct",
    "total_amount_in",
    "total_amount_out",
    "avg_amount_in",
    "avg_amount_out",
    "pass_through_ratio",
    "net_flow_ratio",
    "turnover_rate",
    "avg_turnaround_time_sec",
    "min_turnaround_time_sec",
    "velocity_1h_max",
    "velocity_24h_max",
    "cross_bank_tx_ratio",
    "pagerank",
    "clustering_coeff",
]

CATEGORICAL_FEATURES = [
    "profile_type",
    "bank_id",
]

TARGET_COLUMN = "is_mule"

# XGBoost Default Hyperparameters
XGBOOST_PARAMS = {
    "n_estimators": 120,
    "max_depth": 5,
    "learning_rate": 0.08,
    "subsample": 0.85,
    "colsample_bytree": 0.85,
    "random_state": RANDOM_SEED,
    "eval_metric": "logloss",
}

DEFAULT_ALERT_THRESHOLD = 0.50

# PSI Security Configuration
PSI_HASH_ALGORITHM = "sha256"
PSI_SHARED_SALT = "RINGTRACE_SECURE_CANONICAL_SALT_v1"
