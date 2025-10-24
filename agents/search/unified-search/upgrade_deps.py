#!/usr/bin/env python3
"""
Script to upgrade mcp-use to a compatible version
"""
import subprocess
import sys

def run_command(cmd):
    """Run a command and return the result"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        print(f"Command: {cmd}")
        print(f"Return code: {result.returncode}")
        if result.stdout:
            print(f"STDOUT:\n{result.stdout}")
        if result.stderr:
            print(f"STDERR:\n{result.stderr}")
        return result.returncode == 0
    except Exception as e:
        print(f"Error running command '{cmd}': {e}")
        return False

def main():
    """Main upgrade process"""
    print("Upgrading mcp-use to compatible version...")
    
    # First, uninstall the current version
    print("\n1. Uninstalling current mcp-use...")
    run_command("python -m pip uninstall mcp-use -y")
    
    # Install a compatible version
    print("\n2. Installing compatible mcp-use version...")
    success = run_command("python -m pip install 'mcp-use>=1.4.0'")
    
    if not success:
        print("\n3. Trying alternative installation...")
        # Try installing without version constraint first
        run_command("python -m pip install mcp-use --upgrade")
    
    # Verify installation
    print("\n4. Verifying installation...")
    run_command("python -m pip list | findstr mcp")
    
    print("\nUpgrade complete!")

if __name__ == "__main__":
    main()