#!/usr/bin/env python3
"""
JSON and YAML Processing - Script 12
Why: Configuration files and API responses are commonly in JSON/YAML format
"""

import json
import yaml
from typing import Dict, List, Any, Union
from pathlib import Path
import re

def parse_json_safely(json_string: str) -> Union[Dict, List, None]:
    """
    Parse JSON string with error handling
    Why: Prevent crashes from malformed JSON in API responses
    """
    try:
        return json.loads(json_string)
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
        return None

def merge_json_objects(obj1: Dict, obj2: Dict) -> Dict:
    """
    Deep merge two JSON objects
    Why: Combine configuration objects from multiple sources
    """
    result = obj1.copy()  # Start with first object
    
    for key, value in obj2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            # Recursively merge nested dictionaries
            result[key] = merge_json_objects(result[key], value)
        else:
            # Override or add new key
            result[key] = value
    
    return result

def extract_json_paths(data: Dict, path_prefix: str = "") -> Dict[str, Any]:
    """
    Extract all JSON paths and their values
    Why: Analyze complex JSON structures or create path-based queries
    """
    paths = {}
    
    for key, value in data.items():
        current_path = f"{path_prefix}.{key}" if path_prefix else key
        
        if isinstance(value, dict):
            # Recursively process nested objects
            paths.update(extract_json_paths(value, current_path))
        elif isinstance(value, list):
            # Handle arrays
            paths[current_path] = f"Array[{len(value)}]"
            for i, item in enumerate(value):
                if isinstance(item, dict):
                    paths.update(extract_json_paths(item, f"{current_path}[{i}]"))
        else:
            # Store primitive values
            paths[current_path] = value
    
    return paths

def validate_json_schema(data: Dict, required_fields: List[str]) -> Dict:
    """
    Validate JSON against required schema
    Why: Ensure API responses or configs have expected structure
    """
    validation_result = {
        'valid': True,
        'missing_fields': [],
        'type_errors': []
    }
    
    def check_nested_field(obj: Dict, field_path: str) -> bool:
        """Check if nested field exists (e.g., 'user.profile.name')"""
        keys = field_path.split('.')
        current = obj
        
        for key in keys:
            if not isinstance(current, dict) or key not in current:
                return False
            current = current[key]
        
        return True
    
    # Check required fields
    for field in required_fields:
        if not check_nested_field(data, field):
            validation_result['missing_fields'].append(field)
            validation_result['valid'] = False
    
    return validation_result

def convert_yaml_to_json(yaml_file: str, json_file: str) -> bool:
    """
    Convert YAML file to JSON format
    Why: Some tools require JSON format instead of YAML
    """
    try:
        with open(yaml_file, 'r') as f:
            yaml_data = yaml.safe_load(f)
        
        with open(json_file, 'w') as f:
            json.dump(yaml_data, f, indent=2, default=str)  # default=str handles datetime objects
        
        return True
    except Exception as e:
        print(f"Conversion failed: {e}")
        return False

def filter_json_by_criteria(data: List[Dict], criteria: Dict) -> List[Dict]:
    """
    Filter JSON array by specified criteria
    Why: Query configuration data or filter API responses
    """
    filtered_results = []
    
    for item in data:
        matches = True
        
        for key, expected_value in criteria.items():
            # Support nested key access (e.g., 'metadata.name')
            keys = key.split('.')
            current_value = item
            
            try:
                for k in keys:
                    current_value = current_value[k]
                
                # Check if value matches criteria
                if isinstance(expected_value, str) and expected_value.startswith('regex:'):
                    # Regular expression matching
                    pattern = expected_value[6:]  # Remove 'regex:' prefix
                    if not re.search(pattern, str(current_value)):
                        matches = False
                        break
                elif current_value != expected_value:
                    matches = False
                    break
                    
            except (KeyError, TypeError):
                matches = False
                break
        
        if matches:
            filtered_results.append(item)
    
    return filtered_results

def transform_json_structure(data: Dict, mapping: Dict[str, str]) -> Dict:
    """
    Transform JSON structure using field mapping
    Why: Adapt data structure between different APIs or systems
    """
    transformed = {}
    
    for new_key, old_path in mapping.items():
        # Extract value from old path
        keys = old_path.split('.')
        current_value = data
        
        try:
            for key in keys:
                current_value = current_value[key]
            
            # Set value in new structure
            if '.' in new_key:
                # Handle nested new keys
                new_keys = new_key.split('.')
                current_dict = transformed
                
                for k in new_keys[:-1]:
                    if k not in current_dict:
                        current_dict[k] = {}
                    current_dict = current_dict[k]
                
                current_dict[new_keys[-1]] = current_value
            else:
                transformed[new_key] = current_value
                
        except (KeyError, TypeError):
            print(f"Warning: Could not extract value for path '{old_path}'")
    
    return transformed

def create_sample_configs():
    """
    Create sample configuration files for testing
    Why: Demonstrate JSON/YAML processing with realistic data
    """
    # Sample application configuration
    app_config = {
        'application': {
            'name': 'web-service',
            'version': '1.2.3',
            'environment': 'production'
        },
        'database': {
            'host': 'db.example.com',
            'port': 5432,
            'credentials': {
                'username': 'app_user',
                'password_env': 'DB_PASSWORD'
            }
        },
        'features': {
            'authentication': True,
            'rate_limiting': {
                'enabled': True,
                'requests_per_minute': 1000
            }
        },
        'services': [
            {'name': 'redis', 'host': 'redis.example.com', 'port': 6379},
            {'name': 'elasticsearch', 'host': 'es.example.com', 'port': 9200}
        ]
    }
    
    # Save as JSON
    with open('/tmp/app_config.json', 'w') as f:
        json.dump(app_config, f, indent=2)
    
    # Save as YAML
    with open('/tmp/app_config.yaml', 'w') as f:
        yaml.dump(app_config, f, default_flow_style=False)
    
    print("Sample configuration files created")

if __name__ == "__main__":
    # Create sample files
    create_sample_configs()
    
    # Load and process JSON
    with open('/tmp/app_config.json', 'r') as f:
        config = json.load(f)
    
    # Extract all paths
    paths = extract_json_paths(config)
    print(f"Found {len(paths)} configuration paths")
    
    # Validate schema
    required_fields = ['application.name', 'database.host', 'features.authentication']
    validation = validate_json_schema(config, required_fields)
    print(f"Configuration valid: {validation['valid']}")
    
    # Filter services
    services = config['services']
    redis_services = filter_json_by_criteria(services, {'name': 'redis'})
    print(f"Found {len(redis_services)} Redis services")
    
    # Transform structure
    mapping = {
        'app_name': 'application.name',
        'app_version': 'application.version',
        'db_host': 'database.host'
    }
    simplified_config = transform_json_structure(config, mapping)
    print(f"Simplified config: {simplified_config}")
    
    print("JSON/YAML processing script ready!")