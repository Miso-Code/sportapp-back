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

    db_url = env.get("DATABASE_URL", f"{db_driver}://{user}:{password}@{host}:{port}/{db_name}")

    try:
        if db_driver == "test":
            db_url = "sqlite:///:memory:"
            new_engine = create_engine(db_url, connect_args={"check_same_thread": False}, poolclass=StaticPool)
        else:
            new_engine = create_engine(db_url)

        new_session_local = sessionmaker(autocommit=False, autoflush=False, bind=new_engine)

        return new_engine, new_session_local
    except Exception as e:
        print(f"Error creating engine: {e}")
        raise e


def get_db():
    db = session_local()
    try:
        yield db
    finally:
        db.close()


engine, session_local = _create_engine()
base = declarative_base()
