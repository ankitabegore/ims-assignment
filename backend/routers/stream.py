import asyncio
from fastapi import APIRouter, Request
from sse_starlette.sse import EventSourceResponse
from db.redis_client import redis_client

router = APIRouter()

@router.get("/stream")
async def stream_incidents(request: Request):
    async def event_generator():
        pubsub = redis_client.client.pubsub()
        await pubsub.subscribe("incident_updates")
        try:
            while True:
                if await request.is_disconnected():
                    break
                    
                message = await pubsub.get_message(ignore_subscribe_messages=True)
                if message:
                    yield {"data": message["data"]}
                await asyncio.sleep(0.5)
        finally:
            await pubsub.unsubscribe("incident_updates")
            
    return EventSourceResponse(event_generator())
