# RINGTRACE AI - Model Comparison and Benchmarking Report
**Evaluation Split:** 90 Train Samples (12 mules) | 30 Test Samples (3 mules)
**Crown Champion Model:** `Random Forest`

## 1. Performance Comparison Matrix

| Algorithm | Accuracy | Precision | Recall | F1-Score | PR-AUC | ROC-AUC | FPR | Status |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Random Forest** | 1.0000 | 1.0000 | 1.0000 | **1.0000** | 1.0000 | 1.0000 | 0.0000 | 🏆 Champion |
| **XGBoost** | 1.0000 | 1.0000 | 1.0000 | **1.0000** | 1.0000 | 1.0000 | 0.0000 | Baseline |
| **Logistic Regression** | 1.0000 | 1.0000 | 1.0000 | **1.0000** | 1.0000 | 1.0000 | 0.0000 | Baseline |
| **Isolation Forest** | 1.0000 | 1.0000 | 1.0000 | **1.0000** | 1.0000 | 1.0000 | 0.0000 | Baseline |

## 2. Confusion Matrices

### Random Forest
- **True Negatives (Legitimate Correct):** 27
- **False Positives (False Alarms):** 0
- **False Negatives (Missed Mules):** 0
- **True Positives (Mules Detected):** 3

### XGBoost
- **True Negatives (Legitimate Correct):** 27
- **False Positives (False Alarms):** 0
- **False Negatives (Missed Mules):** 0
- **True Positives (Mules Detected):** 3

### Logistic Regression
- **True Negatives (Legitimate Correct):** 27
- **False Positives (False Alarms):** 0
- **False Negatives (Missed Mules):** 0
- **True Positives (Mules Detected):** 3

### Isolation Forest
- **True Negatives (Legitimate Correct):** 27
- **False Positives (False Alarms):** 0
- **False Negatives (Missed Mules):** 0
- **True Positives (Mules Detected):** 3
