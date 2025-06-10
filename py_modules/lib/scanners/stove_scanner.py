import json
import os
import glob
import decky_plugin
from scanners.game_tracker import track_game

def stove_scanner(logged_in_home, stove_launcher, create_new_entry):
    # STOVE Client Scanner
    steam_compat_base = f"{logged_in_home}/.local/share/Steam/steamapps/compatdata/{stove_launcher}"
    stove_launcher_path = os.path.join(steam_compat_base, "pfx/drive_c/ProgramData/Smilegate/STOVE/STOVE.exe")
    client_config_path = os.path.join(steam_compat_base, "pfx/drive_c/users/steamuser/AppData/Local/STOVE/Config/ClientConfig.json")

    if not os.path.isfile(client_config_path):
        decky_plugin.logger.info(f"Skipping STOVE Scanner: ClientConfig.json not found at {client_config_path}")
        return

    with open(client_config_path, "r", encoding="utf-8") as f:
        client_config = json.load(f)

    win_games_dir = client_config.get("defaultPath", "")
    if not win_games_dir:
        decky_plugin.logger.info("No defaultPath found in ClientConfig.json")
        return

    linux_games_dir = win_games_dir.replace("C:\\", f"{steam_compat_base}/pfx/drive_c/").replace("\\", "/")
    if not os.path.isdir(linux_games_dir):
        decky_plugin.logger.info(f"Games directory not found at {linux_games_dir}")
        return

    search_pattern = os.path.join(linux_games_dir, "*/combinedata_manifest/GameManifest_*.upf")
    manifest_files = glob.glob(search_pattern)

    if not manifest_files:
        decky_plugin.logger.info("No game manifest files found")
        return

    for manifest_path in manifest_files:
        try:
            with open(manifest_path, "r", encoding="utf-8") as mf:
                game_data = json.load(mf)

            game_id = game_data.get("game_id")
            game_title = game_data.get("game_title", game_id)

            if not game_id:
                decky_plugin.logger.info(f"Missing game_id in manifest: {manifest_path}")
                continue

            launch_options = f'STEAM_COMPAT_DATA_PATH="{steam_compat_base}/" %command% "sgup://run/{game_id}"'

            create_new_entry(
                f'"{stove_launcher_path}"',
                game_title,
                launch_options,
                f'"{os.path.dirname(stove_launcher_path)}"',
                "STOVE Client"
            )
            track_game(game_title, "STOVE Client")

        except Exception as e:
            decky_plugin.logger.info(f"Error reading manifest {manifest_path}: {e}")
