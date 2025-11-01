#!/usr/bin/env python3
"""
Security and Compliance Scripts for DevOps
Topics: Security Scanning, Compliance Checks, Secret Management, RBAC
"""

import hashlib
import secrets
import subprocess
import json
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import boto3
from cryptography.fernet import Fernet
import hvac  # HashiCorp Vault client

@dataclass
class SecurityFinding:
    severity: str
    title: str
    description: str
    file_path: str
    line_number: int
    cve_id: Optional[str] = None

@dataclass
class ComplianceCheck:
    control_id: str
    description: str
    status: str  # PASS, FAIL, MANUAL
    evidence: str

class SecretManager:
    """Secure secret management"""
    
    def __init__(self, vault_url: str = None, vault_token: str = None):
        self.vault_client = None
        if vault_url and vault_token:
            self.vault_client = hvac.Client(url=vault_url, token=vault_token)
        
        # Fallback to local encryption
        self.cipher_key = Fernet.generate_key()
        self.cipher = Fernet(self.cipher_key)
    
    def store_secret(self, path: str, secret_data: Dict) -> bool:
        """Store secret in Vault or encrypted locally"""
        if self.vault_client and self.vault_client.is_authenticated():
            try:
                self.vault_client.secrets.kv.v2.create_or_update_secret(
                    path=path,
                    secret=secret_data
                )
                return True
            except Exception as e:
                print(f"Vault storage failed: {e}")
        
        # Fallback to local encrypted storage
        encrypted_data = self.cipher.encrypt(json.dumps(secret_data).encode())
        with open(f"/tmp/{path.replace('/', '_')}.enc", 'wb') as f:
            f.write(encrypted_data)
        return True
    
    def retrieve_secret(self, path: str) -> Optional[Dict]:
        """Retrieve secret from Vault or local storage"""
        if self.vault_client and self.vault_client.is_authenticated():
            try:
                response = self.vault_client.secrets.kv.v2.read_secret_version(path=path)
                return response['data']['data']
            except Exception as e:
                print(f"Vault retrieval failed: {e}")
        
        # Fallback to local encrypted storage
        try:
            with open(f"/tmp/{path.replace('/', '_')}.enc", 'rb') as f:
                encrypted_data = f.read()
            decrypted_data = self.cipher.decrypt(encrypted_data)
            return json.loads(decrypted_data.decode())
        except Exception:
            return None
    
    def rotate_secret(self, path: str, new_secret_data: Dict) -> bool:
        """Rotate secret with versioning"""
        # Store old version with timestamp
        old_secret = self.retrieve_secret(path)
        if old_secret:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            self.store_secret(f"{path}_backup_{timestamp}", old_secret)
        
        return self.store_secret(path, new_secret_data)

class SecurityScanner:
    """Security vulnerability scanner"""
    
    def __init__(self):
        self.secret_patterns = [
            (r'aws_access_key_id\s*=\s*["\']?([A-Z0-9]{20})["\']?', 'AWS Access Key'),
            (r'aws_secret_access_key\s*=\s*["\']?([A-Za-z0-9/+=]{40})["\']?', 'AWS Secret Key'),
            (r'password\s*=\s*["\']([^"\']+)["\']', 'Hardcoded Password'),
            (r'api_key\s*=\s*["\']([^"\']+)["\']', 'API Key'),
            (r'token\s*=\s*["\']([^"\']+)["\']', 'Token'),
            (r'-----BEGIN PRIVATE KEY-----', 'Private Key'),
            (r'-----BEGIN RSA PRIVATE KEY-----', 'RSA Private Key')
        ]
    
    def scan_secrets_in_code(self, directory: str) -> List[SecurityFinding]:
        """Scan for hardcoded secrets in code"""
        findings = []
        
        for root, dirs, files in os.walk(directory):
            # Skip common directories
            dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules', '__pycache__']]
            
            for file in files:
                if file.endswith(('.py', '.js', '.yaml', '.yml', '.json', '.env')):
                    file_path = os.path.join(root, file)
                    findings.extend(self._scan_file_for_secrets(file_path))
        
        return findings
    
    def _scan_file_for_secrets(self, file_path: str) -> List[SecurityFinding]:
        """Scan individual file for secrets"""
        findings = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line_num, line in enumerate(f, 1):
                    for pattern, secret_type in self.secret_patterns:
                        if re.search(pattern, line, re.IGNORECASE):
                            findings.append(SecurityFinding(
                                severity='HIGH',
                                title=f'Hardcoded {secret_type} Found',
                                description=f'Potential {secret_type} found in source code',
                                file_path=file_path,
                                line_number=line_num
                            ))
        except Exception as e:
            print(f"Error scanning {file_path}: {e}")
        
        return findings
    
    def scan_dependencies(self, requirements_file: str) -> List[SecurityFinding]:
        """Scan dependencies for known vulnerabilities"""
        findings = []
        
        try:
            # Use safety to check for known vulnerabilities
            result = subprocess.run([
                'safety', 'check', '--json', '--file', requirements_file
            ], capture_output=True, text=True)
            
            if result.returncode != 0 and result.stdout:
                vulnerabilities = json.loads(result.stdout)
                
                for vuln in vulnerabilities:
                    findings.append(SecurityFinding(
                        severity='HIGH' if vuln.get('severity') == 'high' else 'MEDIUM',
                        title=f"Vulnerable dependency: {vuln['package']}",
                        description=vuln['advisory'],
                        file_path=requirements_file,
                        line_number=1,
                        cve_id=vuln.get('cve')
                    ))
        
        except Exception as e:
            print(f"Dependency scan failed: {e}")
        
        return findings
    
    def scan_docker_image(self, image_name: str) -> List[SecurityFinding]:
        """Scan Docker image for vulnerabilities"""
        findings = []
        
        try:
            result = subprocess.run([
                'trivy', 'image', '--format', 'json', image_name
            ], capture_output=True, text=True, check=True)
            
            scan_results = json.loads(result.stdout)
            
            for result in scan_results.get('Results', []):
                for vuln in result.get('Vulnerabilities', []):
                    findings.append(SecurityFinding(
                        severity=vuln.get('Severity', 'UNKNOWN'),
                        title=f"Container vulnerability: {vuln.get('VulnerabilityID')}",
                        description=vuln.get('Description', ''),
                        file_path=f"docker://{image_name}",
                        line_number=0,
                        cve_id=vuln.get('VulnerabilityID')
                    ))
        
        except Exception as e:
            print(f"Docker image scan failed: {e}")
        
        return findings

class ComplianceChecker:
    """Compliance framework checker (SOC2, PCI-DSS, etc.)"""
    
    def __init__(self):
        self.soc2_controls = [
            'CC6.1 - Logical and Physical Access Controls',
            'CC6.2 - System Access Monitoring',
            'CC6.3 - Access Revocation',
            'CC7.1 - System Boundaries and Data Classification',
            'CC8.1 - Change Management'
        ]
    
    def check_soc2_compliance(self, infrastructure_config: Dict) -> List[ComplianceCheck]:
        """Check SOC2 compliance controls"""
        checks = []
        
        # CC6.1 - Access Controls
        checks.append(self._check_access_controls(infrastructure_config))
        
        # CC6.2 - Monitoring
        checks.append(self._check_monitoring_controls(infrastructure_config))
        
        # CC7.1 - Data Classification
        checks.append(self._check_data_classification(infrastructure_config))
        
        return checks
    
    def _check_access_controls(self, config: Dict) -> ComplianceCheck:
        """Check access control implementation"""
        has_mfa = config.get('mfa_enabled', False)
        has_rbac = config.get('rbac_enabled', False)
        
        if has_mfa and has_rbac:
            return ComplianceCheck(
                control_id='CC6.1',
                description='Logical and Physical Access Controls',
                status='PASS',
                evidence='MFA and RBAC are properly configured'
            )
        else:
            return ComplianceCheck(
                control_id='CC6.1',
                description='Logical and Physical Access Controls',
                status='FAIL',
                evidence=f'MFA: {has_mfa}, RBAC: {has_rbac}'
            )
    
    def _check_monitoring_controls(self, config: Dict) -> ComplianceCheck:
        """Check monitoring and logging controls"""
        has_logging = config.get('centralized_logging', False)
        has_alerting = config.get('security_alerting', False)
        
        if has_logging and has_alerting:
            return ComplianceCheck(
                control_id='CC6.2',
                description='System Access Monitoring',
                status='PASS',
                evidence='Centralized logging and security alerting enabled'
            )
        else:
            return ComplianceCheck(
                control_id='CC6.2',
                description='System Access Monitoring',
                status='FAIL',
                evidence=f'Logging: {has_logging}, Alerting: {has_alerting}'
            )
    
    def _check_data_classification(self, config: Dict) -> ComplianceCheck:
        """Check data classification controls"""
        has_encryption = config.get('data_encryption', False)
        has_classification = config.get('data_classification_policy', False)
        
        if has_encryption and has_classification:
            return ComplianceCheck(
                control_id='CC7.1',
                description='System Boundaries and Data Classification',
                status='PASS',
                evidence='Data encryption and classification policies in place'
            )
        else:
            return ComplianceCheck(
                control_id='CC7.1',
                description='System Boundaries and Data Classification',
                status='FAIL',
                evidence=f'Encryption: {has_encryption}, Classification: {has_classification}'
            )

class RBACManager:
    """Role-Based Access Control management"""
    
    def __init__(self):
        self.roles = {}
        self.users = {}
        self.permissions = {}
    
    def create_role(self, role_name: str, permissions: List[str]) -> bool:
        """Create role with specific permissions"""
        self.roles[role_name] = {
            'permissions': permissions,
            'created_at': datetime.now(),
            'users': []
        }
        return True
    
    def assign_role_to_user(self, user_id: str, role_name: str) -> bool:
        """Assign role to user"""
        if role_name not in self.roles:
            return False
        
        if user_id not in self.users:
            self.users[user_id] = {'roles': []}
        
        if role_name not in self.users[user_id]['roles']:
            self.users[user_id]['roles'].append(role_name)
            self.roles[role_name]['users'].append(user_id)
        
        return True
    
    def check_permission(self, user_id: str, permission: str) -> bool:
        """Check if user has specific permission"""
        if user_id not in self.users:
            return False
        
        user_roles = self.users[user_id]['roles']
        
        for role in user_roles:
            if role in self.roles and permission in self.roles[role]['permissions']:
                return True
        
        return False
    
    def audit_permissions(self) -> Dict:
        """Generate permission audit report"""
        audit_report = {
            'total_users': len(self.users),
            'total_roles': len(self.roles),
            'users_without_roles': [],
            'roles_without_users': [],
            'permission_matrix': {}
        }
        
        # Find users without roles
        for user_id, user_data in self.users.items():
            if not user_data['roles']:
                audit_report['users_without_roles'].append(user_id)
        
        # Find roles without users
        for role_name, role_data in self.roles.items():
            if not role_data['users']:
                audit_report['roles_without_users'].append(role_name)
        
        # Create permission matrix
        for role_name, role_data in self.roles.items():
            audit_report['permission_matrix'][role_name] = role_data['permissions']
        
        return audit_report

class EncryptionManager:
    """Data encryption and key management"""
    
    def __init__(self):
        self.master_key = Fernet.generate_key()
        self.cipher = Fernet(self.master_key)
    
    def encrypt_data(self, data: str) -> Tuple[bytes, str]:
        """Encrypt data and return encrypted data with key ID"""
        encrypted_data = self.cipher.encrypt(data.encode())
        key_id = hashlib.sha256(self.master_key).hexdigest()[:16]
        return encrypted_data, key_id
    
    def decrypt_data(self, encrypted_data: bytes, key_id: str) -> str:
        """Decrypt data using key ID"""
        # In production, retrieve key using key_id from secure key store
        decrypted_data = self.cipher.decrypt(encrypted_data)
        return decrypted_data.decode()
    
    def rotate_encryption_key(self) -> str:
        """Rotate encryption key"""
        old_key_id = hashlib.sha256(self.master_key).hexdigest()[:16]
        self.master_key = Fernet.generate_key()
        self.cipher = Fernet(self.master_key)
        new_key_id = hashlib.sha256(self.master_key).hexdigest()[:16]
        
        return f"Key rotated from {old_key_id} to {new_key_id}"

# Interview scenarios
if __name__ == "__main__":
    # Interview Question: How do you implement zero-trust security?
    secret_mgr = SecretManager()
    
    # Interview Question: How do you ensure compliance in CI/CD?
    scanner = SecurityScanner()
    compliance = ComplianceChecker()
    
    # Interview Question: How do you implement proper access controls?
    rbac = RBACManager()
    rbac.create_role('developer', ['read:code', 'write:code'])
    rbac.create_role('admin', ['read:*', 'write:*', 'delete:*'])
    
    print("Security and compliance scripts ready for interview prep!")