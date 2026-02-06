import asyncio
import logging
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models import Tenant, User, UserRole, Campaign, CampaignStatus
from app.core.security import get_password_hash

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def seed_data():
    async with AsyncSessionLocal() as session:
        # 1. Check if data exists
        result = await session.execute(select(Tenant).where(Tenant.name == "Demo Corp"))
        existing_tenant = result.scalars().first()
        
        if existing_tenant:
            logger.info("Data already exists. Skipping seed.")
            return

        # 2. Create Tenant
        tenant = Tenant(name="Demo Corp", plan_tier="ENTERPRISE")
        session.add(tenant)
        await session.flush() # Get ID
        
        # 3. Create Admin
        admin = User(
            tenant_id=tenant.id,
            role=UserRole.ADMIN.value,
            name="Alice Admin",
            phone="+15550001",
            hashed_password=get_password_hash("admin123"),
            wallet_balance=1000.0
        )
        session.add(admin)

        # 4. Create Agents
        agent1 = User(
            tenant_id=tenant.id,
            role=UserRole.AGENT.value,
            name="Bob Agent",
            phone="+15550002",
            hashed_password=get_password_hash("agent123"), # Usually OTP, but password for now
            current_score=150,
            wallet_balance=50.0
        )
        agent2 = User(
            tenant_id=tenant.id,
            role=UserRole.AGENT.value,
            name="Charlie Agent",
            phone="+15550003",
            hashed_password=get_password_hash("agent123"),
            current_score=320,
            wallet_balance=120.0
        )
        session.add(agent1)
        session.add(agent2)

        # 5. Create Campaign
        campaign = Campaign(
            tenant_id=tenant.id,
            name="Summer Festival 2026",
            status=CampaignStatus.ACTIVE.value,
            budget_cap=5000.0
        )
        session.add(campaign)
        
        await session.commit()
        logger.info("Seeding Complete!")
        logger.info("Admin Credentials: Phone: +15550001, Pass: admin123")

if __name__ == "__main__":
    asyncio.run(seed_data())
