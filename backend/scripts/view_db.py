from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
sys.path.append('.')  # Add current directory to path

from app.models.user import User, QueryHistory
from app.database import SQLALCHEMY_DATABASE_URL

def view_database():
    """View all users and their query history"""
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    print("\n=== Users ===")
    users = db.query(User).all()
    for user in users:
        print(f"\nUsername: {user.username}")
        print(f"Email: {user.email}")
        print(f"Created: {user.created_at}")
        print(f"Last Login: {user.last_login}")
        
        # Get user's queries
        queries = db.query(QueryHistory).filter(
            QueryHistory.user_id == user.id,
            QueryHistory.parent_id.is_(None)  # Only root queries
        ).all()
        
        if queries:
            print(f"\nQueries ({len(queries)}):")
            for query in queries:
                print(f"- {query.query} (ID: {query.id}, Created: {query.created_at})")
                # Show follow-ups if any
                for followup in query.follow_ups:
                    print(f"  └─ {followup.query} (ID: {followup.id})")
        else:
            print("\nNo queries found")
    
    if not users:
        print("No users found in database")

if __name__ == "__main__":
    view_database() 