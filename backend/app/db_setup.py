from app.database import engine, Base
from app.models.user import User, QueryHistory

def setup_database():
    """Create all database tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

if __name__ == "__main__":
    setup_database() 