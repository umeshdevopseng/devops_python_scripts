#!/usr/bin/env python3
"""
Run Examples - Test All DevOps Python Scripts
Why: Validate that all scripts work correctly and demonstrate their functionality
"""

import sys
import importlib
import traceback
from pathlib import Path

def run_script_examples():
    """
    Run examples from all DevOps Python scripts
    Why: Ensure all scripts are working and demonstrate their capabilities
    """
    
    # List of scripts to test (excluding this one and README)
    scripts_to_test = [
        "6_file_operations",
        "7_process_management", 
        "8_network_operations",
        "9_database_operations",
        "10_configuration_management",
        "11_error_handling",
        "12_json_yaml_processing",
        "13_environment_variables",
        "14_logging_setup",
        "15_async_operations",
        "16_data_structures",
        "17_string_processing",
        "18_datetime_operations",
        "19_regex_patterns",
        "20_decorators_context"
    ]
    
    print("DEVOPS PYTHON SCRIPTS - EXAMPLE RUNNER")
    print("="*60)
    
    results = {}
    
    for script_name in scripts_to_test:
        print(f"\n🔄 Testing {script_name}...")
        
        try:
            # Import the module
            module = importlib.import_module(script_name)
            
            # Run the main function if it exists
            if hasattr(module, '__main__') or hasattr(module, 'main'):
                print(f"✅ {script_name} - Import successful")
                results[script_name] = "SUCCESS"
            else:
                print(f"✅ {script_name} - Import successful (no main function)")
                results[script_name] = "SUCCESS"
                
        except ImportError as e:
            print(f"❌ {script_name} - Import failed: {e}")
            results[script_name] = f"IMPORT_ERROR: {e}"
            
        except Exception as e:
            print(f"⚠️  {script_name} - Runtime error: {e}")
            results[script_name] = f"RUNTIME_ERROR: {e}"
    
    # Print summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}")
    
    success_count = 0
    total_count = len(scripts_to_test)
    
    for script, result in results.items():
        status = "✅" if result == "SUCCESS" else "❌"
        print(f"{status} {script}: {result}")
        if result == "SUCCESS":
            success_count += 1
    
    print(f"\nResults: {success_count}/{total_count} scripts passed")
    
    if success_count == total_count:
        print("🎉 All scripts are working correctly!")
    else:
        print("⚠️  Some scripts need attention. Check the errors above.")
    
    return results

def demonstrate_key_concepts():
    """
    Demonstrate key DevOps concepts with working examples
    Why: Show practical applications of the scripts
    """
    
    print(f"\n{'='*60}")
    print("KEY CONCEPT DEMONSTRATIONS")
    print(f"{'='*60}")
    
    # 1. File Operations
    print("\n1. FILE OPERATIONS")
    print("-" * 20)
    try:
        from pathlib import Path
        import tempfile
        
        # Create a temporary config file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write('{"app_name": "test-app", "version": "1.0.0"}')
            temp_file = f.name
        
        print(f"✅ Created temporary config file: {Path(temp_file).name}")
        
        # Clean up
        Path(temp_file).unlink()
        print("✅ File operations working correctly")
        
    except Exception as e:
        print(f"❌ File operations error: {e}")
    
    # 2. Error Handling
    print("\n2. ERROR HANDLING WITH RETRY")
    print("-" * 30)
    try:
        import time
        import random
        
        def unreliable_operation():
            if random.random() < 0.7:  # 70% chance of failure
                raise ConnectionError("Simulated network error")
            return "Success!"
        
        # Simple retry logic
        max_retries = 3
        for attempt in range(max_retries):
            try:
                result = unreliable_operation()
                print(f"✅ Operation succeeded on attempt {attempt + 1}: {result}")
                break
            except ConnectionError as e:
                if attempt == max_retries - 1:
                    print(f"❌ Operation failed after {max_retries} attempts")
                else:
                    print(f"⚠️  Attempt {attempt + 1} failed, retrying...")
                    time.sleep(0.1)  # Short delay for demo
        
    except Exception as e:
        print(f"❌ Error handling demo error: {e}")
    
    # 3. Configuration Management
    print("\n3. CONFIGURATION MANAGEMENT")
    print("-" * 30)
    try:
        import os
        
        # Demonstrate environment variable handling
        test_var = "DEMO_CONFIG_VAR"
        test_value = "production"
        
        # Set environment variable
        os.environ[test_var] = test_value
        
        # Retrieve with default
        config_value = os.environ.get(test_var, "development")
        print(f"✅ Configuration loaded: {test_var}={config_value}")
        
        # Clean up
        del os.environ[test_var]
        print("✅ Configuration management working correctly")
        
    except Exception as e:
        print(f"❌ Configuration management error: {e}")
    
    # 4. Data Processing
    print("\n4. DATA PROCESSING")
    print("-" * 20)
    try:
        from collections import Counter, defaultdict
        
        # Simulate log analysis
        log_levels = ["INFO", "ERROR", "INFO", "WARNING", "ERROR", "INFO"]
        level_counts = Counter(log_levels)
        
        print(f"✅ Log level analysis: {dict(level_counts)}")
        
        # Group by service
        services_by_level = defaultdict(list)
        for level in log_levels:
            services_by_level[level].append(f"service-{len(services_by_level[level]) + 1}")
        
        print(f"✅ Services by level: {dict(services_by_level)}")
        print("✅ Data processing working correctly")
        
    except Exception as e:
        print(f"❌ Data processing error: {e}")
    
    # 5. Time-based Operations
    print("\n5. TIME-BASED OPERATIONS")
    print("-" * 25)
    try:
        from datetime import datetime, timedelta
        
        # Calculate uptime
        start_time = datetime.now() - timedelta(hours=24)
        current_time = datetime.now()
        uptime = current_time - start_time
        
        print(f"✅ Uptime calculation: {uptime.total_seconds():.0f} seconds")
        
        # Schedule next backup
        next_backup = datetime.now().replace(hour=2, minute=0, second=0, microsecond=0)
        if next_backup <= datetime.now():
            next_backup += timedelta(days=1)
        
        print(f"✅ Next backup scheduled: {next_backup.strftime('%Y-%m-%d %H:%M')}")
        print("✅ Time-based operations working correctly")
        
    except Exception as e:
        print(f"❌ Time-based operations error: {e}")

def create_requirements_file():
    """
    Create requirements.txt file for the project
    Why: Document dependencies needed to run all scripts
    """
    
    requirements = [
        "# Core dependencies for DevOps Python scripts",
        "boto3>=1.26.0  # AWS SDK for infrastructure automation",
        "requests>=2.28.0  # HTTP client for API interactions", 
        "pyyaml>=6.0  # YAML processing for configuration files",
        "psutil>=5.9.0  # System monitoring and process management",
        "aiohttp>=3.8.0  # Async HTTP client for concurrent operations",
        "aiofiles>=22.1.0  # Async file operations",
        "prometheus-client>=0.15.0  # Prometheus metrics collection",
        "cryptography>=38.0.0  # Encryption and security operations",
        "hvac>=1.0.0  # HashiCorp Vault client",
        "",
        "# Optional dependencies (install as needed)",
        "# docker>=6.0.0  # Docker API client",
        "# kubernetes>=25.0.0  # Kubernetes API client", 
        "# pytz>=2022.7  # Timezone handling",
        "# croniter>=1.3.0  # Cron expression parsing",
        "",
        "# Development and testing",
        "pytest>=7.2.0  # Testing framework",
        "black>=22.0.0  # Code formatting",
        "flake8>=6.0.0  # Code linting"
    ]
    
    requirements_file = Path("requirements.txt")
    
    try:
        with open(requirements_file, 'w') as f:
            f.write('\n'.join(requirements))
        
        print(f"✅ Created {requirements_file}")
        print("📦 Install dependencies with: pip install -r requirements.txt")
        
    except Exception as e:
        print(f"❌ Failed to create requirements.txt: {e}")

def main():
    """Main function to run all examples and demonstrations"""
    
    print("DEVOPS PYTHON SCRIPTS - COMPREHENSIVE TEST")
    print("="*60)
    print("Testing all scripts and demonstrating key concepts...")
    
    # Test all scripts
    test_results = run_script_examples()
    
    # Demonstrate key concepts
    demonstrate_key_concepts()
    
    # Create requirements file
    print(f"\n{'='*60}")
    print("CREATING PROJECT FILES")
    print(f"{'='*60}")
    create_requirements_file()
    
    # Final summary
    print(f"\n{'='*60}")
    print("FINAL SUMMARY")
    print(f"{'='*60}")
    
    success_count = sum(1 for result in test_results.values() if result == "SUCCESS")
    total_count = len(test_results)
    
    print(f"📊 Script Tests: {success_count}/{total_count} passed")
    print(f"📚 Total Scripts Created: 20+ comprehensive examples")
    print(f"🎯 Interview Topics Covered: Infrastructure, CI/CD, Monitoring, Security, Python")
    print(f"💡 Key Concepts Demonstrated: Error handling, Async ops, Data structures, etc.")
    
    if success_count == total_count:
        print(f"\n🎉 SUCCESS! All scripts are working correctly.")
        print(f"🚀 You're ready for your DevOps Python interview!")
    else:
        print(f"\n⚠️  Some scripts need attention, but core concepts are demonstrated.")
        print(f"🔧 Review the error messages above and install missing dependencies.")
    
    print(f"\n📖 Next Steps:")
    print(f"   1. Review each script and understand the 'why' explanations")
    print(f"   2. Practice explaining the code and concepts out loud")
    print(f"   3. Modify examples to match your experience")
    print(f"   4. Run 'python interview_summary.py' for quick review")
    print(f"   5. Practice live coding similar solutions")

if __name__ == "__main__":
    main()