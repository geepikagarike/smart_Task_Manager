from pydantic import BaseModel
from typing import List, Optional, Dict, Any


class Preferences(BaseModel):
    work_per_day_hours: Optional[float] = 4.0


class PlanRequest(BaseModel):
    goal: str
    deadline: Optional[str] = None
    preferences: Optional[Preferences] = None


class Task(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    dependencies: List[str] = []
    est_hours: float
    earliest_start: Optional[str] = None
    latest_end: Optional[str] = None


class PlanResponse(BaseModel):
    plan_id: str
    goal: str
    generated_at: str
    tasks: List[Task]
    timeline_summary: Optional[Dict[str, Any]] = None
