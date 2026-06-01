"""
Database Configuration
SQLAlchemy session management and database connection
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
import os
from dotenv import load_dotenv
from models import Base
from db_url import resolve_database_url

load_dotenv()

# ============================================================================
# DATABASE CONFIGURATION
# ============================================================================

# Database URL from Railway/PostgreSQL environment variables or local default.
DATABASE_URL = resolve_database_url()

def _engine_options(database_url: str):
    """Return engine options compatible with the selected database backend."""
    if database_url.startswith("sqlite"):
        return {
            "echo": False,
            "connect_args": {"check_same_thread": False}
        }

    return {
        "echo": False,
        "pool_size": int(os.getenv("DB_POOL_SIZE", 10)),
        "max_overflow": int(os.getenv("DB_MAX_OVERFLOW", 20)),
        "pool_pre_ping": True,
        "pool_recycle": int(os.getenv("DB_POOL_RECYCLE", 3600)),
    }


# Create engine with backend-appropriate options.
engine = create_engine(DATABASE_URL, **_engine_options(DATABASE_URL))

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False
)

# ============================================================================
# SESSION MANAGEMENT
# ============================================================================

def get_db() -> Session:
    """
    Dependency for FastAPI/Flask to get database session
    
    Usage (Flask):
        from database import get_db
        
        @app.route('/users')
        def get_users():
            db = next(get_db())
            users = db.query(User).all()
            return users
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context():
    """
    Context manager for database session
    
    Usage:
        from database import get_db_context
        
        with get_db_context() as db:
            user = db.query(User).filter_by(email='test@example.com').first()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db(quiet=False):
    """
    Initialize database by creating all tables
    
    Usage:
        from database import init_db
        init_db()
    """
    from models import Base
    Base.metadata.create_all(bind=engine)
    if not quiet:
        print("Database initialized successfully")


def test_connection():
    """
    Test database connection
    
    Usage:
        from database import test_connection
        test_connection()
    """
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
            print("Database connection successful")
            return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False


# ============================================================================
# MIGRATION HELPERS
# ============================================================================

def get_db_url():
    """Get database URL (safe for logging)"""
    return DATABASE_URL.split('@')[-1] if '@' in DATABASE_URL else DATABASE_URL


def print_db_config():
    """Print database configuration (safe)"""
    print("=" * 60)
    print("Database Configuration")
    print("=" * 60)
    print(f"Database URL: ...@{get_db_url()}")
    if not DATABASE_URL.startswith("sqlite"):
        print(f"Pool Size: {os.getenv('DB_POOL_SIZE', 10)}")
        print(f"Max Overflow: {os.getenv('DB_MAX_OVERFLOW', 20)}")
    print("=" * 60)
