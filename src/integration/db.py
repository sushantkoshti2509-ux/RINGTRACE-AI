"""
Database abstraction layer for RINGTRACE AI Step 3: Multi-Bank Data Integration.
Provides SQLAlchemy ORM models and session management supporting both
PostgreSQL (production) and zero-configuration SQLite (local prototype).
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
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
