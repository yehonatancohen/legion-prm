import asyncio
import os
from sqlalchemy import text
from app.core.config import settings
from app.core.database import AsyncSessionLocal

# Force update settings from env if needed (though Pydantic does this auto)
# This mimics exactly what the app does.

async def check_db():
    print("--- Database Diagnostic ---")
    print(f"1. Configured Host: {settings.POSTGRES_SERVER}")
    print(f"2. Configured Port: {settings.POSTGRES_PORT}")
    print(f"3. Configured DB:   {settings.POSTGRES_DB}")
    print(f"4. Full Connection URL: {settings.assemble_db_url().replace(settings.POSTGRES_PASSWORD, '******')}")
    
    print("\nAttempting connection...")
    
    try:
        async with AsyncSessionLocal() as session:
            # Check connection info
            result = await session.execute(text("SELECT inet_server_addr(), inet_server_port(), current_database();"))
            row = result.fetchone()
            print(f"CONNECTED SUCCESS!")
            print(f"   - Server IP: {row[0]}")
            print(f"   - Server Port: {row[1]}")
            print(f"   - Active Database: {row[2]}")

            # Check Data
            print("\nChecking Data Counts:")
            
            # Count Users
            try:
                users = await session.execute(text("SELECT count(*) FROM users"))
                print(f"   - Users found: {users.scalar()}")
            except Exception as e:
                print(f"   - Users table error: {e}")

            # Count Campaigns
            try:
                camps = await session.execute(text("SELECT count(*) FROM campaigns"))
                print(f"   - Campaigns found: {camps.scalar()}")
            except Exception as e:
                print(f"   - Campaigns table error: {e}")

    except Exception as e:
        print(f"CONNECTION FAILED: {e}")

if __name__ == "__main__":
    # Ensure event loop logic works on Windows
    # (FastAPI does this automatically, script needs manual set)
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(check_db())
