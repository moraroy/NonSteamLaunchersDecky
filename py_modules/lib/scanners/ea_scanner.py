import os
import platform
import time
import externals.xml.etree.ElementTree as ET
import decky_plugin
from scanners.game_tracker import track_game

# EA App Game Scanner

def get_ea_app_game_info(installed_games, game_directory_path):
    game_dict = {}
    for game in installed_games:
        if platform.system() == "Windows":
            xml_file_path = f"{game_directory_path}\\{game}\\__Installer\\installerdata.xml"
        else:
            xml_file_path = f"{game_directory_path}/{game}/__Installer/installerdata.xml"

        if not os.path.exists(xml_file_path):
            continue

        xml_file = ET.parse(xml_file_path)
        xml_root = xml_file.getroot()
        ea_ids = None
        game_name = None
        for content_id in xml_root.iter('contentID'):
            ea_ids = content_id.text
            break  # Exit the loop after the first ID is found
        for game_title in xml_root.iter('gameTitle'):
            if game_name is None:
                game_name = game_title.text
                continue
        for game_title in xml_root.iter('title'):
            if game_name is None:
                game_name = game_title.text
                continue
        if game_name is None:
            game_name = game
        if ea_ids:  # Add the game's info to the dictionary if its ID was found in the folder
            game_dict[game_name] = ea_ids
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
    else:
        installed_games = os.listdir(game_directory_path)  # Get a list of game folders
        game_dict = get_ea_app_game_info(installed_games, game_directory_path)

        for game, ea_ids in game_dict.items():
            time.sleep(0.1)
            if platform.system() == "Windows":
                launch_options = f"origin2://game/launch?offerIds={ea_ids}"
                exe_path = f'"{ea_launcher_path}"'.strip('"')
                start_dir = f'"C:\\Program Files\\Electronic Arts\\EA Desktop\\EA Desktop"'.strip('"')
            else:
                launch_options = f'STEAM_COMPAT_DATA_PATH="{logged_in_home}/.local/share/Steam/steamapps/compatdata/{ea_app_launcher}/" %command% "origin2://game/launch?offerIds={ea_ids}"'
                exe_path = f'"{logged_in_home}/.local/share/Steam/steamapps/compatdata/{ea_app_launcher}/pfx/drive_c/Program Files/Electronic Arts/EA Desktop/EA Desktop/EALaunchHelper.exe"'
                start_dir = f'"{logged_in_home}/.local/share/Steam/steamapps/compatdata/{ea_app_launcher}/pfx/drive_c/Program Files/Electronic Arts/EA Desktop/EA Desktop/"'

            create_new_entry(exe_path, game, launch_options, start_dir, "EA App")
            track_game(game, "EA App")
