"""Test query sets for F1 data pipeline testing"""

from typing import Dict, List, NamedTuple
from dataclasses import dataclass

@dataclass
class QueryCategory:
    name: str
    description: str
    queries: List[str]

class TestQueries:
    """Collection of test queries organized by category"""
    
    BASIC_STATS = QueryCategory(
        name="Natural Language to Stats",
        description="Basic statistical queries about F1 races and drivers",
        queries=[
            "Who won the most races in 2023?",
            "What is the fastest lap time recorded in 2023?",
            "Which team has the most podium finishes this season?",
            "How many races has Verstappen won in 2023?",
            "What is the average lap time for Hamilton in 2023?",
            "Which driver has the highest pole position percentage in 2023?",
            "How many races were won by Ferrari in 2022?",
            "Who leads the driver standings in 2023?"
        ]
    )

    DRIVER_COMPARISONS = QueryCategory(
        name="Driver Comparisons",
        description="Comparative analysis between F1 drivers",
        queries=[
            "Compare Verstappen and Hamilton's wins in 2023",
            "Who has more podium finishes: Leclerc or Norris in 2023?",
            "Compare lap times between Verstappen and Alonso in Monaco 2023",
            "Which driver performed better in the rain: Verstappen or Russell?",
            "How does Verstappen's pole position percentage compare to Hamilton's in 2023?",
            "Compare Verstappen and Hamilton in terms of race wins and fastest laps",
            "Who had the better average qualifying position: Norris or Sainz?",
            "Compare Leclerc and Perez's DNFs in 2023"
        ]
    )

    HISTORICAL_TRENDS = QueryCategory(
        name="Historical Trends",
        description="Long-term analysis of F1 statistics",
        queries=[
            "How has Ferrari's win rate changed since 2015?",
            "What are Red Bull's podium finishes from 2010 to 2023?",
            "Which driver has the most wins in wet races since 2000?",
            "How many wins does Hamilton have each season since 2014?",
            "Which team dominated constructors' championships from 2010 to 2020?",
            "Show Mercedes' win percentage over the last decade",
            "How have the fastest lap times changed in Monaco since 2010?",
            "What is the historical win trend of Verstappen?"
        ]
    )

    SPECIFIC_ANALYSIS = QueryCategory(
        name="Specific Driver Analysis",
        description="Detailed analysis of specific driver performance",
        queries=[
            "How has Max Verstappen's rank changed across the last 10 seasons?",
            "How does Lewis Hamilton compare to Charles Leclerc in terms of wins, podiums, and points over the last 5 seasons?",
            "What is Fernando Alonso's performance (wins, fastest laps, podiums) on Circuit Silverstone over the past seasons?",
            "What were Sergio Pérez's key stats (wins, poles, fastest laps) for each season?",
            "What is Carlos Sainz Jr.'s average qualifying position across all races in a given season?",
            "How does Lando Norris perform in wet vs. dry conditions (wins, DNFs, lap times)?",
            "How does George Russell compare to his teammate in points, podiums, and wins for the last 3 seasons?",
            "How has Oscar Piastri performed in races with safety car interventions (positions gained/lost)?",
            "What is Valtteri Bottas's average lap time consistency across all races in a season?",
            "How often does Charles Leclerc finish in the top 5 after starting outside the top 10?"
        ]
    )

    CHALLENGING_QUERIES = QueryCategory(
        name="Challenging Queries",
        description="Complex or ambiguous queries requiring sophisticated analysis",
        queries=[
            "Which driver performs best in the rain?",
            "Who is the fastest driver in Monaco?",
            "What team has improved the most over the last 5 seasons?",
            "Which constructor is the best on street circuits?",
            "What is Hamilton's success rate at circuits where Verstappen also won?",
            "Which races had the closest finishes in F1 history?",
            "How does Ferrari perform compared to Red Bull in wet conditions?",
            "What is the average finishing position for Alonso in 2023?",
            "Which races had safety cars deployed in 2022?",
            "Who are the best drivers on tire conservation strategies?"
        ]
    )

    @classmethod
    def get_all_categories(cls) -> List[QueryCategory]:
        """Get all query categories"""
        return [
            cls.BASIC_STATS,
            cls.DRIVER_COMPARISONS,
            cls.HISTORICAL_TRENDS,
            cls.SPECIFIC_ANALYSIS,
            cls.CHALLENGING_QUERIES
        ]

    @classmethod
    def get_all_queries(cls) -> List[str]:
        """Get all queries as a flat list"""
        return [
            query
            for category in cls.get_all_categories()
            for query in category.queries
        ]

    @classmethod
    def get_queries_by_category(cls, category_name: str) -> List[str]:
        """Get queries for a specific category"""
        for category in cls.get_all_categories():
            if category.name.lower() == category_name.lower():
                return category.queries
        raise ValueError(f"Category '{category_name}' not found")

    @classmethod
    def get_random_queries(cls, n: int = 10) -> List[str]:
        """Get n random queries from all categories"""
        import random
        all_queries = cls.get_all_queries()
        return random.sample(all_queries, min(n, len(all_queries))) 