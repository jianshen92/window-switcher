#!/usr/bin/env python3
"""
StarCraft Mode Toggle
Activate/deactivate window switcher hotkeys
"""

import subprocess
import json
import sys
from pathlib import Path

UNIFIED_CONFIG_PATH = Path.home() / "code" / "window_switcher" / "window-switcher-config.json"
STATE_FILE = Path.home() / "code" / "window_switcher" / ".starcraft-mode-state"


def load_config():
    """Load unified configuration and return shortcuts with app names"""
    try:
        if UNIFIED_CONFIG_PATH.exists():
            with open(UNIFIED_CONFIG_PATH, 'r') as f:
                config = json.load(f)
                shortcuts = config.get("shortcuts", {})
                applications = config.get("applications", {})
                
                # Build a mapping of shortcut -> app name
                result = {}
                for key, app_id in shortcuts.items():
                    if app_id in applications:
                        result[key] = applications[app_id].get('name', app_id)
                    else:
                        result[key] = app_id
                return result
        else:
            print(f"Unified config file not found: {UNIFIED_CONFIG_PATH}")
            return {}
    except Exception as e:
        print(f"Error loading unified config: {e}", file=sys.stderr)
        return {}

def is_starcraft_mode_active():
    """Check if StarCraft mode is currently active"""
    return STATE_FILE.exists()

def activate_starcraft_mode():
    """Activate StarCraft mode"""
    try:
        # Kill existing xbindkeys if running
        subprocess.run(['killall', 'xbindkeys'], capture_output=True)

        # Start xbindkeys with our config
        result = subprocess.run(['xbindkeys'], capture_output=True)

        if result.returncode == 0:
            # Create state file
            STATE_FILE.touch()
            print("🚀 StarCraft Mode ACTIVATED")
            print("   Hotkeys are now active!")
            return True
        else:
            print("❌ Failed to activate StarCraft mode")
            return False
    except Exception as e:
        print(f"❌ Error activating StarCraft mode: {e}")
        return False

def deactivate_starcraft_mode():
    """Deactivate StarCraft mode"""
    try:
        # Kill xbindkeys
        result = subprocess.run(['killall', 'xbindkeys'], capture_output=True)

        # Remove state file
        if STATE_FILE.exists():
            STATE_FILE.unlink()

        print("⏹️  StarCraft Mode DEACTIVATED")
        print("   Hotkeys are now disabled")
        return True

    except Exception as e:
        print(f"❌ Error deactivating StarCraft mode: {e}")
        return False

def toggle_starcraft_mode():
    """Toggle StarCraft mode on/off"""
    if is_starcraft_mode_active():
        deactivate_starcraft_mode()
    else:
        activate_starcraft_mode()

def show_status():
    """Show current StarCraft mode status"""
    config = load_config()
    if is_starcraft_mode_active():
        print("🚀 StarCraft Mode is ACTIVE")
        for key, app in config.items():
            print(f"   {key} → {app}")
    else:
        print("⏹️  StarCraft Mode is INACTIVE")
        print("   Hotkeys are disabled")

def show_help():
    """Show help message"""
    print("StarCraft Mode Control")
    print("")
    print("Usage: starcraft-mode.py [command]")
    print("")
    print("Commands:")
    print("  on       - Activate StarCraft mode")
    print("  off      - Deactivate StarCraft mode")
    print("  toggle   - Toggle StarCraft mode (default)")
    print("  status   - Show current status")
    print("  --help   - Show this help message")
    print("")
    print("If no command is provided, 'toggle' is used by default.")
    print("")
    print("Examples:")
    print("  sc2              # Toggle mode on/off")
    print("  sc2 status       # Check current status")
    print("  sc2 on           # Activate mode")

def main():
    # Default to toggle if no arguments
    command = "toggle"
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
    
    if command in ["--help", "-h", "help"]:
        show_help()
    elif command == "on":
        activate_starcraft_mode()
    elif command == "off":
        deactivate_starcraft_mode()
    elif command == "toggle":
        toggle_starcraft_mode()
    elif command == "status":
        show_status()
    else:
        print(f"Unknown command: {command}")
        print("Use 'sc2 --help' for usage information.")
        sys.exit(1)

if __name__ == "__main__":
    main()

