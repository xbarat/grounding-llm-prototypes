"""
Storage module for managing test artifacts.
"""
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd

class TestArtifactStorage:
    """Manages storage and retrieval of test artifacts."""
    
    def __init__(self, storage_dir: Optional[Path] = None):
        self.storage_dir = storage_dir or Path("test_artifacts")
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
    async def store_results(self, results: List, query_set_name: str):
        """Store test results and artifacts."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        batch_dir = self.storage_dir / f"{query_set_name}_{timestamp}"
        batch_dir.mkdir(parents=True, exist_ok=True)
        
        # Store summary
        summary = {
            "timestamp": timestamp,
            "query_set": query_set_name,
            "total_queries": len(results),
            "successful_queries": sum(1 for r in results if r.overall_success),
            "results": [result.to_dict() for result in results]
        }
        
        with open(batch_dir / "summary.json", "w") as f:
            json.dump(summary, f, indent=2)
            
        # Store individual test artifacts
        for i, result in enumerate(results):
            test_dir = batch_dir / f"test_{i:03d}"
            test_dir.mkdir(parents=True, exist_ok=True)
            
            # Store test metadata
            with open(test_dir / "metadata.json", "w") as f:
                json.dump(result.to_dict(), f, indent=2)
            
            # Store stage artifacts
            for stage in result.stages:
                stage_dir = test_dir / stage.stage
                stage_dir.mkdir(parents=True, exist_ok=True)
                
                # Store stage data if available
                if stage.response_data:
                    if isinstance(stage.response_data, pd.DataFrame):
                        stage.response_data.to_parquet(stage_dir / "data.parquet")
                    elif isinstance(stage.response_data, dict):
                        with open(stage_dir / "data.json", "w") as f:
                            json.dump(stage.response_data, f, indent=2)
                    else:
                        with open(stage_dir / "data.txt", "w") as f:
                            f.write(str(stage.response_data))
                            
    async def get_result(self, batch_id: str, test_id: str) -> Optional[Dict]:
        """Retrieve a specific test result."""
        test_dir = self.storage_dir / batch_id / f"test_{test_id}"
        if not test_dir.exists():
            return None
            
        with open(test_dir / "metadata.json") as f:
            return json.load(f)
            
    async def get_batch_summary(self, batch_id: str) -> Optional[Dict]:
        """Retrieve summary for a specific batch."""
        batch_dir = self.storage_dir / batch_id
        if not batch_dir.exists():
            return None
            
        with open(batch_dir / "summary.json") as f:
            return json.load(f)
            
    def list_batches(self) -> List[str]:
        """List all available test batches."""
        return [d.name for d in self.storage_dir.iterdir() if d.is_dir()]
        
    def cleanup_old_artifacts(self, max_age_days: int = 30):
        """Remove artifacts older than specified age."""
        cutoff = datetime.now().timestamp() - (max_age_days * 24 * 60 * 60)
        
        for path in self.storage_dir.rglob("*"):
            if path.is_file() and path.stat().st_mtime < cutoff:
                path.unlink()
            elif path.is_dir() and not any(path.iterdir()):
                path.rmdir() 