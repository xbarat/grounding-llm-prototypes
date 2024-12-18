import sqlite3
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import json
import io
import requests
import os
from typing import Dict, List, Tuple, Optional, Any
from anthropic import Anthropic
from utils.prompts import custom_prompt, custom_prompt_with_error
from dotenv import load_dotenv
from utils.variable_mapper import VariableMapper, preprocess_code
from utils.plotting import (
    setup_plotting_style,
    plot_player_dashboard,
    get_player_stats
)
from utils.query_guidance import QueryGuidance
from evals.eval_logger import EvalLogger

# Load environment variables
load_dotenv()
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')

def fetch_user_stats(username: str) -> Optional[Dict]:
    """Fetch user statistics from TypeRacer API."""
    try:
        url = f'https://data.typeracer.com/users'
        params = {
            'id': f'tr:{username}',
            'universe': 'play'
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Failed to fetch user stats: {str(e)}")
        return None

def fetch_data(player_id: str, universe: str, n: int, before_id: str = None) -> Optional[List[Dict[str, Any]]]:
    """Fetch data from TypeRacer API with improved error handling"""
    url = f'https://data.typeracer.com/games'
    params = {
        'playerId': player_id,
        'universe': universe,
        'n': n,
        'beforeId': before_id
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        if not data:
            st.warning("No data returned from API")
            return None
        save_to_database(data, player_id)
        return data
    except requests.RequestException as e:
        st.error(f"API request failed: {str(e)}")
        return None
    except json.JSONDecodeError:
        st.error("Invalid JSON response from API")
        return None

def save_to_database(data: List[Dict[str, Any]], player_id: str, db_name: str = "racer_data.db") -> None:
    """Save fetched data to SQLite database"""
    if os.path.exists(db_name):
        os.remove(db_name)

    sorted_data = sorted(data, key=lambda x: x['gn'])
    
    conn = sqlite3.connect(db_name)
    try:
        cursor = conn.cursor()
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS typing_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_id TEXT NOT NULL,
            entry_number INTEGER NOT NULL,
            speed REAL NOT NULL,
            accuracy REAL NOT NULL,
            pts REAL,
            time REAL NOT NULL,
            rank INTEGER,
            game_entry INTEGER NOT NULL,
            text_id INTEGER,
            skill_level TEXT,
            num_players INTEGER,
            UNIQUE(player_id, entry_number)
        )
        ''')

        for i, entry in enumerate(sorted_data, start=1):
            cursor.execute('''
            INSERT INTO typing_stats (
                player_id, entry_number, speed, accuracy, pts, 
                time, rank, game_entry, text_id, 
                skill_level, num_players
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (player_id, i, entry['wpm'], entry['ac'], entry.get('pts'),
                  entry['t'], entry.get('r'), entry['gn'], entry.get('tid'),
                  entry.get('sl'), entry.get('np')))
        
        conn.commit()
        st.success(f"Data successfully saved to {db_name}")
    except sqlite3.Error as e:
        st.error(f"Database error: {str(e)}")
        conn.rollback()
    finally:
        conn.close()

def load_data_from_db(db_path: str = "racer_data.db") -> Optional[pd.DataFrame]:
    """Load data from SQLite database"""
    try:
        conn = sqlite3.connect(db_path)
        query = "SELECT * FROM typing_stats"
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Error loading database: {str(e)}")
        return None

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

def extract_code_block(response: str) -> Optional[str]:
    """Extract code block from Claude's response"""
    try:
        start_idx = response.find('```python')
        if start_idx == -1:
            start_idx = response.find('```')
        if start_idx != -1:
            end_idx = response.find('```', start_idx + 3)
            if end_idx != -1:
                code = response[start_idx:end_idx].strip()
                code = code.replace('```python', '').replace('```', '').strip()
                return code
    except Exception as e:
        st.error(f"Code Extraction Failed (104): {str(e)}")
    return None

def execute_code_safely(code: str, df: pd.DataFrame) -> Tuple[bool, str, str]:
    """Execute code in a safe environment with proper setup"""
    try:
        # Initialize variable mapper and setup
        mapper = VariableMapper(df)
        setup_plotting_style()
        
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
            st.pyplot(plt.gcf())
            plt.close()
            
        return True, str(result) if result is not None else "", modified_code
        
    except Exception as e:
        return False, str(e), code

def regenerate_code_with_error(df: pd.DataFrame, question: str, error_message: str, modified_code: str = None) -> str:
    """Regenerate code with error context"""
    client = Anthropic(api_key=ANTHROPIC_API_KEY)
    prompt = custom_prompt_with_error(df, question, error_message, modified_code)
    
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
        return f"Error getting response: {str(e)}"

## PROMPTS.py

def custom_prompt(df, question: str) -> str:
    prompt = f"""
    You are writing code that will be executed with an existing DataFrame named 'df' that contains TypeRacer performance data.
    The DataFrame has the following columns:
    - 'id': unique identifier for each record
    - 'player_id': player identifier (e.g., 'tr:username')
    - 'entry_number': sequential ID tracking total games played (1 = first game, max = latest game)
    - 'speed': typing speed in words per minute (WPM)
    - 'accuracy': accuracy percentage
    - 'pts': points earned in the race
    - 'time': Unix timestamp (numerical, for calculations and plotting)
    - 'rank': player's rank in the race
    - 'game_entry': game identifier
    - 'text_id': identifier for the text typed
    - 'skill_level': skill level indicator
    - 'num_players': number of players in the race
    
    For time-based analysis, use the 'time' column directly as it's already in numerical format.
    For displaying specific dates, you can convert as needed using pd.to_datetime(df['time'], unit='s').
    
    data structure:
    {df.head().to_string()}
    
    Question: {question}
    
    Please provide a Python code solution that:
    1. Assumes the DataFrame 'df' is already loaded and available
    2. Uses the exact column names as shown above
    3. Includes necessary imports
    4. For plotting, use seaborn's set_theme() with style='whitegrid', 'darkgrid', 'white', or 'dark'
    
    Do not include sample data or DataFrame creation - work with the existing 'df'.
    """
    return prompt

  
def custom_prompt_with_error(df, question: str, error_message: str, modified_code: str = None) -> str:
    prompt = f"""
    The previous code attempt resulted in the following error:
    {error_message}

    {"The code that produced this error was:\n" + modified_code if modified_code else ""}

    Please provide a corrected Python solution for the following question:
    {question}

    The DataFrame 'df' contains TypeRacer performance data with columns:
    - 'speed': typing speed (words per minute)
    - 'accuracy': accuracy percentage
    - 'entry_number': sequential ID tracking total games played (1 = first game, max = latest game)
    - 'game_entry': game number identifier
    - 'timestamp': datetime of the race (converted from Unix timestamp)
    - 'time': original Unix timestamp
    - 'pts': points earned
    - 'rank': player's rank in the race
    - 'text_id': identifier for the text typed
    - 'skill_level': skill level indicator
    - 'num_players': number of players in the race
  
    Sample data structure:
    {df.head().to_string()}
  
    Requirements:
    1. Fix the error mentioned above
    2. Assumes the DataFrame 'df' is already loaded
    3. Uses the exact column names as shown
    4. Includes necessary imports
    5. For plotting, use seaborn's set_theme() with style='whitegrid', 'darkgrid', 'white', or 'dark'
  
    Provide only working code by addressing the error.
    """
    return prompt

## VARIABLE MAPPER.py

class VariableMapper:
    """Maps semantic variable names to actual database columns"""
    
    COMMON_MAPPINGS = {
        'speed': ['wpm', 'speed', 'words_per_minute', 'typing_speed'],
        'accuracy': ['ac', 'accuracy', 'acc', 'precision'],
        'time': ['timestamp', 'date', 'time', 'datetime'],
        'score': ['score', 'points', 'total_score'],
    }
    
    DATA_LOADING_REPLACEMENTS = [
        ("data = pd.read_clipboard()", "data = df.copy()"),
        ("data = pd.read_csv('typeracer_data.csv')", "data = df.copy()"),
        ("pd.read_clipboard()", "df.copy()"),
    ]
    
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.column_map = self._create_column_map()
    
    def _create_column_map(self) -> Dict[str, str]:
        """Create mapping from semantic names to actual column names"""
        mapping = {}
        df_columns = set(self.df.columns)
        
        for semantic_name, possible_names in self.COMMON_MAPPINGS.items():
            for col in possible_names:
                if col in df_columns:
                    mapping[semantic_name] = col
                    break
        
        return mapping
    
    def get_column(self, semantic_name: str) -> str:
        """Get actual column name from semantic name"""
        if semantic_name in self.column_map:
            return self.column_map[semantic_name]
        raise KeyError(f"No mapping found for '{semantic_name}'")
    
    def analyze_question(self, question: str) -> List[str]:
        """Analyze question text to identify required variables"""
        semantic_vars = []
        for var in self.COMMON_MAPPINGS.keys():
            if var in question.lower():
                semantic_vars.append(var)
        return semantic_vars

def preprocess_code(code: str, mapper: VariableMapper) -> Tuple[str, Dict[str, str]]:
    """Preprocess code to use correct column names"""
    modified_code = code
    used_mappings = {}
    
    # Replace data loading statements
    data_loading_replacements = {
        "data = pd.read_clipboard(sep='\\s+')" : "data = df.copy()",
        "data = pd.read_clipboard()" : "data = df.copy()",
        "data = pd.read_csv('typeracer_data.csv')" : "data = df.copy()",
        "pd.read_clipboard()" : "df.copy()"
    }
    
    for old, new in data_loading_replacements.items():
        if old in modified_code:
            modified_code = modified_code.replace(old, new)
            break
    
    # Handle the case where we're using the actual column names
    if 'wpm' in mapper.df.columns:
        used_mappings = {'speed': 'wpm', 'accuracy': 'ac'}
        
        # Replace any alternative references to these columns
        column_replacements = {
            "data['speed']": "data['wpm']",
            "data['accuracy']": "data['ac']",
            "df['speed']": "df['wpm']",
            "df['accuracy']": "df['ac']"
        }
        
        for old, new in column_replacements.items():
            modified_code = modified_code.replace(old, new)
    
    return modified_code, used_mappings

## PLOTTING style.py

def setup_plotting_style(style: str = 'whitegrid') -> None:
    """Set up consistent plotting style for all visualizations"""
    try:
        valid_styles = ['darkgrid', 'whitegrid', 'dark', 'white', 'ticks']
        if style not in valid_styles:
            style = 'whitegrid'
            
        sns.set_theme(style=style)
        plt.style.use('default')
        plt.rcParams['figure.figsize'] = [10, 6]
        plt.rcParams['figure.dpi'] = 100
    except Exception as e:
        st.warning(f"Warning: Could not set plot style. Using defaults. ({str(e)})")