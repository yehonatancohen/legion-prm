import asyncio
import os
from sqlalchemy import text
from app.core.database import AsyncSessionLocal

async def show_data():
    print("\n--- CURRENT DATA IN DB ---")
    async with AsyncSessionLocal() as session:
        # Show Users
        print("\n[USERS TABLE]")
        result = await session.execute(text("SELECT name, phone, role, current_score FROM users"))
        users = result.fetchall()
        for u in users:
            print(f" - {u[0]} | {u[1]} | {u[2]} | XP: {u[3]}")

        # Show Campaigns
        print("\n[CAMPAIGNS TABLE]")
        result = await session.execute(text("SELECT name, status, target_url FROM campaigns"))
        campaigns = result.fetchall()
        for c in campaigns:
            print(f" - {c[0]} ({c[1]}) -> {c[2]}")
            
    print("\n--------------------------")

if __name__ == "__main__":
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(show_data())
