import json
import pytest
from pathlib import Path
from app.utils.code_utils import generate_code, execute_code_safely
from app.utils.platform_fetcher import PlatformFetcher
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.axes import Axes
import seaborn as sns
from typing import Dict, Any, Optional

def validate_visualization(result: Optional[Dict[str, Any]], query_info: Dict[str, Any]) -> bool:
    """Validate if the visualization meets requirements"""
    if not result or "figure" not in result:
        return False
    
    fig = result["figure"]
    if not isinstance(fig, Figure):
        return False
    
    # Check if visualization type matches expected
    if "line_chart" in query_info["visualization_type"]:
        return any(isinstance(ax, Axes) for ax in fig.axes)
    elif "bar_chart" in query_info["visualization_type"]:
        return any(isinstance(ax, Axes) and ax.patches for ax in fig.axes)
    elif "pie_chart" in query_info["visualization_type"]:
        return any(isinstance(ax, Axes) and ax.patches for ax in fig.axes)
    elif "heat_map" in query_info["visualization_type"]:
        return any(isinstance(ax, Axes) and ax.collections for ax in fig.axes)
    elif "wagon_wheel" in query_info["visualization_type"]:
        return any(isinstance(ax, Axes) and ax.patches for ax in fig.axes)
    elif "radar_chart" in query_info["visualization_type"]:
        return any(isinstance(ax, Axes) and ax.patches for ax in fig.axes)
    elif "timeline" in query_info["visualization_type"]:
        return any(isinstance(ax, Axes) for ax in fig.axes)
    elif "box_plot" in query_info["visualization_type"]:
        return any(isinstance(ax, Axes) and ax.artists for ax in fig.axes)
    elif "scatter_plot" in query_info["visualization_type"]:
        return any(isinstance(ax, Axes) and ax.collections for ax in fig.axes)
    
    return True

def prepare_test_data(query_info: Dict[str, Any], 
                     sample_match_data: pd.DataFrame,
                     sample_player_data: pd.DataFrame,
                     sample_ball_by_ball_data: pd.DataFrame) -> pd.DataFrame:
    """Prepare test data based on query requirements"""
    data = {}
    
    for required in query_info["required_data"]:
        if required == "player_stats":
            data.update({"player_stats": sample_player_data})
        elif required == "match_data":
            data.update({"match_data": sample_match_data})
        elif required == "ball_by_ball":
            data.update({"ball_by_ball": sample_ball_by_ball_data})
        elif required == "match_format":
            # Add format information to match data
            format_data = sample_match_data.copy()
            format_data["format"] = ["T20"] * len(format_data)
            data.update({"format_data": format_data})
    
    # Convert to single DataFrame if possible
    if len(data) == 1:
        return pd.DataFrame(list(data.values())[0])
    else:
        # Merge relevant DataFrames based on common keys
        result_df = pd.DataFrame()
        for key, df in data.items():
            if result_df.empty:
                result_df = df
            else:
                common_cols = set(result_df.columns) & set(df.columns)
                if common_cols:
                    result_df = result_df.merge(df, on=list(common_cols), how='outer')
                else:
                    # If no common columns, use cross join
                    result_df = result_df.assign(key=1).merge(df.assign(key=1), on='key').drop('key', axis=1)
        return result_df

@pytest.mark.parametrize("category", ["player_performance", "match_insights", "venue_analysis"])
def test_category_queries(category: str,
                        query_set: Dict[str, Any],
                        sample_match_data: pd.DataFrame,
                        sample_player_data: pd.DataFrame,
                        sample_ball_by_ball_data: pd.DataFrame) -> None:
    """Test queries in specific categories"""
    category_info = query_set["categories"][category]
    
    for query in category_info["queries"]:
        print(f"\nTesting query: {query['text']}")
        
        # Prepare test data
        df = prepare_test_data(
            query,
            sample_match_data,
            sample_player_data,
            sample_ball_by_ball_data
        )
        
        # Generate visualization code
        code_response = generate_code(df, query["text"])
        assert code_response is not None, f"Failed to generate code for query: {query['id']}"
        
        # Execute code
        success, result, modified_code = execute_code_safely(code_response, df)
        assert success, f"Code execution failed for query: {query['id']}"
        
        # Validate visualization
        assert validate_visualization(result, query), f"Visualization validation failed for query: {query['id']}"
        
        # Check if required metrics are present
        if isinstance(result.get("result"), dict):
            for metric in query["metrics"]:
                assert any(metric in key.lower() for key in result["result"].keys()), \
                    f"Required metric {metric} not found in results for query: {query['id']}"

def test_visualization_types(query_set: Dict[str, Any],
                           sample_player_data: pd.DataFrame) -> None:
    """Test support for all visualization types"""
    viz_types = query_set["metadata"]["supported_visualizations"]
    
    for viz_type in viz_types:
        print(f"\nTesting visualization type: {viz_type}")
        
        # Create a simple test query for each visualization type
        test_query = f"Create a {viz_type} showing runs scored by top 5 batsmen"
        
        # Use sample player data for visualization tests
        df = sample_player_data.copy()
        
        code_response = generate_code(df, test_query)
        success, result, _ = execute_code_safely(code_response, df)
        
        assert success, f"Failed to create {viz_type} visualization"
        assert result.get("figure") is not None, f"No figure generated for {viz_type}"

def test_complexity_handling(query_set: Dict[str, Any],
                           sample_match_data: pd.DataFrame,
                           sample_player_data: pd.DataFrame,
                           sample_ball_by_ball_data: pd.DataFrame) -> None:
    """Test handling of queries with different complexity levels"""
    for category in query_set["categories"].values():
        for query in category["queries"]:
            if query["complexity"] == "high":
                print(f"\nTesting high-complexity query: {query['text']}")
                
                # Prepare test data
                df = prepare_test_data(
                    query,
                    sample_match_data,
                    sample_player_data,
                    sample_ball_by_ball_data
                )
                
                code_response = generate_code(df, query["text"])
                success, result, _ = execute_code_safely(code_response, df)
                
                assert success, f"High-complexity query failed: {query['id']}"
                assert result is not None, f"No result for high-complexity query: {query['id']}"

if __name__ == "__main__":
    print("Running cricket analysis tests...")
    pytest.main([__file__, "-v"]) 