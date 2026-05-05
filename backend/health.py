from fastapi import APIRouter
from db.mongo import mongo_client
from db.postgres import pg_client
from db.redis_client import redis_client
from db.timescale import timescale_client

router = APIRouter()

@router.get("/health")
async def health():
    status = {
        "postgres": "ok" if pg_client.pool else "error",
        "mongo": "ok" if mongo_client.client else "error",
        "redis": "ok" if redis_client.client else "error",
        "timescale": "ok" if timescale_client.pool else "error",
    }
    return status
