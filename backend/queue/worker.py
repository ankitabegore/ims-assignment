import asyncio
import logging
import uuid
import json
from datetime import datetime
from tenacity import retry, wait_exponential, stop_after_attempt

from .signal_queue import signal_queue
from .debounce import debouncer
from db.mongo import mongo_client
from db.postgres import pg_client
from db.timescale import timescale_client
from db.redis_client import redis_client
from models.enums import Status, Priority
from workflow.alert_strategy import get_alert_strategy

logger = logging.getLogger(__name__)

@retry(wait=wait_exponential(multiplier=1, min=1, max=10), stop=stop_after_attempt(3))
async def persist_batch(comp_id, signals):
    # 1. Mongo (raw signals)
    signal_dicts = [s.model_dump() for s in signals]
    if mongo_client.db is not None:
        await mongo_client.db.signals.insert_many(signal_dicts)

    # 2. Timescale
    if timescale_client.pool is not None:
        async with timescale_client.pool.acquire() as conn:
            records = [(s.timestamp, s.component_id, s.id) for s in signals]
            await conn.copy_records_to_table(
                'signal_metrics', records=records, columns=['time', 'component_id', 'signal_id']
            )

    # 3. Postgres (Work Item)
    async with pg_client.pool.acquire() as conn:
        # Check for open incident
        row = await conn.fetchrow("""
            SELECT id, status, signals FROM work_items 
            WHERE component_id = $1 AND status != 'CLOSED'
        """, comp_id)

        signal_ids = [s.id for s in signals]
        new_item = False
        
        if row:
            work_item_id = row['id']
            existing_signals = json.loads(row['signals']) if row['signals'] else []
            existing_signals.extend(signal_ids)
            await conn.execute("""
                UPDATE work_items 
                SET signals = $1, updated_at = $2
                WHERE id = $3
            """, json.dumps(existing_signals), datetime.utcnow(), work_item_id)
        else:
            new_item = True
            work_item_id = str(uuid.uuid4())
            await conn.execute("""
                INSERT INTO work_items (id, component_id, title, status, priority, signals, created_at, updated_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            """, work_item_id, comp_id, f"Incident for {comp_id}", Status.OPEN.value, Priority.P3.value, 
                 json.dumps(signal_ids), datetime.utcnow(), datetime.utcnow())

    # 4. Redis pub/sub for SSE
    if redis_client.client is not None:
        event = {"type": "new_incident" if new_item else "update_incident", "id": work_item_id}
        await redis_client.client.publish("incident_updates", json.dumps(event))

    # Alert Strategy if new item
    if new_item:
        from models.work_item import WorkItem
        # we construct a minimal WorkItem to pass to the strategy
        wi = WorkItem(id=work_item_id, component_id=comp_id, title=f"Incident for {comp_id}")
        get_alert_strategy(Priority.P3).send_alert(wi)

async def process_signal_batch(comp_id, signals):
    logger.info(f"Processing debounced batch for {comp_id}: {len(signals)} signals")
    try:
        await persist_batch(comp_id, signals)
    except Exception as e:
        logger.error(f"Failed to persist batch for {comp_id}: {e}")

debouncer.callback = process_signal_batch

async def worker():
    logger.info("Signal consumer worker started")
    while True:
        try:
            signal = await signal_queue.get()
            await debouncer.add_signal(signal)
            signal_queue.task_done()
        except asyncio.CancelledError:
            logger.info("Worker cancelled")
            break
        except Exception as e:
            logger.error(f"Error processing signal in worker: {e}")
