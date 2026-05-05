import asyncpg
from config import settings

class PostgresClient:
    def __init__(self):
        self.pool = None

    async def connect(self):
        # asyncpg connection string does not support "postgresql+asyncpg", just "postgresql"
        url = settings.POSTGRES_URL.replace("+asyncpg", "")
        self.pool = await asyncpg.create_pool(url)
        # Initialize tables
        async with self.pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS work_items (
                    id TEXT PRIMARY KEY,
                    component_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    status TEXT NOT NULL,
                    priority TEXT NOT NULL,
                    signals JSONB,
                    rca JSONB,
                    created_at TIMESTAMP,
                    updated_at TIMESTAMP,
                    resolved_at TIMESTAMP,
                    closed_at TIMESTAMP
                );
            """)

    async def close(self):
        if self.pool:
            await self.pool.close()

pg_client = PostgresClient()
