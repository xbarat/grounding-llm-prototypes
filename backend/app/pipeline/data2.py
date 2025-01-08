"""
Data Pipeline with parallel fetch support for Q2 system.
"""

import asyncio
from typing import Dict, Any, List, Optional, Union, cast
import pandas as pd
from datetime import datetime

class DataPipeline:
    """Pipeline for processing F1 data requests"""
    
    async def process(self, requirements: Any) -> Dict[str, Any]:
        """Process data requirements with parallel fetch support"""
        try:
            # Check if this is a multi-entity request
            params = requirements.params
            if isinstance(params.get('driver'), list) or isinstance(params.get('constructor'), list):
                return await self._process_parallel(requirements)
            else:
                return await self._process_single(requirements)
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'data': None
            }
    
    async def _process_parallel(self, requirements: Any) -> Dict[str, Any]:
        """Process multiple entities in parallel"""
        params = requirements.params
        base_params = {k: v for k, v in params.items()}
        
        # Determine what we're comparing
        if isinstance(params.get('driver'), list):
            entities = params['driver']
            entity_type = 'driver'
        elif isinstance(params.get('constructor'), list):
            entities = params['constructor']
            entity_type = 'constructor'
        else:
            raise ValueError("No parallel entities found")
        
        # Create tasks for each entity
        tasks = []
        for entity in entities:
            entity_params = base_params.copy()
            entity_params[entity_type] = entity
            single_req = type(requirements)(
                endpoint=requirements.endpoint,
                params=entity_params
            )
            tasks.append(self._process_single(single_req))
        
        # Execute all tasks in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Merge results
        success = True
        merged_data = {'results': pd.DataFrame()}
        errors = []
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                success = False
                errors.append(f"Error processing {entities[i]}: {str(result)}")
                continue
                
            result_dict = cast(Dict[str, Any], result)
            if not result_dict.get('success', False):
                success = False
                errors.append(f"Failed to process {entities[i]}: {result_dict.get('error', 'Unknown error')}")
            else:
                # Merge DataFrames
                result_data = result_dict.get('data', {})
                if isinstance(result_data, dict):
                    df = result_data.get('results', pd.DataFrame())
                    if not df.empty:
                        if merged_data['results'].empty:
                            merged_data['results'] = df
                        else:
                            merged_data['results'] = pd.concat([merged_data['results'], df], ignore_index=True)
        
        return {
            'success': success and not merged_data['results'].empty,
            'data': merged_data if not merged_data['results'].empty else None,
            'error': '; '.join(errors) if errors else None,
            'metadata': {
                'entity_type': entity_type,
                'entities': entities,
                'timestamp': datetime.now().isoformat()
            }
        }
    
    async def _process_single(self, requirements: Any) -> Dict[str, Any]:
        """Process a single entity request"""
        try:
            # Extract parameters
            endpoint = requirements.endpoint
            params = requirements.params
            
            # Normalize parameters
            if 'driver' in params and isinstance(params['driver'], str):
                params['driver'] = params['driver'].replace('_', ' ')
            if 'constructor' in params and isinstance(params['constructor'], str):
                params['constructor'] = params['constructor'].replace('_', ' ')
            if 'circuit' in params and isinstance(params['circuit'], str):
                params['circuit'] = params['circuit'].replace('_', ' ')
            
            # Fetch and process data
            # This is a placeholder - actual implementation would fetch from API
            data = {'results': pd.DataFrame()}  # Placeholder
            
            return {
                'success': True,
                'data': data,
                'error': None,
                'metadata': {
                    'endpoint': endpoint,
                    'params': params,
                    'timestamp': datetime.now().isoformat()
                }
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'data': None,
                'metadata': {
                    'endpoint': requirements.endpoint,
                    'timestamp': datetime.now().isoformat()
                }
            }
