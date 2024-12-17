import pandas as pd
from typing import Dict, List, Tuple

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