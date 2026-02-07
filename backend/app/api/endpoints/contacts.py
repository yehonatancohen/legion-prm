"""
Contacts API Endpoints

Provides endpoints for:
- Uploading Excel files to contact pool
- Generating VCF batches
- Assigning batches to agents
- Getting pool statistics
- Downloading VCF files
"""

import os
import uuid
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.core.database import AsyncSessionLocal
from app.models import User, VcfBatch, VcfBatchStatus, AgentProgress
from app.services.contact_pool import contact_pool_service
from app.services.vcf_generator import vcf_generator
from app.services.export import export_service

router = APIRouter()


# ============== Schemas ==============

class UploadResponse(BaseModel):
    file_name: str
    total_rows: int
    valid_phones: int
    new_contacts: int
    duplicates: int
    invalid_entries: int
    invalid_samples: List[str]


class PoolStatsResponse(BaseModel):
    total_contacts: int
    assigned: int
    unassigned: int
    assignment_rate: float
    sources: List[dict]


class VcfBatchResponse(BaseModel):
    id: str
    file_name: Optional[str]
    contact_count: int
    prefix: str
    start_serial: int
    status: str
    agent_id: Optional[str]
    agent_name: Optional[str]
    assigned_at: Optional[datetime]
    created_at: datetime


class GenerateBatchesRequest(BaseModel):
    prefix: str = "LEG"
    contacts_per_batch: int = 1500
    contacts_per_serial: int = 25
    max_batches: int = 1


class AssignBatchRequest(BaseModel):
    agent_id: str


class ProgressReportRequest(BaseModel):
    batch_id: str
    session_type: str  # "morning" or "evening"
    count: int
    notes: Optional[str] = None


class AgentStatusResponse(BaseModel):
    id: str
    name: str
    phone: str
    status: str
    status_icon: str
    inactive_days: int
    today_total: int
    total_added: int


# ============== Admin Endpoints ==============

@router.post("/admin/contacts/upload", response_model=UploadResponse)
async def upload_contacts(
    file: UploadFile = File(...),
    current_user: User = Depends(deps.get_current_admin_user)
):
    """
    Upload an Excel file with phone numbers to the contact pool.
    Accepts .xlsx files.
    """
    # Validate file type
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Please upload an Excel file (.xlsx or .xls)"
        )
    
    # Read file content
    content = await file.read()
    
    async with AsyncSessionLocal() as session:
        result = await contact_pool_service.upload_contacts(
            session=session,
            tenant_id=current_user.tenant_id,
            file_content=content,
            file_name=file.filename
        )
    
    return UploadResponse(**result)


@router.get("/admin/contacts/pool/stats", response_model=PoolStatsResponse)
async def get_pool_stats(
    current_user: User = Depends(deps.get_current_admin_user)
):
    """Get statistics about the contact pool."""
    async with AsyncSessionLocal() as session:
        stats = await contact_pool_service.get_pool_stats(
            session=session,
            tenant_id=current_user.tenant_id
        )
    return PoolStatsResponse(**stats)


@router.post("/admin/vcf/generate", response_model=List[VcfBatchResponse])
async def generate_vcf_batches(
    request: GenerateBatchesRequest,
    current_user: User = Depends(deps.get_current_admin_user)
):
    """
    Generate VCF batches from the contact pool.
    Each batch contains up to contacts_per_batch contacts.
    """
    async with AsyncSessionLocal() as session:
        batches = await vcf_generator.generate_multiple_batches(
            session=session,
            tenant_id=current_user.tenant_id,
            prefix=request.prefix,
            contacts_per_batch=request.contacts_per_batch,
            contacts_per_serial=request.contacts_per_serial,
            max_batches=request.max_batches
        )
        
        # Format response
        response = []
        for batch in batches:
            response.append(VcfBatchResponse(
                id=str(batch.id),
                file_name=batch.file_name,
                contact_count=batch.contact_count,
                prefix=batch.prefix,
                start_serial=batch.start_serial,
                status=batch.status,
                agent_id=str(batch.agent_id) if batch.agent_id else None,
                agent_name=None,
                assigned_at=batch.assigned_at,
                created_at=batch.created_at
            ))
        
        return response


@router.get("/admin/vcf/batches", response_model=List[VcfBatchResponse])
async def list_vcf_batches(
    status: Optional[str] = Query(None, description="Filter by status"),
    current_user: User = Depends(deps.get_current_admin_user)
):
    """List all VCF batches for the tenant."""
    async with AsyncSessionLocal() as session:
        query = select(VcfBatch).where(VcfBatch.tenant_id == current_user.tenant_id)
        
        if status:
            query = query.where(VcfBatch.status == status)
        
        query = query.order_by(VcfBatch.created_at.desc())
        
        result = await session.execute(query)
        batches = result.scalars().all()
        
        response = []
        for batch in batches:
            # Get agent name if assigned
            agent_name = None
            if batch.agent_id:
                agent_result = await session.execute(
                    select(User).where(User.id == batch.agent_id)
                )
                agent = agent_result.scalars().first()
                if agent:
                    agent_name = agent.name
            
            response.append(VcfBatchResponse(
                id=str(batch.id),
                file_name=batch.file_name,
                contact_count=batch.contact_count,
                prefix=batch.prefix,
                start_serial=batch.start_serial,
                status=batch.status,
                agent_id=str(batch.agent_id) if batch.agent_id else None,
                agent_name=agent_name,
                assigned_at=batch.assigned_at,
                created_at=batch.created_at
            ))
        
        return response


@router.post("/admin/vcf/batches/{batch_id}/assign", response_model=VcfBatchResponse)
async def assign_batch_to_agent(
    batch_id: str,
    request: AssignBatchRequest,
    current_user: User = Depends(deps.get_current_admin_user)
):
    """Assign a VCF batch to an agent."""
    async with AsyncSessionLocal() as session:
        batch = await vcf_generator.assign_batch_to_agent(
            session=session,
            batch_id=uuid.UUID(batch_id),
            agent_id=uuid.UUID(request.agent_id)
        )
        
        if not batch:
            raise HTTPException(status_code=404, detail="Batch not found or not available")
        
        # Get agent name
        agent_result = await session.execute(
            select(User).where(User.id == batch.agent_id)
        )
        agent = agent_result.scalars().first()
        
        return VcfBatchResponse(
            id=str(batch.id),
            file_name=batch.file_name,
            contact_count=batch.contact_count,
            prefix=batch.prefix,
            start_serial=batch.start_serial,
            status=batch.status,
            agent_id=str(batch.agent_id) if batch.agent_id else None,
            agent_name=agent.name if agent else None,
            assigned_at=batch.assigned_at,
            created_at=batch.created_at
        )


@router.get("/admin/agents/status", response_model=List[AgentStatusResponse])
async def get_agents_status(
    current_user: User = Depends(deps.get_current_admin_user)
):
    """Get status of all agents including activity and progress."""
    async with AsyncSessionLocal() as session:
        statuses = await export_service.get_agent_status_list(
            session=session,
            tenant_id=current_user.tenant_id
        )
        return [AgentStatusResponse(**s) for s in statuses]


@router.get("/admin/agents/inactive")
async def get_inactive_agents(
    days: int = Query(1, description="Inactivity threshold in days"),
    current_user: User = Depends(deps.get_current_admin_user)
):
    """Get list of inactive agents."""
    async with AsyncSessionLocal() as session:
        inactive = await export_service.get_inactive_agents(
            session=session,
            tenant_id=current_user.tenant_id,
            inactive_threshold_days=days
        )
        return inactive


@router.get("/admin/export/text")
async def export_status_text(
    current_user: User = Depends(deps.get_current_admin_user)
):
    """Generate a text status report for sharing."""
    async with AsyncSessionLocal() as session:
        report = await export_service.generate_text_report(
            session=session,
            tenant_id=current_user.tenant_id
        )
        return {"report": report}


# ============== Agent Endpoints ==============

@router.get("/agent/vcf/batches", response_model=List[VcfBatchResponse])
async def get_my_batches(
    current_user: User = Depends(deps.get_current_active_user)
):
    """Get VCF batches assigned to the current agent."""
    async with AsyncSessionLocal() as session:
        batches = await vcf_generator.get_agent_batches(
            session=session,
            agent_id=current_user.id
        )
        
        return [VcfBatchResponse(
            id=str(batch.id),
            file_name=batch.file_name,
            contact_count=batch.contact_count,
            prefix=batch.prefix,
            start_serial=batch.start_serial,
            status=batch.status,
            agent_id=str(batch.agent_id) if batch.agent_id else None,
            agent_name=current_user.name,
            assigned_at=batch.assigned_at,
            created_at=batch.created_at
        ) for batch in batches]


@router.get("/agent/vcf/download/{batch_id}")
async def download_vcf(
    batch_id: str,
    current_user: User = Depends(deps.get_current_active_user)
):
    """Download a VCF file for a batch assigned to the agent."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(VcfBatch)
            .where(VcfBatch.id == uuid.UUID(batch_id))
            .where(VcfBatch.agent_id == current_user.id)
        )
        batch = result.scalars().first()
        
        if not batch:
            raise HTTPException(status_code=404, detail="Batch not found")
        
        if not batch.file_path or not os.path.exists(batch.file_path):
            raise HTTPException(status_code=404, detail="VCF file not found")
        
        return FileResponse(
            path=batch.file_path,
            filename=batch.file_name or f"contacts_{batch_id}.vcf",
            media_type="text/vcard"
        )


@router.post("/agent/progress/report")
async def report_progress(
    request: ProgressReportRequest,
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    Report progress for adding contacts.
    Session type should be 'morning' or 'evening'.
    """
    if request.session_type not in ["morning", "evening"]:
        raise HTTPException(
            status_code=400,
            detail="session_type must be 'morning' or 'evening'"
        )
    
    async with AsyncSessionLocal() as session:
        # Verify batch belongs to agent
        batch_result = await session.execute(
            select(VcfBatch)
            .where(VcfBatch.id == uuid.UUID(request.batch_id))
            .where(VcfBatch.agent_id == current_user.id)
        )
        batch = batch_result.scalars().first()
        
        if not batch:
            raise HTTPException(status_code=404, detail="Batch not found")
        
        # Find or create today's progress record
        today = datetime.utcnow().date()
        progress_result = await session.execute(
            select(AgentProgress)
            .where(AgentProgress.agent_id == current_user.id)
            .where(AgentProgress.vcf_batch_id == batch.id)
            .where(AgentProgress.date == today)
        )
        progress = progress_result.scalars().first()
        
        if not progress:
            progress = AgentProgress(
                agent_id=current_user.id,
                vcf_batch_id=batch.id,
                date=today
            )
            session.add(progress)
        
        # Update progress
        now = datetime.utcnow()
        if request.session_type == "morning":
            progress.morning_count = request.count
            progress.morning_reported_at = now
        else:
            progress.evening_count = request.count
            progress.evening_reported_at = now
        
        if request.notes:
            progress.notes = request.notes
        
        # Update batch status
        if batch.status == VcfBatchStatus.ASSIGNED.value:
            batch.status = VcfBatchStatus.IN_PROGRESS.value
        
        # Update agent's last activity
        current_user.last_activity_at = now
        
        # ============== XP System with Streak ==============
        # Base XP: 1 point per contact
        base_xp = request.count
        
        # Calculate streak (consecutive days with activity)
        from datetime import timedelta
        yesterday = today - timedelta(days=1)
        streak_result = await session.execute(
            select(AgentProgress)
            .where(AgentProgress.agent_id == current_user.id)
            .where(AgentProgress.date == yesterday)
        )
        had_activity_yesterday = streak_result.scalars().first() is not None
        
        # Streak multiplier: 1.0 base, +0.1 per consecutive day, max 1.5x
        streak_multiplier = 1.0
        if had_activity_yesterday:
            # Count streak days (simplified: just check if yesterday had activity)
            # A more complex implementation would track actual streak count
            streak_multiplier = 1.2  # 20% bonus for continuing streak
        
        # Bonus for completing both sessions (if both morning and evening done)
        session_bonus = 0
        if progress.morning_count > 0 and progress.evening_count > 0:
            session_bonus = 10  # Extra 10 XP for completing both
        
        # Goal completion bonus
        total_today = progress.morning_count + progress.evening_count
        goal_bonus = 0
        if total_today >= 50:
            goal_bonus = 25  # Bonus for hitting daily goal
        
        # Calculate final XP
        xp_earned = int(base_xp * streak_multiplier) + session_bonus + goal_bonus
        
        # Update user score
        if current_user.current_score is None:
            current_user.current_score = 0
        current_user.current_score += xp_earned
        
        await session.commit()
        
        return {
            "status": "success",
            "date": today.isoformat(),
            "morning_count": progress.morning_count,
            "evening_count": progress.evening_count,
            "total_today": progress.morning_count + progress.evening_count,
            "xp_earned": xp_earned,
            "total_xp": current_user.current_score,
            "streak_multiplier": streak_multiplier
        }


@router.get("/agent/progress/today")
async def get_today_progress(
    current_user: User = Depends(deps.get_current_active_user)
):
    """Get today's progress for the current agent."""
    async with AsyncSessionLocal() as session:
        today = datetime.utcnow().date()
        result = await session.execute(
            select(AgentProgress)
            .where(AgentProgress.agent_id == current_user.id)
            .where(AgentProgress.date == today)
        )
        progress_records = result.scalars().all()
        
        total_morning = sum(p.morning_count for p in progress_records)
        total_evening = sum(p.evening_count for p in progress_records)
        
        return {
            "date": today.isoformat(),
            "morning_count": total_morning,
            "evening_count": total_evening,
            "total": total_morning + total_evening,
            "goal": 50,  # 25 morning + 25 evening
            "progress_percent": min(100, round((total_morning + total_evening) / 50 * 100))
        }
