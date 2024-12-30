import asyncio
import httpx
from data2 import DataPipeline, DataRequirements

async def test_verstappen_query():
    """Test connection for Max Verstappen's 2023 results"""
    print("\nTesting Max Verstappen 2023 Query")
    print("-" * 50)
    
    pipeline = DataPipeline()
    requirements = DataRequirements(
        endpoint="/api/f1/drivers",
        params={
            "season": "2023",
            "driver": "max_verstappen"
        }
    )

    # Test with increased timeout and different chunk sizes
    timeout = httpx.Timeout(60.0)  # Increased timeout
    async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
        url = pipeline._build_url(requirements)
        print(f"Testing URL: {url}")
        
        for attempt in range(3):
            try:
                print(f"\nAttempt {attempt + 1}")
                response = await client.get(url)
                print(f"Status Code: {response.status_code}")
                print(f"Headers: {dict(response.headers)}")
                
                if response.status_code == 200:
                    data = response.json()
                    print("Successfully retrieved and parsed JSON")
                    print(f"Response size: {len(response.content)} bytes")
                    return True
                else:
                    print(f"Request failed with status {response.status_code}")
                    print(f"Response text: {response.text[:200]}...")
                
            except Exception as e:
                print(f"Error on attempt {attempt + 1}: {str(e)}")
                if "incomplete message" in str(e).lower():
                    print("Connection closed before complete message received")
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
        
        return False

async def main():
    success = await test_verstappen_query()
    print("\nTest Result:", "Success" if success else "Failure")

if __name__ == "__main__":
    asyncio.run(main()) 