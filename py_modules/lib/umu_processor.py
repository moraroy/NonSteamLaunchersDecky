import requests
import csv
import os
import re
import decky_plugin

CSV_URL = "https://raw.githubusercontent.com/Open-Wine-Components/umu-database/main/umu-database.csv"

# Global variable to store CSV data
csv_data = []

def fetch_and_parse_csv():
    global csv_data
    response = requests.get(CSV_URL)
    response.raise_for_status()
    csv_data = [row for row in csv.DictReader(response.text.splitlines())]
    decky_plugin.logger.info("Successfully fetched and parsed CSV data.")
    return csv_data

def list_all_entries():
    global csv_data
    if not csv_data:
        csv_data = fetch_and_parse_csv()
    return csv_data

def extract_umu_id_from_launch_options(launchoptions):
    # Check if the launch options contain STEAM_COMPAT_DATA_PATH
    if 'STEAM_COMPAT_DATA_PATH=' not in launchoptions:
        return None

    # EA
    match = re.search(r'offerIds=(\d+)', launchoptions)
    if match:
        return match.group(1)
    # Amazon
    match = re.search(r'(amzn1\.adg\.product\.\S+)', launchoptions)
    if match:
        product_id = match.group(1).rstrip("'")  # Remove trailing single quote
        return product_id
    # Epic
    match = re.search(r'com\.epicgames\.launcher://apps/(\w+)[?&]', launchoptions)
    if match:
        epic_id = match.group(1).lower() if not match.group(1).isdigit() else match.group(1)
        return epic_id
    # Ubisoft
    match = re.search(r'uplay://launch/(\d+)/\d+', launchoptions)
    if match:
        return match.group(1)
    # GOG
    match = re.search(r'/gameId=(\d+)', launchoptions)
    if match:
        return match.group(1)
    return None

def extract_base_path(launchoptions):
    match = re.search(r'STEAM_COMPAT_DATA_PATH="([^"]+)"', launchoptions)
    if match:
        return match.group(1)
    raise ValueError("STEAM_COMPAT_DATA_PATH not found in launch options")

def modify_shortcut_for_umu(appname, exe, launchoptions, startingdir, logged_in_home, compat_tool_name):
    # Skip UMU modification for specific titles
    skip_titles = ["genshin impact", "zenless zone zero"]
    if appname.lower() in skip_titles:
        decky_plugin.logger.info(f"Skipping UMU modification for {appname}.")
        return exe, startingdir, launchoptions
    
    dir_path = os.path.expanduser("~/.steam/root/compatibilitytools.d")
    pattern = re.compile(r"UMU-Proton-(\d+(?:\.\d+)*)(?:-(\d+(?:\.\d+)*))?")

    def parse_version(m):
        main, sub = m.groups()
        return tuple(map(int, (main + '.' + (sub or '0')).split('.')))

    umu_folders = [
        (parse_version(m), name)
        for name in os.listdir(dir_path)
        if (m := pattern.match(name)) and os.path.isdir(os.path.join(dir_path, name))
    ]

    if umu_folders:
        compat_tool_name = max(umu_folders)[1]


    # Skip processing if STEAM_COMPAT_DATA_PATH is not present
    if 'STEAM_COMPAT_DATA_PATH=' not in launchoptions:
        decky_plugin.logger.info(f"Launch options for {appname} do not contain STEAM_COMPAT_DATA_PATH. Skipping modification.")
        return exe, startingdir, launchoptions

    codename = extract_umu_id_from_launch_options(launchoptions)
    if not codename:
        print(f"No codename found in launch options for {appname}. Trying to match appname.")

    entries = list_all_entries()
    if not entries:
        print(f"No entries found in UMU database. Skipping modification for {appname}.")
        return exe, startingdir, launchoptions

    if not codename:
        for entry in entries:
            if entry.get('TITLE') and entry['TITLE'].lower() == appname.lower():
                codename = entry['CODENAME']
                break

    if codename:
        for entry in entries:
            if entry['CODENAME'] == codename:
                umu_id = entry['UMU_ID'].replace("umu-", "")  # Remove the "umu-" prefix
                base_path = extract_base_path(launchoptions)
                new_exe = f'"{logged_in_home}/bin/umu-run" {exe}'
                new_start_dir = f'"{logged_in_home}/bin/"'

                # Update only the launchoptions part for different game types
                updated_launch = launchoptions

                # Hoyoplay - Extract the game identifier
               #match = re.search(r'--game=(\w+)', launchoptions)
                #if match:
                    #codename = match.group(1)  # Capture the identifier
                    #updated_launch = f"'--game={codename}'"

                if "origin2://game/launch?offerIds=" in launchoptions:
                    updated_launch = f'"origin2://game/launch?offerIds={codename}"'
                elif "amazon-games://play/amzn1.adg.product." in launchoptions:
                    updated_launch = f"-'amazon-games://play/{codename}'"
                elif "com.epicgames.launcher://apps/" in launchoptions:
                    updated_launch = f"-'com.epicgames.launcher://apps/{codename}?action=launch&silent=true'"
                elif "uplay://launch/" in launchoptions:
                    updated_launch = f'"uplay://launch/{codename}/0"'
                elif "/command=runGame /gameId=" in launchoptions:
                    updated_launch = f'/command=runGame /gameId={codename} /path={launchoptions.split("/path=")[1]}'

                # Ensure the first STEAM_COMPAT_DATA_PATH is included and avoid adding it again
                if 'STEAM_COMPAT_DATA_PATH=' in updated_launch:
                    # Remove the existing STEAM_COMPAT_DATA_PATH if it exists in the launch options
                    updated_launch = re.sub(r'STEAM_COMPAT_DATA_PATH="[^"]+" ', '', updated_launch)

                # Always include the first STEAM_COMPAT_DATA_PATH at the start
                new_launch_options = (
                    f'STEAM_COMPAT_DATA_PATH="{base_path}" '
                    f'WINEPREFIX="{base_path}pfx" '
                    f'GAMEID="{umu_id}" '
                    f'PROTONPATH="{logged_in_home}/.steam/root/compatibilitytools.d/{compat_tool_name}" '
                )

                # Check if %command% is already in the launch options
                if '%command%' not in updated_launch:
                    updated_launch = f'%command% {updated_launch}'

                # Final new launch options
                new_launch_options += updated_launch

                decky_plugin.logger.info(f"Modified shortcut for {appname}")
                return new_exe, new_start_dir, new_launch_options
    decky_plugin.logger.info(f"No matching codename found in UMU database for {appname}. Skipping modification.")
    return exe, startingdir, launchoptions
