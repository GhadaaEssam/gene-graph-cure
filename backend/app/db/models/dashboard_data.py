from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class DashboardData(Base):
    __tablename__ = "dashboard_data"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    role_type = Column(String)
    total_analyses = Column(Integer, default=0)
    recent_prediction = Column(String)
    cached_statistics = Column(JSON)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner = relationship("User", back_populates="dashboard")