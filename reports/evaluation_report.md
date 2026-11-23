# RINGTRACE AI — Comprehensive System Evaluation Report

**Evaluation Date:** 2026-11-22  
**Target Ecosystem:** Indian Digital Payments / UPI-like Transactions  
**Target Environment:** 3 Simulated Banks (Bank A, Bank B, Bank C)  
**Evaluation Mode:** Held-Out Unseen Data (Ring-Group Aware Split)  

---

## 1. Executive Summary of Performance

| Metric | Score | Target / Benchmark | Status |
|---|:---:|:---:|:---:|
| **Accuracy** | **1.0000** | > 0.9000 | Passed |
| **Precision** | **1.0000** | > 0.8500 | Passed |
| **Recall (Sensitivity)** | **1.0000** | > 0.8500 | Passed |
| **F1-Score** | **1.0000** | > 0.8500 | Passed |
| **False Positive Rate (FPR)** | **0.0000** | < 0.0500 | Passed |
| **PR-AUC** | **1.0000** | > 0.8800 | Passed |
| **ROC-AUC** | **1.0000** | > 0.9000 | Passed |

---

## 2. Confusion Matrix & Decision Breakdown

```
===================================================================
                       PREDICTED CLASS
                 Legitimate (0)        Mule Alert (1)
ACTUAL   ----------------------------------------------------------
Legitimate (0)   TN = 1035   (Cleared)    FP = 0      (False Alarm)
Mule (1)         FN = 0      (Missed)     TP = 165    (Detected)
===================================================================
```

---
## 4. False Positive Analysis Across Legitimate Customer Profiles

Evaluating detection rates across legitimate profiles to guarantee that gig workers, digital merchants, and first-time students are not unfairly penalized:

| Customer Profile | Total Accounts | Legitimate Count | False Positives | Profile FPR | Avg Risk Score |
|---|:---:|:---:|:---:|:---:|:---:|
| **GIG_WORKER** | 208 | 208 | 0 | 0.0000 | 0.0014 |
| **MERCHANT** | 205 | 205 | 0 | 0.0000 | 0.0014 |
| **MULE_SUSPECT** | 165 | 0 | 0 | 0.0000 | 0.9986 |
| **REGULAR_P2P** | 157 | 157 | 0 | 0.0000 | 0.0014 |
| **SALARIED** | 291 | 291 | 0 | 0.0000 | 0.0014 |
| **STUDENT_FIRST_TIME** | 174 | 174 | 0 | 0.0000 | 0.0014 |

---
## 5. Comparative Baseline Experiments (PRD Section 16.8)

| Evaluation Aspect | Exp A: Isolated Banks | Exp B: Combined Graph | Exp C: Combined Graph + PSI |
|---|:---:|:---:|:---:|
| **Precision** | 0.1731 | 1.0000 | **1.0000** |
| **Recall** | 0.4061 | 1.0000 | **1.0000** |
| **F1-Score** | 0.2428 | 1.0000 | **1.0000** |
| **False Positive Rate** | 0.3092 | 0.0000 | **0.0000** |
| **PR-AUC** | 0.1844 | 1.0000 | **1.0000** |

> **Key Finding:** Isolated bank monitoring misses multi-hop cross-bank laundering chains due to fragmented visibility. Combining graph network analysis with privacy-preserving matching (PSI) provides significant recall and precision improvements without sharing raw customer ledgers.

---
## 7. Generated Visualizations

The following publication-grade charts have been generated in `reports/figures/`:
1. `reports/figures/roc_curve.png`: Receiver Operating Characteristic (ROC) curve.
2. `reports/figures/pr_curve.png`: Precision-Recall curve under class imbalance.
3. `reports/figures/confusion_matrix.png`: Annotated classification heatmap.
4. `reports/figures/profile_fpr_analysis.png`: FPR across gig workers, merchants, and students.
5. `reports/figures/cross_bank_performance.png`: Performance across Bank A, Bank B, and Bank C slices.
