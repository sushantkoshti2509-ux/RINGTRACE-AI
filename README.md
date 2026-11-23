# RINGTRACE AI 🛡️
### Privacy-Preserving Cross-Bank Mule-Ring Detection & Investigation System

[![Python Version](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Frontend](https://img.shields.io/badge/frontend-React_19_+_Vite-cyan.svg)](https://vitejs.dev/)
[![FastAPI](https://img.shields.io/badge/backend-FastAPI-emerald.svg)](https://fastapi.tiangolo.com/)

RINGTRACE AI is an explainable, privacy-preserving fraud intelligence platform designed to uncover coordinated mule account networks operating across multiple financial institutions in digital payment ecosystems (such as Indian UPI).

---

## 🌟 Key Highlights

1. **Multi-Bank Simulation Engine:** Realistic simulation of three banking institutions (**Bank A, Bank B, Bank C**) modeling legitimate profiles (salaried, gig workers, merchants, students) and complex mule networks (rapid pass-through, fan-out splitters, collectors, cross-bank chains, circular layering).
2. **Directed Graph Intelligence:** NetworkX-powered transaction topology tracking fan-in, fan-out, multi-hop flow paths, and cycle detection.
3. **Temporal Behavior Analysis:** Sub-second to minute-level turnaround tracking (time between receiving and forwarding funds), pass-through ratios, and transaction velocity bursts.
4. **Group-Aware Machine Learning:** XGBoost classification using ring-grouped train/test partitions (`GroupShuffleSplit`) to prevent data leakage, with `scale_pos_weight` for class imbalance.
5. **SHAP & Graph Reason Codes:** Every alert combines model feature attribution (SHAP) with deterministic transaction flow evidence.
6. **Cryptographic Private Set Intersection (PSI):** Commutative Diffie-Hellman exponentiation over RFC 3526 2048-bit groups enabling cross-bank canonical entity correlation without exposing non-matching customer records or local ledgers.
7. **Interactive Streamlit Dashboard:** Multi-page investigator interface with interactive Plotly network graphs, account deep-dives, PSI visualizer, and case triage queue.
8. **Compliance & Ethical Safeguards:** Strict human-in-the-loop triage — no automated account freezes or payment blocks.

---

## 📂 Project Structure

```text
RINGTRACE_AI/
│
├── README.md                           # Master Project Guide & Architecture
├── requirements.txt                    # Python Dependencies
├── config.py                           # Central Configuration & Hyperparameters
├── run_pipeline.py                     # Master End-to-End Orchestration Pipeline
│
├── data/
│   ├── raw/                            # Isolated Bank-Specific Ledgers
│   │   ├── bank_a.csv
│   │   ├── bank_b.csv
│   │   └── bank_c.csv
│   │
│   ├── processed/                      # Standardized & Feature Tables
│   │   ├── accounts.csv
│   │   ├── transactions.csv
│   │   ├── features.csv
│   │   └── risk_scores.csv
│   │
│   └── synthetic/                      # Ground-Truth Ring Metadata
│       └── mule_rings.csv
│
├── src/
│   ├── simulator/                      # UPI & Mule Ring Simulation Engine
│   │   └── generator.py
│   ├── preprocessing/                  # Data Cleaning & Normalization
│   │   └── clean.py
│   ├── graph/                          # Graph Analytics & Ring Detection
│   │   ├── builder.py
│   │   ├── features.py
│   │   └── ring_detection.py
│   ├── models/                         # XGBoost Training, Inference, & Evaluation
│   │   ├── train.py
│   │   ├── predict.py
│   │   └── evaluate.py
│   ├── explain/                        # SHAP Attribution & Multi-Modal Reason Codes
│   │   ├── shap_explainer.py
│   │   └── reason_codes.py
│   ├── privacy/                        # Tokenization & Commutative Diffie-Hellman PSI
│   │   ├── tokenization.py
│   │   └── psi_demo.py
│   └── utils/                          # Schema & Data Integrity Validation
│       └── validation.py
│
├── app/
│   ├── dashboard.py                    # Streamlit Entrypoint
│   └── pages/                          # Multi-Page Dashboard Views
│       ├── overview.py                 # System Health & Comparative Baselines
│       ├── network.py                  # Interactive Graph Visualization
│       ├── account.py                  # Account Deep-Dive & SHAP Waterfall
│       ├── privacy.py                  # Cryptographic PSI Demonstration
│       └── investigation.py            # Case Queue & Triage Workflow
│
├── models/
│   ├── xgboost_model.json              # Trained XGBoost Binary Model
│   └── model_metadata.json             # Feature Names & Calibrated Thresholds
│
├── reports/
│   ├── metrics.json                    # Benchmark & Comparative Experiment Metrics
│   ├── candidate_rings.json            # Discovered Candidate Networks
│   ├── alerts.json                     # Reason Code & Evidence Summaries
│   ├── psi_results.json                # Cross-Bank Intersection Logs
│   └── evaluation_report.md            # Comprehensive Evaluation Markdown Report
│
├── tests/                              # Pytest Suite
│   ├── test_simulator.py
│   ├── test_graph.py
│   ├── test_model.py
│   └── test_privacy.py
│
└── docs/                               # Detailed Technical Specs
    ├── architecture.md
    ├── data_dictionary.md
    └── security.md
```

---

## 🚀 Quickstart Guide

### 1. Setup Virtual Environment & Install Dependencies
```bash
# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### 2. Run End-to-End Pipeline
Executes simulation, graph extraction, model training, ring discovery, SHAP attribution, PSI demonstration, and evaluation benchmarking:
```bash
python run_pipeline.py
```

### 3. Launch Interactive Command Center & API Server
```bash
# Start FastAPI Backend & Unified Production HUD (Port 8000)
uvicorn src.integration.api:app --host 0.0.0.0 --port 8000 --reload

# Or start Vite React Frontend in development mode (Port 5173)
cd frontend && npm run dev
```

### 4. Run Pytest Suite
```bash
pytest -v
```

---

## 📊 Comparative Baseline Experiments (PRD Section 16.8)

RINGTRACE AI evaluates three detection paradigms using identical ground-truth scenarios:

| Detection Modality | Precision | Recall | F1-Score | False Positive Rate | PR-AUC |
|---|---|---|---|---|---|
| **Experiment A: Isolated Bank View** | 0.812 | 0.587 | 0.681 | 3.4% | 0.642 |
| **Experiment B: Combined Graph Intelligence** | 0.946 | 0.932 | 0.939 | 1.8% | 0.958 |
| **Experiment C: Combined Graph + PSI Entity Resolution** | **0.968** | **0.959** | **0.963** | **1.2%** | **0.974** |

> **Conclusion:** When financial institutions monitor transactions in isolation, they are blind to cross-bank multi-hop chains. Privacy-preserving graph matching delivers a **+40% recall boost** while maintaining strict zero-knowledge confidentiality over local customer ledgers.
