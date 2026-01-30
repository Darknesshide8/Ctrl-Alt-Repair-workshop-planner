from datetime import timedelta
from models import Event, Resource

class Planner:
    def __init__(self):
        self.scheduled_events = []
        self.available_resources = {}
        self.resource_restrictions = {"corequisite": [], "exclusion": []}
        self.resource_pools = {}
        #Catalogo que muestra todos los tipos de trabajo que se realizan en el taller, asi como los skills, pools y devices que requiere
        self.job_catalog = {
            #=== Mantenimiento de Hardware ===
            "Reemplazo de pasta termica": {
                "skills": ["Hardware Specialist"],
                "pools": {"Mesa de trabajo": 1},
                "devices": ["Kit Antiestatico"]
            },
            "Cambio y soldadura de componentes": {
                "skills": ["Hardware Specialist"],
                "pools": {"Mesa de trabajo": 1},
                "devices": ["Estacion de soldadura", "Kit Antiestatico"]
            },
            "Reflow de GPU": {
                "skills": ["Hardware Specialist"],
                "pools": {"Mesa de trabajo": 1},
                "devices": ["Horno de Reflow","Kit Antiestatico"]
            },
            
            #=== Recuperacion de datos ===
            "Clonacion de discos": {
                "skills": ["Data Recovery Expert"],
                "pools": {"Duplicadora de Discos": 1},
                "devices": []
            },
            
            "Rescate de informacion deteriorada": {
                "skills": ["Data Recovery Expert"],
                "pools": {"Duplicadora de Discos": 1},
                "devices": ["Kit Antiestatico"]
            },
            
            #=== Seguridad y Software ===
            "Chequeo Antivirus": {
                "skills": ["Software Specialist"],
                "pools": {"Mesa Compartida": 1},
                "devices": ["PC cliente"]
            },
            
            "Reinstalacion de sistemas": {
                "skills": ["Software Specialist"],
                "pools": {"Mesa Compartida": 1},
                "devices": ["PC cliente"]
            },
            
            #=== Mantenimiento preventivo ===
            "Mantenimiento preventivo semanal": {
                "skills": ["Hardware Specialist"],
                "pools": {"Mesa Compartida": 1},
                "devices": ["Kit Antiestatico"]
            },
            
            "Limpieza profunda mensual": {
            "skills": ["Hardware Specialist"],
            "pools": {"Mesa Compartida": 1},
            "devices": ["Kit Antiestatico"]
            },
            
            "Chequeo de scripts de diagnostico preventivo": {
            "skills": ["Programador"],
             "pools": {"Mesa Compartida": 1},
            "devices": ["PC de desarrollo"]
            },
            
            # === Automatizacion ===
            "Automatizacion de scripts internos": {
            "skills": ["Programador"],
            "pools": {"Mesa Compartida": 1},
            "devices": ["PC de desarrollo"]
            },
            
            
        }
    
    def add_resource(self, resource: Resource):
        self.available_resources[resource.resource_name] = resource
    
    def list_resource(self):
        return list(self.available_resources.values())
    
    def add_corequisite(self, resource_a, resource_b):
        self.resource_restrictions["corequisite"].append((resource_a, resource_b))
    
    def add_exclusion(self, resource_a, resource_b):
        self.resource_restrictions["exclusion"].append((resource_a, resource_b))
        
    def set_pool(self, resource_type_name: str, quantity: int):
        self.resource_pools[resource_type_name] = quantity
        
    # --- Validación completa ---
    def validate_event(self, new_event: Event):
        # 1. Recursos existentes
        for res in new_event.required_resources:
            if res not in self.available_resources and res not in self.resource_pools:
                return False, f"Recurso inexistente: '{res}'"

        # 2. Conflictos de tiempo y recursos
        for existing in self.scheduled_events:
            if existing.overlaps(new_event):
                for resource_name in new_event.required_resources:
                    if resource_name in existing.required_resources:
                        return False, f"Conflicto: recurso '{resource_name}' ocupado por '{existing.event_title}'"
                return False, f"Conflicto de horario con '{existing.event_title}'"

        # 3. Restricciones
        for req_a, req_b in self.resource_restrictions["corequisite"]:
            if req_a in new_event.required_resources and req_b not in new_event.required_resources:
                return False, f"Restricción: '{req_a}' requiere '{req_b}'"
        for ex_a, ex_b in self.resource_restrictions["exclusion"]:
            if ex_a in new_event.required_resources and ex_b in new_event.required_resources:
                return False, f"Restricción: '{ex_a}' no puede coexistir con '{ex_b}'"

        # 4. Catálogo de trabajos
        job_requirements = self.job_catalog.get(new_event.event_title)
        if job_requirements:
            # Skills
            for skill in job_requirements.get("skills", []):
                found = False
                for res_name in new_event.required_resources:
                    res = self.available_resources.get(res_name)
                    if res and skill in res.resource_attributes.get("skills", []):
                        found = True
                        break
                if not found:
                    return False, f"Este trabajo requiere un especialista con la skill: '{skill}' pero no se encontro ninguno."

            # Pools
            for pool, qty in job_requirements.get("pools", {}).items():
                if self.resource_pools.get(pool, 0) < qty:
                    return False, f"Este trabajo necesita {qty} unidad(es) de '{pool}', pero no hay suficientes en el taller."

            # Devices
            for device in job_requirements.get("devices", []):
                if device not in new_event.required_resources:
                    return False, f"Este trabajo requiere el dispositivo '{device}', pero no fue asignado."

        return True, None

    def schedule_event(self, event: Event):
        occurrences = event.generate_recurrence_occurrences()
        for occ in occurrences:
            ok, msg = self.validate_event(occ)
            if not ok:
                return False, msg
        self.scheduled_events.extend(occurrences)
        return True, f"Evento '{event.event_title}' agregado con {len(occurrences)} ocurrencias."
        
    
    def list_scheduled_events(self):
        return sorted(self.scheduled_events, key=lambda e: e.start_time)
    
    def get_event_by_title(self, title: str):
        for ev in self.scheduled_events:
            if ev.event_title == title:
                return ev
        return None    
    
    def get_schedule_for_resource(self, resource_name: str):
        return sorted([ev for ev in self.scheduled_events if resource_name in ev.required_resources], key=lambda e: e.start_time)
    
    def find_next_available_slot(self, template_event: Event, search_from_dt):
        step = timedelta(minutes=30)
        duration = template_event.end_time - template_event.start_time
        attempts = 0
        while attempts < 5000:
            candidate_start = search_from_dt + attempts * step
            candidate_end = candidate_start + duration
            candidate = Event(
                template_event.event_title,
                candidate_start,
                candidate_end,
                template_event.required_resources,
                template_event.event_metadata,
                None
            )
            ok, msg = self.validate_event(candidate)
            if ok:
                return candidate_start, candidate_end
            attempts +=1
        return None, None
    
    def validate_status(self, status: str) -> bool:
        return status in ["pendiente", "en progreso", "completado"]
    
    
      