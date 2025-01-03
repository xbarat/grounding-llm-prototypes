import pytest
import pandas as pd
import os
from app.models.gpt4_assistant import GPT4Assistant
from app.models.base import AnalysisResult
import pytest_asyncio

@pytest.fixture
def sample_df():
    """Create a sample F1 DataFrame for testing."""
    return pd.DataFrame({
        'driver': ['Max Verstappen', 'Lewis Hamilton', 'Charles Leclerc'] * 3,
        'race': ['Monaco GP', 'Monaco GP', 'Monaco GP', 
                'British GP', 'British GP', 'British GP',
                'Italian GP', 'Italian GP', 'Italian GP'],
        'position': [1, 2, 3, 2, 1, 4, 1, 3, 2],
        'lap_time': [80.5, 81.2, 81.5, 79.8, 79.5, 80.1, 80.2, 80.8, 80.4]
    })

@pytest_asyncio.fixture
async def assistant():
    """Create a GPT4Assistant instance."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.skip("OPENAI_API_KEY not found in environment")
    
    assistant = GPT4Assistant(api_key=api_key)
    try:
        await assistant.setup_assistant()  # Initialize the assistant
        yield assistant
    finally:
        await assistant.cleanup()  # Clean up after tests

@pytest.mark.asyncio
async def test_basic_analysis(assistant: GPT4Assistant, sample_df):
    """Test basic analysis with a simple query."""
    context = {
        'query': 'Show me Max Verstappen\'s performance across different races',
        'df': sample_df
    }
    
    result = await assistant.direct_analysis(context)
    
    assert isinstance(result, AnalysisResult)
    assert isinstance(result.data, dict)
    assert 'text' in result.data
    assert 'images' in result.data
    assert result.explanation is not None

@pytest.mark.asyncio
async def test_follow_up_query(assistant: GPT4Assistant, sample_df):
    """Test follow-up query capability."""
    # First query
    context1 = {
        'query': 'Compare lap times between Verstappen and Hamilton',
        'df': sample_df
    }
    result1 = await assistant.direct_analysis(context1)
    assert isinstance(result1, AnalysisResult)
    
    # Follow-up query (should use the same thread and data)
    context2 = {
        'query': 'Who had better performance in Monaco?'
    }
    result2 = await assistant.direct_analysis(context2)
    assert isinstance(result2, AnalysisResult)

@pytest.mark.asyncio
async def test_visualization_request(assistant: GPT4Assistant, sample_df):
    """Test if the assistant generates visualizations when requested."""
    context = {
        'query': 'Create a line plot showing lap time trends for all drivers',
        'df': sample_df
    }
    
    result = await assistant.direct_analysis(context)
    
    assert isinstance(result, AnalysisResult)
    assert len(result.data['images']) > 0  # Should have at least one visualization 