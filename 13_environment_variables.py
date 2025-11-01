#!/usr/bin/env python3
"""
Environment Variables Management - Script 13
Why: Environment variables are the standard way to configure applications
"""

import os
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass

@dataclass
class EnvConfig:
    """
    Environment configuration with type validation
    Why: Structure environment variables with proper types
    """
    database_url: str
    debug: bool
    port: int
    timeout: float
    allowed_hosts: list

def get_env_var(key: str, default: Any = None, var_type: type = str) -> Any:
    """
    Get environment variable with type conversion
    Why: Environment variables are strings but we need typed values
    """
    value = os.getenv(key, default)
    
    if value is None:
        return None
    
    # Convert string to appropriate type
    try:
        if var_type == bool:
            # Handle boolean conversion properly
            return value.lower() in ('true', '1', 'yes', 'on')
        elif var_type == int:
            return int(value)
        elif var_type == float:
            return float(value)
        elif var_type == list:
            # Split comma-separated values
            return [item.strip() for item in value.split(',') if item.strip()]
        else:
            return var_type(value)
    except (ValueError, TypeError) as e:
        print(f"Error converting {key}={value} to {var_type.__name__}: {e}")
        return default

def load_env_from_file(env_file: str = '.env') -> Dict[str, str]:
    """
    Load environment variables from .env file
    Why: Manage environment variables in development without setting them globally
    """
    env_vars = {}
    
    try:
        with open(env_file, 'r') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                
                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue
                
                # Parse KEY=VALUE format
                if '=' in line:
                    key, value = line.split('=', 1)  # Split only on first =
                    key = key.strip()
                    value = value.strip()
                    
                    # Remove quotes if present
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]
                    
                    env_vars[key] = value
                    os.environ[key] = value  # Set in current environment
                else:
                    print(f"Warning: Invalid format in {env_file} line {line_num}: {line}")
    
    except FileNotFoundError:
        print(f"Environment file {env_file} not found")
    except Exception as e:
        print(f"Error loading environment file: {e}")
    
    return env_vars

def validate_required_env_vars(required_vars: Dict[str, type]) -> Dict[str, Any]:
    """
    Validate that required environment variables are set
    Why: Fail fast if critical configuration is missing
    """
    config = {}
    missing_vars = []
    invalid_vars = []
    
    for var_name, var_type in required_vars.items():
        value = get_env_var(var_name, var_type=var_type)
        
        if value is None:
            missing_vars.append(var_name)
        else:
            config[var_name] = value
    
    # Report validation results
    if missing_vars:
        raise EnvironmentError(f"Missing required environment variables: {missing_vars}")
    
    if invalid_vars:
        raise ValueError(f"Invalid environment variable values: {invalid_vars}")
    
    return config

def create_env_template(template_name: str) -> str:
    """
    Create .env template file with documentation
    Why: Provide developers with example environment configuration
    """
    templates = {
        'web_app': '''# Web Application Environment Configuration
# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/myapp
DB_POOL_SIZE=10

# Application Settings
DEBUG=false
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# Server Configuration
PORT=8000
WORKERS=4
TIMEOUT=30.0

# External Services
REDIS_URL=redis://localhost:6379/0
ELASTICSEARCH_URL=http://localhost:9200

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# Feature Flags
ENABLE_ANALYTICS=true
ENABLE_CACHING=true
''',
        'microservice': '''# Microservice Environment Configuration
# Service Identity
SERVICE_NAME=user-service
SERVICE_VERSION=1.0.0
SERVICE_PORT=8080

# Dependencies
API_GATEWAY_URL=http://api-gateway:8000
MESSAGE_QUEUE_URL=amqp://rabbitmq:5672
DATABASE_URL=postgresql://localhost:5432/userdb

# Monitoring
METRICS_PORT=9090
HEALTH_CHECK_PATH=/health

# Security
JWT_SECRET=your-jwt-secret
API_KEY=your-api-key
'''
    }
    
    template_content = templates.get(template_name, "# Environment template not found")
    
    with open(f'.env.{template_name}', 'w') as f:
        f.write(template_content)
    
    return f'.env.{template_name}'

def get_environment_info() -> Dict[str, Any]:
    """
    Get information about current environment
    Why: Debug environment issues and understand runtime context
    """
    return {
        'python_path': os.environ.get('PYTHONPATH', 'Not set'),
        'path': os.environ.get('PATH', '').split(os.pathsep)[:5],  # First 5 PATH entries
        'home': os.environ.get('HOME', 'Not set'),
        'user': os.environ.get('USER', 'Not set'),
        'shell': os.environ.get('SHELL', 'Not set'),
        'total_env_vars': len(os.environ),
        'custom_vars': {
            k: v for k, v in os.environ.items() 
            if k.startswith(('APP_', 'SERVICE_', 'DB_', 'REDIS_'))
        }
    }

def set_env_defaults(defaults: Dict[str, str]) -> Dict[str, str]:
    """
    Set default environment variables if not already set
    Why: Provide sensible defaults for development environment
    """
    set_vars = {}
    
    for key, default_value in defaults.items():
        if key not in os.environ:
            os.environ[key] = default_value
            set_vars[key] = default_value
    
    return set_vars

class EnvironmentManager:
    """
    Centralized environment variable management
    Why: Organize environment configuration in one place
    """
    
    def __init__(self, env_file: str = '.env'):
        self.env_file = env_file
        self.config = {}
        self.load_configuration()
    
    def load_configuration(self):
        """Load configuration from environment and file"""
        # Load from .env file first
        load_env_from_file(self.env_file)
        
        # Define configuration schema
        config_schema = {
            'DEBUG': bool,
            'PORT': int,
            'DATABASE_URL': str,
            'TIMEOUT': float,
            'ALLOWED_HOSTS': list
        }
        
        # Load and validate configuration
        for key, var_type in config_schema.items():
            self.config[key.lower()] = get_env_var(key, var_type=var_type)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self.config.get(key.lower(), default)
    
    def is_development(self) -> bool:
        """Check if running in development mode"""
        return self.get('debug', False)
    
    def is_production(self) -> bool:
        """Check if running in production mode"""
        env = get_env_var('ENVIRONMENT', 'development')
        return env.lower() == 'production'

if __name__ == "__main__":
    # Create sample .env file
    env_content = '''DEBUG=true
PORT=8000
DATABASE_URL=postgresql://localhost:5432/testdb
TIMEOUT=30.0
ALLOWED_HOSTS=localhost,127.0.0.1,testserver
'''
    
    with open('/tmp/.env', 'w') as f:
        f.write(env_content)
    
    # Load environment variables
    env_vars = load_env_from_file('/tmp/.env')
    print(f"Loaded {len(env_vars)} environment variables")
    
    # Validate required variables
    required_vars = {
        'DEBUG': bool,
        'PORT': int,
        'DATABASE_URL': str,
        'TIMEOUT': float
    }
    
    try:
        config = validate_required_env_vars(required_vars)
        print(f"Configuration validated: {config}")
    except EnvironmentError as e:
        print(f"Configuration error: {e}")
    
    # Create environment template
    template_file = create_env_template('web_app')
    print(f"Created environment template: {template_file}")
    
    # Get environment info
    env_info = get_environment_info()
    print(f"Environment info: {env_info['total_env_vars']} total variables")
    
    print("Environment variables script ready!")