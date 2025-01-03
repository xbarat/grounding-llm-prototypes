from typing import Dict, Any, Optional, List
import pandas as pd
from openai import AsyncOpenAI
from .base import BaseAssistantModel, AnalysisResult
import asyncio

class GPT4Assistant(BaseAssistantModel):
    def __init__(self, api_key: str, model: str = "gpt-4"):
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model
        self.assistant = None
        self.thread = None
        self.current_df = None
        
    async def setup_assistant(self):
        """Create or get the assistant with appropriate configuration."""
        if not self.assistant:
            self.assistant = await self.client.beta.assistants.create(
                name="F1 Data Analyst",
                description="Expert in analyzing Formula 1 race data and statistics",
                model=self.model,
                tools=[{"type": "code_interpreter"}]
            )
            
    async def create_thread(self):
        """Create a new conversation thread."""
        self.thread = await self.client.beta.threads.create()
        
    async def direct_analysis(self, context: dict) -> AnalysisResult:
        """Perform analysis using the Assistants API with code interpreter."""
        try:
            # Setup assistant if not already done
            await self.setup_assistant()
            
            # Create new thread if none exists
            if not self.thread:
                await self.create_thread()
            
            # Update current dataframe if provided
            if 'df' in context:
                self.current_df = context['df']
                
            # Create message with the query and data context
            message = await self.client.beta.threads.messages.create(
                thread_id=self.thread.id,
                role="user",
                content=context['query']
            )
            
            # Run the assistant
            run = await self.client.beta.threads.runs.create(
                thread_id=self.thread.id,
                assistant_id=self.assistant.id,
                instructions=f"""
                Analyze the F1 race data based on the query.
                The data is available as a pandas DataFrame.
                Generate visualizations when appropriate.
                Provide clear explanations of your findings.
                """
            )
            
            # Wait for completion and check status
            while True:
                run = await self.client.beta.threads.runs.retrieve(
                    thread_id=self.thread.id,
                    run_id=run.id
                )
                if run.status == "completed":
                    break
                elif run.status in ["failed", "cancelled", "expired"]:
                    raise RuntimeError(f"Assistant run failed with status: {run.status}")
                await asyncio.sleep(1)  # Wait before checking again
            
            # Get the response
            messages = await self.client.beta.threads.messages.list(
                thread_id=self.thread.id
            )
            
            # Extract the latest assistant message
            latest_message = messages.data[0]
            content = latest_message.content[0]
            
            # Handle different content types
            if hasattr(content, 'text'):
                analysis_text = content.text.value
            else:
                analysis_text = str(content)  # Fallback for other content types
            
            return AnalysisResult(
                data=analysis_text,  # Main analysis
                explanation=analysis_text,  # Same as data for now
                code=None  # Code is handled by the assistant internally
            )
            
        except Exception as e:
            raise RuntimeError(f"Assistant analysis failed: {str(e)}")
            
    async def cleanup(self):
        """Clean up resources when done."""
        if self.thread and hasattr(self.thread, 'id'):
            await self.client.beta.threads.delete(self.thread.id)
            self.thread = None 