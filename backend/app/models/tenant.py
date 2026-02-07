import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Boolean, ForeignKey, Enum, Float
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base
import enum

class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    AGENT = "AGENT"

class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    plan_tier = Column(String, default="BASIC")
    created_at = Column(DateTime, default=datetime.utcnow)

    users = relationship("User", back_populates="tenant")
    campaigns = relationship("Campaign", back_populates="tenant")

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    role = Column(String, default=UserRole.AGENT.value) # Storing as string for simplicity with Enum
    phone = Column(String, nullable=False, unique=True)
    name = Column(String, nullable=False)
    current_score = Column(Integer, default=0)
    wallet_balance = Column(Float, default=0.0)
    hashed_password = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Activity tracking (for inactivity alerts)
    last_activity_at = Column(DateTime, default=datetime.utcnow)
    tutorial_completed = Column(Boolean, default=False)
    notification_token = Column(String, nullable=True)  # For push notifications

    tenant = relationship("Tenant", back_populates="users")
    assignments = relationship("Assignment", back_populates="agent")
    tracking_links = relationship("TrackingLink", back_populates="agent")
    
    # New relationships for contact system
    vcf_batches = relationship("VcfBatch", back_populates="agent")
    progress_reports = relationship("AgentProgress", back_populates="agent")

