from sqlalchemy import Column, Integer, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class PredictionDetails(Base):
    __tablename__ = "prediction_details"
    
    id = Column(Integer, primary_key=True, index=True)
    prediction_id = Column(Integer, ForeignKey("prediction_history.id"), nullable=False, unique=True)
    last_synced = Column(DateTime, default=datetime.utcnow)
    core_genes = Column(JSON) 
    pathways = Column(JSON) 
    alternative_drugs = Column(JSON) 

    prediction = relationship("PredictionHistory", back_populates="details")