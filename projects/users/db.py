from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from os import environ as env


# Base de datos principal (Todos los experimentos)
def _create_engine():
    user = env.get("DB_USER", "postgres")
    password = env.get("DB_PASSWORD", "postgres")
    host = env.get("DB_HOST", "localhost")
    port = env.get("DB_PORT", "5432")
    db_name = env.get("DB_NAME", "postgres")
    db_driver = env.get("DB_DRIVER", "postgresql+psycopg2")

    db_url = env.get("DB_URL", f"{db_driver}://{user}:{password}@{host}:{port}/{db_name}")

    engine = create_engine(db_url, pool_pre_ping=True, pool_size=10, max_overflow=0, pool_recycle=3600)

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    return engine, SessionLocal


# Base de datos local para sincronización vertical (Experimento 2)
def _create_local_engine():
    db_url = "sqlite:///./local.db"
    engine = create_engine(db_url)

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    return engine, SessionLocal


Base = declarative_base()

# Experimento 2, usar base de datos local para fastapi y sincronización vertical con base de datos principal
# engine, SessionLocal = _create_local_engine()

# Experimentos 1 y 2 Base de datos principal
engine, SessionLocal = _create_engine()
Base.metadata.create_all(bind=engine)
