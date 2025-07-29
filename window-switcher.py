#!/usr/bin/env python3
"""
Declarative Window Switcher for GNOME
Reads unified configuration from window-switcher-config.json
"""

import os
import sys
import subprocess
import time
import json
from pathlib import Path

UNIFIED_CONFIG_FILE = Path.home() / "code" / "window_switcher" / "window-switcher-config.json"

def load_unified_config():
    """Load unified configuration from JSON file"""
    try:
        if UNIFIED_CONFIG_FILE.exists():
            with open(UNIFIED_CONFIG_FILE, 'r') as f:
                return json.load(f)
        else:
            print(f"Unified config file not found: {UNIFIED_CONFIG_FILE}")
            return {"shortcuts": {}, "applications": {}, "aliases": {}}
    except Exception as e:
        print(f"Error loading unified config: {e}", file=sys.stderr)
        return {"shortcuts": {}, "applications": {}, "aliases": {}}

def resolve_app_id(app_name_or_alias, config):
    """Resolve app name or alias to actual application ID"""
    # Check if it's already a valid application ID
    if app_name_or_alias in config.get("applications", {}):
        return app_name_or_alias
    
    # Check if it's an alias
    if app_name_or_alias in config.get("aliases", {}):
        return config["aliases"][app_name_or_alias]
    
    # Return as-is if not found (for backward compatibility)
    return app_name_or_alias

def matches_app(app_id, wm_class, title, config):
    """Check if a window matches the given app using unified configuration"""
    applications = config.get("applications", {})
    
    if app_id not in applications:
        # Fallback to simple matching
        app_lower = app_id.lower()
        wm_class_lower = wm_class.lower()
        title_lower = title.lower()
        return app_lower in wm_class_lower or app_lower in title_lower
    
    app_config = applications[app_id]
    window_identification = app_config.get("window_identification", {})
    
    wm_class_lower = wm_class.lower()
    title_lower = title.lower()
    
    # Check window classes
    for window_class in window_identification.get('window_classes', []):
        if window_class.lower() in wm_class_lower:
            return True
    
    # Check title patterns  
    for pattern in window_identification.get('title_patterns', []):
        if pattern.lower() in title_lower:
            return True
    
    return False

def focus_window_by_class(app_name_or_alias):
    """Try to focus a window using wmctrl and unified configuration"""
    try:
        # Load unified configuration
        config = load_unified_config()
        
        # Resolve app name/alias to actual app ID
        app_id = resolve_app_id(app_name_or_alias, config)
        applications = config.get("applications", {})
        
        # Check if this is a launch-only mapping
        if app_id in applications:
            app_config = applications[app_id]
            if app_config.get('launch_only', False):
                return False  # Skip window searching, always launch
        
        # Get list of windows with their classes
        result = subprocess.run(['wmctrl', '-lx'], capture_output=True, text=True)
        if result.returncode != 0:
            return False
        
        # Check if this is a position-based mapping
        target_position = None
        if app_id in applications:
            window_identification = applications[app_id].get("window_identification", {})
            if 'window_position' in window_identification:
                target_position = window_identification['window_position']
        
        # Parse windows and find matching ones
        matching_windows = []
        for line in result.stdout.strip().split('\n'):
            if not line.strip():
                continue
            
            parts = line.split(None, 4)  # Split into max 5 parts
            if len(parts) < 4:
                continue
            
            window_id = parts[0]
            desktop = parts[1]
            wm_class = parts[2]  # This is WM_CLASS
            title = parts[4] if len(parts) > 4 else ""
            
            # Skip windows on desktop -1 (usually system windows)
            if desktop == '-1':
                continue
            
            if matches_app(app_id, wm_class, title, config):
                matching_windows.append((window_id, wm_class, title))
        
        if not matching_windows:
            return False
        
        # Handle position-based selection
        if target_position is not None:
            if target_position < len(matching_windows):
                window_id = matching_windows[target_position][0]
                focus_result = subprocess.run(['wmctrl', '-ia', window_id], capture_output=True)
                if focus_result.returncode == 0:
                    print(f"Focused window {target_position}: {matching_windows[target_position][2]} (class: {matching_windows[target_position][1]})")
                    return True
            else:
                # Position not found, focus the first one
                window_id = matching_windows[0][0]
                focus_result = subprocess.run(['wmctrl', '-ia', window_id], capture_output=True)
                if focus_result.returncode == 0:
                    print(f"Focused first available window: {matching_windows[0][2]} (class: {matching_windows[0][1]})")
                    return True
        
        # Default: focus the first matching window
        window_id = matching_windows[0][0]
        focus_result = subprocess.run(['wmctrl', '-ia', window_id], capture_output=True)
        if focus_result.returncode == 0:
            print(f"Focused window: {matching_windows[0][2]} (class: {matching_windows[0][1]})")
            return True
        
        return False
        
    except Exception as e:
        print(f"Error focusing window: {e}", file=sys.stderr)
        return False

def launch_application(command):
    """Launch an application using the given command"""
    try:
        # Launch in background, detached from this process
        subprocess.Popen(command, shell=True, 
                        stdout=subprocess.DEVNULL, 
                        stderr=subprocess.DEVNULL,
                        preexec_fn=os.setsid)
        return True
    except Exception as e:
        print(f"Error launching application: {e}", file=sys.stderr)
        return False

def handle_key(pressed_key):
    """Handle a key press by focusing or launching the configured application"""
    config = load_unified_config()
    shortcuts = config.get("shortcuts", {})
    applications = config.get("applications", {})
    
    if pressed_key not in shortcuts:
        print(f"No configuration found for key: {pressed_key}")
        return
    
    app_id = shortcuts[pressed_key]
    
    if app_id not in applications:
        print(f"Application '{app_id}' not found in configuration")
        return
    
    app_config = applications[app_id]
    app_name = app_config.get('name', app_id)
    command = app_config.get('launch_command', '')
    
    print(f"Handling {pressed_key}: {app_name}")
    
    # Try to focus existing window first
    if focus_window_by_class(app_id):
        print(f"Focused existing {app_name} window")
    else:
        print(f"No existing window found, launching: {command}")
        launch_application(command)
        # Give the application a moment to start
        time.sleep(0.5)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 window-switcher.py <key>")
        print("Example: python3 window-switcher.py F1")
        sys.exit(1)
    
    key = sys.argv[1]
    handle_key(key)
