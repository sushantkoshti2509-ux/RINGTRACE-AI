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
INTEGRATED_DATA_DIR = DATA_DIR / "integrated"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
SYNTHETIC_DATA_DIR = DATA_DIR / "synthetic"
MODELS_DIR = PROJECT_ROOT / "models"
REPORTS_DIR = PROJECT_ROOT / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"
DOCS_DIR = PROJECT_ROOT / "docs"

# Database Configuration (Defaults to local SQLite; override with DATABASE_URL for PostgreSQL)
DEFAULT_SQLITE_URL = f"sqlite:///{INTEGRATED_DATA_DIR / 'ringtrace_integrated.db'}"

# Ensure all primary directories exist
for directory in [
    RAW_DATA_DIR,
    PREPROCESSED_DATA_DIR,
    INTEGRATED_DATA_DIR,
    PROCESSED_DATA_DIR,
    SYNTHETIC_DATA_DIR,
    MODELS_DIR,
    REPORTS_DIR,
    FIGURES_DIR,
    DOCS_DIR,
]:
    directory.mkdir(parents=True, exist_ok=True)

# Simulation Constants
RANDOM_SEED = 42
SIMULATED_BANKS = [
    "BANK_A",
    "BANK_B",
    "BANK_C",
    "BANK_D",
]

BANK_METADATA = {
    "BANK_A": {"name": "Bank A", "code": "BNKA", "color": "#06B6D4"},
    "BANK_B": {"name": "Bank B", "code": "BNKB", "color": "#10B981"},
    "BANK_C": {"name": "Bank C", "code": "BNKC", "color": "#A855F7"},
    "BANK_D": {"name": "Bank D", "code": "BNKD", "color": "#F59E0B"},
    "BANK_E": {"name": "Bank E", "code": "BNKE", "color": "#3B82F6"},
    "BANK_F": {"name": "Bank F", "code": "BNKF", "color": "#EC4899"},
}

# Synthetic Data Sizing
TOTAL_ACCOUNTS = 1200
NUM_MULE_RINGS = 28
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
    "tx_frequency_total",
    "total_amount_in",
    "total_amount_out",
    "avg_amount_in",
    "avg_amount_out",
    "avg_amount_total",
    "high_value_tx_count",
    "high_value_ratio",
    "off_hours_tx_ratio",
    "pass_through_ratio",
    "net_flow_ratio",
    "turnover_rate",
    "avg_turnaround_time_sec",
    "min_turnaround_time_sec",
    "min_time_gap_sec",
    "velocity_1h_max",
    "velocity_24h_max",
    "velocity_score",
    "cross_bank_tx_ratio",
    "pagerank",
    "clustering_coeff",
    "behavioral_risk_score",
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
