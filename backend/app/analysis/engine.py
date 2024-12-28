"""
Analysis engine module for generating and executing analysis code.
"""
from typing import Dict, Any
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
from anthropic import Anthropic
import os
from dotenv import load_dotenv
from ..query.processor import AnalysisRequirements

# Load environment variables
load_dotenv()
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')

class AnalysisEngine:
    """Generates and executes analysis code using Claude"""
    
    def __init__(self):
        """Initialize analysis engine with Claude client"""
        self.claude = Anthropic(api_key=ANTHROPIC_API_KEY)
        
        # Set matplotlib backend
        plt.switch_backend('Agg')
    
    async def analyze(
        self,
        df: pd.DataFrame,
        requirements: AnalysisRequirements
    ) -> Dict[str, Any]:
        """
        Generate and execute analysis code.
        
        Args:
            df: Input DataFrame to analyze
            requirements: Analysis requirements from query processor
            
        Returns:
            Analysis results including visualizations
        """
        # Generate analysis code
        code = await self._generate_code(df, requirements)
        
        # Execute code
        return await self._execute_code(code, df)
    
    async def _generate_code(
        self,
        df: pd.DataFrame,
        requirements: AnalysisRequirements
    ) -> str:
        """Generate Python code for analysis using Claude"""
        prompt = self._build_analysis_prompt(df, requirements)
        
        response = await self.claude.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=2000,
            temperature=0,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )
        
        # Extract code from response
        message = response.content[0]
        content = message.text if hasattr(message, 'text') else str(message)
        return self._extract_code(content)
    
    def _build_analysis_prompt(
        self,
        df: pd.DataFrame,
        requirements: AnalysisRequirements
    ) -> str:
        """Build prompt for code generation"""
        return f"""
        Generate Python code to analyze this DataFrame and create visualizations.
        
        DataFrame Schema:
        {df.dtypes.to_dict()}
        
        Requirements:
        - Metrics: {requirements['metrics']}
        - Grouping: {requirements['grouping']}
        - Visualization: {requirements['visualization']}
        - Operations: {requirements['operations']}
        
        The code should:
        1. Calculate required metrics
        2. Create visualizations using matplotlib/seaborn
        3. Save plot to base64 string
        4. Return results dictionary with:
           - metrics: calculated values
           - visualization_type: plot type
           - plot_data: base64 encoded plot
           - summary: text summary of findings
        
        Use this template:
        ```python
        import pandas as pd
        import numpy as np
        import matplotlib.pyplot as plt
        import seaborn as sns
        import io
        import base64
        
        # Your analysis code here
        
        # Create visualization
        plt.figure(figsize=(10, 6))
        # Your plotting code here
        
        # Save plot to base64
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        plot_data = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        # Return results
        result = {{
            'metrics': {{}},
            'visualization_type': 'line',
            'plot_data': plot_data,
            'summary': ''
        }}
        ```
        
        Return only the code, no explanations.
        """
    
    def _extract_code(self, response: str) -> str:
        """Extract code block from Claude's response"""
        try:
            start_idx = response.find('```python')
            if start_idx == -1:
                start_idx = response.find('```')
            if start_idx != -1:
                end_idx = response.find('```', start_idx + 3)
                if end_idx != -1:
                    code = response[start_idx:end_idx].strip()
                    return code.replace('```python', '').replace('```', '').strip()
        except Exception:
            pass
        raise ValueError("No valid code block found in response")
    
    async def _execute_code(
        self,
        code: str,
        df: pd.DataFrame
    ) -> Dict[str, Any]:
        """Execute generated code safely"""
        # Create execution namespace
        namespace = {
            'pd': pd,
            'df': df,
            'np': np,
            'plt': plt,
            'sns': sns,
            'io': io,
            'base64': base64
        }
        
        try:
            # Execute code
            exec(code, namespace)
            
            # Get results
            result = namespace.get('result', {})
            
            # Clean up
            plt.close('all')
            
            return result
            
        except Exception as e:
            plt.close('all')
            raise ValueError(f"Error executing analysis code: {str(e)}")
        
    async def regenerate_with_error(
        self,
        df: pd.DataFrame,
        requirements: AnalysisRequirements,
        error: str,
        previous_code: str
    ) -> str:
        """Regenerate code after an error"""
        prompt = f"""
        The previous code generated an error. Please fix and regenerate.
        
        Error:
        {error}
        
        Previous Code:
        ```python
        {previous_code}
        ```
        
        DataFrame Schema:
        {df.dtypes.to_dict()}
        
        Requirements:
        {requirements}
        
        Return only the fixed code, no explanations.
        """
        
        response = await self.claude.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=2000,
            temperature=0,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )
        
        # Extract code from response
        message = response.content[0]
        content = message.text if hasattr(message, 'text') else str(message)
        return self._extract_code(content) 