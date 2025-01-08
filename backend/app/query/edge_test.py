"""Edge case testing for Q2 query processing system"""
import asyncio
import json
from datetime import datetime
from .processor import QueryProcessor

async def run_edge_tests():
    processor = QueryProcessor()
    
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
    
    results = []
    for query in edge_queries:
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
    with open(f'edge_test_results_{timestamp}.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    return results

if __name__ == "__main__":
    results = asyncio.run(run_edge_tests())
    
    # Print summary
    print("\nEdge Case Testing Results:")
    print("-" * 80)
    
    success_count = 0
    total_time = 0
    total_confidence = 0
    
    for result in results:
        print(f"\nQuery: {result['query']}")
        if 'error' in result:
            print(f"Error: {result['error']}")
            print("❌ Failed")
        else:
            success_count += 1
            total_time += result['processing_time']
            total_confidence += result['confidence']
            print(f"Endpoint: {result['endpoint']}")
            print(f"Parameters: {json.dumps(result['parameters'], indent=2)}")
            print(f"Confidence: {result['confidence']:.2f}")
            print(f"Processing Time: {result['processing_time']:.3f}s")
            print("✅ Success")
        print("-" * 80)
    
    # Print overall statistics
    print("\nOverall Statistics:")
    print(f"Success Rate: {success_count/len(results)*100:.1f}%")
    if success_count > 0:
        print(f"Average Processing Time: {total_time/success_count:.2f}s")
        print(f"Average Confidence: {total_confidence/success_count:.2f}")
    print(f"Total Queries: {len(results)}")
    print(f"Successful Queries: {success_count}")
    print(f"Failed Queries: {len(results) - success_count}") 