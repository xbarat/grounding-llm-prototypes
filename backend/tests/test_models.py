"""Tests for model implementations"""
import pytest
import pandas as pd
import os
from dotenv import load_dotenv
from app.analyst.models import get_code_generator
from app.analyst.prompts import f1_prompt

@pytest.fixture(autouse=True)
def setup_environment():
    """Set up test environment variables"""
    # Load environment variables from .env file
    load_dotenv()
    yield

def test_gpt4_code_generation():
    """Test GPT-4 code generation"""
    # Create a sample DataFrame
    test_data = {
        'season': ['2021', '2021', '2022', '2022', '2023', '2023'],
        'round': ['1', '2', '1', '2', '1', '2'],
        'driver': ['Max Verstappen'] * 6,
        'points': [25, 18, 25, 25, 25, 18],
        'position': [1, 2, 1, 1, 1, 2],
        'grid': [1, 3, 1, 1, 1, 2],
        'status': ['Finished'] * 6,
        'constructor': ['Red Bull'] * 6,
        'circuit': ['Circuit 1', 'Circuit 2'] * 3
    }
    df = pd.DataFrame(test_data)
    
    # Get GPT-4 generator
    generator = get_code_generator("gpt4")
    
    # Create prompt
    query = "Show Max Verstappen's performance trend from 2021 to 2023"
    prompt = f1_prompt(df, query)
    
    # Generate code
    print("\nGenerating code with GPT-4...")
    response = generator.generate(prompt)
    print("\nGPT-4 Response:")
    print(response)
    
    # Basic validation
    assert response is not None, "No response from GPT-4"
    assert "```python" in response, "No Python code block in response"
    assert "plt.show()" not in response, "Response contains plt.show()"
    assert "plt.savefig" not in response, "Response contains plt.savefig"
    
    # Check for required components
    assert "import" in response.lower(), "No imports in code"
    assert "sns" in response.lower(), "No seaborn usage in code"
    assert "lineplot" in response.lower() or "plot" in response.lower(), "No plotting code"
    assert "output" in response.lower(), "No output text" 