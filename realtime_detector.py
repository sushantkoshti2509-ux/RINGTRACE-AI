"""
RINGTRACE AI - Step 7: Real-Time Fraud Detection System CLI Runner.
Simulates real-time multi-bank transaction streaming from Bank A, Bank B, and Bank C,
evaluates fraud risk probabilities in milliseconds, categorizes operational tiers,
and launches the low-latency FastAPI detection service.
"""

import sys
import time
import argparse
from pathlib import Path
import pandas as pd

# Setup paths
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import config
from src.realtime.detector import RealtimeFraudDetector


def print_banner(model_name: str):
    print("=" * 82)
    print("⚡ RINGTRACE AI - STEP 7: REAL-TIME MULTI-BANK FRAUD DETECTION SYSTEM")
    print("• Scope: Live Stream Scoring for Bank A, Bank B, and Bank C")
    print(f"• Active Champion Model: {model_name}")
    print("• Latency SLA: Sub-10ms Automated Transaction Risk Scoring")
    print("=" * 82)


def run_simulation(count: int = 40, delay: float = 0.05, model_type: str = None):
    detector = RealtimeFraudDetector(model_type=model_type)
    print_banner(detector.active_model_name)

    # Ingest candidate stream from transactions.csv or synthetic generator
    tx_path = config.PROCESSED_DATA_DIR / "transactions.csv"
    if not tx_path.exists():
        print("❌ Error: Missing transactions.csv. Please run Step 1 & 2 first.")
        sys.exit(1)

    df_tx = pd.read_csv(tx_path)

    # Sample a mixture of legitimate and suspicious transactions to demonstrate all risk tiers
    suspicious_samples = df_tx[df_tx["is_suspicious"] == 1].head(count // 3)
    legit_samples = df_tx[df_tx["is_suspicious"] == 0].head(count - len(suspicious_samples))
    stream_sample = pd.concat([suspicious_samples, legit_samples]).sample(frac=1.0, random_state=42).reset_index(drop=True)

    print(f"\n[1/3] Initializing In-Memory Detection Engine...")
    print(f"  • Preloaded Accounts: {len(detector.account_profiles):,} profiles")
    print(f"  • Simulating Live Inbound Stream: {len(stream_sample)} transactions across Bank A, B, and C\n")

    print("[2/3] Live Transaction Stream Monitoring:")
    print("-" * 82)
    print(f"| {'Transaction':<14} | {'Bank':<8} | {'Risk Level':<12} | {'Status':<16} | {'Latency':<8} |")
    print("-" * 82)

    results = []
    for _, row in stream_sample.iterrows():
        tx_dict = {
            "transaction_id": row["transaction_id"],
            "sender_account": row["sender_account"],
            "receiver_account": row["receiver_account"],
            "sender_bank": row["sender_bank"],
            "receiver_bank": row["receiver_bank"],
            "amount": row["amount"],
            "timestamp": row["timestamp"],
        }

        res = detector.process_transaction(tx_dict)
        results.append(res)

        # Color-coded indicator in terminal
        status = res["status"]
        risk_lvl = res["risk_level"]
        bank = res["bank_id"]
        tx_id = res["transaction_id"]
        lat = f"{res['latency_ms']:.1f}ms"

        # Format row to match PRD specification
        print(f"| {tx_id:<14} | {bank:<8} | {risk_lvl:<12} | {status:<16} | {lat:<8} |")

        if delay > 0:
            time.sleep(delay)

    print("-" * 82)

    # 3. Stream Summary
    stats = detector.get_summary_stats()
    print("\n[3/3] Real-Time Streaming Performance Summary:")
    print("=" * 82)
    print(f"  • Total Transactions Analyzed:  {stats['total_processed']}")
    print(f"  • High Risk (Suspicious):        {stats['high_risk_suspicious']} (Action: Automated Alert & Investigation Queue)")
    print(f"  • Medium Risk (Review Required): {stats['medium_risk_review']} (Action: Step-Up Auth / Flagged for Review)")
    print(f"  • Low Risk (Normal):             {stats['low_risk_normal']} (Action: Instant Frictionless Approval)")
    print(f"  • Average Detection Latency:    {stats['avg_latency_ms']:.2f} ms")
    print(f"  • Audit Logs Persisted:         ringtrace_integrated.db -> realtime_detection_logs")
    print("=" * 82)


def main():
    parser = argparse.ArgumentParser(
        description="RINGTRACE AI - Step 7: Real-Time Fraud Detection System."
    )
    parser.add_argument(
        "--simulate",
        action="store_true",
        default=True,
        help="Run real-time multi-bank transaction stream simulation (default: True)",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=40,
        help="Number of transactions to stream in simulation (default: 40)",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=0.03,
        help="Delay between stream arrivals in seconds (default: 0.03s)",
    )
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        choices=["random_forest", "xgboost"],
        help="Override active detection model",
    )
    parser.add_argument(
        "--serve",
        action="store_true",
        help="Launch the FastAPI real-time REST API server",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port number for FastAPI server (default: 8000)",
    )

    args = parser.parse_args()

    if args.serve:
        print(f"\n🚀 Launching Real-Time Fraud Detection API on http://0.0.0.0:{args.port}...")
        import uvicorn
        from src.integration.api import app
        uvicorn.run(app, host="0.0.0.0", port=args.port)
    else:
        run_simulation(count=args.count, delay=args.delay, model_type=args.model)


if __name__ == "__main__":
    main()
