"""
Database abstraction layer for RINGTRACE AI Step 3: Multi-Bank Data Integration.
Provides SQLAlchemy ORM models and session management supporting both
PostgreSQL (production) and zero-configuration SQLite (local prototype).
"""

from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timezone
import json
import os
import pandas as pd
from sqlalchemy import (
    create_engine,
    Column,
    String,
    Float,
    Integer,
    Boolean,
    DateTime,
    Text,
    Index,
    func,
)
from sqlalchemy.orm import declarative_base, sessionmaker, Session

import config

Base = declarative_base()


class IntegratedTransactionModel(Base):
    """Consolidated multi-bank transaction record table."""
    __tablename__ = "integrated_transactions"

    transaction_id = Column(String(64), primary_key=True, index=True)
    customer_id = Column(String(64), index=True, nullable=False)
    sender_account = Column(String(64), index=True, nullable=False)
    receiver_account = Column(String(64), index=True, nullable=False)
    sender_bank = Column(String(32), index=True, nullable=False)
    receiver_bank = Column(String(32), index=True, nullable=False)
    amount = Column(Float, nullable=False)
    timestamp = Column(String(32), index=True, nullable=False)
    transaction_type = Column(String(32), default="UPI_P2P")
    transaction_status = Column(String(32), default="SUCCESS")
    is_suspicious = Column(Integer, default=0, index=True)
    ring_id = Column(String(64), default="NONE", index=True)
    pattern_type = Column(String(64), default="NORMAL_P2P")
    participating_banks = Column(String(128), nullable=False)
    primary_source_bank = Column(String(32), nullable=False)
    reconciliation_status = Column(String(32), default="RECONCILED", index=True)
    is_cross_bank = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index("idx_tx_sender_rec", "sender_account", "receiver_account"),
        Index("idx_tx_banks", "sender_bank", "receiver_bank"),
        Index("idx_tx_time_amount", "timestamp", "amount"),
    )


class BankLedgerAuditModel(Base):
    """Audit metadata tracking per-bank ingestion batches."""
    __tablename__ = "bank_ledgers_audit"

    bank_id = Column(String(32), primary_key=True)
    raw_row_count = Column(Integer, default=0)
    reconciled_count = Column(Integer, default=0)
    unilateral_count = Column(Integer, default=0)
    total_volume = Column(Float, default=0.0)
    last_sync_time = Column(String(32), nullable=False)


class ReconciliationLogModel(Base):
    """Log table for cross-bank twin matching and audit discrepancies."""
    __tablename__ = "reconciliation_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    transaction_id = Column(String(64), index=True, nullable=False)
    discrepancy_type = Column(String(64), nullable=False)
    details = Column(Text, nullable=False)
    logged_at = Column(String(32), nullable=False)


class RealtimeDetectionLogModel(Base):
    """Audit log table for real-time transaction fraud predictions."""
    __tablename__ = "realtime_detection_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    transaction_id = Column(String(64), index=True, nullable=False)
    bank_id = Column(String(32), index=True, nullable=False)
    sender_account = Column(String(64), index=True, nullable=False)
    receiver_account = Column(String(64), index=True, nullable=False)
    amount = Column(Float, nullable=False)
    timestamp = Column(String(32), index=True, nullable=False)
    fraud_probability = Column(Float, nullable=False)
    risk_level = Column(String(32), index=True, nullable=False)  # Low, Medium, High
    status = Column(String(32), index=True, nullable=False)      # Normal, Review Required, Suspicious
    trigger_reasons = Column(String(512), default="[]")
    latency_ms = Column(Float, default=0.0)
    processed_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class FraudAlertModel(Base):
    """Centralized fraud alert table for Bank A, Bank B, and Bank C."""
    __tablename__ = "fraud_alerts"

    alert_id = Column(String(64), primary_key=True, index=True)
    transaction_id = Column(String(64), unique=True, index=True, nullable=False)
    bank_id = Column(String(32), index=True, nullable=False)
    sender_account = Column(String(64), index=True, nullable=False)
    receiver_account = Column(String(64), index=True, nullable=False)
    amount = Column(Float, nullable=False)
    timestamp = Column(String(32), index=True, nullable=False)
    fraud_probability = Column(Float, nullable=False)
    risk_level = Column(String(32), index=True, nullable=False)  # Low, Medium, High
    status = Column(String(32), index=True, default="Pending")    # Pending, Under Review, Resolved, Escalated
    trigger_reasons = Column(String(512), default="[]")
    recommendation = Column(Text, default="Suspicious transaction detected. Further investigation is recommended.")
    disclaimer = Column(String(128), default="Illustrative example, not actual transaction data.")
    assigned_to = Column(String(64), nullable=True)
    investigation_notes = Column(Text, default="[]")
    notified_channels = Column(String(256), default="[]")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index("idx_alert_bank_status", "bank_id", "status"),
        Index("idx_alert_risk_status", "risk_level", "status"),
    )


class DatabaseManager:
    """Manages database connection, table initialization, and high-performance ingestion."""

    def __init__(self, db_url: Optional[str] = None):
        # Prefer provided URL, then environment DATABASE_URL (for PostgreSQL), then default SQLite
        self.db_url = (
            db_url
            or os.getenv("DATABASE_URL")
            or config.DEFAULT_SQLITE_URL
        )

        # Standardize postgres:// to postgresql:// for SQLAlchemy compatibility if needed
        if self.db_url.startswith("postgres://"):
            self.db_url = self.db_url.replace("postgres://", "postgresql://", 1)

        connect_args = {"check_same_thread": False} if "sqlite" in self.db_url else {}
        self.engine = create_engine(self.db_url, connect_args=connect_args)
        self.SessionFactory = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.init_db()

    def init_db(self):
        """Creates tables if they do not already exist."""
        Base.metadata.create_all(bind=self.engine)

    def get_session(self) -> Session:
        """Returns a new SQLAlchemy session."""
        return self.SessionFactory()

    def save_integrated_transactions(self, df: pd.DataFrame, batch_size: int = 2000) -> int:
        """
        Persists integrated transactions DataFrame into database using bulk operations.
        Returns total number of rows inserted/updated.
        """
        if df.empty:
            return 0

        # Drop existing records to allow idempotent runs
        with self.get_session() as session:
            session.query(IntegratedTransactionModel).delete()
            session.commit()

        # Format dataframe columns to match ORM
        df_to_save = df.copy()
        if "participating_banks" in df_to_save.columns:
            if isinstance(df_to_save["participating_banks"].iloc[0], list):
                df_to_save["participating_banks"] = df_to_save["participating_banks"].apply(lambda x: ",".join(x))

        records = df_to_save.to_dict(orient="records")

        # Insert in chunks to optimize memory and connection limits
        total_inserted = 0
        with self.get_session() as session:
            for i in range(0, len(records), batch_size):
                chunk = records[i : i + batch_size]
                orm_objects = [
                    IntegratedTransactionModel(
                        transaction_id=str(r.get("transaction_id")),
                        customer_id=str(r.get("customer_id")),
                        sender_account=str(r.get("sender_account")),
                        receiver_account=str(r.get("receiver_account")),
                        sender_bank=str(r.get("sender_bank")),
                        receiver_bank=str(r.get("receiver_bank")),
                        amount=float(r.get("amount", 0.0)),
                        timestamp=str(r.get("timestamp")),
                        transaction_type=str(r.get("transaction_type", "UPI_P2P")),
                        transaction_status=str(r.get("transaction_status", "SUCCESS")),
                        is_suspicious=int(r.get("is_suspicious", 0)),
                        ring_id=str(r.get("ring_id", "NONE")),
                        pattern_type=str(r.get("pattern_type", "NORMAL_P2P")),
                        participating_banks=str(r.get("participating_banks", "")),
                        primary_source_bank=str(r.get("primary_source_bank", r.get("sender_bank"))),
                        reconciliation_status=str(r.get("reconciliation_status", "RECONCILED")),
                        is_cross_bank=bool(r.get("is_cross_bank", False)),
                    )
                    for r in chunk
                ]
                session.bulk_save_objects(orm_objects)
                session.commit()
                total_inserted += len(orm_objects)

        return total_inserted

    def save_audit_metrics(self, audit_records: List[Dict[str, Any]]):
        """Saves or updates per-bank audit summary rows."""
        with self.get_session() as session:
            session.query(BankLedgerAuditModel).delete()
            for rec in audit_records:
                audit_obj = BankLedgerAuditModel(
                    bank_id=rec["bank_id"],
                    raw_row_count=rec["raw_row_count"],
                    reconciled_count=rec["reconciled_count"],
                    unilateral_count=rec["unilateral_count"],
                    total_volume=rec["total_volume"],
                    last_sync_time=rec.get("last_sync_time", datetime.now(timezone.utc).isoformat()),
                )
                session.merge(audit_obj)
            session.commit()

    def query_transactions(
        self,
        bank_id: Optional[str] = None,
        is_suspicious: Optional[int] = None,
        min_amount: Optional[float] = None,
        max_amount: Optional[float] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """Queries integrated transactions with flexible filtering."""
        with self.get_session() as session:
            query = session.query(IntegratedTransactionModel)

            if bank_id:
                b_norm = bank_id.strip().upper()
                query = query.filter(
                    (IntegratedTransactionModel.sender_bank == b_norm)
                    | (IntegratedTransactionModel.receiver_bank == b_norm)
                )

            if is_suspicious is not None:
                query = query.filter(IntegratedTransactionModel.is_suspicious == is_suspicious)

            if min_amount is not None:
                query = query.filter(IntegratedTransactionModel.amount >= min_amount)

            if max_amount is not None:
                query = query.filter(IntegratedTransactionModel.amount <= max_amount)

            total_matches = query.count()
            rows = query.order_by(IntegratedTransactionModel.timestamp.desc()).offset(offset).limit(limit).all()

            return [
                {
                    "transaction_id": r.transaction_id,
                    "customer_id": r.customer_id,
                    "sender_account": r.sender_account,
                    "receiver_account": r.receiver_account,
                    "sender_bank": r.sender_bank,
                    "receiver_bank": r.receiver_bank,
                    "amount": r.amount,
                    "timestamp": r.timestamp,
                    "transaction_type": r.transaction_type,
                    "transaction_status": r.transaction_status,
                    "is_suspicious": r.is_suspicious,
                    "ring_id": r.ring_id,
                    "pattern_type": r.pattern_type,
                    "participating_banks": r.participating_banks.split(",") if r.participating_banks else [],
                    "primary_source_bank": r.primary_source_bank,
                    "reconciliation_status": r.reconciliation_status,
                    "is_cross_bank": r.is_cross_bank,
                }
                for r in rows
            ]

    def save_realtime_log(self, log_dict: Dict[str, Any]):
        """Persists a real-time transaction detection event into the audit table."""
        with self.get_session() as session:
            obj = RealtimeDetectionLogModel(
                transaction_id=str(log_dict.get("transaction_id")),
                bank_id=str(log_dict.get("bank_id", "BANK_A")),
                sender_account=str(log_dict.get("sender_account")),
                receiver_account=str(log_dict.get("receiver_account")),
                amount=float(log_dict.get("amount", 0.0)),
                timestamp=str(log_dict.get("timestamp")),
                fraud_probability=float(log_dict.get("fraud_probability", 0.0)),
                risk_level=str(log_dict.get("risk_level", "Low")),
                status=str(log_dict.get("status", "Normal")),
                trigger_reasons=json.dumps(log_dict.get("trigger_reasons", [])),
                latency_ms=float(log_dict.get("latency_ms", 0.0)),
            )
            session.add(obj)
            session.commit()

    def query_realtime_logs(
        self,
        bank_id: Optional[str] = None,
        risk_level: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """Queries real-time detection logs with optional filtering."""
        with self.get_session() as session:
            query = session.query(RealtimeDetectionLogModel)
            if bank_id:
                query = query.filter(RealtimeDetectionLogModel.bank_id == bank_id.upper())
            if risk_level:
                query = query.filter(RealtimeDetectionLogModel.risk_level == risk_level.capitalize())
            if status:
                query = query.filter(RealtimeDetectionLogModel.status == status)

            rows = query.order_by(RealtimeDetectionLogModel.id.desc()).offset(offset).limit(limit).all()
            return [
                {
                    "id": r.id,
                    "transaction_id": r.transaction_id,
                    "bank_id": r.bank_id,
                    "sender_account": r.sender_account,
                    "receiver_account": r.receiver_account,
                    "amount": r.amount,
                    "timestamp": r.timestamp,
                    "fraud_probability": r.fraud_probability,
                    "risk_level": r.risk_level,
                    "status": r.status,
                    "trigger_reasons": json.loads(r.trigger_reasons) if r.trigger_reasons else [],
                    "latency_ms": r.latency_ms,
                    "processed_at": r.processed_at.isoformat() if r.processed_at else None,
                }
                for r in rows
            ]

    # -------------------------------------------------------------
    # Step 8: Fraud Alert & Notification Management
    # -------------------------------------------------------------
    def save_alert(self, alert_dict: Dict[str, Any]) -> Tuple[Dict[str, Any], bool]:
        """
        Saves a fraud alert to the centralized database with duplicate prevention.
        Returns (alert_record, is_created). If alert for transaction_id already exists,
        is_created will be False and the existing record is returned without duplicating.
        """
        tx_id = str(alert_dict.get("transaction_id", "")).strip()
        with self.get_session() as session:
            existing = session.query(FraudAlertModel).filter(FraudAlertModel.transaction_id == tx_id).first()
            if existing:
                return self._alert_model_to_dict(existing), False

            clean_id = tx_id
            for prefix in ["TXN_", "TX_", "TXN", "TX"]:
                if clean_id.startswith(prefix):
                    clean_id = clean_id[len(prefix):]
                    break
            alert_id = alert_dict.get("alert_id") or f"ALT_{clean_id}"
            triggers = alert_dict.get("trigger_reasons", [])
            triggers_str = json.dumps(triggers) if isinstance(triggers, list) else str(triggers)
            notes = alert_dict.get("investigation_notes", [])
            notes_str = json.dumps(notes) if isinstance(notes, list) else str(notes)
            channels = alert_dict.get("notified_channels", [])
            channels_str = json.dumps(channels) if isinstance(channels, list) else str(channels)

            new_alert = FraudAlertModel(
                alert_id=alert_id,
                transaction_id=tx_id,
                bank_id=str(alert_dict.get("bank_id", "BANK_A")).upper().replace(" ", "_"),
                sender_account=str(alert_dict.get("sender_account", "UNKNOWN")),
                receiver_account=str(alert_dict.get("receiver_account", "UNKNOWN")),
                amount=float(alert_dict.get("amount", 0.0)),
                timestamp=str(alert_dict.get("timestamp", datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"))),
                fraud_probability=float(alert_dict.get("fraud_probability", 0.0)),
                risk_level=str(alert_dict.get("risk_level", "High")),
                status=str(alert_dict.get("status", "Pending")),
                trigger_reasons=triggers_str,
                recommendation=str(alert_dict.get("recommendation", "Suspicious transaction detected. Further investigation is recommended.")),
                disclaimer="Illustrative example, not actual transaction data.",
                assigned_to=alert_dict.get("assigned_to"),
                investigation_notes=notes_str,
                notified_channels=channels_str,
            )
            session.add(new_alert)
            session.commit()
            session.refresh(new_alert)
            return self._alert_model_to_dict(new_alert), True

    def get_alert(self, alert_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves single alert record by alert_id."""
        with self.get_session() as session:
            obj = session.query(FraudAlertModel).filter(FraudAlertModel.alert_id == alert_id).first()
            return self._alert_model_to_dict(obj) if obj else None

    def get_alert_by_transaction_id(self, tx_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves alert record by underlying transaction_id."""
        with self.get_session() as session:
            obj = session.query(FraudAlertModel).filter(FraudAlertModel.transaction_id == tx_id).first()
            return self._alert_model_to_dict(obj) if obj else None

    def update_alert_status(
        self,
        alert_id: str,
        new_status: str,
        notes: Optional[str] = None,
        updated_by: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Updates alert status (Pending, Under Review, Resolved, Escalated) and appends notes."""
        with self.get_session() as session:
            obj = session.query(FraudAlertModel).filter(FraudAlertModel.alert_id == alert_id).first()
            if not obj:
                return None

            obj.status = new_status
            obj.updated_at = datetime.now(timezone.utc)
            if updated_by:
                obj.assigned_to = updated_by

            if notes:
                existing_notes = json.loads(obj.investigation_notes) if obj.investigation_notes else []
                existing_notes.append({
                    "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
                    "author": updated_by or "Investigator",
                    "status_change": new_status,
                    "note": notes,
                })
                obj.investigation_notes = json.dumps(existing_notes)

            session.commit()
            session.refresh(obj)
            return self._alert_model_to_dict(obj)

    def query_alerts(
        self,
        bank_id: Optional[str] = None,
        risk_level: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """Queries alerts across Bank A, Bank B, and Bank C with multi-field filtering."""
        with self.get_session() as session:
            query = session.query(FraudAlertModel)
            if bank_id and bank_id.upper() != "ALL":
                query = query.filter(FraudAlertModel.bank_id == bank_id.upper())
            if risk_level and risk_level.upper() != "ALL":
                query = query.filter(FraudAlertModel.risk_level == risk_level.capitalize())
            if status and status.upper() != "ALL":
                query = query.filter(FraudAlertModel.status == status)

            rows = query.order_by(FraudAlertModel.created_at.desc()).offset(offset).limit(limit).all()
            return [self._alert_model_to_dict(r) for r in rows]

    def get_alert_stats(self) -> Dict[str, Any]:
        """Calculates multi-bank alert statistics and status breakdowns."""
        with self.get_session() as session:
            total = session.query(FraudAlertModel).count()
            pending = session.query(FraudAlertModel).filter(FraudAlertModel.status == "Pending").count()
            under_review = session.query(FraudAlertModel).filter(FraudAlertModel.status == "Under Review").count()
            escalated = session.query(FraudAlertModel).filter(FraudAlertModel.status == "Escalated").count()
            resolved = session.query(FraudAlertModel).filter(FraudAlertModel.status == "Resolved").count()

            high_risk = session.query(FraudAlertModel).filter(FraudAlertModel.risk_level == "High").count()
            medium_risk = session.query(FraudAlertModel).filter(FraudAlertModel.risk_level == "Medium").count()
            low_risk = session.query(FraudAlertModel).filter(FraudAlertModel.risk_level == "Low").count()

            by_bank = {
                "BANK_A": session.query(FraudAlertModel).filter(FraudAlertModel.bank_id == "BANK_A").count(),
                "BANK_B": session.query(FraudAlertModel).filter(FraudAlertModel.bank_id == "BANK_B").count(),
                "BANK_C": session.query(FraudAlertModel).filter(FraudAlertModel.bank_id == "BANK_C").count(),
            }

            return {
                "total_alerts": total,
                "pending": pending,
                "under_review": under_review,
                "escalated": escalated,
                "resolved": resolved,
                "high_risk": high_risk,
                "medium_risk": medium_risk,
                "low_risk": low_risk,
                "by_bank": by_bank,
            }

    @staticmethod
    def _alert_model_to_dict(r: FraudAlertModel) -> Dict[str, Any]:
        return {
            "alert_id": r.alert_id,
            "transaction_id": r.transaction_id,
            "bank_id": r.bank_id,
            "sender_account": r.sender_account,
            "receiver_account": r.receiver_account,
            "amount": r.amount,
            "timestamp": r.timestamp,
            "fraud_probability": r.fraud_probability,
            "risk_level": r.risk_level,
            "status": r.status,
            "trigger_reasons": json.loads(r.trigger_reasons) if r.trigger_reasons else [],
            "recommendation": r.recommendation,
            "disclaimer": r.disclaimer,
            "assigned_to": r.assigned_to,
            "investigation_notes": json.loads(r.investigation_notes) if r.investigation_notes else [],
            "notified_channels": json.loads(r.notified_channels) if r.notified_channels else [],
            "created_at": r.created_at.isoformat() if r.created_at else None,
            "updated_at": r.updated_at.isoformat() if r.updated_at else None,
        }
