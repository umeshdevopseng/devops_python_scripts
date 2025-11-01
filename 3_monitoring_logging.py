#!/usr/bin/env python3
"""
Monitoring and Logging Scripts for DevOps
Topics: Prometheus, Grafana, ELK Stack, Custom Metrics, Alerting
"""

import time
import json
import logging
import requests
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from prometheus_client import Counter, Histogram, Gauge, start_http_server
import psutil

# Custom metrics for application monitoring
REQUEST_COUNT = Counter('app_requests_total', 'Total app requests', ['method', 'endpoint'])
REQUEST_LATENCY = Histogram('app_request_duration_seconds', 'Request latency')
ACTIVE_CONNECTIONS = Gauge('app_active_connections', 'Active connections')

@dataclass
class Alert:
    name: str
    severity: str
    message: str
    timestamp: datetime
    labels: Dict[str, str]

class PrometheusMetrics:
    """Custom Prometheus metrics collector"""
    
    def __init__(self):
        self.cpu_usage = Gauge('system_cpu_usage_percent', 'CPU usage percentage')
        self.memory_usage = Gauge('system_memory_usage_bytes', 'Memory usage in bytes')
        self.disk_usage = Gauge('system_disk_usage_percent', 'Disk usage percentage')
    
    def collect_system_metrics(self):
        """Collect and expose system metrics"""
        while True:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            self.cpu_usage.set(cpu_percent)
            
            # Memory metrics
            memory = psutil.virtual_memory()
            self.memory_usage.set(memory.used)
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            self.disk_usage.set(disk.percent)
            
            time.sleep(30)  # Collect every 30 seconds

class ElasticsearchLogger:
    """Custom Elasticsearch logging handler"""
    
    def __init__(self, es_host: str, index_prefix: str):
        self.es_host = es_host
        self.index_prefix = index_prefix
    
    def send_log(self, level: str, message: str, extra_fields: Dict = None):
        """Send structured log to Elasticsearch"""
        doc = {
            '@timestamp': datetime.utcnow().isoformat(),
            'level': level,
            'message': message,
            'service': 'python-app',
            'environment': 'production'
        }
        
        if extra_fields:
            doc.update(extra_fields)
        
        index_name = f"{self.index_prefix}-{datetime.now().strftime('%Y.%m.%d')}"
        url = f"{self.es_host}/{index_name}/_doc"
        
        try:
            requests.post(url, json=doc, timeout=5)
        except requests.RequestException as e:
            print(f"Failed to send log to Elasticsearch: {e}")

class AlertManager:
    """Custom alerting system"""
    
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
        self.alert_rules = []
    
    def add_rule(self, name: str, condition: callable, severity: str = 'warning'):
        """Add alerting rule"""
        self.alert_rules.append({
            'name': name,
            'condition': condition,
            'severity': severity
        })
    
    def check_alerts(self, metrics: Dict) -> List[Alert]:
        """Check all alert rules against current metrics"""
        alerts = []
        
        for rule in self.alert_rules:
            if rule['condition'](metrics):
                alert = Alert(
                    name=rule['name'],
                    severity=rule['severity'],
                    message=f"Alert triggered: {rule['name']}",
                    timestamp=datetime.now(),
                    labels={'service': 'monitoring'}
                )
                alerts.append(alert)
        
        return alerts
    
    def send_alert(self, alert: Alert):
        """Send alert to webhook"""
        payload = {
            'text': f"🚨 {alert.severity.upper()}: {alert.message}",
            'attachments': [{
                'color': 'danger' if alert.severity == 'critical' else 'warning',
                'fields': [
                    {'title': 'Alert', 'value': alert.name, 'short': True},
                    {'title': 'Time', 'value': alert.timestamp.isoformat(), 'short': True}
                ]
            }]
        }
        
        try:
            requests.post(self.webhook_url, json=payload, timeout=10)
        except requests.RequestException as e:
            print(f"Failed to send alert: {e}")

class LogAnalyzer:
    """Analyze logs for patterns and anomalies"""
    
    def __init__(self):
        self.error_patterns = [
            r'ERROR',
            r'FATAL',
            r'Exception',
            r'Traceback',
            r'500 Internal Server Error'
        ]
    
    def analyze_log_file(self, file_path: str) -> Dict:
        """Analyze log file for errors and patterns"""
        import re
        
        stats = {
            'total_lines': 0,
            'error_count': 0,
            'error_rate': 0.0,
            'top_errors': {},
            'time_range': {}
        }
        
        with open(file_path, 'r') as f:
            for line in f:
                stats['total_lines'] += 1
                
                # Check for error patterns
                for pattern in self.error_patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        stats['error_count'] += 1
                        stats['top_errors'][pattern] = stats['top_errors'].get(pattern, 0) + 1
                        break
        
        if stats['total_lines'] > 0:
            stats['error_rate'] = (stats['error_count'] / stats['total_lines']) * 100
        
        return stats
    
    def detect_anomalies(self, metrics_history: List[Dict]) -> List[Dict]:
        """Detect anomalies in metrics using simple statistical methods"""
        anomalies = []
        
        if len(metrics_history) < 10:
            return anomalies
        
        # Calculate moving average and standard deviation
        values = [m.get('cpu_usage', 0) for m in metrics_history[-10:]]
        avg = sum(values) / len(values)
        std_dev = (sum((x - avg) ** 2 for x in values) / len(values)) ** 0.5
        
        # Check if current value is anomalous (> 2 standard deviations)
        current_value = metrics_history[-1].get('cpu_usage', 0)
        if abs(current_value - avg) > 2 * std_dev:
            anomalies.append({
                'metric': 'cpu_usage',
                'value': current_value,
                'expected_range': (avg - 2*std_dev, avg + 2*std_dev),
                'timestamp': datetime.now().isoformat()
            })
        
        return anomalies

class GrafanaDashboard:
    """Grafana dashboard management"""
    
    def __init__(self, grafana_url: str, api_key: str):
        self.grafana_url = grafana_url.rstrip('/')
        self.headers = {'Authorization': f'Bearer {api_key}'}
    
    def create_dashboard(self, dashboard_config: Dict) -> str:
        """Create Grafana dashboard"""
        url = f"{self.grafana_url}/api/dashboards/db"
        response = requests.post(url, headers=self.headers, json=dashboard_config)
        
        if response.status_code == 200:
            return response.json().get('url', '')
        return None
    
    def get_dashboard_template(self) -> Dict:
        """Get basic dashboard template"""
        return {
            "dashboard": {
                "title": "Application Monitoring",
                "panels": [
                    {
                        "title": "CPU Usage",
                        "type": "graph",
                        "targets": [{"expr": "system_cpu_usage_percent"}]
                    },
                    {
                        "title": "Memory Usage",
                        "type": "graph", 
                        "targets": [{"expr": "system_memory_usage_bytes"}]
                    },
                    {
                        "title": "Request Rate",
                        "type": "graph",
                        "targets": [{"expr": "rate(app_requests_total[5m])"}]
                    }
                ]
            }
        }

# Interview scenarios and usage examples
if __name__ == "__main__":
    # Interview Question: How do you implement comprehensive monitoring?
    metrics = PrometheusMetrics()
    
    # Interview Question: How do you handle log aggregation at scale?
    es_logger = ElasticsearchLogger('http://localhost:9200', 'app-logs')
    
    # Interview Question: How do you implement intelligent alerting?
    alert_mgr = AlertManager('https://hooks.slack.com/webhook')
    alert_mgr.add_rule(
        'high_cpu',
        lambda m: m.get('cpu_usage', 0) > 80,
        'critical'
    )
    
    # Start Prometheus metrics server
    start_http_server(8000)
    print("Monitoring and logging scripts ready for interview prep!")