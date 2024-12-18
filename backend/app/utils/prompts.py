# prompts.py

## test question:
question = "Plot the average speed in a smoothed line graph"

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
