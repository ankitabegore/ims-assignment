import asyncpg
from config import settings

class TimescaleClient:
    def __init__(self):
        self.pool = None

    async def connect(self):
        url = settings.TIMESCALE_URL.replace("+asyncpg", "")
        self.pool = await asyncpg.create_pool(url)
        async with self.pool.acquire() as conn:
            # Check if timescaledb extension exists
            await conn.execute("CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;")
            
            # Create metrics table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS signal_metrics (
                    time TIMESTAMPTZ NOT NULL,
                    component_id TEXT NOT NULL,
                    signal_id TEXT NOT NULL
                );
            """)
            
            # Convert to hypertable if not already
            try:
                await conn.execute("SELECT create_hypertable('signal_metrics', 'time', if_not_exists => TRUE);")
            except Exception as e:
                pass

    async def close(self):
        if self.pool:
            await self.pool.close()

timescale_client = TimescaleClient()
