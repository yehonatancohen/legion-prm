import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base

class TrackingLink(Base):
    __tablename__ = "tracking_links"

    short_code = Column(String, primary_key=True, index=True)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    target_id = Column(UUID(as_uuid=True), ForeignKey("campaign_targets.id"), nullable=True)  # Now optional
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Track unique views per link
    view_count = Column(Integer, default=0)
    unique_view_count = Column(Integer, default=0)

    agent = relationship("User", back_populates="tracking_links")
    target = relationship("CampaignTarget", back_populates="tracking_links")
    campaign = relationship("Campaign", back_populates="tracking_links")

class AnalyticsEvent(Base):
    __tablename__ = "analytics_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_type = Column(String, nullable=False, index=True) # CLICK, CONVERSION
    tracking_link_id = Column(String, ForeignKey("tracking_links.short_code"), nullable=False)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True) # Denormalized for easier querying
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    metadata_json = Column(String, nullable=True) # IP, User Agent stored as JSON string or dedicated columns

    # Index for fast time-series queries
    __table_args__ = (
        Index('idx_analytics_agent_time', 'agent_id', 'timestamp'),
    )
