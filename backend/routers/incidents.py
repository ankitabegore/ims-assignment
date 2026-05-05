from fastapi import APIRouter, HTTPException
from typing import List
from models.work_item import WorkItem
from models.enums import Status
from db.postgres import pg_client
import json

router = APIRouter()

@router.get("/incidents", response_model=List[WorkItem])
async def list_incidents():
    if not pg_client.pool:
        raise HTTPException(status_code=503, detail="Database not ready")
        
    async with pg_client.pool.acquire() as conn:
        rows = await conn.fetch("SELECT * FROM work_items ORDER BY updated_at DESC LIMIT 100")
        
    result = []
    for row in rows:
        item = dict(row)
        item['signals'] = json.loads(item['signals']) if item['signals'] else []
        item['rca'] = json.loads(item['rca']) if item['rca'] else None
        result.append(WorkItem(**item))
    return result

@router.get("/incidents/{incident_id}", response_model=WorkItem)
async def get_incident(incident_id: str):
    async with pg_client.pool.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM work_items WHERE id = $1", incident_id)
        
    if not row:
        raise HTTPException(status_code=404, detail="Incident not found")
        
    item = dict(row)
    item['signals'] = json.loads(item['signals']) if item['signals'] else []
    item['rca'] = json.loads(item['rca']) if item['rca'] else None
    return WorkItem(**item)

@router.patch("/incidents/{incident_id}/status")
async def update_status(incident_id: str, status: Status):
    from workflow.state_machine import get_state_machine, InvalidTransitionError, RCAMissingError
    from db.redis_client import redis_client
    
    async with pg_client.pool.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM work_items WHERE id = $1", incident_id)
        if not row:
            raise HTTPException(status_code=404, detail="Incident not found")
            
        item = dict(row)
        item['signals'] = json.loads(item['signals']) if item['signals'] else []
        item['rca'] = json.loads(item['rca']) if item['rca'] else None
        work_item = WorkItem(**item)
        
        try:
            state_machine = get_state_machine(work_item)
            state_machine.transition(status)
        except InvalidTransitionError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except RCAMissingError as e:
            raise HTTPException(status_code=400, detail=str(e))
            
        await conn.execute("""
            UPDATE work_items 
            SET status = $1, updated_at = NOW() 
            WHERE id = $2
        """, status.value, incident_id)
        
    # Notify via SSE
    if redis_client.client:
        event = {"type": "update_incident", "id": incident_id}
        await redis_client.client.publish("incident_updates", json.dumps(event))
        
    return {"status": "updated", "new_status": status.value}
