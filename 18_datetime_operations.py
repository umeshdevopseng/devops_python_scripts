#!/usr/bin/env python3
"""
DateTime Operations for DevOps - Script 18
Why: Time-based operations are crucial for scheduling, monitoring, and log analysis
"""

from datetime import datetime, timedelta, timezone
import time
from typing import List, Dict, Optional, Tuple
import calendar
from dataclasses import dataclass

@dataclass
class TimeWindow:
    """
    Time window for monitoring and analysis
    Why: Structure time-based queries and monitoring periods
    """
    start: datetime
    end: datetime
    
    def duration_seconds(self) -> float:
        """Get duration in seconds"""
        return (self.end - self.start).total_seconds()
    
    def contains(self, timestamp: datetime) -> bool:
        """Check if timestamp falls within window"""
        return self.start <= timestamp <= self.end

def parse_timestamp(timestamp_str: str, formats: List[str] = None) -> Optional[datetime]:
    """
    Parse timestamp string with multiple format support
    Why: Handle various timestamp formats from different systems
    """
    if formats is None:
        formats = [
            '%Y-%m-%d %H:%M:%S',           # 2024-01-15 10:30:15
            '%Y-%m-%dT%H:%M:%S',           # 2024-01-15T10:30:15
            '%Y-%m-%dT%H:%M:%SZ',          # 2024-01-15T10:30:15Z
            '%Y-%m-%dT%H:%M:%S.%fZ',       # 2024-01-15T10:30:15.123456Z
            '%d/%b/%Y:%H:%M:%S %z',        # 15/Jan/2024:10:30:15 +0000
            '%Y-%m-%d',                    # 2024-01-15
            '%m/%d/%Y %H:%M:%S',           # 01/15/2024 10:30:15
        ]
    
    for fmt in formats:
        try:
            return datetime.strptime(timestamp_str, fmt)
        except ValueError:
            continue
    
    # Try parsing Unix timestamp
    try:
        timestamp = float(timestamp_str)
        return datetime.fromtimestamp(timestamp)
    except ValueError:
        pass
    
    return None

def get_time_windows(start_time: datetime, end_time: datetime, 
                    window_size: timedelta) -> List[TimeWindow]:
    """
    Split time range into smaller windows
    Why: Process large time ranges in manageable chunks for analysis
    """
    windows = []
    current_start = start_time
    
    while current_start < end_time:
        current_end = min(current_start + window_size, end_time)
        windows.append(TimeWindow(current_start, current_end))
        current_start = current_end
    
    return windows

def calculate_uptime_percentage(downtime_periods: List[Tuple[datetime, datetime]], 
                              total_period: TimeWindow) -> float:
    """
    Calculate uptime percentage from downtime periods
    Why: Generate SLA reports and availability metrics
    """
    total_seconds = total_period.duration_seconds()
    downtime_seconds = 0
    
    for start, end in downtime_periods:
        # Ensure downtime period overlaps with total period
        overlap_start = max(start, total_period.start)
        overlap_end = min(end, total_period.end)
        
        if overlap_start < overlap_end:
            downtime_seconds += (overlap_end - overlap_start).total_seconds()
    
    uptime_seconds = total_seconds - downtime_seconds
    return (uptime_seconds / total_seconds) * 100 if total_seconds > 0 else 0

def get_business_hours_windows(date: datetime, 
                             start_hour: int = 9, end_hour: int = 17,
                             weekdays_only: bool = True) -> List[TimeWindow]:
    """
    Get business hours windows for a date
    Why: Schedule maintenance and deployments during appropriate hours
    """
    windows = []
    
    # Check if it's a weekday (Monday=0, Sunday=6)
    if weekdays_only and date.weekday() >= 5:  # Saturday or Sunday
        return windows
    
    # Create business hours window for the date
    start_time = date.replace(hour=start_hour, minute=0, second=0, microsecond=0)
    end_time = date.replace(hour=end_hour, minute=0, second=0, microsecond=0)
    
    windows.append(TimeWindow(start_time, end_time))
    return windows

def schedule_recurring_task(start_time: datetime, interval: timedelta, 
                          count: int) -> List[datetime]:
    """
    Generate schedule for recurring tasks
    Why: Plan automated backups, health checks, and maintenance tasks
    """
    schedule = []
    current_time = start_time
    
    for _ in range(count):
        schedule.append(current_time)
        current_time += interval
    
    return schedule

def find_next_maintenance_window(current_time: datetime,
                               maintenance_hours: List[int] = None,
                               maintenance_days: List[int] = None) -> datetime:
    """
    Find next available maintenance window
    Why: Schedule deployments and maintenance during low-traffic periods
    """
    if maintenance_hours is None:
        maintenance_hours = [2, 3, 4]  # 2 AM - 4 AM
    
    if maintenance_days is None:
        maintenance_days = [6, 0]  # Sunday and Monday
    
    # Start checking from the next hour
    check_time = current_time.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
    
    # Look up to 7 days ahead
    for _ in range(7 * 24):  # 7 days * 24 hours
        if (check_time.weekday() in maintenance_days and 
            check_time.hour in maintenance_hours):
            return check_time
        
        check_time += timedelta(hours=1)
    
    # Fallback: return next occurrence of first maintenance hour
    return current_time.replace(hour=maintenance_hours[0], minute=0, second=0, microsecond=0) + timedelta(days=1)

def calculate_response_time_percentiles(response_times: List[Tuple[datetime, float]],
                                      time_window: TimeWindow,
                                      percentiles: List[float] = None) -> Dict[float, float]:
    """
    Calculate response time percentiles for a time window
    Why: Generate performance reports and SLA metrics
    """
    if percentiles is None:
        percentiles = [50, 90, 95, 99]
    
    # Filter response times within the window
    filtered_times = [
        response_time for timestamp, response_time in response_times
        if time_window.contains(timestamp)
    ]
    
    if not filtered_times:
        return {p: 0.0 for p in percentiles}
    
    # Sort response times
    sorted_times = sorted(filtered_times)
    
    # Calculate percentiles
    result = {}
    for p in percentiles:
        index = int((len(sorted_times) - 1) * p / 100)
        result[p] = sorted_times[index]
    
    return result

def get_timezone_aware_time(timestamp: datetime, timezone_name: str) -> datetime:
    """
    Convert timestamp to specific timezone
    Why: Handle logs and events from different geographic locations
    """
    import pytz
    
    try:
        tz = pytz.timezone(timezone_name)
        
        # If timestamp is naive, assume it's UTC
        if timestamp.tzinfo is None:
            timestamp = pytz.UTC.localize(timestamp)
        
        return timestamp.astimezone(tz)
    except pytz.exceptions.UnknownTimeZoneError:
        # Fallback to UTC
        return timestamp.replace(tzinfo=timezone.utc)

def calculate_deployment_duration(deployment_events: List[Tuple[str, datetime]]) -> Dict[str, float]:
    """
    Calculate deployment phase durations
    Why: Analyze deployment performance and identify bottlenecks
    """
    durations = {}
    events_by_time = sorted(deployment_events, key=lambda x: x[1])
    
    for i in range(len(events_by_time) - 1):
        current_event, current_time = events_by_time[i]
        next_event, next_time = events_by_time[i + 1]
        
        phase_name = f"{current_event}_to_{next_event}"
        duration = (next_time - current_time).total_seconds()
        durations[phase_name] = duration
    
    return durations

def generate_cron_schedule(minute: str = "*", hour: str = "*", day: str = "*",
                         month: str = "*", weekday: str = "*") -> str:
    """
    Generate cron schedule expression
    Why: Create scheduled tasks for automation and maintenance
    """
    return f"{minute} {hour} {day} {month} {weekday}"

def parse_cron_next_run(cron_expression: str, current_time: datetime = None) -> datetime:
    """
    Calculate next run time for cron expression (simplified)
    Why: Predict when scheduled tasks will execute
    """
    if current_time is None:
        current_time = datetime.now()
    
    # This is a simplified implementation
    # In production, use a library like croniter
    
    parts = cron_expression.split()
    if len(parts) != 5:
        raise ValueError("Invalid cron expression")
    
    minute, hour, day, month, weekday = parts
    
    # Simple case: daily at specific time
    if minute.isdigit() and hour.isdigit() and day == "*" and month == "*" and weekday == "*":
        target_hour = int(hour)
        target_minute = int(minute)
        
        next_run = current_time.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)
        
        # If time has passed today, schedule for tomorrow
        if next_run <= current_time:
            next_run += timedelta(days=1)
        
        return next_run
    
    # Fallback: next hour
    return current_time.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)

class MetricsTimeAggregator:
    """
    Aggregate metrics over time windows
    Why: Generate time-based reports and dashboards
    """
    
    def __init__(self):
        self.data_points = []  # List of (timestamp, value) tuples
    
    def add_data_point(self, timestamp: datetime, value: float):
        """Add a data point"""
        self.data_points.append((timestamp, value))
    
    def aggregate_by_window(self, window_size: timedelta, 
                          aggregation_func: str = 'avg') -> List[Tuple[datetime, float]]:
        """Aggregate data points by time windows"""
        if not self.data_points:
            return []
        
        # Sort by timestamp
        sorted_data = sorted(self.data_points, key=lambda x: x[0])
        
        # Find time range
        start_time = sorted_data[0][0]
        end_time = sorted_data[-1][0]
        
        # Generate windows
        windows = get_time_windows(start_time, end_time, window_size)
        
        aggregated = []
        for window in windows:
            # Get data points in this window
            window_data = [
                value for timestamp, value in sorted_data
                if window.contains(timestamp)
            ]
            
            if window_data:
                if aggregation_func == 'avg':
                    agg_value = sum(window_data) / len(window_data)
                elif aggregation_func == 'sum':
                    agg_value = sum(window_data)
                elif aggregation_func == 'max':
                    agg_value = max(window_data)
                elif aggregation_func == 'min':
                    agg_value = min(window_data)
                else:
                    agg_value = sum(window_data) / len(window_data)  # Default to avg
                
                aggregated.append((window.start, agg_value))
        
        return aggregated

if __name__ == "__main__":
    # Example 1: Parse various timestamp formats
    timestamps = [
        "2024-01-15 10:30:15",
        "2024-01-15T10:30:15Z",
        "1705315815",  # Unix timestamp
        "15/Jan/2024:10:30:15 +0000"
    ]
    
    for ts in timestamps:
        parsed = parse_timestamp(ts)
        print(f"Parsed '{ts}': {parsed}")
    
    # Example 2: Calculate uptime
    now = datetime.now()
    total_period = TimeWindow(now - timedelta(days=1), now)
    downtime_periods = [
        (now - timedelta(hours=2), now - timedelta(hours=1)),  # 1 hour downtime
    ]
    
    uptime = calculate_uptime_percentage(downtime_periods, total_period)
    print(f"Uptime: {uptime:.2f}%")
    
    # Example 3: Schedule recurring backups
    start_time = datetime.now().replace(hour=2, minute=0, second=0, microsecond=0)
    backup_schedule = schedule_recurring_task(start_time, timedelta(days=1), 7)
    print(f"Next 7 backup times: {[t.strftime('%Y-%m-%d %H:%M') for t in backup_schedule]}")
    
    # Example 4: Find next maintenance window
    next_maintenance = find_next_maintenance_window(datetime.now())
    print(f"Next maintenance window: {next_maintenance}")
    
    # Example 5: Metrics aggregation
    aggregator = MetricsTimeAggregator()
    
    # Add sample data points
    base_time = datetime.now() - timedelta(hours=1)
    for i in range(60):  # 60 minutes of data
        timestamp = base_time + timedelta(minutes=i)
        value = 50 + (i % 10)  # Sample CPU usage
        aggregator.add_data_point(timestamp, value)
    
    # Aggregate by 10-minute windows
    aggregated = aggregator.aggregate_by_window(timedelta(minutes=10), 'avg')
    print(f"Aggregated data points: {len(aggregated)}")
    
    print("DateTime operations script ready!")