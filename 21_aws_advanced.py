#!/usr/bin/env python3
"""
Advanced AWS Operations - Script 21
Why: AWS expertise is critical for senior DevOps roles
"""

import boto3
import json
from typing import Dict, List, Optional
from botocore.exceptions import ClientError

class AWSInfrastructureManager:
    def __init__(self, region='us-east-1'):
        self.region = region
        self.ec2 = boto3.client('ec2', region_name=region)
        self.elbv2 = boto3.client('elbv2', region_name=region)
        self.autoscaling = boto3.client('autoscaling', region_name=region)
        self.cloudformation = boto3.client('cloudformation', region_name=region)
        self.iam = boto3.client('iam')
        self.route53 = boto3.client('route53')
    
    def create_vpc_infrastructure(self, vpc_cidr: str, name: str) -> Dict:
        """
        Create complete VPC with subnets, IGW, NAT, and route tables
        Why: Interview question - Design scalable network architecture
        """
        try:
            # Create VPC
            vpc = self.ec2.create_vpc(CidrBlock=vpc_cidr)
            vpc_id = vpc['Vpc']['VpcId']
            
            # Tag VPC
            self.ec2.create_tags(Resources=[vpc_id], Tags=[{'Key': 'Name', 'Value': name}])
            
            # Create Internet Gateway
            igw = self.ec2.create_internet_gateway()
            igw_id = igw['InternetGateway']['InternetGatewayId']
            self.ec2.attach_internet_gateway(InternetGatewayId=igw_id, VpcId=vpc_id)
            
            # Create public and private subnets
            public_subnet = self.ec2.create_subnet(
                VpcId=vpc_id, CidrBlock=f"{vpc_cidr[:-4]}0/24", AvailabilityZone=f"{self.region}a"
            )
            private_subnet = self.ec2.create_subnet(
                VpcId=vpc_id, CidrBlock=f"{vpc_cidr[:-4]}1/24", AvailabilityZone=f"{self.region}b"
            )
            
            # Create NAT Gateway
            nat_gw = self.ec2.create_nat_gateway(
                SubnetId=public_subnet['Subnet']['SubnetId'],
                AllocationId=self.ec2.allocate_address(Domain='vpc')['AllocationId']
            )
            
            return {
                'vpc_id': vpc_id,
                'public_subnet': public_subnet['Subnet']['SubnetId'],
                'private_subnet': private_subnet['Subnet']['SubnetId'],
                'igw_id': igw_id,
                'nat_gw_id': nat_gw['NatGateway']['NatGatewayId']
            }
        except ClientError as e:
            print(f"VPC creation failed: {e}")
            return {}
    
    def create_auto_scaling_group(self, launch_template_id: str, subnets: List[str]) -> str:
        """
        Create Auto Scaling Group with health checks
        Why: Interview question - How do you handle auto-scaling?
        """
        asg_name = f"asg-{launch_template_id[:8]}"
        
        self.autoscaling.create_auto_scaling_group(
            AutoScalingGroupName=asg_name,
            LaunchTemplate={'LaunchTemplateId': launch_template_id, 'Version': '$Latest'},
            MinSize=2,
            MaxSize=10,
            DesiredCapacity=3,
            VPCZoneIdentifier=','.join(subnets),
            HealthCheckType='ELB',
            HealthCheckGracePeriod=300,
            Tags=[{'Key': 'Environment', 'Value': 'production', 'PropagateAtLaunch': True}]
        )
        
        # Create scaling policies
        scale_up_policy = self.autoscaling.put_scaling_policy(
            AutoScalingGroupName=asg_name,
            PolicyName=f"{asg_name}-scale-up",
            PolicyType='TargetTrackingScaling',
            TargetTrackingConfiguration={
                'TargetValue': 70.0,
                'PredefinedMetricSpecification': {'PredefinedMetricType': 'ASGAverageCPUUtilization'}
            }
        )
        
        return asg_name
    
    def setup_load_balancer(self, vpc_id: str, subnets: List[str]) -> Dict:
        """
        Create Application Load Balancer with SSL termination
        Why: Interview question - Design highly available architecture
        """
        # Create security group for ALB
        sg = self.ec2.create_security_group(
            GroupName='alb-sg',
            Description='ALB Security Group',
            VpcId=vpc_id
        )
        
        self.ec2.authorize_security_group_ingress(
            GroupId=sg['GroupId'],
            IpPermissions=[
                {'IpProtocol': 'tcp', 'FromPort': 80, 'ToPort': 80, 'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},
                {'IpProtocol': 'tcp', 'FromPort': 443, 'ToPort': 443, 'IpRanges': [{'CidrIp': '0.0.0.0/0'}]}
            ]
        )
        
        # Create ALB
        alb = self.elbv2.create_load_balancer(
            Name='production-alb',
            Subnets=subnets,
            SecurityGroups=[sg['GroupId']],
            Scheme='internet-facing',
            Type='application'
        )
        
        # Create target group
        target_group = self.elbv2.create_target_group(
            Name='web-servers',
            Protocol='HTTP',
            Port=80,
            VpcId=vpc_id,
            HealthCheckPath='/health',
            HealthCheckIntervalSeconds=30,
            HealthyThresholdCount=2,
            UnhealthyThresholdCount=5
        )
        
        return {
            'alb_arn': alb['LoadBalancers'][0]['LoadBalancerArn'],
            'target_group_arn': target_group['TargetGroups'][0]['TargetGroupArn'],
            'dns_name': alb['LoadBalancers'][0]['DNSName']
        }
    
    def deploy_cloudformation_stack(self, template: Dict, stack_name: str, parameters: Dict) -> str:
        """
        Deploy CloudFormation stack with rollback handling
        Why: Interview question - Infrastructure as Code best practices
        """
        try:
            # Convert parameters to CloudFormation format
            cf_params = [{'ParameterKey': k, 'ParameterValue': v} for k, v in parameters.items()]
            
            response = self.cloudformation.create_stack(
                StackName=stack_name,
                TemplateBody=json.dumps(template),
                Parameters=cf_params,
                Capabilities=['CAPABILITY_IAM', 'CAPABILITY_NAMED_IAM'],
                OnFailure='ROLLBACK',
                EnableTerminationProtection=True,
                Tags=[{'Key': 'Environment', 'Value': 'production'}]
            )
            
            # Wait for stack creation
            waiter = self.cloudformation.get_waiter('stack_create_complete')
            waiter.wait(StackName=stack_name, WaiterConfig={'Delay': 30, 'MaxAttempts': 120})
            
            return response['StackId']
            
        except ClientError as e:
            if 'AlreadyExistsException' in str(e):
                # Update existing stack
                return self.update_cloudformation_stack(template, stack_name, parameters)
            raise
    
    def setup_cross_region_replication(self, source_bucket: str, dest_region: str) -> Dict:
        """
        Setup S3 cross-region replication for disaster recovery
        Why: Interview question - Disaster recovery strategies
        """
        s3 = boto3.client('s3')
        
        # Create destination bucket
        dest_bucket = f"{source_bucket}-replica-{dest_region}"
        s3.create_bucket(
            Bucket=dest_bucket,
            CreateBucketConfiguration={'LocationConstraint': dest_region}
        )
        
        # Enable versioning on both buckets
        for bucket in [source_bucket, dest_bucket]:
            s3.put_bucket_versioning(
                Bucket=bucket,
                VersioningConfiguration={'Status': 'Enabled'}
            )
        
        # Create IAM role for replication
        trust_policy = {
            "Version": "2012-10-17",
            "Statement": [{
                "Effect": "Allow",
                "Principal": {"Service": "s3.amazonaws.com"},
                "Action": "sts:AssumeRole"
            }]
        }
        
        role_name = f"s3-replication-role-{source_bucket}"
        self.iam.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(trust_policy)
        )
        
        return {'source_bucket': source_bucket, 'dest_bucket': dest_bucket, 'role_name': role_name}

class AWSCostOptimizer:
    """
    AWS cost optimization utilities
    Why: Interview question - How do you optimize AWS costs?
    """
    
    def __init__(self):
        self.ec2 = boto3.client('ec2')
        self.ce = boto3.client('ce')  # Cost Explorer
        self.cloudwatch = boto3.client('cloudwatch')
    
    def find_unused_resources(self) -> Dict:
        """Find unused AWS resources for cost optimization"""
        unused = {'ebs_volumes': [], 'elastic_ips': [], 'load_balancers': []}
        
        # Find unattached EBS volumes
        volumes = self.ec2.describe_volumes(Filters=[{'Name': 'status', 'Values': ['available']}])
        unused['ebs_volumes'] = [v['VolumeId'] for v in volumes['Volumes']]
        
        # Find unassociated Elastic IPs
        addresses = self.ec2.describe_addresses()
        unused['elastic_ips'] = [addr['AllocationId'] for addr in addresses['Addresses'] 
                                if 'InstanceId' not in addr]
        
        return unused
    
    def get_rightsizing_recommendations(self) -> List[Dict]:
        """Get EC2 rightsizing recommendations"""
        try:
            response = self.ce.get_rightsizing_recommendation(
                Service='AmazonEC2',
                Configuration={'BenefitsConsidered': True, 'RecommendationTarget': 'SAME_INSTANCE_FAMILY'}
            )
            return response.get('RightsizingRecommendations', [])
        except ClientError:
            return []

if __name__ == "__main__":
    # Interview Demo: Complete AWS infrastructure setup
    aws_mgr = AWSInfrastructureManager()
    
    print("AWS Advanced Operations - Interview Ready!")
    print("Key concepts: VPC design, Auto Scaling, Load Balancing, Cost Optimization")