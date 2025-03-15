"""
Helper utilities for the Data Agent.

This module provides various utility functions used throughout the application.
"""

import hashlib
import json
import os
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from .logging import logger


def get_timestamp() -> str:
    """
    Get a formatted timestamp.
    
    Returns:
        str: Formatted timestamp
    """
    return time.strftime("%Y-%m-%d_%H-%M-%S")


def generate_hash(data: Union[str, bytes, Dict, List]) -> str:
    """
    Generate a hash from input data.
    
    Args:
        data: Input data to hash
        
    Returns:
        str: Hexadecimal hash
    """
    if isinstance(data, (dict, list)):
        data = json.dumps(data, sort_keys=True)
    
    if isinstance(data, str):
        data = data.encode("utf-8")
    
    return hashlib.md5(data).hexdigest()


def ensure_directory(path: Union[str, Path]) -> Path:
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        path: Directory path
        
    Returns:
        Path: Path object for the directory
    """
    path_obj = Path(path)
    path_obj.mkdir(exist_ok=True, parents=True)
    return path_obj


def load_json(file_path: Union[str, Path]) -> Dict:
    """
    Load JSON file.
    
    Args:
        file_path: Path to JSON file
        
    Returns:
        Dict: Loaded JSON data
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        logger.error(f"Error loading JSON file {file_path}: {str(e)}")
        return {}


def save_json(data: Dict, file_path: Union[str, Path]) -> bool:
    """
    Save data to JSON file.
    
    Args:
        data: Data to save
        file_path: Path to save JSON file
        
    Returns:
        bool: Success status
    """
    try:
        # Ensure directory exists
        path_obj = Path(file_path)
        path_obj.parent.mkdir(exist_ok=True, parents=True)
        
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        logger.error(f"Error saving JSON file {file_path}: {str(e)}")
        return False


def truncate_text(text: str, max_length: int = 100) -> str:
    """
    Truncate text to specified length.
    
    Args:
        text: Input text
        max_length: Maximum length
        
    Returns:
        str: Truncated text
    """
    if len(text) <= max_length:
        return text
    return f"{text[:max_length-3]}..."
