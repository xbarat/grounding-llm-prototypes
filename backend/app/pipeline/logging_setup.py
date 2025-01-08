import os
import logging
from pathlib import Path
from typing import Optional

def setup_logging(log_dir: str = "logs", log_file: str = "query_processing.log") -> Optional[logging.Logger]:
    """
    Set up logging with proper directory creation and error handling
    """
    try:
        # Create logs directory if it doesn't exist
        log_path = Path(log_dir)
        log_path.mkdir(parents=True, exist_ok=True)
        
        # Configure logger
        logger = logging.getLogger("query_processor")
        logger.setLevel(logging.DEBUG)
        
        # Create file handler
        log_file_path = log_path / log_file
        file_handler = logging.FileHandler(str(log_file_path))
        file_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        )
        
        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        )
        
        # Add handlers
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        logger.info(f"Logging setup complete. Log file: {log_file_path}")
        return logger
        
    except Exception as e:
        print(f"Error setting up logging: {str(e)}")
        # Return a basic console logger as fallback
        fallback_logger = logging.getLogger("fallback_logger")
        fallback_logger.addHandler(logging.StreamHandler())
        fallback_logger.warning(f"Using fallback console logging due to error: {str(e)}")
        return fallback_logger 