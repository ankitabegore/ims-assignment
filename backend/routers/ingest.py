from fastapi import APIRouter, Request, HTTPException
import asyncio
from slowapi import Limiter
from slowapi.util import get_remote_address
from models.signal import Signal
from queue.signal_queue import signal_queue

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

@router.post("/signals", status_code=202)
@limiter.limit("1000/second")
async def ingest_signal(request: Request, signal: Signal):
    try:
        # Push to backpressure queue and return immediately
        signal_queue.put_nowait(signal)
        return {"status": "accepted", "signal_id": signal.id}
    except asyncio.QueueFull:
        raise HTTPException(status_code=503, detail="System under heavy load")
