import asyncio
from app.core.database import AsyncSessionLocal
from app.models.tenant import User, Tenant, UserRole
from app.core.security import get_password_hash
from sqlalchemy import select
import uuid

async def create_admin():
    async with AsyncSessionLocal() as session:
        # Check if Tenant exists
        result = await session.execute(select(Tenant).where(Tenant.name == "Default Tenant"))
        tenant = result.scalars().first()
        if not tenant:
            tenant = Tenant(name="Default Tenant")
            session.add(tenant)
            await session.commit()
            print("Created Default Tenant")
        
        # Check if Admin exists
        result = await session.execute(select(User).where(User.name == "Admin User"))
        user = result.scalars().first()
        if not user:
            user = User(
                tenant_id=tenant.id,
                name="Admin User",
                phone="admin",
                role=UserRole.ADMIN.value,
                hashed_password=get_password_hash("admin123"),
                wallet_balance=0.0
            )
            session.add(user)
            await session.commit()
            print("Created Admin User: admin / admin123")
        else:
            print("Admin User already exists")
            # Ensure role is ADMIN needed for dashboard
            if user.role != UserRole.ADMIN.value:
                user.role = UserRole.ADMIN.value
                session.add(user)
                await session.commit()
                print("Updated user role to ADMIN")

if __name__ == "__main__":
    asyncio.run(create_admin())
