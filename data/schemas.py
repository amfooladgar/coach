# data/schemas.py
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class Task(BaseModel):
    task_id: str
    title: str
    why: str
    steps: List[str]
    priority: str = Field(..., pattern="^(P1|P2|P3)$")
    energy: str = Field(..., pattern="^(deep|steady|light)$")
    duration_est_min: int
    due: datetime
    pillar: str = Field(..., pattern="^(Connection|Curiosity|Presence|Contribution)$")
    deps: List[str] = []
    status: str = Field(..., pattern="^(todo|doing|done|blocked)$")
    artifact_link: Optional[str] = None
    source: str = Field(default="goal", pattern="^(goal|reflection)$")

class CalendarEvent(BaseModel):
    event_id: str
    task_id: Optional[str] = None  # None for breaks/fixed blocks
    title: str
    start_time: datetime
    end_time: datetime
    duration_min: int
    block_type: str = Field(..., pattern="^(work|break|fixed|travel)$")
    created_at: datetime
