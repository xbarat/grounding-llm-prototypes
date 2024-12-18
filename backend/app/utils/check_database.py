import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_database():
    try:
        # Get database URL from environment variable
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            print("Error: DATABASE_URL not found in environment variables")
            return

        conn = psycopg2.connect(database_url)
        cur = conn.cursor()
        
        # Check if table exists
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'typing_stats'
            );
        """)
        table_exists = cur.fetchone()[0]
        
        if not table_exists:
            print("Table 'typing_stats' does not exist yet")
            return

        cur.execute("SELECT COUNT(*) FROM typing_stats")
        count = cur.fetchone()[0]
        print(f"Number of records in database: {count}")
        
        # Show some sample data if available
        if count > 0:
            cur.execute("SELECT player_id, speed, accuracy FROM typing_stats LIMIT 5")
            samples = cur.fetchall()
            print("\nSample records:")
            for sample in samples:
                print(f"Player: {sample[0]}, Speed: {sample[1]}, Accuracy: {sample[2]}")

    except psycopg2.OperationalError as e:
        print(f"Database connection error: {str(e)}")
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    check_database()
