#!/usr/bin/env python3
"""
Network Operations for DevOps - Script 8
Why: Network connectivity and API interactions are fundamental to DevOps
"""

import requests
import socket
import urllib3
from typing import Dict, List, Optional
import time

# Disable SSL warnings for internal services
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def check_port_connectivity(host: str, port: int, timeout: int = 5) -> bool:
    """
    Check if a port is open on a host
    Why: Verify service availability before deployment
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)  # Set connection timeout
        result = sock.connect_ex((host, port))  # Returns 0 if successful
        sock.close()
        return result == 0
    except socket.gaierror:
        return False  # DNS resolution failed

def health_check_endpoint(url: str, expected_status: int = 200) -> Dict:
    """
    Perform HTTP health check on endpoint
    Why: Monitor service health in production
    """
    try:
        start_time = time.time()
        response = requests.get(
            url,
            timeout=10,           # 10-second timeout
            verify=False,         # Skip SSL verification for internal services
            allow_redirects=True  # Follow redirects
        )
        response_time = time.time() - start_time
        
        return {
            'healthy': response.status_code == expected_status,
            'status_code': response.status_code,
            'response_time': response_time,
            'content_length': len(response.content)
        }
    except requests.RequestException as e:
        return {
            'healthy': False,
            'error': str(e),
            'response_time': None
        }

def batch_health_checks(endpoints: List[str]) -> Dict:
    """
    Check multiple endpoints concurrently
    Why: Efficiently monitor multiple services
    """
    import concurrent.futures
    
    results = {}
    
    # Use ThreadPoolExecutor for concurrent requests
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        # Submit all health checks
        future_to_url = {
            executor.submit(health_check_endpoint, url): url 
            for url in endpoints
        }
        
        # Collect results as they complete
        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]
            try:
                results[url] = future.result()
            except Exception as e:
                results[url] = {'healthy': False, 'error': str(e)}
    
    return results

def get_public_ip() -> Optional[str]:
    """
    Get public IP address of current machine
    Why: Useful for dynamic DNS updates or security group rules
    """
    try:
        response = requests.get('https://httpbin.org/ip', timeout=5)
        return response.json()['origin']
    except:
        try:
            # Fallback service
            response = requests.get('https://api.ipify.org', timeout=5)
            return response.text.strip()
        except:
            return None

def download_file_with_progress(url: str, local_path: str) -> bool:
    """
    Download file with progress tracking
    Why: Download artifacts, configs, or updates safely
    """
    try:
        response = requests.get(url, stream=True)  # Stream to handle large files
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        
        with open(local_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):  # 8KB chunks
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    
                    # Show progress
                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        print(f"\rDownloading: {percent:.1f}%", end='', flush=True)
        
        print()  # New line after progress
        return True
        
    except Exception as e:
        print(f"Download failed: {e}")
        return False

def scan_network_range(network: str, port: int) -> List[str]:
    """
    Scan network range for open ports
    Why: Discover services in network for inventory
    """
    import ipaddress
    import concurrent.futures
    
    active_hosts = []
    
    try:
        # Parse network (e.g., "192.168.1.0/24")
        net = ipaddress.ip_network(network, strict=False)
        
        def check_host(ip):
            if check_port_connectivity(str(ip), port, timeout=1):
                return str(ip)
            return None
        
        # Scan hosts concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
            futures = [executor.submit(check_host, ip) for ip in net.hosts()]
            
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if result:
                    active_hosts.append(result)
    
    except Exception as e:
        print(f"Network scan failed: {e}")
    
    return active_hosts

if __name__ == "__main__":
    # Example: Check if database is accessible
    db_available = check_port_connectivity('localhost', 5432)
    print(f"Database available: {db_available}")
    
    # Example: Health check multiple services
    services = [
        'http://localhost:8080/health',
        'http://localhost:9090/metrics'
    ]
    health_results = batch_health_checks(services)
    print(f"Health check results: {health_results}")
    
    print("Network operations script ready!")