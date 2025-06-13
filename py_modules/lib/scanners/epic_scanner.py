import os
import json
import decky_plugin
import platform
import time
from scanners.game_tracker import track_game


def epic_games_scanner(logged_in_home, epic_games_launcher, create_new_entry):
    if platform.system() == "Windows":
        item_dir = r"C:\ProgramData\Epic\EpicGamesLauncher\Data\Manifests"
        dat_file_path = r"C:\ProgramData\Epic\UnrealEngineLauncher\LauncherInstalled.dat"
        exe_template = r"C:\Program Files (x86)\Epic Games\Launcher\Portal\Binaries\Win32\EpicGamesLauncher.exe"
        start_dir_template = r"C:\Program Files (x86)\Epic Games\Launcher\Portal\Binaries\Win32"
        launch_options_template = "-'com.epicgames.launcher://apps/{app_name}?action=launch&silent=true'"
    else:
        item_dir = f"{logged_in_home}/.local/share/Steam/steamapps/compatdata/{epic_games_launcher}/pfx/drive_c/ProgramData/Epic/EpicGamesLauncher/Data/Manifests/"
        dat_file_path = f"{logged_in_home}/.local/share/Steam/steamapps/compatdata/{epic_games_launcher}/pfx/drive_c/ProgramData/Epic/UnrealEngineLauncher/LauncherInstalled.dat"
        exe_template = f"\"{logged_in_home}/.local/share/Steam/steamapps/compatdata/{epic_games_launcher}/pfx/drive_c/Program Files (x86)/Epic Games/Launcher/Portal/Binaries/Win32/EpicGamesLauncher.exe\""
        start_dir_template = f"\"{logged_in_home}/.local/share/Steam/steamapps/compatdata/{epic_games_launcher}/pfx/drive_c/Program Files (x86)/Epic Games/Launcher/Portal/Binaries/Win32/\""
        launch_options_template = f"STEAM_COMPAT_DATA_PATH=\"{logged_in_home}/.local/share/Steam/steamapps/compatdata/{epic_games_launcher}/\" %command% -'com.epicgames.launcher://apps/{{app_name}}?action=launch&silent=true'"

    if os.path.exists(dat_file_path) and os.path.exists(item_dir):
        with open(dat_file_path, 'r') as file:
            dat_data = json.load(file)

        # Epic Game Scanner
        for item_file in os.listdir(item_dir):
            if item_file.endswith('.item'):

                time.sleep(0.1)
                with open(os.path.join(item_dir, item_file), 'r') as file:
                    item_data = json.load(file)

                # Initialize variables
                display_name = item_data['DisplayName']
                app_name = item_data['AppName']
                exe_path = exe_template
                start_dir = start_dir_template
                launch_options = launch_options_template.format(app_name=app_name)

                # Check if the game is still installed and if the LaunchExecutable is valid, not content-related, and is a .exe file
                if item_data['LaunchExecutable'].endswith('.exe') and "Content" not in item_data['DisplayName'] and "Content" not in item_data['InstallLocation']:
                    for game in dat_data['InstallationList']:
                        if game['AppName'] == item_data['AppName']:
                            create_new_entry(exe_path, display_name, launch_options, start_dir, "Epic Games")
                            track_game(display_name, "Epic Games")


    else:
        decky_plugin.logger.info("Epic Games Launcher data not found. Skipping scanning for installed Epic Games.")
