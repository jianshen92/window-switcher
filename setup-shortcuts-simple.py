#!/usr/bin/env python3
"""
Simple setup script that creates xbindkeys configuration
This is more reliable than trying to use gsettings
"""

import subprocess
import sys
import json
from pathlib import Path

UNIFIED_CONFIG_FILE = Path.home() / "code" / "window_switcher" / "window-switcher-config.json"
XBINDKEYS_CONFIG = Path.home() / ".xbindkeysrc"
SWITCHER_SCRIPT = Path.home() / "code" / "window_switcher" / "window-switcher.py"

def load_config():
    """Load unified configuration"""
    try:
        if not UNIFIED_CONFIG_FILE.exists():
            print(f"Unified config file not found: {UNIFIED_CONFIG_FILE}")
            return {}
        
        with open(UNIFIED_CONFIG_FILE, 'r') as f:
            config = json.load(f)
            shortcuts = config.get("shortcuts", {})
            applications = config.get("applications", {})
            
            # Build config in the format expected by setup script
            result = {}
            for key, app_id in shortcuts.items():
                if app_id in applications:
                    app_config = applications[app_id]
                    result[key] = {
                        'app_name': app_config.get('name', app_id),
                        'command': app_config.get('launch_command', '')
                    }
            return result
    except Exception as e:
        print(f"Error loading unified config: {e}", file=sys.stderr)
        return {}

def setup_xbindkeys():
    """Create xbindkeys configuration"""
    config = load_config()
    
    if not config:
        print("No configuration found!")
        return
    
    # Create xbindkeys config
    xbindkeys_content = "# Window Switcher Hotkeys\n# Generated automatically\n\n"
    
    for key, app_config in config.items():
        xbindkeys_content += f'# {app_config["app_name"]}\n'
        xbindkeys_content += f'"{SWITCHER_SCRIPT} {key}"\n'
        xbindkeys_content += f'  {key}\n\n'
    
    with open(XBINDKEYS_CONFIG, 'w') as f:
        f.write(xbindkeys_content)
    
    print(f"Created xbindkeys config: {XBINDKEYS_CONFIG}")
    
    # Check if xbindkeys is installed
    try:
        subprocess.run(['which', 'xbindkeys'], check=True, capture_output=True)
    except subprocess.CalledProcessError:
        print("xbindkeys not found. Installing...")
        try:
            subprocess.run(['sudo', 'apt', 'install', '-y', 'xbindkeys'], check=True)
        except subprocess.CalledProcessError:
            print("Failed to install xbindkeys. Please install it manually:")
            print("sudo apt install xbindkeys")
            return
    
    # Reload xbindkeys
    try:
        subprocess.run(['killall', 'xbindkeys'], capture_output=True)
    except subprocess.CalledProcessError:
        pass  # xbindkeys wasn't running
    
    try:
        subprocess.run(['xbindkeys'], check=True)
        print("✓ xbindkeys started")
    except subprocess.CalledProcessError as e:
        print(f"✗ Error starting xbindkeys: {e}")
    
    print("\nShortcuts configured:")
    for key, app_config in config.items():
        print(f"  {key} -> {app_config['app_name']}")

if __name__ == "__main__":
    print("Setting up window switcher with xbindkeys...")
    setup_xbindkeys()
    print(f"\nTo make xbindkeys start automatically, add 'xbindkeys' to your startup applications.")
    print(f"Edit {UNIFIED_CONFIG_FILE} and re-run this script to update shortcuts.")
