import os
import json
import decky_plugin
import platform
import time
from scanners.game_tracker import track_game


# Define your mapping
flavor_mapping = {
    "RTRO": "Blizzard Arcade Collection",
    "D1": "Diablo",
    "OSI": "Diablo II Resurrected",
    "D3": "Diablo III",
    "Fen": "Diablo IV",
    "ANBS": "Diablo Immortal (PC)",
    "WTCG": "Hearthstone",
    "Hero": "Heroes of the Storm",
    "Pro": "Overwatch 2",
    "S1": "StarCraft",
    "S2": "StarCraft 2",
    "W1": "Warcraft: Orcs & Humans",
    "W1R": "Warcraft I: Remastered",
    "W2": "Warcraft II: Battle.net Edition",
    "W2R": "Warcraft II: Remastered",
    "W3": "Warcraft III: Reforged",
    "WoW": "World of Warcraft",
    "WoWC": "World of Warcraft Classic",
    "GRY": "Warcraft Rumble",
    "ZEUS": "Call of Duty: Black Ops - Cold War",
    "VIPR": "Call of Duty: Black Ops 4",
    "ODIN": "Call of Duty: Modern Warfare",
    "AUKS": "Call of Duty",
    "LAZR": "Call of Duty: MW 2 Campaign Remastered",
    "FORE": "Call of Duty: Vanguard",
    "SPOT": "Call of Duty: Modern Warfare III",
    "WLBY": "Crash Bandicoot 4: It's About Time",
    "Aqua": "Avowed",
    "LBRA": "Tony Hawk's Pro Skater 3 + 4",
    "SCOR": "Sea of Thieves",
    "ARK": "The Outer Worlds 2",
}


def parse_battlenet_config(config_file_path):
    decky_plugin.logger.info(f"Opening Battle.net config file at: {config_file_path}")

    with open(config_file_path, 'r') as file:
        config_data = json.load(file)

    games_info = config_data.get("Games", {})
    game_dict = {}

    for game_key, game_data in games_info.items():
        decky_plugin.logger.info(f"Processing game: {game_key}")

        if game_key == "battle_net":
            continue

        if "Resumable" not in game_data:
            decky_plugin.logger.info(f"Skipping {game_key}, no 'Resumable' key found")
            continue

        game_dict[game_key] = {
            "ServerUid": game_data.get("ServerUid", ""),
            "LastActioned": game_data.get("LastActioned", ""),
            "LastPlayed": game_data.get("LastPlayed", "")
        }

        decky_plugin.logger.info(f"{game_key} marked as INSTALLED")

    return game_dict


def fix_windows_path(path):
    decky_plugin.logger.info(f"Fixing Windows path: {path}")
    if path.startswith('/c/'):
        return 'C:\\' + path[3:].replace('/', '\\')
    return path


def battle_net_scanner(logged_in_home, bnet_launcher, create_new_entry):
    game_dict = {}

    if platform.system() == "Windows":
        decky_plugin.logger.info("Detected platform: Windows")
        config_file_path = (
            fix_windows_path(logged_in_home)
            + '\\AppData\\Roaming\\Battle.net\\Battle.net.config'
        )
    else:
        decky_plugin.logger.info("Detected platform: Non-Windows")
        config_file_path = (
            f"{logged_in_home}/.local/share/Steam/steamapps/"
            f"compatdata/{bnet_launcher}/pfx/drive_c/users/"
            f"steamuser/AppData/Roaming/Battle.net/Battle.net.config"
        )

    decky_plugin.logger.info(f"Config file path: {config_file_path}")

    if os.path.exists(config_file_path):
        decky_plugin.logger.info("Battle.net config file found, parsing...")
        game_dict = parse_battlenet_config(config_file_path)
    else:
        decky_plugin.logger.info("Battle.net config file not found. Skipping Battle.net Games Scanner.")

    if game_dict:
        for raw_key, game_info in game_dict.items():
            time.sleep(0.1)
            decky_plugin.logger.info(f"Processing game: {raw_key}")

            game_key = raw_key

            # Normalize internal keys
            if game_key == "prometheus":
                game_key = "Pro"
            elif game_key == "fenris":
                game_key = "Fen"
            elif game_key == "diablo3":
                game_key = "D3"
            elif game_key == "hs_beta":
                game_key = "WTCG"
            elif game_key == "wow_classic":
                game_key = "WoWC"
            elif game_key == "wow":
                game_key = "WoW"
            elif game_key == "aqua":
                game_key = "Aqua"
            elif game_key == "heroes":
                game_key = "Hero"
            elif game_key == "gryphon":
                game_key = "GRY"
            elif game_key == "lbra":
                game_key = "LBRA"
            elif game_key in ("seaofthieves", "sot", "scor"):
                game_key = "SCOR"
            elif game_key == "wow_classic_era":
                game_key = "WoWC"




            game_name = flavor_mapping.get(game_key)

            if not game_name:
                game_name = flavor_mapping.get(game_key.upper())

            if not game_name:
                game_name = flavor_mapping.get(game_key.lower())

            if not game_name:
                game_name = flavor_mapping.get(game_key.title())

            if not game_name:
                decky_plugin.logger.info(f"Unknown game mapping: {game_key}, skipping")
                continue

            decky_plugin.logger.info(f"Resolved {raw_key} → {game_name}")

            matched_key = game_key

            if platform.system() == "Windows":
                exe_path = 'C:\\Program Files (x86)\\Battle.net\\Battle.net.exe'
                start_dir = 'C:\\Program Files (x86)\\Battle.net\\'
                launch_options = f'--exec="launch {matched_key}" battlenet://{matched_key}'
            else:
                compat_path = (
                    f"{logged_in_home}/.local/share/Steam/steamapps/"
                    f"compatdata/{bnet_launcher}"
                )

                exe_path = (
                    f'"{compat_path}/pfx/drive_c/Program Files (x86)/'
                    f'Battle.net/Battle.net.exe"'
                )

                start_dir = (
                    f'"{compat_path}/pfx/drive_c/Program Files (x86)/'
                    f'Battle.net/"'
                )

                launch_options = (
                    f'STEAM_COMPAT_DATA_PATH="{compat_path}" '
                    f'%command% --exec="launch {matched_key}" '
                    f'battlenet://{matched_key}'
                )

            decky_plugin.logger.info(f"Creating entry for {game_name}")
            create_new_entry(exe_path, game_name, launch_options, start_dir, "Battle.net")
            track_game(game_name, "Battle.net")

    decky_plugin.logger.info("Battle.net Games Scanner completed.")