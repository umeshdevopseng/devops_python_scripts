#!/usr/bin/env python3

import platform
import psutil
import datetime

def get_system_info():
    """
    Get basic system information including OS, CPU, memory, and disk usage
    """
    system_info = {
        "OS": platform.system(),
        "OS Version": platform.version(),
        "Machine": platform.machine(),
        "Processor": platform.processor(),
        "Python Version": platform.python_version(),
        "CPU Usage": f"{psutil.cpu_percent()}%",
        "Memory Usage": f"{psutil.virtual_memory().percent}%",
        "Disk Usage": f"{psutil.disk_usage('/').percent}%",
        "Current Time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    return system_info

def display_info(info):
    """
    Display system information in a formatted way
    """
    print("\n=== System Information ===")
    for key, value in info.items():
        print(f"{key}: {value}")

if __name__ == "__main__":
    system_info = get_system_info()
    display_info(system_info)