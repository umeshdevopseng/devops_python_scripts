#!/usr/bin/env python3
"""
Data Structures for DevOps - Script 16
Why: Efficient data structures improve performance in large-scale operations
"""

from collections import defaultdict, deque, Counter, namedtuple
from typing import Dict, List, Set, Tuple, Any, Optional
import heapq
import bisect
from dataclasses import dataclass
from enum import Enum

# Named tuple for structured data
ServerInfo = namedtuple('ServerInfo', ['hostname', 'ip', 'status', 'cpu_usage'])

@dataclass
class DeploymentRecord:
    """
    Structured deployment record
    Why: Type-safe data structure for deployment tracking
    """
    app_name: str
    version: str
    environment: str
    timestamp: float
    status: str
    rollback_version: Optional[str] = None

class ServiceStatus(Enum):
    """
    Service status enumeration
    Why: Prevent typos and ensure consistent status values
    """
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"

class LRUCache:
    """
    Least Recently Used cache implementation
    Why: Cache frequently accessed data with automatic eviction
    """
    
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = {}  # key -> value
        self.access_order = deque()  # Track access order
    
    def get(self, key: str) -> Any:
        """Get value and mark as recently used"""
        if key in self.cache:
            # Move to end (most recently used)
            self.access_order.remove(key)
            self.access_order.append(key)
            return self.cache[key]
        return None
    
    def put(self, key: str, value: Any):
        """Add/update value in cache"""
        if key in self.cache:
            # Update existing key
            self.access_order.remove(key)
        elif len(self.cache) >= self.capacity:
            # Remove least recently used item
            oldest_key = self.access_order.popleft()
            del self.cache[oldest_key]
        
        self.cache[key] = value
        self.access_order.append(key)

class CircularBuffer:
    """
    Fixed-size circular buffer for metrics
    Why: Store recent metrics without unbounded memory growth
    """
    
    def __init__(self, size: int):
        self.size = size
        self.buffer = [None] * size
        self.index = 0
        self.count = 0
    
    def append(self, value: Any):
        """Add value to buffer"""
        self.buffer[self.index] = value
        self.index = (self.index + 1) % self.size
        self.count = min(self.count + 1, self.size)
    
    def get_all(self) -> List[Any]:
        """Get all values in chronological order"""
        if self.count < self.size:
            return self.buffer[:self.count]
        else:
            # Buffer is full, return in correct order
            return self.buffer[self.index:] + self.buffer[:self.index]
    
    def average(self) -> float:
        """Calculate average of numeric values"""
        values = [v for v in self.get_all() if v is not None and isinstance(v, (int, float))]
        return sum(values) / len(values) if values else 0.0

class PriorityTaskQueue:
    """
    Priority queue for task scheduling
    Why: Process high-priority tasks (alerts, failures) before low-priority ones
    """
    
    def __init__(self):
        self.heap = []  # Min-heap for priorities
        self.counter = 0  # Ensure stable ordering
    
    def add_task(self, priority: int, task: str, data: Dict = None):
        """Add task with priority (lower number = higher priority)"""
        heapq.heappush(self.heap, (priority, self.counter, task, data or {}))
        self.counter += 1
    
    def get_next_task(self) -> Tuple[str, Dict]:
        """Get highest priority task"""
        if self.heap:
            priority, counter, task, data = heapq.heappop(self.heap)
            return task, data
        return None, {}
    
    def peek_next_priority(self) -> Optional[int]:
        """Check priority of next task without removing it"""
        return self.heap[0][0] if self.heap else None
    
    def size(self) -> int:
        """Get number of queued tasks"""
        return len(self.heap)

class ServiceRegistry:
    """
    Service registry using efficient data structures
    Why: Fast service discovery and health tracking
    """
    
    def __init__(self):
        self.services = defaultdict(list)  # service_name -> [instances]
        self.health_status = {}  # instance_id -> status
        self.service_index = {}  # instance_id -> service_name
    
    def register_service(self, service_name: str, instance_id: str, 
                        host: str, port: int):
        """Register service instance"""
        instance = {
            'id': instance_id,
            'host': host,
            'port': port,
            'registered_at': time.time()
        }
        
        self.services[service_name].append(instance)
        self.service_index[instance_id] = service_name
        self.health_status[instance_id] = ServiceStatus.UNKNOWN
    
    def update_health(self, instance_id: str, status: ServiceStatus):
        """Update instance health status"""
        self.health_status[instance_id] = status
    
    def get_healthy_instances(self, service_name: str) -> List[Dict]:
        """Get all healthy instances of a service"""
        instances = self.services.get(service_name, [])
        return [
            instance for instance in instances
            if self.health_status.get(instance['id']) == ServiceStatus.HEALTHY
        ]
    
    def remove_service(self, instance_id: str):
        """Remove service instance"""
        if instance_id in self.service_index:
            service_name = self.service_index[instance_id]
            
            # Remove from services list
            self.services[service_name] = [
                inst for inst in self.services[service_name]
                if inst['id'] != instance_id
            ]
            
            # Clean up indexes
            del self.service_index[instance_id]
            del self.health_status[instance_id]

class MetricsAggregator:
    """
    Efficient metrics aggregation using appropriate data structures
    Why: Collect and analyze metrics from multiple sources efficiently
    """
    
    def __init__(self):
        self.counters = Counter()  # For counting events
        self.gauges = {}  # For current values
        self.histograms = defaultdict(list)  # For value distributions
        self.timeseries = defaultdict(CircularBuffer)  # For time-based data
    
    def increment_counter(self, metric_name: str, value: int = 1):
        """Increment counter metric"""
        self.counters[metric_name] += value
    
    def set_gauge(self, metric_name: str, value: float):
        """Set gauge metric to specific value"""
        self.gauges[metric_name] = value
    
    def record_histogram(self, metric_name: str, value: float):
        """Record value in histogram"""
        self.histograms[metric_name].append(value)
        
        # Keep only recent values to prevent memory growth
        if len(self.histograms[metric_name]) > 1000:
            self.histograms[metric_name] = self.histograms[metric_name][-1000:]
    
    def add_timeseries_point(self, metric_name: str, value: float):
        """Add point to time series"""
        if metric_name not in self.timeseries:
            self.timeseries[metric_name] = CircularBuffer(100)  # Keep last 100 points
        
        self.timeseries[metric_name].append(value)
    
    def get_histogram_percentiles(self, metric_name: str, 
                                percentiles: List[float]) -> Dict[float, float]:
        """Calculate percentiles for histogram"""
        values = sorted(self.histograms.get(metric_name, []))
        if not values:
            return {p: 0.0 for p in percentiles}
        
        result = {}
        for p in percentiles:
            index = int((len(values) - 1) * p / 100)
            result[p] = values[index]
        
        return result
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of all metrics"""
        return {
            'counters': dict(self.counters),
            'gauges': self.gauges.copy(),
            'histogram_counts': {k: len(v) for k, v in self.histograms.items()},
            'timeseries_averages': {
                k: v.average() for k, v in self.timeseries.items()
            }
        }

class ConfigurationTree:
    """
    Tree structure for hierarchical configuration
    Why: Organize configuration with inheritance and overrides
    """
    
    def __init__(self, name: str):
        self.name = name
        self.values = {}
        self.children = {}
        self.parent = None
    
    def add_child(self, name: str) -> 'ConfigurationTree':
        """Add child configuration node"""
        child = ConfigurationTree(name)
        child.parent = self
        self.children[name] = child
        return child
    
    def set_value(self, key: str, value: Any):
        """Set configuration value"""
        self.values[key] = value
    
    def get_value(self, key: str, default: Any = None) -> Any:
        """Get configuration value with inheritance"""
        # Check current node first
        if key in self.values:
            return self.values[key]
        
        # Check parent nodes
        if self.parent:
            return self.parent.get_value(key, default)
        
        return default
    
    def get_all_values(self) -> Dict[str, Any]:
        """Get all values including inherited ones"""
        result = {}
        
        # Start with parent values
        if self.parent:
            result.update(self.parent.get_all_values())
        
        # Override with current values
        result.update(self.values)
        
        return result

def efficient_log_parsing(log_lines: List[str]) -> Dict[str, Any]:
    """
    Efficiently parse log lines using appropriate data structures
    Why: Process large log files quickly with minimal memory usage
    """
    # Use Counter for frequency counting
    log_levels = Counter()
    error_messages = Counter()
    
    # Use set for unique IPs
    unique_ips = set()
    
    # Use defaultdict for grouping
    errors_by_hour = defaultdict(int)
    
    for line in log_lines:
        # Extract log level
        if 'ERROR' in line:
            log_levels['ERROR'] += 1
            # Extract error message (simplified)
            if ':' in line:
                error_msg = line.split(':', 1)[1].strip()[:50]  # First 50 chars
                error_messages[error_msg] += 1
        elif 'WARNING' in line:
            log_levels['WARNING'] += 1
        elif 'INFO' in line:
            log_levels['INFO'] += 1
        
        # Extract IP addresses (simplified pattern)
        import re
        ip_pattern = r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b'
        ips = re.findall(ip_pattern, line)
        unique_ips.update(ips)
        
        # Extract hour for time-based analysis
        if '[' in line and ']' in line:
            timestamp = line[line.find('[')+1:line.find(']')]
            if ':' in timestamp:
                hour = timestamp.split(':')[1] if len(timestamp.split(':')) > 1 else '00'
                errors_by_hour[hour] += 1
    
    return {
        'log_levels': dict(log_levels),
        'top_errors': error_messages.most_common(5),
        'unique_ip_count': len(unique_ips),
        'errors_by_hour': dict(errors_by_hour)
    }

if __name__ == "__main__":
    import time
    
    # Example 1: LRU Cache
    cache = LRUCache(3)
    cache.put('config1', {'db_host': 'localhost'})
    cache.put('config2', {'api_key': 'secret'})
    cache.put('config3', {'timeout': 30})
    
    print(f"Cache hit: {cache.get('config1')}")
    
    # Example 2: Priority Task Queue
    task_queue = PriorityTaskQueue()
    task_queue.add_task(1, 'critical_alert', {'message': 'Service down'})
    task_queue.add_task(5, 'routine_backup', {'database': 'users'})
    task_queue.add_task(3, 'deploy_app', {'version': '1.2.3'})
    
    print(f"Next task: {task_queue.get_next_task()}")
    
    # Example 3: Service Registry
    registry = ServiceRegistry()
    registry.register_service('web-api', 'web-1', '10.0.1.10', 8080)
    registry.register_service('web-api', 'web-2', '10.0.1.11', 8080)
    registry.update_health('web-1', ServiceStatus.HEALTHY)
    registry.update_health('web-2', ServiceStatus.DEGRADED)
    
    healthy_instances = registry.get_healthy_instances('web-api')
    print(f"Healthy web-api instances: {len(healthy_instances)}")
    
    # Example 4: Metrics Aggregator
    metrics = MetricsAggregator()
    metrics.increment_counter('requests_total', 100)
    metrics.set_gauge('cpu_usage', 75.5)
    metrics.record_histogram('response_time', 0.25)
    metrics.add_timeseries_point('memory_usage', 512.0)
    
    summary = metrics.get_summary()
    print(f"Metrics summary: {summary}")
    
    # Example 5: Circular Buffer
    buffer = CircularBuffer(5)
    for i in range(10):
        buffer.append(i * 10)
    
    print(f"Buffer contents: {buffer.get_all()}")
    print(f"Buffer average: {buffer.average()}")
    
    print("Data structures script ready!")