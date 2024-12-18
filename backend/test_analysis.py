import pandas as pd
from app.utils.code_utils import generate_code, extract_code_block, execute_code_safely
from app.database.operations import load_typing_stats
from app.database.config import get_db
from sqlalchemy.orm import Session

def test_analysis_flow():
    """Test the complete analysis flow from query to execution"""
    
    # Get database session
    db = next(get_db())
    
    try:
        # Load test data
        print("\nLoading data from database...")
        data = load_typing_stats(db)
        if not data:
            print("No data found in database!")
            return
        
        df = pd.DataFrame(data)
        print(f"Loaded {len(df)} records")
        print("\nDataFrame head:")
        print(df.head())
        
        # Test queries
        test_queries = [
            "Show my average WPM for the last 10 races",
            "Plot my WPM trend over time",
            "Calculate my accuracy trend",
            "Show my performance by time of day"
        ]
        
        for query in test_queries:
            print(f"\n\nTesting query: {query}")
            print("-" * 50)
            
            # Generate code
            print("\nGenerating code...")
            response = generate_code(df, query)
            code = extract_code_block(response)
            
            if not code:
                print("Failed to generate code!")
                continue
                
            print("\nGenerated code:")
            print(code)
            
            # Execute code
            print("\nExecuting code...")
            success, result, modified_code = execute_code_safely(code, df)
            
            if success:
                print("\nExecution successful!")
                if isinstance(result, dict):
                    if result.get('result') is not None:
                        print("\nResult:")
                        print(result['result'])
                    if result.get('figure'):
                        print("\nFigure was generated")
            else:
                print(f"\nExecution failed: {result}")
                print("\nModified code that failed:")
                print(modified_code)
    
    except Exception as e:
        print(f"Test failed with error: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    print("Starting analysis test...")
    test_analysis_flow() 