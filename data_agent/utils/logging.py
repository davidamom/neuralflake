"""
Logging utilities for the Data Agent.

This module provides a standardized logging setup for the entire application.
"""

import logging
import sys
from pathlib import Path
from typing import Optional

from ..core.config import config


def setup_logging(
    name: str, level: Optional[str] = None, log_file: Optional[str] = None
) -> logging.Logger:
    """
    Set up logging for a module.
    
    Args:
        name: Logger name
        level: Logging level
        log_file: Log file path
        
    Returns:
        logging.Logger: Configured logger
    """
    # Use configuration if not explicitly provided
    if level is None:
        level = config.logging.level
    
    if log_file is None and config.logging.file:
        log_file = config.logging.file
    
    # Create logger
    logger = logging.getLogger(name)
    
    # Set level
    log_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(log_level)
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Create formatters
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Create file handler if log file specified
    if log_file:
        try:
            # Ensure directory exists
            log_path = Path(log_file)
            log_path.parent.mkdir(exist_ok=True, parents=True)
            
            # Add file handler
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            logger.warning(f"Failed to set up file logging: {e}")
    
    return logger


# Root logger for the application
logger = setup_logging("data_agent")
