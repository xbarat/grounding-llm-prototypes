from typing import Dict, Any, Optional
import pandas as pd
from anthropic import AsyncAnthropic
import os
from dotenv import load_dotenv
from app.query.analysis import AnalysisQuery
from dataclasses import dataclass
import numpy as np
import matplotlib.pyplot as plt
import json
import ast

# Load environment variables
load_dotenv()
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')

@dataclass
class AnalysisResult:
    code: str
    result: Any
    plot: Optional[str] = None
    error: Optional[str] = None

class AnalysisEngine:
    """Engine for generating F1 data analysis code"""
    
    def __init__(self):
        if not ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY environment variable is not set")
        self.client = AsyncAnthropic(api_key=ANTHROPIC_API_KEY)
    
    async def analyze(self, df: pd.DataFrame, query: str) -> AnalysisResult:
        """Generate and execute analysis code based on the query and DataFrame."""
        try:
            # Get DataFrame info for the prompt
            df_info = self._get_df_info(df)
            
            # Generate analysis code
            code = await self._generate_code(df_info, query)
            
            # Execute the generated code
            result = self._execute_code(code, df)
            
            return AnalysisResult(code=code, result=result)
            
        except Exception as e:
            # If there's an error, try to regenerate code with error context
            try:
                code = await self._generate_code(df_info, query, str(e))
                result = self._execute_code(code, df)
                return AnalysisResult(code=code, result=result)
            except Exception as e:
                return AnalysisResult(code="", result=None, error=str(e))

    async def _generate_code(self, df_info: str, query: str, error_context: Optional[str] = None) -> str:
        """Generate Python code for the analysis using Claude."""
        prompt = f"""You are an expert Python data analyst. Generate code to analyze Formula 1 data based on this query: {query}

DataFrame Information:
{df_info}

Requirements:
1. Use pandas, numpy and matplotlib for analysis
2. Include clear comments explaining the code
3. Handle data type conversions properly, especially for time-based columns
4. Return both numerical results and visualizations when relevant
5. Use plt.style.use('default') for consistent plotting
6. Include proper error handling
7. Format time deltas as MM:SS.mmm
8. Store the final result in a variable named 'result'

The code should be complete and executable. Only return the code, no explanations.
"""
        if error_context:
            prompt += f"\n\nPrevious error: {error_context}\nPlease fix the error in the generated code."

        response = await self.client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        # Extract code from the response
        if response.content:
            # Convert the response content to string
            content_str = str(response.content)
            # Remove any text before the first code block
            if '```python' in content_str:
                content_str = content_str[content_str.find('```python'):]
            elif '```' in content_str:
                content_str = content_str[content_str.find('```'):]
            return self._extract_code(content_str)
        else:
            raise Exception("No response content received from Claude")

    def _execute_code(self, code: str, df: pd.DataFrame) -> Any:
        """Execute the generated code in a safe environment."""
        # Create a copy of the DataFrame to avoid modifications
        df_copy = df.copy()
        
        # Create a namespace for code execution
        namespace = {
            'pd': pd,
            'np': np,
            'plt': plt,
            'df': df_copy
        }
        
        # Execute the code
        exec(code, namespace)
        
        # Return the result if available
        return namespace.get('result', None)

    def _extract_code(self, response: str) -> str:
        """Extract code blocks from Claude's response."""
        try:
            # Look for code between triple backticks
            if '```python' in response:
                code = response.split('```python')[1].split('```')[0]
            elif '```' in response:
                code = response.split('```')[1].split('```')[0]
            else:
                code = response
            return code.strip()
        except Exception:
            return response

    def _get_df_info(self, df: pd.DataFrame) -> str:
        """Get DataFrame information for the prompt."""
        info = []
        info.append(f"Shape: {df.shape}")
        info.append("\nColumns and data types:")
        for col in df.columns:
            info.append(f"- {col}: {df[col].dtype}")
        info.append("\nFirst few rows:")
        info.append(str(df.head()))
        return "\n".join(info)

# Test the analysis engine
def main():
    # Create sample DataFrame
    df = pd.DataFrame({
        'lap': range(1, 11),
        'driverId': ['max_verstappen', 'lewis_hamilton', 'charles_leclerc'] * 3 + ['max_verstappen'],
        'position': [1, 2, 3] * 3 + [1],
        'time': ['1:13.123', '1:13.456', '1:13.789'] * 3 + ['1:13.100']
    })
    
    # Create sample analysis query
    from app.query.analysis import AnalysisQuery, AnalysisType, AnalysisConstraints
    
    analysis_query = AnalysisQuery(
        analysis_type=AnalysisType.STATISTICAL,
        description="Calculate the average lap times for the top 3 drivers",
        data_context={
            "columns": ["lap", "driverId", "position", "time"],
            "data_type": "lap times",
            "special_fields": {"time": "lap time in MM:SS.sss format"}
        },
        constraints=AnalysisConstraints(
            time_range=None,
            entities=["max_verstappen", "lewis_hamilton", "charles_leclerc"],
            metrics=["average lap time"],
            limit=3
        ),
        expected_output="table"
    )
    
    # Initialize analysis engine
    engine = AnalysisEngine()
    
    # Generate analysis code
    print("\nGenerating analysis code...")
    code = engine.generate_code(df, analysis_query)
    
    print("\nGenerated Analysis Code:")
    print(code)

if __name__ == "__main__":
    main() 