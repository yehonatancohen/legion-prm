import asyncio
import asyncpg
import os
from dotenv import load_dotenv

# Load env directly to avoid Pydantic validation issues if any
load_dotenv()

POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgrespassword")
POSTGRES_SERVER = os.getenv("POSTGRES_SERVER", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB", "promotion_manager")

async def create_database():
    print(f"Connecting to postgres system database at {POSTGRES_SERVER}:{POSTGRES_PORT} as {POSTGRES_USER}...")
    try:
        # Connect to 'postgres' system database
        sys_conn = await asyncpg.connect(
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            host=POSTGRES_SERVER,
            port=POSTGRES_PORT,
            database=POSTGRES_DB
        )
    except Exception as e:
        print(f"Failed to connect to system database: {e}")
        return

    try:
        # Check if db exists
        exists = await sys_conn.fetchval("SELECT 1 FROM pg_database WHERE datname = $1", POSTGRES_DB)
        if not exists:
            print(f"Database '{POSTGRES_DB}' does not exist. Creating it...")
            await sys_conn.execute(f'CREATE DATABASE "{POSTGRES_DB}"')
            print(f"Database '{POSTGRES_DB}' created successfully!")
        else:
            print(f"Database '{POSTGRES_DB}' already exists according to Postgres.")
    except Exception as e:
        print(f"Error creating database: {e}")
    finally:
        await sys_conn.close()

if __name__ == "__main__":
    asyncio.run(create_database())
