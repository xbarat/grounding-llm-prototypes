"""Test runner for Q2 query processing system"""
import asyncio
import json
from datetime import datetime
from .processor import QueryProcessor

async def run_tests():
    processor = QueryProcessor()
    
    test_queries = [
        # Natural Language to Stats
        "Who won the most races in 2023?",
        "What is the fastest lap time recorded in 2023?",
        "Which team has the most podium finishes this season?",
        "How many races has Verstappen won in 2023?",
        "What is the average lap time for Hamilton in 2023?",
        "Which driver has the highest pole position percentage in 2023?",
        "How many races were won by Ferrari in 2022?",
        "Who leads the driver standings in 2023?",
        
        # Driver Comparisons
        "Compare Verstappen and Hamilton's wins in 2023",
        "Who has more podium finishes: Leclerc or Norris in 2023?",
        "Compare lap times between Verstappen and Alonso in Monaco 2023",
        "Which driver performed better in the rain: Verstappen or Russell?",
        "How does Verstappen's pole position percentage compare to Hamilton's in 2023?",
        "Compare Verstappen and Hamilton in terms of race wins and fastest laps",
        "Who had the better average qualifying position: Norris or Sainz?",
        "Compare Leclerc and Perez's DNFs in 2023",
        
        # Historical Trends
        "How has Ferrari's win rate changed since 2015?",
        "What are Red Bull's podium finishes from 2010 to 2023?",
        "Which driver has the most wins in wet races since 2000?",
        "How many wins does Hamilton have each season since 2014?",
        "Which team dominated constructors' championships from 2010 to 2020?",
        "Show Mercedes' win percentage over the last decade",
        "How have the fastest lap times changed in Monaco since 2010?",
        "What is the historical win trend of Verstappen?"
    ]
    
    results = []
    for query in test_queries:
        try:
            result = await processor.process_query(query)
            results.append({
                "query": query,
                "endpoint": result.requirements.endpoint,
                "parameters": result.requirements.params,
                "confidence": result.confidence,
                "processing_time": result.processing_time,
                "source": result.source
            })
        except Exception as e:
            results.append({
                "query": query,
                "error": str(e)
            })
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    with open(f'query_test_results_{timestamp}.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    return results

if __name__ == "__main__":
    results = asyncio.run(run_tests())
    
    # Print summary
    print("\nQuery Processing Results:")
    print("-" * 80)
    
    for result in results:
        print(f"\nQuery: {result['query']}")
        if 'error' in result:
            print(f"Error: {result['error']}")
        else:
            print(f"Endpoint: {result['endpoint']}")
            print(f"Parameters: {json.dumps(result['parameters'], indent=2)}")
            print(f"Confidence: {result['confidence']:.2f}")
            print(f"Processing Time: {result['processing_time']:.3f}s")
            print(f"Source: {result['source']}")
        print("-" * 80) 