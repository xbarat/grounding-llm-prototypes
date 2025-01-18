"""Checklist and Quality Tests for F1 Query System"""

import asyncio
from typing import Dict, Any, List
from datetime import datetime
import pandas as pd

class ComponentCheck:
    """Individual component checks"""
    
    @staticmethod
    async def check_f1_endpoints():
        """Check F1 Endpoints Configuration"""
        checks = {
            "endpoint_templates_exist": False,
            "build_endpoint_works": False,
            "valid_parameter_substitution": False
        }
        try:
            from backend.app.api.f1_endpoints import F1Endpoints, build_endpoint
            
            # Check endpoint templates
            checks["endpoint_templates_exist"] = (
                hasattr(F1Endpoints, 'DRIVERS') and
                hasattr(F1Endpoints, 'RESULTS')
            )
            
            # Test endpoint building
            test_endpoint = build_endpoint('DRIVERS.specific', driverid='max_verstappen')
            checks["build_endpoint_works"] = test_endpoint == '/drivers/max_verstappen'
            
            # Test parameter substitution
            test_complex = build_endpoint('RESULTS.race', year='2023', round='1')
            checks["valid_parameter_substitution"] = test_complex == '/2023/1/results'
            
        except Exception as e:
            print(f"F1Endpoints Check Error: {str(e)}")
        
        return checks

    @staticmethod
    async def check_f1_api():
        """Check F1 API Functionality"""
        checks = {
            "api_connection_works": False,
            "rate_limiting_works": False,
            "response_processing_works": False
        }
        try:
            from backend.app.api.f1_api import fetch_f1_data
            
            # Test API connection
            response = await fetch_f1_data('/drivers/max_verstappen')
            checks["api_connection_works"] = response['success']
            
            # Test rate limiting (multiple quick requests)
            responses = await asyncio.gather(*[
                fetch_f1_data('/current/last/results')
                for _ in range(3)
            ])
            checks["rate_limiting_works"] = all(r['success'] for r in responses)
            
            # Check response processing
            checks["response_processing_works"] = (
                'data' in response and 
                isinstance(response['data'], pd.DataFrame)
            )
            
        except Exception as e:
            print(f"F1 API Check Error: {str(e)}")
        
        return checks

    @staticmethod
    async def check_data_pipeline():
        """Check Data Pipeline Processing"""
        checks = {
            "processes_single_query": False,
            "processes_historical": False,
            "processes_comparison": False,
            "error_handling_works": False
        }
        try:
            from backend.app.pipeline.data2 import DataPipeline
            from backend.app.query.models import DataRequirements
            
            pipeline = DataPipeline()
            
            # Test single query
            req_single = DataRequirements(
                endpoint='DRIVERS.year',
                params={'year': '2023'}
            )
            result_single = await pipeline.process(req_single)
            checks["processes_single_query"] = result_single['success']
            
            # Test historical query
            req_historical = DataRequirements(
                endpoint='RESULTS.race',
                params={'year': '2023', 'round': '1'}
            )
            result_hist = await pipeline.process(req_historical)
            checks["processes_historical"] = result_hist['success']
            
            # Test comparison query
            req_comparison = DataRequirements(
                endpoint='DRIVERS.year',
                params={'year': '2023', 'driver': ['max_verstappen', 'lewis_hamilton']}
            )
            result_comparison = await pipeline.process(req_comparison)
            checks["processes_comparison"] = result_comparison['success']
            
            # Test error handling
            req_invalid = DataRequirements(
                endpoint='INVALID',
                params={}
            )
            result_invalid = await pipeline.process(req_invalid)
            checks["error_handling_works"] = not result_invalid['success']
            
        except Exception as e:
            print(f"Data Pipeline Check Error: {str(e)}")
        
        return checks

class ConnectionCheck:
    """Check connections between components"""
    
    @staticmethod
    async def check_endpoint_to_api():
        """Check if endpoints correctly connect to API"""
        from backend.app.api.f1_endpoints import build_endpoint
        from backend.app.api.f1_api import fetch_f1_data
        
        endpoint = build_endpoint('DRIVERS.year', year='2023')
        response = await fetch_f1_data(endpoint)
        
        return {
            "endpoint_builds_correctly": endpoint.startswith('/'),
            "api_accepts_endpoint": response['success']
        }

    @staticmethod
    async def check_api_to_pipeline():
        """Check if API data flows into pipeline"""
        from backend.app.pipeline.data2 import DataPipeline
        from backend.app.query.models import DataRequirements
        
        pipeline = DataPipeline()
        requirements = DataRequirements(
            endpoint='DRIVERS.year',
            params={'year': '2023'}
        )
        
        result = await pipeline.process(requirements)
        return {
            "pipeline_processes_api_data": result['success'],
            "data_properly_transformed": 'data' in result
        }

async def run_quality_check():
    """Run all quality checks"""
    print("=== Starting F1 Query System Quality Check ===")
    print(f"Timestamp: {datetime.now()}\n")
    
    # Component Checks
    print("1. Checking Individual Components:")
    component_results = {
        "F1 Endpoints": await ComponentCheck.check_f1_endpoints(),
        "F1 API": await ComponentCheck.check_f1_api(),
        "Data Pipeline": await ComponentCheck.check_data_pipeline()
    }
    
    # Connection Checks
    print("\n2. Checking Component Connections:")
    connection_results = {
        "Endpoint → API": await ConnectionCheck.check_endpoint_to_api(),
        "API → Pipeline": await ConnectionCheck.check_api_to_pipeline()
    }
    
    # Print Results
    print("\n=== Check Results ===")
    print("\nComponent Checks:")
    for component, checks in component_results.items():
        print(f"\n{component}:")
        for check, result in checks.items():
            print(f"  - {check}: {'✓' if result else '✗'}")
    
    print("\nConnection Checks:")
    for connection, checks in connection_results.items():
        print(f"\n{connection}:")
        for check, result in checks.items():
            print(f"  - {check}: {'✓' if result else '✗'}")

if __name__ == "__main__":
    asyncio.run(run_quality_check()) 