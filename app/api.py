from fastapi import APIRouter, HTTPException
from app.models import PlanRequest, PlanResponse
from app.llm import generate_plan_from_goal
from app.scheduling import schedule_tasks
from datetime import datetime
import uuid

router = APIRouter()


@router.post("/plan", response_model=PlanResponse)
async def create_plan(req: PlanRequest):
    if not req.goal or not req.goal.strip():
        raise HTTPException(status_code=400, detail="goal is required")

    # Call LLM (mock) to get raw tasks
    raw = generate_plan_from_goal(req.goal, deadline=req.deadline, preferences=req.preferences)

    # raw is expected to be a dict with 'tasks'
    try:
        tasks = raw["tasks"]
    except Exception:
        raise HTTPException(status_code=500, detail="LLM returned invalid format")

    # schedule tasks
    scheduled = schedule_tasks(tasks, deadline=req.deadline, preferences=req.preferences)

    plan_id = str(uuid.uuid4())
    resp = {
        "plan_id": plan_id,
        "goal": req.goal,
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "tasks": scheduled,
        "timeline_summary": {
            "start_date": scheduled[0]["earliest_start"] if scheduled else None,
            "end_date": scheduled[-1]["latest_end"] if scheduled else None,
            "total_tasks": len(scheduled),
        },
    }
    return resp
