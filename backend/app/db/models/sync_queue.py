from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from .base import Base

class SyncQueue(Base):
    __tablename__ = "sync_queue"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    entity_type = Column(String, nullable=False)
    action = Column(String, nullable=False)
    synced = Column(Boolean, default=False)
    payload = Column(JSON, nullable=False)

    owner = relationship("User", back_populates="sync_queue")