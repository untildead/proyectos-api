from sqlalchemy import Integer, String, Text, Enum, ForeignKey, UniqueConstraint, Float
# ...

class EstadoEmpleado(str, enum.Enum):
    activo = "activo"
    inactivo = "inactivo"

class Empleado(Base):
    __tablename__ = "empleados"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    cc: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    cargo: Mapped[str | None] = mapped_column(String(50), nullable=True)

    especialidad: Mapped[str | None] = mapped_column(String(80), nullable=True)
    salario: Mapped[float | None] = mapped_column(Float, nullable=True)
    estado_empleado: Mapped[EstadoEmpleado] = mapped_column(Enum(EstadoEmpleado), default=EstadoEmpleado.activo, nullable=False)

    asignaciones = relationship("Asignacion", back_populates="empleado", cascade="all, delete-orphan")
    proyectos_dirigidos = relationship("Proyecto", back_populates="gerente", cascade="all")

class Proyecto(Base):
    __tablename__ = "proyectos"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nombre: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)
    fecha_inicio: Mapped[str | None] = mapped_column(String(10), nullable=True)
    fecha_fin: Mapped[str | None] = mapped_column(String(10), nullable=True)
    estado: Mapped[EstadoProyecto] = mapped_column(Enum(EstadoProyecto), default=EstadoProyecto.planeado, nullable=False)

    presupuesto: Mapped[float | None] = mapped_column(Float, nullable=True)

    gerente_id: Mapped[int | None] = mapped_column(ForeignKey("empleados.id", ondelete="SET NULL"), nullable=True, index=True)
    gerente = relationship("Empleado", back_populates="proyectos_dirigidos")
    asignaciones = relationship("Asignacion", back_populates="proyecto", cascade="all, delete-orphan")
