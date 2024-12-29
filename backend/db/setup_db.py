import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def setup_database():
    """Set up the F1 database and tables"""
    
    # Database connection parameters
    params = {
        'dbname': 'postgres',  # Connect to default database first
        'user': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD', 'postgres'),
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': os.getenv('DB_PORT', '5432')
    }
    
    try:
        # Connect to default database
        conn = psycopg2.connect(**params)
        conn.autocommit = True
        cur = conn.cursor()
        
        # Create f1_db database if it doesn't exist
        cur.execute("SELECT 1 FROM pg_database WHERE datname = 'f1_db'")
        if not cur.fetchone():
            cur.execute('CREATE DATABASE f1_db')
        
        # Close connection to default database
        cur.close()
        conn.close()
        
        # Connect to f1_db
        params['dbname'] = 'f1_db'
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        
        # Read and execute schema.sql
        with open('backend/db/schema.sql', 'r') as f:
            cur.execute(f.read())
            
        # Commit changes and close connection
        conn.commit()
        print("Database setup completed successfully!")
        
    except Exception as e:
        print(f"Error setting up database: {str(e)}")
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    setup_database() 