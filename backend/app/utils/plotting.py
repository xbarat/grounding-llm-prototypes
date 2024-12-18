import seaborn as sns
import matplotlib.pyplot as plt
from typing import Dict, Optional

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
        print(f"Warning: Could not set plot style. Using defaults. ({str(e)})")

def get_player_stats(player_id: str) -> Optional[Dict]:
    """Get player statistics for dashboard"""
    try:
        # This is a placeholder. You'll need to implement the actual stats gathering
        # based on your database and requirements
        stats = {
            "total_races": 0,
            "average_speed": 0,
            "max_speed": 0,
            "average_accuracy": 0,
            "total_points": 0
        }
        return stats
    except Exception as e:
        print(f"Error getting player stats: {str(e)}")
        return None
