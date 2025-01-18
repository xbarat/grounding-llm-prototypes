"""
Performance metrics tracking module for batch testing.
"""
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import psutil

class PerformanceMetrics:
    """Tracks performance metrics during batch testing."""
    
    def __init__(self, metrics_dir: Optional[Path] = None):
        self.metrics_dir = metrics_dir or Path("test_metrics")
        self.metrics_dir.mkdir(parents=True, exist_ok=True)
        
        self.batch_start_time: float = 0
        self.batch_end_time: float = 0
        self.query_times: List[float] = []
        self.memory_samples: List[float] = []
        self.cpu_samples: List[float] = []
        self.concurrent_queries: List[int] = []
        self._sampling_interval: float = 1.0  # seconds
        
    def current_time(self) -> float:
        """Get current time in seconds."""
        return time.time()
        
    def start_batch(self):
        """Start tracking a new batch of tests."""
        self.batch_start_time = self.current_time()
        self.query_times = []
        self.memory_samples = []
        self.cpu_samples = []
        self.concurrent_queries = []
        
    def end_batch(self):
        """End the current batch and save metrics."""
        self.batch_end_time = self.current_time()
        self._save_metrics()
        
    def add_query_time(self, duration: float):
        """Record the duration of a query execution."""
        self.query_times.append(duration)
        
    def sample_system_metrics(self, active_queries: int):
        """Sample current system metrics."""
        self.memory_samples.append(psutil.Process().memory_info().rss / 1024 / 1024)  # MB
        self.cpu_samples.append(psutil.cpu_percent())
        self.concurrent_queries.append(active_queries)
        
    def _save_metrics(self):
        """Save metrics to files."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        metrics_file = self.metrics_dir / f"metrics_{timestamp}.txt"
        
        with open(metrics_file, "w") as f:
            f.write("Batch Test Performance Metrics\n")
            f.write("=============================\n\n")
            
            # Timing metrics
            total_duration = self.batch_end_time - self.batch_start_time
            avg_query_time = sum(self.query_times) / len(self.query_times) if self.query_times else 0
            
            f.write(f"Total Duration: {total_duration:.2f}s\n")
            f.write(f"Average Query Time: {avg_query_time:.2f}s\n")
            f.write(f"Min Query Time: {min(self.query_times):.2f}s\n") if self.query_times else None
            f.write(f"Max Query Time: {max(self.query_times):.2f}s\n") if self.query_times else None
            
            # Resource metrics
            f.write("\nResource Usage:\n")
            f.write(f"Average Memory Usage: {sum(self.memory_samples)/len(self.memory_samples):.1f}MB\n")
            f.write(f"Peak Memory Usage: {max(self.memory_samples):.1f}MB\n")
            f.write(f"Average CPU Usage: {sum(self.cpu_samples)/len(self.cpu_samples):.1f}%\n")
            f.write(f"Peak CPU Usage: {max(self.cpu_samples):.1f}%\n")
            
            # Concurrency metrics
            f.write("\nConcurrency Metrics:\n")
            f.write(f"Max Concurrent Queries: {max(self.concurrent_queries)}\n")
            f.write(f"Average Concurrent Queries: {sum(self.concurrent_queries)/len(self.concurrent_queries):.1f}\n")
            
    def print_summary(self):
        """Print a summary of the current metrics."""
        if not self.query_times:
            print("No metrics available")
            return
            
        print("\nPerformance Metrics:")
        print(f"Total Duration: {self.batch_end_time - self.batch_start_time:.2f}s")
        print(f"Average Query Time: {sum(self.query_times)/len(self.query_times):.2f}s")
        print(f"Peak Memory Usage: {max(self.memory_samples):.1f}MB")
        print(f"Peak CPU Usage: {max(self.cpu_samples):.1f}%")
        print(f"Max Concurrent Queries: {max(self.concurrent_queries)}") 