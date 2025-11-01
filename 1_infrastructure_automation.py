#!/usr/bin/env python3
"""
Infrastructure Automation Scripts for DevOps Interview Prep
Topics: AWS SDK, Infrastructure as Code, Resource Management
"""

import boto3
import json
from typing import Dict, List, Optional

class AWSResourceManager:
    def __init__(self, region='us-east-1'):
        self.ec2 = boto3.client('ec2', region_name=region)
        self.s3 = boto3.client('s3')
        self.cloudformation = boto3.client('cloudformation', region_name=region)
    
    def create_vpc_with_subnets(self, vpc_cidr: str, subnet_cidrs: List[str]) -> Dict:
        """Create VPC with multiple subnets"""
        vpc = self.ec2.create_vpc(CidrBlock=vpc_cidr)
        vpc_id = vpc['Vpc']['VpcId']
        
        subnets = []
        for i, cidr in enumerate(subnet_cidrs):
            subnet = self.ec2.create_subnet(
                VpcId=vpc_id,
                CidrBlock=cidr,
                AvailabilityZone=f"{self.ec2.meta.region_name}{'a' if i % 2 == 0 else 'b'}"
            )
            subnets.append(subnet['Subnet']['SubnetId'])
        
        return {'vpc_id': vpc_id, 'subnet_ids': subnets}
    
    def deploy_stack(self, stack_name: str, template_body: str, parameters: Dict) -> str:
        """Deploy CloudFormation stack"""
        params = [{'ParameterKey': k, 'ParameterValue': v} for k, v in parameters.items()]
        
        response = self.cloudformation.create_stack(
            StackName=stack_name,
            TemplateBody=template_body,
            Parameters=params,
            Capabilities=['CAPABILITY_IAM']
        )
        return response['StackId']
    
    def get_resource_costs(self, resource_type: str) -> List[Dict]:
        """Get resource utilization for cost optimization"""
        if resource_type == 'ec2':
            instances = self.ec2.describe_instances()
            return [
                {
                    'instance_id': inst['InstanceId'],
                    'type': inst['InstanceType'],
                    'state': inst['State']['Name'],
                    'launch_time': inst['LaunchTime'].isoformat()
                }
                for reservation in instances['Reservations']
                for inst in reservation['Instances']
            ]

class TerraformWrapper:
    """Python wrapper for Terraform operations"""
    
    def __init__(self, working_dir: str):
        self.working_dir = working_dir
    
    def plan(self) -> str:
        """Execute terraform plan"""
        import subprocess
        result = subprocess.run(
            ['terraform', 'plan', '-out=tfplan'],
            cwd=self.working_dir,
            capture_output=True,
            text=True
        )
        return result.stdout
    
    def apply(self) -> bool:
        """Execute terraform apply"""
        import subprocess
        result = subprocess.run(
            ['terraform', 'apply', 'tfplan'],
            cwd=self.working_dir,
            capture_output=True
        )
        return result.returncode == 0

# Example usage and interview questions
if __name__ == "__main__":
    # Interview Question: How would you automate infrastructure provisioning?
    aws_mgr = AWSResourceManager()
    
    # Interview Question: How do you handle infrastructure state management?
    terraform = TerraformWrapper('/path/to/terraform')
    
    print("Infrastructure automation scripts ready for interview prep!")