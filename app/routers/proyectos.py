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
def listar(
    estado: models.EstadoProyecto | None = Query(default=None),
    presupuesto_min: float | None = Query(default=None),
    presupuesto_max: float | None = Query(default=None),
    db: Session = Depends(get_db)
):
    return crud.listar_proyectos(db, estado=estado,
                                 presupuesto_min=presupuesto_min,
                                 presupuesto_max=presupuesto_max)

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

@router.get("/{proyecto_id}/detalle", response_model=schemas.ProyectoDetalle)
def obtener_detalle(proyecto_id: int, db: Session = Depends(get_db)):
    pr, ger, emps = crud.detalle_proyecto(db, proyecto_id)
    return {"proyecto": pr, "gerente": ger, "empleados": emps}