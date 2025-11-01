#!/usr/bin/env python3
"""
Error Handling and Retry Logic - Script 11
Why: Robust error handling prevents system failures and improves reliability
"""

import time
import logging
from typing import Callable, Any, Optional
from functools import wraps
import random

# Configure logging for error tracking
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def retry_with_backoff(max_retries: int = 3, backoff_factor: float = 2.0):
    """
    Decorator for retrying functions with exponential backoff
    Why: Handle transient failures in network calls or external services
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)  # Preserve original function metadata
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)  # Try to execute function
                except Exception as e:
                    last_exception = e
                    
                    if attempt == max_retries:
                        logger.error(f"Function {func.__name__} failed after {max_retries} retries: {e}")
                        raise  # Re-raise the last exception
                    
                    # Calculate backoff delay: 1s, 2s, 4s, 8s...
                    delay = backoff_factor ** attempt
                    logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay}s...")
                    time.sleep(delay)
            
            raise last_exception  # This should never be reached
        
        return wrapper
    return decorator

class CircuitBreaker:
    """
    Circuit breaker pattern implementation
    Why: Prevent cascading failures by stopping calls to failing services
    """
    
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold  # Number of failures before opening circuit
        self.timeout = timeout  # Seconds to wait before trying again
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function through circuit breaker
        Why: Protect system from repeated calls to failing services
        """
        if self.state == 'OPEN':
            # Check if timeout period has passed
            if time.time() - self.last_failure_time > self.timeout:
                self.state = 'HALF_OPEN'  # Try one request
                logger.info("Circuit breaker moving to HALF_OPEN state")
            else:
                raise Exception("Circuit breaker is OPEN - service unavailable")
        
        try:
            result = func(*args, **kwargs)
            
            # Success - reset circuit breaker
            if self.state == 'HALF_OPEN':
                self.state = 'CLOSED'
                self.failure_count = 0
                logger.info("Circuit breaker CLOSED - service recovered")
            
            return result
            
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            # Open circuit if threshold reached
            if self.failure_count >= self.failure_threshold:
                self.state = 'OPEN'
                logger.error(f"Circuit breaker OPEN - too many failures ({self.failure_count})")
            
            raise e

def safe_execute(func: Callable, default_value: Any = None, 
                log_errors: bool = True) -> Any:
    """
    Safely execute function with default fallback
    Why: Prevent application crashes from non-critical operations
    """
    try:
        return func()
    except Exception as e:
        if log_errors:
            logger.error(f"Safe execution failed: {e}")
        return default_value

class ErrorAggregator:
    """
    Collect and analyze errors for monitoring
    Why: Track error patterns to identify system issues
    """
    
    def __init__(self):
        self.errors = []
        self.error_counts = {}
    
    def record_error(self, error: Exception, context: str = ""):
        """
        Record error with context information
        Why: Collect error data for analysis and alerting
        """
        error_info = {
            'timestamp': time.time(),
            'type': type(error).__name__,
            'message': str(error),
            'context': context
        }
        
        self.errors.append(error_info)
        
        # Count error types
        error_type = error_info['type']
        self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1
        
        logger.error(f"Error recorded: {error_type} in {context}: {error}")
    
    def get_error_summary(self, time_window: int = 3600) -> dict:
        """
        Get error summary for specified time window
        Why: Monitor error rates and patterns
        """
        current_time = time.time()
        recent_errors = [
            e for e in self.errors 
            if current_time - e['timestamp'] <= time_window
        ]
        
        return {
            'total_errors': len(recent_errors),
            'error_rate': len(recent_errors) / (time_window / 60),  # Errors per minute
            'top_errors': sorted(
                self.error_counts.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:5]
        }

# Example functions that might fail
@retry_with_backoff(max_retries=3, backoff_factor=1.5)
def unreliable_api_call():
    """
    Simulate unreliable API call
    Why: Demonstrate retry logic for external service calls
    """
    if random.random() < 0.7:  # 70% chance of failure
        raise ConnectionError("API temporarily unavailable")
    return {"status": "success", "data": "API response"}

def failing_service():
    """
    Simulate a service that always fails
    Why: Demonstrate circuit breaker pattern
    """
    raise Exception("Service is down")

if __name__ == "__main__":
    # Example 1: Retry with backoff
    try:
        result = unreliable_api_call()
        print(f"API call succeeded: {result}")
    except Exception as e:
        print(f"API call failed permanently: {e}")
    
    # Example 2: Circuit breaker
    circuit_breaker = CircuitBreaker(failure_threshold=3, timeout=10)
    
    for i in range(5):
        try:
            result = circuit_breaker.call(failing_service)
        except Exception as e:
            print(f"Call {i+1} failed: {e}")
    
    # Example 3: Safe execution
    result = safe_execute(
        lambda: 1 / 0,  # This will fail
        default_value="Operation failed safely"
    )
    print(f"Safe execution result: {result}")
    
    # Example 4: Error aggregation
    error_aggregator = ErrorAggregator()
    error_aggregator.record_error(ValueError("Invalid input"), "user_validation")
    error_aggregator.record_error(ConnectionError("Network timeout"), "api_call")
    
    summary = error_aggregator.get_error_summary()
    print(f"Error summary: {summary}")
    
    print("Error handling script ready!")