import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from typing import Dict, Tuple, Optional, List, Any
from anthropic import Anthropic
import os
import json
import re
from dataclasses import dataclass
from app.utils.prompts import custom_prompt, custom_prompt_with_error
from app.utils.variable_mapper import VariableMapper, preprocess_code

# Load environment variables
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')

@dataclass
class Question:
    id: int
    question: str
    level: str
    category: str

def generate_code(df: pd.DataFrame, user_question: str) -> str:
    """Generate code using Claude API"""
    client = Anthropic(api_key=ANTHROPIC_API_KEY)    
    prompt = custom_prompt(df, user_question)
    try:
        response = client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=1000,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )
        return response.content[0].text
    except Exception as e:
        return f"Claude Response Failed (103): {str(e)}"

def execute_code_safely(code: str, df: pd.DataFrame) -> Tuple[bool, str, str]:
    """Execute code in a safe environment with proper setup"""
    try:
        # Initialize variable mapper and setup
        mapper = VariableMapper(df)
        
        # Create a copy of DataFrame with timestamp
        df = df.copy()
        df['timestamp'] = pd.to_datetime(df['time'], unit='s')
        
        # Setup execution environment
        local_ns = {
            'pd': pd,
            'df': df,
            'plt': plt,
            'sns': sns,
            'np': np
        }
        
        # Preprocess code
        modified_code, _ = preprocess_code(code, mapper)
        
        # Execute code
        exec(modified_code, local_ns)
        
        # Handle results
        result = local_ns.get('result', None)
        if plt.get_fignums():
            plt.close()
            
        return True, str(result) if result is not None else "", modified_code
        
    except Exception as e:
        return False, str(e), code

class QueryGuidance:
    def __init__(self):
        """Initialize QueryGuidance with question bank"""
        self.question_bank_path = os.path.join(os.path.dirname(__file__), 'questionbank.json')
        self.questions: List[Question] = []
        self._load_questions()

    def _load_questions(self) -> None:
        """Load and parse questions from the JSON file"""
        try:
            with open(self.question_bank_path, 'r') as f:
                data = json.load(f)
                
            for category_group in data:
                level = category_group['level']
                category = category_group['category']
                for q in category_group['questions']:
                    self.questions.append(Question(
                        id=q['id'],
                        question=q['question'],
                        level=level,
                        category=category
                    ))
        except Exception as e:
            print(f"Error loading questions: {str(e)}")
            self.questions = []

    def _calculate_relevance_score(self, question: Question, query: str) -> float:
        """Calculate relevance score for a question based on the query"""
        if not query:
            return 0.0
            
        q_text = question.question.lower()
        query = query.lower()
        
        # Exact match gets highest score
        if query == q_text:
            return 1.0
            
        # Contains full query as substring
        if query in q_text:
            return 0.8
            
        # Check for word matches
        query_words = set(re.findall(r'\w+', query))
        question_words = set(re.findall(r'\w+', q_text))
        
        matching_words = query_words.intersection(question_words)
        if matching_words:
            return 0.5 * len(matching_words) / len(query_words)
            
        return 0.0

    def filter_questions(self, level: str = None, category: str = None, query: str = None, max_suggestions: int = 5) -> List[Dict[str, Any]]:
        """Return filtered and scored questions based on level, category, and query"""
        if not self.questions:
            return []

        # First, filter by level and category
        filtered_questions = self.questions
        if level:
            filtered_questions = [q for q in filtered_questions if q.level == level]
        if category:
            filtered_questions = [q for q in filtered_questions if q.category == category]

        # If there's a search query, score and sort the questions
        if query:
            scored_questions = [
                (self._calculate_relevance_score(q, query), q) 
                for q in filtered_questions
            ]
            scored_questions.sort(key=lambda x: x[0], reverse=True)
            filtered_questions = [q for score, q in scored_questions if score > 0]

        # If no filters are set and no query, return a diverse set of basic questions
        if not any([level, category, query]):
            basic_questions = [q for q in self.questions 
                             if q.level in ["Basic", "Users"]][:max_suggestions]
            return [{"id": q.id, "question": q.question, "level": q.level, "category": q.category}
                    for q in basic_questions]

        # Convert Question objects to dictionaries for JSON serialization
        return [{"id": q.id, "question": q.question, "level": q.level, "category": q.category}
                for q in filtered_questions[:max_suggestions]]

    def get_levels(self) -> List[str]:
        """Get available question levels"""
        return list(set(q.level for q in self.questions))

    def get_categories(self) -> List[str]:
        """Get available question categories"""
        return list(set(q.category for q in self.questions))

    def get_question_by_id(self, question_id: int) -> Optional[Question]:
        """Retrieve a question by its ID"""
        for q in self.questions:
            if q.id == question_id:
                return q
        return None