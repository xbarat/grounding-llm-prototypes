import time
from typing import Dict, Any
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)

class MetricsCollector:
    def __init__(self):
        self.metrics = defaultdict(list)
        
    def log_duration(self, model: str, operation: str, duration: float):
        """Log the duration of an operation."""
        metric_key = f"{model}_{operation}_duration"
        self.metrics[metric_key].append(duration)
        logger.info(f"{metric_key}: {duration:.2f}s")
        
    def log_success(self, model: str, operation: str, success: bool):
        """Log whether an operation was successful."""
        metric_key = f"{model}_{operation}_success"
        self.metrics[metric_key].append(int(success))
        logger.info(f"{metric_key}: {success}")
    
    def get_summary(self) -> Dict[str, Dict[str, float]]:
        """Get summary statistics for all collected metrics."""
        summary = {}
        for key, values in self.metrics.items():
            if not values:
                continue
            summary[key] = {
                "count": len(values),
                "mean": sum(values) / len(values),
                "min": min(values),
                "max": max(values)
            }
        return summary

# Global metrics collector instance
collector = MetricsCollector() 