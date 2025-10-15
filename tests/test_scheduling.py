import sys
import os
import pytest

# ensure project root is on sys.path so 'app' package is importable when running pytest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.scheduling import schedule_tasks, topological_sort


def test_topological_sort_simple():
    tasks = [
        {"id": "a", "dependencies": []},
        {"id": "b", "dependencies": ["a"]},
        {"id": "c", "dependencies": ["b"]},
    ]
    out = topological_sort(tasks)
    assert [t["id"] for t in out] == ["a", "b", "c"]


def test_cycle_detection():
    tasks = [
        {"id": "a", "dependencies": ["c"]},
        {"id": "b", "dependencies": ["a"]},
        {"id": "c", "dependencies": ["b"]},
    ]
    with pytest.raises(ValueError):
        topological_sort(tasks)


def test_schedule_basic():
    tasks = [
        {"id": "t1", "dependencies": [], "est_hours": 4},
        {"id": "t2", "dependencies": ["t1"], "est_hours": 8},
    ]
    scheduled = schedule_tasks(tasks, preferences={"work_per_day_hours": 4})
    assert len(scheduled) == 2
    assert scheduled[0]["earliest_start"] <= scheduled[1]["earliest_start"]
