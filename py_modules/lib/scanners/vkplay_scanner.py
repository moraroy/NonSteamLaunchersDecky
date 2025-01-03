import decky_plugin
import os
import json
import platform
import configparser
import externals.xml.etree.ElementTree as ET

def vkplay_scanner(logged_in_home, vkplay_launcher, create_new_entry):
    # Set up paths based on the platform (Windows or others)
    if platform.system() == "Windows":
        gamecenter_ini_path = r"C:\ProgramData\VK\GameCenter.ini"
        cache_folder_path = r"C:\ProgramData\VK\Cache\GameDescription"
        exe_template = r"C:\Program Files\VK\GameCenter\GameCenter.exe"
        start_dir_template = r"C:\Program Files\VK\GameCenter"
        launch_options_template = "-'vkplay://play/{game_id}'"
    else:
        # Assuming Linux or similar paths for VK Play data (adjust these paths accordingly)
        gamecenter_ini_path = f"{logged_in_home}/.local/share/Steam/steamapps/compatdata/{vkplay_launcher}/pfx/drive_c/users/steamuser/AppData/Local/GameCenter/GameCenter.ini"
        cache_folder_path = f"{logged_in_home}/.local/share/Steam/steamapps/compatdata/{vkplay_launcher}/pfx/drive_c/users/steamuser/AppData/Local/GameCenter/Cache/GameDescription/"
        exe_template = f"\"{logged_in_home}/.local/share/Steam/steamapps/compatdata/{vkplay_launcher}/pfx/drive_c/users/steamuser/AppData/Local/GameCenter/GameCenter.exe\""
        start_dir_template = f"\"{logged_in_home}/.local/share/Steam/steamapps/compatdata/{vkplay_launcher}/pfx/drive_c/users/steamuser/AppData/Local/GameCenter/\""
        launch_options_template = f"STEAM_COMPAT_DATA_PATH=\"{logged_in_home}/.local/share/Steam/steamapps/compatdata/{vkplay_launcher}/\" %command% 'vkplay://play/{{game_id}}'"

    # Check if the necessary files and directories exist
    if os.path.exists(gamecenter_ini_path) and os.path.exists(cache_folder_path):
        config = configparser.ConfigParser()

        try:
            with open(gamecenter_ini_path, 'r', encoding='utf-16') as file:
                config.read_file(file)
        except Exception as e:
            decky_plugin.logger.info(f"Error reading the GameCenter.ini file: {e}")
            return

        downloaded_games = dict(config.items('StartDownloadingGames')) if 'StartDownloadingGames' in config else {}
        installed_games = dict(config.items('DownloadFormSettings')) if 'DownloadFormSettings' in config else {}

        all_game_ids = set(downloaded_games.keys()).union(installed_games.keys())

        if 'Ad' in config:
            for key in config['Ad']:
                key_lower = key.lower()
                if key_lower.startswith('idmtlink0.') or key_lower.startswith('idmtlinkts0.'):
                    game_id = '0.' + key_lower.split('.')[1]
                    all_game_ids.add(game_id)

        decky_plugin.logger.info(f"All game IDs from INI: {all_game_ids}")

        # Check the cache folder for valid XML files
        all_files = os.listdir(cache_folder_path)
        valid_xml_files = []

        for file_name in all_files:
            if file_name.endswith(".json"):
                continue

            file_path = os.path.join(cache_folder_path, file_name)
            try:
                tree = ET.parse(file_path)
                valid_xml_files.append(file_path)
            except ET.ParseError:
                continue

        processed_game_ids = set()
        found_games = []

        # Process XML files to match games
        for xml_file in valid_xml_files:
            try:
                tree = ET.parse(xml_file)
                root = tree.getroot()
                game_item = root.find('GameItem')

                if game_item is not None:
                    game_id_xml = game_item.get('Name') or game_item.get('PackageName')
                    if game_id_xml:
                        game_id_in_ini = game_id_xml.replace('_', '.')
                        if game_id_in_ini in all_game_ids and game_id_in_ini not in processed_game_ids:
                            game_name = game_item.get('TitleEn', 'Unnamed Game')
                            found_games.append(f"{game_name} (ID: {game_id_in_ini})")
                            processed_game_ids.add(game_id_in_ini)
            except ET.ParseError:
                continue

        # Display found games
        if found_games:
            decky_plugin.logger.info("Found the following games:")
            for game in found_games:
                decky_plugin.logger.info(game)
        else:
            decky_plugin.logger.info("No games found.")

        # Generate the final entry for each game
        for game_id in all_game_ids:
            game_name = 'Unknown Game'
            for xml_file in valid_xml_files:
                try:
                    tree = ET.parse(xml_file)
                    root = tree.getroot()
                    game_item = root.find('GameItem')

                    if game_item is not None:
                        game_id_xml = game_item.get('Name') or game_item.get('PackageName')

                        if game_id_xml and game_id_xml.replace('_', '.') == game_id:
                            game_name = game_item.get('TitleEn', 'Unnamed Game')
                            break
                except ET.ParseError:
                    continue

            if game_name != 'Unknown Game':
                display_name = game_name
                launch_options = launch_options_template.format(game_id=game_id)
                exe_path = exe_template
                start_dir = start_dir_template

                # Create new entry for the game
                create_new_entry(exe_path, display_name, launch_options, start_dir, "VK Play")
    else:
        decky_plugin.logger.info("VK Play data not found. Skipping scanning for installed games.")
