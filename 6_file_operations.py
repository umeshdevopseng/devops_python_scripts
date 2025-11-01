#!/usr/bin/env python3
"""
File Operations for DevOps - Script 6
Why: File manipulation is crucial for config management, log processing, and automation
"""

import os
import shutil
import json
import yaml
from pathlib import Path

def read_config_file(file_path: str) -> dict:
    """
    Read configuration files (JSON/YAML)
    Why: DevOps engineers constantly work with config files
    """
    path = Path(file_path)
    
    if path.suffix == '.json':
        with open(file_path, 'r') as f:
            return json.load(f)  # Parse JSON into Python dict
    elif path.suffix in ['.yaml', '.yml']:
        with open(file_path, 'r') as f:
            return yaml.safe_load(f)  # Parse YAML safely
    else:
        raise ValueError("Unsupported file format")

def backup_file(source: str, backup_dir: str) -> str:
    """
    Create timestamped backup of file
    Why: Always backup before modifying critical files
    """
    from datetime import datetime
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')  # Create unique timestamp
    filename = Path(source).name  # Extract filename from path
    backup_path = Path(backup_dir) / f"{filename}.backup.{timestamp}"
    
    shutil.copy2(source, backup_path)  # Copy with metadata preserved
    return str(backup_path)

def find_files_by_pattern(directory: str, pattern: str) -> list:
    """
    Find files matching pattern recursively
    Why: Locate config files, logs, or scripts across directories
    """
    import glob
    
    search_pattern = os.path.join(directory, '**', pattern)
    return glob.glob(search_pattern, recursive=True)  # ** means recursive search

def rotate_log_files(log_dir: str, max_files: int = 5):
    """
    Rotate log files to prevent disk space issues
    Why: Log rotation is essential for system maintenance
    """
    log_files = sorted(Path(log_dir).glob('*.log'), key=os.path.getmtime)
    
    # Remove oldest files if exceeding limit
    while len(log_files) > max_files:
        oldest_file = log_files.pop(0)  # Remove first (oldest) file
        oldest_file.unlink()  # Delete the file
        print(f"Deleted old log: {oldest_file}")

if __name__ == "__main__":
    # Example usage
    print("File operations script ready!")