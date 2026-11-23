# RINGTRACE AI - Model Comparison and Benchmarking Report
**Evaluation Split:** 905 Train Samples (130 mules) | 295 Test Samples (35 mules)
**Crown Champion Model:** `Random Forest`

## 1. Performance Comparison Matrix

| Algorithm | Accuracy | Precision | Recall | F1-Score | PR-AUC | ROC-AUC | FPR | Status |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Random Forest** | 1.0000 | 1.0000 | 1.0000 | **1.0000** | 1.0000 | 1.0000 | 0.0000 | 🏆 Champion |
| **XGBoost** | 1.0000 | 1.0000 | 1.0000 | **1.0000** | 1.0000 | 1.0000 | 0.0000 | Baseline |
| **Logistic Regression** | 1.0000 | 1.0000 | 1.0000 | **1.0000** | 1.0000 | 1.0000 | 0.0000 | Baseline |
| **Isolation Forest** | 0.9356 | 0.6481 | 1.0000 | **0.7865** | 0.8750 | 0.9880 | 0.0731 | Baseline |

## 2. Confusion Matrices

### Random Forest
- **True Negatives (Legitimate Correct):** 260
- **False Positives (False Alarms):** 0
- **False Negatives (Missed Mules):** 0
- **True Positives (Mules Detected):** 35

### XGBoost
- **True Negatives (Legitimate Correct):** 260
- **False Positives (False Alarms):** 0
- **False Negatives (Missed Mules):** 0
- **True Positives (Mules Detected):** 35

### Logistic Regression
- **True Negatives (Legitimate Correct):** 260
- **False Positives (False Alarms):** 0
- **False Negatives (Missed Mules):** 0
- **True Positives (Mules Detected):** 35

### Isolation Forest
- **True Negatives (Legitimate Correct):** 241
- **False Positives (False Alarms):** 19
- **False Negatives (Missed Mules):** 0
- **True Positives (Mules Detected):** 35
