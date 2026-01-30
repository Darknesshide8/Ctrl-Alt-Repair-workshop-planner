from models import Event, Resource
from planner import Planner
from storage import save_planner_state, load_planner_state
from datetime import datetime
import os


aplication_name = "Ctrl + Alt + Repair"

def format_event(ev: Event, index: int = None) -> str:
    client = ev.event_metadata.get("client", "")
    status = ev.event_metadata.get("status", "pendiente")
    notes = ev.event_metadata.get("notes", "")
    prefix = f"{index}. " if index is not None else ""
    return(
        f"{prefix}{ev.event_title} | {ev.start_time} => {ev.end_time} | "
        f"Recursos : {', '.join(ev.required_resources)}"
        + (f" | Cliente : {client}")
        + f" | Estado: {status}" 
        + (f" | Notes: {notes}" if notes else "")
    )

def select_event_by_index(planner, prompt = "Índice del evento: "):
    events = planner.list_scheduled_events()
    if not events:
        print("No hay eventos programados actualmente")
        return None, events
    try:
        idx = int(input(prompt).strip())
        if 0 <= idx <= len(events):
            return events[idx], events
        else:
            print("Indice fuera de rango.")
            return None, events
    except ValueError:
        print("Debes ingresar un número válido")
        return None, events

def get_date(prompt):
    while True:
        date_str = input(f"{prompt} (o escribe 'cancel' para cancelar): ").strip()
        if date_str.lower() == "cancel":
            return None
        try:
            datetime.fromisoformat(date_str)
            return date_str
        except ValueError:
            print("Formato de fecha invalido. Usa YYYY-MM-DDTHH:MM:SS (por ejemplo: 2025-12-09T09:00:00)")
    
    
    

def run_cli():
    print(f"Bienvenido a {aplication_name} - Planificador de reparaciones de computadoras (CLI)")
    workshop_planner = Planner()
    
    try:
        load_planner_state(workshop_planner, "data.json")
        print("Estado cargado satisfactoriamente desde data.json")
    except FileNotFoundError:
        print("No existe data.json, iniciando estado vacio.")
        
    while True:
        print("\nComandos: help, list, add, remove, jobs, res, slot, addres, addpool, rules, seed, save, load, clear, quit, clean")
        command = input("> ").strip().lower()
        
        if command == "help":
            print("Comandos disponibles en Ctrl + Alt + Repair:\n      list      =>  Lista todos  los eventos programados.\n      add      =>  Agrega un nuevo evento (con recurrencia opcional).\n      remove      => Elimina un evento por índice.\n      res      => Muestra la agenda de un recurso.\n      slot      => Busca el proximo hueco disponible para un evento.\n      addres      => Agrega un recurso con atributos.\n      addpool      => Configura un pool de recursos (tipo con cantidad).\n      rules      => Muestra las restricciones actuales.\n      seed       => Carga el dominio base del taller Ctrl + Alt + Repair.\n      save       => Guarda el estado en data.json.\n      load      => Carga el estado desde data.json\n      help       => Muestra esta ayuda\n      quit      => Sale de la aplicacion.\n      jobs      => Muestra un catalogo de los tipos de trabajos disponibles para realizar en el taller Ctrl + Alt + Repair.\n      clear      => Elimina toda la información (eventos, recursos, etc).\n      clean      => Limpia la consola.")
        
        elif command == "list":
            events = workshop_planner.list_scheduled_events()
            if not events:
                print("Sin eventos")
            else:
                for i, ev in enumerate(events):
                    print(format_event(ev, i))
        
        elif command == "add":
            try:
                title = input("Titulo: ").strip()
                client = input("Cliente: ").strip()
                start = get_date("Inicio (YYYY-MM-DDTHH:MM:SS): ").strip()
                end = get_date("Fin (YYYY-MM-DDTHH:MM:SS): ").strip()
                if end <= start:
                    raise ValueError("El tiempo de finalizacion debe ser despues del de inicio")
                resources = [x.strip() for x in input("Recursos (separados por coma): ").split(",") if x.strip()]
                rec_freq = input("Recurrencia (none/daily/weekly/monthly): ").strip().lower()
                recurrence = None
                if rec_freq in ("daily", "weekly", "monthly"):
                    rec_count_in = input("Repeticiones (entero, por defecto 1): ").strip()
                    rec_count = int(rec_count_in) if rec_count_in else 1
                    recurrence = {"freq": rec_freq, "count": rec_count}
                
                new_event = Event(title, start, end, resources, {"client": client}, recurrence)
                ok, msg = workshop_planner.schedule_event(new_event)
                print(msg)
            except Exception as e:
                print(f"Error: {e}")
                
        elif command == "remove":
            ev, events = select_event_by_index(workshop_planner, "Indice del evento a eliminar: ")
            if ev:
                workshop_planner.scheduled_events.remove(ev)
                print(f"Evento '{ev.event_title}' eliminado correctamente.")
        
        elif command == "jobs":
            print("Catalogo de trabajos disponibles en el taller Ctrl + Alt + Repair")
            for job in workshop_planner.job_catalog:
                print(f" - {job}")
            
        elif command == "res":
            name = input("Recurso: ").strip()
            sched = workshop_planner.get_schedule_for_resource(name)
            if not sched:
                print("Sin agenda para ese recurso, o inexistente.")
            else:
                for i, ev in enumerate(sched):
                    print(format_event(ev, i))
        
        elif command == "slot":
            try:
                title = input("Titulo del evento base: ").strip()
                ev = workshop_planner.get_event_by_title(title)
                if not ev:
                    print("Evento no encontrado.")
                    continue
                from_str = input("Buscar desde (YYYY-MM-DDTHH:MM:SS) ").strip()
                from_dt = datetime.fromisoformat(from_str)
                slot_start, slot_end = workshop_planner.find_next_available_slot(ev, from_dt)
                if slot_start and slot_end:
                    print(f"Hueco: {slot_start} => {slot_end}")
                else:
                    print("No se encontro hueco en el rango")
            except Exception as e:
                print(f"Error: {e}")
                
        elif command == "addres":
            name = input("Nombre del recurso: ").strip()
            typ = input("Tipo (tech, station, tool, device) ").strip()
            attrs = {"type": typ}
            skills = input("Skills (opcional, coma): ").strip()
            if skills:
                attrs["skills"] = [s.strip() for s in skills.split(",") if s.strip()]
            workshop_planner.add_resource(Resource(name, attrs))
            print(f"Recurso agregado: {name} ({typ})")
        
        elif command == "addpool":
            typ = input("Tipo de recurso pool (nombre exacto, ej: 'Duplicadora de Discos') ").strip()
            qty = int(input("Cantidad disponible: ").strip())
            workshop_planner.set_pool(typ, qty)
            print(f"Pool configurado: {typ} = {qty}")
        
        elif command == "rules":
            print("=== Reglas actuales del taller ===")

            # Corequisitos
            print("Correquisitos:")
            if workshop_planner.resource_restrictions["corequisite"]:
                for a, b in workshop_planner.resource_restrictions["corequisite"]:
                    print(f"  - {a} requiere {b}")
            else:
                print("  (ninguno)")

            # Exclusiones
            print("Exclusiones:")
            if workshop_planner.resource_restrictions["exclusion"]:
                for a, b in workshop_planner.resource_restrictions["exclusion"]:
                    print(f"  - {a} excluye {b}")
            else:
                print("  (ninguno)")

            # Pools
            print("Pools de recursos:")
            if workshop_planner.resource_pools:
                for pool, qty in workshop_planner.resource_pools.items():
                    print(f"  - {pool}: {qty} unidades disponibles")
            else:
                print("  (ninguno)")

            # Catálogo de trabajos
            print("Catálogo de trabajos:")
            for job, reqs in workshop_planner.job_catalog.items():
                parts = []
                if reqs.get("skills"):
                    skills = ", ".join(reqs["skills"])
                    parts.append(skills)
                if reqs.get("pools"):
                    pools = ", ".join(f"{qty} {pool}" for pool, qty in reqs["pools"].items())
                    parts.append(pools)
                if reqs.get("devices"):
                    devices = ", ".join(reqs["devices"])
                    parts.append(devices)

                requirements = ", ".join(parts)
                print(f"  - {job} siempre requiere {requirements}")
        
        elif command == "seed":
            seed_domain(workshop_planner)
            print("Dominio base de Ctrl + Alt + Repair cargado.")
        
        elif command == "save":
            save_planner_state(workshop_planner)
            print("Guardado en data.json")
        
        elif command == "load":
            try:
                load_planner_state(workshop_planner)
                print("Cargado data.json")
            except FileNotFoundError:
                print("No existe data.json")
        
        elif command == "clear":
            confirm = input("¿Seguro que quieres eliminar toda la información? (y/n): ")
            if confirm.lower() == "y":
                workshop_planner.scheduled_events = []
                workshop_planner.available_resources = {}
                workshop_planner.resource_restrictions = {"corequisite": [], "exclusion": []}
                workshop_planner.resource_pools = {}
                workshop_planner.job_catalog = []
            print("Toda la información fue borrada, recuerda que siempre puedes cargar una plantilla predefinida usando el comando 'seed'.")
        
        elif command == "quit":
            print(f"Gracias por usar {aplication_name}")
            break
        
        elif command == "clean":
            os.system("cls" if os.name == "nt" else "clear" )
            
        elif command == "update":
            ev, events = select_event_by_index(workshop_planner, "Indice del evento a actualizar: ")
            if ev:
                print(f"Evento seleccionado: '{ev.event_title}'")
                new_status = input("Nuevo estado (pendiente/en progreso/completado) ").strip().lower()
                if workshop_planner.validate_status(new_status):
                    ev.event_metadata["status"] = new_status
                    print(f"Estado del evento '{ev.event_title}' actualizado a '{new_status}'")
                else:
                    print("Estado inválido.")
        else:
            print("Comando no reconocido.")
        

                            
def seed_domain(workshop_planner: Planner):
    #Plantilla por defecto creada para usar la app Ctrl + Alt + Repair
    
    #=== Tecnicos ===
    workshop_planner.add_resource(Resource("Jorge Alejandro Correa (Hardware Specialist)", {"type": "tech", "skills": ["Hardware Specialist"]}))
    workshop_planner.add_resource(Resource("Javier Correa (Software Specialist)", {"type": "tech", "skills": ["Software Specialist"]}))
    workshop_planner.add_resource(Resource("Karina Aschlie Diaz Hernandez 'mi novia XD' (Data Recovery Expert)", {"type": "tech", "skills": ["Data Recovery Expert"]}))
    workshop_planner.add_resource(Resource("Derek Velazquez Abad (Programador)", {"type": "tech", "skills": ["Programador"]}))
    
    #=== Estaciones ===
    workshop_planner.set_pool("Mesa de trabajo", 2)

    workshop_planner.add_resource(Resource("Mesa Compartida", {"type": "station"}))
    
    #=== Herramientas ===
    workshop_planner.add_resource(Resource("Estacion de Soldadura", {"type": "tool"}))
    workshop_planner.add_resource(Resource("Horno de Reflow", {"type": "tool"}))
    workshop_planner.add_resource(Resource("Kit Antiestatico", {"type": "tool"}))
    
    #=== Dispositivos unicos ===
    workshop_planner.add_resource(Resource("Banco de Pruebas Sensible", {"type": "device"}))
    workshop_planner.add_resource(Resource("PC cliente", {"type": "device"}))
    workshop_planner.add_resource(Resource("PC de desarrollo", {"type": "device"}))
    
    #=== Pools ===
    workshop_planner.set_pool("Duplicadora de Discos", 2)
    
    #Restricciones de este pool
    workshop_planner.add_corequisite("Horno de Reflow", "Hardware Specialist")
    workshop_planner.add_corequisite("Horno de Reflow", "Kit Antiestatico")
    workshop_planner.add_corequisite("Duplicadora de Discos", "Tecnico Data Recovery")
    
    workshop_planner.add_exclusion("Horno de Reflow", "Banco de Pruebas Sensible")
    workshop_planner.add_exclusion("Estacion de Soldadura", "Mesa Compartida")
    
    #--- Eventos automaticos ---
    ev1 = Event(
        "Reemplazo de pasta termica",
        "2025-12-09T09:00:00", 
        "2025-12-09T10:00:00",
        ["Mesa de trabajo", "Jorge Alejandro Correa (Hardware Specialist)", "Kit Antiestatico"],
        {"client": "Laura", "job_type": "Mantenimiento de Hardware", "notes": "Laptop con sobrecalentamiento"},
    )
    workshop_planner.schedule_event(ev1)
    
    ev2 = Event(
        "Reflow de GPU", 
        "2025-12-09T09:30:00",
        "2025-12-09T11:00:00",
        ["Mesa de trabajo", "Horno de Reflow", "Jorge Alejandro Correa (Hardware Specialist)", "Kit Antiestatico"],
        {"client": "Maria", "job_type": "Mantenimiento de Hardware"}
    )
    workshop_planner.schedule_event(ev2)
    
    ev3 = Event(
        "Clonacion de discos",
        "2025-12-09T10:00:00",
        "2025-12-09T12:00:00",
        ["Mesa de trabajo", "Duplicadora de Discos", "Karina Aschlie Diaz Hernandez 'mi novia XD' (Data Recovery Expert)"],
        {"client": "Carlos", "job_type": "Recuperacion de Datos", "notes": "Disco con sectores dañados"}
    )
    workshop_planner.schedule_event(ev3)
    
    #Evento semanal, el parametro count indica cuantas veces se lleva a cabo el evento
    #En este caso se repite 4 semanas seguidas (1 vez a la semana)
    ev4 = Event(
        "Mantenimiento preventivo semanal",
        "2025-12-15T09:00:00",
        "2025-12-15T10:00:00",
        ["Mesa Compartida", "Jorge Alejandro Correa (Hardware Specialist)"],
        {"client": "Empresa Haier", "job_type": "Mantenimiento Preventivo"},
        recurrence_pattern={"freq": "weekly", "count": 4}
    )
    workshop_planner.schedule_event(ev4)
    
    #Evento mensual, se repite 3 meses seguidos
    ev5 = Event(
        "Limpieza profunda mensual",
        "2025-12-20T14:00:00",
        "2025-12-20T16:00:00",
        ["Mesa de trabajo", "Jorge Alejandro Correa (Hardware Specialist)", "Kit Antiestatico"],
        {"client": "Empresa Mediatek", "job_type": "Limpieza Profunda", "notes": "Retirar polvo acumulado"},
        recurrence_pattern={"freq": "monthly", "count": 3}
    )
    workshop_planner.schedule_event(ev5)
    
    #Evento diario, se repite 5 dias seguidos a la misma hora
    ev6 = Event(
        "Chequeo antivirus",
        "2025-12-10T08:30:00",
        "2025-12-10T09:00:00",
        ["Mesa Compartida", "Javier Correa (Software Specialist)"],
        {"client": "Empresa Apple", "job_type": "Seguridad y Software"},
        recurrence_pattern={"freq": "daily", "count": 5}
    )
    workshop_planner.schedule_event(ev6)
    
    ev7 = Event(
        "Automatizacion de scripts internos",
        "2025-12-11T14:00:00",
        "2025-12-11T16:00:00",
        ["Derek Velazquez Abad (Programador)"],
        {"client": "Taller Interno", "job_type": "Automatizacion de Procesos", "notes": "Crear script para reportes automaticos"}
    )
    workshop_planner.schedule_event(ev7)