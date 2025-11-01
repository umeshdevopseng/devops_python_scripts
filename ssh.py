#!/usr/bin/env python3
import paramiko

# --- SSH Connection Details ---
hostname = "your.server.com"     # or IP address
username = "your_username"
password = "your_password"

# --- Create SSH Client ---
client = paramiko.SSHClient()

# Automatically add new host keys (like known_hosts)
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    # Connect to remote host
    print(f"Connecting to {hostname}...")
    client.connect(hostname, username=username, password=password)

    # Run a command (for example, check uptime)
    stdin, stdout, stderr = client.exec_command("uptime")

    # Read and print output
    print("Command output:")
    print(stdout.read().decode())

except Exception as e:
    print(f"❌ Connection failed: {e}")

finally:
    client.close()
    print("Connection closed.")

