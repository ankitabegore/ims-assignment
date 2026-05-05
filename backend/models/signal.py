from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any

class Signal(BaseModel):
    id: str = Field(..., description="Unique identifier for the signal")
    component_id: str = Field(..., description="ID of the failing component")
    message: str = Field(..., description="Description of the failure")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
