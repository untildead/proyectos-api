from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

#SQLite Local
DATABASE_URL = "sqlite:///./proyectos.db"

class Base(DeclarativeBase):
    pass

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # necesario en SQLite con hilos
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
