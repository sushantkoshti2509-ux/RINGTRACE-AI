# RINGTRACE AI — System Architecture & Design Specification

## 1. System Vision & Layered Design
RINGTRACE AI provides a privacy-preserving, cross-bank mule-ring detection architecture designed to identify coordinated suspicious account networks across digital payment ecosystems (such as Indian UPI).

The system architecture is structured into seven distinct layers:

```
               BANK A Ledgers       BANK B Ledgers       BANK C Ledgers
                     \                    |                    /
                      \                   |                   /
                       v                  v                  v
                    ============================================
                    LAYER 1: SYNTHETIC DATA GENERATION ENGINE
                    ============================================
                                          |
                                          v
                    ============================================
                    LAYER 2: DATA PREPROCESSING & INTEGRITY
                    ============================================
                                          |
                                          v
                    ============================================
                    LAYER 3: NETWORKX DIRECTED GRAPH ENGINE
                    ============================================
                                          |
                                          v
                    ============================================
                    LAYER 4: GRAPH & TEMPORAL FEATURE ENGINE
                    ============================================
                                          |
                                          v
                    ============================================
                    LAYER 5: XGBOOST RISK MODEL & RING ENGINE
                    ============================================
                             /                          \
                            v                            v
                 LAYER 6A: SHAP & GRAPH        LAYER 6B: COMMUTATIVE
                   REASON CODE ENGINE             DIFFIE-HELLMAN PSI
                            \                            /
                             v                          v
                    ============================================
                    LAYER 7: STREAMLIT INVESTIGATION DASHBOARD
                    ============================================
                                          |
                                          v
                              HUMAN FRAUD INVESTIGATOR
```

## 2. Component Breakdown

### Layer 1: Data Simulation (`src/simulator/generator.py`)
Generates realistic financial ecosystems for three simulated institutions:
- **Legitimate Archetypes:** Salaried, Gig-Workers, Digital Merchants, Students/First-Time Users, Regular P2P.
- **Mule Ring Archetypes:** Rapid Pass-Through, Fan-Out Splitters, Fan-In Collectors, Cross-Bank Multi-Hop Chains, Circular Layering.
- **Isolated Bank Ledgers:** Generates local perspectives (`bank_a.csv`, `bank_b.csv`, `bank_c.csv`) where institutions only see their own transactions.

### Layer 2: Preprocessing & Validation (`src/preprocessing/clean.py`, `src/utils/validation.py`)
- Standardizes schemas and datatypes.
- Enforces strict data integrity: non-negative amounts, absence of self-loops, duplicate transaction prevention.

### Layer 3: Directed Graph Engine (`src/graph/builder.py`)
- Builds directed multi-edge graphs ($G = (V, E)$).
- Nodes represent bank accounts annotated with institution and profile metadata.
- Directed edges represent monetary flow with timestamps and amounts.

### Layer 4: Feature Engine (`src/graph/features.py`)
- Extracts network topology: Fan-In, Fan-Out, PageRank, Clustering Coefficients.
- Computes temporal velocity: Pass-Through Ratio, Turnaround Time (seconds between incoming and outgoing funds), 1-hour and 24-hour transaction bursts.

### Layer 5: XGBoost & Ring Grouping (`src/models/train.py`, `src/graph/ring_detection.py`)
- **Group-Aware Splitting:** Rings are partitioned as atomic groups (`GroupShuffleSplit`) to prevent data leakage between train and test splits.
- **Class Imbalance:** Handled via `scale_pos_weight`.
- **Ring Discovery:** Identifies weakly connected components in the high-risk subgraph and classifies topology types.

### Layer 6: Explainability & Cryptographic Privacy
- **Explainability:** SHAP feature attribution combined with graph telemetry to generate human-readable multi-modal reason codes.
- **Privacy:** Commutative Diffie-Hellman Private Set Intersection (RFC 3526 2048-bit MODP) allowing Bank A, Bank B, and Bank C to discover common suspicious entities without sharing transaction records.

### Layer 7: Interactive Investigation Interface (`app/dashboard.py`)
- Overview, interactive network graph, account deep-dive, PSI demonstration, and investigator triage queue.
