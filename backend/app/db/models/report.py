from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class Report(Base):
    __tablename__ = "reports"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    prediction_id = Column(Integer, ForeignKey("prediction_history.id"), nullable=False)
    report_code = Column(String, unique=True, index=True)
    file_url = Column(String)
    generated_date = Column(DateTime, default=datetime.utcnow)
    downloaded = Column(Boolean, default=False)

    owner = relationship("User", back_populates="reports")
    prediction = relationship("PredictionHistory", back_populates="reports")