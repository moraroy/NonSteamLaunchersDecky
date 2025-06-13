import os
import json
import decky_plugin
import time
from scanners.game_tracker import track_game


def minecraft_scanner(logged_in_home, minecraft_launcher, create_new_entry):
    # Path to the JSON file
    file_path = f"{logged_in_home}/.local/share/Steam/steamapps/compatdata/{minecraft_launcher}/pfx/drive_c/users/deck/AppData/Roaming/.minecraft/launcher_settings.json"

    # Function to convert Windows path to Unix path dynamically
    def convert_to_unix_path(windows_path, home_dir):
        unix_path = windows_path.replace('\\', '/')

        if len(windows_path) > 2 and windows_path[1] == ":":
            unix_path = unix_path[2:]
            unix_path = os.path.join(home_dir, unix_path.lstrip('/'))

        return unix_path

    # Check if the JSON file exists
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r') as file:
                # Parse the JSON data
                data = json.load(file)

                # Extract the productLibraryDir
                product_library_dir = data.get('productLibraryDir')

                if product_library_dir:
                    home_dir = os.path.expanduser("~")
                    unix_product_library_dir = convert_to_unix_path(product_library_dir, home_dir)

                    # Define the target file path
                    target_file = os.path.join(unix_product_library_dir, 'dungeons', 'dungeons', 'Dungeons.exe')

                    # Check if the file exists
                    if os.path.exists(target_file):
                        decky_plugin.logger.info(f"File exists: {target_file}")
                    else:
                        decky_plugin.logger.info(f"File does not exist: {target_file}")

                    # Set the display name to the game shortcut name from the JSON
                    display_name = "Minecraft Dungeons"
                    launch_options = f"STEAM_COMPAT_DATA_PATH=\"{logged_in_home}/.local/share/Steam/steamapps/compatdata/{minecraft_launcher}/\" %command%"
                    exe_path = f"\"{target_file}\""
                    start_dir = f"\"{os.path.dirname(target_file)}\""

                    # Create the new entry (this is where you can use your custom function for Steam shortcuts)
                    create_new_entry(exe_path, display_name, launch_options, start_dir, "Minecraft Launcher")
                    track_game(display_name, "Minecraft Launcher")
                    time.sleep(0.1)

                else:
                    decky_plugin.logger.info("Key 'productLibraryDir' not found in the JSON.")
        except json.JSONDecodeError:
            decky_plugin.logger.info("Error decoding the JSON file.")
    else:
        decky_plugin.logger.info("Skipping Minecraft Legacy Launcher Scanner")

# End of the Minecraft Legacy Launcher
