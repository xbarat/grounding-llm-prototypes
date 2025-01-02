# prompts.py
from typing import Optional

def f1_prompt(df, question: str) -> str:
    """Generate a prompt specifically for F1 data visualization with robust data handling"""
    prompt = f'''You are an F1 data analyst creating visualizations. You have a DataFrame 'data' containing F1 race data with this structure:

DataFrame Info:
{df.info()}

First few rows:
{df.head().to_string()}

Question: {question}

Generate Python code that follows these exact requirements:
1. Use matplotlib's dark_background style
2. Set seaborn's darkgrid theme
3. Use the existing 'data' DataFrame exactly as provided
4. Create clear visualizations with proper data validation
5. IMPORTANT: Season values are strings (e.g. '2021', not 2021)

The code MUST follow this exact structure:
```python
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Setup style
plt.style.use('dark_background')
sns.set_theme(style='darkgrid')
plt.rcParams['figure.figsize'] = [12, 6]
plt.rcParams['figure.dpi'] = 100
plt.rcParams['savefig.dpi'] = 100
plt.rcParams['font.size'] = 12
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['axes.labelsize'] = 12
plt.rcParams['xtick.labelsize'] = 10
plt.rcParams['ytick.labelsize'] = 10

# Create visualization
plt.figure(figsize=(12, 6))

# Your visualization code here using the 'data' DataFrame
# Example for performance trend:
# sns.lineplot(data=data, x='season', y='points', marker='o')
# plt.title('Performance Trend')
# plt.xlabel('Season')
# plt.ylabel('Points')

# IMPORTANT: When checking seasons, use string values
# Example:
# required_seasons = ['2021', '2022', '2023']  # Use strings, not integers
# available_seasons = data['season'].unique()
# missing_seasons = set(required_seasons) - set(available_seasons)

# Add any necessary text output
output = "Analysis summary: ..."
```

Key requirements:
- Use the exact DataFrame column names shown in the info
- Create clear visualizations with proper titles and labels
- Include a text summary in the 'output' variable
- NO plt.savefig() calls - handled externally
- Always handle seasons as strings, not integers

Respond ONLY with the Python code block. Start with ```python and end with ```.
'''
    return prompt

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
