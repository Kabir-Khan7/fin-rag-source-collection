"""
Database session management.

Provides the SessionLocal factory for creating database sessions and
the get_db dependency used by FastAPI to inject sessions into endpoints.
"""

from collections.abc import Generator

from sqlalchemy.orm import Session, sessionmaker

from app.database.engine import engine

# SessionLocal is a factory that produces new Session objects.
# Each request will use its own session created by this factory.
SessionLocal = sessionmaker(
    bind=engine,          # Bind sessions to our engine
    autoflush=False,      # Don't auto-send pending changes before queries (explicit control)
    autocommit=False,     # Require explicit commits (safer, standard practice)
    expire_on_commit=False,  # Keep object data usable after commit
)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that provides a database session.

    Creates a new session for each request, yields it to the endpoint,
    and guarantees the session is closed afterward — even if an error
    occurs. This prevents connection leaks.

    Yields:
        Session: An active SQLAlchemy database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()