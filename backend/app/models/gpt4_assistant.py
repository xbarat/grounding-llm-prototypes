from typing import Dict, Any, Optional, List
import pandas as pd
import tempfile
import json
from pathlib import Path
from openai import AsyncOpenAI, AsyncAssistantEventHandler, AsyncStream
from typing_extensions import override
from .base import BaseAssistantModel, BaseGenerationModel, AnalysisResult
import asyncio

class F1AnalysisEventHandler(AsyncAssistantEventHandler):
    def __init__(self):
        super().__init__()
        self.analysis_text = ""
        self.code_output = ""
        self.image_files: List[str] = []
        
    @override
    async def on_text_created(self, text: Any) -> None:
        pass
        
    @override
    async def on_text_delta(self, delta: Any, snapshot: Any) -> None:
        if hasattr(delta, 'text') and delta.text and delta.text.value:
            self.analysis_text += delta.text.value
        
    @override
    async def on_tool_call_created(self, tool_call: Any) -> None:
        pass

    @override
    async def on_tool_call_delta(self, delta: Any, snapshot: Any) -> None:
        if hasattr(delta, 'code_interpreter') and delta.code_interpreter:
            if hasattr(delta.code_interpreter, 'input'):
                self.code_output += delta.code_interpreter.input + "\n"
            if hasattr(delta.code_interpreter, 'outputs'):
                for output in delta.code_interpreter.outputs:
                    if hasattr(output, 'type'):
                        if output.type == "image":
                            if hasattr(output.image, 'file_id'):
                                self.image_files.append(output.image.file_id)
                        elif output.type == "text":
                            self.code_output += output.text + "\n"

class GPT4Assistant(BaseGenerationModel):
    def __init__(self, api_key: str, model: str = "gpt-4"):
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model
        self.assistant: Optional[Any] = None
        self.thread: Optional[Any] = None
        self.current_df = None
        self.file_ids: List[str] = []
        
    async def setup_assistant(self, file_ids: Optional[List[str]] = None):
        """Create or get the assistant with appropriate configuration."""
        if not self.assistant:
            create_params = {
                "name": "F1 Data Analyst",
                "description": "Expert in analyzing Formula 1 race data and statistics using Python",
                "model": self.model,
                "tools": [{"type": "code_interpreter"}],
                "instructions": """
                You are an expert F1 data analyst. Your role is to:
                1. Generate Python code to analyze F1 race data
                2. Create visualizations using matplotlib/seaborn
                3. Provide clear explanations of the analysis
                4. Follow best practices for data visualization
                5. Handle data cleaning and preprocessing
                
                Always use pandas for data manipulation and seaborn/matplotlib for visualization.
                """
            }
            if file_ids:
                create_params["files"] = file_ids
                
            self.assistant = await self.client.beta.assistants.create(**create_params)

    async def create_thread(self):
        """Create a new conversation thread."""
        self.thread = await self.client.beta.threads.create()

    async def upload_dataframe(self, df: pd.DataFrame) -> str:
        """Upload DataFrame as a file for the assistant."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            df.to_csv(f.name, index=True)
            with open(f.name, 'rb') as file:
                response = await self.client.files.create(
                    file=file,
                    purpose='assistants'
                )
            Path(f.name).unlink()
            return response.id

    async def code_generation(self, data: Dict[str, pd.DataFrame], requirements: Dict[str, Any]) -> str:
        """Generate analysis code using the Assistant."""
        try:
            # Upload the DataFrame
            if data:
                main_df = next(iter(data.values()))
                file_id = await self.upload_dataframe(main_df)
                self.file_ids.append(file_id)
                await self.setup_assistant(file_ids=[file_id])
            else:
                await self.setup_assistant()
            
            # Create new thread
            if not self.thread:
                await self.create_thread()
            
            if not self.thread or not self.assistant:
                raise RuntimeError("Failed to initialize thread or assistant")
            
            # Create the analysis prompt
            prompt = f"""
            Analyze the F1 race data in the uploaded CSV file and generate Python code to visualize the following:
            {requirements.get('query', '')}
            
            Requirements:
            {json.dumps(requirements, indent=2)}
            
            The data is available in the uploaded CSV file as 'df'.
            Generate Python code that:
            1. Processes and cleans the data appropriately
            2. Creates clear and informative visualizations
            3. Adds proper titles, labels, and legends
            4. Includes a summary of the findings
            
            Use pandas for data manipulation and seaborn/matplotlib for visualization.
            Test the code with the provided data and ensure it works correctly.
            """
            
            # Add the prompt to the thread
            await self.client.beta.threads.messages.create(
                thread_id=self.thread.id,
                role="user",
                content=prompt
            )
            
            # Create event handler for streaming
            event_handler = F1AnalysisEventHandler()
            
            # Run the assistant
            async with self.client.beta.threads.runs.stream(
                thread_id=self.thread.id,
                assistant_id=self.assistant.id,
                event_handler=event_handler
            ) as stream:
                await stream.until_done()
            
            # Extract and clean the generated code
            code = event_handler.code_output.strip()
            
            # If no code was captured from the code interpreter, use the text response
            if not code:
                code = event_handler.analysis_text
            
            # Extract code blocks if present
            if "```python" in code:
                code = code.split("```python")[1].split("```")[0].strip()
            elif "```" in code:
                code = code.split("```")[1].strip()
            
            return code
            
        except Exception as e:
            raise RuntimeError(f"Code generation failed: {str(e)}")
        finally:
            await self.cleanup()
            
    async def cleanup(self):
        """Clean up resources when done."""
        try:
            if self.thread and hasattr(self.thread, 'id'):
                await self.client.beta.threads.delete(self.thread.id)
                self.thread = None
            
            for file_id in self.file_ids:
                try:
                    await self.client.files.delete(file_id)
                except Exception:
                    pass
            self.file_ids = []
            
        except Exception as e:
            raise RuntimeError(f"Cleanup failed: {str(e)}") 