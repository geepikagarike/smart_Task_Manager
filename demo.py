"""Demo script showing the Smart Task Planner in action.
This script submits a goal to the planner and displays the resulting task breakdown.
"""
import json
import requests
from datetime import datetime, timedelta

def print_plan(plan):
    """Pretty print a task plan with dependencies and timeline."""
    print("\nGoal:", plan["goal"])
    print("\nTasks:")
    for task in plan["tasks"]:
        deps = ", ".join(task["dependencies"]) if task["dependencies"] else "none"
        print(f"\n{task['id']}. {task['title']}")
        print(f"   Description: {task['description']}")
        print(f"   Estimated hours: {task['est_hours']}")
        print(f"   Dependencies: {deps}")
        if "earliest_start" in task:
            print(f"   Start: {task['earliest_start']}")
        if "latest_end" in task:
            print(f"   End: {task['latest_end']}")

def main():
    # Example goal with realistic timeline
    goal = "Launch a mobile app in 3 weeks"
    deadline = (datetime.now() + timedelta(weeks=3)).strftime("%Y-%m-%d")
    
    payload = {
        "goal": goal,
        "deadline": deadline,
        "preferences": {"work_per_day_hours": 4}
    }
    
    print("Submitting plan request...")
    print(f"Goal: {goal}")
    print(f"Deadline: {deadline}")
    
    try:
        response = requests.post(
            "http://localhost:8000/plan",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        plan = response.json()
        print_plan(plan)
        
        # Save example output
        with open("example_plan.json", "w") as f:
            json.dump(plan, f, indent=2)
        print("\nPlan saved to example_plan.json")
        
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        print("\nIs the server running? Start it with:")
        print("uvicorn app.main:app --reload --port 8000")

if __name__ == "__main__":
    main()