import enum
from sqlalchemy import Integer, String, Text, Enum, ForeignKey, UniqueConstraint, Float
from sqlalchemy.orm import relationship, Mapped, mapped_column
from .database import Base


class EstadoEmpleado(str, enum.Enum):
    activo = "activo"
    inactivo = "inactivo"

class EstadoProyecto(str, enum.Enum):
    planeado = "planeado"
    en_curso = "en_curso"
    en_pausa = "en_pausa"
    terminado = "terminado"
    cancelado = "cancelado"

class Empleado(Base):
    __tablename__ = "empleados"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    cc: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    cargo: Mapped[str | None] = mapped_column(String(50), nullable=True)
    estado: Mapped[EstadoEmpleado] = mapped_column(Enum(EstadoEmpleado), default=EstadoEmpleado.activo, nullable=False)

    asignaciones = relationship("Asignacion", back_populates="empleado", cascade="all, delete-orphan")
    proyectos_dirigidos = relationship("Proyecto", back_populates="gerente", cascade="all")

    # Compatibilidad con esquemas: exponer estado_empleado como alias de 'estado'
    @property
    def estado_empleado(self) -> EstadoEmpleado:
        return self.estado

    @estado_empleado.setter
    def estado_empleado(self, value: EstadoEmpleado | str | None) -> None:
        if value is None:
            return
        self.estado = EstadoEmpleado(value) if isinstance(value, str) else value

class Proyecto(Base):
    __tablename__ = "proyectos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nombre: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)
    presupuesto: Mapped[int | None] = mapped_column(Integer, nullable=True)
    estado: Mapped[EstadoProyecto] = mapped_column(
        Enum(EstadoProyecto),
        default=EstadoProyecto.planeado,
        nullable=False
    )

    gerente_id: Mapped[int | None] = mapped_column(ForeignKey("empleados.id", ondelete="SET NULL"), nullable=True, index=True)
    gerente = relationship("Empleado", back_populates="proyectos_dirigidos")

    asignaciones = relationship("Asignacion", back_populates="proyecto", cascade="all, delete-orphan")

class Asignacion(Base):
    __tablename__ = "asignaciones"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    empleado_id: Mapped[int] = mapped_column(ForeignKey("empleados.id", ondelete="CASCADE"), index=True)
    proyecto_id: Mapped[int] = mapped_column(ForeignKey("proyectos.id", ondelete="CASCADE"), index=True)

    empleado = relationship("Empleado", back_populates="asignaciones")
    proyecto = relationship("Proyecto", back_populates="asignaciones")

    __table_args__ = (
        UniqueConstraint("empleado_id", "proyecto_id", name="uq_empleado_proyecto"),
    )
