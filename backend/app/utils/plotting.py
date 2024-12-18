import matplotlib
matplotlib.use('Agg')  # Set non-interactive backend before importing pyplot
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, Optional

def setup_plotting_style():
    """Setup consistent plotting style"""
    plt.style.use('dark_background')
    sns.set_theme(style='darkgrid')
    plt.rcParams['figure.figsize'] = [12, 6]
    plt.rcParams['figure.dpi'] = 100
    plt.rcParams['savefig.dpi'] = 100
    plt.rcParams['font.size'] = 12
    plt.rcParams['axes.titlesize'] = 14
    plt.rcParams['axes.labelsize'] = 12
    plt.rcParams['xtick.labelsize'] = 10
    plt.rcParams['ytick.labelsize'] = 10

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
