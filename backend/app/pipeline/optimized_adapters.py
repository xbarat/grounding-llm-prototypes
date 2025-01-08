"""
Optimized Adapters for Q2 Pipeline System
Includes caching, parallel processing, and performance optimizations.
"""

import asyncio
from dataclasses import dataclass
from typing import Dict, Any, Optional, List, Union, Tuple, TypeVar, Sequence, cast, Callable
from functools import lru_cache
from datetime import datetime
import hashlib
import json
from concurrent.futures import ThreadPoolExecutor

from ..query.processor import ProcessingResult
from ..query.models import DataRequirements

T = TypeVar('T')
R = TypeVar('R')

@dataclass
class CacheKey:
    """Cache key for query results"""
    endpoint: str
    params_hash: str
    timestamp: float

    @classmethod
    def from_query(cls, endpoint: str, params: Dict[str, Any]) -> "CacheKey":
        params_str = json.dumps(params, sort_keys=True)
        params_hash = hashlib.sha256(params_str.encode()).hexdigest()
        return cls(
            endpoint=endpoint,
            params_hash=params_hash,
            timestamp=datetime.now().timestamp()
        )

    def __hash__(self) -> int:
        return hash((self.endpoint, self.params_hash))

class CacheManager:
    """Manages caching for adapted results"""
    
    def __init__(self, max_size: int = 1000, ttl: int = 3600):
        self.cache: Dict[CacheKey, Any] = {}
        self.max_size = max_size
        self.ttl = ttl
        self._lock = asyncio.Lock()
    
    async def get(self, key: Optional[CacheKey]) -> Optional[Any]:
        """Get item from cache if not expired"""
        if key is None:
            return None
            
        async with self._lock:
            if key in self.cache:
                item = self.cache[key]
                if datetime.now().timestamp() - key.timestamp < self.ttl:
                    return item
                else:
                    del self.cache[key]
        return None
    
    async def set(self, key: Optional[CacheKey], value: Any):
        """Set item in cache with cleanup if needed"""
        if key is None:
            return
            
        async with self._lock:
            if len(self.cache) >= self.max_size:
                # Remove oldest items
                sorted_keys = sorted(self.cache.keys(), key=lambda k: k.timestamp)
                for old_key in sorted_keys[:len(self.cache) // 4]:  # Remove 25% oldest
                    del self.cache[old_key]
            self.cache[key] = value

@dataclass
class OptimizedQueryResult:
    """Enhanced query result with caching and validation"""
    endpoint: str
    params: Dict[str, Any]
    metadata: Dict[str, Any]
    source_type: str
    cache_key: Optional[CacheKey] = None
    cache_hit: bool = False
    
    @classmethod
    def from_processing_result(cls, result: ProcessingResult) -> "OptimizedQueryResult":
        """Convert ProcessingResult to OptimizedQueryResult with cache key"""
        cache_key = CacheKey.from_query(result.requirements.endpoint, result.requirements.params)
        return cls(
            endpoint=result.requirements.endpoint,
            params=result.requirements.params,
            metadata={
                "confidence": result.confidence,
                "processing_time": result.processing_time,
                "source": result.source,
                "timestamp": datetime.now().isoformat()
            },
            source_type="processing_result",
            cache_key=cache_key,
            cache_hit=False
        )
    
    def to_data_requirements(self) -> DataRequirements:
        """Convert to DataRequirements for pipeline"""
        return DataRequirements(
            endpoint=self.endpoint,
            params=self.params
        )

class ParallelProcessor:
    """Handles parallel processing of data transformations"""
    
    def __init__(self, max_workers: int = 4):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
    
    async def process_batch(self, items: List[T], process_func: Callable[[T], R]) -> Sequence[R]:
        """Process items in parallel"""
        loop = asyncio.get_event_loop()
        tasks = []
        for item in items:
            task = loop.run_in_executor(self.executor, process_func, item)
            tasks.append(task)
        results = await asyncio.gather(*tasks)
        return cast(Sequence[R], results)

@dataclass
class ParallelFetchRequest:
    """Structure for parallel fetch requests"""
    endpoint: str
    params: Dict[str, Any]
    entity_type: str  # 'driver', 'constructor', 'circuit', etc.
    entity_id: str

@dataclass
class ParallelFetchResult:
    """Results from parallel fetches"""
    success: bool
    data: Optional[Dict[str, Any]]
    entity_type: str
    entity_id: str
    error: Optional[str] = None

class ParallelFetchManager:
    """Manages parallel data fetches for multi-entity queries"""
    
    def __init__(self, max_workers: int = 4):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
    
    def create_fetch_requests(self, query_result: OptimizedQueryResult) -> List[ParallelFetchRequest]:
        """Create fetch requests based on query parameters"""
        requests = []
        params = query_result.params
        
        # Handle driver comparisons
        if isinstance(params.get('driver'), list):
            base_params = {k: v for k, v in params.items() if k != 'driver'}
            for driver in params['driver']:
                requests.append(ParallelFetchRequest(
                    endpoint=query_result.endpoint,
                    params={**base_params, 'driver': driver},
                    entity_type='driver',
                    entity_id=driver
                ))
        
        # Handle constructor comparisons
        elif isinstance(params.get('constructor'), list):
            base_params = {k: v for k, v in params.items() if k != 'constructor'}
            for constructor in params['constructor']:
                requests.append(ParallelFetchRequest(
                    endpoint=query_result.endpoint,
                    params={**base_params, 'constructor': constructor},
                    entity_type='constructor',
                    entity_id=constructor
                ))
        
        # Handle single entity
        else:
            requests.append(ParallelFetchRequest(
                endpoint=query_result.endpoint,
                params=params,
                entity_type=self._determine_entity_type(params),
                entity_id=self._get_entity_id(params)
            ))
        
        return requests
    
    def _determine_entity_type(self, params: Dict[str, Any]) -> str:
        """Determine the main entity type from params"""
        if 'driver' in params:
            return 'driver'
        elif 'constructor' in params:
            return 'constructor'
        elif 'circuit' in params:
            return 'circuit'
        return 'general'
    
    def _get_entity_id(self, params: Dict[str, Any]) -> str:
        """Get the main entity ID from params"""
        for key in ['driver', 'constructor', 'circuit']:
            if key in params:
                return str(params[key])
        return 'general'
    
    async def fetch_all(self, requests: List[ParallelFetchRequest]) -> List[ParallelFetchResult]:
        """Fetch data for all requests in parallel"""
        loop = asyncio.get_event_loop()
        tasks = []
        for request in requests:
            task = loop.run_in_executor(
                self.executor,
                self._fetch_single,
                request
            )
            tasks.append(task)
        return await asyncio.gather(*tasks)
    
    def _fetch_single(self, request: ParallelFetchRequest) -> ParallelFetchResult:
        """Fetch data for a single request"""
        try:
            # This would be replaced with actual API fetch logic
            # For now, just a placeholder
            return ParallelFetchResult(
                success=True,
                data={'params': request.params},
                entity_type=request.entity_type,
                entity_id=request.entity_id
            )
        except Exception as e:
            return ParallelFetchResult(
                success=False,
                data=None,
                entity_type=request.entity_type,
                entity_id=request.entity_id,
                error=str(e)
            )

class OptimizedQueryAdapter:
    """Enhanced adapter with caching and parallel processing"""
    
    def __init__(self):
        self.cache_manager = CacheManager()
        self.parallel_processor = ParallelProcessor()
        self.fetch_manager = ParallelFetchManager()
    
    async def adapt(self, result: Union[ProcessingResult, Dict[str, Any]]) -> OptimizedQueryResult:
        """Adapt query result with caching and parallel fetch support"""
        adapted = await self._adapt_initial(result)
        
        # Check if we need parallel fetches
        fetch_requests = self.fetch_manager.create_fetch_requests(adapted)
        if len(fetch_requests) > 1:
            # Multiple entities to fetch
            fetch_results = await self.fetch_manager.fetch_all(fetch_requests)
            adapted.metadata['parallel_fetches'] = {
                'count': len(fetch_results),
                'successful': sum(1 for r in fetch_results if r.success),
                'entities': [{'type': r.entity_type, 'id': r.entity_id} for r in fetch_results]
            }
        
        return adapted
    
    async def _adapt_initial(self, result: Union[ProcessingResult, Dict[str, Any]]) -> OptimizedQueryResult:
        """Initial adaptation of the result"""
        if isinstance(result, ProcessingResult):
            adapted = OptimizedQueryResult.from_processing_result(result)
            if cached := await self.cache_manager.get(adapted.cache_key):
                cached.cache_hit = True
                return cast(OptimizedQueryResult, cached)
            await self.cache_manager.set(adapted.cache_key, adapted)
            return adapted
        elif isinstance(result, dict):
            cache_key = CacheKey.from_query(
                result.get("endpoint", ""),
                result.get("params", {})
            )
            adapted = OptimizedQueryResult(
                endpoint=result.get("endpoint", ""),
                params=result.get("params", {}),
                metadata=result.get("metadata", {}),
                source_type="dict",
                cache_key=cache_key,
                cache_hit=False
            )
            await self.cache_manager.set(cache_key, adapted)
            return adapted
        else:
            raise ValueError(f"Unsupported result type: {type(result)}")
    
    async def adapt_batch(self, results: List[Union[ProcessingResult, Dict[str, Any]]]) -> Sequence[OptimizedQueryResult]:
        """Adapt multiple results in parallel"""
        return await self.parallel_processor.process_batch(results, self._adapt_single)
    
    def _adapt_single(self, result: Union[ProcessingResult, Dict[str, Any]]) -> OptimizedQueryResult:
        """Helper for parallel processing"""
        if isinstance(result, ProcessingResult):
            return OptimizedQueryResult.from_processing_result(result)
        elif isinstance(result, dict):
            return OptimizedQueryResult(
                endpoint=result.get("endpoint", ""),
                params=result.get("params", {}),
                metadata=result.get("metadata", {}),
                source_type="dict",
                cache_key=CacheKey.from_query(
                    result.get("endpoint", ""),
                    result.get("params", {})
                ),
                cache_hit=False
            )
        else:
            raise ValueError(f"Unsupported result type: {type(result)}")

@dataclass
class OptimizedPipelineResult:
    """Enhanced pipeline result with performance metrics"""
    success: bool
    data: Optional[Dict[str, Any]]
    error: Optional[str]
    metadata: Dict[str, Any]
    processing_time: float
    cache_hit: bool
    
    @classmethod
    def from_success(cls, data: Dict[str, Any], metadata: Dict[str, Any], processing_time: float, cache_hit: bool) -> "OptimizedPipelineResult":
        return cls(
            success=True,
            data=data,
            error=None,
            metadata=metadata,
            processing_time=processing_time,
            cache_hit=cache_hit
        )
    
    @classmethod
    def from_error(cls, error: str, metadata: Dict[str, Any], processing_time: float) -> "OptimizedPipelineResult":
        return cls(
            success=False,
            data=None,
            error=error,
            metadata=metadata,
            processing_time=processing_time,
            cache_hit=False
        )

class OptimizedResultAdapter:
    """Enhanced result adapter with performance optimizations"""
    
    def __init__(self):
        self.cache_manager = CacheManager()
    
    async def adapt_pipeline_result(self, result: Any, start_time: float) -> OptimizedPipelineResult:
        """Convert pipeline result with performance metrics"""
        processing_time = datetime.now().timestamp() - start_time
        
        if isinstance(result, dict):
            # Handle dictionary response from pipeline
            cache_key = CacheKey.from_query(
                "pipeline_result",
                {"data_hash": hashlib.sha256(str(result.get('data', {})).encode()).hexdigest()}
            )
            
            # Check cache
            if cached := await self.cache_manager.get(cache_key):
                return cast(OptimizedPipelineResult, cached)
            
            # Create new result
            pipeline_result = OptimizedPipelineResult(
                success=result.get('success', False),
                data=result.get('data'),
                error=result.get('error'),
                metadata={
                    "source": "pipeline",
                    "timestamp": datetime.now().isoformat(),
                    "cache_key": cache_key,
                    **result.get('metadata', {})
                },
                processing_time=processing_time,
                cache_hit=False
            )
            
            # Cache result
            await self.cache_manager.set(cache_key, pipeline_result)
            return pipeline_result
            
        elif hasattr(result, 'success') and hasattr(result, 'data'):
            # Handle object response
            cache_key = CacheKey.from_query(
                "pipeline_result",
                {"data_hash": hashlib.sha256(str(result.data).encode()).hexdigest()}
            )
            
            # Check cache
            if cached := await self.cache_manager.get(cache_key):
                return cast(OptimizedPipelineResult, cached)
            
            # Create new result
            pipeline_result = OptimizedPipelineResult(
                success=result.success,
                data=result.data if result.success else None,
                error=result.error if hasattr(result, "error") else None,
                metadata={
                    "source": "pipeline",
                    "timestamp": datetime.now().isoformat(),
                    "cache_key": cache_key
                },
                processing_time=processing_time,
                cache_hit=False
            )
            
            # Cache result
            await self.cache_manager.set(cache_key, pipeline_result)
            return pipeline_result
        else:
            raise ValueError(f"Unsupported result type: {type(result)}")

class OptimizedValidationAdapter:
    """Enhanced validation with parallel processing"""
    
    def __init__(self):
        self.parallel_processor = ParallelProcessor()
    
    async def validate_batch(self, results: List[Union[OptimizedQueryResult, OptimizedPipelineResult]]) -> Sequence[bool]:
        """Validate multiple results in parallel"""
        validated_results = await self.parallel_processor.process_batch(results, self._validate_single)
        return cast(Sequence[bool], validated_results)
    
    def _validate_single(self, result: Union[OptimizedQueryResult, OptimizedPipelineResult]) -> bool:
        """Validate single result"""
        if isinstance(result, OptimizedQueryResult):
            return self.validate_query_result(result)
        elif isinstance(result, OptimizedPipelineResult):
            return self.validate_pipeline_result(result)
        else:
            raise ValueError(f"Unsupported result type: {type(result)}")
    
    @staticmethod
    def validate_query_result(result: OptimizedQueryResult) -> bool:
        """Validate optimized query result"""
        return all([
            isinstance(result.endpoint, str) and result.endpoint,
            isinstance(result.params, dict),
            isinstance(result.metadata, dict),
            isinstance(result.source_type, str),
            result.cache_key is None or isinstance(result.cache_key, CacheKey),
            isinstance(result.cache_hit, bool)
        ])
    
    @staticmethod
    def validate_pipeline_result(result: OptimizedPipelineResult) -> bool:
        """Validate optimized pipeline result"""
        return all([
            isinstance(result.success, bool),
            result.data is None or isinstance(result.data, dict),
            result.error is None or isinstance(result.error, str),
            isinstance(result.metadata, dict),
            isinstance(result.processing_time, float),
            isinstance(result.cache_hit, bool)
        ]) 