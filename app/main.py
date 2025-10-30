from fastapi import FastAPI
from .database import engine, Base
from .routers import empleados, proyectos, asignaciones

# Crea tablas (solo para demo práctica)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Sistema de Gestión de Proyectos", version="1.0.0")

app.include_router(empleados.router)
app.include_router(proyectos.router)
app.include_router(asignaciones.router)

@app.get("/", tags=["salud"])
def raiz():
    return {"ok": True, "servicio": "proyectos-api"}
