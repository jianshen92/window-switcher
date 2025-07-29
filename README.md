# StarCraft Mode Window Switcher

A minimal, declarative window switcher inspired by StarCraft's screen management for Linux/GNOME. Switch between applications with F1-F5 hotkeys like a pro gamer!

## Features

- **Unified JSON Configuration**: Single config file for all settings
- **Position-Based Window Selection**: F1 → first browser window, F2 → second browser window
- **Focus or Launch**: If a window exists, it focuses it; otherwise, it launches the application  
- **StarCraft Mode Toggle**: Easily enable/disable hotkeys with `sc2` command
- **Minimal Dependencies**: Uses wmctrl for reliable window management

## Core Files

- `window-switcher-config.json` - Unified configuration (shortcuts + applications)
- `window-switcher.py` - Main window switching logic
- `starcraft-mode.py` - Toggle script (aliased as `sc2`)
- `setup-shortcuts-simple.py` - Setup script using xbindkeys

## Quick Start

1. **Edit the unified config** `window-switcher-config.json`:
   ```json
   {
     "shortcuts": {
       "F1": "js-personal-browser",
       "F2": "bentoml-browser",
       "F3": "cursor-editor",
       "F4": "warp-terminal",
       "F5": "obsidian-notes"
     },
     "applications": {
       "js-personal-browser": {
         "name": "Brave Browser (JS Personal)",
         "launch_command": "brave-browser --profile-directory='JS Personal'",
         "window_identification": {
           "window_classes": ["brave-browser"],
           "window_position": 0
         }
       }
     }
   }
   ```

2. **Apply the shortcuts**:
   ```bash
   ./setup-shortcuts-simple.py
   ```

3. **Enable StarCraft Mode**:
   ```bash
   sc2  # Toggle on/off
   ```

4. **Use your shortcuts**: Press F1-F5 to switch between applications!

## StarCraft Mode Commands

- `sc2` - Toggle StarCraft mode on/off (default)
- `sc2 status` - Check current status and show hotkey mappings
- `sc2 on` - Activate StarCraft mode
- `sc2 off` - Deactivate StarCraft mode
- `sc2 --help` - Show help

## Unified Configuration Format

The `window-switcher-config.json` has three main sections:

### 1. Shortcuts
Maps keys to application IDs:
```json
"shortcuts": {
  "F1": "my-browser",
  "F2": "my-editor"
}
```

### 2. Applications  
Defines each application with its properties:
```json
"applications": {
  "my-browser": {
    "name": "My Browser",
    "launch_command": "firefox",
    "window_identification": {
      "window_classes": ["firefox"],
      "title_patterns": ["firefox"]
    }
  }
}
```

### 3. Position-Based Selection
For multiple windows of the same application:
```json
"window_identification": {
  "window_classes": ["brave-browser"],
  "window_position": 0  // 0 = first window, 1 = second window
}
```

## How It Works

1. **Window Detection**: Uses `wmctrl` to find windows by class name and title patterns
2. **Position Logic**: For multiple windows of same app, selects by position (0=first, 1=second)
3. **Focus Logic**: If a matching window exists, it brings it to focus
4. **Launch Logic**: If no window exists, it launches the specified command
5. **Hotkey Binding**: Uses xbindkeys for reliable global hotkeys

## Manual Testing

Test individual shortcuts manually:
```bash
python3 window-switcher.py F1  # Focus first Brave window
python3 window-switcher.py F2  # Focus second Brave window
python3 window-switcher.py F3  # Focus Cursor editor
```

## Customization

### Adding More Applications

Edit `window-switcher-config.json` and add to the applications section:
```json
"spotify-music": {
  "name": "Spotify",
  "launch_command": "spotify",
  "window_identification": {
    "window_classes": ["spotify"],
    "title_patterns": ["spotify"]
  }
}
```

Then add to shortcuts:
```json
"shortcuts": {
  "F6": "spotify-music"
}
```

### Multiple Windows of Same App

For apps like terminals where you want multiple instances:
```json
"terminal-1": {
  "name": "Terminal 1",
  "launch_command": "gnome-terminal",
  "window_identification": {
    "window_classes": ["gnome-terminal-server"],
    "window_position": 0
  }
},
"terminal-2": {
  "name": "Terminal 2", 
  "launch_command": "gnome-terminal",
  "window_identification": {
    "window_classes": ["gnome-terminal-server"],
    "window_position": 1
  }
}
```

## Troubleshooting

### xbindkeys not starting
- Install: `sudo apt install xbindkeys`
- Add to startup applications: `xbindkeys`

### Application not found
- Check the application name in the config matches the window class
- Use `wmctrl -l` to see current windows and their names

### Hotkeys not working
- Make sure xbindkeys is running: `ps aux | grep xbindkeys`
- Check config syntax: `cat ~/.xbindkeysrc`
- Restart: `killall xbindkeys && xbindkeys`

## Philosophy

This tool follows the principle of **declarative configuration**:
- Edit the config file to declare what you want
- Run the setup script to apply it
- No complex GUIs or manual clicking through settings
- Version control friendly (your shortcuts are just a text file!)

Inspired by StarCraft's screen positioning system where you could quickly jump between different areas of the battlefield.
