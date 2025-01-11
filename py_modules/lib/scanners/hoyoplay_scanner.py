import decky_plugin
import os
import json

def hoyoplay_scanner(logged_in_home, hoyoplay_launcher, create_new_entry):
    # Path to the HoYoPlay data file
    file_path = f"{logged_in_home}/.local/share/Steam/steamapps/compatdata/{hoyoplay_launcher}/pfx/drive_c/users/steamuser/AppData/Roaming/Cognosphere/HYP/1_0/data/gamedata.dat"

    # Check if the file exists
    if not os.path.exists(file_path):
        decky_plugin.logger.info("Skipping HoYoPlay Scanner - File not found.")
        return

    # Read the file with ISO-8859-1 encoding
    try:
        with open(file_path, 'r', encoding='ISO-8859-1') as file:
            file_content = file.read()
    except Exception as e:
        decky_plugin.logger.error(f"Error reading file {file_path}: {e}")
        return

    # Function to manually extract JSON-like objects by finding balanced braces
    def extract_json_objects(content):
        objects = []
        brace_count = 0
        json_start = None

        for i, char in enumerate(content):
            if char == '{':
                if brace_count == 0:
                    json_start = i  # Mark the start of a JSON object
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    json_object = content[json_start:i+1]  # Extract the full JSON object
                    objects.append(json_object)
                    json_start = None

        return objects

    # Extract JSON objects from the file content
    json_objects = extract_json_objects(file_content)

    # Create a set to track seen gameBiz values and avoid duplicates
    seen_game_biz = set()

    # Parse each JSON object
    for json_object in json_objects:
        json_object = json_object.strip()

        # Skip empty JSON objects
        if json_object == "{}":
            continue

        if json_object:
            try:
                # Attempt to load the JSON object
                data = json.loads(json_object)

                # Extract gameBiz from the root and from the 'gameInstallStatus' object
                game_biz = data.get("gameBiz", "").strip()

                # If gameBiz is empty, check inside the 'gameInstallStatus' object
                if not game_biz:
                    game_biz = data.get("gameInstallStatus", {}).get("gameBiz", "").strip()

                # Skip JSON objects where gameBiz is empty or already processed
                if not game_biz or game_biz in seen_game_biz:
                    continue  # Skip this object and move to the next one

                # Add this gameBiz to the seen set
                seen_game_biz.add(game_biz)

                # Extract other relevant fields
                persistent_install_path = data.get("persistentInstallPath", None)
                game_install_status = data.get("gameInstallStatus", {})

                game_exe_name = game_install_status.get("gameExeName", None)
                install_path = game_install_status.get("gameInstallPath", None)
                game_shortcut_name = data.get("gameShortcutName", None)  # Get the game shortcut name

                # Check if all important fields are missing or empty
                if not game_exe_name and not install_path and not persistent_install_path:
                    decky_plugin.logger.info(f"Skipping empty game entry for gameBiz: {game_biz}")
                    continue  # Skip if all important fields are empty

                if not persistent_install_path:
                    decky_plugin.logger.info(f"Skipping gameBiz: {game_biz} - No persistent install path found.")
                    continue  # Skip if no persistent install path

                if game_shortcut_name:
                    decky_plugin.logger.info(f"  Game Shortcut Name: {game_shortcut_name}")

                # Set the display name to the game shortcut name from the JSON
                display_name = game_shortcut_name if game_shortcut_name else game_biz
                launch_options = f"STEAM_COMPAT_DATA_PATH=\"{logged_in_home}/.local/share/Steam/steamapps/compatdata/{hoyoplay_launcher}/\" %command% \"--game={game_biz}\""
                exe_path = f"\"{logged_in_home}/.local/share/Steam/steamapps/compatdata/{hoyoplay_launcher}/pfx/drive_c/Program Files/HoYoPlay/launcher.exe\""
                start_dir = f"\"{logged_in_home}/.local/share/Steam/steamapps/compatdata/{hoyoplay_launcher}/pfx/drive_c/Program Files/HoYoPlay\""

                # Ensure that create_new_entry does not throw errors on missing fields
                if any(v is None for v in [exe_path, display_name, launch_options, start_dir]):
                    decky_plugin.logger.warning(f"Missing fields for gameBiz: {game_biz}, skipping entry creation.")
                    continue  # Skip this entry if essential fields are missing

                # Create the new entry (this is where you can use your custom function for Steam shortcuts)
                create_new_entry(exe_path, display_name, launch_options, start_dir, "HoYoPlay")

            except json.JSONDecodeError as e:
                decky_plugin.logger.info(f"Error decoding JSON: {e}")
                decky_plugin.logger.info(f"Problematic JSON content (first 200 chars): {json_object[:200]}")
            except Exception as e:
                decky_plugin.logger.error(f"Unexpected error while processing JSON: {e}")
