import os
import json
import decky_plugin
import platform
from scanners.game_tracker import track_game


def epic_games_scanner(logged_in_home, epic_games_launcher, create_new_entry):
    if platform.system() == "Windows":
        item_dir = r"C:\ProgramData\Epic\EpicGamesLauncher\Data\Manifests"
        exe_template = r"C:\Program Files\Epic Games\Launcher\Portal\Binaries\Win64\EpicGamesLauncher.exe"
        start_dir_template = r"C:\Program Files\Epic Games\Launcher\Portal\Binaries\Win64"
        launch_options_template = "-'com.epicgames.launcher://apps/{app_name}?action=launch&silent=true'"
    else:
        item_dir = f"{logged_in_home}/.local/share/Steam/steamapps/compatdata/{epic_games_launcher}/pfx/drive_c/ProgramData/Epic/EpicGamesLauncher/Data/Manifests/"
        exe_template = f"\"{logged_in_home}/.local/share/Steam/steamapps/compatdata/{epic_games_launcher}/pfx/drive_c/Program Files/Epic Games/Launcher/Portal/Binaries/Win64/EpicGamesLauncher.exe\""
        start_dir_template = f"\"{logged_in_home}/.local/share/Steam/steamapps/compatdata/{epic_games_launcher}/pfx/drive_c/Program Files/Epic Games/Launcher/Portal/Binaries/Win64/\""
        launch_options_template = f"STEAM_COMPAT_DATA_PATH=\"{logged_in_home}/.local/share/Steam/steamapps/compatdata/{epic_games_launcher}/\" %command% -'com.epicgames.launcher://apps/{{app_name}}?action=launch&silent=true'"

    if os.path.exists(item_dir):
        # Epic Game Scanner
        for item_file in os.listdir(item_dir):
            if not item_file.endswith('.item'):
                continue

            item_path = os.path.join(item_dir, item_file)

            try:
                with open(item_path, 'r') as file:
                    item_data = json.load(file)
            except (OSError, json.JSONDecodeError) as e:
                decky_plugin.logger.warning(
                    f"Failed to read Epic manifest {item_file}: {e}"
                )
                continue

            display_name = item_data.get('DisplayName', '')
            app_name = item_data.get('AppName', '')
            launch_executable = item_data.get('LaunchExecutable', '')
            install_location = item_data.get('InstallLocation', '')

            # Only use the manifest itself to determine installed games.
            if (
                launch_executable.lower().endswith('.exe')
                and "Content" not in display_name
                and "Content" not in install_location
            ):
                exe_path = exe_template
                start_dir = start_dir_template
                launch_options = launch_options_template.format(app_name=app_name)

                create_new_entry(
                    exe_path,
                    display_name,
                    launch_options,
                    start_dir,
                    "Epic Games"
                )
                track_game(display_name, "Epic Games")

    else:
        decky_plugin.logger.info(
            "Epic Games Launcher manifests not found. "
            "Skipping scanning for installed Epic Games."
        )
