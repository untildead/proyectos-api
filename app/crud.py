from sqlalchemy.orm import Session
from sqlalchemy import select, func
from fastapi import HTTPException
from . import models, schemas

MAX_PROYECTOS_POR_EMPLEADO = 5

# ---------- Empleados ----------
def crear_empleado(db: Session, datos: schemas.EmpleadoCrear) -> models.Empleado:
    existe = db.scalar(select(models.Empleado).where(models.Empleado.cc == datos.cc))
    if existe:
        raise HTTPException(status_code=400, detail="La cédula (cc) ya existe")
    emp = models.Empleado(cc=datos.cc, nombre=datos.nombre, cargo=datos.cargo)
    db.add(emp); db.commit(); db.refresh(emp)
    return emp

def listar_empleados(db: Session, especialidad: str | None = None, estado_empleado: models.EstadoEmpleado | None = None):
    """
    Lista empleados con filtros opcionales. El filtro por "especialidad" se
    ignora (no existe en el modelo). El filtro de estado usa la columna
    real "estado" del modelo.
    """
    query = select(models.Empleado)
    if estado_empleado:
        query = query.where(models.Empleado.estado == estado_empleado)
    return db.scalars(query.order_by(models.Empleado.id)).all()

def obtener_empleado(db: Session, empleado_id: int):
    emp = db.get(models.Empleado, empleado_id)
    if not emp:
        raise HTTPException(404, "Empleado no encontrado")
    return emp

def actualizar_empleado(db: Session, empleado_id: int, datos: schemas.EmpleadoActualizar):
    emp = obtener_empleado(db, empleado_id)
    payload = datos.model_dump(exclude_unset=True)
    # Mapear estado_empleado -> estado y descartar campos no existentes
    estado_val = payload.get("estado_empleado", None)
    if estado_val is not None:
        payload["estado"] = models.EstadoEmpleado(estado_val)
    # Aplicar solo campos soportados por el modelo
    for k in ("nombre", "cargo", "estado"):
        if k in payload and payload[k] is not None:
            setattr(emp, k, payload[k])
    db.commit(); db.refresh(emp)
    return emp

def eliminar_empleado(db: Session, empleado_id: int):
    emp = obtener_empleado(db, empleado_id)
    dirige = db.scalar(select(func.count(models.Proyecto.id)).where(models.Proyecto.gerente_id == emp.id))
    if dirige:
        raise HTTPException(409, "No se puede eliminar: es gerente de algún proyecto")
    db.delete(emp); db.commit()

# ---------- Proyectos ----------
def crear_proyecto(db: Session, datos: schemas.ProyectoCrear) -> models.Proyecto:
    if datos.gerente_id is not None and not db.get(models.Empleado, datos.gerente_id):
        raise HTTPException(404, "Gerente no existe")
    pr = models.Proyecto(
        nombre=datos.nombre,
        descripcion=datos.descripcion,
        estado=models.EstadoProyecto(datos.estado),
        gerente_id=datos.gerente_id,
        presupuesto=(int(datos.presupuesto) if getattr(datos, "presupuesto", None) is not None else None),
    )
    db.add(pr); db.commit(); db.refresh(pr)
    return pr

def actualizar_proyecto(db: Session, proyecto_id: int, datos: schemas.ProyectoActualizar):
    pr = db.get(models.Proyecto, proyecto_id)
    if not pr: raise HTTPException(404, "Proyecto no encontrado")
    payload = datos.model_dump(exclude_unset=True)
    if "estado" in payload and payload["estado"] is not None:
        payload["estado"] = models.EstadoProyecto(payload["estado"])
    if "gerente_id" in payload and payload["gerente_id"] is not None:
        if not db.get(models.Empleado, payload["gerente_id"]):
            raise HTTPException(404, "Gerente no existe")
        # Si el nuevo gerente estaba asignado como empleado, quitar esa asignación
        db.query(models.Asignacion).filter(
            models.Asignacion.proyecto_id == proyecto_id,
            models.Asignacion.empleado_id == payload["gerente_id"]
        ).delete(synchronize_session=False)
    # Ajustar tipos y descartar campos no existentes
    if "presupuesto" in payload and payload["presupuesto"] is not None:
        payload["presupuesto"] = int(payload["presupuesto"])
    for k in ("nombre", "descripcion", "estado", "gerente_id", "presupuesto"):
        if k in payload:
            setattr(pr, k, payload[k])
    db.commit(); db.refresh(pr)
    return pr

def eliminar_proyecto(db: Session, proyecto_id: int):
    pr = db.get(models.Proyecto, proyecto_id)
    if not pr: raise HTTPException(404, "Proyecto no encontrado")
    db.delete(pr); db.commit()

def listar_proyectos(db: Session, estado: models.EstadoProyecto | None = None,
                     presupuesto_min: float | None = None, presupuesto_max: float | None = None):
    """
    Lista proyectos con filtros opcionales por estado y rango de presupuesto.
    """
    query = select(models.Proyecto)
    if estado:
        query = query.where(models.Proyecto.estado == estado)
    if presupuesto_min is not None:
        query = query.where(models.Proyecto.presupuesto >= presupuesto_min)
    if presupuesto_max is not None:
        query = query.where(models.Proyecto.presupuesto <= presupuesto_max)
    return db.scalars(query.order_by(models.Proyecto.id)).all()

def detalle_proyecto(db: Session, proyecto_id: int):
    """
    Devuelve proyecto + gerente + empleados asignados (consulta relacional).
    """
    pr = db.get(models.Proyecto, proyecto_id)
    if not pr:
        raise HTTPException(404, "Proyecto no encontrado")
    emps = db.scalars(
        select(models.Empleado).join(models.Asignacion, models.Asignacion.empleado_id == models.Empleado.id
        ).where(models.Asignacion.proyecto_id == proyecto_id)
    ).all()
    ger = db.get(models.Empleado, pr.gerente_id) if pr.gerente_id else None
    return pr, ger, emps

# ---------- Asignaciones (N:M) ----------
def _cuenta_asignaciones(db: Session, empleado_id: int) -> int:
    return db.scalar(select(func.count(models.Asignacion.id)).where(models.Asignacion.empleado_id == empleado_id)) or 0

def asignar_empleado(db: Session, datos: schemas.AsignacionCrear) -> models.Asignacion:
    emp = db.get(models.Empleado, datos.empleado_id)
    pr = db.get(models.Proyecto, datos.proyecto_id)
    if not emp or not pr:
        raise HTTPException(404, "Empleado o proyecto inexistente")

    # No duplicado N:M
    ya = db.scalar(select(models.Asignacion).where(
        models.Asignacion.empleado_id == emp.id,
        models.Asignacion.proyecto_id == pr.id
    ))
    if ya: raise HTTPException(409, "Empleado ya está asignado a este proyecto")

    # Máximo 5 proyectos por empleado
    if _cuenta_asignaciones(db, emp.id) >= MAX_PROYECTOS_POR_EMPLEADO:
        raise HTTPException(409, "Empleado ya tiene el máximo de 5 proyectos")

    # Gerente no puede estar asignado como empleado del mismo proyecto
    if pr.gerente_id == emp.id:
        raise HTTPException(409, "El gerente del proyecto no puede asignarse como empleado")

    asg = models.Asignacion(empleado_id=emp.id, proyecto_id=pr.id)
    db.add(asg); db.commit(); db.refresh(asg)
    return asg

def desasignar_empleado(db: Session, datos: schemas.AsignacionCrear):
    filas = db.query(models.Asignacion).filter(
        models.Asignacion.empleado_id == datos.empleado_id,
        models.Asignacion.proyecto_id == datos.proyecto_id
    ).delete(synchronize_session=False)
    if not filas: raise HTTPException(404, "Asignación no encontrada")
    db.commit()

def fijar_gerente(db: Session, proyecto_id: int, empleado_id: int):
    pr = db.get(models.Proyecto, proyecto_id)
    emp = db.get(models.Empleado, empleado_id)
    if not pr or not emp:
        raise HTTPException(404, "Proyecto o empleado no existe")

    # Si estaba asignado como empleado, quitarlo
    db.query(models.Asignacion).filter(
        models.Asignacion.proyecto_id == proyecto_id,
        models.Asignacion.empleado_id == empleado_id
    ).delete(synchronize_session=False)

    pr.gerente_id = empleado_id
    db.commit(); db.refresh(pr)
    return pr

def quitar_gerente(db: Session, proyecto_id: int):
    pr = db.get(models.Proyecto, proyecto_id)
    if not pr: raise HTTPException(404, "Proyecto no existe")
    pr.gerente_id = None
    db.commit(); db.refresh(pr)
    return pr

def empleados_sin_proyecto(db: Session):
    sub = select(models.Asignacion.empleado_id).distinct()
    return db.scalars(select(models.Empleado).where(models.Empleado.id.not_in(sub)).order_by(models.Empleado.id)).all()

def empleados_con_proyecto(db: Session):
    sub = select(models.Asignacion.empleado_id).distinct()
    return db.scalars(select(models.Empleado).where(models.Empleado.id.in_(sub)).order_by(models.Empleado.id)).all()

def proyectos_de_empleado(db: Session, empleado_id: int):
    emp = obtener_empleado(db, empleado_id)
    proys = db.scalars(
        select(models.Proyecto).join(models.Asignacion, models.Asignacion.proyecto_id == models.Proyecto.id
        ).where(models.Asignacion.empleado_id == empleado_id)
    ).all()
    return emp, proys

def empleados_de_proyecto(db: Session, proyecto_id: int):
    pr = db.get(models.Proyecto, proyecto_id)
    if not pr: raise HTTPException(404, "Proyecto no encontrado")
    emps = db.scalars(
        select(models.Empleado).join(models.Asignacion, models.Asignacion.empleado_id == models.Empleado.id
        ).where(models.Asignacion.proyecto_id == proyecto_id)
    ).all()
    return pr, emps
