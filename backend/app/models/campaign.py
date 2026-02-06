import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Boolean, ForeignKey, Enum, Float, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base
import enum

class CampaignStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"

class TargetType(str, enum.Enum):
    URL = "URL"
    WA_GROUP = "WA_GROUP"

class AssignmentStatus(str, enum.Enum):
    PENDING = "PENDING"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"

class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    name = Column(String, nullable=False)
    status = Column(String, default=CampaignStatus.DRAFT.value)
    start_date = Column(DateTime, nullable=True)
    budget_cap = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    tenant = relationship("Tenant", back_populates="campaigns")
    targets = relationship("CampaignTarget", back_populates="campaign", cascade="all, delete-orphan")
    assignments = relationship("Assignment", back_populates="campaign")

class CampaignTarget(Base):
    __tablename__ = "campaign_targets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id"), nullable=False)
    type = Column(String, default=TargetType.URL.value)
    target_value = Column(String, nullable=False) # The URL or Group ID
    description = Column(String, nullable=True)

    campaign = relationship("Campaign", back_populates="targets")
    tracking_links = relationship("TrackingLink", back_populates="target")

class Assignment(Base):
    __tablename__ = "assignments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id"), nullable=False)
    status = Column(String, default=AssignmentStatus.PENDING.value)
    proof_data = Column(JSON, nullable=True) # URLs to screenshots, etc.
    created_at = Column(DateTime, default=datetime.utcnow)

    agent = relationship("User", back_populates="assignments")
    campaign = relationship("Campaign", back_populates="assignments")
