from sqlalchemy.engine import Engine

from app import models  # noqa: F401
from app.database import Base, engine

_ = models


def initialize_database(database_engine: Engine | None = None) -> None:
    """Create the application's tables when explicitly requested."""
    bind = database_engine if database_engine is not None else engine
    Base.metadata.create_all(bind=bind)
