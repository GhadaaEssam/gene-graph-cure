from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class PredictionHistory(Base):
    __tablename__ = "prediction_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    analysis_code = Column(String, unique=True, index=True)
    cancer_type = Column(String)
    drug_name = Column(String)
    prediction_result = Column(String)
    confidence_score = Column(Float)
    analysis_date = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="predictions")
    details = relationship("PredictionDetails", back_populates="prediction", uselist=False, cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="prediction", cascade="all, delete-orphan")