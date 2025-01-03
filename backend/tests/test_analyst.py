import pytest
import pandas as pd
import os
from app.analyst.generate import execute_code_safely

def test_code_execution():
    """Test code execution and figure capture"""
    # Create a sample DataFrame similar to F1 data
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
    
    # Test code that saves figure before showing
    test_code = """
# Data processing
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import io
import base64

# Convert string columns to numeric
df['season'] = pd.to_numeric(df['season'])
df['round'] = pd.to_numeric(df['round'])

# Create visualization
fig, ax = plt.subplots(figsize=(10, 6))
sns.lineplot(data=df, x='round', y='points', hue='season', marker='o', ax=ax)
ax.set_title('Max Verstappen Performance Trend (2021-2023)')
ax.set_xlabel('Race Round')
ax.set_ylabel('Points Scored')

# Save figure to buffer before showing
buffer = io.BytesIO()
fig.savefig(buffer, format='png', bbox_inches='tight')
buffer.seek(0)
saved_figure = base64.b64encode(buffer.getvalue()).decode()

# Now show the plot
plt.show()

# Generate summary
output = "Test visualization showing Max Verstappen's performance trend"
print(f"Saved figure length: {len(saved_figure)}")
"""
    
    # Execute the test code
    print("\nExecuting test code")
    success, result, modified_code = execute_code_safely(test_code, df)
    
    # Print detailed results
    print("\nModified Code:")
    print(modified_code)
    print("\nExecution Success:", success)
    if not success:
        print("Error:", result.get("error"))
    else:
        print("\nOutput:", result.get("output"))
        print("\nFigure data length:", len(result.get("figure", "")))
        print("\nData sample:", result.get("data", [])[:2])
    
    # Assertions
    assert success, "Code execution failed"
    assert result.get("figure") is not None, "No figure generated"
    assert len(result.get("figure", "")) > 0, "Empty figure data"
    assert result.get("output") is not None, "No output text generated" 