#!/usr/bin/env python3
"""
Logging Setup and Management - Script 14
Why: Proper logging is essential for debugging and monitoring applications
"""

import logging
import logging.handlers
import json
import sys
from typing import Dict, Any
from datetime import datetime
from pathlib import Path

class JSONFormatter(logging.Formatter):
    """
    Custom JSON formatter for structured logging
    Why: JSON logs are easier to parse and analyze in log aggregation systems
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON"""
        log_entry = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add exception information if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        # Add extra fields if present
        if hasattr(record, 'extra_fields'):
            log_entry.update(record.extra_fields)
        
        return json.dumps(log_entry)

class ContextFilter(logging.Filter):
    """
    Add contextual information to log records
    Why: Include request IDs, user IDs, or other context for better debugging
    """
    
    def __init__(self, context: Dict[str, Any] = None):
        super().__init__()
        self.context = context or {}
    
    def filter(self, record: logging.LogRecord) -> bool:
        """Add context to log record"""
        # Add context fields to record
        for key, value in self.context.items():
            setattr(record, key, value)
        
        # Add process and thread info
        record.process_name = 'main'  # Could be set dynamically
        record.thread_name = 'worker-1'  # Could be set dynamically
        
        return True

def setup_application_logging(
    app_name: str,
    log_level: str = 'INFO',
    log_format: str = 'json',
    log_file: str = None,
    max_file_size: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5
) -> logging.Logger:
    """
    Setup comprehensive application logging
    Why: Centralized logging configuration for consistent log format
    """
    
    # Create logger
    logger = logging.getLogger(app_name)
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # Choose formatter based on format preference
    if log_format.lower() == 'json':
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    # Console handler for immediate feedback
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler for persistent logs
    if log_file:
        # Ensure log directory exists
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        
        # Use rotating file handler to prevent huge log files
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_file_size,
            backupCount=backup_count
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    # Add context filter
    context_filter = ContextFilter({'service': app_name})
    logger.addFilter(context_filter)
    
    return logger

def setup_error_logging(logger: logging.Logger, error_file: str = None):
    """
    Setup separate error logging for critical issues
    Why: Separate error logs for alerting and monitoring systems
    """
    if error_file:
        # Create error-only handler
        error_handler = logging.handlers.RotatingFileHandler(
            error_file,
            maxBytes=5 * 1024 * 1024,  # 5MB
            backupCount=3
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(JSONFormatter())
        
        logger.addHandler(error_handler)

def log_function_calls(logger: logging.Logger):
    """
    Decorator to log function calls and execution time
    Why: Debug performance issues and trace function execution
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = datetime.now()
            
            # Log function entry
            logger.info(f"Calling {func.__name__}", extra={
                'extra_fields': {
                    'function': func.__name__,
                    'args_count': len(args),
                    'kwargs_count': len(kwargs),
                    'event': 'function_start'
                }
            })
            
            try:
                result = func(*args, **kwargs)
                
                # Log successful completion
                execution_time = (datetime.now() - start_time).total_seconds()
                logger.info(f"Completed {func.__name__}", extra={
                    'extra_fields': {
                        'function': func.__name__,
                        'execution_time': execution_time,
                        'event': 'function_success'
                    }
                })
                
                return result
                
            except Exception as e:
                # Log function failure
                execution_time = (datetime.now() - start_time).total_seconds()
                logger.error(f"Failed {func.__name__}: {e}", extra={
                    'extra_fields': {
                        'function': func.__name__,
                        'execution_time': execution_time,
                        'error': str(e),
                        'event': 'function_error'
                    }
                })
                raise
        
        return wrapper
    return decorator

class LogAnalyzer:
    """
    Analyze log files for patterns and issues
    Why: Extract insights from log data for monitoring and debugging
    """
    
    def __init__(self, log_file: str):
        self.log_file = log_file
    
    def count_log_levels(self) -> Dict[str, int]:
        """Count occurrences of each log level"""
        level_counts = {}
        
        try:
            with open(self.log_file, 'r') as f:
                for line in f:
                    try:
                        log_entry = json.loads(line.strip())
                        level = log_entry.get('level', 'UNKNOWN')
                        level_counts[level] = level_counts.get(level, 0) + 1
                    except json.JSONDecodeError:
                        # Handle non-JSON log lines
                        if 'ERROR' in line:
                            level_counts['ERROR'] = level_counts.get('ERROR', 0) + 1
                        elif 'WARNING' in line:
                            level_counts['WARNING'] = level_counts.get('WARNING', 0) + 1
                        elif 'INFO' in line:
                            level_counts['INFO'] = level_counts.get('INFO', 0) + 1
        
        except FileNotFoundError:
            print(f"Log file not found: {self.log_file}")
        
        return level_counts
    
    def find_error_patterns(self) -> Dict[str, int]:
        """Find common error patterns in logs"""
        error_patterns = {}
        
        try:
            with open(self.log_file, 'r') as f:
                for line in f:
                    try:
                        log_entry = json.loads(line.strip())
                        if log_entry.get('level') == 'ERROR':
                            message = log_entry.get('message', '')
                            # Extract error type from message
                            if ':' in message:
                                error_type = message.split(':')[0].strip()
                                error_patterns[error_type] = error_patterns.get(error_type, 0) + 1
                    except json.JSONDecodeError:
                        continue
        
        except FileNotFoundError:
            print(f"Log file not found: {self.log_file}")
        
        return error_patterns

def create_log_rotation_script(log_dir: str, retention_days: int = 30) -> str:
    """
    Create script for log rotation and cleanup
    Why: Prevent log files from consuming too much disk space
    """
    script_content = f'''#!/bin/bash
# Log rotation and cleanup script
# Generated by Python logging setup

LOG_DIR="{log_dir}"
RETENTION_DAYS={retention_days}

# Compress old log files
find "$LOG_DIR" -name "*.log" -mtime +1 -exec gzip {{}} \\;

# Remove old compressed logs
find "$LOG_DIR" -name "*.log.gz" -mtime +$RETENTION_DAYS -delete

# Remove empty log files
find "$LOG_DIR" -name "*.log" -size 0 -delete

echo "Log rotation completed at $(date)"
'''
    
    script_path = f"{log_dir}/rotate_logs.sh"
    with open(script_path, 'w') as f:
        f.write(script_content)
    
    # Make script executable
    import os
    os.chmod(script_path, 0o755)
    
    return script_path

if __name__ == "__main__":
    # Setup application logging
    logger = setup_application_logging(
        app_name='devops-app',
        log_level='INFO',
        log_format='json',
        log_file='/tmp/app.log'
    )
    
    # Setup error logging
    setup_error_logging(logger, '/tmp/errors.log')
    
    # Test logging with different levels
    logger.info("Application started", extra={
        'extra_fields': {'version': '1.0.0', 'environment': 'development'}
    })
    
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    
    # Test function logging decorator
    @log_function_calls(logger)
    def sample_function(x: int, y: int) -> int:
        """Sample function to demonstrate logging"""
        if x < 0:
            raise ValueError("x must be positive")
        return x + y
    
    # Test function calls
    try:
        result = sample_function(5, 3)
        logger.info(f"Function result: {result}")
        
        # This will cause an error
        sample_function(-1, 3)
    except ValueError as e:
        logger.error(f"Function call failed: {e}")
    
    # Analyze logs
    analyzer = LogAnalyzer('/tmp/app.log')
    level_counts = analyzer.count_log_levels()
    print(f"Log level counts: {level_counts}")
    
    # Create log rotation script
    rotation_script = create_log_rotation_script('/tmp', retention_days=7)
    print(f"Created log rotation script: {rotation_script}")
    
    print("Logging setup script ready!")