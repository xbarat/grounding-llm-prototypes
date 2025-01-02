import asyncio
import pandas as pd
from app.pipeline.data2 import DataPipeline, DataRequirements
from app.analyst.generate import generate_code, extract_code_block, execute_code_safely

async def test_hamilton_data():
    """Test fetching multiple seasons of data for Lewis Hamilton"""
    pipeline = DataPipeline()
    requirements = DataRequirements(
        endpoint='/api/f1/drivers',
        params={
            'season': ['2021', '2022', '2023'],
            'driver': 'hamilton'
        }
    )
    
    print('\nTesting data fetch for Lewis Hamilton 2021-2023...')
    print('Requirements:', requirements)
    
    response = await pipeline.process(requirements)
    if response.success and response.data:
        df = response.data['results']
        print('\nData shape:', df.shape)
        print('\nSeasons available:', sorted(df['season'].unique()))
        print('\nRaces per season:')
        print(df.groupby('season').size())
        
        # Test code generation and execution
        print('\nTesting code generation and execution...')
        query = "Compare Lewis Hamilton's points progression across 2021-2023 seasons"
        code_response = generate_code(df, query)
        code = extract_code_block(code_response)
        
        if code is None:
            print('\nNo code block found in response')
            return
            
        print('\nGenerated code:')
        print(code)
        
        print('\nExecuting code...')
        success, result, modified_code = execute_code_safely(code, df)
        
        print('\nExecution result:', success)
        if not success:
            print('Error:', result.get('error'))
        else:
            print('Output:', result.get('output'))
            
        # Save data for inspection
        df.to_csv('hamilton_data.csv', index=False)
        print('\nData saved to hamilton_data.csv')
    else:
        print('Error:', response.error)

if __name__ == '__main__':
    asyncio.run(test_hamilton_data()) 