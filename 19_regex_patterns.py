#!/usr/bin/env python3
"""
Regular Expression Patterns for DevOps - Script 19
Why: Regex is essential for log parsing, validation, and text processing
"""

import re
from typing import List, Dict, Optional, Tuple, Pattern
from dataclasses import dataclass

@dataclass
class LogPattern:
    """
    Structured log pattern definition
    Why: Organize regex patterns for different log formats
    """
    name: str
    pattern: str
    groups: List[str]
    compiled: Pattern = None
    
    def __post_init__(self):
        self.compiled = re.compile(self.pattern)

class DevOpsRegexPatterns:
    """
    Collection of common DevOps regex patterns
    Why: Centralize frequently used patterns for consistency
    """
    
    # Network patterns
    IPV4 = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
    IPV6 = r'\b(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}\b'
    MAC_ADDRESS = r'\b(?:[0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}\b'
    
    # URL patterns
    HTTP_URL = r'https?://[^\s<>"{}|\\^`\[\]]+'
    DOMAIN = r'\b(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}\b'
    
    # File patterns
    FILE_PATH = r'(?:/[^/\s]+)+/?'
    LOG_FILE = r'[^\s]+\.log(?:\.\d+)?(?:\.gz)?'
    
    # Version patterns
    SEMANTIC_VERSION = r'\bv?(\d+)\.(\d+)\.(\d+)(?:-([a-zA-Z0-9.-]+))?(?:\+([a-zA-Z0-9.-]+))?\b'
    
    # Time patterns
    TIMESTAMP_ISO = r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?'
    TIMESTAMP_APACHE = r'\d{2}/\w{3}/\d{4}:\d{2}:\d{2}:\d{2} [+-]\d{4}'
    
    # Security patterns
    JWT_TOKEN = r'\beyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\b'
    API_KEY = r'\b[A-Za-z0-9]{32,}\b'
    
    # System patterns
    PID = r'\bpid[:\s]*(\d+)\b'
    MEMORY_SIZE = r'\b(\d+(?:\.\d+)?)\s*(B|KB|MB|GB|TB)\b'
    
    # Error patterns
    STACK_TRACE = r'Traceback \(most recent call last\):.*?(?=\n\S|\Z)'
    EXCEPTION = r'(\w+(?:Error|Exception)): (.+)'

def extract_log_components(log_line: str) -> Dict[str, str]:
    """
    Extract components from common log formats
    Why: Parse structured data from various log formats
    """
    patterns = [
        # Apache/Nginx access log
        LogPattern(
            name="apache_access",
            pattern=r'(\S+) \S+ \S+ \[([^\]]+)\] "(\S+) (\S+) (\S+)" (\d+) (\d+) "([^"]*)" "([^"]*)"',
            groups=['ip', 'timestamp', 'method', 'url', 'protocol', 'status', 'size', 'referer', 'user_agent']
        ),
        
        # Application log with level
        LogPattern(
            name="app_log",
            pattern=r'\[([^\]]+)\]\s+(\w+)\s+([^:]+):\s*(.*)',
            groups=['timestamp', 'level', 'component', 'message']
        ),
        
        # Syslog format
        LogPattern(
            name="syslog",
            pattern=r'(\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})\s+(\S+)\s+([^:]+):\s*(.*)',
            groups=['timestamp', 'hostname', 'process', 'message']
        ),
        
        # Docker container log
        LogPattern(
            name="docker_log",
            pattern=r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+Z)\s+(\w+)\s+(.*)',
            groups=['timestamp', 'stream', 'message']
        )
    ]
    
    for pattern in patterns:
        match = pattern.compiled.match(log_line)
        if match:
            result = {'format': pattern.name}
            for i, group_name in enumerate(pattern.groups, 1):
                result[group_name] = match.group(i) if i <= len(match.groups()) else ''
            return result
    
    # No pattern matched
    return {'format': 'unknown', 'raw': log_line}

def validate_configuration_values(config_dict: Dict[str, str]) -> Dict[str, List[str]]:
    """
    Validate configuration values using regex patterns
    Why: Ensure configuration values meet expected formats
    """
    validation_rules = {
        'email': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
        'url': r'^https?://[^\s<>"{}|\\^`\[\]]+$',
        'port': r'^([1-9]\d{0,3}|[1-5]\d{4}|6[0-4]\d{3}|65[0-4]\d{2}|655[0-2]\d|6553[0-5])$',
        'ipv4': r'^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$',
        'version': r'^v?(\d+)\.(\d+)\.(\d+)(?:-([a-zA-Z0-9.-]+))?$',
        'duration': r'^\d+[smhd]$',
        'percentage': r'^(100|[1-9]?\d)%?$'
    }
    
    errors = {}
    
    for key, value in config_dict.items():
        key_errors = []
        
        # Determine validation rule based on key name
        if 'email' in key.lower():
            rule = validation_rules['email']
        elif 'url' in key.lower() or 'endpoint' in key.lower():
            rule = validation_rules['url']
        elif 'port' in key.lower():
            rule = validation_rules['port']
        elif 'ip' in key.lower() and 'v4' in key.lower():
            rule = validation_rules['ipv4']
        elif 'version' in key.lower():
            rule = validation_rules['version']
        elif 'timeout' in key.lower() or 'interval' in key.lower():
            rule = validation_rules['duration']
        elif 'percent' in key.lower() or 'ratio' in key.lower():
            rule = validation_rules['percentage']
        else:
            continue  # No validation rule for this key
        
        if not re.match(rule, str(value)):
            key_errors.append(f"Value '{value}' doesn't match expected format")
        
        if key_errors:
            errors[key] = key_errors
    
    return errors

def extract_security_indicators(text: str) -> Dict[str, List[str]]:
    """
    Extract security-related indicators from text
    Why: Identify potential security issues in logs and configurations
    """
    indicators = {
        'ip_addresses': [],
        'urls': [],
        'file_paths': [],
        'potential_secrets': [],
        'suspicious_patterns': []
    }
    
    # Extract IP addresses
    indicators['ip_addresses'] = re.findall(DevOpsRegexPatterns.IPV4, text)
    
    # Extract URLs
    indicators['urls'] = re.findall(DevOpsRegexPatterns.HTTP_URL, text)
    
    # Extract file paths
    indicators['file_paths'] = re.findall(DevOpsRegexPatterns.FILE_PATH, text)
    
    # Look for potential secrets
    secret_patterns = [
        (r'password\s*[=:]\s*[^\s]+', 'password'),
        (r'api[_-]?key\s*[=:]\s*[^\s]+', 'api_key'),
        (r'secret\s*[=:]\s*[^\s]+', 'secret'),
        (r'token\s*[=:]\s*[^\s]+', 'token')
    ]
    
    for pattern, secret_type in secret_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            indicators['potential_secrets'].extend([f"{secret_type}: {match}" for match in matches])
    
    # Look for suspicious patterns
    suspicious_patterns = [
        (r'(?:rm\s+-rf|del\s+/[fs])', 'dangerous_command'),
        (r'(?:DROP\s+TABLE|DELETE\s+FROM)', 'sql_injection'),
        (r'(?:<script|javascript:)', 'xss_attempt'),
        (r'(?:\.\./){2,}', 'path_traversal')
    ]
    
    for pattern, threat_type in suspicious_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            indicators['suspicious_patterns'].append(threat_type)
    
    return indicators

def parse_performance_metrics(log_text: str) -> List[Dict[str, any]]:
    """
    Extract performance metrics from logs
    Why: Monitor application performance and identify bottlenecks
    """
    metrics = []
    
    # Response time patterns
    response_time_patterns = [
        r'response[_\s]time[:\s]*(\d+(?:\.\d+)?)\s*(ms|s)',
        r'took\s+(\d+(?:\.\d+)?)\s*(ms|s)',
        r'duration[:\s]*(\d+(?:\.\d+)?)\s*(ms|s)'
    ]
    
    for pattern in response_time_patterns:
        matches = re.finditer(pattern, log_text, re.IGNORECASE)
        for match in matches:
            value = float(match.group(1))
            unit = match.group(2).lower()
            
            # Convert to milliseconds
            if unit == 's':
                value *= 1000
            
            metrics.append({
                'type': 'response_time',
                'value': value,
                'unit': 'ms'
            })
    
    # Memory usage patterns
    memory_patterns = [
        r'memory[_\s]usage[:\s]*(\d+(?:\.\d+)?)\s*(MB|GB|KB)',
        r'heap[_\s]size[:\s]*(\d+(?:\.\d+)?)\s*(MB|GB|KB)'
    ]
    
    for pattern in memory_patterns:
        matches = re.finditer(pattern, log_text, re.IGNORECASE)
        for match in matches:
            value = float(match.group(1))
            unit = match.group(2).upper()
            
            metrics.append({
                'type': 'memory_usage',
                'value': value,
                'unit': unit
            })
    
    # CPU usage patterns
    cpu_pattern = r'cpu[_\s]usage[:\s]*(\d+(?:\.\d+)?)%?'
    matches = re.finditer(cpu_pattern, log_text, re.IGNORECASE)
    for match in matches:
        value = float(match.group(1))
        metrics.append({
            'type': 'cpu_usage',
            'value': value,
            'unit': 'percent'
        })
    
    return metrics

def extract_error_details(error_text: str) -> Dict[str, any]:
    """
    Extract detailed information from error messages
    Why: Categorize and analyze errors for better debugging
    """
    error_info = {
        'type': 'unknown',
        'message': '',
        'file': '',
        'line': '',
        'stack_trace': '',
        'severity': 'medium'
    }
    
    # Extract exception type and message
    exception_match = re.search(DevOpsRegexPatterns.EXCEPTION, error_text)
    if exception_match:
        error_info['type'] = exception_match.group(1)
        error_info['message'] = exception_match.group(2)
    
    # Extract file and line number
    file_line_pattern = r'File "([^"]+)", line (\d+)'
    file_match = re.search(file_line_pattern, error_text)
    if file_match:
        error_info['file'] = file_match.group(1)
        error_info['line'] = file_match.group(2)
    
    # Extract stack trace
    stack_match = re.search(DevOpsRegexPatterns.STACK_TRACE, error_text, re.DOTALL)
    if stack_match:
        error_info['stack_trace'] = stack_match.group(0)
    
    # Determine severity based on error type
    critical_errors = ['OutOfMemoryError', 'StackOverflowError', 'SystemExit']
    high_errors = ['ConnectionError', 'TimeoutError', 'DatabaseError']
    
    if error_info['type'] in critical_errors:
        error_info['severity'] = 'critical'
    elif error_info['type'] in high_errors:
        error_info['severity'] = 'high'
    elif 'Error' in error_info['type']:
        error_info['severity'] = 'medium'
    else:
        error_info['severity'] = 'low'
    
    return error_info

def sanitize_log_for_storage(log_text: str) -> str:
    """
    Sanitize log text for safe storage and display
    Why: Remove sensitive information and prevent injection attacks
    """
    # Remove potential secrets
    sanitized = re.sub(r'(password|token|key|secret)\s*[=:]\s*[^\s]+', 
                      r'\1=***REDACTED***', log_text, flags=re.IGNORECASE)
    
    # Remove credit card numbers
    sanitized = re.sub(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b', 
                      'XXXX-XXXX-XXXX-XXXX', sanitized)
    
    # Remove email addresses (optional, depending on requirements)
    sanitized = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', 
                      'user@example.com', sanitized)
    
    # Remove potential SQL injection attempts
    sanitized = re.sub(r'(?:DROP\s+TABLE|DELETE\s+FROM|INSERT\s+INTO)', 
                      '[SQL_COMMAND_BLOCKED]', sanitized, flags=re.IGNORECASE)
    
    # Remove script tags
    sanitized = re.sub(r'<script[^>]*>.*?</script>', '[SCRIPT_BLOCKED]', 
                      sanitized, flags=re.IGNORECASE | re.DOTALL)
    
    return sanitized

if __name__ == "__main__":
    # Example 1: Log parsing
    sample_logs = [
        '192.168.1.100 - - [15/Jan/2024:10:30:15 +0000] "GET /api/users HTTP/1.1" 200 1234 "-" "Mozilla/5.0"',
        '[2024-01-15 10:30:15] ERROR database: Connection timeout after 30s',
        'Jan 15 10:30:15 server01 nginx: worker process 1234 exited on signal 11'
    ]
    
    for log in sample_logs:
        components = extract_log_components(log)
        print(f"Log format: {components.get('format', 'unknown')}")
        if 'ip' in components:
            print(f"  IP: {components['ip']}")
        if 'level' in components:
            print(f"  Level: {components['level']}")
    
    # Example 2: Configuration validation
    config = {
        'admin_email': 'admin@example.com',
        'api_url': 'https://api.example.com',
        'server_port': '8080',
        'timeout_duration': '30s'
    }
    
    validation_errors = validate_configuration_values(config)
    if validation_errors:
        print(f"Configuration errors: {validation_errors}")
    else:
        print("Configuration is valid")
    
    # Example 3: Security indicators
    suspicious_text = """
    password=secret123
    Accessing file ../../etc/passwd
    <script>alert('xss')</script>
    """
    
    security_indicators = extract_security_indicators(suspicious_text)
    print(f"Security indicators found: {len(security_indicators['potential_secrets'])} secrets, "
          f"{len(security_indicators['suspicious_patterns'])} suspicious patterns")
    
    # Example 4: Performance metrics
    perf_log = "Request completed in 250ms, memory usage: 512MB, CPU usage: 75%"
    metrics = parse_performance_metrics(perf_log)
    print(f"Extracted {len(metrics)} performance metrics")
    
    # Example 5: Error analysis
    error_text = """
    Traceback (most recent call last):
      File "/app/main.py", line 42, in process_request
        result = database.query(sql)
    ConnectionError: Unable to connect to database
    """
    
    error_details = extract_error_details(error_text)
    print(f"Error type: {error_details['type']}, severity: {error_details['severity']}")
    
    print("Regex patterns script ready!")