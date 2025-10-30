from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./proyectos.db"
    class Config:
        env_file = ".env"

settings = Settings()

class Base(DeclarativeBase):
    pass

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def _sqlite_table_exists(conn, table: str) -> bool:
    return bool(
        conn.exec_driver_sql(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=:t",
            {"t": table},
        ).first()
    )


def _sqlite_has_column(conn, table: str, column: str) -> bool:
    rows = conn.exec_driver_sql(f"PRAGMA table_info({table})").all()
    return any(r[1] == column for r in rows)


def ensure_sqlite_schema():
    """
    Pequeña migración en caliente para SQLite.
    - Añade empleados.estado (Enum como VARCHAR) si falta.
    - Añade proyectos.presupuesto (INTEGER) si falta.

    Nota: Sólo aplica cuando DATABASE_URL es SQLite.
    """
    if not settings.DATABASE_URL.startswith("sqlite"):
        return
    # Usar transacción que hace commit automáticamente
    with engine.begin() as conn:
        # empleados.estado
        if _sqlite_table_exists(conn, "empleados") and not _sqlite_has_column(conn, "empleados", "estado"):
            conn.exec_driver_sql("ALTER TABLE empleados ADD COLUMN estado VARCHAR(8) NOT NULL DEFAULT 'activo'")
        # proyectos.presupuesto
        if _sqlite_table_exists(conn, "proyectos") and not _sqlite_has_column(conn, "proyectos", "presupuesto"):
            conn.exec_driver_sql("ALTER TABLE proyectos ADD COLUMN presupuesto INTEGER")
