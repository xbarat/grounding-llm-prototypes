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
                'data': None,
                'metadata': {
                    'timestamp': datetime.now().isoformat(),
                    'error_type': type(e).__name__
                }
            }
    
    async def _process_parallel(self, requirements: Any) -> Dict[str, Any]:
        """Process multiple entities in parallel with batching"""
        params = requirements.params
        base_params = {k: v for k, v in params.items()}
        
        # Determine what we're comparing
        entities = []
        entity_type = None
        
        if isinstance(params.get('driver'), list):
            entities = params['driver']
            entity_type = 'driver'
            del base_params['driver']
        elif isinstance(params.get('constructor'), list):
            entities = params['constructor']
            entity_type = 'constructor'
            del base_params['constructor']
        
        if not entities or not entity_type:
            return {
                'success': False,
                'error': "No parallel entities found",
                'data': None,
                'metadata': {
                    'timestamp': datetime.now().isoformat()
                }
            }
        
        # Process entities in batches
        batch_size = 4
        all_results = []
        
        for i in range(0, len(entities), batch_size):
            batch = entities[i:i + batch_size]
            batch_tasks = []
            
            for entity in batch:
                entity_params = base_params.copy()
                entity_params[entity_type] = entity
                single_req = type(requirements)(
                    endpoint=requirements.endpoint,
                    params=entity_params
                )
                batch_tasks.append(self._process_single(single_req))
            
            # Execute batch with retry logic
            try:
                batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
                all_results.extend(batch_results)
            except Exception as e:
                print(f"Error processing batch {i//batch_size + 1}: {str(e)}")
        
        # Merge results
        success = True
        merged_data = {'results': pd.DataFrame()}
        errors = []
        
        for i, result in enumerate(all_results):
            if isinstance(result, Exception):
                success = False
                errors.append(f"Error processing {entities[i]}: {str(result)}")
                continue
            
            result_dict = cast(Dict[str, Any], result)
            if not result_dict.get('success', False):
                success = False
                errors.append(f"Failed to process {entities[i]}: {result_dict.get('error', 'Unknown error')}")
            else:
                # Merge DataFrames with entity information
                result_data = result_dict.get('data', {})
                if isinstance(result_data, dict):
                    df = result_data.get('results', pd.DataFrame())
                    if not df.empty:
                        # Add entity information to DataFrame
                        df[entity_type] = entities[i]
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
                'timestamp': datetime.now().isoformat(),
                'batch_size': batch_size,
                'total_batches': (len(entities) + batch_size - 1) // batch_size
            }
        }
    
    async def _process_single(self, requirements: Any) -> Dict[str, Any]:
        """Process a single entity request with retries"""
        max_retries = 3
        retry_delay = 1.0  # seconds
        
        for attempt in range(max_retries):
            try:
                # Extract parameters
                endpoint = requirements.endpoint
                params = self._normalize_params(requirements.params)
                
                # Fetch and process data
                # This is a placeholder - actual implementation would fetch from API
                data = await self._fetch_data(endpoint, params)
                
                if data and isinstance(data.get('results'), pd.DataFrame):
                    return {
                        'success': True,
                        'data': data,
                        'error': None,
                        'metadata': {
                            'endpoint': endpoint,
                            'params': params,
                            'timestamp': datetime.now().isoformat(),
                            'attempt': attempt + 1
                        }
                    }
                
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay * (attempt + 1))
                    continue
                
                return {
                    'success': False,
                    'error': 'No data retrieved',
                    'data': None,
                    'metadata': {
                        'endpoint': endpoint,
                        'params': params,
                        'timestamp': datetime.now().isoformat(),
                        'attempt': attempt + 1
                    }
                }
                
            except Exception as e:
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay * (attempt + 1))
                    continue
                
                return {
                    'success': False,
                    'error': str(e),
                    'data': None,
                    'metadata': {
                        'endpoint': requirements.endpoint,
                        'timestamp': datetime.now().isoformat(),
                        'attempt': attempt + 1,
                        'error_type': type(e).__name__
                    }
                }
        
        # This is the fallback return in case all retries fail
        return {
            'success': False,
            'error': 'Max retries exceeded',
            'data': None,
            'metadata': {
                'endpoint': requirements.endpoint,
                'timestamp': datetime.now().isoformat(),
                'max_retries': max_retries
            }
        }
    
    def _normalize_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize parameters handling both single values and lists"""
        normalized = {}
        for key, value in params.items():
            if isinstance(value, str):
                normalized[key] = value.replace('_', ' ')
            elif isinstance(value, list):
                normalized[key] = [v.replace('_', ' ') if isinstance(v, str) else v for v in value]
            else:
                normalized[key] = value
        return normalized
    
    async def _fetch_data(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Placeholder for actual API fetch implementation"""
        # This is where you would implement the actual API call
        # For now, return a mock DataFrame
        df = pd.DataFrame({
            'position': [1, 2, 3],
            'points': [25, 18, 15],
            'time': ['1:30.000', '1:30.500', '1:31.000']
        })
        return {'results': df}
