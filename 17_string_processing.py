#!/usr/bin/env python3
"""
String Processing for DevOps - Script 17
Why: Text processing is essential for log analysis, config parsing, and automation
"""

import re
from typing import List, Dict, Tuple, Optional
from collections import defaultdict
import json

def parse_log_entry(log_line: str) -> Dict[str, str]:
    """
    Parse structured log entry into components
    Why: Extract meaningful data from log files for analysis
    """
    # Common log format: [timestamp] LEVEL service: message
    pattern = r'\[([^\]]+)\]\s+(\w+)\s+([^:]+):\s*(.*)'
    
    match = re.match(pattern, log_line)
    if match:
        return {
            'timestamp': match.group(1),
            'level': match.group(2),
            'service': match.group(3).strip(),
            'message': match.group(4)
        }
    
    # Fallback for unstructured logs
    return {
        'timestamp': '',
        'level': 'UNKNOWN',
        'service': 'unknown',
        'message': log_line.strip()
    }

def extract_ip_addresses(text: str) -> List[str]:
    """
    Extract all IP addresses from text
    Why: Find IP addresses in logs for security analysis
    """
    # IPv4 pattern
    ipv4_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
    
    # IPv6 pattern (simplified)
    ipv6_pattern = r'\b(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}\b'
    
    ipv4_addresses = re.findall(ipv4_pattern, text)
    ipv6_addresses = re.findall(ipv6_pattern, text)
    
    return ipv4_addresses + ipv6_addresses

def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for safe filesystem operations
    Why: Prevent path traversal and invalid characters in filenames
    """
    # Remove or replace dangerous characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove leading/trailing dots and spaces
    sanitized = sanitized.strip('. ')
    
    # Limit length
    if len(sanitized) > 255:
        sanitized = sanitized[:255]
    
    # Ensure not empty
    if not sanitized:
        sanitized = 'unnamed_file'
    
    return sanitized

def parse_key_value_pairs(text: str, delimiter: str = '=') -> Dict[str, str]:
    """
    Parse key-value pairs from text
    Why: Extract configuration parameters from various formats
    """
    pairs = {}
    
    # Split by lines and process each
    for line in text.strip().split('\n'):
        line = line.strip()
        
        # Skip empty lines and comments
        if not line or line.startswith('#'):
            continue
        
        # Split on delimiter
        if delimiter in line:
            key, value = line.split(delimiter, 1)  # Split only on first occurrence
            key = key.strip()
            value = value.strip()
            
            # Remove quotes if present
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
            elif value.startswith("'") and value.endswith("'"):
                value = value[1:-1]
            
            pairs[key] = value
    
    return pairs

def format_bytes(bytes_value: int) -> str:
    """
    Format bytes into human-readable string
    Why: Display file sizes and memory usage in readable format
    """
    units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    
    size = float(bytes_value)
    unit_index = 0
    
    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1
    
    return f"{size:.2f} {units[unit_index]}"

def parse_duration(duration_str: str) -> int:
    """
    Parse duration string into seconds
    Why: Handle timeout and interval configurations in various formats
    """
    # Handle formats like: "30s", "5m", "2h", "1d"
    pattern = r'(\d+)([smhd]?)'
    
    match = re.match(pattern, duration_str.lower())
    if not match:
        return 0
    
    value = int(match.group(1))
    unit = match.group(2) or 's'  # Default to seconds
    
    multipliers = {
        's': 1,
        'm': 60,
        'h': 3600,
        'd': 86400
    }
    
    return value * multipliers.get(unit, 1)

def mask_sensitive_data(text: str) -> str:
    """
    Mask sensitive information in text
    Why: Protect secrets when logging or displaying configuration
    """
    patterns = [
        # Credit card numbers
        (r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b', 'XXXX-XXXX-XXXX-XXXX'),
        
        # Email addresses
        (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', 'user@example.com'),
        
        # API keys (assuming they're long alphanumeric strings)
        (r'\b[A-Za-z0-9]{32,}\b', 'API_KEY_MASKED'),
        
        # Passwords in key=value format
        (r'(password\s*=\s*)[^\s]+', r'\1***MASKED***'),
        
        # JWT tokens
        (r'\beyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\b', 'JWT_TOKEN_MASKED')
    ]
    
    masked_text = text
    for pattern, replacement in patterns:
        masked_text = re.sub(pattern, replacement, masked_text, flags=re.IGNORECASE)
    
    return masked_text

def extract_urls(text: str) -> List[str]:
    """
    Extract URLs from text
    Why: Find service endpoints and external dependencies in logs
    """
    # URL pattern
    url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
    
    urls = re.findall(url_pattern, text)
    return urls

def normalize_service_name(service_name: str) -> str:
    """
    Normalize service name for consistent naming
    Why: Ensure consistent service naming across different systems
    """
    # Convert to lowercase
    normalized = service_name.lower()
    
    # Replace spaces and special characters with hyphens
    normalized = re.sub(r'[^a-z0-9]+', '-', normalized)
    
    # Remove leading/trailing hyphens
    normalized = normalized.strip('-')
    
    # Ensure it starts with a letter
    if normalized and not normalized[0].isalpha():
        normalized = 'service-' + normalized
    
    return normalized

def parse_version_string(version: str) -> Tuple[int, int, int]:
    """
    Parse semantic version string
    Why: Compare versions for deployment and compatibility checks
    """
    # Remove 'v' prefix if present
    version = version.lstrip('v')
    
    # Extract major.minor.patch
    pattern = r'(\d+)\.(\d+)\.(\d+)'
    match = re.match(pattern, version)
    
    if match:
        return (int(match.group(1)), int(match.group(2)), int(match.group(3)))
    
    # Fallback for invalid versions
    return (0, 0, 0)

def generate_config_template(template_vars: Dict[str, str]) -> str:
    """
    Generate configuration file from template
    Why: Create environment-specific configs from templates
    """
    template = """
# Application Configuration
app_name = {app_name}
app_version = {app_version}
environment = {environment}

# Database Configuration
db_host = {db_host}
db_port = {db_port}
db_name = {db_name}

# Server Configuration
server_port = {server_port}
worker_count = {worker_count}
timeout = {timeout}

# Feature Flags
debug_mode = {debug_mode}
enable_metrics = {enable_metrics}
"""
    
    # Replace template variables
    try:
        return template.format(**template_vars)
    except KeyError as e:
        raise ValueError(f"Missing template variable: {e}")

def analyze_log_patterns(log_lines: List[str]) -> Dict[str, any]:
    """
    Analyze patterns in log lines
    Why: Identify common issues and trends in application logs
    """
    analysis = {
        'total_lines': len(log_lines),
        'error_count': 0,
        'warning_count': 0,
        'info_count': 0,
        'unique_services': set(),
        'error_patterns': defaultdict(int),
        'ip_addresses': set(),
        'urls': set()
    }
    
    for line in log_lines:
        # Count log levels
        if 'ERROR' in line.upper():
            analysis['error_count'] += 1
            
            # Extract error patterns
            if 'exception' in line.lower():
                analysis['error_patterns']['exception'] += 1
            elif 'timeout' in line.lower():
                analysis['error_patterns']['timeout'] += 1
            elif 'connection' in line.lower():
                analysis['error_patterns']['connection'] += 1
                
        elif 'WARNING' in line.upper():
            analysis['warning_count'] += 1
        elif 'INFO' in line.upper():
            analysis['info_count'] += 1
        
        # Parse log entry for service name
        parsed = parse_log_entry(line)
        if parsed['service'] != 'unknown':
            analysis['unique_services'].add(parsed['service'])
        
        # Extract IP addresses
        ips = extract_ip_addresses(line)
        analysis['ip_addresses'].update(ips)
        
        # Extract URLs
        urls = extract_urls(line)
        analysis['urls'].update(urls)
    
    # Convert sets to lists for JSON serialization
    analysis['unique_services'] = list(analysis['unique_services'])
    analysis['ip_addresses'] = list(analysis['ip_addresses'])
    analysis['urls'] = list(analysis['urls'])
    analysis['error_patterns'] = dict(analysis['error_patterns'])
    
    return analysis

if __name__ == "__main__":
    # Example log lines for testing
    sample_logs = [
        "[2024-01-15 10:30:15] INFO web-service: Request processed successfully",
        "[2024-01-15 10:30:16] ERROR database-service: Connection timeout to 192.168.1.100:5432",
        "[2024-01-15 10:30:17] WARNING auth-service: Invalid API key from 203.0.113.45",
        "[2024-01-15 10:30:18] INFO web-service: GET https://api.example.com/users completed"
    ]
    
    # Test log parsing
    for log in sample_logs:
        parsed = parse_log_entry(log)
        print(f"Parsed: {parsed['service']} - {parsed['level']}")
    
    # Test IP extraction
    text_with_ips = "Connection from 192.168.1.100 failed, trying 10.0.0.1"
    ips = extract_ip_addresses(text_with_ips)
    print(f"Found IPs: {ips}")
    
    # Test duration parsing
    durations = ["30s", "5m", "2h", "1d"]
    for duration in durations:
        seconds = parse_duration(duration)
        print(f"{duration} = {seconds} seconds")
    
    # Test byte formatting
    sizes = [1024, 1048576, 1073741824]
    for size in sizes:
        formatted = format_bytes(size)
        print(f"{size} bytes = {formatted}")
    
    # Test sensitive data masking
    sensitive_text = "password=secret123 and api_key=abcd1234567890efgh"
    masked = mask_sensitive_data(sensitive_text)
    print(f"Masked: {masked}")
    
    # Test log analysis
    analysis = analyze_log_patterns(sample_logs)
    print(f"Log analysis: {json.dumps(analysis, indent=2)}")
    
    print("String processing script ready!")