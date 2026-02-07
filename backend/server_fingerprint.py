import asyncio
import os
from sqlalchemy import text
from app.core.database import AsyncSessionLocal

async def server_fingerprint():
    print("\n--- SERVER FINGERPRINT ---")
    async with AsyncSessionLocal() as session:
        # 1. Get Data Directory (Unique ID of the server instance)
        try:
            res = await session.execute(text("SHOW data_directory;"))
            data_dir = res.scalar()
            print(f"Data Directory: {data_dir}")
        except Exception as e:
            print(f"Could not get data_dir: {e}")

        # 2. Get Current Schema
        try:
            res = await session.execute(text("SELECT current_schema();"))
            schema = res.scalar()
            print(f"Current Schema: {schema}")
        except Exception as e:
            print(f"Could not get schema: {e}")

        # 3. List ALL Tables found in ALL schemas
        print("\n[ALL TABLES FOUND]")
        try:
            query = text("""
                SELECT table_schema, table_name 
                FROM information_schema.tables 
                WHERE table_schema NOT IN ('information_schema', 'pg_catalog')
            """)
            res = await session.execute(query)
            tables = res.fetchall()
            if not tables:
                print("⚠️ NO TABLES FOUND! (This is why you see nothing)")
            for t in tables:
                print(f" - {t[0]}.{t[1]}")
        except Exception as e:
            print(f"Error listing tables: {e}")

    print("\n--------------------------")

if __name__ == "__main__":
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(server_fingerprint())
