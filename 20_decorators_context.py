#!/usr/bin/env python3
"""
Decorators and Context Managers for DevOps - Script 20
Why: Advanced Python patterns improve code reusability and resource management
"""

import time
import logging
from functools import wraps
from contextlib import contextmanager
from typing import Callable, Any, Dict, Optional
import threading
from dataclasses import dataclass

# Setup logging for examples
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def timing_decorator(func: Callable) -> Callable:
    """
    Decorator to measure function execution time
    Why: Monitor performance of critical operations like deployments
    """
    @wraps(func)  # Preserve original function metadata
    def wrapper(*args, **kwargs) -> Any:
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            logger.info(f"{func.__name__} completed in {execution_time:.3f}s")
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"{func.__name__} failed after {execution_time:.3f}s: {e}")
            raise
    
    return wrapper

def retry_decorator(max_attempts: int = 3, delay: float = 1.0, 
                   backoff: float = 2.0, exceptions: tuple = (Exception,)):
    """
    Decorator for retrying failed operations
    Why: Handle transient failures in network operations and external services
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == max_attempts - 1:
                        logger.error(f"{func.__name__} failed after {max_attempts} attempts")
                        raise
                    
                    wait_time = delay * (backoff ** attempt)
                    logger.warning(f"{func.__name__} attempt {attempt + 1} failed, "
                                 f"retrying in {wait_time:.1f}s: {e}")
                    time.sleep(wait_time)
            
            raise last_exception
        
        return wrapper
    return decorator

def cache_decorator(ttl_seconds: int = 300):
    """
    Simple caching decorator with TTL (Time To Live)
    Why: Cache expensive operations like API calls or database queries
    """
    def decorator(func: Callable) -> Callable:
        cache = {}
        cache_times = {}
        
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Create cache key from function arguments
            cache_key = str(args) + str(sorted(kwargs.items()))
            current_time = time.time()
            
            # Check if cached result is still valid
            if (cache_key in cache and 
                cache_key in cache_times and
                current_time - cache_times[cache_key] < ttl_seconds):
                
                logger.debug(f"Cache hit for {func.__name__}")
                return cache[cache_key]
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache[cache_key] = result
            cache_times[cache_key] = current_time
            
            logger.debug(f"Cache miss for {func.__name__}, result cached")
            return result
        
        # Add cache management methods
        wrapper.clear_cache = lambda: cache.clear() or cache_times.clear()
        wrapper.cache_info = lambda: {
            'size': len(cache),
            'keys': list(cache.keys())
        }
        
        return wrapper
    return decorator

def rate_limit_decorator(calls_per_second: float = 1.0):
    """
    Rate limiting decorator
    Why: Prevent overwhelming external APIs or services
    """
    def decorator(func: Callable) -> Callable:
        last_called = [0.0]  # Use list to make it mutable in closure
        min_interval = 1.0 / calls_per_second
        lock = threading.Lock()
        
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            with lock:
                current_time = time.time()
                time_since_last = current_time - last_called[0]
                
                if time_since_last < min_interval:
                    sleep_time = min_interval - time_since_last
                    logger.debug(f"Rate limiting {func.__name__}, sleeping {sleep_time:.3f}s")
                    time.sleep(sleep_time)
                
                last_called[0] = time.time()
                return func(*args, **kwargs)
        
        return wrapper
    return decorator

def audit_decorator(operation_type: str):
    """
    Audit decorator to log function calls
    Why: Track critical operations for compliance and debugging
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Log function entry
            logger.info(f"AUDIT: {operation_type} started - {func.__name__}")
            
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                logger.info(f"AUDIT: {operation_type} completed - {func.__name__} "
                          f"in {execution_time:.3f}s")
                return result
                
            except Exception as e:
                execution_time = time.time() - start_time
                logger.error(f"AUDIT: {operation_type} failed - {func.__name__} "
                           f"after {execution_time:.3f}s: {e}")
                raise
        
        return wrapper
    return decorator

@contextmanager
def database_transaction():
    """
    Context manager for database transactions
    Why: Ensure proper transaction handling with automatic rollback on errors
    """
    # Simulate database connection
    connection = {"transaction_active": False}
    
    try:
        # Begin transaction
        connection["transaction_active"] = True
        logger.info("Database transaction started")
        
        yield connection
        
        # Commit transaction
        logger.info("Database transaction committed")
        
    except Exception as e:
        # Rollback transaction on error
        if connection["transaction_active"]:
            logger.error(f"Database transaction rolled back due to error: {e}")
        raise
    
    finally:
        # Cleanup
        connection["transaction_active"] = False
        logger.info("Database connection closed")

@contextmanager
def temporary_environment_variable(key: str, value: str):
    """
    Context manager for temporary environment variables
    Why: Set environment variables for specific operations without permanent changes
    """
    import os
    
    old_value = os.environ.get(key)
    
    try:
        os.environ[key] = value
        logger.debug(f"Set environment variable {key}={value}")
        yield
        
    finally:
        if old_value is None:
            os.environ.pop(key, None)
            logger.debug(f"Removed environment variable {key}")
        else:
            os.environ[key] = old_value
            logger.debug(f"Restored environment variable {key}={old_value}")

@contextmanager
def service_maintenance_mode(service_name: str):
    """
    Context manager for service maintenance mode
    Why: Safely perform maintenance operations with proper state management
    """
    try:
        # Enable maintenance mode
        logger.info(f"Enabling maintenance mode for {service_name}")
        # In real implementation, this would update load balancer, etc.
        
        yield service_name
        
    finally:
        # Disable maintenance mode
        logger.info(f"Disabling maintenance mode for {service_name}")
        # In real implementation, this would restore normal operation

@contextmanager
def file_lock(file_path: str, timeout: float = 10.0):
    """
    Context manager for file locking
    Why: Prevent concurrent access to critical files during operations
    """
    import fcntl
    import os
    
    lock_file = f"{file_path}.lock"
    lock_fd = None
    
    try:
        # Create lock file
        lock_fd = os.open(lock_file, os.O_CREAT | os.O_EXCL | os.O_RDWR)
        
        # Acquire exclusive lock with timeout
        start_time = time.time()
        while True:
            try:
                fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except IOError:
                if time.time() - start_time > timeout:
                    raise TimeoutError(f"Could not acquire lock for {file_path}")
                time.sleep(0.1)
        
        logger.debug(f"Acquired file lock for {file_path}")
        yield
        
    except OSError:
        # Lock file already exists
        raise RuntimeError(f"Lock file {lock_file} already exists")
    
    finally:
        # Release lock and cleanup
        if lock_fd is not None:
            fcntl.flock(lock_fd, fcntl.LOCK_UN)
            os.close(lock_fd)
            os.unlink(lock_file)
            logger.debug(f"Released file lock for {file_path}")

class ResourceManager:
    """
    Context manager class for resource management
    Why: Manage complex resources like connection pools or temporary infrastructure
    """
    
    def __init__(self, resource_type: str, config: Dict[str, Any]):
        self.resource_type = resource_type
        self.config = config
        self.resource = None
    
    def __enter__(self):
        """Acquire resource"""
        logger.info(f"Acquiring {self.resource_type} resource")
        
        # Simulate resource acquisition
        self.resource = {
            'type': self.resource_type,
            'config': self.config,
            'status': 'active',
            'created_at': time.time()
        }
        
        return self.resource
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Release resource"""
        if self.resource:
            logger.info(f"Releasing {self.resource_type} resource")
            self.resource['status'] = 'released'
        
        # Handle exceptions if needed
        if exc_type is not None:
            logger.error(f"Exception occurred while using {self.resource_type}: {exc_val}")
        
        return False  # Don't suppress exceptions

def deployment_pipeline(stages: list):
    """
    Decorator for deployment pipeline with stage tracking
    Why: Track deployment progress through multiple stages
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            pipeline_start = time.time()
            completed_stages = []
            
            try:
                logger.info(f"Starting deployment pipeline: {stages}")
                
                # Execute the decorated function
                result = func(*args, **kwargs)
                
                # Mark all stages as completed (simplified)
                completed_stages = stages.copy()
                
                total_time = time.time() - pipeline_start
                logger.info(f"Deployment pipeline completed in {total_time:.3f}s")
                
                return result
                
            except Exception as e:
                failed_stage = stages[len(completed_stages)] if len(completed_stages) < len(stages) else "unknown"
                logger.error(f"Deployment pipeline failed at stage '{failed_stage}': {e}")
                raise
        
        return wrapper
    return decorator

# Example usage functions
@timing_decorator
@retry_decorator(max_attempts=3, delay=1.0)
@cache_decorator(ttl_seconds=60)
def fetch_service_status(service_name: str) -> Dict[str, Any]:
    """
    Example function with multiple decorators
    Why: Demonstrate combining decorators for robust service operations
    """
    # Simulate API call that might fail
    import random
    
    if random.random() < 0.3:  # 30% chance of failure
        raise ConnectionError(f"Failed to connect to {service_name}")
    
    return {
        'service': service_name,
        'status': 'healthy',
        'timestamp': time.time()
    }

@audit_decorator("DEPLOYMENT")
@deployment_pipeline(['build', 'test', 'deploy', 'verify'])
def deploy_application(app_name: str, version: str) -> bool:
    """
    Example deployment function with audit and pipeline tracking
    Why: Demonstrate comprehensive deployment monitoring
    """
    logger.info(f"Deploying {app_name} version {version}")
    
    # Simulate deployment work
    time.sleep(0.5)
    
    return True

if __name__ == "__main__":
    # Example 1: Function with multiple decorators
    try:
        status = fetch_service_status("web-api")
        print(f"Service status: {status}")
        
        # Call again to test caching
        status = fetch_service_status("web-api")
        print(f"Cached status: {status}")
        
    except Exception as e:
        print(f"Service check failed: {e}")
    
    # Example 2: Context managers
    with database_transaction() as conn:
        print(f"Performing database operations: {conn}")
    
    with temporary_environment_variable("DEPLOY_ENV", "staging"):
        import os
        print(f"Current environment: {os.environ.get('DEPLOY_ENV')}")
    
    with service_maintenance_mode("web-service"):
        print("Performing maintenance operations")
    
    # Example 3: Resource manager
    with ResourceManager("database_pool", {"max_connections": 10}) as resource:
        print(f"Using resource: {resource['type']}")
    
    # Example 4: Deployment with pipeline tracking
    try:
        result = deploy_application("my-app", "1.2.3")
        print(f"Deployment result: {result}")
    except Exception as e:
        print(f"Deployment failed: {e}")
    
    print("Decorators and context managers script ready!")