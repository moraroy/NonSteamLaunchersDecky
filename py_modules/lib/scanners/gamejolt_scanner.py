import os
import json
import time
import decky_plugin
from scanners.game_tracker import track_game

def gamejolt_scanner(logged_in_home, gamejolt_launcher, create_new_entry):
    # Game Jolt Scanner

    # File paths for both the game list and package details
    games_file_path = f"{logged_in_home}/.local/share/Steam/steamapps/compatdata/{gamejolt_launcher}/pfx/drive_c/users/steamuser/AppData/Local/game-jolt-client/User Data/Default/games.wttf"
    packages_file_path = f"{logged_in_home}/.local/share/Steam/steamapps/compatdata/{gamejolt_launcher}/pfx/drive_c/users/steamuser/AppData/Local/game-jolt-client/User Data/Default/packages.wttf"

    # Check if both files exist before proceeding
    if not os.path.exists(games_file_path) or not os.path.exists(packages_file_path):
        decky_plugin.logger.info("One or both of the files do not exist. Skipping Game Jolt Scanner.")
    else:
        try:
            # Load the games file
            with open(games_file_path, 'r') as f:
                games_data = json.load(f)

            # Load the packages file
            with open(packages_file_path, 'r') as f:
                packages_data = json.load(f)

            # Check if 'objects' exists in the games data
            if 'objects' in games_data:
                # Iterate through each game object in the games file
                for game_id, game_info in games_data['objects'].items():
                    # Default values if information is missing
                    description = 'No Description'
                    install_dir = 'No Install Directory'
                    version = 'No Version Info'
                    executable_path = 'No Executable Path'

                    # Iterate over the 'objects' in the packages file to find a match
                    for package_id, package_info in packages_data.get('objects', {}).items():
                        # Check if the game_id in the package matches the current game_id
                        if package_info.get('game_id') == int(game_id):  # Match on game_id
                            # Extract information from the matched package
                            description = package_info.get('description', description)
                            install_dir = package_info.get('install_dir', install_dir)

                            # Safe extraction of version_number from 'release'
                            release_info = package_info.get('release', {})
                            version = release_info.get('version_number', version)

                            # Handle missing or empty launch options
                            if package_info.get('launch_options'):
                                executable_path = package_info['launch_options'][0].get('executable_path', executable_path)

                            break

                    # Set the display name to the game shortcut name from the JSON
                    display_name = game_info.get('title', 'No Title')
                    launch_options = f"STEAM_COMPAT_DATA_PATH=\"{logged_in_home}/.local/share/Steam/steamapps/compatdata/{gamejolt_launcher}/\" %command% --dir \"{install_dir}\" run"
                    exe_path = f"\"{logged_in_home}/.local/share/Steam/steamapps/compatdata/{gamejolt_launcher}/pfx/drive_c/users/steamuser/AppData/Local/GameJoltClient/GameJoltClient.exe\""
                    start_dir = f"\"{logged_in_home}/.local/share/Steam/steamapps/compatdata/{gamejolt_launcher}/pfx/drive_c/users/steamuser/AppData/Local/GameJoltClient\""

                    # Create the new entry (this is where you can use your custom function for Steam shortcuts)
                    create_new_entry(exe_path, display_name, launch_options, start_dir, 'Game Jolt Client')
                    track_game(display_name, "Game Jolt Client")
                    time.sleep(0.1)

            else:
                decky_plugin.logger.info("'objects' key not found in the games data.")

        except json.JSONDecodeError as e:
            decky_plugin.logger.info(f"Error decoding JSON: {e}")
        except FileNotFoundError as e:
            decky_plugin.logger.info(f"Error: File not found - {e}")
        except Exception as e:
            decky_plugin.logger.info(f"An error occurred: {e}")

    # End of Game Jolt Scanner
