import pytest
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Dict, Any

@pytest.fixture(scope="session")
def query_set() -> Dict[str, Any]:
    """Load the cricket analysis query set once for the test session"""
    query_file = Path(__file__).parent.parent / "app" / "utils" / "cricket_queries.json"
    with open(query_file, 'r') as f:
        return pytest.importorskip("json").load(f)

@pytest.fixture(scope="function")
def sample_match_data() -> pd.DataFrame:
    """Create sample match data for testing"""
    return pd.DataFrame({
        "match_id": range(1, 11),
        "date": pd.date_range(start="2024-01-01", periods=10),
        "team1": ["India"] * 5 + ["Australia"] * 5,
        "team2": ["Australia"] * 5 + ["India"] * 5,
        "winner": ["India", "Australia"] * 5,
        "margin": [45, 6, 89, 4, 56, 23, 78, 2, 34, 67],
        "ground": ["MCG", "SCG"] * 5
    })

@pytest.fixture(scope="function")
def sample_player_data() -> pd.DataFrame:
    """Create sample player statistics for testing"""
    return pd.DataFrame({
        "player_id": range(1, 6),
        "name": ["Virat Kohli", "Steve Smith", "Kane Williamson", "Joe Root", "Babar Azam"],
        "matches": [10, 12, 8, 15, 9],
        "runs": [450, 386, 289, 524, 312],
        "average": [56.25, 48.25, 41.29, 47.64, 44.57],
        "strike_rate": [150.5, 142.8, 138.2, 125.5, 118.9],
        "hundreds": [2, 1, 0, 2, 1],
        "fifties": [2, 3, 3, 2, 2]
    })

@pytest.fixture(scope="function")
def sample_ball_by_ball_data() -> pd.DataFrame:
    """Create sample ball-by-ball data for testing"""
    return pd.DataFrame({
        "match_id": [1] * 20,
        "over": [i // 6 + 1 for i in range(20)],
        "ball": [i % 6 + 1 for i in range(20)],
        "batsman": ["Virat Kohli"] * 10 + ["Rohit Sharma"] * 10,
        "bowler": ["Mitchell Starc"] * 10 + ["Pat Cummins"] * 10,
        "runs": [1, 4, 0, 6, 2, 1, 0, 0, 4, 1, 2, 0, 1, 4, 6, 0, 2, 1, 0, 4],
        "extras": [0] * 20,
        "wicket": [0] * 19 + [1],
        "dismissal_type": [""] * 19 + ["caught"]
    })

@pytest.fixture(autouse=True)
def setup_and_teardown():
    """Setup and teardown for each test"""
    # Setup
    plt.style.use('seaborn')
    
    yield
    
    # Teardown
    plt.close('all')  # Clean up any open figures 