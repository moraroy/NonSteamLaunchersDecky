import os
import platform
import logging
import vdf
import decky_plugin
from decky_plugin import DECKY_USER_HOME

env_vars_path = f"{DECKY_USER_HOME}/.config/systemd/user/env_vars"
env_vars = {}

# Detect OS
SYSTEM = platform.system()
WINREG_AVAILABLE = False

# Conditionally import winreg for Windows
if SYSTEM == "Windows":
    try:
        import winreg
        WINREG_AVAILABLE = True
    except ImportError:
        decky_plugin.logger.warning("winreg not available, skipping Windows registry access")

# ---------- Helpers ----------
def check_and_set_path(env_vars, key, path):
    if path and os.path.exists(path):
        env_vars[key] = path

# ---------- Windows Registry Helpers ----------
def get_reg_value(root, subkey, name):
    if not WINREG_AVAILABLE:
        return None
    try:
        with winreg.OpenKey(root, subkey) as key:
            value, _ = winreg.QueryValueEx(key, name)
            return value
    except Exception:
        return None

# ---------- Launcher Detection (Windows only) ----------
def find_launcher_path():
    if not WINREG_AVAILABLE:
        return {}

    launchers = {}

    registry_paths = [
        ("epic", winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Epic Games\EpicGamesLauncher", "AppDataPath", "EpicGamesLauncher.exe"),
        ("gog", winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\GOG.com\GalaxyClient", "path", "GalaxyClient.exe"),
        ("uplay", winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Ubisoft\Launcher", "InstallDir", "upc.exe"),
        ("battlenet", winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Battle.net", "InstallPath", "Battle.net Launcher.exe"),
        ("eaapp", winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Electronic Arts\EA Desktop", "InstallDir", "EADesktop.exe"),
        ("rockstar", winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Rockstar Games\Launcher", "InstallFolder", "Launcher.exe"),
        ("hoyoplay", winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\HoYoPlay", "InstallPath", "launcher.exe"),
        ("amazon", winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Amazon Games", "InstallPath", "App/Amazon Games.exe"),
        ("itchio", winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\itch", "InstallLocation", "itch.exe"),
        ("legacy", winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Legacy Games\Launcher", "InstallDir", "Legacy Games Launcher.exe"),
        ("humble", winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Humble App", "InstallDir", "Humble App.exe"),
        ("indie", winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\IGClient", "InstallDir", "IGClient.exe"),
        ("psplus", winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\PlayStationPlus", "InstallDir", "pspluslauncher.exe")
    ]

    for name, root, key, reg_name, exe_name in registry_paths:
        path = get_reg_value(root, key, reg_name)
        if path:
            exe_path = os.path.join(path, exe_name)
            launchers[f"{name}shortcutdirectory"] = exe_path
            launchers[f"{name}startingdir"] = os.path.dirname(exe_path)

    return launchers

# ---------- Steam Detection ----------
def get_steam_userdata_dir():
    if SYSTEM != "Windows" or not WINREG_AVAILABLE:
        return None

    possible_paths = []
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam") as key:
            install_path, _ = winreg.QueryValueEx(key, "SteamPath")
            if install_path:
                possible_paths.append(os.path.join(install_path, "userdata"))
    except Exception:
        pass

    # Fallback common paths
    for drive in "CDEFGHIJKLMNOPQRSTUVWXYZ":
        possible_paths.append(fr"{drive}:\Steam\userdata")

    for path in possible_paths:
        if os.path.exists(path):
            return path
    return None

# ---------- Main Refresh Function ----------
def refresh_env_vars():
    global env_vars
    env_vars = {}
    decky_plugin.logger.info("Refreshing environment variables...")

    if SYSTEM == "Windows" and WINREG_AVAILABLE:
        decky_plugin.logger.info("Running Windows-specific logic")

        # Launcher detection
        launcher_paths = find_launcher_path()
        for key, path in launcher_paths.items():
            check_and_set_path(env_vars, key, path)

        # Steam detection
        USERS_DATA_DIR = get_steam_userdata_dir()
        decky_plugin.logger.info(f"Steam userdata directory: {USERS_DATA_DIR}")

        if not USERS_DATA_DIR or not os.path.exists(USERS_DATA_DIR):
            decky_plugin.logger.warning("Steam userdata directory not found.")
            env_vars["steamid3"] = None
        else:
            try:
                users = [
                    u for u in os.listdir(USERS_DATA_DIR)
                    if os.path.isdir(os.path.join(USERS_DATA_DIR, u)) and u != "0"
                ]
                decky_plugin.logger.info(f"Found Steam users: {users}")

                if users:
                    def get_user_timestamp(uid):
                        cfg = os.path.join(USERS_DATA_DIR, uid, "config")
                        return os.path.getmtime(cfg) if os.path.exists(cfg) else 0

                    current_user = max(users, key=get_user_timestamp)
                    env_vars["steamid3"] = current_user
                    decky_plugin.logger.info(f"Active Steam user: {current_user}")

                    shortcuts_path = os.path.join(USERS_DATA_DIR, current_user, "config", "shortcuts.vdf")
                    if not os.path.exists(shortcuts_path):
                        os.makedirs(os.path.dirname(shortcuts_path), exist_ok=True)
                        with open(shortcuts_path, "wb") as file:
                            file.write(vdf.binary_dumps({"shortcuts": {}}))
                        os.chmod(shortcuts_path, 0o755)
                        decky_plugin.logger.info(f"Created missing shortcuts.vdf at {shortcuts_path}")
                else:
                    env_vars["steamid3"] = None
                    decky_plugin.logger.warning("No Steam users found in userdata.")
            except Exception as e:
                decky_plugin.logger.error(f"Error reading Steam userdata: {e}")
                env_vars["steamid3"] = None

        env_vars["logged_in_home"] = DECKY_USER_HOME

    else:
        # Linux / other OS
        decky_plugin.logger.info("Running Linux/other OS logic")

        # Ensure the env_vars file exists
        if not os.path.exists(env_vars_path):
            decky_plugin.logger.warning(f"{env_vars_path} does not exist. Creating empty env vars file.")
            os.makedirs(os.path.dirname(env_vars_path), exist_ok=True)
            with open(env_vars_path, "w") as f:
                f.write("")  # create empty file
            # Return an empty dict (valid)
            env_vars["logged_in_home"] = DECKY_USER_HOME
            return env_vars

        # File exists (may be empty, may have values)
        with open(env_vars_path, "r") as f:
            lines = f.readlines()

        for line in lines:
            if line.startswith("export "):
                line = line[7:]
            if "=" in line:
                name, value = line.strip().split("=", 1)
                env_vars[name] = value

        with open(env_vars_path, "w") as f:
            for line in lines:
                if (
                    "chromelaunchoptions" not in line
                    and "websites_str" not in line
                ):
                    f.write(line)

        # Always include logged_in_home
        env_vars["logged_in_home"] = DECKY_USER_HOME

    return env_vars
