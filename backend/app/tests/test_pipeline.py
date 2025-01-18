"""Tests for the pipeline components."""
import pytest
import pandas as pd
from datetime import datetime
import time

from app.pipeline.data2 import DataPipeline
from app.pipeline.optimized_adapters import OptimizedQueryAdapter, OptimizedResultAdapter

@pytest.mark.asyncio
async def test_pipeline_processing(sample_pipeline_result):
    """Test pipeline data processing"""
    pipeline = DataPipeline()
    
    # Create test requirements
    requirements = {
        'endpoint': '/api/f1/constructors',
        'params': {
            'constructor': 'ferrari',
            'season': list(range(2015, 2024))
        }
    }
    
    # Process requirements
    response = await pipeline.process(requirements)
    
    assert response is not None
    assert response['success'] == True
    assert 'data' in response
    assert 'results' in response['data']
    assert len(response['data']['results']) > 0
    
    # Verify data structure
    results = response['data']['results']
    df = pd.DataFrame(results)
    assert not df.empty
    assert 'constructor_id' in df.columns
    assert 'year' in df.columns
    assert 'points' in df.columns

@pytest.mark.asyncio
async def test_query_adapter(sample_query):
    """Test query adaptation"""
    adapter = OptimizedQueryAdapter()
    
    # Create mock query result as a dictionary
    query_result = {
        'requirements': {
            'endpoint': '/api/f1/constructors',
            'params': {'constructor': 'ferrari'}
        },
        'source': 'test',
        'confidence': 1.0,
        'processing_time': 0.5,
        'trace': ['Test trace']
    }
    
    # Adapt query
    adapted = await adapter.adapt(query_result)
    
    assert adapted is not None
    assert hasattr(adapted, 'endpoint')
    assert hasattr(adapted, 'params')
    assert hasattr(adapted, 'metadata')
    assert adapted.metadata.get('source') == 'test'
    assert adapted.metadata.get('confidence') == 1.0

@pytest.mark.asyncio
async def test_result_adapter(sample_pipeline_result):
    """Test result adaptation"""
    adapter = OptimizedResultAdapter()
    start_time = time.time()
    
    # Adapt result
    adapted = await adapter.adapt_pipeline_result(sample_pipeline_result, start_time)
    
    assert adapted.success == True
    assert adapted.data is not None
    assert 'results' in adapted.data
    assert adapted.metadata['query_type'] == 'historical'
    assert 'processing_time' in adapted.metadata 