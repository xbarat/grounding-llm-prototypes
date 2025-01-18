from typing import Dict, List, Any
from collections import defaultdict
import json
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

from batch_test import QueryTestResult

class TestResultsAnalyzer:
    """Analyzes and reports test results"""
    
    def __init__(self, results_dir: Path):
        self.results_dir = results_dir
        self.results_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_summary_report(self, results: Dict[str, QueryTestResult]) -> Dict[str, Any]:
        """Generate comprehensive test summary"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        summary = {
            'overall_stats': self._calculate_overall_stats(results),
            'stage_analysis': self._analyze_stages(results),
            'failure_patterns': self._identify_failure_patterns(results),
            'performance_metrics': self._analyze_performance(results)
        }
        
        # Save summary report
        report_path = self.results_dir / f"summary_report_{timestamp}.json"
        with open(report_path, 'w') as f:
            json.dump(summary, f, indent=2)
        
        # Generate visualizations
        self._generate_visualizations(results, timestamp)
        
        return summary
    
    def _calculate_overall_stats(self, results: Dict[str, QueryTestResult]) -> Dict[str, Any]:
        """Calculate overall test statistics"""
        total = len(results)
        successful = sum(1 for r in results.values() if r.final_status == "SUCCESS")
        failed = total - successful
        
        return {
            'total_queries': total,
            'successful_queries': successful,
            'failed_queries': failed,
            'success_rate': (successful / total) * 100 if total > 0 else 0,
            'average_duration': sum(r.total_duration for r in results.values()) / total if total > 0 else 0
        }
    
    def _analyze_stages(self, results: Dict[str, QueryTestResult]) -> Dict[str, Dict[str, Any]]:
        """Analyze success/failure patterns by stage"""
        stage_stats = defaultdict(lambda: {
            'total': 0,
            'success': 0,
            'failure': 0,
            'avg_duration': 0.0,
            'error_types': defaultdict(int)
        })
        
        for result in results.values():
            for stage_name, stage in result.stages.items():
                stats = stage_stats[stage_name]
                stats['total'] += 1
                
                if stage.success:
                    stats['success'] += 1
                else:
                    stats['failure'] += 1
                    if stage.error:
                        stats['error_types'][stage.error] += 1
                
                stats['avg_duration'] += stage.duration
        
        # Calculate averages
        for stats in stage_stats.values():
            if stats['total'] > 0:
                stats['avg_duration'] /= stats['total']
        
        return dict(stage_stats)
    
    def _identify_failure_patterns(self, results: Dict[str, QueryTestResult]) -> List[Dict[str, Any]]:
        """Identify common failure patterns"""
        failure_patterns = []
        error_counts = defaultdict(int)
        stage_failure_counts = defaultdict(int)
        
        for result in results.values():
            if result.final_status != "SUCCESS":
                # Track stage where failure occurred
                failed_stage = None
                for stage_name, stage in result.stages.items():
                    if not stage.success:
                        failed_stage = stage_name
                        stage_failure_counts[stage_name] += 1
                        if stage.error:
                            error_counts[stage.error] += 1
                        break
                
                if failed_stage:
                    failure_patterns.append({
                        'query': result.query,
                        'failed_stage': failed_stage,
                        'error': result.stages[failed_stage].error if failed_stage in result.stages else None
                    })
        
        # Summarize patterns
        return {
            'common_errors': dict(error_counts),
            'stage_failures': dict(stage_failure_counts),
            'failure_examples': failure_patterns[:5]  # Include up to 5 examples
        }
    
    def _analyze_performance(self, results: Dict[str, QueryTestResult]) -> Dict[str, Any]:
        """Analyze performance metrics"""
        durations = [r.total_duration for r in results.values()]
        stage_durations = defaultdict(list)
        
        for result in results.values():
            for stage_name, stage in result.stages.items():
                stage_durations[stage_name].append(stage.duration)
        
        performance_metrics = {
            'overall': {
                'min_duration': min(durations) if durations else 0,
                'max_duration': max(durations) if durations else 0,
                'avg_duration': sum(durations) / len(durations) if durations else 0,
                'total_duration': sum(durations)
            },
            'stages': {}
        }
        
        for stage_name, durations in stage_durations.items():
            performance_metrics['stages'][stage_name] = {
                'min_duration': min(durations) if durations else 0,
                'max_duration': max(durations) if durations else 0,
                'avg_duration': sum(durations) / len(durations) if durations else 0
            }
        
        return performance_metrics
    
    def _generate_visualizations(self, results: Dict[str, QueryTestResult], timestamp: str):
        """Generate visualization plots"""
        # 1. Stage Success Rates
        stage_stats = self._analyze_stages(results)
        stages = list(stage_stats.keys())
        success_rates = [
            (stats['success'] / stats['total']) * 100 
            for stats in stage_stats.values()
        ]
        
        plt.figure(figsize=(10, 6))
        plt.bar(stages, success_rates)
        plt.title('Success Rate by Stage')
        plt.ylabel('Success Rate (%)')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(self.results_dir / f"stage_success_rates_{timestamp}.png")
        plt.close()
        
        # 2. Stage Durations
        stage_durations = {
            stage: stats['avg_duration']
            for stage, stats in stage_stats.items()
        }
        
        plt.figure(figsize=(10, 6))
        plt.bar(stage_durations.keys(), stage_durations.values())
        plt.title('Average Duration by Stage')
        plt.ylabel('Duration (seconds)')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(self.results_dir / f"stage_durations_{timestamp}.png")
        plt.close()
        
        # 3. Query Duration Distribution
        durations = [r.total_duration for r in results.values()]
        plt.figure(figsize=(10, 6))
        plt.hist(durations, bins=20)
        plt.title('Query Duration Distribution')
        plt.xlabel('Duration (seconds)')
        plt.ylabel('Number of Queries')
        plt.tight_layout()
        plt.savefig(self.results_dir / f"duration_distribution_{timestamp}.png")
        plt.close()

def format_duration(seconds: float) -> str:
    """Format duration in seconds to a readable string"""
    if seconds < 1:
        return f"{seconds*1000:.2f}ms"
    elif seconds < 60:
        return f"{seconds:.2f}s"
    else:
        minutes = int(seconds // 60)
        remaining_seconds = seconds % 60
        return f"{minutes}m {remaining_seconds:.2f}s" 