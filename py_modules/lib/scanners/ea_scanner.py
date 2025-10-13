import os
import platform
import time
import externals.xml.etree.ElementTree as ET
import decky_plugin
from scanners.game_tracker import track_game
import re

# Your mojibake fix function
def fix_encoding(text):
    return text.encode('latin1').decode('utf-8')

# Registry parser from first snippet
def extract_games_fixed(filename):
    games = {}
    key_re = re.compile(r'\[Software\\\\Wow6432Node\\\\Origin Games\\\\(\d+)\]')
    name_re = re.compile(r'"DisplayName"="(.+)"')
    current_id = None
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            key_match = key_re.search(line)
            if key_match:
                current_id = key_match.group(1)
                continue
            if current_id:
                name_match = name_re.search(line)
                if name_match:
                    raw_name = name_match.group(1)
                    raw_name = raw_name.replace(r'\x2122', '™')
                    name = bytes(raw_name, "utf-8").decode("unicode_escape")
                    name = fix_encoding(name)
                    games[current_id] = name
                    current_id = None
    return games


def get_ea_app_game_info(installed_games, game_directory_path, sys_reg_file=None):
    sys_reg_games = {}
    if sys_reg_file and os.path.isfile(sys_reg_file):
        try:
            sys_reg_games = extract_games_fixed(sys_reg_file)
            sys_reg_name_to_id = {v: k for k, v in sys_reg_games.items()}
        except Exception as e:
            decky_plugin.logger.error(f"Error reading sys reg fallback file: {e}")
            sys_reg_name_to_id = {}
    else:
        sys_reg_name_to_id = {}

    game_dict = {}
    for game in installed_games:
        try:
            if platform.system() == "Windows":
                xml_path = os.path.join(game_directory_path, game, "__Installer", "installerdata.xml")
            else:
                xml_path = os.path.join(game_directory_path, game, "__Installer", "installerdata.xml")

            if not os.path.isfile(xml_path):
                continue

            xml_file = ET.parse(xml_path)
            xml_root = xml_file.getroot()

            ea_ids = None
            game_name = None

            for content_id in xml_root.iter('contentID'):
                ea_ids = content_id.text
                break

            for game_title in xml_root.iter('gameTitle'):
                if game_name is None:
                    game_name = game_title.text

            for game_title in xml_root.iter('title'):
                if game_name is None:
                    game_name = game_title.text

            if game_name is None:
                game_name = game

            matched_id = None
            if not ea_ids and sys_reg_name_to_id:
                decky_plugin.logger.info(f"No ID in XML for '{game_name}', checking registry fallback...")
                for reg_name, reg_id in sys_reg_name_to_id.items():
                    if reg_name == game_name:
                        matched_id = reg_id
                        break
                if matched_id:
                    ea_ids = matched_id

            if ea_ids:
                game_dict[game_name] = ea_ids
        except Exception as e:
            decky_plugin.logger.error(f"Error parsing XML for {game}: {e}")

    return game_dict


def ea_scanner(logged_in_home, ea_app_launcher, create_new_entry):
    if platform.system() == "Windows":
        game_directory_path = "C:\\Program Files\\EA Games\\"
        ea_launcher_path = "C:\\Program Files\\Electronic Arts\\EA Desktop\\EA Desktop\\EALaunchHelper.exe"
    else:
        game_directory_path = f"{logged_in_home}/.local/share/Steam/steamapps/compatdata/{ea_app_launcher}/pfx/drive_c/Program Files/EA Games/"
        ea_launcher_path = f"{logged_in_home}/.local/share/Steam/steamapps/compatdata/{ea_app_launcher}/pfx/drive_c/Program Files/Electronic Arts/EA Desktop/EA Desktop/EALaunchHelper.exe"

    if not os.path.isdir(game_directory_path):
        decky_plugin.logger.info("EA App game data not found. Skipping EA App Scanner.")
        return

    installed_games = [g for g in os.listdir(game_directory_path) if os.path.isdir(os.path.join(game_directory_path, g))]
    sys_reg_path = f"{logged_in_home}/.local/share/Steam/steamapps/compatdata/{ea_app_launcher}/pfx/system.reg"

    game_dict = get_ea_app_game_info(installed_games, game_directory_path, sys_reg_file=sys_reg_path)

    for game, ea_ids in game_dict.items():
        time.sleep(0.1)
        if platform.system() == "Windows":
            launch_options = f"origin2://game/launch?offerIds={ea_ids}"
            exe_path = ea_launcher_path.strip('"')
            start_dir = "C:\\Program Files\\Electronic Arts\\EA Desktop\\EA Desktop"
        else:
            launch_options = f'STEAM_COMPAT_DATA_PATH="{logged_in_home}/.local/share/Steam/steamapps/compatdata/{ea_app_launcher}/" %command% "origin2://game/launch?offerIds={ea_ids}"'
            exe_path = f'"{ea_launcher_path}"'
            start_dir = f'"{logged_in_home}/.local/share/Steam/steamapps/compatdata/{ea_app_launcher}/pfx/drive_c/Program Files/Electronic Arts/EA Desktop/EA Desktop/"'

        create_new_entry(exe_path, game, launch_options, start_dir, "EA App")
        track_game(game, "EA App")
