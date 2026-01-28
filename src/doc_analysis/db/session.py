"""Database session management."""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from src.doc_analysis.config import settings
from src.doc_analysis.db.models import Base

_engine = None
_SessionLocal = None


def _get_engine():
    """Get or create engine lazily."""
    global _engine
    if _engine is None:
        _engine = create_engine(
            settings.database_url,
            pool_pre_ping=True,
            pool_recycle=3600,
            echo=settings.log_level == "DEBUG",
        )
    return _engine


def get_session_local():
    """Get or create sessionmaker lazily."""
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_get_engine())
    return _SessionLocal


# For backward compatibility
engine = property(_get_engine)
SessionLocal = property(get_session_local)


def get_db() -> Session:
    """Get database session."""
    Session = get_session_local()
    db = Session()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables if they don't exist."""
    # Skip in testing environment (SQLite in-memory)
    if "sqlite" in settings.database_url:
        return
    try:
        Base.metadata.create_all(bind=_get_engine(), checkfirst=True)
    except Exception:
        # Ignore errors
        pass
