"""
Database Initialization Script

This script creates all database tables based on our SQLAlchemy models.

What it does:
1. Imports all models (Transaction, Document, Party, Task)
2. Creates tables in the database if they don't exist
3. Reports success/failure

Usage:
    python scripts/init_db.py

After running this, you'll have an empty database with all tables ready.
"""

import sys
import os

# Add parent directory to path so we can import backend modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.database import Base, engine
from backend.models import Transaction, Document, Party, Task

def init_database():
    """
    Create all database tables.

    This uses SQLAlchemy's create_all() method which:
    - Reads the model definitions
    - Generates CREATE TABLE statements
    - Executes them on the database
    - Skips tables that already exist (safe to run multiple times)
    """
    print("=" * 60)
    print("INITIALIZING DATABASE")
    print("=" * 60)

    # Show what database we're connecting to
    print(f"\nDatabase URL: {engine.url}")
    print(f"Database Type: {'SQLite' if 'sqlite' in str(engine.url) else 'PostgreSQL'}")

    print("\nCreating tables...")
    print("  - transactions")
    print("  - documents")
    print("  - parties")
    print("  - tasks")

    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)

        print("\n" + "=" * 60)
        print("SUCCESS: Database tables created successfully!")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Run 'python scripts/seed_data.py' to populate with sample data")
        print("2. Start the API server with 'uvicorn backend.main:app --reload'")
        print("\n")

    except Exception as e:
        print("\n" + "=" * 60)
        print("ERROR: Failed to create database tables")
        print("=" * 60)
        print(f"\nError details: {str(e)}")
        print("\nTroubleshooting:")
        print("- Check that database.py has correct DATABASE_URL")
        print("- Ensure you have write permissions in the project directory")
        print("- Verify all models are properly defined")
        sys.exit(1)


if __name__ == "__main__":
    init_database()
