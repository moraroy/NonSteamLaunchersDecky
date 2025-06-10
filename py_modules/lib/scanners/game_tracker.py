import os
import sys
import json
from datetime import datetime
import subprocess
import time
import decky_plugin
from decky_plugin import DECKY_PLUGIN_DIR, DECKY_USER_HOME
import vdf
import re


def normalize_appname(name):
    if not name:
        return ""
    return name.strip().lower()


def get_steamid3(DECKY_USER_HOME, decky_plugin):
    paths = [
        f"{DECKY_USER_HOME}/.steam/root/config/loginusers.vdf",
        f"{DECKY_USER_HOME}/.local/share/Steam/config/loginusers.vdf"
    ]

    # Find the first existing loginusers.vdf file
    file_path = next((p for p in paths if os.path.isfile(p)), None)
    if not file_path:
        decky_plugin.logger.error("loginusers.vdf not found in expected locations.")
        return None

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Regex to find steamid blocks (steamID 17-digit followed by {...})
        users = re.findall(r'"(\d{17})"\s*{([^}]+)}', content, re.DOTALL)

        max_timestamp = 0
        current_steamid = None

        for steamid, block in users:
            account_match = re.search(r'"AccountName"\s+"([^"]+)"', block)
            timestamp_match = re.search(r'"Timestamp"\s+"(\d+)"', block)

            if account_match and timestamp_match:
                timestamp = int(timestamp_match.group(1))

                if timestamp > max_timestamp:
                    max_timestamp = timestamp
                    current_steamid = steamid

        if current_steamid:
            decky_plugin.logger.info(f"SteamID64 found: {current_steamid}")
            # Convert SteamID64 to SteamID3 (as int)
            steamid3 = int(current_steamid) - 76561197960265728
            userdata_path = f"{DECKY_USER_HOME}/.steam/root/userdata/{steamid3}"

            if os.path.isdir(userdata_path):
                decky_plugin.logger.info(f"Found userdata folder for SteamID3 {steamid3}: {userdata_path}")
            else:
                decky_plugin.logger.warning(f"Userdata folder does not exist for SteamID3 {steamid3}: {userdata_path}")

            return steamid3

        decky_plugin.logger.error("No valid SteamID found in loginusers.vdf.")
        return None

    except Exception as e:
        decky_plugin.logger.error(f"Failed to process SteamID: {e}")
        return None


def get_shortcuts_path():
    steamid3 = get_steamid3(DECKY_USER_HOME, decky_plugin)
    if steamid3 is None:
        decky_plugin.logger.error("steamid3 is not initialized yet!")
        return None
    return f"{DECKY_USER_HOME}/.steam/root/userdata/{steamid3}/config/shortcuts.vdf"


def get_installed_apps_path():
    return f"{DECKY_USER_HOME}/.config/systemd/user/installedapps.json"


_current_scan = {}
_master_list = {}
_previous_master_list = {}  # To track previous scan state


def clear_current_scan():
    _current_scan.clear()


def load_master_list():
    global _master_list, _previous_master_list
    installed_apps_path = get_installed_apps_path()

    if os.path.exists(installed_apps_path):
        try:
            with open(installed_apps_path, "r") as f:
                master_list_raw = json.load(f)
                if not isinstance(master_list_raw, dict):
                    raise ValueError("Master list JSON format is incorrect! Expected dictionary.")
                _master_list = master_list_raw
                _previous_master_list = json.loads(json.dumps(_master_list))  # Deep copy
        except Exception as e:
            decky_plugin.logger.error(f"Failed to load master list: {e}")
            _master_list = {}
            _previous_master_list = {}
    else:
        _master_list = {}
        _previous_master_list = {}



def track_game(appname, launcher):
    now = datetime.utcnow().isoformat() + "Z"

    if launcher not in _current_scan:
        _current_scan[launcher] = {}

    _current_scan[launcher][appname] = {  # Keeping original name as key
        "first_seen": _master_list.get(launcher, {}).get(appname, {}).get("first_seen", now),
        "last_seen": now,
        "still_installed": True
    }




def load_shortcuts_appid_map():
    shortcuts_path = get_shortcuts_path()
    if not shortcuts_path or not os.path.isfile(shortcuts_path):
        decky_plugin.logger.warning("shortcuts.vdf not found!")
        return {}

    try:
        with open(shortcuts_path, "rb") as f:
            data = vdf.binary_load(f)

        shortcuts = data.get("shortcuts", data)
        appid_map = {}

        for key, entry in shortcuts.items():
            appname = entry.get("AppName") or entry.get("appname")
            appid = entry.get("appid") or entry.get("AppID")
            if appname and appid:
                norm_name = normalize_appname(appname)
                appid_map[norm_name] = appid

        return appid_map

    except Exception as e:
        decky_plugin.logger.error(f"Failed to load shortcuts.vdf: {e}")
        return {}


def uninstall_removed_apps(removed_appnames, appid_map):
    for appname in removed_appnames:
        norm_name = normalize_appname(appname)
        appid = appid_map.get(norm_name)
        if appid:
            decky_plugin.logger.info(f"Attempting to uninstall '{appname}' with AppID {appid} ...")
            try:
                cmd = ["steam", f"steam://uninstall/{appid}"]
                subprocess.run(cmd, check=True)
                time.sleep(2)
                decky_plugin.logger.info(f"Uninstall command sent for '{appname}' using Steam client.")
            except subprocess.CalledProcessError as e:
                decky_plugin.logger.error(f"Failed to uninstall '{appname}' using Steam client: {e}")
                try:
                    cmd = ["steam", f"steam://uninstall/{appid}"]
                    subprocess.run(cmd, check=True)
                    time.sleep(2)
                    decky_plugin.logger.info(f"Uninstall command sent for '{appname}' using Steam URI handler.")
                except subprocess.CalledProcessError as e:
                    decky_plugin.logger.error(f"Failed to uninstall '{appname}' using Steam URI handler: {e}")
                    decky_plugin.logger.warning(f"Uninstallation failed for '{appname}' (AppID {appid}). Manual intervention may be required.")
        else:
            decky_plugin.logger.warning(f"AppID not found for removed app '{appname}'")

def finalize_game_tracking():
    now = datetime.utcnow().isoformat() + "Z"
    installed_apps_path = get_installed_apps_path()

    removed_apps = {}

    # Mark missing launchers as uninstalled
    for launcher in list(_master_list.keys()):
        if launcher not in _current_scan:
            removed_apps[launcher] = list(_master_list[launcher].keys())
            del _master_list[launcher]  # Remove the launcher entirely
        else:
            # Check missing games within the launcher
            for appname in list(_master_list[launcher].keys()):
                if appname not in _current_scan[launcher]:
                    was_installed_before = _previous_master_list.get(launcher, {}).get(appname, {}).get("still_installed", True)
                    if was_installed_before:
                        if launcher not in removed_apps:
                            removed_apps[launcher] = []
                        removed_apps[launcher].append(appname)

                    _master_list[launcher][appname]["still_installed"] = False
                    _master_list[launcher][appname]["last_seen"] = now

    # Merge updated scan data
    for launcher, games in _current_scan.items():
        if launcher not in _master_list:
            _master_list[launcher] = {}
        _master_list[launcher].update(games)

    # Save updated JSON
    os.makedirs(os.path.dirname(installed_apps_path), exist_ok=True)
    with open(installed_apps_path, "w") as f:
        json.dump(_master_list, f, indent=4)

    # Handle removed apps
    if removed_apps:
        decky_plugin.logger.info(f"Newly removed apps detected: {removed_apps}")
        appid_map = load_shortcuts_appid_map()
        for launcher, apps in removed_apps.items():
            uninstall_removed_apps(apps, appid_map)
    else:
        decky_plugin.logger.info("No newly removed apps detected.")


# Optional helper for debugging shortcut contents:
def debug_print_shortcuts():
    shortcuts_path = get_shortcuts_path()
    if not shortcuts_path or not os.path.isfile(shortcuts_path):
        decky_plugin.logger.warning("shortcuts.vdf not found!")
        return

    with open(shortcuts_path, "rb") as f:
        data = vdf.binary_load(f)

    shortcuts = data.get("shortcuts", data)
    for key, entry in shortcuts.items():
        appname = entry.get("AppName") or entry.get("appname") or "<No AppName>"
        appid = entry.get("appid") or entry.get("AppID") or "<No AppID>"
        decky_plugin.logger.info(f"Shortcut index: {key} | AppName: {appname} | AppID: {appid}")
