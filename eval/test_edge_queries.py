"""Edge cases for query processor"""

edge_queries = [
        # Complex temporal queries
        "Compare Verstappen's performance in rainy races vs dry races in the last 5 seasons, but only counting races where he qualified in top 3",
        
        # Multi-entity nested comparisons
        "Show me races where Ferrari outperformed Red Bull in qualifying but lost the race, focusing on tire strategy differences in 2023",
        
        # Ambiguous entity references
        "Who performed better in their rookie season - Hamilton or Verstappen?",
        
        # Complex statistical analysis
        "Calculate the correlation between pit stop times and final race position for Mercedes in races where it rained during qualifying but was dry during the race",
        
        # Boundary conditions
        "Compare lap times between P1 and P20 in Monaco 2023 but only in sectors where yellow flags were shown",
        
        # Mixed temporal and conditional queries
        "Find races where a driver started outside top 10 but won the race, then compare their tire strategies with P2 finisher",
        
        # Complex multi-driver scenarios
        "Compare Verstappen, Hamilton, and Alonso's performance in the last 3 laps of races where all three finished on podium",
        
        # Hypothetical scenarios
        "How would the 2023 championship standings look if we only counted races where all drivers finished?",
        
        # Extreme data ranges
        "Compare every driver who has ever won a race in wet conditions since F1 began, ranked by win percentage",
        
        # Complex conditional aggregations
        "Show me the average gap between teammates in qualifying but only count sessions where track temperature was above 40°C and both cars made it to Q3"
    ]