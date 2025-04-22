#!/usr/bin/env python3
import os
import json
import re
import decky_plugin
from decky_plugin import DECKY_PLUGIN_DIR, DECKY_USER_HOME
import platform
import time
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
from scanners.rpw_scanner import rpw_scanner
from scanners.chrome_scanner import chrome_scanner
from get_env_vars import refresh_env_vars
from umu_processor import modify_shortcut_for_umu


# Refresh environment variables
env_vars = refresh_env_vars()

def initialiseVariables(env_vars):
    # Variables from NonSteamLaunchers.sh
    global steamid3
    steamid3 = env_vars.get('steamid3')
    global logged_in_home
    logged_in_home = env_vars.get('logged_in_home')
    global compat_tool_name
    compat_tool_name = env_vars.get('compat_tool_name')
    global controller_config_path
    controller_config_path = env_vars.get('controller_config_path')

    #Scanner Variables
    global epic_games_launcher
    epic_games_launcher = env_vars.get('epic_games_launcher', '')
    global ubisoft_connect_launcher
    ubisoft_connect_launcher = env_vars.get('ubisoft_connect_launcher', '')
    global ea_app_launcher
    ea_app_launcher = env_vars.get('ea_app_launcher', '')
    global gog_galaxy_launcher
    gog_galaxy_launcher = env_vars.get('gog_galaxy_launcher', '')
    global bnet_launcher
    bnet_launcher = env_vars.get('bnet_launcher', '')
    global amazon_launcher
    amazon_launcher = env_vars.get('amazon_launcher', '')
    global itchio_launcher
    itchio_launcher = env_vars.get('itchio_launcher', '')
    global legacy_launcher
    legacy_launcher = env_vars.get('legacy_launcher', '')
    global vkplay_launcher
    vkplay_launcher = env_vars.get('vkplay_launcher', '')
    global hoyoplay_launcher
    hoyoplay_launcher = env_vars.get('hoyoplay_launcher', '')
    global gamejolt_launcher
    gamejolt_launcher = env_vars.get('gamejolt_launcher', '')
    global minecraft_launcher
    minecraft_launcher = env_vars.get('minecraft_launcher', '')

    #Variables of the Launchers
    # Define the path of the Launchers
    global epicshortcutdirectory
    epicshortcutdirectory = env_vars.get('epicshortcutdirectory')
    global gogshortcutdirectory
    gogshortcutdirectory = env_vars.get('gogshortcutdirectory')
    global uplayshortcutdirectory
    uplayshortcutdirectory = env_vars.get('uplayshortcutdirectory')
    global battlenetshortcutdirectory
    battlenetshortcutdirectory = env_vars.get('battlenetshortcutdirectory')
    global eaappshortcutdirectory
    eaappshortcutdirectory = env_vars.get('eaappshortcutdirectory')
    global amazonshortcutdirectory
    amazonshortcutdirectory = env_vars.get('amazonshortcutdirectory')
    global itchioshortcutdirectory
    itchioshortcutdirectory = env_vars.get('itchioshortcutdirectory')
    global legacyshortcutdirectory
    legacyshortcutdirectory = env_vars.get('legacyshortcutdirectory')
    global humbleshortcutdirectory
    humbleshortcutdirectory = env_vars.get('humbleshortcutdirectory')
    global indieshortcutdirectory
    indieshortcutdirectory = env_vars.get('indieshortcutdirectory')
    global rockstarshortcutdirectory
    rockstarshortcutdirectory = env_vars.get('rockstarshortcutdirectory')
    global glyphshortcutdirectory
    glyphshortcutdirectory = env_vars.get('glyphshortcutdirectory')
    global minecraftshortcutdirectory
    minecraftshortcutdirectory = env_vars.get('minecraftshortcutdirectory')
    global psplusshortcutdirectory
    psplusshortcutdirectory = env_vars.get('psplusshortcutdirectory')
    global vkplayshortcutdirectory
    vkplayshortcutdirectory = env_vars.get('vkplayshortcutdirectory')
    global hoyoplayshortcutdirectory
    hoyoplayshortcutdirectory = env_vars.get('hoyoplayshortcutdirectory')
    global gamejoltshortcutdirectory
    gamejoltshortcutdirectory = env_vars.get('gamejoltshortcutdirectory')
    global artixgameshortcutdirectory
    artixgameshortcutdirectory = env_vars.get('artixgameshortcutdirectory')
    global arcshortcutdirectory
    arcshortcutdirectory = env_vars.get('arcshortcutdirectory')
    global poketcgshortcutdirectory
    poketcgshortcutdirectory = env_vars.get('poketcgshortcutdirectory')
    global antstreamshortcutdirectory
    antstreamshortcutdirectory = env_vars.get('antstreamshortcutdirectory')
    global vfunshortcutdirectory
    vfunshortcutdirectory = env_vars.get('vfunshortcutdirectory')
    global temposhortcutdirectory
    temposhortcutdirectory = env_vars.get('temposhortcutdirectory')





    
    global repaireaappshortcutdirectory
    repaireaappshortcutdirectory = env_vars.get('repaireaappshortcutdirectory')
    #Streaming
    global chromedirectory
    chromedirectory = env_vars.get('chromedirectory')

#Vars
proxy_url = 'https://nonsteamlaunchers.onrender.com/api'
decky_shortcuts = {}

def scan():
    global decky_shortcuts
    global env_vars
    decky_shortcuts = {}

    # Refresh env_vars using the refresh_env_vars function
    env_vars = refresh_env_vars()
    if env_vars:
        initialiseVariables(env_vars)
        add_launchers()
        epic_games_scanner(logged_in_home, epic_games_launcher, create_new_entry)
        ubisoft_scanner(logged_in_home, ubisoft_connect_launcher, create_new_entry)
        ea_scanner(logged_in_home, ea_app_launcher, create_new_entry)
        gog_scanner(logged_in_home, gog_galaxy_launcher, create_new_entry)
        battle_net_scanner(logged_in_home, bnet_launcher, create_new_entry)
        amazon_scanner(logged_in_home, amazon_launcher, create_new_entry)
        itchio_games_scanner(logged_in_home, itchio_launcher, create_new_entry)
        legacy_games_scanner(logged_in_home, legacy_launcher, create_new_entry)
        vkplay_scanner(logged_in_home, vkplay_launcher, create_new_entry)
        hoyoplay_scanner(logged_in_home, hoyoplay_launcher, create_new_entry)
        gamejolt_scanner(logged_in_home, gamejolt_launcher, create_new_entry)
        minecraft_scanner(logged_in_home, minecraft_launcher, create_new_entry)
        rpw_scanner(logged_in_home, create_new_entry)

        # Call chrome_scanner to process the Chrome Bookmarks
        chrome_scanner(logged_in_home, create_new_entry)
        # After all scanners, write the shortcuts to the file
        write_shortcuts_to_file(decky_shortcuts, DECKY_USER_HOME, decky_plugin)

    return decky_shortcuts

def addCustomSite(customSiteJSON):
    global decky_shortcuts
    decky_shortcuts = {}

    # Always refresh env_vars before initializing
    env_vars = refresh_env_vars()
    initialiseVariables(env_vars)

    customSites = json.loads(customSiteJSON)
    decky_plugin.logger.info(customSites)
    refresh_env_vars()
    for site in customSites:
        customSiteName = site['siteName']
        customSiteURL = site['siteURL'].strip()
        cleanSiteURL = customSiteURL.replace('http://', '').replace('https://', '').replace('www.', '')
        chromelaunch_options = f'run --branch=stable --arch=x86_64 --command=/app/bin/chrome --file-forwarding com.google.Chrome @@u @@ --window-size=1280,800 --force-device-scale-factor=1.00 --device-scale-factor=1.00 --start-fullscreen https://{cleanSiteURL} --no-first-run --enable-features=OverlayScrollbar'
        create_new_entry(env_vars.get('chromedirectory'), customSiteName, chromelaunch_options, env_vars.get('chrome_startdir'), None)
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

                    if (s.get('appname') == display_name or s.get('AppName') == display_name) and \
                       (s.get('exe') and s.get('exe').strip('\"') == stripped_exe_path or s.get('Exe') and s.get('Exe').strip('\"') == stripped_exe_path) and \
                       s.get('StartDir') and s.get('StartDir').strip('\"') == stripped_start_dir and \
                       (s.get('LaunchOptions') == launch_options or (not s.get('LaunchOptions') and not launch_options)):
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
    if 'chrome' in launchoptions or '--appid 0' in launchoptions:
        return False
    else:
        return compat_tool_name




#shortcuts file
def write_shortcuts_to_file(decky_shortcuts, DECKY_USER_HOME, decky_plugin):
    # Define the path for the new file
    new_file_path = f'{DECKY_USER_HOME}/.config/systemd/user/shortcuts'

    # Define the extensions to skip
    skip_extensions = {'.exe', '.sh', '.bat', '.msi', '.app', '.apk', '.url', '.desktop'}

    # Initialize a set to store the unique app names
    existing_shortcuts = set()

    # Check if the shortcuts file exists
    if not os.path.exists(new_file_path):
        decky_plugin.logger.info(f"Shortcuts file not found: {new_file_path}. Creating file...")
        with open(new_file_path, 'w') as f:
            pass  # Create an empty file

    # Read the existing shortcuts from the file and add them to the set
    with open(new_file_path, 'r') as f:
        for line in f:
            existing_shortcuts.add(line.strip())  # Add existing shortcuts to the set

        # Iterate over all appnames and check for duplicates before adding
        new_shortcuts = []
        for appname in decky_shortcuts:
            # If appname doesn't end with a skip extension and is not already in existing_shortcuts, add it
            if appname and not any(appname.endswith(ext) for ext in skip_extensions) and appname not in existing_shortcuts:
                new_shortcuts.append(appname)  # Collect the new shortcuts to append
                existing_shortcuts.add(appname)  # Add to the existing shortcuts set to avoid future duplicates

        # Only append new shortcuts to the file
        if new_shortcuts:
            with open(new_file_path, 'a') as f:
                for name in new_shortcuts:
                    f.write(f"{name}\n")  # Write only the appname (raw)

            decky_plugin.logger.info(f"New shortcuts added to {new_file_path}.")
        else:
            decky_plugin.logger.info("No new shortcuts to add.")
#End of Shortcuts file



#Manifest File Logic
def get_steam_store_appid(steam_store_game_name):
    search_url = f"{proxy_url}/search/{steam_store_game_name}"
    try:
        response = requests.get(search_url)
        response.raise_for_status()
        data = response.json()
        if 'data' in data and data['data']:
            steam_store_appid = data['data'][0].get('steam_store_appid')
            if steam_store_appid:
                return steam_store_appid
        return None

    except requests.exceptions.RequestException as e:
        return None


def create_steam_store_app_manifest_file(steam_store_appid, steam_store_game_name):
    steamapps_dir = f"{logged_in_home}/.steam/root/steamapps/"
    appmanifest_path = os.path.join(steamapps_dir, f"appmanifest_{steam_store_appid}.acf")

    # Ensure the directory exists
    os.makedirs(steamapps_dir, exist_ok=True)

    # Check if the file already exists
    if os.path.exists(appmanifest_path):
        decky_plugin.logger.info(f"Manifest file for {steam_store_appid} already exists.")
        return

    # Prepare the appmanifest data
    app_manifest_data = {
        "AppState": {
            "AppID": str(steam_store_appid),
            "Universe": "1",
            "installdir": steam_store_game_name,
            "StateFlags": "0"
        }
    }

    # Write the manifest to the file
    with open(appmanifest_path, 'w') as file:
        json.dump(app_manifest_data, file, indent=2)

    decky_plugin.logger.info(f"Created appmanifest file at: {appmanifest_path}")
#End of manifest file logic



# Descriptions file logic
# Define the path for descriptions.json
descriptions_file_path = f"{DECKY_USER_HOME}/.config/systemd/user/descriptions.json"

# Function to create descriptions.json if it doesn't exist
def create_descriptions_file():
    if not os.path.exists(descriptions_file_path):
        try:
            # Create an empty list inside the JSON file if it doesn't exist
            with open(descriptions_file_path, 'w') as file:
                json.dump([], file, indent=4)
            decky_plugin.logger.info(f"{descriptions_file_path} created successfully with an empty list.")
        except IOError as e:
            decky_plugin.logger.error(f"Error creating {descriptions_file_path}: {e}")

# Function to load existing game data from descriptions.json
def load_game_data():
    create_descriptions_file()  # Ensure the file is created if it doesn't exist
    try:
        with open(descriptions_file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        decky_plugin.logger.info(f"File not found: {descriptions_file_path}, returning empty data.")
        return []
    except json.JSONDecodeError as e:
        decky_plugin.logger.error(f"Error decoding JSON: {e}, returning empty data.")
        return []

# Function to check if a game already exists in descriptions.json
def game_exists_in_data(existing_data, game_name):
    return any(game['game_name'] == game_name for game in existing_data)

# Function to fetch game details from the API
def get_game_details(game_name):
    url = f"https://nonsteamlaunchers.onrender.com/api/details/{game_name}"
    response = requests.get(url)

    if response.status_code == 200:
        return response.json()  # Return game details as a dictionary
    else:
        decky_plugin.logger.error(f"Error: Unable to retrieve data for {game_name}. Status code {response.status_code}")
        return None  # Return None when API fails to fetch game details

# Function to strip HTML tags from a string
def strip_html_tags(text):
    clean_text = re.sub(r'<[^>]*>', '', text)
    return clean_text

# Function to decode HTML entities like \u00a0 (non-breaking space) and \u2013 (en dash)
def decode_html_entities(text):
    text = text.replace("\u00a0", " ")
    text = text.replace("\u2013", "-")
    text = text.replace("\u2019", "'")
    return text

# Function to write game details to descriptions.json (only if it's not already present)
def write_game_details(existing_data, game_details):
    if not game_details:
        decky_plugin.logger.info("No game details to write.")
        return existing_data

    # Only process 'about_the_game' if it's not None
    if 'about_the_game' in game_details:
        if game_details['about_the_game'] is not None:
            game_details['about_the_game'] = strip_html_tags(game_details['about_the_game'])
            game_details['about_the_game'] = decode_html_entities(game_details['about_the_game'])
        else:
            # Explicitly set 'about_the_game' as None if it's missing (this will become null in JSON)
            game_details['about_the_game'] = None

    # Ensure that 'game_details' key does not exist before adding
    if 'game_details' in game_details:
        del game_details['game_details']  # Remove 'game_details' key

    # Check if the game details already exist in the data based on game_name
    game_exists = any(game['game_name'] == game_details['game_name'] for game in existing_data)

    if not game_exists:
        # Append new data if it doesn't already exist
        existing_data.append(game_details)
        decky_plugin.logger.info(f"Game details for {game_details['game_name']} added successfully.")
    else:
        decky_plugin.logger.info(f"Game details for {game_details['game_name']} already exist, skipping.")

    return existing_data

# Function to update descriptions.json for new games
def update_game_details(games_to_check):
    # Load the existing game data
    existing_data = load_game_data()

    # List of app names to exclude from API requests
    excluded_apps = [
        "Epic Games",
        "GOG Galaxy",
        "Ubisoft Connect",
        "Battle.net",
        "EA App",
        "Amazon Games",
        "itch.io",
        "Legacy Games",
        "Humble Bundle",
        "IndieGala Client",
        "Rockstar Games Launcher",
        "Glyph",
        "Minecraft Launcher",
        "Playstation Plus",
        "VK Play",
        "HoYoPlay",
        "Game Jolt Client",
        "Artix Game Launcher",
        "ARC Launcher",
        "Pokémon Trading Card Game Live",
        "Antstream Arcade",
        "VFUN Launcher",
        "Tempo Launcher",
        "Repair EA App"
    ]

    # Iterate through the list of games to check and update game details
    for game_name in games_to_check:
        # Skip the API call for excluded app names
        if game_name in excluded_apps:
            decky_plugin.logger.info(f"Skipping API call for {game_name} as it is in the exclusion list.")
            continue  # Skip this iteration and move to the next game

        # Check if the game already exists in the data
        existing_game = next((game for game in existing_data if game['game_name'] == game_name), None)

        # If game exists and 'about_the_game' is null, skip the API call
        if existing_game and existing_game.get('about_the_game') is None:
            decky_plugin.logger.warning(f"Skipping API call for {game_name} as 'about_the_game' is null.")
            continue  # Skip this iteration and move to the next game

        # If game details are missing, fetch details
        if not game_exists_in_data(existing_data, game_name):
            decky_plugin.logger.info(f"Fetching details for {game_name} as details were missing...")
            game_details = get_game_details(game_name)

            # Check if game details were fetched successfully
            if game_details:
                existing_data = write_game_details(existing_data, game_details)
            else:
                # If details could not be fetched, add a placeholder with null for 'about_the_game'
                existing_data = write_game_details(existing_data, {
                    "game_name": game_name,
                    "about_the_game": None  # Use None to ensure it's converted to null in JSON
                })
                decky_plugin.logger.warning(f"Inserted placeholder with null for {game_name} as no details were found.")

    # Only write back to descriptions.json if new data was added
    if existing_data != load_game_data():  # Check if data was changed
        with open(descriptions_file_path, 'w') as file:
            json.dump(existing_data, file, indent=4)
        decky_plugin.logger.info(f"Updated {descriptions_file_path} with new game details (if applicable).")
    else:
        decky_plugin.logger.info("No new game details to add. No changes made to descriptions.json.")
#End of Descriptions file logic




#Create a shortcut
def create_new_entry(exe, appname, launchoptions, startingdir, launcher):
    global decky_shortcuts
    # Check if the necessary fields are provided
    if not exe or not appname or not startingdir:
        decky_plugin.logger.info(f"Skipping creation for {appname}. Missing fields: exe={exe}, appname={appname}, startingdir={startingdir}")
        return

    update_game_details([appname])

    if launchoptions is None:
        launchoptions = ''

    if check_if_shortcut_exists(appname, exe, startingdir, launchoptions):
        return
    # Modify the shortcut for UMU if on Linux
    umu = False
    if platform.system() != "Windows":
        exe, startingdir, launchoptions = modify_shortcut_for_umu(appname, exe, launchoptions, startingdir, logged_in_home, compat_tool_name)
        # Check if the modified shortcut is a UMU shortcut
        if '/bin/umu-run' in exe:
            umu = True
            if check_if_shortcut_exists(appname, exe, startingdir, launchoptions):
                return

    # Format the executable path and start directory
    if platform.system() == "Windows":
        formatted_exe = f'"{exe}"'
        formatted_start_dir = f'"{startingdir}"'
    else:
        formatted_exe = exe
        formatted_start_dir = startingdir

    # Format the launch options
    formatted_launch_options = launchoptions

    # Initialize artwork variables
    icon, logo64, hero64, gridp64, grid64, launcher_icon = None, None, None, None, None, None

    # Skip artwork fetching for specific shortcuts
    if appname not in ["NonSteamLaunchers", "Repair EA App", "RemotePlayWhatever"]:
        # Get artwork
        game_id = get_game_id(appname)
        decky_plugin.logger.info(f"Game ID for {appname}: {game_id}")
        if game_id is not None and game_id != "default_game_id":
            icon, logo64, hero64, gridp64, grid64, launcher_icon = get_sgdb_art(game_id, launcher)
        else:
            decky_plugin.logger.info(f"No valid game ID found for {appname}. Skipping artwork download.")

    steam_store_appid = get_steam_store_appid(appname)
    if steam_store_appid:
        decky_plugin.logger.info(f"Found Steam App ID for {appname}: {steam_store_appid}")
        create_steam_store_app_manifest_file(steam_store_appid, appname)

    # Create a new entry for the Steam shortcut
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
        'Icon': icon,  # Use the game icon if available
        'LauncherIcon': launcher_icon,  # Add launcher icon
        'Launcher': launcher,  # Add launcher information
    }
    decky_shortcuts[appname] = decky_entry
    decky_plugin.logger.info(f"Added new entry for {appname} to shortcuts.")




def add_launchers():
    create_new_entry(env_vars.get('epicshortcutdirectory'), 'Epic Games', env_vars.get('epiclaunchoptions'), env_vars.get('epicstartingdir'), None)
    create_new_entry(env_vars.get('gogshortcutdirectory'), 'GOG Galaxy', env_vars.get('goglaunchoptions'), env_vars.get('gogstartingdir'), None)
    create_new_entry(env_vars.get('uplayshortcutdirectory'), 'Ubisoft Connect', env_vars.get('uplaylaunchoptions'), env_vars.get('uplaystartingdir'), None)
    create_new_entry(env_vars.get('battlenetshortcutdirectory'), 'Battle.net', env_vars.get('battlenetlaunchoptions'), env_vars.get('battlenetstartingdir'), None)
    create_new_entry(env_vars.get('eaappshortcutdirectory'), 'EA App', env_vars.get('eaapplaunchoptions'), env_vars.get('eaappstartingdir'), None)
    create_new_entry(env_vars.get('amazonshortcutdirectory'), 'Amazon Games', env_vars.get('amazonlaunchoptions'), env_vars.get('amazonstartingdir'), None)
    create_new_entry(env_vars.get('itchioshortcutdirectory'), 'itch.io', env_vars.get('itchiolaunchoptions'), env_vars.get('itchiostartingdir'), None)
    create_new_entry(env_vars.get('legacyshortcutdirectory'), 'Legacy Games', env_vars.get('legacylaunchoptions'), env_vars.get('legacystartingdir'), None)
    create_new_entry(env_vars.get('humbleshortcutdirectory'), 'Humble Bundle', env_vars.get('humblelaunchoptions'), env_vars.get('humblestartingdir'), None)
    create_new_entry(env_vars.get('indieshortcutdirectory'), 'IndieGala Client', env_vars.get('indielaunchoptions'), env_vars.get('indiestartingdir'), None)
    create_new_entry(env_vars.get('rockstarshortcutdirectory'), 'Rockstar Games Launcher', env_vars.get('rockstarlaunchoptions'), env_vars.get('rockstarstartingdir'), None)
    create_new_entry(env_vars.get('glyphshortcutdirectory'), 'Glyph', env_vars.get('glyphlaunchoptions'), env_vars.get('glyphstartingdir'), "Glyph")
    create_new_entry(env_vars.get('minecraftshortcutdirectory'), 'Minecraft Launcher', env_vars.get('minecraftlaunchoptions'), env_vars.get('minecraftstartingdir'), None)
    create_new_entry(env_vars.get('psplusshortcutdirectory'), 'Playstation Plus', env_vars.get('pspluslaunchoptions'), env_vars.get('psplusstartingdir'), None)
    create_new_entry(env_vars.get('vkplayshortcutdirectory'), 'VK Play', env_vars.get('vkplaylaunchoptions'), env_vars.get('vkplaystartingdir'), None)
    create_new_entry(env_vars.get('hoyoplayshortcutdirectory'), 'HoYoPlay', env_vars.get('hoyoplaylaunchoptions'), env_vars.get('hoyoplaystartingdir'), None)
    create_new_entry(env_vars.get('gamejoltshortcutdirectory'), 'Game Jolt Client', env_vars.get('gamejoltlaunchoptions'), env_vars.get('gamejoltstartingdir'), None)
    create_new_entry(env_vars.get('artixgameshortcutdirectory'), 'Artix Game Launcher', env_vars.get('artixgamelaunchoptions'), env_vars.get('artixgamestartingdir'), None)
    create_new_entry(env_vars.get('arcshortcutdirectory'), 'ARC Launcher', env_vars.get('arclaunchoptions'), env_vars.get('arcstartingdir'), None)
    create_new_entry(env_vars.get('poketcgshortcutdirectory'), 'Pokémon Trading Card Game Live', env_vars.get('poketcglaunchoptions'), env_vars.get('poketcgstartingdir'), None)
    create_new_entry(env_vars.get('antstreamshortcutdirectory'), 'Antstream Arcade', env_vars.get('antstreamlaunchoptions'), env_vars.get('antstreamstartingdir'), None)
    create_new_entry(env_vars.get('vfunshortcutdirectory'), 'VFUN Launcher', env_vars.get('vfunlaunchoptions'), env_vars.get('vfunstartingdir'), None)
    create_new_entry(env_vars.get('temposhortcutdirectory'), 'Tempo Launcher', env_vars.get('tempolaunchoptions'), env_vars.get('tempostartingdir'), None)
    create_new_entry(env_vars.get('repaireaappshortcutdirectory'), 'Repair EA App', env_vars.get('repaireaapplaunchoptions'), env_vars.get('repaireaappstartingdir'), None)



def get_sgdb_art(game_id, launcher):
    decky_plugin.logger.info(f"Downloading icon artwork...")
    icon = download_artwork(game_id, "icons")
    decky_plugin.logger.info(f"Downloading logo artwork...")
    logo64 = download_artwork(game_id, "logos")
    decky_plugin.logger.info(f"Downloading hero artwork...")
    hero64 = download_artwork(game_id, "heroes")
    decky_plugin.logger.info("Downloading grids artwork of size 600x900...")
    gridp64 = download_artwork(game_id, "grids", "600x900")
    decky_plugin.logger.info("Downloading grids artwork of size 920x430...")
    grid64 = download_artwork(game_id, "grids", "920x430")

    # Fetch launcher icon based on the launcher type for (scanner icon notiifications in the front end)
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
    }

    launcher_icon = download_artwork(launcher_icons.get(launcher, ""), "icons")

    # Use the game icon if available, otherwise use the launcher icon
    if not icon:
        icon = launcher_icon

    return icon, logo64, hero64, gridp64, grid64, launcher_icon


def download_artwork(game_id, art_type, dimensions=None):
    if not game_id:
        decky_plugin.logger.info(f"Skipping download for {art_type} artwork. Game ID is empty.")
        return None

    # If the result is not in the cache, make the API call
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
        return None

    # Continue with the rest of your function using `data`
    for artwork in data['data']:
        if game_id == 5297303 and dimensions == "600x900":  # get a better poster for Xbox Game Pass
            image_url = "https://cdn2.steamgriddb.com/thumb/eea5656d3244578f512f32cb4043792a.jpg"
        else:
            image_url = artwork['thumb']
        decky_plugin.logger.info(f"Downloading image from: {image_url}")
        try:
            response = requests.get(image_url, stream=True)
            response.raise_for_status()
            if response.status_code == 200:
                return b64encode(response.content).decode('utf-8')
        except requests.exceptions.RequestException as e:
            decky_plugin.logger.info(f"Error downloading image: {e}")
            if art_type == 'icons':
                return download_artwork(game_id, 'icons_ico', dimensions)
    return None

def get_game_id(game_name):
    if game_name == "Disney+":  # hardcode disney+ game ID
        return 5260961
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
            decky_plugin.logger.info(f"Error searching for game ID (attempt {attempt + 1}): {e}")
            if "502 Server Error: Bad Gateway" in str(e) and attempt < retry_attempts:
                # Retry after a short delay
                delay_time = 2  # 2 seconds delay for retry
                decky_plugin.logger.info(f"Retrying search for game ID after {delay_time}s...")
                time.sleep(delay_time)  # Retry after 2 seconds
            else:
                decky_plugin.logger.info(f"Error searching for game ID: {e}")
                return "default_game_id"  # Return default game ID if the error is not related to server issues

    # If all retry attempts fail, return the default game ID
    decky_plugin.logger.info("Max retry attempts reached. Returning default game ID.")
    return "default_game_id"
