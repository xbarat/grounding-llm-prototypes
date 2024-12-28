"""
Pipeline validation module.

This module provides validation functions for each stage of the data pipeline.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
import pandas as pd
from pydantic import BaseModel, field_validator, model_validator

logger = logging.getLogger(__name__)

class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass

class RawDataValidator(BaseModel):
    """Validator for raw data from platform APIs"""
    platform: str
    timestamp: datetime
    data: Dict[str, Any]

    @field_validator('platform')
    def validate_platform(cls, v):
        if v not in ['typeracer', 'f1']:
            raise ValidationError(f'Invalid platform: {v}')
        return v

    @field_validator('data')
    def validate_data(cls, v, info):
        platform = info.data.get('platform')
        if platform == 'f1':
            if not isinstance(v, dict) or 'MRData' not in v or not v['MRData']:
                raise ValidationError('Invalid F1 data format')
        elif platform == 'typeracer':
            if not isinstance(v, dict) or not any(k in v for k in ['wpm', 'accuracy']):
                raise ValidationError('Invalid TypeRacer data format')
        return v

class NormalizedDataValidator(BaseModel):
    """Validator for normalized data"""
    platform: str
    timestamp: datetime
    metrics: Dict[str, Any]
    metadata: Optional[Dict[str, Any]]

    @field_validator('metrics')
    def validate_metrics(cls, v, info):
        platform = info.data.get('platform')
        if platform == 'f1':
            # Check if this is race data or standings data
            if 'races' in v:
                # Race data validation
                required_fields = ['races', 'circuits', 'drivers', 'constructors']
                if not all(field in v for field in required_fields):
                    raise ValidationError(f'Missing required F1 race fields: {required_fields}')
                
                # Validate data types
                if not isinstance(v['races'], list):
                    raise ValidationError('F1 races must be a list')
            else:
                # Standings data validation
                required_fields = ['drivers', 'constructors', 'driver_standings']
                if not all(field in v for field in required_fields):
                    raise ValidationError(f'Missing required F1 standings fields: {required_fields}')
                
                # Validate data types
                if not isinstance(v['driver_standings'], list):
                    raise ValidationError('F1 driver standings must be a list')
                if not isinstance(v['drivers'], list):
                    raise ValidationError('F1 drivers must be a list')
                if not isinstance(v['constructors'], list):
                    raise ValidationError('F1 constructors must be a list')
                
                # Validate standings data
                for standing in v['driver_standings']:
                    if not all(k in standing for k in ['driver_id', 'points', 'position', 'wins']):
                        raise ValidationError('Invalid driver standing format')
                    if not isinstance(standing['points'], (int, float)):
                        raise ValidationError('Driver standing points must be numeric')
                    if not isinstance(standing['position'], int):
                        raise ValidationError('Driver standing position must be an integer')
                    if not isinstance(standing['wins'], int):
                        raise ValidationError('Driver standing wins must be an integer')

        elif platform == 'typeracer':
            required_fields = ['wpm', 'accuracy', 'session_id']
            if not all(field in v for field in required_fields):
                raise ValidationError(f'Missing required TypeRacer fields: {required_fields}')
            
            # Validate data types
            if not isinstance(v.get('wpm'), (int, float)):
                raise ValidationError('TypeRacer WPM must be a number')
            if not isinstance(v.get('accuracy'), (int, float)):
                raise ValidationError('TypeRacer accuracy must be a number')
            if not isinstance(v.get('session_id'), str):
                raise ValidationError('TypeRacer session_id must be a string')
        return v

class QueryValidator(BaseModel):
    """Validator for query processing"""
    query: str
    platform: str
    parameters: Optional[Dict[str, Any]] = None

    @field_validator('query')
    def validate_query(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValidationError('Empty query')
        return v

    @model_validator(mode='after')
    def validate_parameters(self):
        if self.parameters is not None and not isinstance(self.parameters, dict):
            raise ValidationError('Parameters must be a dictionary')
        return self

class DataFrameValidator(BaseModel):
    """Validator for transformed DataFrame"""
    required_columns: List[str]
    min_rows: int = 1
    allow_nulls: bool = False

    def validate_dataframe(self, df) -> bool:
        """Validate the DataFrame structure and content"""
        try:
            # Check DataFrame type
            if not isinstance(df, pd.DataFrame):
                raise ValidationError('Input must be a pandas DataFrame')

            # Check required columns
            missing_cols = set(self.required_columns) - set(df.columns)
            if missing_cols:
                raise ValidationError(f'Missing required columns: {missing_cols}')

            # Check minimum rows
            if len(df) < self.min_rows:
                raise ValidationError(f'DataFrame must have at least {self.min_rows} rows')

            # Check for null values
            if not self.allow_nulls and df[self.required_columns].isnull().any().any():
                raise ValidationError('Null values found in required columns')

            return True
        except Exception as e:
            logger.error(f'DataFrame validation failed: {str(e)}')
            raise ValidationError(str(e))

def validate_pipeline_stage(stage: str, data: Any, platform: str, **kwargs) -> bool:
    """
    Validate data at each pipeline stage.
    
    Args:
        stage: Pipeline stage ('ingestion', 'normalization', 'query', 'transformation')
        data: Data to validate
        platform: The platform being used ('typeracer' or 'f1')
        **kwargs: Additional validation parameters
    
    Returns:
        bool: True if validation passes
        
    Raises:
        ValidationError: If validation fails
    """
    try:
        if stage == 'ingestion':
            RawDataValidator(
                platform=platform,
                timestamp=datetime.now(),
                data=data
            )
        elif stage == 'normalization':
            NormalizedDataValidator(
                platform=platform,
                timestamp=datetime.now(),
                metrics=data,
                metadata=kwargs.get('metadata')
            )
        elif stage == 'query':
            QueryValidator(
                query=data,
                platform=platform,
                parameters=kwargs.get('parameters')
            )
        elif stage == 'transformation':
            validator = DataFrameValidator(
                required_columns=kwargs.get('required_columns', []),
                min_rows=kwargs.get('min_rows', 1),
                allow_nulls=kwargs.get('allow_nulls', False)
            )
            validator.validate_dataframe(data)
        else:
            raise ValidationError(f'Unknown pipeline stage: {stage}')
        
        return True
    except Exception as e:
        logger.error(f'Validation failed at {stage} stage: {str(e)}')
        if not isinstance(e, ValidationError):
            raise ValidationError(str(e))
        raise 