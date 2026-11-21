"""
RINGTRACE AI - Step 7: Real-Time Fraud Detection System Module.
Provides low-latency stream processing, real-time feature extraction,
multi-tier risk categorization (Low, Medium, High), and audit logging.
"""

from src.realtime.detector import RealtimeFraudDetector

__all__ = ["RealtimeFraudDetector"]
