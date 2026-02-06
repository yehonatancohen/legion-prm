from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func, desc, update
from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime
from uuid import UUID
from app.api import deps
from app.core.database import AsyncSessionLocal
from app.models import User, Campaign, AnalyticsEvent, UserRole, Assignment, AssignmentStatus, CampaignStatus

router = APIRouter()

# --- Pydantic Models for Requests & Responses ---
class CampaignCreate(BaseModel):
    name: str
    budget_cap: float
    status: str = "ACTIVE"

class AssignmentUpdate(BaseModel):
    status: str 

class UserOut(BaseModel):
    id: UUID
    name: str
    current_score: int
    model_config = ConfigDict(from_attributes=True)

class CampaignOut(BaseModel):
    id: UUID
    name: str
    model_config = ConfigDict(from_attributes=True)

class AssignmentOut(BaseModel):
    id: UUID
    status: str
    proof_data: Optional[dict] = None
    agent: UserOut
    campaign: CampaignOut
    model_config = ConfigDict(from_attributes=True)

# --- Dashboard ---
@router.get("/dashboard/stats")
async def get_dashboard_stats(current_user: User = Depends(deps.get_current_active_admin)):
    tenant_id = current_user.tenant_id
    async with AsyncSessionLocal() as session:
        # Agents
        agents = await session.execute(select(func.count(User.id)).where(User.tenant_id == tenant_id, User.role == UserRole.AGENT.value))
        total_agents = agents.scalar()
        # Campaigns
        campaigns = await session.execute(select(func.count(Campaign.id)).where(Campaign.tenant_id == tenant_id))
        total_campaigns = campaigns.scalar()
        # Clicks
        clicks = await session.execute(select(func.count(AnalyticsEvent.id)).where(AnalyticsEvent.event_type == "CLICK"))
        total_clicks = clicks.scalar() # In real-world, join with Tenant
        # Top Agents
        top = await session.execute(select(User).where(User.tenant_id == tenant_id, User.role == UserRole.AGENT.value).order_by(desc(User.current_score)).limit(5))
        
        return {
            "total_agents": total_agents,
            "total_campaigns": total_campaigns,
            "total_clicks": total_clicks,
            "top_agents": [{"name": a.name, "score": a.current_score, "balance": a.wallet_balance} for a in top.scalars().all()]
        }

# --- Campaigns ---
@router.get("/campaigns")
async def get_campaigns(current_user: User = Depends(deps.get_current_active_admin)):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Campaign).where(Campaign.tenant_id == current_user.tenant_id).order_by(desc(Campaign.created_at)))
        return result.scalars().all()

@router.post("/campaigns")
async def create_campaign(campaign_in: CampaignCreate, current_user: User = Depends(deps.get_current_active_admin)):
    async with AsyncSessionLocal() as session:
        campaign = Campaign(
            tenant_id=current_user.tenant_id,
            name=campaign_in.name,
            budget_cap=campaign_in.budget_cap,
            status=campaign_in.status,
            start_date=datetime.utcnow()
        )
        session.add(campaign)
        await session.commit()
        return campaign

# --- Agents ---
@router.get("/agents")
async def get_agents(current_user: User = Depends(deps.get_current_active_admin)):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.tenant_id == current_user.tenant_id, User.role == UserRole.AGENT.value))
        return result.scalars().all()

# --- Assignments ---
@router.get("/assignments", response_model=List[AssignmentOut])
async def get_assignments(status: Optional[str] = None, current_user: User = Depends(deps.get_current_active_admin)):
    async with AsyncSessionLocal() as session:
        query = select(Assignment).join(User).join(Campaign).where(User.tenant_id == current_user.tenant_id)
        if status:
            query = query.where(Assignment.status == status)
        
        # Eager load for UI
        from sqlalchemy.orm import selectinload
        query = query.options(selectinload(Assignment.agent), selectinload(Assignment.campaign))
        
        result = await session.execute(query)
        assignments = result.scalars().all()
        return assignments

@router.put("/assignments/{assignment_id}")
async def update_assignment(assignment_id: str, update_data: AssignmentUpdate, current_user: User = Depends(deps.get_current_active_admin)):
    async with AsyncSessionLocal() as session:
        stmt = update(Assignment).where(Assignment.id == assignment_id).values(status=update_data.status)
        await session.execute(stmt)
        
        # If Verified, give points? (Logic for later)
        if update_data.status == AssignmentStatus.VERIFIED.value:
            # Fetch assignment
            res = await session.execute(select(Assignment).where(Assignment.id == assignment_id))
            assignment = res.scalar()
            if assignment:
                # Add Points to User
                await session.execute(update(User).where(User.id == assignment.agent_id).values(current_score=User.current_score + 10))

        await session.commit()
        return {"status": "success"}
