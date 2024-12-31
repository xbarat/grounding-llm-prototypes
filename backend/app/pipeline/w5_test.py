"""
W5 Integration Test Suite - Pipeline to Analyst Connection
Tests the full pipeline with focus on time-series analysis capabilities.
"""

import sys
import os
import asyncio
import httpx
from pathlib import Path
import pandas as pd
import pytest
from typing import Dict, Any, List, Optional, Tuple

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from pipeline.data2 import DataPipeline, DataTransformer, DataResponse
from query.processor import QueryProcessor
from analyst.generate import generate_code, extract_code_block, execute_code_safely

@pytest.fixture
def test_suite():
    return W5TestSuite()

class W5TestSuite:
    def __init__(self):
        self.pipeline = DataPipeline()
        self.transformer = DataTransformer()
        self.query_processor = QueryProcessor()
        self.results = {
            "success": 0,
            "failure": 0,
            "errors": []
        }

    async def run_test_case(self, query: str, expected_data_shape: Optional[Tuple[int, int]] = None) -> bool:
        """Run a single test case through the entire pipeline."""
        print(f"\nTesting query: {query}")
        try:
            # 1. Process query
            print("Step 1: Processing query...")
            requirements = await self.query_processor.process_query(query)
            print(f"Generated requirements: {requirements}")

            # 2. Fetch and transform data
            print("\nStep 2: Fetching and processing data...")
            async with httpx.AsyncClient() as client:
                self.pipeline.client = client
                response: DataResponse = await self.pipeline.process(requirements)
                if not response.success or not response.data:
                    raise Exception(f"No data retrieved from pipeline: {response.error}")
                data = response.data
            
            # 3. Generate analysis code
            print("\nStep 3: Generating analysis code...")
            df = next(iter(data.values()))  # Get first DataFrame
            code_response = generate_code(df, query)
            code_block = extract_code_block(code_response)
            if not code_block:
                raise Exception("No code block generated")
            print(f"Generated code length: {len(code_block)}")

            # 4. Execute code
            print("\nStep 4: Executing analysis code...")
            success, result, _ = execute_code_safely(code_block, df)
            if not success:
                raise Exception(f"Code execution failed: {result}")

            # 5. Validate results
            if expected_data_shape and isinstance(df, pd.DataFrame):
                assert df.shape == expected_data_shape, f"Data shape mismatch. Expected {expected_data_shape}, got {df.shape}"

            self.results["success"] += 1
            return True

        except Exception as e:
            print(f"Error: {str(e)}")
            self.results["failure"] += 1
            self.results["errors"].append({
                "query": query,
                "error": str(e)
            })
            return False

@pytest.mark.asyncio
async def test_verstappen_performance(test_suite):
    """Test Max Verstappen's performance trend analysis."""
    query = "Show Max Verstappen's performance trend from 2021 to 2023"
    assert await test_suite.run_test_case(query)

@pytest.mark.asyncio
async def test_hamilton_points(test_suite):
    """Test Lewis Hamilton's points progression analysis."""
    query = "Compare Lewis Hamilton's points progression across 2021-2023 seasons"
    assert await test_suite.run_test_case(query)

@pytest.mark.asyncio
async def test_alonso_position(test_suite):
    """Test Fernando Alonso's average finishing position analysis."""
    query = "How has Fernando Alonso's average finishing position changed from 2021 to 2023?"
    assert await test_suite.run_test_case(query)

@pytest.mark.asyncio
async def test_leclerc_qualifying(test_suite):
    """Test Charles Leclerc's qualifying performance analysis."""
    query = "Show Charles Leclerc's qualifying performance trend from 2021 to 2023"
    assert await test_suite.run_test_case(query)

@pytest.mark.asyncio
async def test_norris_points(test_suite):
    """Test Lando Norris's points accumulation analysis."""
    query = "Compare Lando Norris's points accumulation across the 2023 season"
    assert await test_suite.run_test_case(query)

@pytest.mark.asyncio
async def test_russell_performance(test_suite):
    """Test George Russell's performance development analysis."""
    query = "Show George Russell's performance development from 2022 to 2023"
    assert await test_suite.run_test_case(query)

@pytest.mark.asyncio
async def test_sainz_qualifying(test_suite):
    """Test Carlos Sainz's qualifying position analysis."""
    query = "How has Carlos Sainz's qualifying position varied throughout 2023?"
    assert await test_suite.run_test_case(query)

@pytest.mark.asyncio
async def test_piastri_progression(test_suite):
    """Test Oscar Piastri's rookie season progression analysis."""
    query = "Track Oscar Piastri's rookie season progression in 2023"
    assert await test_suite.run_test_case(query) 