#!/usr/bin/env python3
"""
Process Management for DevOps - Script 7
Why: Managing system processes is core to DevOps operations
"""

import subprocess
import psutil
import signal
import os
from typing import List, Dict

def run_command_safely(command: List[str], timeout: int = 30) -> Dict:
    """
    Execute shell command with error handling
    Why: Safe command execution prevents system crashes
    """
    try:
        result = subprocess.run(
            command,
            capture_output=True,  # Capture stdout and stderr
            text=True,           # Return strings instead of bytes
            timeout=timeout,     # Prevent hanging processes
            check=False          # Don't raise exception on non-zero exit
        )
        
        return {
            'success': result.returncode == 0,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'exit_code': result.returncode
        }
    except subprocess.TimeoutExpired:
        return {'success': False, 'error': 'Command timed out'}

def get_process_info(process_name: str) -> List[Dict]:
    """
    Get information about running processes
    Why: Monitor application health and resource usage
    """
    processes = []
    
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            if process_name.lower() in proc.info['name'].lower():
                processes.append({
                    'pid': proc.info['pid'],
                    'name': proc.info['name'],
                    'cpu_percent': proc.info['cpu_percent'],
                    'memory_percent': proc.info['memory_percent']
                })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue  # Skip processes we can't access
    
    return processes

def kill_process_gracefully(pid: int) -> bool:
    """
    Gracefully terminate process with fallback to force kill
    Why: Proper process termination prevents data corruption
    """
    try:
        os.kill(pid, signal.SIGTERM)  # Send termination signal
        
        # Wait for process to terminate
        import time
        for _ in range(10):  # Wait up to 10 seconds
            if not psutil.pid_exists(pid):
                return True
            time.sleep(1)
        
        # Force kill if still running
        os.kill(pid, signal.SIGKILL)
        return True
        
    except ProcessLookupError:
        return True  # Process already dead
    except PermissionError:
        return False  # No permission to kill

def monitor_system_resources() -> Dict:
    """
    Get current system resource usage
    Why: Monitor system health for capacity planning
    """
    return {
        'cpu_percent': psutil.cpu_percent(interval=1),  # 1-second interval for accuracy
        'memory': {
            'total': psutil.virtual_memory().total,
            'available': psutil.virtual_memory().available,
            'percent': psutil.virtual_memory().percent
        },
        'disk': {
            'total': psutil.disk_usage('/').total,
            'free': psutil.disk_usage('/').free,
            'percent': psutil.disk_usage('/').percent
        },
        'load_average': os.getloadavg()  # System load (Unix only)
    }

def start_daemon_process(command: List[str]) -> int:
    """
    Start process as daemon (background service)
    Why: Run services that persist after script ends
    """
    process = subprocess.Popen(
        command,
        stdout=subprocess.DEVNULL,  # Redirect output to null
        stderr=subprocess.DEVNULL,
        stdin=subprocess.DEVNULL,
        preexec_fn=os.setsid  # Create new session (Unix only)
    )
    return process.pid

if __name__ == "__main__":
    # Example: Monitor nginx processes
    nginx_procs = get_process_info('nginx')
    print(f"Found {len(nginx_procs)} nginx processes")
    
    # Example: Check system resources
    resources = monitor_system_resources()
    print(f"CPU: {resources['cpu_percent']}%")
    print("Process management script ready!")