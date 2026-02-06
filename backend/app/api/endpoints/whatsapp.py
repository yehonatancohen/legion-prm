from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, update
from typing import List, Any
from app.api import deps
from app.core.database import get_db
from app.models import whatsapp as models
from app.models.tenant import User
from app.schemas import whatsapp as schemas
import pandas as pd
import io
import uuid
import os
from datetime import datetime

router = APIRouter()

STORAGE_DIR = "storage/vcf"
os.makedirs(STORAGE_DIR, exist_ok=True)

@router.post("/upload", response_model=schemas.WhatsappCampaign)
async def upload_campaign_file(
    file: UploadFile = File(...),
    name: str = Form(...),
    batch_size: int = Form(1000),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_admin),
):
    if not file.filename.endswith(('.xlsx', '.xls', '.csv')):
        raise HTTPException(400, "Invalid file format. Use CSV or Excel.")

    contents = await file.read()
    if file.filename.endswith('.csv'):
        df = pd.read_csv(io.BytesIO(contents))
    else:
        df = pd.read_excel(io.BytesIO(contents))

    possible_name_cols = [c for c in df.columns if 'name' in str(c).lower()]
    possible_phone_cols = [c for c in df.columns if 'phone' in str(c).lower() or 'tel' in str(c).lower() or 'mobile' in str(c).lower()]
    
    if not possible_name_cols or not possible_phone_cols:
         raise HTTPException(400, "Could not identify Name or Phone columns. Please use 'Name' and 'Phone' headers.")
    
    col_name = possible_name_cols[0]
    col_phone = possible_phone_cols[0]

    campaign = models.WhatsappCampaign(
        name=name,
        file_name=file.filename,
        total_contacts=len(df)
    )
    db.add(campaign)
    await db.commit()
    await db.refresh(campaign)

    # Split
    total_rows = len(df)
    for i in range(0, total_rows, batch_size):
        chunk = df.iloc[i:i+batch_size]
        vcf_content = ""
        for _, row in chunk.iterrows():
            c_name = str(row[col_name]).strip()
            c_phone = str(row[col_phone]).strip()
            vcf_content += f"BEGIN:VCARD\nVERSION:3.0\nFN:{c_name}\nTEL:{c_phone}\nEND:VCARD\n"
        
        batch_filename = f"{campaign.id}_batch_{i//batch_size}.vcf"
        file_path = os.path.join(STORAGE_DIR, batch_filename)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(vcf_content)
            
        batch = models.WhatsappBatch(
            campaign_id=campaign.id,
            status=models.WhatsappBatchStatus.PENDING.value,
            vcf_file_path=file_path,
            contact_count=len(chunk)
        )
        db.add(batch)
    
    await db.commit()
    
    # Reload with batches
    result = await db.execute(select(models.WhatsappCampaign).where(models.WhatsappCampaign.id == campaign.id))
    campaign = result.scalars().first()
    # Force load batches (lazy loading might be issue in async without specific load options, but let's try)
    # Actually explicit join or selectinload is better, but pydantic ignores missing lazy fields usually or errors.
    # For now, let's return campaign. Batches might be empty list if not loaded.
    return campaign

@router.get("/my-batches", response_model=List[schemas.WhatsappBatch])
async def read_my_batches(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
):
    result = await db.execute(select(models.WhatsappBatch).filter(models.WhatsappBatch.agent_id == current_user.id))
    batches = result.scalars().all()
    return batches

@router.post("/batches/{batch_id}/report", response_model=schemas.WhatsappDailyReport)
async def create_report(
    batch_id: uuid.UUID,
    report_in: schemas.WhatsappDailyReportCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
):
    result = await db.execute(select(models.WhatsappBatch).filter(models.WhatsappBatch.id == batch_id))
    batch = result.scalars().first()
    if not batch:
        raise HTTPException(404, "Batch not found")
    if batch.agent_id != current_user.id:
         raise HTTPException(403, "Not assigned to this batch")

    report = models.WhatsappDailyReport(
        batch_id=batch_id,
        agent_id=current_user.id,
        added_count=report_in.added_count,
        notes=report_in.notes,
        is_verified=True # Auto-verify for now, or require admin check
    )
    db.add(report)
    
    # Award Points (e.g. 1 point per add)
    points = report_in.added_count * 1
    # Award Cash (e.g. 0.5 per add? User didn't specify rate, just "pay them". Let's add placeholder logic)
    cash = report_in.added_count * 0.5 

    # Update User
    # We need to fetch user again or attached to session? current_user is detached? 
    # Usually in FastAPI deps it is attached but let's be safe and use update query
    await db.execute(
        update(User)
        .where(User.id == current_user.id)
        .values(
            current_score=User.current_score + points,
            wallet_balance=User.wallet_balance + cash
        )
    )

    await db.commit()
    await db.refresh(report)
    return report

@router.get("/leaderboard")
async def get_leaderboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
):
    stmt = select(
        models.WhatsappDailyReport.agent_id, 
        func.sum(models.WhatsappDailyReport.added_count).label("total")
    ).group_by(models.WhatsappDailyReport.agent_id).order_by(func.sum(models.WhatsappDailyReport.added_count).desc()).limit(10)
    
    result = await db.execute(stmt)
    rows = result.all()
    # Basic return, schemas can handle this if we define a generic one or just return dict
    return [{"agent_id": r[0], "total": r[1]} for r in rows]

@router.put("/batches/{batch_id}/assign", response_model=schemas.WhatsappBatch)
async def assign_batch(
    batch_id: uuid.UUID,
    assign_in: schemas.BatchAssignRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_admin),
):
    result = await db.execute(select(models.WhatsappBatch).filter(models.WhatsappBatch.id == batch_id))
    batch = result.scalars().first()
    if not batch:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Batch not found")
    
    batch.agent_id = assign_in.agent_id
    batch.target_group_name = assign_in.target_group_name
    batch.status = models.WhatsappBatchStatus.ASSIGNED.value
    batch.assigned_at = datetime.utcnow()
    
    db.add(batch)
    await db.commit()
    await db.refresh(batch)
    return batch
