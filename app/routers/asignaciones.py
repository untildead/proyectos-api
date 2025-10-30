from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from ..database import SessionLocal
from .. import schemas, crud

router = APIRouter(prefix="/asignaciones", tags=["asignaciones"])

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

@router.post("", response_model=schemas.AsignacionSalida, status_code=status.HTTP_201_CREATED)
def asignar(payload: schemas.AsignacionCrear, db: Session = Depends(get_db)):
    return crud.asignar_empleado(db, payload)

@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
def desasignar(payload: schemas.AsignacionCrear, db: Session = Depends(get_db)):
    crud.desasignar_empleado(db, payload)
    return
