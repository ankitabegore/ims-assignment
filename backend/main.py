from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from routers.ingest import router as ingest_router, limiter
from routers.stream import router as stream_router
from routers.incidents import router as incidents_router
from routers.rca import router as rca_router
from health import router as health_router
import asyncio
from queue.worker import worker
import logging
from contextlib import asynccontextmanager

from db.mongo import mongo_client
from db.postgres import pg_client
from db.redis_client import redis_client
from db.timescale import timescale_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await mongo_client.connect()
    await pg_client.connect()
    await redis_client.connect()
    await timescale_client.connect()
    logger.info("Databases connected.")

    worker_task = asyncio.create_task(worker())
    logger.info("Application starting up...")
    
    yield
    
    logger.info("Shutting down...")
    worker_task.cancel()
    try:
        await worker_task
    except asyncio.CancelledError:
        pass

    await mongo_client.close()
    await pg_client.close()
    await redis_client.close()
    await timescale_client.close()
    logger.info("Databases disconnected.")

app = FastAPI(title="IMS API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.include_router(ingest_router)
app.include_router(health_router)
app.include_router(stream_router)
app.include_router(incidents_router)
app.include_router(rca_router)
