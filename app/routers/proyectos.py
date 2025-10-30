from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from ..database import SessionLocal
from .. import schemas, crud, models

router = APIRouter(prefix="/proyectos", tags=["proyectos"])

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

@router.post("", response_model=schemas.ProyectoSalida, status_code=status.HTTP_201_CREATED)
def crear(payload: schemas.ProyectoCrear, db: Session = Depends(get_db)):
    return crud.crear_proyecto(db, payload)

@router.get("", response_model=list[schemas.ProyectoSalida])
def listar(db: Session = Depends(get_db)):
    return crud.listar_proyectos(db)

@router.get("/{proyecto_id}", response_model=schemas.ProyectoSalida)
def obtener(proyecto_id: int, db: Session = Depends(get_db)):
    pr = db.get(models.Proyecto, proyecto_id)
    if not pr: raise HTTPException(404, "Proyecto no encontrado")
    return pr

@router.patch("/{proyecto_id}", response_model=schemas.ProyectoSalida)
def actualizar(proyecto_id: int, payload: schemas.ProyectoActualizar, db: Session = Depends(get_db)):
    return crud.actualizar_proyecto(db, proyecto_id, payload)

@router.delete("/{proyecto_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar(proyecto_id: int, db: Session = Depends(get_db)):
    crud.eliminar_proyecto(db, proyecto_id)
    return

@router.post("/{proyecto_id}/gerente/{empleado_id}", response_model=schemas.ProyectoSalida)
def fijar_gerente(proyecto_id: int, empleado_id: int, db: Session = Depends(get_db)):
    return crud.fijar_gerente(db, proyecto_id, empleado_id)

@router.delete("/{proyecto_id}/gerente", response_model=schemas.ProyectoSalida)
def quitar_gerente(proyecto_id: int, db: Session = Depends(get_db)):
    return crud.quitar_gerente(db, proyecto_id)

@router.get("/{proyecto_id}/empleados", response_model=schemas.EmpleadosDeProyecto)
def listar_empleados_de_proyecto(proyecto_id: int, db: Session = Depends(get_db)):
    pr, emps = crud.empleados_de_proyecto(db, proyecto_id)
    return {"proyecto": pr, "empleados": emps}
