from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from .base import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)

    # Relationships mapped via string names
    tokens = relationship("JWTToken", back_populates="owner", cascade="all, delete-orphan")
    sessions = relationship("UserSession", back_populates="owner", cascade="all, delete-orphan")
    dashboard = relationship("DashboardData", back_populates="owner", uselist=False, cascade="all, delete-orphan")
    predictions = relationship("PredictionHistory", back_populates="owner", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="owner", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="owner", cascade="all, delete-orphan")
    sync_queue = relationship("SyncQueue", back_populates="owner", cascade="all, delete-orphan")