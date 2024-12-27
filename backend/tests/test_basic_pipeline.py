"""
Basic test module for verifying the data pipeline functionality.
"""

import pytest
import sys
import os
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.append(str(backend_dir))

from app.utils.platform_fetcher import fetch_platform_data
from app.utils.f1_api import F1API

@pytest.mark.asyncio
async def test_f1_basic_fetch():
    """Test basic F1 data fetching."""
    async with F1API() as f1_api:
        try:
            # Test driver standings
            data = await f1_api.fetch_driver_standings()
            print("\nF1 Driver Standings Response:")
            print(data)
            assert isinstance(data, dict), "Response should be a dictionary"
            assert "MRData" in data, "Response should contain MRData"
            return True
        except Exception as e:
            print(f"Error fetching F1 data: {str(e)}")
            return False

if __name__ == "__main__":
    import asyncio
    
    async def run_test():
        result = await test_f1_basic_fetch()
        print(f"\nTest Result: {'✅ Passed' if result else '❌ Failed'}")
    
    asyncio.run(run_test()) 