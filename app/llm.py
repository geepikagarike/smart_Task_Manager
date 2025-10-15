"""LLM wrapper — supports a real OpenAI call when OPENAI_API_KEY is set,
and falls back to a deterministic local mock used for development.
"""
from typing import List, Dict, Any, Optional
import os
import json

OPENAI_KEY = os.getenv("OPENAI_API_KEY")


def _mock_plan(goal: str, deadline: Optional[str] = None, preferences: Optional[dict] = None) -> Dict[str, Any]:
    # Simple deterministic mock used for development and tests
    tasks = [
        {"id": "t1", "title": "Define scope and requirements", "description": "Write clear acceptance criteria.", "dependencies": [], "est_hours": 6.0},
        {"id": "t2", "title": "Design & assets", "description": "Create UI/marketing assets.", "dependencies": ["t1"], "est_hours": 8.0},
        {"id": "t3", "title": "Implementation", "description": "Develop core features.", "dependencies": ["t2"], "est_hours": 20.0},
        {"id": "t4", "title": "Testing & QA", "description": "Test flows and fix bugs.", "dependencies": ["t3"], "est_hours": 6.0},
        {"id": "t5", "title": "Launch", "description": "Deploy and announce.", "dependencies": ["t4"], "est_hours": 4.0},
    ]
    return {"goal": goal, "tasks": tasks, "deadline": deadline, "preferences": preferences}


def _call_openai(goal: str, deadline: Optional[str], preferences: Optional[dict]) -> Dict[str, Any]:
    try:
        import openai
    except Exception:
        # if package not installed for some reason, fall back to mock
        return _mock_plan(goal, deadline, preferences)

    openai.api_key = OPENAI_KEY

    system_prompt = (
        "You are an assistant that breaks down goals into actionable tasks with deadlines and dependencies. "
        "Output only JSON matching the schema: {\"goal\":string, \"tasks\":[{\"id\":string,\"title\":string,\"description\":string,\"dependencies\":[],\"est_hours\":number}]}"
    )

    user_prompt = (
        f"Break down this goal into actionable tasks with suggested deadlines and dependencies:\n\n"
        f"Goal: {goal}\n"
        f"Deadline: {deadline}\n"
        f"Preferences: {json.dumps(preferences) if preferences else '{}'}\n\n"
        "Return only valid JSON matching the schema above."
    )

    # Use ChatCompletion (works with openai package versions supporting it)
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=1000,
            temperature=0.2,
        )
        text = response["choices"][0]["message"]["content"].strip()
        # attempt to parse JSON from the model output
        try:
            parsed = json.loads(text)
            # minimal validation
            if "tasks" in parsed and isinstance(parsed["tasks"], list):
                return parsed
        except json.JSONDecodeError:
            # try to find the first JSON object in the text
            start = text.find("{")
            end = text.rfind("}")
            if start != -1 and end != -1:
                try:
                    parsed = json.loads(text[start:end+1])
                    if "tasks" in parsed and isinstance(parsed["tasks"], list):
                        return parsed
                except Exception:
                    pass
    except Exception:
        # on any error (network, rate limit, key invalid) fall back to mock
        return _mock_plan(goal, deadline, preferences)

    # final fallback
    return _mock_plan(goal, deadline, preferences)


def generate_plan_from_goal(goal: str, deadline: Optional[str] = None, preferences: Optional[dict] = None) -> Dict[str, Any]:
    """Return a dict with key 'tasks' as a list of task dicts.

    If OPENAI_API_KEY is set, this will attempt to call OpenAI and parse a JSON response. Otherwise it returns a deterministic mock plan.
    """
    if OPENAI_KEY:
        return _call_openai(goal, deadline, preferences)
    return _mock_plan(goal, deadline, preferences)
