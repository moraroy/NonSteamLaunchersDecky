import os
import json
import re
import decky_plugin
import platform
import time

from scanners.game_tracker import track_game

flavor_mapping = {

    # Blizzard
    "RTRO": "Blizzard Arcade Collection",
    "D1": "Diablo",
    "OSI": "Diablo II: Resurrected",
    "D3": "Diablo III",
    "Fen": "Diablo IV",
    "ANBS": "Diablo Immortal (PC)",
    "WTCG": "Hearthstone",
    "Hero": "Heroes of the Storm",
    "Pro": "Overwatch",
    "S1": "StarCraft",
    "S2": "StarCraft 2",
    "W1": "Warcraft: Orcs & Humans",
    "W2": "Warcraft II: Battle.net Edition",
    "W1R": "Warcraft: Remastered",
    "W2R": "Warcraft II: Remastered",
    "W3": "Warcraft III: Reforged",
    "WoW": "World of Warcraft",
    "WoWC": "World of Warcraft Classic",
    "WoWF": "World of Warcraft: Forever",
    "GRY": "Warcraft Rumble",

    # Microsoft
    "AQUA": "Avowed",
    "ARIS": "Doom: The Dark Ages",
    "ARK": "The Outer Worlds 2",
    "SCOR": "Sea of Thieves",
    "LBRA": "Tony Hawk's Pro Skater 3 + 4",

    # Activision
    "AUKS": "Call of Duty",
    "VIPR": "Call of Duty: Black Ops 4",
    "BTLR": "Call of Duty: Black Ops 6",
    "ZEUS": "Call of Duty: Black Ops Cold War",
    "LAZR": "Call of Duty: MW 2 Campaign Remastered",
    "ODIN": "Call of Duty: Modern Warfare",
    "NINA": "Call of Duty: Modern Warfare II",
    "PNTA": "Call of Duty: Modern Warfare III",
    "FORE": "Call of Duty: Vanguard",
    "WLBY": "Crash Bandicoot 4: It's About Time",

    # CD Projekt Red
    "LYRA": "The Witcher 3: Wild Hunt Remastered",
}


game_aliases = {

    # Blizzard
    "prometheus": "Pro",
    "fenris": "Fen",
    "diablo3": "D3",
    "hs_beta": "WTCG",
    "wow_classic": "WoWC",
    "wow_classic_era": "WoWC",
    "wow": "WoW",
    "heroes": "Hero",
    "gryphon": "GRY",

    # Microsoft
    "aqua": "AQUA",
    "aris": "ARIS",
    "ark": "ARK",
    "lbra": "LBRA",
    "seaofthieves": "SCOR",
    "sot": "SCOR",
    "scor": "SCOR",

    # Activision
    "blackops6": "BTLR",
    "modernwarfare2": "NINA",
    "modernwarfare3": "PNTA",
}

flavor_lookup = {
    code.casefold(): code
    for code in flavor_mapping
}

def resolve_battlenet_game(raw_key):

    normalized = str(raw_key).strip().casefold()

    # Check config aliases first
    game_code = game_aliases.get(normalized)

    # Otherwise check existing product codes
    if not game_code:
        game_code = flavor_lookup.get(normalized)

    if not game_code:
        return None, None

    game_name = flavor_mapping.get(game_code)

    return game_code, game_name


def detect_latest_ge_proton(logged_in_home):

    ge_proton_dir = os.path.join(
        logged_in_home,
        ".steam",
        "root",
        "compatibilitytools.d"
    )

    decky_plugin.logger.info(
        f"Searching for GE-Proton installations: {ge_proton_dir}"
    )

    ge_proton_versions = []

    if not os.path.isdir(ge_proton_dir):
        raise FileNotFoundError(
            f"GE-Proton directory not found: {ge_proton_dir}"
        )

    for entry in os.scandir(ge_proton_dir):

        if not entry.is_dir():
            continue

        match = re.fullmatch(
            r"GE-Proton(\d+)-(\d+)-x86_64",
            entry.name
        )

        if match:

            version = tuple(map(int, match.groups()))

            ge_proton_versions.append(
                (version, entry.path)
            )

    if not ge_proton_versions:
        raise FileNotFoundError(
            f"No GE-Proton installations found in {ge_proton_dir}"
        )

    latest_ge_proton = max(
        ge_proton_versions,
        key=lambda x: x[0]
    )[1]

    ge_proton = os.path.join(
        latest_ge_proton,
        "proton"
    )

    if not os.path.isfile(ge_proton):
        raise FileNotFoundError(
            f"GE-Proton executable not found: {ge_proton}"
        )

    decky_plugin.logger.info(
        f"Detected latest GE-Proton: {latest_ge_proton}"
    )

    return ge_proton



def parse_battlenet_config(config_file_path):

    decky_plugin.logger.info(
        f"Opening Battle.net config file at: {config_file_path}"
    )

    with open(config_file_path, "r") as file:
        config_data = json.load(file)

    games_info = config_data.get("Games", {})
    game_dict = {}

    for game_key, game_data in games_info.items():

        decky_plugin.logger.info(
            f"Processing game: {game_key}"
        )

        if game_key == "battle_net":
            continue

        # INSTALL RULE: key existence only
        if "Resumable" not in game_data:

            decky_plugin.logger.info(
                f"Skipping {game_key}: no Resumable key found"
            )

            continue

        game_dict[game_key] = {
            "ServerUid": game_data.get("ServerUid", game_key),
            "LastActioned": game_data.get("LastActioned", ""),
            "LastPlayed": game_data.get("LastPlayed", "")
        }

        decky_plugin.logger.info(
            f"{game_key} marked as INSTALLED"
        )

    return game_dict

def fix_windows_path(path):

    decky_plugin.logger.info(
        f"Fixing Windows path: {path}"
    )

    if path.startswith('/c/'):
        return 'C:\\' + path[3:].replace('/', '\\')

    return path



def battle_net_scanner(logged_in_home, bnet_launcher, create_new_entry):

    game_dict = {}

    is_windows = platform.system() == "Windows"

    if is_windows:

        decky_plugin.logger.info(
            "Detected platform: Windows"
        )

        config_file_path = (
            fix_windows_path(logged_in_home)
            + '\\AppData\\Roaming\\Battle.net\\Battle.net.config'
        )

    else:

        decky_plugin.logger.info(
            "Detected platform: Non-Windows"
        )

        compat_path = os.path.join(
            logged_in_home,
            ".local",
            "share",
            "Steam",
            "steamapps",
            "compatdata",
            str(bnet_launcher)
        )

        config_file_path = (
            f"{compat_path}/pfx/drive_c/users/"
            f"steamuser/AppData/Roaming/Battle.net/"
            f"Battle.net.config"
        )

    decky_plugin.logger.info(
        f"Config file path: {config_file_path}"
    )


    if not os.path.exists(config_file_path):

        decky_plugin.logger.info(
            "Battle.net config file not found. "
            "Skipping Battle.net Games Scanner."
        )

        return

    decky_plugin.logger.info(
        "Battle.net config file found."
    )

    ge_proton = None

    if not is_windows:

        try:

            ge_proton = detect_latest_ge_proton(
                logged_in_home
            )

        except (OSError, FileNotFoundError) as error:

            decky_plugin.logger.error(
                f"GE-Proton detection failed: {error}"
            )

            return

    try:

        game_dict = parse_battlenet_config(
            config_file_path
        )

    except (json.JSONDecodeError, OSError) as error:

        decky_plugin.logger.error(
            f"Error reading Battle.net config: {error}"
        )

        return


    if game_dict:

        for raw_key, game_info in game_dict.items():

            time.sleep(0.1)

            decky_plugin.logger.info(
                f"Processing game: {raw_key}"
            )

            # Resolve actual Battle.net product code
            game_code, game_name = resolve_battlenet_game(
                raw_key
            )

            if not game_code or not game_name:

                decky_plugin.logger.info(
                    f"Unknown game mapping: {raw_key}, skipping"
                )

                continue

            decky_plugin.logger.info(
                f"Resolved {raw_key} -> {game_code} -> {game_name}"
            )


            if is_windows:

                exe_path = (
                    'C:\\Program Files (x86)\\'
                    'Battle.net\\Battle.net.exe'
                )

                start_dir = (
                    'C:\\Program Files (x86)\\'
                    'Battle.net\\'
                )

                launch_options = (
                    f'--exec="launch {game_code}" '
                    f'battlenet://{game_code}'
                )

            else:

                exe_path = (
                    f'"{compat_path}/pfx/drive_c/'
                    f'Program Files (x86)/Battle.net/'
                    f'Battle.net.exe"'
                )

                start_dir = (
                    f'"{compat_path}/pfx/drive_c/'
                    f'Program Files (x86)/Battle.net/"'
                )

                launch_options = (
                    f'STEAM_COMPAT_DATA_PATH="{compat_path}/" '
                    f'%command% & sleep 15; '
                    f'STEAM_COMPAT_DATA_PATH="{compat_path}/" '
                    f'"{ge_proton}" run '
                    f'"C:\\\\Program Files (x86)\\\\Battle.net\\\\Battle.net Launcher.exe" '
                    f'--exec="launch {game_code}"'
                )

            decky_plugin.logger.info(
                f"Creating entry for {game_name}"
            )

            decky_plugin.logger.info(
                f"Product code: {game_code}"
            )

            decky_plugin.logger.info(
                f"Launch options: {launch_options}"
            )

            create_new_entry(
                exe_path,
                game_name,
                launch_options,
                start_dir,
                "Battle.net"
            )


            track_game(
                game_name,
                "Battle.net"
            )

    decky_plugin.logger.info(
        "Battle.net Games Scanner completed."
    )

