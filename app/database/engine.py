"""
Database engine configuration.

Creates the SQLAlchemy Engine — the central interface to the MS SQL
Server database. The engine manages the connection pool and is created
once at application startup.
"""

import logging

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from app.core.config import settings

logger = logging.getLogger(__name__)


def create_db_engine() -> Engine:
    """
    Create and configure the SQLAlchemy database engine.

    The engine manages a pool of reusable connections to MS SQL Server.
    Connection pooling avoids the overhead of opening a new connection
    for every request.

    Returns:
        Engine: A configured SQLAlchemy engine instance.
    """
    engine = create_engine(
        settings.database_url,
        # Pool settings — tuned for a local development backend
        pool_size=5,            # Number of connections kept open in the pool
        max_overflow=10,        # Extra connections allowed beyond pool_size under load
        pool_pre_ping=True,     # Test a connection is alive before using it (avoids stale connections)
        pool_recycle=3600,      # Recycle connections after 1 hour (prevents timeouts)
        echo=settings.DEBUG,    # Log all SQL statements when DEBUG=True (great for learning)
    )
    logger.info("Database engine created for %s", settings.DB_NAME)
    return engine


# Create the engine once at import time — shared across the whole app
engine = create_db_engine()