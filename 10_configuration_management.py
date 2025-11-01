#!/usr/bin/env python3
"""
Configuration Management for DevOps - Script 10
Why: Managing configurations across environments is essential for DevOps
"""

import os
import json
import yaml
from typing import Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path

@dataclass
class ConfigEnvironment:
    """
    Configuration environment definition
    Why: Structure configuration data for different environments
    """
    name: str
    database_url: str
    api_key: str
    debug: bool
    replicas: int

class ConfigManager:
    """
    Centralized configuration management
    Why: Single source of truth for application configuration
    """
    
    def __init__(self, config_dir: str):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)  # Create directory if it doesn't exist
        self._configs = {}  # Cache loaded configurations
    
    def load_environment_config(self, env_name: str) -> Dict[str, Any]:
        """
        Load configuration for specific environment
        Why: Different environments need different settings
        """
        config_file = self.config_dir / f"{env_name}.yaml"
        
        if not config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_file}")
        
        # Cache configuration to avoid repeated file reads
        if env_name not in self._configs:
            with open(config_file, 'r') as f:
                self._configs[env_name] = yaml.safe_load(f)
        
        return self._configs[env_name]
    
    def merge_configs(self, base_config: Dict, override_config: Dict) -> Dict:
        """
        Merge configuration dictionaries with override precedence
        Why: Combine base config with environment-specific overrides
        """
        merged = base_config.copy()  # Start with base configuration
        
        for key, value in override_config.items():
            if isinstance(value, dict) and key in merged and isinstance(merged[key], dict):
                # Recursively merge nested dictionaries
                merged[key] = self.merge_configs(merged[key], value)
            else:
                # Override value
                merged[key] = value
        
        return merged
    
    def substitute_environment_variables(self, config: Dict) -> Dict:
        """
        Replace placeholders with environment variables
        Why: Keep secrets out of config files using environment variables
        """
        import re
        
        def substitute_value(value):
            if isinstance(value, str):
                # Replace ${VAR_NAME} with environment variable value
                pattern = r'\$\{([^}]+)\}'
                
                def replace_var(match):
                    var_name = match.group(1)
                    default_value = None
                    
                    # Handle default values: ${VAR_NAME:default}
                    if ':' in var_name:
                        var_name, default_value = var_name.split(':', 1)
                    
                    return os.getenv(var_name, default_value or match.group(0))
                
                return re.sub(pattern, replace_var, value)
            elif isinstance(value, dict):
                return {k: substitute_value(v) for k, v in value.items()}
            elif isinstance(value, list):
                return [substitute_value(item) for item in value]
            else:
                return value
        
        return substitute_value(config)
    
    def validate_config(self, config: Dict, required_keys: list) -> bool:
        """
        Validate configuration has required keys
        Why: Catch configuration errors before deployment
        """
        missing_keys = []
        
        for key in required_keys:
            if '.' in key:  # Handle nested keys like 'database.host'
                keys = key.split('.')
                current = config
                
                for k in keys:
                    if not isinstance(current, dict) or k not in current:
                        missing_keys.append(key)
                        break
                    current = current[k]
            else:
                if key not in config:
                    missing_keys.append(key)
        
        if missing_keys:
            print(f"Missing required configuration keys: {missing_keys}")
            return False
        
        return True
    
    def generate_config_template(self, template_name: str) -> Dict:
        """
        Generate configuration template for new environments
        Why: Standardize configuration structure across environments
        """
        templates = {
            'web_app': {
                'app': {
                    'name': '${APP_NAME}',
                    'version': '${APP_VERSION:1.0.0}',
                    'debug': False
                },
                'database': {
                    'host': '${DB_HOST:localhost}',
                    'port': '${DB_PORT:5432}',
                    'name': '${DB_NAME}',
                    'user': '${DB_USER}',
                    'password': '${DB_PASSWORD}'
                },
                'redis': {
                    'host': '${REDIS_HOST:localhost}',
                    'port': '${REDIS_PORT:6379}'
                },
                'logging': {
                    'level': '${LOG_LEVEL:INFO}',
                    'format': 'json'
                }
            },
            'microservice': {
                'service': {
                    'name': '${SERVICE_NAME}',
                    'port': '${SERVICE_PORT:8080}',
                    'replicas': '${REPLICAS:3}'
                },
                'dependencies': {
                    'api_gateway': '${API_GATEWAY_URL}',
                    'message_queue': '${MQ_URL}'
                }
            }
        }
        
        return templates.get(template_name, {})

def create_environment_configs():
    """
    Create sample configuration files for different environments
    Why: Demonstrate configuration management across environments
    """
    config_manager = ConfigManager('/tmp/configs')
    
    # Development environment
    dev_config = {
        'app': {
            'name': 'myapp',
            'debug': True,
            'replicas': 1
        },
        'database': {
            'host': 'localhost',
            'port': 5432,
            'name': 'myapp_dev'
        },
        'features': {
            'new_ui': True,
            'analytics': False
        }
    }
    
    # Production environment
    prod_config = {
        'app': {
            'name': 'myapp',
            'debug': False,
            'replicas': 5
        },
        'database': {
            'host': 'prod-db.example.com',
            'port': 5432,
            'name': 'myapp_prod'
        },
        'features': {
            'new_ui': False,
            'analytics': True
        }
    }
    
    # Save configurations
    for env_name, config in [('development', dev_config), ('production', prod_config)]:
        config_file = config_manager.config_dir / f"{env_name}.yaml"
        with open(config_file, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
        print(f"Created {env_name} configuration")

def load_config_with_overrides(base_env: str, override_env: str = None) -> Dict:
    """
    Load configuration with optional overrides
    Why: Allow environment-specific customizations while maintaining base config
    """
    config_manager = ConfigManager('/tmp/configs')
    
    # Load base configuration
    config = config_manager.load_environment_config(base_env)
    
    # Apply overrides if specified
    if override_env:
        try:
            override_config = config_manager.load_environment_config(override_env)
            config = config_manager.merge_configs(config, override_config)
        except FileNotFoundError:
            print(f"Override configuration not found: {override_env}")
    
    # Substitute environment variables
    config = config_manager.substitute_environment_variables(config)
    
    return config

if __name__ == "__main__":
    # Create sample configurations
    create_environment_configs()
    
    # Load development configuration
    dev_config = load_config_with_overrides('development')
    print(f"Development config loaded: {dev_config['app']['name']}")
    
    # Validate configuration
    config_manager = ConfigManager('/tmp/configs')
    required_keys = ['app.name', 'database.host', 'app.replicas']
    is_valid = config_manager.validate_config(dev_config, required_keys)
    print(f"Configuration valid: {is_valid}")
    
    print("Configuration management script ready!")