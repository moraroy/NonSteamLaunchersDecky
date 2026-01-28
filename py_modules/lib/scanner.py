#!/usr/bin/env python3
import os
import json
import re
import ssl
import certifi
import decky_plugin
from decky_plugin import DECKY_PLUGIN_DIR, DECKY_USER_HOME
import platform
import time
import urllib
import urllib.parse
import subprocess
import base64
from base64 import b64encode
import externals.requests as requests
import externals.vdf as vdf
from externals.steamgrid import SteamGridDB
from scanners.ea_scanner import ea_scanner
from scanners.epic_scanner import epic_games_scanner
from scanners.ubisoft_scanner import ubisoft_scanner
from scanners.gog_scanner import gog_scanner
from scanners.battle_net_scanner import battle_net_scanner
from scanners.amazon_scanner import amazon_scanner
from scanners.itchio_scanner import itchio_games_scanner
from scanners.legacy_scanner import legacy_games_scanner
from scanners.vkplay_scanner import vkplay_scanner
from scanners.hoyoplay_scanner import hoyoplay_scanner
from scanners.gamejolt_scanner import gamejolt_scanner
from scanners.minecraft_scanner import minecraft_scanner
from scanners.indie_scanner import indie_scanner
from scanners.humble_scanner import humble_scanner
from scanners.stove_scanner import stove_scanner
from scanners.geforcenow_scanner import geforcenow_scanner
from scanners.rpw_scanner import rpw_scanner
from scanners.chrome_scanner import chrome_scanner
from scanners.waydroid_scanner import waydroid_scanner
from scanners.flatpak_scanner import flatpak_scanner
from scanners.microsoftxbox_scanner import microsoftxbox_scanner





from scanners.game_tracker import load_master_list, track_game, finalize_game_tracking
from get_env_vars import refresh_env_vars
from umu_processor import modify_shortcut_for_umu
from concurrent.futures import ThreadPoolExecutor, as_completed

#Vars
proxy_url = 'https://nonsteamlaunchers.onrender.com/api'
decky_shortcuts = {}


launcher_icons = {
    "Epic Games": "5255885",
    "Amazon Games": "5255884",
    "GOG Galaxy": "34605",
    "Battle.net": "5248250",
    "EA App": "5306742",
    "itch.io": "5259585",
    "Legacy Games": "5438208",
    "Ubisoft Connect": "5270094",
    "VK Play": "5418177",
    "HoYoPlay": "5454020",
    "Game Jolt Client": "5299692",
    "Artix Game Launcher": "5264320",
    "Minecraft Launcher": "5302646",
    "Google Chrome": "37126",
    "IndieGala Client": "5317258",
    "Waydroid": "5441196",
    "GeForce Now": "5258450",
    "STOVE Client": "5443968",
    "Humble Bundle": "5333415",
    "NVIDIA GeForce Now": "5258450",
    "Microsoft Xbox": "5297303",
    "Big Fish Games Manager": "5461265",
}

# Initial environment variables refresh
env_vars = refresh_env_vars()


def initialiseVariables(env_vars):
    global steamid3, logged_in_home, compat_tool_name, controller_config_path
    global epic_games_launcher, ubisoft_connect_launcher, ea_app_launcher
    global gog_galaxy_launcher, bnet_launcher, amazon_launcher, itchio_launcher
    global legacy_launcher, vkplay_launcher, hoyoplay_launcher, gamejolt_launcher
    global humble_launcher, stove_launcher, geforcenow_launcher, microsoftxbox_launcher, bigfish_launcher
    global minecraft_launcher, indie_launcher, epicshortcutdirectory, gogshortcutdirectory, uplayshortcutdirectory
    global battlenetshortcutdirectory, eaappshortcutdirectory, amazonshortcutdirectory
    global itchioshortcutdirectory, legacyshortcutdirectory, humbleshortcutdirectory
    global indieshortcutdirectory, rockstarshortcutdirectory, glyphshortcutdirectory
    global minecraftshortcutdirectory, psplusshortcutdirectory, vkplayshortcutdirectory
    global hoyoplayshortcutdirectory, gamejoltshortcutdirectory, artixgameshortcutdirectory
    global arcshortcutdirectory, poketcgshortcutdirectory, antstreamshortcutdirectory
    global vfunshortcutdirectory, temposhortcutdirectory, repaireaappshortcutdirectory, chromedirectory
    global stoveshortcutdirectory, bigfishshortcutdirectory
    global microsoftxbox_launcher

    
    steamid3 = env_vars.get('steamid3')
    logged_in_home = env_vars.get('logged_in_home')
    compat_tool_name = env_vars.get('compat_tool_name')
    controller_config_path = env_vars.get('controller_config_path')

    #scanner Variables
    epic_games_launcher = env_vars.get('epic_games_launcher', '')
    ubisoft_connect_launcher = env_vars.get('ubisoft_connect_launcher', '')
    ea_app_launcher = env_vars.get('ea_app_launcher', '')
    gog_galaxy_launcher = env_vars.get('gog_galaxy_launcher', '')
    bnet_launcher = env_vars.get('bnet_launcher', '')
    amazon_launcher = env_vars.get('amazon_launcher', '')
    itchio_launcher = env_vars.get('itchio_launcher', '')
    legacy_launcher = env_vars.get('legacy_launcher', '')
    vkplay_launcher = env_vars.get('vkplay_launcher', '')
    hoyoplay_launcher = env_vars.get('hoyoplay_launcher', '')
    gamejolt_launcher = env_vars.get('gamejolt_launcher', '')
    minecraft_launcher = env_vars.get('minecraft_launcher', '')
    indie_launcher = env_vars.get('indie_launcher', '')
    humble_launcher = env_vars.get('humble_launcher', '')
    stove_launcher = env_vars.get('stove_launcher', '')
    bigfish_launcher = env_vars.get('bigfish_launcher', '')

    microsoftxbox_launcher = env_vars.get('microsoftxbox_launcher', '')

    epicshortcutdirectory = env_vars.get('epicshortcutdirectory')
    gogshortcutdirectory = env_vars.get('gogshortcutdirectory')
    uplayshortcutdirectory = env_vars.get('uplayshortcutdirectory')
    battlenetshortcutdirectory = env_vars.get('battlenetshortcutdirectory')
    eaappshortcutdirectory = env_vars.get('eaappshortcutdirectory')
    amazonshortcutdirectory = env_vars.get('amazonshortcutdirectory')
    itchioshortcutdirectory = env_vars.get('itchioshortcutdirectory')
    legacyshortcutdirectory = env_vars.get('legacyshortcutdirectory')
    humbleshortcutdirectory = env_vars.get('humbleshortcutdirectory')
    indieshortcutdirectory = env_vars.get('indieshortcutdirectory')
    rockstarshortcutdirectory = env_vars.get('rockstarshortcutdirectory')
    glyphshortcutdirectory = env_vars.get('glyphshortcutdirectory')
    minecraftshortcutdirectory = env_vars.get('minecraftshortcutdirectory')
    psplusshortcutdirectory = env_vars.get('psplusshortcutdirectory')
    vkplayshortcutdirectory = env_vars.get('vkplayshortcutdirectory')
    hoyoplayshortcutdirectory = env_vars.get('hoyoplayshortcutdirectory')
    gamejoltshortcutdirectory = env_vars.get('gamejoltshortcutdirectory')
    artixgameshortcutdirectory = env_vars.get('artixgameshortcutdirectory')
    arcshortcutdirectory = env_vars.get('arcshortcutdirectory')
    poketcgshortcutdirectory = env_vars.get('poketcgshortcutdirectory')
    antstreamshortcutdirectory = env_vars.get('antstreamshortcutdirectory')
    vfunshortcutdirectory = env_vars.get('vfunshortcutdirectory')
    temposhortcutdirectory = env_vars.get('temposhortcutdirectory')
    stoveshortcutdirectory = env_vars.get('stoveshortcutdirectory')
    bigfishshortcutdirectory = env_vars.get('bigfishshortcutdirectory')
    repaireaappshortcutdirectory = env_vars.get('repaireaappshortcutdirectory')
    chromedirectory = env_vars.get('chromedirectory')
    geforcenow_launcher = "com.nvidia.geforcenow"




# Scanner function with threading
def scan():
    load_master_list()
    from scanners.game_tracker import clear_current_scan
    clear_current_scan()


    global decky_shortcuts, env_vars
    decky_shortcuts = {}

    # Refresh env_vars once at the start
    env_vars = refresh_env_vars()
    if env_vars is not None:
        initialiseVariables(env_vars)
        add_launchers()

        # List all scanners with parameters for threading
        scanners = [
            (epic_games_scanner, logged_in_home, epic_games_launcher, create_new_entry),
            (ubisoft_scanner, logged_in_home, ubisoft_connect_launcher, create_new_entry),
            (ea_scanner, logged_in_home, ea_app_launcher, create_new_entry),
            (gog_scanner, logged_in_home, gog_galaxy_launcher, create_new_entry),
            (battle_net_scanner, logged_in_home, bnet_launcher, create_new_entry),
            (amazon_scanner, logged_in_home, amazon_launcher, create_new_entry),
            (itchio_games_scanner, logged_in_home, itchio_launcher, create_new_entry),
            (legacy_games_scanner, logged_in_home, legacy_launcher, create_new_entry),
            (vkplay_scanner, logged_in_home, vkplay_launcher, create_new_entry),
            (hoyoplay_scanner, logged_in_home, hoyoplay_launcher, create_new_entry),
            (gamejolt_scanner, logged_in_home, gamejolt_launcher, create_new_entry),
            (minecraft_scanner, logged_in_home, minecraft_launcher, create_new_entry),
            (indie_scanner, logged_in_home, indie_launcher, create_new_entry),
            (humble_scanner, logged_in_home, humble_launcher, create_new_entry),
            (stove_scanner, logged_in_home, stove_launcher, create_new_entry),    
            (rpw_scanner, logged_in_home, create_new_entry),
            (chrome_scanner, logged_in_home, create_new_entry),
            (waydroid_scanner, logged_in_home, create_new_entry),
            (flatpak_scanner, logged_in_home, create_new_entry),
            (geforcenow_scanner, logged_in_home, geforcenow_launcher, create_new_entry),
            (microsoftxbox_scanner, logged_in_home, microsoftxbox_launcher, create_new_entry)
        ]

        # Use ThreadPoolExecutor to limit to 2 threads
        with ThreadPoolExecutor(max_workers=2) as executor:
            future_to_scanner = {executor.submit(scanner[0], *scanner[1:]): scanner[0] for scanner in scanners}

            for future in as_completed(future_to_scanner):
                scanner_func = future_to_scanner[future]
                try:
                    future.result()  # Block until the result is ready
                except Exception as e:
                    decky_plugin.logger.error(f"Error in {scanner_func.__name__}: {e}")


        removed_apps = finalize_game_tracking()



    return decky_shortcuts, removed_apps


def addCustomSite(customSiteJSON, selectedBrowser):
    global decky_shortcuts
    decky_shortcuts = {}
    new_shortcuts = []

    for site in customSiteJSON:
        customSiteName = site['siteName']
        customSiteURL = site['siteURL'].strip()
        browser_lower = site.get("browser", selectedBrowser).lower()
        browser_name = site.get("browser", selectedBrowser)

        cleanSiteURL = customSiteURL.replace('http://', '').replace('https://', '').replace('www.', '')

        if "chrome" in browser_lower:
            launch_options = (
                f'run --branch=stable --arch=x86_64 --command=/app/bin/chrome '
                f'--file-forwarding com.google.Chrome @@u @@ '
                f'--window-size=1280,800 --force-device-scale-factor=1.00 '
                f'--device-scale-factor=1.00 --start-fullscreen '
                f'https://{cleanSiteURL} --no-first-run --enable-features=OverlayScrollbar'
            )
        elif "edge" in browser_lower:
            launch_options = (
                f'run --arch=x86_64 com.microsoft.Edge --window-size=1280,800 '
                f'--force-device-scale-factor=1.00 --device-scale-factor=1.00 --start-fullscreen '
                f'https://{cleanSiteURL} --no-first-run'
            )
        elif "firefox" in browser_lower:
            launch_options = (
                f'run --branch=stable --arch=x86_64 org.mozilla.firefox --kiosk https://{cleanSiteURL}'
            )
        elif "brave" in browser_lower:
            launch_options = (
                f'run --arch=x86_64 com.brave.Browser --start-fullscreen --window-size=1280,800 '
                f'--force-device-scale-factor=1.00 --no-first-run --no-default-browser-check '
                f'--enable-features=OverlayScrollbar,HardwareMediaKeyHandling '
                f'https://{cleanSiteURL}'
            )
        elif "vivaldi" in browser_lower:
            launch_options = (
                f'run --branch=stable --arch=x86_64 '
                f'--command=vivaldi com.vivaldi.Vivaldi '
                f'--window-size=1280,800 --start-fullscreen '
                f'--force-device-scale-factor=1.00 '
                f'https://{cleanSiteURL} --no-first-run'
            )
        elif "librewolf" in browser_lower:
            launch_options = (
                f'run --branch=stable --arch=x86_64 '
                f'io.gitlab.librewolf-community '
                f'--kiosk https://{cleanSiteURL}'
            )
        else:
            launch_options = f'run https://{cleanSiteURL}'

        new_shortcuts.append({
            'name': customSiteName,
            'url': cleanSiteURL,
            'options': launch_options,
            'browser': browser_name
        })

    env_vars = refresh_env_vars()
    initialiseVariables(env_vars)

    for site in new_shortcuts:
        create_new_entry(
            env_vars.get('chromedirectory'),
            site['name'],
            site['options'],
            env_vars.get('chrome_startdir'),
            site['browser']
        )

    return decky_shortcuts





def check_if_shortcut_exists(display_name, exe_path, start_dir, launch_options):

    # Determine the path based on the operating system
    if platform.system() == "Windows":
        vdf_path = f"C:\\Program Files (x86)\\Steam\\userdata\\{steamid3}\\config\\shortcuts.vdf"
    else:
        vdf_path = f"{logged_in_home}/.steam/root/userdata/{steamid3}/config/shortcuts.vdf"

    # Check if the shortcuts file exists
    if os.path.exists(vdf_path):

        # If the file is not executable, write the shortcuts dictionary and make it executable
        if not os.access(vdf_path, os.X_OK):
            decky_plugin.logger.info(f"VDF file is not executable, initializing: {vdf_path}")
            with open(vdf_path, 'wb') as file:
                vdf.binary_dumps({'shortcuts': {}}, file)
            os.chmod(vdf_path, 0o755)
        else:
            # If the file exists, try to load it
            try:
                with open(vdf_path, 'rb') as file:
                    shortcuts = vdf.binary_loads(file.read())

                for s in shortcuts['shortcuts'].values():
                    stripped_exe_path = exe_path.strip('\"') if exe_path else exe_path
                    stripped_start_dir = start_dir.strip('\"') if start_dir else start_dir


                    # Non-Chrome shortcut check: We remove the launch options comparison for non-Chrome shortcuts
                    if (s.get('appname') == display_name or s.get('AppName') == display_name) and \
                       (s.get('exe') and s.get('exe').strip('\"') == stripped_exe_path or s.get('Exe') and s.get('Exe').strip('\"') == stripped_exe_path) and \
                       s.get('StartDir') and s.get('StartDir').strip('\"') == stripped_start_dir:

                        # Check if the launch options are different (for non-Chrome, no comparison is done, so add a warning here)
                        if s.get('LaunchOptions') != launch_options:
                            decky_plugin.logger.warning(f"Launch options for {display_name} differ from the default. This could be due to the user manually modifying the launch options. Will skip creation")

                        decky_plugin.logger.info(f"Existing shortcut found for game {display_name}. Skipping creation.")
                        return True

                    if (s.get('appname') == display_name or s.get('AppName') == display_name) and \
                       (s.get('exe') and s.get('exe').strip('\"') == '/app/bin/chrome') and \
                       s.get('LaunchOptions') and launch_options in s.get('LaunchOptions'):
                        decky_plugin.logger.info(f"Existing website shortcut found for {display_name}. Skipping creation.")
                        return True

            except Exception as e:
                decky_plugin.logger.error(f"Error reading shortcuts file: {e}")
    else:
        decky_plugin.logger.info(f"VDF file not found at: {vdf_path}")

    return False



# Add or update the proton compatibility settings
def add_compat_tool(launchoptions):
    steam_compat_marker = 'STEAM_COMPAT_DATA_PATH'

    if 'chrome' in launchoptions or 'edge' in launchoptions or 'firefox' in launchoptions or 'brave' in launchoptions or 'vivaldi' in launchoptions or 'librewolf' in launchoptions or '--appid 0' in launchoptions:
        return False
    elif any(x in launchoptions for x in ['jp.', 'com.', 'online.']):
        if steam_compat_marker not in launchoptions:
            return False
    return compat_tool_name





#Manifest File Logic
steam_applist_cache = None

def get_steam_store_appid(steam_store_game_name):
    search_url = f"{proxy_url}/search/{steam_store_game_name}"
    try:
        response = requests.get(search_url, timeout=10)
        response.raise_for_status()
        data = response.json()
        if 'data' in data and data['data']:
            steam_store_appid = data['data'][0].get('steam_store_appid')
            if steam_store_appid:
                decky_plugin.logger.info(
                    f"Found App ID for {steam_store_game_name} via primary source: {steam_store_appid}"
                )
                return steam_store_appid
    except requests.exceptions.RequestException as e:
        decky_plugin.logger.warning(
            f"Primary store App ID lookup failed for {steam_store_game_name}: {e}"
        )

    def normalize_name(name):
        name = name.lower()
        name = re.sub(r'[®™]', '', name)
        name = ' '.join(name.split())
        return name

    global steam_applist_cache
    if steam_applist_cache is None:
        steam_applist_cache = {}

    if steam_store_game_name not in steam_applist_cache:
        time.sleep(0.5)  # Small delay to avoid spamming Steam
        query = urllib.parse.quote(steam_store_game_name)
        url = f"https://store.steampowered.com/api/storesearch/?term={query}&l=english&cc=US"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.RequestException as e:
            decky_plugin.logger.error(
                f"Fallback Steam lookup failed for {steam_store_game_name}: {e}"
            )
            return None

        target = normalize_name(steam_store_game_name)
        fallback_appid = None
        for item in data.get("items", []):
            if normalize_name(item.get("name", "")) == target:
                fallback_appid = str(item.get("id"))
                break

        steam_applist_cache[steam_store_game_name] = fallback_appid

    if steam_applist_cache[steam_store_game_name]:
        decky_plugin.logger.info(
            f"Found App ID for {steam_store_game_name} via fallback Steam search API: {steam_applist_cache[steam_store_game_name]}"
        )
        return steam_applist_cache[steam_store_game_name]

    decky_plugin.logger.warning(
        f"No App ID found for {steam_store_game_name} in fallback Steam search API."
    )
    return None






def create_steam_store_app_manifest_file(steam_store_appid, steam_store_game_name):
    if not steam_store_appid:
        decky_plugin.logger.error(f"Cannot create manifest for '{steam_store_game_name}': no AppID found.")
        return

    steamapps_dir = os.path.join(logged_in_home, ".steam/root/steamapps/")
    appmanifest_path = os.path.join(steamapps_dir, f"appmanifest_{steam_store_appid}.acf")

    os.makedirs(steamapps_dir, exist_ok=True)

    if os.path.exists(appmanifest_path):
        decky_plugin.logger.info(f"Manifest file for AppID {steam_store_appid} already exists at {appmanifest_path}.")
        return

    vdf_content = "\n".join([
        '"AppState"',
        "{",
        f'\t"appid"\t\t"{steam_store_appid}"',
        '\t"Universe"\t\t"1"',
        f'\t"name"\t\t"{steam_store_game_name}"',
        '\t"StateFlags"\t\t"1"',
        "}",
        ""
    ])

    try:
        with open(appmanifest_path, "w", encoding="utf-8") as file:
            file.write(vdf_content)
        decky_plugin.logger.info(f"Created appmanifest file at: {appmanifest_path}")
    except Exception as e:
        decky_plugin.logger.error(f"Failed to write manifest for '{steam_store_game_name}': {e}")

#End of manifest file logic





# Boot video files
def get_movies(game_name):
    # Dynamically build the list of app names to exclude from API requests
    excluded_apps = []
    try:
        with open(f"{DECKY_PLUGIN_DIR}/src/hooks/siteList.ts", 'r', encoding='utf-8') as f:
            content = f.read()
            excluded_apps = re.findall(r"label:\s*'([^']+)'", content)
    except Exception as e:
        decky_plugin.logger.error(f"Failed to read siteList.ts for excluded apps: {e}")
        excluded_apps = []

    OVERRIDE_PATH = os.path.expanduser(f'{DECKY_USER_HOME}/.steam/root/config/uioverrides/movies')
    REQUEST_RETRIES = 5

    def sanitize_filename(filename):
        return re.sub(r'[<>:"/\\|?*]', '_', filename)

    def download_video(video, target_dir):
        """Download video if it does not already exist."""
        sanitized_name = sanitize_filename(video['name'])
        file_path = os.path.join(target_dir, f"{sanitized_name}.webm")

        if os.path.exists(file_path):
            decky_plugin.logger.info(f"Skipping {file_path}, already exists.")
            return

        os.makedirs(target_dir, exist_ok=True)

        download_url = video.get('download_url')
        if download_url:
            try:
                response = requests.get(download_url)
                if response.status_code == 200:
                    with open(file_path, 'wb') as f:
                        f.write(response.content)
                    decky_plugin.logger.info(f"Downloaded {file_path}")
                else:
                    decky_plugin.logger.error(f"Failed to download {file_path}, status code: {response.status_code}")
            except requests.exceptions.RequestException as e:
                decky_plugin.logger.error(f"Download failed for {file_path}: {e}")
        else:
            decky_plugin.logger.info("No download URL found for video.")

    #decky_plugin.logger.info(f"🎮 Fetching boot video for: {game_name}")
    try:
        # Check if the game_name is in the excluded list and skip if so
        if game_name.lower() in [app.lower() for app in excluded_apps]:
            #decky_plugin.logger.info(f"Skipping boot video for {game_name}, as it's in the excluded apps list.")
            return  # Skip downloading this video

        for _ in range(REQUEST_RETRIES):
            try:
                response = requests.get('https://steamdeckrepo.com/api/posts/all', verify=certifi.where())
                if response.status_code == 200:
                    data = response.json().get('posts', [])
                    break
                elif response.status_code == 429:
                    raise Exception('Rate limit exceeded, try again in a minute')
                else:
                    decky_plugin.logger.error(f'steamdeckrepo fetch failed, status={response.status_code}')
            except requests.exceptions.RequestException as e:
                decky_plugin.logger.error(f"Request failed: {e}")
        else:
            raise Exception(f'Retry attempts exceeded')

        # Use the game_name directly instead of splitting it into words
        search_terms = [game_name.lower()]

        # Attempt to find a matching boot video for the full game name
        for term in search_terms:
            filtered_videos = sorted(
                (
                    {
                        'id': entry['id'],
                        'name': entry['title'],
                        'preview_video': entry['video'],
                        'download_url': f'https://steamdeckrepo.com/post/download/{entry["id"]}',
                        'target': 'boot',
                        'likes': entry['likes'],
                    }
                    for entry in data
                    if term in entry['title'].lower() and
                    entry['type'] == 'boot_video'
                ),
                key=lambda x: x['likes'], reverse=True
            )

            if filtered_videos:
                video = filtered_videos[0]
                decky_plugin.logger.info(f"🎬 Downloading boot video: {video['name']}")
                download_video(video, OVERRIDE_PATH)
                return  # Exit after downloading the first matching video

        # If no video was found, check if the game_name has more than one word and use the first two words
        if len(game_name.split()) > 1:
            first_two_words = ' '.join(game_name.split()[:2]).lower()
            decky_plugin.logger.info(f"🔍 No video found for full game name. Trying first two words: {first_two_words}")

            filtered_videos = sorted(
                (
                    {
                        'id': entry['id'],
                        'name': entry['title'],
                        'preview_video': entry['video'],
                        'download_url': f'https://steamdeckrepo.com/post/download/{entry["id"]}',
                        'target': 'boot',
                        'likes': entry['likes'],
                    }
                    for entry in data
                    if first_two_words in entry['title'].lower() and
                    entry['type'] == 'boot_video'
                ),
                key=lambda x: x['likes'], reverse=True
            )

            if filtered_videos:
                video = filtered_videos[0]
                decky_plugin.logger.info(f"🎬 Downloading boot video using first two words: {video['name']}")
                download_video(video, OVERRIDE_PATH)
                return  # Exit after downloading the first matching video

        # If no video was found at all
        decky_plugin.logger.info(f"No top boot video found for {game_name}.")

    except Exception as e:
        decky_plugin.logger.error(f"Failed to fetch steamdeckrepo: {e}")


#End of Boot Videos





#Fallback Artwork
def get_steam_fallback_artwork(steam_store_appid, art_type):
    # Map logical art types to possible Steam CDN files
    art_type_map = {
        "icon": ["icon.png", "icon.ico"],
        "logo": ["logo_2x.png", "logo.png"],
        "hero": ["library_hero_2x.jpg", "library_hero.jpg"],
        "grid": ["library_600x900_2x.jpg", "library_600x900.jpg"],
        "widegrid": ["header_2x.jpg", "header.jpg"],
    }

    file_candidates = art_type_map.get(art_type)
    if not file_candidates:
        decky_plugin.logger.warning(f"No file candidates found for art type '{art_type}'")
        return None

    base_url = f"https://shared.steamstatic.com/store_item_assets/steam/apps/{steam_store_appid}/"

    for file in file_candidates:
        url = base_url + file
        decky_plugin.logger.info(f"Trying to fetch {art_type} from {url}")
        try:
            response = requests.get(url, stream=True)
            if response.status_code == 200:
                decky_plugin.logger.info(f"Successfully fetched {art_type} from {url}")
                return b64encode(response.content).decode("utf-8")
            else:
                decky_plugin.logger.info(f"Received status {response.status_code} for {art_type} from {url}")
        except requests.RequestException as e:
            decky_plugin.logger.warning(f"Exception while fetching {art_type} from {url}: {e}")

    decky_plugin.logger.warning(f"All attempts to fetch {art_type} for app ID {steam_store_appid} failed.")
    return None
#End of fallback artwork





def get_local_tagged_artwork(appname, steamid3, logged_in_home):
    grid_dir = f"{logged_in_home}/.steam/root/userdata/{steamid3}/config/grid"
    artwork = {
        'Icon': None,
        'IconPath': None,
        'Logo': None,
        'Hero': None,
        'Grid': None,
        'WideGrid': None
    }

    decky_plugin.logger.info(f"Looking for local tagged artwork for '{appname}' in {grid_dir}")

    try:
        files = os.listdir(grid_dir)
    except FileNotFoundError:
        decky_plugin.logger.warning(f"Grid directory not found: {grid_dir}")
        return artwork
    except Exception as e:
        decky_plugin.logger.error(f"Error accessing grid directory {grid_dir}: {e}")
        return artwork

    for filename in files:
        file_path = os.path.join(grid_dir, filename)
        try:
            result = subprocess.run(
                ["getfattr", "-n", "user.xdg.tags", "--only-values", file_path],
                capture_output=True,
                text=True,
                check=False
            )
            if result.returncode != 0:
                continue

            tag = result.stdout.strip()
            if tag == appname:
                decky_plugin.logger.info(f"Found tagged file for {appname}: {file_path}")
                with open(file_path, 'rb') as f:
                    encoded = base64.b64encode(f.read()).decode('utf-8')
                if "-icon" in filename:
                    artwork['Icon'] = encoded
                    artwork['IconPath'] = file_path  # <- New addition
                elif "_logo" in filename:
                    artwork['Logo'] = encoded
                elif "_hero" in filename:
                    artwork['Hero'] = encoded
                elif "p." in filename:
                    artwork['Grid'] = encoded
                else:
                    artwork['WideGrid'] = encoded
        except Exception as e:
            decky_plugin.logger.error(f"Unexpected error processing {file_path}: {e}")

    return artwork



def create_new_entry(exe, appname, launchoptions, startingdir, launcher):
    global decky_shortcuts

    pathtoiconfile = None

    if not exe or not appname or not startingdir:
        decky_plugin.logger.info(f"Skipping creation for {appname}. Missing fields: exe={exe}, appname={appname}, startingdir={startingdir}")
        return


    if launchoptions is None:
        launchoptions = ''

    if check_if_shortcut_exists(appname, exe, startingdir, launchoptions):
        return

    umu = False
    if platform.system() != "Windows":
        exe, startingdir, launchoptions = modify_shortcut_for_umu(appname, exe, launchoptions, startingdir, logged_in_home, compat_tool_name)
        if '/bin/umu-run' in exe:
            umu = True
            if check_if_shortcut_exists(appname, exe, startingdir, launchoptions):
                return

    formatted_exe = f'"{exe}"' if platform.system() == "Windows" else exe
    formatted_start_dir = f'"{startingdir}"' if platform.system() == "Windows" else startingdir
    formatted_launch_options = launchoptions

    icon, logo64, hero64, gridp64, grid64, launcher_icon = None, None, None, None, None, None
    icon_path = None

    local_art = get_local_tagged_artwork(appname, steamid3, logged_in_home)
    if local_art:
        icon_path = local_art.get('IconPath')
        icon = local_art.get('Icon')
        logo64 = local_art.get('Logo')
        hero64 = local_art.get('Hero')
        gridp64 = local_art.get('Grid')
        grid64 = local_art.get('WideGrid')

    sgdb_icon_path = None

    if appname not in ["NonSteamLaunchers", "Repair EA App", "RemotePlayWhatever"]:
        game_id = get_game_id(appname)
        decky_plugin.logger.info(f"Game ID for {appname}: {game_id}")

        if game_id and game_id != "default_game_id":
            missing_any_art = any(x is None for x in [icon, logo64, hero64, gridp64, grid64])

            if missing_any_art:
                decky_plugin.logger.info(f"Some artwork missing, selectively fetching from SGDB for {appname}")

                sgdb_icon, sgdb_icon_path = download_artwork(game_id, "icons") if not icon else (None, None)
                sgdb_logo64 = download_artwork(game_id, "logos") if not logo64 else None
                sgdb_hero64 = download_artwork(game_id, "heroes") if not hero64 else None
                sgdb_gridp64 = download_artwork(game_id, "grids", "600x900") if not gridp64 else None
                sgdb_grid64 = download_artwork(game_id, "grids", "920x430") if not grid64 else None

                launcher_icon = None
                launcher_id = launcher_icons.get(launcher)
                if launcher_id:
                    launcher_icon, _ = download_artwork(launcher_id, "icons")

                icon = icon or sgdb_icon or launcher_icon
                logo64 = logo64 or sgdb_logo64
                hero64 = hero64 or sgdb_hero64
                gridp64 = gridp64 or sgdb_gridp64
                grid64 = grid64 or sgdb_grid64

            # Set icon path if not already done
            if not pathtoiconfile:
                if sgdb_icon_path:
                    pathtoiconfile = sgdb_icon_path
                    decky_plugin.logger.info(f"Icon file path set from SGDB download: {pathtoiconfile}")
                elif icon_path and os.path.exists(icon_path):
                    pathtoiconfile = icon_path
                    decky_plugin.logger.info(f"Icon file path set from local cache: {pathtoiconfile}")
        else:
            decky_plugin.logger.info(f"No valid game ID found for {appname}. Skipping artwork download.")

    steam_store_appid = get_steam_store_appid(appname)
    needs_fallback = any(x is None for x in [icon, logo64, hero64, gridp64, grid64])

    if steam_store_appid:
        decky_plugin.logger.info(f"Found Steam App ID for {appname}: {steam_store_appid}")
        create_steam_store_app_manifest_file(steam_store_appid, appname)

        if needs_fallback:
            decky_plugin.logger.info(f"Some artwork missing for {appname}. Checking fallback sources...")


            if not gridp64:
                gridp64 = get_steam_fallback_artwork(steam_store_appid, "grid")
            if not grid64:
                grid64 = get_steam_fallback_artwork(steam_store_appid, "widegrid")
            if not hero64:
                hero64 = get_steam_fallback_artwork(steam_store_appid, "hero")
            if not logo64:
                logo64 = get_steam_fallback_artwork(steam_store_appid, "logo")
            if not icon:
                icon = get_steam_fallback_artwork(steam_store_appid, "icon")
                if icon:
                    # Save fallback to file if needed
                    fallback_path = f"/tmp/{appname}_icon.ico"
                    with open(fallback_path, "wb") as f:
                        f.write(base64.b64decode(icon))
                    pathtoiconfile = fallback_path
                else:
                    decky_plugin.logger.warning(f"Fallback icon artwork for {appname} failed.")

    compatTool = None if platform.system() == "Windows" or umu else add_compat_tool(formatted_launch_options)

    decky_entry = {
        'appname': appname,
        'exe': formatted_exe,
        'StartDir': formatted_start_dir,
        'LaunchOptions': formatted_launch_options,
        'CompatTool': compatTool,
        'WideGrid': grid64,
        'Grid': gridp64,
        'Hero': hero64,
        'Logo': logo64,
        'Icon': pathtoiconfile,
        'Icon64': icon,
        'LauncherIcon': launcher_icon,
        'Launcher': launcher,
    }

    decky_shortcuts[appname] = decky_entry
    decky_plugin.logger.info(f"Added new entry for {appname} to shortcuts.")

    get_movies(appname)





def add_launchers():
    def try_add(shortcut_dir, name, launch_options, start_dir, override="NonSteamLaunchers"):
        if shortcut_dir:
            result = create_new_entry(shortcut_dir, name, launch_options, start_dir, override)
            track_game(name, "Launcher" if result else "Launcher")  # Track the game regardless of result
            return result
        return False

    launchers = [
        ('Epic Games', 'epicshortcutdirectory', 'epiclaunchoptions', 'epicstartingdir'),
        ('GOG Galaxy', 'gogshortcutdirectory', 'goglaunchoptions', 'gogstartingdir'),
        ('Ubisoft Connect', 'uplayshortcutdirectory', 'uplaylaunchoptions', 'uplaystartingdir'),
        ('Battle.net', 'battlenetshortcutdirectory', 'battlenetlaunchoptions', 'battlenetstartingdir'),
        ('EA App', 'eaappshortcutdirectory', 'eaapplaunchoptions', 'eaappstartingdir'),
        ('Amazon Games', 'amazonshortcutdirectory', 'amazonlaunchoptions', 'amazonstartingdir'),
        ('itch.io', 'itchioshortcutdirectory', 'itchiolaunchoptions', 'itchiostartingdir'),
        ('Legacy Games', 'legacyshortcutdirectory', 'legacylaunchoptions', 'legacystartingdir'),
        ('Humble Bundle', 'humbleshortcutdirectory', 'humblelaunchoptions', 'humblestartingdir'),
        ('IndieGala Client', 'indieshortcutdirectory', 'indielaunchoptions', 'indiestartingdir'),
        ('Rockstar Games Launcher', 'rockstarshortcutdirectory', 'rockstarlaunchoptions', 'rockstarstartingdir'),
        ('Glyph', 'glyphshortcutdirectory', 'glyphlaunchoptions', 'glyphstartingdir', 'Glyph'),
        ('Minecraft Launcher', 'minecraftshortcutdirectory', 'minecraftlaunchoptions', 'minecraftstartingdir'),
        ('Playstation Plus', 'psplusshortcutdirectory', 'pspluslaunchoptions', 'psplusstartingdir'),
        ('VK Play', 'vkplayshortcutdirectory', 'vkplaylaunchoptions', 'vkplaystartingdir'),
        ('HoYoPlay', 'hoyoplayshortcutdirectory', 'hoyoplaylaunchoptions', 'hoyoplaystartingdir'),
        ('Game Jolt Client', 'gamejoltshortcutdirectory', 'gamejoltlaunchoptions', 'gamejoltstartingdir'),
        ('Artix Game Launcher', 'artixgameshortcutdirectory', 'artixgamelaunchoptions', 'artixgamestartingdir'),
        ('ARC Launcher', 'arcshortcutdirectory', 'arclaunchoptions', 'arcstartingdir'),
        ('Pokémon Trading Card Game Live', 'poketcgshortcutdirectory', 'poketcglaunchoptions', 'poketcgstartingdir'),
        ('Antstream Arcade', 'antstreamshortcutdirectory', 'antstreamlaunchoptions', 'antstreamstartingdir'),
        ('VFUN Launcher', 'vfunshortcutdirectory', 'vfunlaunchoptions', 'vfunstartingdir'),
        ('Tempo Launcher', 'temposhortcutdirectory', 'tempolaunchoptions', 'tempostartingdir'),
        ('Repair EA App', 'repaireaappshortcutdirectory', 'repaireaapplaunchoptions', 'repaireaappstartingdir'),
        ('STOVE Client', 'stoveshortcutdirectory', 'stovelaunchoptions', 'stovestartingdir'),
        ('Big Fish Games Manager', 'bigfishshortcutdirectory', 'bigfishlaunchoptions', 'bigfishstartingdir'),


    ]

    for launcher in launchers:
        name = launcher[0]
        shortcut_dir = env_vars.get(launcher[1])
        launch_options = env_vars.get(launcher[2])
        start_dir = env_vars.get(launcher[3])
        override = launcher[4] if len(launcher) > 4 else "NonSteamLaunchers"  # Default to NonSteamLaunchers
        
        try_add(shortcut_dir, name, launch_options, start_dir, override)





def get_sgdb_art(game_id, launcher):
    decky_plugin.logger.info("Downloading icon artwork...")
    icon, icon_path = download_artwork(game_id, "icons")

    decky_plugin.logger.info("Downloading logo artwork...")
    logo64 = download_artwork(game_id, "logos")

    decky_plugin.logger.info("Downloading hero artwork...")
    hero64 = download_artwork(game_id, "heroes")

    decky_plugin.logger.info("Downloading grids artwork of size 600x900...")
    gridp64 = download_artwork(game_id, "grids", "600x900")

    decky_plugin.logger.info("Downloading grids artwork of size 920x430...")
    grid64 = download_artwork(game_id, "grids", "920x430")

    launcher_icon, _ = download_artwork(launcher_icons.get(launcher, ""), "icons")

    if not icon:
        icon = launcher_icon

    return icon, logo64, hero64, gridp64, grid64, launcher_icon


def download_artwork(game_id, art_type, dimensions=None):
    if not game_id:
        decky_plugin.logger.info(f"Skipping download for {art_type} artwork. Game ID is empty.")
        return (None, None) if art_type == "icons" else None

    decky_plugin.logger.info(f"Game ID: {game_id}")
    url = f"{proxy_url}/{art_type}/game/{game_id}"
    if dimensions:
        url += f"?dimensions={dimensions}"
    decky_plugin.logger.info(f"Sending request to: {url}")

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        decky_plugin.logger.info(f"Error making API call: {e}")
        return (None, None) if art_type == "icons" else None

    for artwork in data.get("data", []):
        if game_id == 5297303 and dimensions == "600x900":
            image_url = "https://cdn2.steamgriddb.com/thumb/eea5656d3244578f512f32cb4043792a.jpg"
        else:
            image_url = artwork['thumb']

        decky_plugin.logger.info(f"Downloading image from: {image_url}")
        try:
            response = requests.get(image_url, stream=True)
            response.raise_for_status()
            if response.status_code == 200:
                image_bytes = response.content

                if art_type == "icons":
                    output_dir = f"{logged_in_home}/.steam/root/userdata/{steamid3}/config/grid"
                    os.makedirs(output_dir, exist_ok=True)
                    output_path = os.path.join(output_dir, f"{game_id}_icon.ico")
                    try:
                        with open(output_path, "wb") as f:
                            f.write(image_bytes)
                        decky_plugin.logger.info(f"Icon saved to disk at: {output_path}")
                    except Exception as e:
                        decky_plugin.logger.warning(f"Failed to save icon to disk: {e}")
                        output_path = None

                    return b64encode(image_bytes).decode("utf-8"), output_path

                return b64encode(image_bytes).decode("utf-8")
        except requests.exceptions.RequestException as e:
            decky_plugin.logger.info(f"Error downloading image: {e}")
            if art_type == "icons":
                return download_artwork(game_id, "icons_ico", dimensions)

    return (None, None) if art_type == "icons" else None



def get_game_id(game_name):

    decky_plugin.logger.info(f"Searching for game ID for: {game_name}")

    retry_attempts = 1  # Retry only once
    for attempt in range(retry_attempts + 1):  # Try once initially, then retry if it fails
        try:
            url = f"{proxy_url}/search/{game_name}"
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            if data['data']:
                game_id = data['data'][0]['id']
                decky_plugin.logger.info(f"Found game ID: {game_id}")
                return game_id
            decky_plugin.logger.info("No game ID found")
            return "default_game_id"  # Return a default value when no games are found
        except requests.exceptions.RequestException as e:
            decky_plugin.logger.error(f"Error searching for game ID (attempt {attempt + 1}): {e}")
            if "502 Server Error: Bad Gateway" in str(e) and attempt < retry_attempts:
                # Retry after a short delay
                delay_time = 2  # 2 seconds delay for retry
                decky_plugin.logger.info(f"Retrying search for game ID after {delay_time}s...")
                time.sleep(delay_time)  # Retry after 2 seconds
            else:
                decky_plugin.logger.error(f"Error searching for game ID: {e}")
                return "default_game_id"  # Return default game ID if the error is not related to server issues

    # If all retry attempts fail, return the default game ID
    decky_plugin.logger.info("Max retry attempts reached. Returning default game ID.")
    return "default_game_id"