#!/usr/bin/env python3
"""
CI/CD Pipeline Automation Scripts
Topics: Jenkins, GitLab CI, GitHub Actions, Pipeline as Code
"""

import requests
import json
import subprocess
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

class PipelineStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"

@dataclass
class BuildJob:
    job_id: str
    status: PipelineStatus
    branch: str
    commit_sha: str
    duration: Optional[int] = None

class JenkinsAPI:
    def __init__(self, base_url: str, username: str, token: str):
        self.base_url = base_url.rstrip('/')
        self.auth = (username, token)
    
    def trigger_build(self, job_name: str, parameters: Dict = None) -> str:
        """Trigger Jenkins build with parameters"""
        url = f"{self.base_url}/job/{job_name}/buildWithParameters"
        response = requests.post(url, auth=self.auth, data=parameters or {})
        
        if response.status_code == 201:
            # Extract build number from Location header
            location = response.headers.get('Location', '')
            return location.split('/')[-2] if location else None
        return None
    
    def get_build_status(self, job_name: str, build_number: str) -> BuildJob:
        """Get build status and details"""
        url = f"{self.base_url}/job/{job_name}/{build_number}/api/json"
        response = requests.get(url, auth=self.auth)
        
        if response.status_code == 200:
            data = response.json()
            return BuildJob(
                job_id=f"{job_name}-{build_number}",
                status=PipelineStatus(data['result'].lower() if data['result'] else 'running'),
                branch=data.get('actions', [{}])[0].get('parameters', [{}])[0].get('value', 'main'),
                commit_sha=data.get('changeSet', {}).get('items', [{}])[0].get('commitId', ''),
                duration=data.get('duration')
            )

class GitLabCI:
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url.rstrip('/')
        self.headers = {'PRIVATE-TOKEN': token}
    
    def create_pipeline(self, project_id: str, ref: str, variables: Dict = None) -> Dict:
        """Create GitLab CI pipeline"""
        url = f"{self.base_url}/api/v4/projects/{project_id}/pipeline"
        data = {'ref': ref}
        if variables:
            data['variables'] = [{'key': k, 'value': v} for k, v in variables.items()]
        
        response = requests.post(url, headers=self.headers, json=data)
        return response.json() if response.status_code == 201 else {}
    
    def get_pipeline_jobs(self, project_id: str, pipeline_id: str) -> List[Dict]:
        """Get jobs for a pipeline"""
        url = f"{self.base_url}/api/v4/projects/{project_id}/pipelines/{pipeline_id}/jobs"
        response = requests.get(url, headers=self.headers)
        return response.json() if response.status_code == 200 else []

class PipelineOrchestrator:
    """Orchestrate multi-stage deployments"""
    
    def __init__(self):
        self.stages = ['build', 'test', 'security-scan', 'deploy-staging', 'deploy-prod']
        self.current_stage = 0
    
    def execute_stage(self, stage: str, context: Dict) -> bool:
        """Execute pipeline stage with context"""
        stage_methods = {
            'build': self._build_application,
            'test': self._run_tests,
            'security-scan': self._security_scan,
            'deploy-staging': self._deploy_to_staging,
            'deploy-prod': self._deploy_to_production
        }
        
        method = stage_methods.get(stage)
        if method:
            return method(context)
        return False
    
    def _build_application(self, context: Dict) -> bool:
        """Build application artifacts"""
        try:
            subprocess.run(['docker', 'build', '-t', context['image_name'], '.'], check=True)
            return True
        except subprocess.CalledProcessError:
            return False
    
    def _run_tests(self, context: Dict) -> bool:
        """Run test suite"""
        try:
            subprocess.run(['pytest', '--cov=src', '--cov-report=xml'], check=True)
            return True
        except subprocess.CalledProcessError:
            return False
    
    def _security_scan(self, context: Dict) -> bool:
        """Run security scans"""
        try:
            # Example: Trivy container scan
            subprocess.run(['trivy', 'image', context['image_name']], check=True)
            return True
        except subprocess.CalledProcessError:
            return False
    
    def _deploy_to_staging(self, context: Dict) -> bool:
        """Deploy to staging environment"""
        return self._deploy_to_environment('staging', context)
    
    def _deploy_to_production(self, context: Dict) -> bool:
        """Deploy to production environment"""
        return self._deploy_to_environment('production', context)
    
    def _deploy_to_environment(self, env: str, context: Dict) -> bool:
        """Generic deployment method"""
        try:
            subprocess.run([
                'kubectl', 'set', 'image', 
                f"deployment/{context['app_name']}", 
                f"{context['app_name']}={context['image_name']}",
                f"--namespace={env}"
            ], check=True)
            return True
        except subprocess.CalledProcessError:
            return False

def generate_github_actions_workflow() -> str:
    """Generate GitHub Actions workflow YAML"""
    workflow = """
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  build-and-test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    - name: Run tests
      run: pytest --cov=src
    - name: Build Docker image
      run: docker build -t ${{ github.repository }}:${{ github.sha }} .
    
  deploy:
    needs: build-and-test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
    - name: Deploy to staging
      run: echo "Deploying to staging"
"""
    return workflow

# Interview scenarios
if __name__ == "__main__":
    # Interview Question: How do you implement blue-green deployments?
    orchestrator = PipelineOrchestrator()
    
    # Interview Question: How do you handle pipeline failures and rollbacks?
    context = {
        'image_name': 'myapp:latest',
        'app_name': 'myapp',
        'environment': 'staging'
    }
    
    print("CI/CD pipeline scripts ready for interview prep!")