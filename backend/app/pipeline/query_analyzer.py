import re
import json
from collections import defaultdict
from typing import Dict, List, Any, Optional
import pandas as pd
from datetime import datetime
from pathlib import Path

class QueryAnalyzer:
    def __init__(self, log_file: str = 'logs/query_processing.log'):
        self.log_file = log_file
        self.queries = defaultdict(dict)
        
    def parse_logs(self) -> bool:
        """Parse the log file and organize data by query_id"""
        log_path = Path(self.log_file)
        if not log_path.exists():
            print(f"Log file not found: {self.log_file}")
            return False
            
        try:
            with open(self.log_file, 'r') as f:
                for line in f:
                    try:
                        timestamp, level, message = self._parse_log_line(line)
                        query_id = self._extract_query_id(message)
                        if query_id:
                            self._process_log_entry(query_id, level, message)
                    except Exception as e:
                        print(f"Error parsing line: {line}. Error: {str(e)}")
            return True
        except Exception as e:
            print(f"Error reading log file: {str(e)}")
            return False
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate analysis report of query processing"""
        if not self.queries:
            return {
                "summary": {
                    "total_queries": 0,
                    "success_rate": 0,
                    "failed_queries": 0
                },
                "failure_analysis": {
                    "common_failures": {},
                    "failure_rate_by_type": {}
                },
                "endpoint_analysis": {
                    "endpoint_usage": {},
                    "most_common_endpoints": []
                }
            }
            
        total_queries = len(self.queries)
        failed_queries = sum(1 for q in self.queries.values() if q.get('status') == 'error')
        success_rate = (total_queries - failed_queries) / total_queries if total_queries > 0 else 0
        
        failure_reasons = defaultdict(int)
        endpoint_matches = defaultdict(int)
        
        for query_data in self.queries.values():
            if query_data.get('status') == 'error':
                failure_reasons[query_data.get('error_message', 'Unknown')] += 1
            if 'matched_endpoints' in query_data:
                for endpoint in query_data['matched_endpoints']:
                    endpoint_matches[endpoint] += 1
        
        return {
            "summary": {
                "total_queries": total_queries,
                "success_rate": success_rate,
                "failed_queries": failed_queries
            },
            "failure_analysis": {
                "common_failures": dict(failure_reasons),
                "failure_rate_by_type": {k: v/total_queries for k, v in failure_reasons.items()}
            },
            "endpoint_analysis": {
                "endpoint_usage": dict(endpoint_matches),
                "most_common_endpoints": sorted(endpoint_matches.items(), key=lambda x: x[1], reverse=True)[:5]
            }
        }
    
    def export_failed_queries(self, output_file: str = 'failed_queries.csv') -> bool:
        """Export failed queries for manual review"""
        if not self.queries:
            print("No queries to export")
            return False
            
        failed = []
        for query_id, data in self.queries.items():
            if data.get('status') == 'error':
                failed.append({
                    'query_id': query_id,
                    'original_query': data.get('original_query'),
                    'error_message': data.get('error_message'),
                    'gpt_response': json.dumps(data.get('gpt_response', {})),
                    'timestamp': data.get('timestamp')
                })
        
        if failed:
            try:
                # Ensure the output directory exists
                output_path = Path(output_file)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                
                df = pd.DataFrame(failed)
                df.to_csv(output_file, index=False)
                print(f"Exported {len(failed)} failed queries to {output_file}")
                return True
            except Exception as e:
                print(f"Error exporting failed queries: {str(e)}")
                return False
        return False
    
    def _parse_log_line(self, line: str) -> tuple[str, str, str]:
        """Parse a log line into timestamp, level, and message"""
        match = re.match(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) - (\w+) - (.+)', line)
        if match:
            return match.groups()
        raise ValueError(f"Invalid log line format: {line}")
    
    def _extract_query_id(self, message: str) -> Optional[str]:
        """Extract query ID from log message"""
        match = re.search(r'\[(\d{8}_\d{6}_\d+)\]', message)
        return match.group(1) if match else None
    
    def _process_log_entry(self, query_id: str, level: str, message: str):
        """Process a log entry and update the queries dictionary"""
        if 'Processing new query' in message:
            query = re.search(r'Processing new query: (.+)$', message)
            if query:
                self.queries[query_id].update({
                    'original_query': query.group(1),
                    'timestamp': datetime.now()
                })
        elif 'GPT Response' in message:
            try:
                gpt_response = json.loads(message.split('GPT Response: ')[1])
                self.queries[query_id]['gpt_response'] = gpt_response
            except:
                pass
        elif 'Matched endpoints' in message:
            endpoints = re.search(r'Matched endpoints: \[(.*?)\]', message)
            if endpoints:
                self.queries[query_id]['matched_endpoints'] = endpoints.group(1).split(',')
        elif 'Error processing query' in message:
            self.queries[query_id].update({
                'status': 'error',
                'error_message': message.split('Error processing query: ')[1]
            })
        elif 'Query processing completed successfully' in message:
            self.queries[query_id]['status'] = 'success'

if __name__ == '__main__':
    analyzer = QueryAnalyzer()
    if analyzer.parse_logs():
        report = analyzer.generate_report()
        print(json.dumps(report, indent=2))
        analyzer.export_failed_queries()
    else:
        print("No logs to analyze yet. Run some queries first.")