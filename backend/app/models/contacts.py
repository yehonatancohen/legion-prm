"""
Contact Pool and VCF Batch Models

These models support the contact distribution system:
- ContactPool: Raw contacts from Excel uploads
- VcfBatch: Generated VCF files assigned to agents
- AgentProgress: Track daily work (morning/evening sessions)
"""

import uuid
from datetime import datetime, date
from sqlalchemy import Column, String, Integer, DateTime, Boolean, ForeignKey, Date, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base
import enum


class VcfBatchStatus(str, enum.Enum):
    PENDING = "PENDING"       # Generated but not assigned
    ASSIGNED = "ASSIGNED"     # Assigned to an agent
    IN_PROGRESS = "IN_PROGRESS"  # Agent started working
    COMPLETED = "COMPLETED"   # All contacts reported as added


class ContactPool(Base):
    """
    Raw contacts from Excel uploads.
    These are pooled and then assigned to VCF batches.
    """
    __tablename__ = "contact_pool"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    
    phone = Column(String, nullable=False)
    source_file = Column(String, nullable=True)  # Original Excel filename
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    
    # Assignment tracking
    vcf_batch_id = Column(UUID(as_uuid=True), ForeignKey("vcf_batches.id"), nullable=True)
    is_assigned = Column(Boolean, default=False)
    
    # Relationships
    tenant = relationship("Tenant")
    vcf_batch = relationship("VcfBatch", back_populates="contacts")


class VcfBatch(Base):
    """
    Generated VCF file containing contacts for an agent.
    Each batch contains up to 1500 contacts with serial naming.
    """
    __tablename__ = "vcf_batches"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    # VCF file info
    file_path = Column(String, nullable=True)  # Path to generated .vcf file
    file_name = Column(String, nullable=True)  # Display filename
    contact_count = Column(Integer, default=0)
    
    # Serial naming config
    prefix = Column(String, default="LEG")  # e.g., "LEG"
    start_serial = Column(Integer, default=1)  # Starting serial number
    contacts_per_serial = Column(Integer, default=25)  # How many contacts share same serial
    
    # Status tracking
    status = Column(String, default=VcfBatchStatus.PENDING.value)
    assigned_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Progress tracking
    total_reported = Column(Integer, default=0)  # Total contacts reported as added
    
    # Relationships
    tenant = relationship("Tenant")
    agent = relationship("User", back_populates="vcf_batches")
    contacts = relationship("ContactPool", back_populates="vcf_batch")
    progress_reports = relationship("AgentProgress", back_populates="vcf_batch")


class AgentProgress(Base):
    """
    Daily progress reports from agents.
    Tracks morning and evening additions.
    """
    __tablename__ = "agent_progress"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    vcf_batch_id = Column(UUID(as_uuid=True), ForeignKey("vcf_batches.id"), nullable=False)
    
    # Daily tracking
    date = Column(Date, default=date.today)
    morning_count = Column(Integer, default=0)  # Reported in morning session
    evening_count = Column(Integer, default=0)  # Reported in evening session
    
    # Metadata
    morning_reported_at = Column(DateTime, nullable=True)
    evening_reported_at = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    agent = relationship("User", back_populates="progress_reports")
    vcf_batch = relationship("VcfBatch", back_populates="progress_reports")
