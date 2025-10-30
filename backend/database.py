"""
Database Configuration Module

This module handles database connection setup and session management.
It's designed to work with both SQLite (development) and PostgreSQL (production)
by simply changing the DATABASE_URL environment variable.

Key Concepts:
- Engine: The connection to the database
- SessionLocal: Factory for creating database sessions (like opening a connection)
- Base: Base class that all our models inherit from
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Database URL - can be changed via environment variable
# SQLite (current): "sqlite:///./real_estate_closing.db"
# PostgreSQL (future): "postgresql://user:password@localhost/closing_platform"
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./real_estate_closing.db")

# Create database engine
# check_same_thread=False is SQLite-specific, allows multiple threads
# When we switch to PostgreSQL, this parameter is ignored (doesn't cause issues)
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

# SessionLocal is a factory for creating database sessions
# A session is like a "workspace" for database operations
# You open it, do your work, then close it
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all our database models
# All table classes (Transaction, Document, etc.) will inherit from this
Base = declarative_base()


def get_db():
    """
    Dependency function that provides database sessions to API endpoints.

    This is a generator function that:
    1. Creates a new database session
    2. Yields it to the caller (API endpoint)
    3. Closes it automatically when done (even if errors occur)

    Usage in FastAPI:
        @app.get("/transactions")
        def get_transactions(db: Session = Depends(get_db)):
            return db.query(Transaction).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
