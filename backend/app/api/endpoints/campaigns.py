"""
Campaigns API Endpoints

Provides endpoints for:
- Creating campaigns with target URLs
- Generating unique referral links for agents
- Tracking views and awarding agents
"""

import uuid
import secrets
import string
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, HttpUrl
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api import deps
from app.core.database import AsyncSessionLocal
from app.models import (
    User, Campaign, CampaignStatus, TrackingLink, AnalyticsEvent, UserRole
)

router = APIRouter()


# ============== Schemas ==============

class CreateCampaignRequest(BaseModel):
    name: str
    description: Optional[str] = None
    target_url: str
    payout_per_view: float = 0.01
    points_per_view: int = 1
    budget_cap: float = 100.0


class CampaignResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    target_url: str
    status: str
    payout_per_view: float
    points_per_view: int
    budget_cap: float
    spent: float
    total_views: int
    total_unique_views: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class TrackingLinkResponse(BaseModel):
    short_code: str
    full_url: str
    campaign_name: str
    view_count: int
    unique_view_count: int
    earnings: float


class AgentCampaignResponse(BaseModel):
    campaign: CampaignResponse
    my_link: Optional[TrackingLinkResponse]
    my_earnings: float
    my_views: int


# ============== Helper Functions ==============

def generate_short_code(length: int = 6) -> str:
    """Generate a random short code for tracking links."""
    chars = string.ascii_letters + string.digits
    return ''.join(secrets.choice(chars) for _ in range(length))


# ============== Admin Endpoints ==============

@router.post("/admin/campaigns", response_model=CampaignResponse)
async def create_campaign(
    request: CreateCampaignRequest,
    current_user: User = Depends(deps.get_current_admin_user)
):
    """Create a new campaign with a target URL."""
    async with AsyncSessionLocal() as session:
        campaign = Campaign(
            tenant_id=current_user.tenant_id,
            name=request.name,
            description=request.description,
            target_url=request.target_url,
            payout_per_view=request.payout_per_view,
            points_per_view=request.points_per_view,
            budget_cap=request.budget_cap,
            status=CampaignStatus.ACTIVE.value
        )
        session.add(campaign)
        await session.commit()
        await session.refresh(campaign)
        
        return CampaignResponse(
            id=str(campaign.id),
            name=campaign.name,
            description=campaign.description,
            target_url=campaign.target_url,
            status=campaign.status,
            payout_per_view=campaign.payout_per_view,
            points_per_view=campaign.points_per_view,
            budget_cap=campaign.budget_cap,
            spent=campaign.spent or 0,
            total_views=campaign.total_views or 0,
            total_unique_views=campaign.total_unique_views or 0,
            created_at=campaign.created_at
        )


@router.get("/admin/campaigns", response_model=List[CampaignResponse])
async def list_campaigns(
    status: Optional[str] = Query(None),
    current_user: User = Depends(deps.get_current_admin_user)
):
    """List all campaigns for the tenant."""
    async with AsyncSessionLocal() as session:
        query = select(Campaign).where(Campaign.tenant_id == current_user.tenant_id)
        if status:
            query = query.where(Campaign.status == status)
        query = query.order_by(Campaign.created_at.desc())
        
        result = await session.execute(query)
        campaigns = result.scalars().all()
        
        return [
            CampaignResponse(
                id=str(c.id),
                name=c.name,
                description=c.description,
                target_url=c.target_url,
                status=c.status,
                payout_per_view=c.payout_per_view,
                points_per_view=c.points_per_view,
                budget_cap=c.budget_cap,
                spent=c.spent or 0,
                total_views=c.total_views or 0,
                total_unique_views=c.total_unique_views or 0,
                created_at=c.created_at
            ) for c in campaigns
        ]


@router.patch("/admin/campaigns/{campaign_id}/status")
async def update_campaign_status(
    campaign_id: str,
    status: str,
    current_user: User = Depends(deps.get_current_admin_user)
):
    """Update campaign status (ACTIVE, PAUSED, COMPLETED)."""
    if status not in [s.value for s in CampaignStatus]:
        raise HTTPException(status_code=400, detail="Invalid status")
    
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Campaign)
            .where(Campaign.id == uuid.UUID(campaign_id))
            .where(Campaign.tenant_id == current_user.tenant_id)
        )
        campaign = result.scalars().first()
        
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        campaign.status = status
        await session.commit()
        
        return {"status": "updated", "new_status": status}


@router.get("/admin/campaigns/{campaign_id}/stats")
async def get_campaign_stats(
    campaign_id: str,
    current_user: User = Depends(deps.get_current_admin_user)
):
    """Get detailed stats for a campaign including per-agent breakdown."""
    async with AsyncSessionLocal() as session:
        # Get campaign
        result = await session.execute(
            select(Campaign)
            .where(Campaign.id == uuid.UUID(campaign_id))
            .where(Campaign.tenant_id == current_user.tenant_id)
        )
        campaign = result.scalars().first()
        
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        # Get per-agent stats
        links_result = await session.execute(
            select(TrackingLink)
            .options(selectinload(TrackingLink.agent))
            .where(TrackingLink.campaign_id == campaign.id)
        )
        links = links_result.scalars().all()
        
        agent_stats = []
        for link in links:
            earnings = (link.unique_view_count or 0) * campaign.payout_per_view
            agent_stats.append({
                "agent_id": str(link.agent_id),
                "agent_name": link.agent.name if link.agent else "Unknown",
                "short_code": link.short_code,
                "views": link.view_count or 0,
                "unique_views": link.unique_view_count or 0,
                "earnings": earnings
            })
        
        return {
            "campaign": {
                "id": str(campaign.id),
                "name": campaign.name,
                "status": campaign.status,
                "total_views": campaign.total_views or 0,
                "total_unique_views": campaign.total_unique_views or 0,
                "spent": campaign.spent or 0,
                "budget_cap": campaign.budget_cap
            },
            "agents": agent_stats
        }


# ============== Agent Endpoints ==============

@router.get("/agent/campaigns", response_model=List[AgentCampaignResponse])
async def get_my_campaigns(
    current_user: User = Depends(deps.get_current_active_user)
):
    """Get all active campaigns available to the agent with their tracking links."""
    async with AsyncSessionLocal() as session:
        # Get all active campaigns for this tenant
        campaigns_result = await session.execute(
            select(Campaign)
            .where(Campaign.tenant_id == current_user.tenant_id)
            .where(Campaign.status == CampaignStatus.ACTIVE.value)
            .order_by(Campaign.created_at.desc())
        )
        campaigns = campaigns_result.scalars().all()
        
        result = []
        for campaign in campaigns:
            # Check if agent already has a link for this campaign
            link_result = await session.execute(
                select(TrackingLink)
                .where(TrackingLink.campaign_id == campaign.id)
                .where(TrackingLink.agent_id == current_user.id)
            )
            link = link_result.scalars().first()
            
            my_link = None
            my_earnings = 0.0
            my_views = 0
            
            if link:
                my_views = link.unique_view_count or 0
                my_earnings = my_views * campaign.payout_per_view
                my_link = TrackingLinkResponse(
                    short_code=link.short_code,
                    full_url=f"http://localhost:8000/r/{link.short_code}",  # TODO: Use proper domain
                    campaign_name=campaign.name,
                    view_count=link.view_count or 0,
                    unique_view_count=link.unique_view_count or 0,
                    earnings=my_earnings
                )
            
            result.append(AgentCampaignResponse(
                campaign=CampaignResponse(
                    id=str(campaign.id),
                    name=campaign.name,
                    description=campaign.description,
                    target_url=campaign.target_url,
                    status=campaign.status,
                    payout_per_view=campaign.payout_per_view,
                    points_per_view=campaign.points_per_view,
                    budget_cap=campaign.budget_cap,
                    spent=campaign.spent or 0,
                    total_views=campaign.total_views or 0,
                    total_unique_views=campaign.total_unique_views or 0,
                    created_at=campaign.created_at
                ),
                my_link=my_link,
                my_earnings=my_earnings,
                my_views=my_views
            ))
        
        return result


@router.post("/agent/campaigns/{campaign_id}/join")
async def join_campaign(
    campaign_id: str,
    current_user: User = Depends(deps.get_current_active_user)
):
    """Join a campaign and get a unique referral link."""
    async with AsyncSessionLocal() as session:
        # Verify campaign exists and is active
        campaign_result = await session.execute(
            select(Campaign)
            .where(Campaign.id == uuid.UUID(campaign_id))
            .where(Campaign.tenant_id == current_user.tenant_id)
            .where(Campaign.status == CampaignStatus.ACTIVE.value)
        )
        campaign = campaign_result.scalars().first()
        
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found or not active")
        
        # Check if already joined
        existing_link = await session.execute(
            select(TrackingLink)
            .where(TrackingLink.campaign_id == campaign.id)
            .where(TrackingLink.agent_id == current_user.id)
        )
        if existing_link.scalars().first():
            raise HTTPException(status_code=400, detail="Already joined this campaign")
        
        # Generate unique short code
        while True:
            short_code = generate_short_code()
            # Check uniqueness
            check = await session.execute(
                select(TrackingLink).where(TrackingLink.short_code == short_code)
            )
            if not check.scalars().first():
                break
        
        # Create tracking link
        tracking_link = TrackingLink(
            short_code=short_code,
            agent_id=current_user.id,
            campaign_id=campaign.id,
            view_count=0,
            unique_view_count=0
        )
        session.add(tracking_link)
        await session.commit()
        
        return {
            "status": "joined",
            "short_code": short_code,
            "tracking_url": f"http://localhost:8000/r/{short_code}",  # TODO: Use proper domain
            "campaign_name": campaign.name,
            "payout_per_view": campaign.payout_per_view,
            "points_per_view": campaign.points_per_view
        }
