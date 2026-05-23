"""
ADRS Database Tables — SQLAlchemy Models
PostgreSQL schema for storing and caching drug recommendations.
Drug weights (SD, Reversal, Coverage, Gene Overlap) included per request.
"""

import importlib
from pathlib import Path
from sqlalchemy import (
    Column, String, Float, Integer, Boolean,
    DateTime, JSON, Text, ForeignKey, Index,
    create_engine
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy.sql import func
from datetime import datetime
import os

load_dotenv = None
try:
    dotenv = importlib.import_module("dotenv")
    load_dotenv = dotenv.load_dotenv
except ImportError:
    pass

if load_dotenv is not None:
    load_dotenv(Path(__file__).resolve().parents[2] / ".env")

Base = declarative_base()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:ghpostgres@localhost:5432/gc_pge_db"
)



# ── Table 1: Alternative Drugs Results ────────────────────────────
class AlternativeDrugsResult(Base):
    """
    Stores each ADRS recommendation result per patient per resistant drug.
    One row = one complete recommendation session.
    """
    __tablename__ = "alternative_drugs_results"

    id              = Column(Integer, primary_key=True, autoincrement=True)
    patient_id      = Column(String(255), nullable=False, index=True)
    resistant_drug  = Column(String(255), nullable=False)
    timestamp       = Column(DateTime, default=datetime.utcnow, nullable=False)
    threshold_used  = Column(Float, default=0.5)
    total_candidates= Column(Integer)
    cached          = Column(Boolean, default=False)

    # Top pathways and genes used (stored as JSON arrays)
    dysregulated_pathways = Column(JSON)   # List[str]
    core_genes            = Column(JSON)   # List[str]

    # LLM context packet
    patient_summary   = Column(Text)
    gene_hit_summary  = Column(Text)

    # Relationship to individual drug recommendations
    recommendations = relationship(
        "DrugRecommendationRecord",
        back_populates="result",
        cascade="all, delete-orphan",
        order_by="DrugRecommendationRecord.rank"
    )

    __table_args__ = (
        Index("idx_patient_drug", "patient_id", "resistant_drug"),
    )

    def __repr__(self):
        return (
            f"<AlternativeDrugsResult "
            f"patient={self.patient_id} "
            f"resistant_to={self.resistant_drug} "
            f"timestamp={self.timestamp}>"
        )


# ── Table 2: Individual Drug Recommendation Records ───────────────
class DrugRecommendationRecord(Base):
    """
    One row per recommended drug per result.
    Stores all score components (weights) for each drug.
    """
    __tablename__ = "drug_recommendation_records"

    id        = Column(Integer, primary_key=True, autoincrement=True)
    result_id = Column(
        Integer,
        ForeignKey("alternative_drugs_results.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    rank = Column(Integer, nullable=False)   # 1 = top drug, 5 = last

    # Drug identity
    drug_name  = Column(String(500), nullable=False)
    drug_id    = Column(String(50))          # DrugBank ID e.g. DB00530

    # ── Score components (the "weights") ──────────────────────────
    sd_score         = Column(Float, nullable=False)   # final composite score
    reversal_score   = Column(Float)                   # IC50-based potency
    pathway_coverage = Column(Float)                   # pathway intersection
    gene_overlap     = Column(Float)                   # gene intersection
    weights_used     = Column(String(100))             # e.g. "standard (0.4R+0.3C+0.3G)"
    mean_ic50_uM     = Column(Float)                   # raw IC50 in µM

    # Drug metadata
    targeted_genes    = Column(JSON)    # List[str]
    targeted_pathways = Column(JSON)    # List[str]
    mechanism_of_action = Column(Text)

    result = relationship("AlternativeDrugsResult", back_populates="recommendations")

    def __repr__(self):
        return (
            f"<DrugRecommendationRecord "
            f"rank={self.rank} "
            f"drug={self.drug_name} "
            f"sd={self.sd_score}>"
        )


# ── Database connection helpers ───────────────────────────────────

def get_engine():
    return create_engine(DATABASE_URL, echo=False)


def get_session_factory():
    engine = get_engine()
    return sessionmaker(bind=engine)


def create_tables():
    """Create all tables if they don't exist. Run once at startup."""
    engine = get_engine()
    Base.metadata.create_all(engine)
    return engine