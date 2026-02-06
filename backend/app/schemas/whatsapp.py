from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from uuid import UUID

class WhatsappDailyReportBase(BaseModel):
    added_count: int
    notes: Optional[str] = None

class WhatsappDailyReportCreate(WhatsappDailyReportBase):
    pass

class WhatsappDailyReport(WhatsappDailyReportBase):
    id: UUID
    batch_id: UUID
    agent_id: UUID
    date: datetime
    is_verified: bool

    class Config:
        from_attributes = True

class WhatsappBatchBase(BaseModel):
    status: str
    target_group_name: Optional[str] = None
    contact_count: int

class WhatsappBatch(WhatsappBatchBase):
    id: UUID
    campaign_id: UUID
    agent_id: Optional[UUID]
    vcf_file_path: Optional[str]
    assigned_at: Optional[datetime]

    class Config:
        from_attributes = True

class BatchAssignRequest(BaseModel):
    agent_id: UUID
    target_group_name: str

class WhatsappCampaignBase(BaseModel):
    name: str

class WhatsappCampaignCreate(WhatsappCampaignBase):
    pass

class WhatsappCampaign(WhatsappCampaignBase):
    id: UUID
    file_name: Optional[str]
    uploaded_at: datetime
    total_contacts: int
    batches: List[WhatsappBatch] = []

    class Config:
        from_attributes = True
