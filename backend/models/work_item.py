from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from .enums import Priority, Status, RootCauseCategory

class RCA(BaseModel):
    category: RootCauseCategory
    description: str
    preventative_actions: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class WorkItem(BaseModel):
    id: str
    component_id: str
    title: str
    status: Status = Status.OPEN
    priority: Priority = Priority.P3
    signals: List[str] = Field(default_factory=list)
    rca: Optional[RCA] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
