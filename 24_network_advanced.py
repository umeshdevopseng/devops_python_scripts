#!/usr/bin/env python3
"""
Advanced Network Operations - Script 24
Why: Network expertise is crucial for infrastructure design and troubleshooting
"""

import socket
import subprocess
import ipaddress
import requests
import concurrent.futures
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

@dataclass
class NetworkInterface:
    name: str
    ip_address: str
    netmask: str
    gateway: str
    status: str

@dataclass
class PortScanResult:
    host: str
    port: int
    status: str
    service: str
    response_time: float

class NetworkScanner:
    def __init__(self):
        self.common_ports = {
            22: 'SSH', 80: 'HTTP', 443: 'HTTPS', 21: 'FTP', 25: 'SMTP',
            53: 'DNS', 110: 'POP3', 143: 'IMAP', 993: 'IMAPS', 995: 'POP3S',
            3306: 'MySQL', 5432: 'PostgreSQL', 6379: 'Redis', 27017: 'MongoDB',
            8080: 'HTTP-Alt', 9090: 'Prometheus', 3000: 'Grafana', 5000: 'Flask'
        }
    
    def scan_port(self, host: str, port: int, timeout: float = 3.0) -> PortScanResult:
        """
        Scan single port on host
        Why: Interview question - How do you troubleshoot network connectivity?
        """
        start_time = time.time()
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            sock.close()
            
            response_time = time.time() - start_time
            status = 'open' if result == 0 else 'closed'
            service = self.common_ports.get(port, 'unknown')
            
            return PortScanResult(host, port, status, service, response_time)
            
        except Exception as e:
            response_time = time.time() - start_time
            return PortScanResult(host, port, 'error', str(e), response_time)
    
    def scan_host_ports(self, host: str, ports: List[int], max_workers: int = 50) -> List[PortScanResult]:
        """
        Scan multiple ports on host concurrently
        Why: Interview question - How do you efficiently scan network services?
        """
        results = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_port = {
                executor.submit(self.scan_port, host, port): port 
                for port in ports
            }
            
            for future in concurrent.futures.as_completed(future_to_port):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    port = future_to_port[future]
                    results.append(PortScanResult(host, port, 'error', str(e), 0.0))
        
        return sorted(results, key=lambda x: x.port)
    
    def discover_network_hosts(self, network: str, timeout: float = 1.0) -> List[str]:
        """
        Discover active hosts in network range
        Why: Interview question - How do you discover network topology?
        """
        try:
            net = ipaddress.ip_network(network, strict=False)
        except ValueError as e:
            return []
        
        active_hosts = []
        
        def ping_host(ip):
            try:
                # Use ping command for host discovery
                result = subprocess.run(
                    ['ping', '-c', '1', '-W', str(int(timeout * 1000)), str(ip)],
                    capture_output=True,
                    timeout=timeout + 1
                )
                return str(ip) if result.returncode == 0 else None
            except:
                return None
        
        # Limit to reasonable network sizes
        if net.num_addresses > 1024:
            print(f"Network too large ({net.num_addresses} addresses), limiting scan")
            hosts = list(net.hosts())[:1024]
        else:
            hosts = list(net.hosts())
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
            futures = [executor.submit(ping_host, ip) for ip in hosts]
            
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if result:
                    active_hosts.append(result)
        
        return sorted(active_hosts, key=ipaddress.ip_address)

class LoadBalancerHealthChecker:
    """
    Health checking for load balancer backends
    Why: Interview question - How do you implement health checking?
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.timeout = 10
    
    def check_http_health(self, url: str, expected_status: int = 200, 
                         expected_content: str = None) -> Dict:
        """Check HTTP endpoint health"""
        start_time = time.time()
        
        try:
            response = self.session.get(url)
            response_time = time.time() - start_time
            
            health_status = {
                'url': url,
                'status_code': response.status_code,
                'response_time': response_time,
                'healthy': response.status_code == expected_status,
                'content_length': len(response.content)
            }
            
            # Check expected content if specified
            if expected_content and expected_content not in response.text:
                health_status['healthy'] = False
                health_status['error'] = 'Expected content not found'
            
            return health_status
            
        except Exception as e:
            return {
                'url': url,
                'healthy': False,
                'error': str(e),
                'response_time': time.time() - start_time
            }
    
    def check_tcp_health(self, host: str, port: int, timeout: float = 5.0) -> Dict:
        """Check TCP port health"""
        start_time = time.time()
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            sock.close()
            
            response_time = time.time() - start_time
            
            return {
                'host': host,
                'port': port,
                'healthy': result == 0,
                'response_time': response_time
            }
            
        except Exception as e:
            return {
                'host': host,
                'port': port,
                'healthy': False,
                'error': str(e),
                'response_time': time.time() - start_time
            }
    
    def monitor_backend_pool(self, backends: List[Dict], check_interval: int = 30) -> Dict:
        """Monitor health of backend pool"""
        results = {
            'timestamp': time.time(),
            'healthy_backends': [],
            'unhealthy_backends': [],
            'total_backends': len(backends)
        }
        
        for backend in backends:
            if 'url' in backend:
                health = self.check_http_health(backend['url'])
            else:
                health = self.check_tcp_health(backend['host'], backend['port'])
            
            if health['healthy']:
                results['healthy_backends'].append(backend)
            else:
                results['unhealthy_backends'].append({**backend, 'error': health.get('error')})
        
        results['health_percentage'] = (
            len(results['healthy_backends']) / results['total_backends'] * 100
            if results['total_backends'] > 0 else 0
        )
        
        return results

class NetworkTroubleshooter:
    """
    Network troubleshooting utilities
    Why: Interview question - How do you troubleshoot network issues?
    """
    
    def traceroute(self, destination: str, max_hops: int = 30) -> List[Dict]:
        """Perform traceroute to destination"""
        try:
            result = subprocess.run(
                ['traceroute', '-m', str(max_hops), destination],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            hops = []
            for line in result.stdout.split('\n'):
                if line.strip() and not line.startswith('traceroute'):
                    parts = line.split()
                    if len(parts) >= 3:
                        hop_num = parts[0]
                        if hop_num.isdigit():
                            hops.append({
                                'hop': int(hop_num),
                                'host': parts[1] if len(parts) > 1 else 'unknown',
                                'raw_line': line.strip()
                            })
            
            return hops
            
        except Exception as e:
            return [{'error': str(e)}]
    
    def dns_lookup(self, hostname: str) -> Dict:
        """Perform comprehensive DNS lookup"""
        import dns.resolver
        
        results = {
            'hostname': hostname,
            'records': {},
            'errors': []
        }
        
        record_types = ['A', 'AAAA', 'CNAME', 'MX', 'TXT', 'NS']
        
        for record_type in record_types:
            try:
                answers = dns.resolver.resolve(hostname, record_type)
                results['records'][record_type] = [str(answer) for answer in answers]
            except Exception as e:
                results['errors'].append(f"{record_type}: {str(e)}")
        
        return results
    
    def network_latency_test(self, hosts: List[str], count: int = 10) -> Dict:
        """Test network latency to multiple hosts"""
        results = {}
        
        for host in hosts:
            try:
                result = subprocess.run(
                    ['ping', '-c', str(count), host],
                    capture_output=True,
                    text=True,
                    timeout=count + 10
                )
                
                # Parse ping statistics
                lines = result.stdout.split('\n')
                stats_line = [line for line in lines if 'min/avg/max' in line]
                
                if stats_line:
                    # Extract timing statistics
                    stats = stats_line[0].split('=')[1].strip().split('/')
                    results[host] = {
                        'min_ms': float(stats[0]),
                        'avg_ms': float(stats[1]),
                        'max_ms': float(stats[2]),
                        'success': True
                    }
                else:
                    results[host] = {'success': False, 'error': 'No statistics found'}
                    
            except Exception as e:
                results[host] = {'success': False, 'error': str(e)}
        
        return results
    
    def bandwidth_test(self, test_url: str, duration: int = 10) -> Dict:
        """Simple bandwidth test using HTTP download"""
        start_time = time.time()
        total_bytes = 0
        
        try:
            response = requests.get(test_url, stream=True, timeout=duration + 5)
            
            for chunk in response.iter_content(chunk_size=8192):
                if time.time() - start_time > duration:
                    break
                total_bytes += len(chunk)
            
            elapsed_time = time.time() - start_time
            bandwidth_mbps = (total_bytes * 8) / (elapsed_time * 1000000)  # Convert to Mbps
            
            return {
                'success': True,
                'duration_seconds': elapsed_time,
                'bytes_downloaded': total_bytes,
                'bandwidth_mbps': bandwidth_mbps
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'duration_seconds': time.time() - start_time
            }

class FirewallRuleManager:
    """
    Firewall rule management utilities
    Why: Interview question - How do you manage network security?
    """
    
    def generate_iptables_rules(self, rules_config: Dict) -> List[str]:
        """Generate iptables rules from configuration"""
        rules = []
        
        # Default policies
        rules.extend([
            'iptables -P INPUT DROP',
            'iptables -P FORWARD DROP',
            'iptables -P OUTPUT ACCEPT'
        ])
        
        # Allow loopback
        rules.extend([
            'iptables -A INPUT -i lo -j ACCEPT',
            'iptables -A OUTPUT -o lo -j ACCEPT'
        ])
        
        # Allow established connections
        rules.append('iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT')
        
        # Process allow rules
        for rule in rules_config.get('allow', []):
            if 'port' in rule:
                protocol = rule.get('protocol', 'tcp')
                port = rule['port']
                source = rule.get('source', '0.0.0.0/0')
                
                iptables_rule = f'iptables -A INPUT -p {protocol} --dport {port} -s {source} -j ACCEPT'
                rules.append(iptables_rule)
        
        # Process deny rules
        for rule in rules_config.get('deny', []):
            if 'source' in rule:
                source = rule['source']
                iptables_rule = f'iptables -A INPUT -s {source} -j DROP'
                rules.append(iptables_rule)
        
        return rules
    
    def validate_security_group_rules(self, sg_rules: List[Dict]) -> Dict:
        """Validate AWS security group rules"""
        validation_results = {
            'valid_rules': [],
            'invalid_rules': [],
            'warnings': [],
            'security_issues': []
        }
        
        for rule in sg_rules:
            rule_valid = True
            
            # Check required fields
            required_fields = ['protocol', 'port_range', 'source']
            for field in required_fields:
                if field not in rule:
                    validation_results['invalid_rules'].append({
                        'rule': rule,
                        'error': f'Missing required field: {field}'
                    })
                    rule_valid = False
                    break
            
            if not rule_valid:
                continue
            
            # Security checks
            if rule['source'] == '0.0.0.0/0':
                if rule['port_range'] in ['22', '3389', '1433', '3306']:
                    validation_results['security_issues'].append({
                        'rule': rule,
                        'issue': f'Dangerous: Port {rule["port_range"]} open to internet'
                    })
                else:
                    validation_results['warnings'].append({
                        'rule': rule,
                        'warning': 'Rule allows access from internet'
                    })
            
            # Port range validation
            if '-' in str(rule['port_range']):
                start, end = rule['port_range'].split('-')
                if int(end) - int(start) > 1000:
                    validation_results['warnings'].append({
                        'rule': rule,
                        'warning': 'Large port range may be overly permissive'
                    })
            
            if rule_valid:
                validation_results['valid_rules'].append(rule)
        
        return validation_results

class NetworkMonitoring:
    """
    Network monitoring and metrics collection
    Why: Interview question - How do you monitor network performance?
    """
    
    def collect_interface_stats(self) -> Dict:
        """Collect network interface statistics"""
        try:
            import psutil
            
            stats = {}
            net_io = psutil.net_io_counters(pernic=True)
            
            for interface, counters in net_io.items():
                stats[interface] = {
                    'bytes_sent': counters.bytes_sent,
                    'bytes_recv': counters.bytes_recv,
                    'packets_sent': counters.packets_sent,
                    'packets_recv': counters.packets_recv,
                    'errin': counters.errin,
                    'errout': counters.errout,
                    'dropin': counters.dropin,
                    'dropout': counters.dropout
                }
            
            return stats
            
        except ImportError:
            # Fallback to parsing /proc/net/dev on Linux
            try:
                with open('/proc/net/dev', 'r') as f:
                    lines = f.readlines()
                
                stats = {}
                for line in lines[2:]:  # Skip header lines
                    parts = line.split()
                    if len(parts) >= 16:
                        interface = parts[0].rstrip(':')
                        stats[interface] = {
                            'bytes_recv': int(parts[1]),
                            'packets_recv': int(parts[2]),
                            'bytes_sent': int(parts[9]),
                            'packets_sent': int(parts[10])
                        }
                
                return stats
                
            except Exception as e:
                return {'error': str(e)}
    
    def monitor_connection_states(self) -> Dict:
        """Monitor TCP connection states"""
        try:
            import psutil
            
            connections = psutil.net_connections()
            states = {}
            
            for conn in connections:
                state = conn.status
                states[state] = states.get(state, 0) + 1
            
            return {
                'connection_states': states,
                'total_connections': len(connections)
            }
            
        except Exception as e:
            return {'error': str(e)}

if __name__ == "__main__":
    # Example usage for interview demonstration
    scanner = NetworkScanner()
    health_checker = LoadBalancerHealthChecker()
    troubleshooter = NetworkTroubleshooter()
    
    print("Network Advanced Operations - Interview Ready!")
    print("Key concepts: Port scanning, Health checking, Troubleshooting, Security")