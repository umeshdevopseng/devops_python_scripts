#!/usr/bin/env python3
"""
Advanced Kubernetes Operations - Script 22
Why: Kubernetes expertise is essential for container orchestration interviews
"""

import yaml
import json
from typing import Dict, List, Optional
from kubernetes import client, config
from kubernetes.client.rest import ApiException

class KubernetesClusterManager:
    def __init__(self, kubeconfig_path: str = None):
        try:
            if kubeconfig_path:
                config.load_kube_config(config_file=kubeconfig_path)
            else:
                config.load_incluster_config()
        except:
            config.load_kube_config()  # Default kubeconfig
        
        self.v1 = client.CoreV1Api()
        self.apps_v1 = client.AppsV1Api()
        self.networking_v1 = client.NetworkingV1Api()
        self.autoscaling_v2 = client.AutoscalingV2Api()
        self.rbac_v1 = client.RbacAuthorizationV1Api()
    
    def create_production_deployment(self, app_name: str, image: str, namespace: str = 'default') -> Dict:
        """
        Create production-ready deployment with all best practices
        Why: Interview question - How do you deploy applications to Kubernetes?
        """
        # Security context - run as non-root
        security_context = client.V1SecurityContext(
            run_as_non_root=True,
            run_as_user=1000,
            run_as_group=3000,
            read_only_root_filesystem=True,
            allow_privilege_escalation=False,
            capabilities=client.V1Capabilities(drop=["ALL"])
        )
        
        # Resource requirements
        resources = client.V1ResourceRequirements(
            requests={"cpu": "100m", "memory": "128Mi"},
            limits={"cpu": "500m", "memory": "512Mi"}
        )
        
        # Probes for health checking
        liveness_probe = client.V1Probe(
            http_get=client.V1HTTPGetAction(path="/health", port=8080),
            initial_delay_seconds=30,
            period_seconds=10,
            timeout_seconds=5,
            failure_threshold=3
        )
        
        readiness_probe = client.V1Probe(
            http_get=client.V1HTTPGetAction(path="/ready", port=8080),
            initial_delay_seconds=5,
            period_seconds=5,
            timeout_seconds=3,
            failure_threshold=3
        )
        
        # Container definition
        container = client.V1Container(
            name=app_name,
            image=image,
            ports=[client.V1ContainerPort(container_port=8080)],
            security_context=security_context,
            resources=resources,
            liveness_probe=liveness_probe,
            readiness_probe=readiness_probe,
            env=[
                client.V1EnvVar(name="ENV", value="production"),
                client.V1EnvVar(name="LOG_LEVEL", value="INFO")
            ],
            volume_mounts=[
                client.V1VolumeMount(name="tmp", mount_path="/tmp"),
                client.V1VolumeMount(name="cache", mount_path="/app/cache")
            ]
        )
        
        # Pod template
        pod_template = client.V1PodTemplateSpec(
            metadata=client.V1ObjectMeta(
                labels={"app": app_name, "version": "v1"},
                annotations={"prometheus.io/scrape": "true", "prometheus.io/port": "8080"}
            ),
            spec=client.V1PodSpec(
                containers=[container],
                volumes=[
                    client.V1Volume(name="tmp", empty_dir={}),
                    client.V1Volume(name="cache", empty_dir={})
                ],
                service_account_name=f"{app_name}-sa",
                automount_service_account_token=False,
                security_context=client.V1PodSecurityContext(
                    run_as_non_root=True,
                    fs_group=2000
                )
            )
        )
        
        # Deployment spec
        deployment_spec = client.V1DeploymentSpec(
            replicas=3,
            selector=client.V1LabelSelector(match_labels={"app": app_name}),
            template=pod_template,
            strategy=client.V1DeploymentStrategy(
                type="RollingUpdate",
                rolling_update=client.V1RollingUpdateDeployment(
                    max_surge="25%",
                    max_unavailable="25%"
                )
            )
        )
        
        deployment = client.V1Deployment(
            api_version="apps/v1",
            kind="Deployment",
            metadata=client.V1ObjectMeta(name=app_name, namespace=namespace),
            spec=deployment_spec
        )
        
        try:
            result = self.apps_v1.create_namespaced_deployment(namespace, deployment)
            return {"status": "created", "name": result.metadata.name}
        except ApiException as e:
            return {"status": "error", "message": str(e)}
    
    def setup_horizontal_pod_autoscaler(self, deployment_name: str, namespace: str = 'default') -> Dict:
        """
        Setup HPA with CPU and memory metrics
        Why: Interview question - How do you handle auto-scaling in Kubernetes?
        """
        hpa = client.V2HorizontalPodAutoscaler(
            api_version="autoscaling/v2",
            kind="HorizontalPodAutoscaler",
            metadata=client.V1ObjectMeta(name=f"{deployment_name}-hpa", namespace=namespace),
            spec=client.V2HorizontalPodAutoscalerSpec(
                scale_target_ref=client.V2CrossVersionObjectReference(
                    api_version="apps/v1",
                    kind="Deployment",
                    name=deployment_name
                ),
                min_replicas=2,
                max_replicas=20,
                metrics=[
                    client.V2MetricSpec(
                        type="Resource",
                        resource=client.V2ResourceMetricSource(
                            name="cpu",
                            target=client.V2MetricTarget(
                                type="Utilization",
                                average_utilization=70
                            )
                        )
                    ),
                    client.V2MetricSpec(
                        type="Resource",
                        resource=client.V2ResourceMetricSource(
                            name="memory",
                            target=client.V2MetricTarget(
                                type="Utilization",
                                average_utilization=80
                            )
                        )
                    )
                ],
                behavior=client.V2HorizontalPodAutoscalerBehavior(
                    scale_up=client.V2HPAScalingRules(
                        stabilization_window_seconds=60,
                        policies=[
                            client.V2HPAScalingPolicy(
                                type="Percent",
                                value=100,
                                period_seconds=15
                            )
                        ]
                    ),
                    scale_down=client.V2HPAScalingRules(
                        stabilization_window_seconds=300,
                        policies=[
                            client.V2HPAScalingPolicy(
                                type="Percent",
                                value=10,
                                period_seconds=60
                            )
                        ]
                    )
                )
            )
        )
        
        try:
            result = self.autoscaling_v2.create_namespaced_horizontal_pod_autoscaler(namespace, hpa)
            return {"status": "created", "name": result.metadata.name}
        except ApiException as e:
            return {"status": "error", "message": str(e)}
    
    def create_network_policy(self, app_name: str, namespace: str = 'default') -> Dict:
        """
        Create network policy for micro-segmentation
        Why: Interview question - How do you secure network traffic in Kubernetes?
        """
        network_policy = client.V1NetworkPolicy(
            api_version="networking.k8s.io/v1",
            kind="NetworkPolicy",
            metadata=client.V1ObjectMeta(name=f"{app_name}-netpol", namespace=namespace),
            spec=client.V1NetworkPolicySpec(
                pod_selector=client.V1LabelSelector(match_labels={"app": app_name}),
                policy_types=["Ingress", "Egress"],
                ingress=[
                    client.V1NetworkPolicyIngressRule(
                        from_=[
                            client.V1NetworkPolicyPeer(
                                namespace_selector=client.V1LabelSelector(
                                    match_labels={"name": namespace}
                                )
                            )
                        ],
                        ports=[
                            client.V1NetworkPolicyPort(protocol="TCP", port=8080)
                        ]
                    )
                ],
                egress=[
                    client.V1NetworkPolicyEgressRule(
                        to=[
                            client.V1NetworkPolicyPeer(
                                namespace_selector=client.V1LabelSelector(
                                    match_labels={"name": "kube-system"}
                                )
                            )
                        ],
                        ports=[
                            client.V1NetworkPolicyPort(protocol="TCP", port=53),
                            client.V1NetworkPolicyPort(protocol="UDP", port=53)
                        ]
                    )
                ]
            )
        )
        
        try:
            result = self.networking_v1.create_namespaced_network_policy(namespace, network_policy)
            return {"status": "created", "name": result.metadata.name}
        except ApiException as e:
            return {"status": "error", "message": str(e)}
    
    def setup_rbac(self, service_account: str, namespace: str = 'default') -> Dict:
        """
        Setup RBAC with least privilege principle
        Why: Interview question - How do you implement security in Kubernetes?
        """
        # Create ServiceAccount
        sa = client.V1ServiceAccount(
            metadata=client.V1ObjectMeta(name=service_account, namespace=namespace)
        )
        
        # Create Role with minimal permissions
        role = client.V1Role(
            metadata=client.V1ObjectMeta(name=f"{service_account}-role", namespace=namespace),
            rules=[
                client.V1PolicyRule(
                    api_groups=[""],
                    resources=["configmaps", "secrets"],
                    verbs=["get", "list"]
                ),
                client.V1PolicyRule(
                    api_groups=[""],
                    resources=["pods"],
                    verbs=["get", "list", "watch"]
                )
            ]
        )
        
        # Create RoleBinding
        role_binding = client.V1RoleBinding(
            metadata=client.V1ObjectMeta(name=f"{service_account}-binding", namespace=namespace),
            subjects=[
                client.V1Subject(
                    kind="ServiceAccount",
                    name=service_account,
                    namespace=namespace
                )
            ],
            role_ref=client.V1RoleRef(
                kind="Role",
                name=f"{service_account}-role",
                api_group="rbac.authorization.k8s.io"
            )
        )
        
        try:
            self.v1.create_namespaced_service_account(namespace, sa)
            self.rbac_v1.create_namespaced_role(namespace, role)
            self.rbac_v1.create_namespaced_role_binding(namespace, role_binding)
            return {"status": "created", "service_account": service_account}
        except ApiException as e:
            return {"status": "error", "message": str(e)}
    
    def create_ingress_with_ssl(self, app_name: str, host: str, namespace: str = 'default') -> Dict:
        """
        Create Ingress with SSL termination and rate limiting
        Why: Interview question - How do you expose applications securely?
        """
        ingress = client.V1Ingress(
            api_version="networking.k8s.io/v1",
            kind="Ingress",
            metadata=client.V1ObjectMeta(
                name=f"{app_name}-ingress",
                namespace=namespace,
                annotations={
                    "kubernetes.io/ingress.class": "nginx",
                    "cert-manager.io/cluster-issuer": "letsencrypt-prod",
                    "nginx.ingress.kubernetes.io/rate-limit": "100",
                    "nginx.ingress.kubernetes.io/rate-limit-window": "1m",
                    "nginx.ingress.kubernetes.io/ssl-redirect": "true"
                }
            ),
            spec=client.V1IngressSpec(
                tls=[
                    client.V1IngressTLS(
                        hosts=[host],
                        secret_name=f"{app_name}-tls"
                    )
                ],
                rules=[
                    client.V1IngressRule(
                        host=host,
                        http=client.V1HTTPIngressRuleValue(
                            paths=[
                                client.V1HTTPIngressPath(
                                    path="/",
                                    path_type="Prefix",
                                    backend=client.V1IngressBackend(
                                        service=client.V1IngressServiceBackend(
                                            name=app_name,
                                            port=client.V1ServiceBackendPort(number=80)
                                        )
                                    )
                                )
                            ]
                        )
                    )
                ]
            )
        )
        
        try:
            result = self.networking_v1.create_namespaced_ingress(namespace, ingress)
            return {"status": "created", "name": result.metadata.name, "host": host}
        except ApiException as e:
            return {"status": "error", "message": str(e)}
    
    def get_cluster_health(self) -> Dict:
        """
        Get comprehensive cluster health status
        Why: Interview question - How do you monitor Kubernetes cluster health?
        """
        health = {
            "nodes": {"ready": 0, "not_ready": 0},
            "pods": {"running": 0, "pending": 0, "failed": 0},
            "resource_usage": {"cpu_requests": 0, "memory_requests": 0}
        }
        
        # Check node status
        nodes = self.v1.list_node()
        for node in nodes.items:
            for condition in node.status.conditions:
                if condition.type == "Ready":
                    if condition.status == "True":
                        health["nodes"]["ready"] += 1
                    else:
                        health["nodes"]["not_ready"] += 1
        
        # Check pod status
        pods = self.v1.list_pod_for_all_namespaces()
        for pod in pods.items:
            phase = pod.status.phase
            if phase == "Running":
                health["pods"]["running"] += 1
            elif phase == "Pending":
                health["pods"]["pending"] += 1
            elif phase == "Failed":
                health["pods"]["failed"] += 1
        
        return health

def generate_kubernetes_manifests(app_name: str, image: str) -> Dict[str, str]:
    """
    Generate complete Kubernetes manifests
    Why: Interview question - How do you structure Kubernetes deployments?
    """
    manifests = {}
    
    # Deployment manifest
    deployment = {
        "apiVersion": "apps/v1",
        "kind": "Deployment",
        "metadata": {"name": app_name, "labels": {"app": app_name}},
        "spec": {
            "replicas": 3,
            "selector": {"matchLabels": {"app": app_name}},
            "template": {
                "metadata": {"labels": {"app": app_name}},
                "spec": {
                    "containers": [{
                        "name": app_name,
                        "image": image,
                        "ports": [{"containerPort": 8080}],
                        "resources": {
                            "requests": {"cpu": "100m", "memory": "128Mi"},
                            "limits": {"cpu": "500m", "memory": "512Mi"}
                        },
                        "livenessProbe": {
                            "httpGet": {"path": "/health", "port": 8080},
                            "initialDelaySeconds": 30,
                            "periodSeconds": 10
                        }
                    }]
                }
            }
        }
    }
    
    # Service manifest
    service = {
        "apiVersion": "v1",
        "kind": "Service",
        "metadata": {"name": app_name},
        "spec": {
            "selector": {"app": app_name},
            "ports": [{"port": 80, "targetPort": 8080}],
            "type": "ClusterIP"
        }
    }
    
    manifests["deployment.yaml"] = yaml.dump(deployment)
    manifests["service.yaml"] = yaml.dump(service)
    
    return manifests

if __name__ == "__main__":
    print("Kubernetes Advanced Operations - Interview Ready!")
    print("Key concepts: Production deployments, HPA, Network policies, RBAC, Ingress")