from typing import Dict, Any, Optional, List
import pandas as pd
import tempfile
import json
from pathlib import Path
from openai import AsyncOpenAI, AsyncAssistantEventHandler, AsyncStream
from typing_extensions import override
from .base import BaseAssistantModel, AnalysisResult
import asyncio

class F1AnalysisEventHandler(AsyncAssistantEventHandler):
    def __init__(self):
        super().__init__()
        self.analysis_text = ""
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
            if hasattr(delta.code_interpreter, 'outputs'):
                for output in delta.code_interpreter.outputs:
                    if hasattr(output, 'type') and output.type == "image":
                        if hasattr(output.image, 'file_id'):
                            self.image_files.append(output.image.file_id)

class GPT4Assistant(BaseAssistantModel):
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
                "description": "Expert in analyzing Formula 1 race data and statistics",
                "model": self.model,
                "tools": [{"type": "code_interpreter"}]
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
            # Save DataFrame to CSV
            df.to_csv(f.name, index=True)
            
            # Upload file
            with open(f.name, 'rb') as file:
                response = await self.client.files.create(
                    file=file,
                    purpose='assistants'
                )
            
            # Clean up temp file
            Path(f.name).unlink()
            
            return response.id

    async def direct_analysis(self, context: dict) -> AnalysisResult:
        """Perform analysis using the Assistants API with code interpreter."""
        try:
            # Handle DataFrame if provided
            if 'df' in context:
                self.current_df = context['df']
                file_id = await self.upload_dataframe(self.current_df)
                self.file_ids.append(file_id)
                
                # Create/update assistant with the file
                await self.setup_assistant(file_ids=[file_id])
            else:
                await self.setup_assistant()
            
            # Create new thread if none exists
            if not self.thread:
                await self.create_thread()
            
            if not self.thread or not self.assistant:
                raise RuntimeError("Failed to initialize thread or assistant")
            
            # Add the user's query to the thread
            await self.client.beta.threads.messages.create(
                thread_id=self.thread.id,
                role="user",
                content=context['query']
            )
            
            # Create event handler for streaming
            event_handler = F1AnalysisEventHandler()
            
            # Run the assistant with streaming
            async with self.client.beta.threads.runs.stream(
                thread_id=self.thread.id,
                assistant_id=self.assistant.id,
                instructions="""
                Analyze the F1 race data provided in the CSV file.
                Generate visualizations when appropriate.
                Provide clear explanations of your findings.
                If generating plots, save them as PNG files.
                """,
                event_handler=event_handler
            ) as stream:
                await stream.until_done()
            
            return AnalysisResult(
                data={
                    "text": event_handler.analysis_text,
                    "images": event_handler.image_files
                },
                explanation=event_handler.analysis_text,
                code=None  # Code is handled by the assistant internally
            )
            
        except Exception as e:
            raise RuntimeError(f"Assistant analysis failed: {str(e)}")
            
    async def cleanup(self):
        """Clean up resources when done."""
        try:
            # Delete thread if it exists
            if self.thread and hasattr(self.thread, 'id'):
                await self.client.beta.threads.delete(self.thread.id)
                self.thread = None
            
            # Delete uploaded files
            for file_id in self.file_ids:
                try:
                    await self.client.files.delete(file_id)
                except Exception:
                    pass  # Ignore errors in file deletion
            self.file_ids = []
            
        except Exception as e:
            raise RuntimeError(f"Cleanup failed: {str(e)}") 