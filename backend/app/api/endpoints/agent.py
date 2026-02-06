from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload
from app.api import deps
from app.core.database import AsyncSessionLocal
from app.models import User, Assignment, Campaign, CampaignTarget, AssignmentStatus, UserRole

router = APIRouter()

# --- Agent Dashboard ---
@router.get("/dashboard")
async def get_agent_dashboard(current_user: User = Depends(deps.get_current_user)):
    """
    Get Agent stats and available tasks.
    """
    async with AsyncSessionLocal() as session:
        # 1. Get refresh user to ensure score is latest
        result = await session.execute(select(User).where(User.id == current_user.id))
        user = result.scalar()

        # 2. Get Available Campaigns (Simplification: All active campaigns for Tenant)
        # In real app: exclude campaigns user is already assigned to, or show them as active tasks.
        # For now: Just fetch all active campaigns user can work on.
        campaigns_res = await session.execute(
            select(Campaign)
            .options(selectinload(Campaign.targets))
            .where(Campaign.tenant_id == user.tenant_id, Campaign.status == "ACTIVE")
        )
        campaigns = campaigns_res.scalars().all()

        return {
            "user": {
                "name": user.name,
                "score": user.current_score,
                "balance": user.wallet_balance
            },
            "tasks": campaigns 
        }

# --- Leaderboard ---
@router.get("/leaderboard")
async def get_leaderboard(current_user: User = Depends(deps.get_current_user)):
    async with AsyncSessionLocal() as session:
         result = await session.execute(
            select(User)
            .where(User.tenant_id == current_user.tenant_id, User.role == UserRole.AGENT.value)
            .order_by(desc(User.current_score))
            .limit(20)
        )
         return result.scalars().all()

# --- Submit Assignment (Proof) ---
# Currently mock only via Admin. But Agent might need to "Accept" task.
# Let's add an endpoint to generate a tracking link for a campaign.

@router.post("/campaigns/{campaign_id}/join")
async def join_campaign(campaign_id: str, current_user: User = Depends(deps.get_current_user)):
    # 1. Create Assignment PENDING
    # 2. Return Tracking Links
    # TODO: Implement Link Generation Logic
    return {"status": "joined", "message": "Links generated"}
