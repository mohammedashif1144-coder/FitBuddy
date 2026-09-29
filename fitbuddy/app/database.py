from pathlib import Path
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from .config import BASE_DIR, get_settings

settings = get_settings()

# Resolve the default relative SQLite path against the project root.
database_url = settings.database_url
if database_url.startswith("sqlite:///./"):
    relative = database_url.replace("sqlite:///./", "", 1)
    db_path = BASE_DIR / relative
    db_path.parent.mkdir(parents=True, exist_ok=True)
    database_url = f"sqlite:///{db_path.as_posix()}"

connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}
engine = create_engine(database_url, connect_args=connect_args, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    from .models import Plan, User  # noqa: F401

    Base.metadata.create_all(bind=engine)
