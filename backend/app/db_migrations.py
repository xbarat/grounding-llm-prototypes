from sqlalchemy import create_engine, text
from app.database import SQLALCHEMY_DATABASE_URL
from app.models.user import Base

def run_migrations():
    """Run database migrations"""
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
    
    # Drop existing tables if they exist
    Base.metadata.drop_all(bind=engine)
    
    # Create tables with updated schema
    Base.metadata.create_all(bind=engine)
    
    # Create indexes
    with engine.connect() as conn:
        # Index for query_history lookups
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_query_history_user_id 
            ON query_history (user_id)
        """))
        
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_query_history_parent_id 
            ON query_history (parent_id)
        """))
        
        # Index for user lookups
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_users_username 
            ON users (username)
        """))
        
        conn.commit()

if __name__ == "__main__":
    print("Running database migrations...")
    run_migrations()
    print("Database migrations completed successfully!") 