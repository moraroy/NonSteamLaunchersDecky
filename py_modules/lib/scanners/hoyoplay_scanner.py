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
                    json_start = i
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    json_object = content[json_start:i+1]
                    objects.append(json_object)
                    json_start = None

        return objects

    # Extract JSON objects from the file content
    json_objects = extract_json_objects(file_content)

    seen_game_biz = set()

    for json_object in json_objects:
        json_object = json_object.strip()
        if json_object == "{}":
            continue

        if json_object:
            try:
                data = json.loads(json_object)

                game_biz = data.get("gameBiz", "").strip()
                if not game_biz:
                    game_biz = data.get("gameInstallStatus", {}).get("gameBiz", "").strip()

                if not game_biz or game_biz in seen_game_biz:
                    continue

                seen_game_biz.add(game_biz)

                persistent_install_path = data.get("persistentInstallPath", None)
                game_install_status = data.get("gameInstallStatus", {})
                game_exe_name = game_install_status.get("gameExeName", None)
                install_path = game_install_status.get("gameInstallPath", None)
                game_shortcut_name = data.get("gameShortcutName", None)

                if not persistent_install_path:
                    decky_plugin.logger.info(f"Persistent Install Path is empty for gameBiz: {game_biz}, using Install Path as fallback.")
                    persistent_install_path = install_path

                if not game_exe_name or not persistent_install_path:
                    decky_plugin.logger.info(f"Skipping gameBiz: {game_biz} - Missing exe name or install path.")
                    continue

                # Convert Windows-style path to Steam Proton path
                proton_path_base = f"{logged_in_home}/.local/share/Steam/steamapps/compatdata/{hoyoplay_launcher}/pfx/drive_c"
                relative_game_path = persistent_install_path.replace("C:\\", "").replace("\\", "/")
                full_game_dir = os.path.join(proton_path_base, relative_game_path)
                full_game_exe = os.path.join(full_game_dir, game_exe_name)

                # Log information for debugging
                decky_plugin.logger.info(f"  Game Business: {game_biz}")
                decky_plugin.logger.info(f"  Game Shortcut Name: {game_shortcut_name}")
                decky_plugin.logger.info(f"  Game Executable: {game_exe_name}")
                decky_plugin.logger.info(f"  Persistent Install Path: {persistent_install_path}")

                display_name = game_shortcut_name if game_shortcut_name else game_biz
                launch_options = f"STEAM_COMPAT_DATA_PATH=\"{logged_in_home}/.local/share/Steam/steamapps/compatdata/{hoyoplay_launcher}/\" %command% \"--game={game_biz}\""
                exe_path = f"\"{full_game_exe}\""
                start_dir = f"\"{full_game_dir}\""

                if any(v is None for v in [exe_path, display_name, launch_options, start_dir]):
                    decky_plugin.logger.warning(f"Missing fields for gameBiz: {game_biz}, skipping entry creation.")
                    continue

                # Create the new Steam shortcut entry
                create_new_entry(exe_path, display_name, launch_options, start_dir, "HoYoPlay")

            except json.JSONDecodeError as e:
                decky_plugin.logger.info(f"Error decoding JSON: {e}")
                decky_plugin.logger.info(f"Problematic JSON content (first 200 chars): {json_object[:200]}")
            except Exception as e:
                decky_plugin.logger.error(f"Unexpected error while processing JSON: {e}")
