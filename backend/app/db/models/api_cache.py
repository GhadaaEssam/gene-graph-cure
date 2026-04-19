from sqlalchemy import Column, Integer, String, DateTime, JSON
from datetime import datetime
from .base import Base

class APICache(Base):
    __tablename__ = "api_cache"

    id = Column(Integer, primary_key=True, index=True)
    endpoint = Column(String, unique=True, index=True, nullable=False)
    cached_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    response_data = Column(JSON, nullable=False)