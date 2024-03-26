from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base

from os import environ as env


def _create_engine():
    user = env.get("DB_USER", "postgres")
    password = env.get("DB_PASSWORD", "postgres")
    host = env.get("DB_HOST", "localhost")
    port = env.get("DB_PORT", "5432")
    db_name = env.get("DB_NAME", "postgres")
    db_driver = env.get("DB_DRIVER", "postgresql")

    db_url = f"{db_driver}://{user}:{password}@{host}:{port}/{db_name}"

    if db_driver == "test":
        db_url = "sqlite:///:memory:"
        engine = create_engine(db_url, connect_args={"check_same_thread": False}, poolclass=StaticPool)
    else:
        engine = create_engine(db_url)

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    return engine, SessionLocal


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


engine, SessionLocal = _create_engine()
Base = declarative_base()
