"""Database session management."""
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import OperationalError, ProgrammingError

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
    """Initialize database tables and add missing columns if needed."""
    # Skip in testing environment (SQLite in-memory)
    if "sqlite" in settings.database_url:
        return

    engine = _get_engine()

    try:
        # First, create tables that don't exist
        Base.metadata.create_all(bind=engine, checkfirst=True)

        # Then, add missing columns to existing tables
        _add_missing_columns(engine)
    except Exception as e:
        # Log but don't fail on initialization errors
        print(f"Database initialization warning: {e}")


def _add_missing_columns(engine):
    """Add missing columns to existing tables."""
    inspector = inspect(engine)

    for table in Base.metadata.sorted_tables:
        table_name = table.name

        # Skip if table doesn't exist in database
        if table_name not in inspector.get_table_names():
            continue

        # Get existing columns in database
        existing_columns = {col['name'] for col in inspector.get_columns(table_name)}

        # Check for missing columns and add them
        with engine.connect() as conn:
            for column in table.columns:
                if column.name not in existing_columns:
                    # Build ALTER TABLE statement
                    column_type = column.type.compile(dialect=engine.dialect)
                    nullable = "NULL" if column.nullable else "NOT NULL"
                    default = f"DEFAULT {column.default.arg}" if column.default else ""
                    comment = f"COMMENT '{column.comment}'" if column.comment else ""

                    alter_sql = text(
                        f"ALTER TABLE {table_name} "
                        f"ADD COLUMN {column.name} {column_type} {nullable} {default} {comment}"
                    )

                    try:
                        conn.execute(alter_sql)
                        conn.commit()
                        print(f"Added missing column: {table_name}.{column.name}")
                    except (OperationalError, ProgrammingError) as e:
                        # Column might have been added concurrently, ignore
                        print(f"Column add warning: {table_name}.{column.name} - {e}")
