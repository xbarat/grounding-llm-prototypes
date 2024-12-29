import asyncio
import pandas as pd
import psycopg2
from psycopg2.extras import RealDictCursor
from query.processor import QueryProcessor
from engine.analysis import AnalysisEngine

async def process_f1_query(query: str):
    """Process an F1 query through the entire pipeline"""
    
    # Initialize components
    processor = QueryProcessor()
    engine = AnalysisEngine()
    
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(
            dbname="f1_db",
            user="postgres",
            password="postgres",
            host="localhost",
            port="5432",
            cursor_factory=RealDictCursor
        )
        
        # Process query to get data requirements
        print(f"\nProcessing query: {query}")
        
        # For qualifying comparison query, fetch qualifying data
        if "qualifying" in query.lower():
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT 
                        d.forename || ' ' || d.surname as driver_name,
                        q.position,
                        q.q1_time as q1,
                        q.q2_time as q2,
                        q.q3_time as q3,
                        r.year,
                        r.round,
                        c.circuit_name
                    FROM qualifying q
                    JOIN races r ON q.race_id = r.race_id
                    JOIN circuits c ON r.circuit_id = c.circuit_id
                    JOIN drivers d ON q.driver_id = d.driver_id
                    WHERE r.year = 2023 AND c.circuit_name = 'Monaco'
                    ORDER BY q.position;
                """)
                rows = cur.fetchall()
                df = pd.DataFrame(rows)
                
                # Debug output
                print("\nDataFrame contents:")
                print(df)
                print("\nDataFrame info:")
                print(df.info())
            
        else:
            raise Exception("Only qualifying queries are supported at the moment")
            
        print("\nData fetched successfully")
        print("DataFrame shape:", df.shape)
        
        # Generate and execute analysis
        analysis_result = await engine.analyze(df, query)
        print("\nAnalysis Result:")
        print(analysis_result)
        
    except Exception as e:
        print(f"Error processing query: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()

async def main():
    # Test qualifying comparison query
    query = "Compare qualifying times between Verstappen and Hamilton at Monaco 2023"
    await process_f1_query(query)

if __name__ == "__main__":
    asyncio.run(main()) 