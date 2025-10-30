# Sistema de Gestión de Proyectos (FastAPI)

API REST académica para gestionar **empleados**, **proyectos** y la **asignación (N:M)** entre ellos.  
Incluye reglas de negocio pedidas en el enunciado:

- Un empleado **no puede tener más de 5 proyectos** asignados.
- Un empleado **no puede estar asignado 2 veces** al mismo proyecto.
- El **gerente** de un proyecto **no puede** estar asignado como empleado en ese mismo proyecto.
- No se puede **eliminar un empleado** que sea **gerente** de algún proyecto.
- Al eliminar un **proyecto** se eliminan también sus **asignaciones** (cascade).

---

## Tecnologías

- Python 3.11+ (recomendado)
- FastAPI
- Uvicorn (servidor ASGI)
- SQLAlchemy 2.x
- SQLite (archivo local `proyectos.db`)
- Pydantic v2

---

## Requisitos

Instalar dependencias:

```bash
pip install -r requirements.txt
