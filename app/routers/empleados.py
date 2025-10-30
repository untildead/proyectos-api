from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from ..database import SessionLocal
from .. import schemas, crud

router = APIRouter(prefix="/empleados", tags=["empleados"])

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

@router.post("", response_model=schemas.EmpleadoSalida, status_code=status.HTTP_201_CREATED)
def crear(payload: schemas.EmpleadoCrear, db: Session = Depends(get_db)):
    return crud.crear_empleado(db, payload)

@router.get("", response_model=list[schemas.EmpleadoSalida])
def listar(db: Session = Depends(get_db)):
    return crud.listar_empleados(db)

@router.get("/{empleado_id}", response_model=schemas.EmpleadoSalida)
def obtener(empleado_id: int, db: Session = Depends(get_db)):
    return crud.obtener_empleado(db, empleado_id)

@router.patch("/{empleado_id}", response_model=schemas.EmpleadoSalida)
def actualizar(empleado_id: int, payload: schemas.EmpleadoActualizar, db: Session = Depends(get_db)):
    return crud.actualizar_empleado(db, empleado_id, payload)

@router.delete("/{empleado_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar(empleado_id: int, db: Session = Depends(get_db)):
    crud.eliminar_empleado(db, empleado_id)
    return

@router.get("/_sin_proyecto", response_model=list[schemas.EmpleadoSalida])
def sin_proyecto(db: Session = Depends(get_db)):
    return crud.empleados_sin_proyecto(db)

@router.get("/_con_proyecto", response_model=list[schemas.EmpleadoSalida])
def con_proyecto(db: Session = Depends(get_db)):
    return crud.empleados_con_proyecto(db)

@router.get("/{empleado_id}/proyectos", response_model=schemas.ProyectosDeEmpleado)
def listar_proyectos_de_empleado(empleado_id: int, db: Session = Depends(get_db)):
    emp, proys = crud.proyectos_de_empleado(db, empleado_id)
    return {"empleado": emp, "proyectos": proys}
