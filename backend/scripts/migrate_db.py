"""Database migration script for staging/production environments."""
import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from app.database import Base
from app.models.user import User, QueryHistory  # Import all your models here

def migrate():
    """Run database migrations."""
    try:
        # Get database URL from environment
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            print("Error: DATABASE_URL environment variable not set")
            sys.exit(1)

        # Create database engine
        engine = create_engine(database_url)

        # Create all tables
        print("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        print("Database migration completed successfully!")

    except SQLAlchemyError as e:
        print(f"Database migration failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    migrate() 