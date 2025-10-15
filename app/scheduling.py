from typing import List, Dict, Any, Optional
from math import ceil
from datetime import datetime, timedelta


def topological_sort(tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    # Kahn's algorithm
    id_map = {t["id"]: t for t in tasks}
    in_degree = {t["id"]: 0 for t in tasks}
    adj = {t["id"]: [] for t in tasks}
    for t in tasks:
        for d in t.get("dependencies", []):
            adj[d].append(t["id"])
            in_degree[t["id"]] += 1

    q = [tid for tid, deg in in_degree.items() if deg == 0]
    out = []
    while q:
        n = q.pop(0)
        out.append(id_map[n])
        for m in adj.get(n, []):
            in_degree[m] -= 1
            if in_degree[m] == 0:
                q.append(m)

    if len(out) != len(tasks):
        raise ValueError("Cycle detected or missing dependency")
    return out


def schedule_tasks(tasks: List[Dict[str, Any]], deadline: Optional[str] = None, preferences: Optional[dict] = None) -> List[Dict[str, Any]]:
    prefs = {"work_per_day_hours": 4.0}
    if preferences:
        prefs.update(preferences if isinstance(preferences, dict) else preferences.dict())

    sorted_tasks = topological_sort(tasks)
    # project start is today
    project_start = datetime.utcnow().date()
    scheduled = []
    end_dates = {}

    for t in sorted_tasks:
        deps = t.get("dependencies", []) or []
        if not deps:
            start = project_start
        else:
            # start next day after latest dependency end
            latest = max(datetime.fromisoformat(end_dates[d]).date() for d in deps)
            start = latest + timedelta(days=1)

        days = max(1, ceil(t.get("est_hours", 1.0) / float(prefs.get("work_per_day_hours", 4.0))))
        end = start + timedelta(days=days - 1)

        t_out = dict(t)
        t_out["earliest_start"] = start.isoformat()
        t_out["latest_end"] = end.isoformat()
        scheduled.append(t_out)
        end_dates[t["id"]] = end.isoformat()

    # If deadline provided, no automatic reschedule yet — just return schedule and let caller handle conflict.
    return scheduled
