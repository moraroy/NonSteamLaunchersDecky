import json
import os
import decky_plugin
from scanners.game_tracker import track_game

def indie_scanner(logged_in_home, indie_launcher, create_new_entry):
    real_indie_launcher_path = os.path.realpath(
        f"{logged_in_home}/.local/share/Steam/steamapps/compatdata/{indie_launcher}"
    )
    decky_plugin.logger.info(f"Resolved indie_launcher path: {real_indie_launcher_path}")

    installed_json_path = os.path.join(
        real_indie_launcher_path,
        "pfx/drive_c/users/steamuser/AppData/Roaming/IGClient/storage/installed.json"
    )
    default_install_path_file = os.path.join(
        real_indie_launcher_path,
        "pfx/drive_c/users/steamuser/AppData/Roaming/IGClient/storage/default-install-path.json"
    )

    def file_is_valid(file_path):
        return os.path.exists(file_path) and os.path.getsize(file_path) > 0

    def windows_to_linux_path(windows_path):
        linux_base = f"{logged_in_home}/.local/share/Steam/steamapps/compatdata/{indie_launcher}/pfx/drive_c/"
        if windows_path.startswith("C:/"):
            return linux_base + windows_path[3:].replace("\\", "/")
        return windows_path.replace("\\", "/")

    def find_exe_file(base_path, slugged_name, game_name):
        search_dir = os.path.join(base_path, slugged_name)
        if not os.path.exists(search_dir):
            decky_plugin.logger.warning(f"Game folder not found: {search_dir}")
            return None

        possible_names = [
            f"{game_name}.exe",
            f"{game_name.title().replace(' ', '')}.exe",
            f"{game_name.replace(' ', '')}.exe",
            f"{game_name.lower().replace(' ', '').replace('-', '')}.exe",
            f"{slugged_name}.exe",
            f"{slugged_name.replace('-', '')}.exe",
        ]

        for name in possible_names:
            full_path = windows_to_linux_path(os.path.join(search_dir, name))
            if os.path.exists(full_path):
                return full_path
        return None

    if not file_is_valid(installed_json_path) or not file_is_valid(default_install_path_file):
        decky_plugin.logger.warning("Required JSON files missing or empty. Skipping scan.")
        return

    with open(default_install_path_file, "r") as f:
        default_data = json.load(f)
        default_install_path = default_data if isinstance(default_data, str) else default_data.get("default-install-path", "C:/IGClientGames")
    default_install_path = windows_to_linux_path(default_install_path)

    with open(installed_json_path, "r") as f:
        data = json.load(f)

    for game_entry in data:
        game_data = game_entry["target"]["game_data"]
        game_info = game_entry["target"]["item_data"]

        game_name = game_info.get("name", "Unnamed Game")
        slugged_name = game_info.get("slugged_name", "missing-slug")
        location = windows_to_linux_path(game_entry.get("path", default_install_path))
        exe_path = game_data.get("exe_path")

        game_path = None

        if exe_path:
            guessed_path = windows_to_linux_path(os.path.join(location, exe_path))
            if os.path.exists(guessed_path):
                game_path = guessed_path
            else:
                parts = exe_path.replace("\\", "/").split("/")
                if len(parts) > 1:
                    parts[0] = slugged_name
                    alt_path = windows_to_linux_path(os.path.join(location, *parts))
                    if os.path.exists(alt_path):
                        game_path = alt_path
                    else:
                        decky_plugin.logger.info(f"Exe path invalid for {game_name}, trying fallback.")
                        game_path = find_exe_file(location, slugged_name, game_name)
                else:
                    game_path = find_exe_file(location, slugged_name, game_name)
        else:
            decky_plugin.logger.info(f"No exe_path for {game_name}, using fallback.")
            game_path = find_exe_file(location, slugged_name, game_name)

        if not game_path or not os.path.exists(game_path):
            decky_plugin.logger.warning(f"Skipping {game_name}: Executable not found.")
            continue

        start_dir = os.path.dirname(game_path)
        launchoptions = f'STEAM_COMPAT_DATA_PATH="{logged_in_home}/.local/share/Steam/steamapps/compatdata/{indie_launcher}/" %command%'
        create_new_entry(f"\"{game_path}\"", game_name, launchoptions, f"\"{start_dir}\"", "IndieGala Client")
        track_game(game_name, "IndieGala Client")
