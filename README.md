---
title: RINGTRACE AI
emoji: 🛡️
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 10000
---

# RINGTRACE AI 🛡️
### Multi-Bank Proactive Mule Ring Defense & Autonomous Financial Interception Engine

[![Python Version](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/)
[![Frontend](https://img.shields.io/badge/frontend-React_18_+_Vite-cyan.svg)](https://vitejs.dev/)
[![Backend](https://img.shields.io/badge/backend-FastAPI-emerald.svg)](https://fastapi.tiangolo.com/)
[![Tests](https://img.shields.io/badge/tests-77%20passed-brightgreen.svg)](tests/)
[![Deploy on Railway](https://railway.com/button.svg)](https://railway.com/template/new?template=https://github.com/sushantkoshti2509-ux/RINGTRACE-AI)
[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/sushantkoshti2509-ux/RINGTRACE-AI)

**RINGTRACE AI** is a real-time, privacy-preserving financial intelligence platform designed to detect, trace, and dismantle coordinated mule account rings operating across multi-bank digital payment corridors (such as Indian UPI, IMPS, and NEFT).

By coupling **Edge-Aware Graph Neural Networks (GINE & GATv2)** with **proactive topological bottleneck severance**, RINGTRACE AI allows participating financial institutions to detect multi-hop laundering chains before funds exit the formal banking perimeter.

---

## 🏛️ Four-Bank Unified Ecosystem

RINGTRACE AI models and coordinates real-time defense across four distinct banking tiers:

| Institution | Institutional Role | Primary Corridor Focus |
|---|---|---|
| **Bank A** | Primary Retail Settlement Switch | High-velocity retail accounts & initial dispersion |
| **Bank B** | Commercial Gateway & Corporate Treasury | High-value transit corridors & intermediary feeder accounts |
| **Bank C** | Regional Cooperative Clearing Hub | Layering aggregation nodes & mule collection points |
| **Bank D** | Federal Wealth & Remittance Rail | High-value cross-border hops & cash-out exit conduits |

---

## ⚡ Key Architectural Capabilities

### 1. Edge-Aware Graph Neural Network (GINE Backbone)
- **Relational Message Passing**: Propagates account features and transaction metadata (amounts, time delta, velocity, corridor) across graph edges.
- **Dual-Head Inference**: Simultaneously outputs node-level mule probabilities ($P(\text{mule})$) and edge-level transaction fraud probabilities.
- **Sub-Hop Explanations**: Generates deterministic reason codes and subgraph feature attributions without exposing non-relevant accounts.

### 2. Proactive Interception & Bottleneck Severance Engine
- **Choke-Point Identification**: Computes topological betweenness and bridge metrics to pinpoint the critical account whose disruption prevents the maximum downstream fund leakage.
- **Countermeasure Strategies**:
  - `COOLING_OFF_DELAY`: Imposes a dynamic 60-minute holding window on suspicious hops.
  - `REVERSE_FREEZE_CASCADE`: Propagates automated downstream hold signals across creditor banks.
  - `COLLATERAL_LOCK`: Temporarily reserves equivalent institutional liquidity at transit nodes.
  - `REGULATORY_OBSERVATION_HOLD`: Silent nodal monitoring for Law Enforcement (LEA) evidence gathering.
- **Calculated ROI**: Computes exact loss prevention metrics, downstream nodes neutralized, and severed edge volumes.

### 3. Cryptographic Privacy & DPDP Act 2023 Compliance
- **Commutative Diffie-Hellman PSI**: Cross-bank entity correlation over RFC 3526 2048-bit groups without revealing local customer ledgers.
- **Zero Raw PII Exposure**: Deterministic SHA-256 masking on all exported ledgers (`BANK_A:••••0100`).
- **Immutable Audit Trails**: Generates cryptographically signed JSON audit dossiers with SHA-256 integrity hashes for regulatory submission.

### 4. Interactive Enterprise HUD Command Center
- **Four-Bank Relational Fraud Network**: Visualized using `@xyflow/react` with 4-quadrant institutional mesh and flow DAG timeline layouts.
- **3D Cyber Clearing Fabric**: WebGL/Three.js spatial visualization of live settlement streams and flagged mule velocities.
- **AI Investigation Assistant**: Copilot for generating standardized Suspicious Activity Reports (SAR).
- **Dual-Reconciled Status Table**: Live multi-bank transaction ledger with instant search, bank filtering, and risk pagination.

---

## 📂 Repository Directory Layout

```text
RINGTRACE_AI/
├── Dockerfile                          # Multi-stage production container (Node + Python 3.12)
├── Procfile                            # Process definition for cloud PaaS
├── render.yaml                         # 1-Click Render Blueprint infrastructure-as-code
├── config.py                           # Central configuration & parameters
├── requirements.txt                    # Backend dependencies (PyTorch, PyG, FastAPI)
│
├── src/
│   ├── gnn/                            # Graph Neural Network models & inference
│   │   ├── models.py                   # EdgeAwareGNN & GATv2Net PyG implementations
│   │   ├── dataset.py                  # PyTorch Geometric dataset pipeline
│   │   ├── trainer.py                  # GNN training loops with group-aware splits
│   │   ├── inference.py                # Low-latency thread-safe GNN scoring service
│   │   └── explainer.py                # 2-hop neighborhood GNN subgraph attribution
│   │
│   ├── interception/                   # Proactive Interception & Choke-Point Engine
│   │   └── interception_engine.py      # Bottleneck analysis, severance, & ROI metrics
│   │
│   ├── integration/                    # Multi-bank data integration & REST API
│   │   ├── api.py                      # FastAPI application with static SPA mounting
│   │   ├── reconciler.py               # Dual-ledger reconciliation engine
│   │   └── database.py                 # SQLite/PostgreSQL persistence layer
│   │
│   ├── privacy/                        # Cryptographic tokenization & PSI
│   │   ├── tokenization.py             # DPDP-compliant canonical token hashing
│   │   └── psi_demo.py                 # 2048-bit Diffie-Hellman Private Set Intersection
│   │
│   └── platform/                       # Platform feature endpoints & helpers
│       ├── assistant.py                # Copilot SAR generator
│       └── cases.py                    # Case management & audit logs
│
├── frontend/                           # React 18 + Vite HUD Command Center
│   ├── src/
│   │   ├── components/                 # UI components
│   │   │   ├── GNNGraphDashboard.jsx   # Four-Bank Relational Fraud Network (React Flow)
│   │   │   ├── MuleRingCanvas.jsx      # Multi-Bank Synthetic Topology Canvas
│   │   │   ├── InterceptionSimulator.jsx # Countermeasure simulation controller
│   │   │   ├── CyberGlobe3D.jsx        # 3D spatial clearing fabric (Three.js)
│   │   │   └── KPIMetricsBar.jsx       # Real-time institutional telemetry cards
│   │   │
│   │   └── views/                      # Workstation module pages
│   │       ├── MonitoringView.jsx      # Default executive dashboard
│   │       ├── GNNIntelligenceView.jsx # GNN model intelligence & predictions
│   │       ├── NetworkExplorerView.jsx # Multi-bank pattern analysis
│   │       └── CaseManagerView.jsx     # Regulatory case dossiers & triage
│   │
│   └── package.json                    # Frontend dependencies
│
└── tests/                              # Pytest test suite (77 passing test cases)
    ├── test_gnn.py                     # GNN models, training, & inference tests
    ├── test_interception.py            # Choke-point detection & severance tests
    ├── test_integration.py             # Dual-ledger reconciliation tests
    └── ...
```

---

## 🚀 Quickstart & Local Setup

### Prerequisites
- Python 3.12+
- Node.js 18+ (for frontend development)

### 1. Clone & Setup Python Virtual Environment
```bash
git clone https://github.com/sushantkoshti2509-ux/RINGTRACE-AI.git
cd RINGTRACE-AI

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Run Complete Test Suite
```bash
MPLCONFIGDIR=/tmp/matplotlib_cache OMP_NUM_THREADS=1 pytest tests/ -v
```
*(All 77 test cases will pass in ~40 seconds).*

### 3. Launch the Application Locally
```bash
# Start FastAPI backend (serves API and compiled frontend at http://localhost:8000)
MPLCONFIGDIR=/tmp/matplotlib_cache OMP_NUM_THREADS=1 uvicorn src.integration.api:app --host 0.0.0.0 --port 8000

# Optional: Run Vite frontend in development hot-reload mode (http://localhost:5173)
cd frontend
npm install
npm run dev
```

---

## ☁️ Cloud Deployment (Render / Docker)

The repository is pre-configured for **Render Free Tier** with zero Out-of-Memory (OOM) risks:

### 1-Click Blueprint Deploy (Recommended)
1. Go to the [Render Dashboard](https://dashboard.render.com/).
2. Click **`+ New`** $\rightarrow$ select **`Blueprint`**.
3. Connect repository: `sushantkoshti2509-ux/RINGTRACE-AI`.
4. Click **`Apply`**. Render will automatically use [render.yaml](render.yaml) to configure the Docker multi-stage build.

### Production Environment Settings
- **Port**: `10000` (Render default)
- **Startup Memory**: `~289 MB` (safely below Render's 512 MB ceiling)
- **Single-Thread Optimization**: `OMP_NUM_THREADS=1`, `MKL_NUM_THREADS=1`
- **Cache Redirection**: `MPLCONFIGDIR=/tmp/matplotlib_cache`

---

## 🔒 Security, Compliance & Ethics

- **DPDP Act 2023 Compliant**: Customer account numbers, names, and PII are masked at point of ingestion.
- **Zero-Knowledge Entity Correlation**: Private Set Intersection ensures banks discover common suspect accounts without leaking innocent customer records.
- **Human-in-the-Loop Governance**: Interception suggestions require regulatory nodal officer authorization. No black-box automated account freezing.

---

## 📄 License
This project is licensed under the MIT License.
