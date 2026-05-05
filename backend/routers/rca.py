from fastapi import APIRouter, HTTPException
from models.work_item import RCA
from db.postgres import pg_client
import json

router = APIRouter()

@router.post("/incidents/{incident_id}/rca")
async def submit_rca(incident_id: str, rca: RCA):
    from db.redis_client import redis_client
    
    async with pg_client.pool.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM work_items WHERE id = $1", incident_id)
        if not row:
            raise HTTPException(status_code=404, detail="Incident not found")
            
        await conn.execute("""
            UPDATE work_items 
            SET rca = $1, updated_at = NOW() 
            WHERE id = $2
        """, rca.model_dump_json(), incident_id)
        
    if redis_client.client:
        event = {"type": "update_incident", "id": incident_id}
        await redis_client.client.publish("incident_updates", json.dumps(event))
        
    return {"status": "rca_submitted"}

@router.get("/incidents/{incident_id}/rca-suggestion")
async def get_rca_suggestion(incident_id: str):
    from services.llm_rca import generate_mock_rca
    async with pg_client.pool.acquire() as conn:
        row = await conn.fetchrow("SELECT component_id FROM work_items WHERE id = $1", incident_id)
        if not row:
            raise HTTPException(status_code=404, detail="Incident not found")
            
    suggestion = await generate_mock_rca(row['component_id'])
    return suggestion

