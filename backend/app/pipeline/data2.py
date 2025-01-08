"""Enhanced Data Pipeline with support for historical and complex queries"""

import asyncio
from typing import Dict, Any, List, Optional, Union, cast
import pandas as pd
from datetime import datetime
from ..query.models import DataRequirements

class DataRequirementsSplitter:
    """Splits complex requirements into atomic fetchable units"""
    
    @staticmethod
    def split_historical(requirements: Any) -> List[Dict[str, Any]]:
        """Split historical query into year-by-year requirements"""
        params = requirements.params
        split_reqs = []
        
        # Extract time range
        start_year = None
        end_year = datetime.now().year
        
        # Parse various time formats
        if isinstance(params.get('season'), list):
            years = params['season']
            if years:
                start_year = min(int(y) for y in years)
                end_year = max(int(y) for y in years)
        elif 'since' in str(params.get('season')):
            start_year = int(str(params['season']).split('since')[-1].strip())
        elif 'last decade' in str(params.get('season')):
            start_year = end_year - 10
        
        if not start_year:
            start_year = end_year - 5  # Default to last 5 years
            
        # Create year-by-year requirements
        base_params = {k: v for k, v in params.items() if k != 'season'}
        for year in range(start_year, end_year + 1):
            split_reqs.append({
                'endpoint': requirements.endpoint,
                'params': {**base_params, 'season': str(year)},
                'metadata': {'year': year}
            })
        
        return split_reqs

    @staticmethod
    def split_career(requirements: Any) -> List[Dict[str, Any]]:
        """Split career comparison into multiple metric requirements"""
        params = requirements.params
        split_reqs = []
        
        # Define metrics to fetch
        metrics = [
            {'endpoint': '/api/f1/drivers', 'key': 'career_stats'},
            {'endpoint': '/api/f1/results', 'key': 'race_results'},
            {'endpoint': '/api/f1/qualifying', 'key': 'qualifying_results'},
            {'endpoint': '/api/f1/standings', 'key': 'championship_standings'}
        ]
        
        # Create requirements for each metric
        for metric in metrics:
            split_reqs.append({
                'endpoint': metric['endpoint'],
                'params': params,
                'metadata': {'metric': metric['key']}
            })
        
        return split_reqs

class DataPipeline:
    """Enhanced pipeline for processing F1 data requests"""
    
    async def process(self, requirements: Any) -> Dict[str, Any]:
        """Process data requirements with support for complex queries"""
        try:
            # Check if this is a complex query requiring multiple fetches
            if self._is_historical_query(requirements):
                return await self._process_historical(requirements)
            elif self._is_career_query(requirements):
                return await self._process_career(requirements)
            elif self._is_multi_entity_query(requirements):
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
    
    def _is_historical_query(self, requirements: Any) -> bool:
        """Check if query requires historical data processing"""
        params = requirements.params
        if isinstance(params.get('season'), list) and len(params['season']) > 1:
            return True
        season_str = str(params.get('season', ''))
        return any(term in season_str.lower() for term in ['since', 'from', 'decade', 'between'])
    
    def _is_career_query(self, requirements: Any) -> bool:
        """Check if query requires career-wide data processing"""
        params = requirements.params
        query_str = str(params.get('query', '')).lower()
        return any(term in query_str for term in ['career', 'all time', 'lifetime', 'overall'])
    
    def _is_multi_entity_query(self, requirements: Any) -> bool:
        """Check if query involves multiple entities"""
        params = requirements.params
        return (isinstance(params.get('driver'), list) or 
                isinstance(params.get('constructor'), list))
    
    async def _process_historical(self, requirements: Any) -> Dict[str, Any]:
        """Process historical query with year-by-year data"""
        split_reqs = DataRequirementsSplitter.split_historical(requirements)
        
        # Process each year in parallel
        tasks = []
        for req in split_reqs:
            single_req = type(requirements)(
                endpoint=req['endpoint'],
                params=req['params']
            )
            tasks.append(self._process_single(single_req))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Merge results with year tracking
        success = True
        merged_data = {'results': pd.DataFrame()}
        errors = []
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                success = False
                errors.append(f"Error processing year {split_reqs[i]['metadata']['year']}: {str(result)}")
                continue
            
            result_dict = cast(Dict[str, Any], result)
            if not result_dict.get('success', False):
                success = False
                errors.append(f"Failed to process year {split_reqs[i]['metadata']['year']}: {result_dict.get('error', 'Unknown error')}")
            else:
                result_data = result_dict.get('data', {})
                if isinstance(result_data, dict):
                    df = result_data.get('results', pd.DataFrame())
                    if not df.empty:
                        df['year'] = split_reqs[i]['metadata']['year']
                        if merged_data['results'].empty:
                            merged_data['results'] = df
                        else:
                            merged_data['results'] = pd.concat([merged_data['results'], df], ignore_index=True)
        
        return {
            'success': success and not merged_data['results'].empty,
            'data': merged_data if not merged_data['results'].empty else None,
            'error': '; '.join(errors) if errors else None,
            'metadata': {
                'query_type': 'historical',
                'years_processed': len(split_reqs),
                'timestamp': datetime.now().isoformat()
            }
        }
    
    async def _process_career(self, requirements: Any) -> Dict[str, Any]:
        """Process career-wide query with multiple metrics"""
        split_reqs = DataRequirementsSplitter.split_career(requirements)
        
        # Process each metric in parallel
        tasks = []
        for req in split_reqs:
            single_req = type(requirements)(
                endpoint=req['endpoint'],
                params=req['params']
            )
            tasks.append(self._process_single(single_req))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Merge results with metric tracking
        success = True
        merged_data = {}
        errors = []
        
        for i, result in enumerate(results):
            metric = split_reqs[i]['metadata']['metric']
            if isinstance(result, Exception):
                success = False
                errors.append(f"Error processing {metric}: {str(result)}")
                continue
            
            result_dict = cast(Dict[str, Any], result)
            if not result_dict.get('success', False):
                success = False
                errors.append(f"Failed to process {metric}: {result_dict.get('error', 'Unknown error')}")
            else:
                result_data = result_dict.get('data', {})
                if isinstance(result_data, dict):
                    merged_data[metric] = result_data.get('results', pd.DataFrame())
        
        return {
            'success': success and any(not df.empty for df in merged_data.values()),
            'data': {'results': merged_data} if merged_data else None,
            'error': '; '.join(errors) if errors else None,
            'metadata': {
                'query_type': 'career',
                'metrics_processed': len(split_reqs),
                'timestamp': datetime.now().isoformat()
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
                result_data = result_dict.get('data', {})
                if isinstance(result_data, dict):
                    df = result_data.get('results', pd.DataFrame())
                    if not df.empty:
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
