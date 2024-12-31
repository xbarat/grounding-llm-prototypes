import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data_validation.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

class DataFrameValidator:
    @staticmethod
    def validate_df(df: pd.DataFrame, query_type: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Validates DataFrame contents without modifying the data
        Returns (is_valid, validation_metrics)
        """
        metrics = {
            'shape': df.shape,
            'total_rows': len(df),
            'columns': df.columns.tolist(),
            'null_counts': df.isnull().sum().to_dict(),
            'non_null_counts': df.count().to_dict(),
            'has_data': len(df) > 0
        }
        
        # Check for required columns based on query type
        required_cols = {
            'qualifying': ['race', 'season', 'driver', 'position', 'Q1', 'Q2', 'Q3'],
            'race_result': ['race', 'season', 'driver', 'position', 'points'],
            'driver_stats': ['race', 'season', 'driver', 'position', 'points', 'status']
        }
        
        if query_type in required_cols:
            missing_cols = [col for col in required_cols[query_type] if col not in df.columns]
            metrics['missing_columns'] = missing_cols
            metrics['has_required_columns'] = len(missing_cols) == 0
        
        # Log detailed metrics
        logging.info(f"\nDataFrame Validation Results for {query_type}:")
        logging.info(f"Shape: {metrics['shape']}")
        logging.info(f"Columns: {metrics['columns']}")
        logging.info(f"Null counts per column:")
        for col, count in metrics['null_counts'].items():
            if count > 0:
                logging.info(f"  {col}: {count} nulls")
        
        # Numeric columns analysis
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            metrics['numeric_stats'] = {}
            for col in numeric_cols:
                stats = df[col].describe().to_dict()
                metrics['numeric_stats'][col] = stats
                logging.info(f"\nStats for {col}:")
                logging.info(f"  Mean: {stats.get('mean', 'N/A')}")
                logging.info(f"  Min: {stats.get('min', 'N/A')}")
                logging.info(f"  Max: {stats.get('max', 'N/A')}")
        
        # Determine if DataFrame is valid
        is_valid = metrics['has_data'] and (
            query_type not in required_cols or metrics['has_required_columns']
        )
        
        return is_valid, metrics

    @staticmethod
    def log_validation_summary(validation_results: Dict[str, Tuple[bool, Dict[str, Any]]]):
        """
        Logs a summary of validation results for all queries
        """
        logging.info("\n=== Data Validation Summary ===")
        for query, (is_valid, metrics) in validation_results.items():
            logging.info(f"\nQuery: {query}")
            logging.info(f"Valid: {is_valid}")
            logging.info(f"Rows: {metrics['total_rows']}")
            if 'missing_columns' in metrics:
                logging.info(f"Missing columns: {metrics['missing_columns']}")
            
            # Log percentage of non-null values
            for col, non_null_count in metrics['non_null_counts'].items():
                pct = (non_null_count / metrics['total_rows']) * 100 if metrics['total_rows'] > 0 else 0
                logging.info(f"{col}: {pct:.1f}% non-null") 