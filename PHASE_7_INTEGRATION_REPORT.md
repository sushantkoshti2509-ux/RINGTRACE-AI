# PHASE 7 INTEGRATION REPORT: GRAPH NEURAL NETWORK (GNN) ARCHITECTURE
## Advanced Four-Bank Mule Ring Detection Platform

---

### 1. Existing System Architecture Baseline

The current platform successfully integrates six intelligence and defense layers operating across four synthetic clearing institutions (**Bank A**, **Bank B**, **Bank C**, **Bank D**):

- **Data & Ingestion**: Consolidated dual-ledger reconciliation engine (`src/integration/integrator.py`) managing 27,743 transactions across 1,200 accounts (₹8.04 Cr volume).
- **Global Identifiers**: Globally unique, bank-qualified identifiers (`BANK_A:BNK_A_ACC_00001`, `BANK_B:BNK_B_ACC_00002`).
- **Graph Foundation**: Directed multigraph constructed in NetworkX (`src/graph/builder.py`, `src/cross_bank_network/graph_builder.py`) tracking edge weights, timestamps, and cross-bank attributes.
- **ML Detection Engine**: XGBoost with ring group-aware stratification preventing cross-fold synthetic ring leakage (`src/models/train.py`, `src/models/predict.py`).
- **Explainable AI (XAI)**: TreeSHAP explanations with natural-language reason code generation (`src/explainable_ai/`).
- **Investigation Copilot**: Evidence-grounded case management with automated regulatory SAR narrative drafting and ReportLab PDF export (`src/investigation_assistant/`).
- **Real-Time Stream Processing**: Sub-15ms incremental scoring and deduplicated alert lifecycle engine (`src/realtime/`).
- **Interception & Digital Twin**: Graph bottleneck analysis, graduated regulatory countermeasures, chronological replay, and what-if scenario simulation (`src/interception/`, `src/platform_features/`).

---

### 2. Recommended GNN Architecture

Financial fraud networks exploit structural blindspots across bank borders. Traditional tabular ML models treat transactions as independent samples or aggregate static neighborhood features. In contrast, **Graph Neural Networks (GNNs)** propagate relational messages directly across inter-bank edges.

#### A. Model Topologies
1. **Baseline Model: Edge-Aware GraphSAGE / GINE (Graph Isomorphism Network with Edge Features)**
   - Formulates message passing where edge vectors (transfer amount, timestamp delta, cross-bank flag, transaction type) modulate node embeddings:
     $$h_v^{(k)} = \text{MLP}^{(k)} \left( (1 + \epsilon^{(k)}) h_v^{(k-1)} + \sum_{u \in \mathcal{N}(v)} \text{ReLU}\left(h_u^{(k-1)} + e_{uv}\right) \right)$$
   - Superior inductive capability for generalizing to newly opened or previously unseen accounts.
2. **Experimental Comparison: GATv2 (Graph Attention Network v2)**
   - Computes dynamic, multi-head attention coefficients $\alpha_{uv}$ over counterparties:
     $$\alpha_{uv} = \frac{\exp\left(\mathbf{a}^\top \text{LeakyReLU}\left(\mathbf{W}_s h_u + \mathbf{W}_t h_v + \mathbf{W}_e e_{uv}\right)\right)}{\sum_{k \in \mathcal{N}(u)} \exp\left(\mathbf{a}^\top \text{LeakyReLU}\left(\mathbf{W}_s h_u + \mathbf{W}_t h_k + \mathbf{W}_e e_{uk}\right)\right)}$$
   - Fixes the static attention problem in original GAT, allowing the model to prioritize suspicious high-velocity burst nodes.

#### B. Multi-Task Prediction Heads
- **Account-Level Node Head**: Multi-layer perceptron with Sigmoid activation outputting account mule risk $P(\text{mule} \mid v)$.
- **Transaction-Level Edge Head**: Bilinear / concat MLP outputting transaction fraud probability $P(\text{fraud} \mid e_{uv})$.
- **Network/Ring Subgraph Head**: Global pooling (Mean + Max readout) outputting candidate ring threat score $P(\text{mule\_ring} \mid G_{\text{ring}})$.

---

### 3. Feature Pipeline & Data Representation

#### A. Node Feature Vector ($d_{\text{node}} = 16$)
1. Normalized Inbound Volume ($\log_{10}(1 + \text{vol}_{\text{in}})$)
2. Normalized Outbound Volume ($\log_{10}(1 + \text{vol}_{\text{out}})$)
3. Total Transaction Frequency
4. In-Degree Centrality
5. Out-Degree Centrality
6. Net Flow Drainage Ratio ($\frac{\text{vol}_{\text{out}} - \text{vol}_{\text{in}}}{\text{vol}_{\text{in}} + \epsilon}$)
7. Pass-Through Turnover Rate ($> 90\%$ drainage signature)
8. Mean Turnaround Latency (seconds)
9. Minimum Inter-Hop Time Gap
10. PageRank Centrality
11. Local Clustering Coefficient
12. One-Hot Bank Representation (Bank A, Bank B, Bank C, Bank D)

#### B. Edge Feature Vector ($d_{\text{edge}} = 8$)
1. Normalized Transaction Amount ($\log_{10}(1 + \text{amount})$)
2. Normalized Amount Z-score
3. Is Cross-Bank Indicator ($0$ = intra-bank, $1$ = inter-bank)
4. Bank Pair Code (16 directed combinations $A \rightarrow B, B \rightarrow C$, etc.)
5. Transaction Type (UPI, IMPS, NEFT, RTGS)
6. Transaction Status (SUCCESS, PENDING, REVERSED)
7. Temporal Hour of Day (Sine & Cosine cyclical encodings)

---

### 4. Graph-Based Explainability (GNNExplainer)

Unlike tabular SHAP which explains isolated feature values, **GNNExplainer** identifies the compact subgraph and relational feature masks that maximize the mutual information with the GNN prediction:
$$\max_{G_s, X_s} \text{MI}\left(Y, (G_s, X_s)\right) = H(Y) - H\left(Y \mid G = G_s, X = X_s\right)$$
Outputs:
- Top influential neighboring accounts.
- Critical transaction edges in the laundering path.
- Essential relational features.
- Visual explanation subgraph for fraud investigators.

---

### 5. New Dependencies

| Package | Minimum Version | Installation Target | Compatibility |
| :--- | :--- | :--- | :--- |
| `torch` | $\ge 2.2.0$ | `.venv` | macOS ARM64 Apple Silicon (MPS / CPU) |
| `torch-geometric` | $\ge 2.5.0$ | `.venv` | Universal PyPI wheels, zero C++ compilation |

---

### 6. Architectural File Blueprint

```text
src/
├── gnn/                                # NEW: Phase 7 Graph Neural Network Module
│   ├── __init__.py                     # Package exports
│   ├── dataset.py                      # PyG Data / HeteroData converter & group splits
│   ├── features.py                     # Dedicated node & edge normalizers
│   ├── models.py                       # Edge-aware GraphSAGE, GINE, and GATv2 architectures
│   ├── trainer.py                      # Reproducible training pipeline & evaluation
│   ├── inference.py                    # Independent inference service with model versioning
│   ├── explainer.py                    # Graph-specific explainability (GNNExplainer)
│   └── api.py                          # Dedicated FastAPI router (/api/v1/gnn)
frontend/
└── src/
    └── views/
        └── GNNIntelligenceView.jsx     # NEW: GNN Intelligence Center React workstation
tests/
└── test_gnn.py                         # NEW: Comprehensive GNN unit, integration & regression tests
```

---

### 7. Database Integration

Added to `src/integration/db.py`:
- `GNNModelRunModel` (`gnn_model_runs` table): Stores model checkpoints, hyperparameter configurations, and evaluation metrics (PR-AUC, ROC-AUC, F1, Latency).
- `GNNPredictionModel` (`gnn_predictions` table): Stores inferred account, transaction, and network risk probabilities alongside generated explanation subgraphs.

---

### 8. API Contract (`/api/v1/gnn`)

- `GET /api/v1/gnn/metadata`: Model type, checkpoint version, parameter count, device (CPU/MPS).
- `GET /api/v1/gnn/metrics`: Evaluated performance (Precision, Recall, F1, PR-AUC, ROC-AUC, FPR, Latency).
- `GET /api/v1/gnn/comparison`: Side-by-side performance: Existing ML (XGBoost) vs Graph Rules vs GNN.
- `GET /api/v1/gnn/predictions/accounts`: Account-level predictions with GNN risk scores.
- `GET /api/v1/gnn/predictions/transactions`: Transaction-level edge classifications.
- `GET /api/v1/gnn/predictions/networks`: Subgraph-level ring threat rankings.
- `POST /api/v1/gnn/explain`: GNNExplainer subgraph, neighbor attributions, and edge masks.
- `POST /api/v1/gnn/predict/account`: Real-time GNN inference for a specific account.

---

### 9. Integration Risks & Mitigation Strategies

1. **Risk: Startup Latency & Memory Overhead**
   - *Mitigation*: PyTorch and GNN models are lazily loaded on first request. Models are lightweight (2 layers, 64 hidden units, $< 150\text{k}$ parameters), executing inference in $< 12\text{ms}$.
2. **Risk: Dependency / Service Failure**
   - *Mitigation*: The GNN module is decoupled. If PyTorch is unavailable or disabled, the system gracefully falls back to the existing XGBoost and graph rule engines.
3. **Risk: Target / Synthetic Leakage**
   - *Mitigation*: Group-aware splitting ensures that accounts belonging to the same candidate synthetic ring are isolated exclusively within either the training or testing partition.
4. **Risk: Double-Counting in Risk Engine**
   - *Mitigation*: Individual scores are preserved independently. The composite risk score combines distinct signals using calibrated validation weights without double-counting collinear indicators.

---

### 10. Verification & Testing Strategy

- **Component Tests**: PyG data creation, node/edge tensor generation, forward pass across GraphSAGE, GINE, and GATv2.
- **Explainability Tests**: Verification that GNNExplainer returns valid edge masks and subgraphs.
- **Inference Tests**: Cold-start evaluation, unseen account inference, and error handling.
- **Regression Tests**: All 66 existing unit and integration tests must pass with 100% fidelity.
