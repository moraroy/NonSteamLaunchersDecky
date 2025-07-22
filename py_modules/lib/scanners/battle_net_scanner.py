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
    # Add more games here...
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
            decky_plugin.logger.info("Skipping 'battle_net' entry")
            continue
        if "Resumable" not in game_data:
            decky_plugin.logger.info(f"Skipping {game_key}, no 'Resumable' key found")
            continue
        if game_data["Resumable"] == "false":
            decky_plugin.logger.info(f"Game {game_key} is not resumable, adding to game_dict")
            game_dict[game_key] = {
                "ServerUid": game_data.get("ServerUid", ""),
                "LastActioned": game_data.get("LastActioned", "")
            }

    decky_plugin.logger.info(f"Parsed config data: {game_dict}")
    return game_dict

def fix_windows_path(path):
    decky_plugin.logger.info(f"Fixing Windows path: {path}")
    if path.startswith('/c/'):
        fixed_path = 'C:\\' + path[3:].replace('/', '\\')
        decky_plugin.logger.info(f"Fixed Windows path: {fixed_path}")
        return fixed_path
    return path



def battle_net_scanner(logged_in_home, bnet_launcher, create_new_entry):
    game_dict = {}

    if platform.system() == "Windows":
        decky_plugin.logger.info("Detected platform: Windows")
        config_file_path = fix_windows_path(logged_in_home) + '\\AppData\\Roaming\\Battle.net\\Battle.net.config'
    else:
        decky_plugin.logger.info("Detected platform: Non-Windows")
        config_file_path = f"{logged_in_home}/.local/share/Steam/steamapps/compatdata/{bnet_launcher}/pfx/drive_c/users/steamuser/AppData/Roaming/Battle.net/Battle.net.config"

    decky_plugin.logger.info(f"Config file path: {config_file_path}")

    if os.path.exists(config_file_path):
        decky_plugin.logger.info("Battle.net config file found, parsing...")
        game_dict = parse_battlenet_config(config_file_path)
    else:
        decky_plugin.logger.info("Battle.net config file not found. Skipping Battle.net Games Scanner.")

    if game_dict:
        for game_key, game_info in game_dict.items():
            time.sleep(0.1)
            decky_plugin.logger.info(f"Processing game: {game_key}")

            if game_key == "prometheus":
                decky_plugin.logger.info("Handling 'prometheus' as 'Pro'")
                game_key = "Pro"
            elif game_key == "fenris":
                decky_plugin.logger.info("Handling 'fenris' as 'Fen'")
                game_key = "Fen"
            elif game_key == "diablo3":
                decky_plugin.logger.info("Handling 'diablo3' as 'D3'")
                game_key = "D3"
            elif game_key == "hs_beta":
                decky_plugin.logger.info("Handling 'hs_beta' as 'WTCG'")
                game_key = "WTCG"
            elif game_key == "wow_classic":
                decky_plugin.logger.info("Handling 'wow_classic' as 'WoWC'")
                game_key = "WoWC"
            elif game_key == "wow":
                decky_plugin.logger.info("Handling 'wow' as 'WoW'")
                game_key = "WoW"
            elif game_key == "aqua":
                decky_plugin.logger.info("Handling 'aqua' as 'Aqua'")
                game_key = "Aqua"
            elif game_key == "aris":
                decky_plugin.logger.info("Handling 'aris' as 'Aris'")
                game_key = "Aris"
            elif game_key == "heroes":
                game_key = "Hero"
            elif game_key == "gryphon":
                game_key = "GRY"
            elif game_key == "lbra":
                decky_plugin.logger.info("Handling 'lbra' as 'LBRA'")
                game_key = "LBRA"

            game_name = flavor_mapping.get(game_key, "unknown")

            if game_name == "unknown":
                # Try to match with uppercase version of the key
                game_name = flavor_mapping.get(game_key.upper(), "unknown")
                decky_plugin.logger.info(f"Trying uppercase for {game_key}: {game_name}")
                if game_name == "unknown":
                    decky_plugin.logger.info(f"Game {game_key} remains unknown, skipping...")
                    continue

            # Update game_key to its matched form
            matched_key = next((k for k, v in flavor_mapping.items() if v == game_name), game_key)
            decky_plugin.logger.info(f"Matched key for {game_key}: {matched_key}")

            if game_name == "Overwatch":
                game_name = "Overwatch 2"
                decky_plugin.logger.info(f"Renaming 'Overwatch' to 'Overwatch 2'")

            if game_info['ServerUid'] == "unknown":
                decky_plugin.logger.info(f"Skipping game {game_key} due to unknown ServerUid")
                continue

            if platform.system() == "Windows":
                exe_path = 'C:\\Program Files (x86)\\Battle.net\\Battle.net.exe'
                start_dir = 'C:\\Program Files (x86)\\Battle.net\\'
                launch_options = '--exec="launch {}" battlenet://{}'.format(matched_key, matched_key)
            else:
                exe_path = f'"{logged_in_home}/.local/share/Steam/steamapps/compatdata/{bnet_launcher}/pfx/drive_c/Program Files (x86)/Battle.net/Battle.net.exe"'.format(logged_in_home, bnet_launcher)
                start_dir = f'"{logged_in_home}/.local/share/Steam/steamapps/compatdata/{bnet_launcher}/pfx/drive_c/Program Files (x86)/Battle.net/"'.format(logged_in_home, bnet_launcher)
                launch_options = f'STEAM_COMPAT_DATA_PATH="{logged_in_home}/.local/share/Steam/steamapps/compatdata/{bnet_launcher}" %command% --exec="launch {matched_key}" battlenet://{matched_key}'



            decky_plugin.logger.info(f"Creating new entry for {game_name} with exe_path: {exe_path}")
            create_new_entry(exe_path, game_name, launch_options, start_dir, "Battle.net")
            track_game(game_name, "Battle.net")

    decky_plugin.logger.info("Battle.net Games Scanner completed.")


# End of Battle.net Scanner
