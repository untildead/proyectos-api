from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from enum import Enum

class EstadoProyecto(str, Enum):
    planeado = "planeado"
    en_curso = "en_curso"
    en_pausa = "en_pausa"
    terminado = "terminado"
    cancelado = "cancelado"

# ---- Empleado
class EmpleadoBase(BaseModel):
    cc: str = Field(..., min_length=5, max_length=20)
    nombre: str = Field(..., min_length=2, max_length=100)
    cargo: Optional[str] = Field(None, max_length=50)

class EmpleadoCrear(EmpleadoBase): pass

class EmpleadoActualizar(BaseModel):
    nombre: Optional[str] = Field(None, min_length=2, max_length=100)
    cargo: Optional[str] = Field(None, max_length=50)

class EmpleadoSalida(EmpleadoBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

# ---- Proyecto
class ProyectoBase(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=120)
    descripcion: Optional[str] = None
    fecha_inicio: Optional[str] = None
    fecha_fin: Optional[str] = None
    estado: EstadoProyecto = EstadoProyecto.planeado

class ProyectoCrear(ProyectoBase):
    gerente_id: Optional[int] = None

class ProyectoActualizar(BaseModel):
    nombre: Optional[str] = Field(None, min_length=2, max_length=120)
    descripcion: Optional[str] = None
    fecha_inicio: Optional[str] = None
    fecha_fin: Optional[str] = None
    estado: Optional[EstadoProyecto] = None
    gerente_id: Optional[int] = None

class ProyectoSalida(ProyectoBase):
    id: int
    gerente_id: Optional[int] = None
    model_config = ConfigDict(from_attributes=True)

# ---- Asignación (N:M)
class AsignacionCrear(BaseModel):
    empleado_id: int
    proyecto_id: int

class AsignacionSalida(BaseModel):
    id: int
    empleado_id: int
    proyecto_id: int
    model_config = ConfigDict(from_attributes=True)

class ProyectosDeEmpleado(BaseModel):
    empleado: EmpleadoSalida
    proyectos: List[ProyectoSalida]

class EmpleadosDeProyecto(BaseModel):
    proyecto: ProyectoSalida
    empleados: List[EmpleadoSalida]
