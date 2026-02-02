# Ctrl + Alt + Repair – Workshop Planner

**Ctrl + Alt + Repair** es un planificador inteligente de eventos diseñado para gestionar un **taller de reparaciones de computadoras**.  
El sistema organiza trabajos que consumen recursos limitados (técnicos, estaciones, herramientas, dispositivos) evitando conflictos de tiempo y aplicando reglas de **restricciones personalizadas**.

Este proyecto fue desarrollado en **Python** y utiliza una **interfaz de línea de comandos (CLI)** para que el usuario pueda interactuar de forma sencilla y directa.

---

El objetivo principal es garantizar que:
1. **Los recursos no se asignen a más de un evento a la vez.**
2. **Se respeten las reglas de co-requisito y exclusión** definidas en el dominio.

Además, se incluyen funcionalidades avanzadas como:
- Eventos recurrentes (diarios, semanales, mensuales).
- Pools de recursos (ej. varias mesas de trabajo).
- Persistencia de datos en JSON.
- Búsqueda automática de huecos disponibles.
- Validación de catálogo de trabajos según skills, pools y dispositivos.

---

## Interfaz CLI
La aplicación se ejecuta en consola y ofrece una serie de comandos para gestionar el taller.  
Al iniciar (`python main.py`), verás un prompt donde puedes escribir los siguientes comandos:

### Lista de Comandos
- **help** : Muestra la lista de comandos disponibles y su descripción.  
- **list** : Lista todos los eventos programados.  
- **add** : Agrega un nuevo evento (con recurrencia opcional).  
- **remove** : Elimina un evento por índice.  
- **jobs** : Muestra el catálogo de trabajos disponibles en el taller.  
- **res** : Muestra la agenda de un recurso específico.  
- **slot** : Busca el próximo hueco disponible para un evento.  
- **addres** : Agrega un recurso con atributos (tipo, skills).  
- **addpool** : Configura un pool de recursos (ej. varias unidades de un mismo recurso).  
- **rules** : Muestra las restricciones actuales (co-requisitos, exclusiones, pools, catálogo).  
- **seed** : Carga el dominio base del taller Ctrl + Alt + Repair con recursos y eventos de ejemplo.  
- **save** : Guarda el estado actual en "data.json".  
- **load** : Carga el estado desde "data.json".  
- **clear** : Elimina toda la información (eventos, recursos, restricciones).  
- **clean** : Limpia la consola.  
- **quit** : Sale de la aplicación.  
- **update** : Actualiza el estado de un evento (pendiente, en progreso, completado).

---

## Dominio Escogido
El dominio elegido es un **taller de reparaciones de computadoras**, con el propósito de cumplir mi sueño algún día de tener un espacio propio para ayudar a otros con sus equipos y en agradecimiento a los técnicos cuyos nombres aparecen en este proyecto:

- Jorge Alejandro Correa 
- Javier Correa

Dos especialistas amigos míos 
Por ayudarme a conocer un poco más sobre el tema cada día, y por su enorme apoyo en este camino de aprendizaje y crecimiento. 

### Ejemplos de Eventos
- *Reflow de GPU*  
- *Clonación de discos*  
- *Chequeo antivirus*  
- *Mantenimiento preventivo semanal*  
- *Automatización de scripts internos*  
- *Limpieza profunda mensual*  
- *Reemplazo de pasta térmica*  

### Ejemplos de Recursos
- **Técnicos con skills:**  
  - *Hardware Specialist*  
  - *Software Specialist*  
  - *Data Recovery Expert*  
  - *Programador*  
- **Estaciones de trabajo:**  
  - Pool de mesas de trabajo (cantidad: 2)  
  - Mesa compartida  
- **Herramientas:**  
  - Estación de soldadura  
  - Horno de Reflow  
  - Kit Antiestático  
- **Dispositivos:**  
  - Banco de pruebas sensible  
  - PC cliente  
  - PC de desarrollo  

---

## ⚖️ Restricciones Implementadas
- **Co-requisito (Inclusión):**  
  - El *Horno de Reflow* requiere un técnico con skill *Hardware Specialist* y el *Kit Antiestático*.  
  - La *Duplicadora de Discos* requiere un técnico con skill *Data Recovery Expert*.  

- **Exclusión Mutua:**  
  - El *Horno de Reflow* no puede usarse junto con el *Banco de Pruebas Sensible*.  
  - La *Estación de Soldadura* no puede usarse junto con la *Mesa Compartida*.  

Estas reglas garantizan seguridad y coherencia en el uso de los recursos.

---

## Persistencia
El estado del taller (recursos, eventos, restricciones, pools) se guarda en un archivo JSON ("save/data.json").  
Esto permite cargar escenarios predefinidos o continuar donde se dejó la última sesión.

---

## Ejemplos de Uso

### 1. Cargar dominio base
> seed
Dominio base de Ctrl + Alt + Repair cargado.

### 2. Listar eventos
> list
0. Reemplazo de pasta térmica | 2025-12-09T09:00:00 => 2025-12-09T10:00:00 | Recursos: Mesa de trabajo, Jorge Alejandro Correa (Hardware Specialist), Kit Antiestático | Cliente: Laura | Estado: pendiente
1. Reflow de GPU | 2025-12-09T09:30:00 => 2025-12-09T11:00:00 | Recursos: Mesa de trabajo, Horno de Reflow, Jorge Alejandro Correa (Hardware Specialist), Kit Antiestático | Cliente: Maria | Estado: pendiente

### 3. Buscar hueco disponible
> slot
Titulo del evento base: Reflow de GPU
Buscar desde (YYYY-MM-DDTHH:MM:SS): 2025-12-09T12:00:00
Hueco: 2025-12-09T12:30:00 => 2025-12-09T14:00:00

### 4. Agregar recurso
bash
> addres
Nombre del recurso: Nuevo Técnico
Tipo (tech, station, tool, device): tech
Skills (opcional, coma): Hardware Specialist
Recurso agregado: Nuevo Técnico (tech)

### 5. Guardar y cargar estado
> save
Guardado en data.json

> load
Cargado data.json
