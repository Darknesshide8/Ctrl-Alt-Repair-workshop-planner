import json
import os
from datetime import datetime
from models import Event, Resource

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SAVE_DIR = os.path.join(BASE_DIR, "save")
os.makedirs(SAVE_DIR, exist_ok=True)

DEFAULT_FILE = os.path.join(SAVE_DIR, "data.json")

def save_planner_state(planner, filename=DEFAULT_FILE):
    data = {
        "resources": [
            {"name": r.resource_name, "attributes": r.resource_attributes}
            for r in planner.available_resources.values()
        ],
        "events": [
            {
                "title": ev.event_title,
                "start": ev.start_time.isoformat(),
                "end": ev.end_time.isoformat(),
                "resources": ev.required_resources,
                "metadata": ev.event_metadata,
                "recurrence": ev.recurrence_pattern
            } for ev in planner.scheduled_events
        ],
        "restrictions": planner.resource_restrictions,
        "pools": planner.resource_pools,
    }
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        
def load_planner_state(planner, filename =DEFAULT_FILE):
    with open(filename, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    planner.scheduled_events.clear()
    planner.available_resources.clear()
    planner.resource_restrictions = data.get("restrictions", {"corequisite": [], "exclusion": []})
    planner.resource_pools = data.get("pools", {})
    
    for r in data.get("resources", []):
        planner.add_resource(Resource(r["name"], r.get("attributes")))
    
    for e in data.get("events", []):
        event = Event(
            e["title"],
            datetime.fromisoformat(e["start"]),
            datetime.fromisoformat(e["end"]),
            e["resources"],
            e.get("metadata"),
            e.get("recurrence")
        )
        ok, _ = planner.schedule_event(event)
                