#!/usr/bin/env python3
"""
Containerization and Orchestration Scripts
Topics: Docker, Kubernetes, Helm, Container Security, Service Mesh
"""

import docker
import yaml
import subprocess
from typing import Dict, List, Optional
from dataclasses import dataclass
from kubernetes import client, config
import base64

@dataclass
class ContainerInfo:
    name: str
    image: str
    status: str
    ports: List[str]
    created: str

class DockerManager:
    """Docker container management"""
    
    def __init__(self):
        self.client = docker.from_env()
    
    def build_image(self, dockerfile_path: str, tag: str, build_args: Dict = None) -> bool:
        """Build Docker image with security best practices"""
        try:
            self.client.images.build(
                path=dockerfile_path,
                tag=tag,
                buildargs=build_args or {},
                nocache=True,
                rm=True
            )
            return True
        except docker.errors.BuildError as e:
            print(f"Build failed: {e}")
            return False
    
    def run_container(self, image: str, name: str, **kwargs) -> Optional[str]:
        """Run container with security configurations"""
        security_opts = [
            'no-new-privileges:true',
            'apparmor:docker-default'
        ]
        
        container = self.client.containers.run(
            image,
            name=name,
            detach=True,
            security_opt=security_opts,
            read_only=True,
            user='1000:1000',  # Non-root user
            **kwargs
        )
        return container.id
    
    def get_container_stats(self, container_id: str) -> Dict:
        """Get real-time container statistics"""
        container = self.client.containers.get(container_id)
        stats = container.stats(stream=False)
        
        # Calculate CPU percentage
        cpu_delta = stats['cpu_stats']['cpu_usage']['total_usage'] - \
                   stats['precpu_stats']['cpu_usage']['total_usage']
        system_delta = stats['cpu_stats']['system_cpu_usage'] - \
                      stats['precpu_stats']['system_cpu_usage']
        cpu_percent = (cpu_delta / system_delta) * 100.0
        
        # Memory usage
        memory_usage = stats['memory_stats']['usage']
        memory_limit = stats['memory_stats']['limit']
        memory_percent = (memory_usage / memory_limit) * 100.0
        
        return {
            'cpu_percent': cpu_percent,
            'memory_usage': memory_usage,
            'memory_percent': memory_percent,
            'network_rx': stats['networks']['eth0']['rx_bytes'],
            'network_tx': stats['networks']['eth0']['tx_bytes']
        }
    
    def scan_image_vulnerabilities(self, image: str) -> Dict:
        """Scan image for security vulnerabilities using Trivy"""
        try:
            result = subprocess.run([
                'trivy', 'image', '--format', 'json', image
            ], capture_output=True, text=True, check=True)
            
            return json.loads(result.stdout)
        except subprocess.CalledProcessError:
            return {'error': 'Vulnerability scan failed'}

class KubernetesManager:
    """Kubernetes cluster management"""
    
    def __init__(self, kubeconfig_path: str = None):
        if kubeconfig_path:
            config.load_kube_config(config_file=kubeconfig_path)
        else:
            config.load_incluster_config()
        
        self.v1 = client.CoreV1Api()
        self.apps_v1 = client.AppsV1Api()
        self.networking_v1 = client.NetworkingV1Api()
    
    def create_deployment(self, name: str, image: str, namespace: str = 'default', 
                         replicas: int = 3, resources: Dict = None) -> bool:
        """Create Kubernetes deployment with best practices"""
        
        # Resource limits and requests
        default_resources = {
            'requests': {'cpu': '100m', 'memory': '128Mi'},
            'limits': {'cpu': '500m', 'memory': '512Mi'}
        }
        resources = resources or default_resources
        
        # Security context
        security_context = client.V1SecurityContext(
            run_as_non_root=True,
            run_as_user=1000,
            read_only_root_filesystem=True,
            allow_privilege_escalation=False
        )
        
        # Container spec
        container = client.V1Container(
            name=name,
            image=image,
            resources=client.V1ResourceRequirements(**resources),
            security_context=security_context,
            liveness_probe=client.V1Probe(
                http_get=client.V1HTTPGetAction(path='/health', port=8080),
                initial_delay_seconds=30,
                period_seconds=10
            ),
            readiness_probe=client.V1Probe(
                http_get=client.V1HTTPGetAction(path='/ready', port=8080),
                initial_delay_seconds=5,
                period_seconds=5
            )
        )
        
        # Pod template
        template = client.V1PodTemplateSpec(
            metadata=client.V1ObjectMeta(labels={'app': name}),
            spec=client.V1PodSpec(containers=[container])
        )
        
        # Deployment spec
        spec = client.V1DeploymentSpec(
            replicas=replicas,
            selector=client.V1LabelSelector(match_labels={'app': name}),
            template=template,
            strategy=client.V1DeploymentStrategy(
                type='RollingUpdate',
                rolling_update=client.V1RollingUpdateDeployment(
                    max_surge='25%',
                    max_unavailable='25%'
                )
            )
        )
        
        deployment = client.V1Deployment(
            api_version='apps/v1',
            kind='Deployment',
            metadata=client.V1ObjectMeta(name=name),
            spec=spec
        )
        
        try:
            self.apps_v1.create_namespaced_deployment(namespace, deployment)
            return True
        except client.ApiException as e:
            print(f"Failed to create deployment: {e}")
            return False
    
    def create_hpa(self, deployment_name: str, namespace: str = 'default',
                   min_replicas: int = 2, max_replicas: int = 10,
                   cpu_target: int = 70) -> bool:
        """Create Horizontal Pod Autoscaler"""
        
        hpa = client.V2HorizontalPodAutoscaler(
            api_version='autoscaling/v2',
            kind='HorizontalPodAutoscaler',
            metadata=client.V1ObjectMeta(name=f"{deployment_name}-hpa"),
            spec=client.V2HorizontalPodAutoscalerSpec(
                scale_target_ref=client.V2CrossVersionObjectReference(
                    api_version='apps/v1',
                    kind='Deployment',
                    name=deployment_name
                ),
                min_replicas=min_replicas,
                max_replicas=max_replicas,
                metrics=[
                    client.V2MetricSpec(
                        type='Resource',
                        resource=client.V2ResourceMetricSource(
                            name='cpu',
                            target=client.V2MetricTarget(
                                type='Utilization',
                                average_utilization=cpu_target
                            )
                        )
                    )
                ]
            )
        )
        
        try:
            # Note: Using apps_v1 client for HPA (adjust based on K8s version)
            self.apps_v1.create_namespaced_horizontal_pod_autoscaler(namespace, hpa)
            return True
        except client.ApiException as e:
            print(f"Failed to create HPA: {e}")
            return False
    
    def get_cluster_resources(self) -> Dict:
        """Get cluster resource utilization"""
        nodes = self.v1.list_node()
        pods = self.v1.list_pod_for_all_namespaces()
        
        total_cpu = 0
        total_memory = 0
        used_cpu = 0
        used_memory = 0
        
        for node in nodes.items:
            # Get node capacity
            capacity = node.status.capacity
            total_cpu += int(capacity['cpu'])
            total_memory += self._parse_memory(capacity['memory'])
        
        for pod in pods.items:
            if pod.status.phase == 'Running':
                for container in pod.spec.containers:
                    if container.resources and container.resources.requests:
                        requests = container.resources.requests
                        if 'cpu' in requests:
                            used_cpu += self._parse_cpu(requests['cpu'])
                        if 'memory' in requests:
                            used_memory += self._parse_memory(requests['memory'])
        
        return {
            'total_cpu': total_cpu,
            'used_cpu': used_cpu,
            'cpu_utilization': (used_cpu / total_cpu) * 100 if total_cpu > 0 else 0,
            'total_memory': total_memory,
            'used_memory': used_memory,
            'memory_utilization': (used_memory / total_memory) * 100 if total_memory > 0 else 0
        }
    
    def _parse_cpu(self, cpu_str: str) -> float:
        """Parse CPU string to float (cores)"""
        if cpu_str.endswith('m'):
            return float(cpu_str[:-1]) / 1000
        return float(cpu_str)
    
    def _parse_memory(self, memory_str: str) -> int:
        """Parse memory string to bytes"""
        units = {'Ki': 1024, 'Mi': 1024**2, 'Gi': 1024**3}
        for unit, multiplier in units.items():
            if memory_str.endswith(unit):
                return int(memory_str[:-2]) * multiplier
        return int(memory_str)

class HelmManager:
    """Helm chart management"""
    
    def __init__(self):
        pass
    
    def install_chart(self, release_name: str, chart_path: str, 
                     namespace: str = 'default', values: Dict = None) -> bool:
        """Install Helm chart"""
        cmd = ['helm', 'install', release_name, chart_path, '--namespace', namespace]
        
        if values:
            # Create temporary values file
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                yaml.dump(values, f)
                cmd.extend(['--values', f.name])
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"Helm install failed: {e}")
            return False
    
    def create_chart_template(self, chart_name: str) -> Dict:
        """Create basic Helm chart template"""
        return {
            'Chart.yaml': {
                'apiVersion': 'v2',
                'name': chart_name,
                'version': '0.1.0',
                'description': f'A Helm chart for {chart_name}'
            },
            'values.yaml': {
                'replicaCount': 3,
                'image': {
                    'repository': f'{chart_name}',
                    'tag': 'latest',
                    'pullPolicy': 'IfNotPresent'
                },
                'service': {
                    'type': 'ClusterIP',
                    'port': 80
                },
                'resources': {
                    'limits': {'cpu': '500m', 'memory': '512Mi'},
                    'requests': {'cpu': '100m', 'memory': '128Mi'}
                }
            }
        }

class ServiceMeshManager:
    """Istio service mesh management"""
    
    def __init__(self):
        pass
    
    def create_virtual_service(self, service_name: str, namespace: str,
                              routes: List[Dict]) -> Dict:
        """Create Istio VirtualService for traffic management"""
        return {
            'apiVersion': 'networking.istio.io/v1beta1',
            'kind': 'VirtualService',
            'metadata': {
                'name': f'{service_name}-vs',
                'namespace': namespace
            },
            'spec': {
                'hosts': [service_name],
                'http': routes
            }
        }
    
    def create_destination_rule(self, service_name: str, namespace: str,
                               subsets: List[Dict]) -> Dict:
        """Create Istio DestinationRule for load balancing"""
        return {
            'apiVersion': 'networking.istio.io/v1beta1',
            'kind': 'DestinationRule',
            'metadata': {
                'name': f'{service_name}-dr',
                'namespace': namespace
            },
            'spec': {
                'host': service_name,
                'trafficPolicy': {
                    'loadBalancer': {
                        'simple': 'LEAST_CONN'
                    }
                },
                'subsets': subsets
            }
        }

# Interview scenarios
if __name__ == "__main__":
    # Interview Question: How do you implement zero-downtime deployments?
    k8s_mgr = KubernetesManager()
    
    # Interview Question: How do you handle container security?
    docker_mgr = DockerManager()
    
    # Interview Question: How do you manage microservices communication?
    service_mesh = ServiceMeshManager()
    
    print("Containerization and orchestration scripts ready for interview prep!")