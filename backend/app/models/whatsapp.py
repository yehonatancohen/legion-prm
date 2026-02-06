import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Boolean, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base
import enum

class WhatsappBatchStatus(str, enum.Enum):
    PENDING = "PENDING"
    ASSIGNED = "ASSIGNED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"

class WhatsappCampaign(Base):
    __tablename__ = "whatsapp_campaigns"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    file_name = Column(String, nullable=True) # Original uploaded filename
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    total_contacts = Column(Integer, default=0)
    
    # Relationships
    batches = relationship("WhatsappBatch", back_populates="campaign")

class WhatsappBatch(Base):
    # A chunk of contacts (VCF) assigned to an agent
    __tablename__ = "whatsapp_batches"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("whatsapp_campaigns.id"))
    agent_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    status = Column(String, default=WhatsappBatchStatus.PENDING.value)
    assigned_at = Column(DateTime, nullable=True)
    
    # Generated VCF file stored path
    vcf_file_path = Column(String, nullable=True)
    contact_count = Column(Integer, default=0)
    
    # Which group this agent is supposed to add these people to
    target_group_name = Column(String, nullable=True)

    # Relationships
    campaign = relationship("WhatsappCampaign", back_populates="batches")
    agent = relationship("app.models.tenant.User")
    daily_reports = relationship("WhatsappDailyReport", back_populates="batch")

class WhatsappDailyReport(Base):
    __tablename__ = "whatsapp_daily_reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    batch_id = Column(UUID(as_uuid=True), ForeignKey("whatsapp_batches.id"))
    agent_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    date = Column(DateTime, default=datetime.utcnow)
    added_count = Column(Integer, nullable=False)
    notes = Column(Text, nullable=True)
    is_verified = Column(Boolean, default=False)
    
    batch = relationship("WhatsappBatch", back_populates="daily_reports")
