from datetime import datetime, timedelta

class Resource:
    def __init__(self, resource_name, resource_attributes = None):
        self.resource_name = resource_name
        self.resource_attributes = resource_attributes
    
    def __repr__(self):
        return f"Resource({self.resource_name})"

class Event:
    def __init__(self, event_title, start_time, end_time, required_resources, event_metadata = None, recurrence_pattern = None, status = "pendiente"):
        self.event_title = event_title
        try:
            self.start_time = start_time if isinstance(start_time, datetime) else datetime.fromisoformat(start_time)
            self.end_time = end_time if isinstance(end_time, datetime) else datetime.fromisoformat(end_time)
        except Exception:
            raise ValueError("Formato de fecha inválido, usa YYYY-MM-DDTHH:MM:SS")
        if self.end_time <= self.start_time:
            raise ValueError("El tiempo de finalizacion debe ser despues del de inicio")
        self.required_resources = list(required_resources)
        self.event_metadata = event_metadata or {}
        self.recurrence_pattern = recurrence_pattern
        self.status = status
    
    def __repr__(self):
        return f"Event({self.event_title}, {self.start_time.isoformat()} => {self.end_time.isoformat()}, {self.required_resources})"
    
    def overlaps(self, other_event):
        return not (self.end_time <= other_event.start_time or self.start_time >= other_event.end_time)
    
    def generate_recurrence_occurrences(self):
        if not self.recurrence_pattern:
            return[self]
        frequency = self.recurrence_pattern.get("freq")
        count = int(self.recurrence_pattern.get("count", 1))
        if frequency == "daily":
            delta = timedelta(days=1)
        elif frequency == "weekly":
            delta = timedelta(weeks=1)
        elif frequency == "monthly":
            delta = timedelta(days=30)
        else:
            return [self]
        
        occurrences = []
        for i in range(count):
            start = self.start_time + i * delta
            end = self.end_time + i * delta
            occ = Event(
                f"{self.event_title} (#{i+1})", 
                start, 
                end, 
                self.required_resources, 
                self.event_metadata,
                self.recurrence_pattern,
                self.status
            )
            occurrences.append(occ)
        return occurrences    
        
    