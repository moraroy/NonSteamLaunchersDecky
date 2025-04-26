import os
import platform
import decky_plugin
import logging
import vdf
from decky_plugin import DECKY_USER_HOME

# Path to the env_vars file for Linux
env_vars_path = f"{DECKY_USER_HOME}/.config/systemd/user/env_vars"
env_vars = {}

def check_and_set_path(env_vars, key, path):
    if os.path.exists(path):
        env_vars[key] = path

def refresh_env_vars():
    global env_vars
    env_vars = {}
    decky_plugin.logger.info("Refreshing environment variables...")

    if platform.system() == "Windows":  # Check if the system is Windows
        decky_plugin.logger.info("Running on Windows")
        # Define paths for Windows
        paths = {
            'epicshortcutdirectory': "C:\\Program Files (x86)\\Epic Games\\Launcher\\Portal\\Binaries\\Win32\\EpicGamesLauncher.exe",
            'epicstartingdir': "C:\\Program Files (x86)\\Epic Games\\Launcher\\Portal\\Binaries\\Win32",
            'gogshortcutdirectory': "C:\\Program Files (x86)\\GOG Galaxy\\GalaxyClient.exe",
            'gogstartingdir': "C:\\Program Files (x86)\\GOG Galaxy",
            'uplayshortcutdirectory': "C:\\Program Files (x86)\\Ubisoft\\Ubisoft Game Launcher\\upc.exe",
            'uplaystartingdir': "C:\\Program Files (x86)\\Ubisoft\\Ubisoft Game Launcher",
            'battlenetshortcutdirectory': "C:\\Program Files (x86)\\Battle.net\\Battle.net Launcher.exe",
            'battlenetstartingdir': "C:\\Program Files (x86)\\Battle.net",
            'eaappshortcutdirectory': "C:\\Program Files\\Electronic Arts\\EA Desktop\\EA Desktop\\EADesktop.exe",
            'eaappstartingdir': "C:\\Program Files\\Electronic Arts\\EA Desktop\\EA Desktop",
            'amazonshortcutdirectory': "C:\\Users\\steamuser\\AppData\\Local\\Amazon Games\\App\\Amazon Games.exe",
            'amazonstartingdir': "C:\\Users\\steamuser\\AppData\\Local\\Amazon Games\\App",
            'itchioshortcutdirectory': "C:\\Users\\steamuser\\AppData\\Local\\itch\\app-26.1.9\\itch.exe",
            'itchiostartingdir': "C:\\Users\\steamuser\\AppData\\Local\\itch\\app-26.1.9",
            'legacyshortcutdirectory': "C:\\Program Files\\Legacy Games\\Legacy Games Launcher\\Legacy Games Launcher.exe",
            'legacystartingdir': "C:\\Program Files\\Legacy Games\\Legacy Games Launcher",
            'humbleshortcutdirectory': "C:\\Program Files\\Humble App\\Humble App.exe",
            'humblestartingdir': "C:\\Program Files\\Humble App",
            'indieshortcutdirectory': "C:\\Program Files\\IGClient\\IGClient.exe",
            'indiestartingdir': "C:\\Program Files\\IGClient",
            'rockstarshortcutdirectory': "C:\\Program Files\\Rockstar Games\\Launcher\\Launcher.exe",
            'rockstarstartingdir': "C:\\Program Files\\Rockstar Games\\Launcher",
            'psplusshortcutdirectory': "C:\\Program Files (x86)\\PlayStationPlus\\pspluslauncher.exe",
            'psplusstartingdir': "C:\\Program Files (x86)\\PlayStationPlus",
            'hoyoplayshortcutdirectory': "C:\\Program Files\\HoYoPlay\\launcher.exe",
            'hoyoplaystartingdir': "C:\\Program Files\\HoYoPlay"
        }

        # Check each path and set in env_vars if it exists
        for key, path in paths.items():
            check_and_set_path(env_vars, key, path)

        # Steam ID retrieval function
        USERS_DATA_DIR = "C:\\Program Files (x86)\\Steam\\userdata"
        decky_plugin.logger.info(f"Steam userdata directory: {USERS_DATA_DIR}")

        def get_users():
            users = [item for item in os.listdir(USERS_DATA_DIR) if os.path.isdir(os.path.join(USERS_DATA_DIR, item)) and item != '0']
            decky_plugin.logger.info(f"Found users: {users}")
            return users

        def get_current_user():
            try:
                current_user = max(get_users(), key=lambda user: os.path.getmtime(os.path.join(USERS_DATA_DIR, user, 'config', 'shortcuts.vdf')))
                decky_plugin.logger.info(f"Current user: {current_user}")
                return current_user
            except FileNotFoundError:
                # If the file is not found, create it
                current_user = max(get_users(), key=lambda user: os.path.getmtime(os.path.join(USERS_DATA_DIR, user, 'config')))
                shortcuts_path = os.path.join(USERS_DATA_DIR, current_user, 'config', 'shortcuts.vdf')
                decky_plugin.logger.info(f"VDF file not found at: {shortcuts_path}, creating and initializing it.")
                try:
                    os.makedirs(os.path.dirname(shortcuts_path), exist_ok=True)
                    with open(shortcuts_path, 'wb') as file:
                        file.write(vdf.binary_dumps({'shortcuts': {}}))
                    os.chmod(shortcuts_path, 0o755)
                except Exception as e:
                    decky_plugin.logger.info(f"Error creating shortcuts file: {e}")
                    return None
                return current_user
            except Exception as e:
                logging.error(f'Failed to get current user: {str(e)}')
                return None

        users = get_users()
        current_user = get_current_user()
        if current_user:
            env_vars['steamid3'] = current_user
        else:
            env_vars['steamid3'] = None
        decky_plugin.logger.info(f"Steam ID3: {env_vars['steamid3']}")

        # Miscellaneous Variables
        env_vars['logged_in_home'] = DECKY_USER_HOME
    else:
        decky_plugin.logger.info("Running on Linux or other OS")

        # Check if the env_vars file exists
        if not os.path.exists(env_vars_path):
            decky_plugin.logger.error(f"Error: {env_vars_path} does not exist.")
            return

        # Read variables from the file
        with open(env_vars_path, 'r') as f:
            lines = f.readlines()
        for line in lines:
            if line.startswith('export '):
                line = line[7:]  # Remove 'export '
            name, value = line.strip().split('=', 1)
            env_vars[name] = value

        # Delete env_vars entries for Chrome shortcuts so that they're only added once
        with open(env_vars_path, 'w') as f:
            for line in lines:
                if 'chromelaunchoptions' not in line and 'websites_str' not in line:
                    f.write(line)

    return env_vars
