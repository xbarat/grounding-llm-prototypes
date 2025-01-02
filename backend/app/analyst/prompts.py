# prompts.py
from typing import Optional
import pandas as pd
from io import StringIO

def f1_prompt(df: pd.DataFrame, query: str) -> str:
    """Generate a prompt for F1 data analysis"""
    # Get DataFrame info
    buffer = StringIO()
    df.info(buf=buffer)
    df_info = buffer.getvalue()
    
    return f"""You are an F1 data analyst. Generate Python code to analyze and visualize F1 race data based on the user's query.
The data is available in a pandas DataFrame with the following structure:

{df_info}

Important guidelines:
1. Use seaborn and matplotlib for visualizations
2. Ensure numeric operations are performed on numeric data types
3. Convert string columns to numeric when needed (e.g., 'season', 'round')
4. Handle missing values appropriately
5. Create clear and informative visualizations
6. Include a brief text summary of the findings

User Query: {query}

Generate Python code that:
1. Processes the data appropriately
2. Creates a visualization
3. Provides a text summary

Return only the Python code block, no explanations. The code should be complete and ready to execute.
Use this format:
```python
# Data processing
[processing code]

# Create visualization
[visualization code]

# Generate summary
output = "[summary text]"
```"""

def stable_prompt_with_error(df, question: str, error_message: str, previous_code: Optional[str] = None) -> str:
    """Generate a prompt for error correction in F1 data analysis"""
    prompt = f'''The previous code attempt resulted in this error:
{error_message}

{"Previous code:\n" + previous_code if previous_code else ""}

Please provide corrected Python code for the F1 analysis question:
{question}

DataFrame structure:
{df.info()}

First few rows:
{df.head().to_string()}

Requirements:
- Fix the error in the code
- Keep the same visualization approach
- Ensure all imports are included
- Maintain proper formatting and styling
- DO NOT include any plt.savefig() calls - the figure will be handled externally
- IMPORTANT: Always handle seasons as strings (e.g. '2021', not 2021)

Respond ONLY with a Python code block that creates the visualization. The DataFrame 'data' is already loaded.
Your response must start with ```python and end with ```. Do not include any other text.
'''
    return prompt

def custom_prompt(df, question: str) -> str:
    """Generate a prompt for F1 data analysis, with focus on time-series visualization"""
    prompt = f'''You are an F1 data analyst creating visualizations. You are writing a code that will be executed with an existing DataFrame 'data' that contains F1 race data with the following structure:

DataFrame Info:
{df.info()}

First few rows:
{df.head().to_string()}

Question: {question}

Please provide a Python code solution that:
1. Assumes the DataFrame 'data' is already loaded and available as 'data'
2. Uses the exact column names and data types as shown in the DataFrame info
3. Includes necessary imports (matplotlib.pyplot as plt, seaborn as sns, numpy as np)
4. Creates clear and informative visualizations

Required code structure:
```python
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Set style
plt.style.use('seaborn')
sns.set_palette("deep")

# Create figure with appropriate size
plt.figure(figsize=(12, 6))

# Data validation
if len(data) == 0:
    print("No data found. Cannot create visualization.")
    plt.close()
else:
    # Your visualization code here
    # Make sure to include:
    # - Clear title
    # - Labeled axes
    # - Legend if multiple series
    # - Appropriate plot type
    # - Data type conversion if needed
    pass

# DO NOT include plt.savefig() - the figure will be handled externally
```

Key requirements:
- Validate data before plotting
- Use appropriate plot type (line, bar, scatter)
- Include clear title and labels
- Add legend if needed
- Format numbers properly
- NO plt.savefig() calls

Respond ONLY with the Python code block. Start with ```python and end with ```.
'''
    return prompt
