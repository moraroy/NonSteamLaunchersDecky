import os
import re
import decky_plugin
import platform
from scanners.game_tracker import track_game

# Gog Galaxy Scanner
def getGogGameInfo(filePath):
    # Check if the file contains any GOG entries
    with open(filePath, 'r') as file:
        if "GOG.com" not in file.read():
            decky_plugin.logger.info("No GOG entries found in the registry file. Skipping GOG Galaxy Games Scanner.")
            return {}

    # If GOG entries exist, parse the registry file
    game_dict = {}
    with open(filePath, 'r') as file:
        game_id = None
        game_name = None
        exe_path = None
        depends_on = None
        launch_command = None
        start_menu_link = None
        gog_entry = False
        for line in file:
            split_line = line.split("=")
            if len(split_line) > 1:
                if "gameid" in line.lower():
                    game_id = re.findall(r'\"(.+?)\"', split_line[1])
                    if game_id:
                        game_id = game_id[0]
                if "gamename" in line.lower():
                    game_name = re.findall(r'\"(.+?)\"', split_line[1])
                    if game_name:
                        game_name = bytes(game_name[0], 'utf-8').decode('unicode_escape')
                        game_name = game_name.replace('!22', '™')
                if "exe" in line.lower() and not "unins000.exe" in line.lower():
                    exe_path = re.findall(r'\"(.+?)\"', split_line[1])
                    if exe_path:
                        exe_path = exe_path[0].replace('\\\\', '\\')
                if "dependson" in line.lower():
                    depends_on = re.findall(r'\"(.+?)\"', split_line[1])
                    if depends_on:
                        depends_on = depends_on[0]
                if "launchcommand" in line.lower():
                    launch_command = re.findall(r'\"(.+?)\"', split_line[1])
                    if launch_command:
                        launch_command = launch_command[0]
            if game_id and game_name and launch_command:
                game_dict[game_name] = {'id': game_id, 'exe': exe_path}
                game_id = None
                game_name = None
                exe_path = None
                depends_on = None
                launch_command = None

    return game_dict

def getGogGameInfoWindows():
    if platform.system() == "Windows":
        import winreg

        game_dict = {}
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\GOG.com\Games")
            i = 0
            while True:
                try:
                    subkey_name = winreg.EnumKey(key, i)
                    subkey = winreg.OpenKey(key, subkey_name)
                    game_id = subkey_name
                    game_name, _ = winreg.QueryValueEx(subkey, "gameName")
                    exe_path, _ = winreg.QueryValueEx(subkey, "exe")

                    try:
                        launch_params, _ = winreg.QueryValueEx(subkey, "launchParam")  # Changed to launchParam
                    except FileNotFoundError:
                        launch_params = None  # If not found, set as None

                    game_dict[game_name] = {'id': game_id, 'exe': exe_path, 'launchParams': launch_params}
                    i += 1
                except OSError:
                    break
        except OSError:
            decky_plugin.logger.info("No GOG entries found in the Windows registry. Skipping GOG Galaxy Games Scanner.")

        return game_dict
    else:

        return {}

def adjust_dosbox_launch_options(launch_command, game_id, logged_in_home, gog_galaxy_launcher, is_windows, launch_params=None):
    print(f"Adjusting launch options for command: {launch_command}")

    if "dosbox.exe" in launch_command.lower():
        try:
            # Find the part of the command with DOSBox.exe and its arguments
            exe_part, args_part = launch_command.split("DOSBox.exe", 1)
            exe_path = exe_part.strip() + "DOSBox.exe"
            args = args_part.strip()

            # If there are launch parameters from the registry, append them to args
            if launch_params:
                # Ensure launchParams is not empty before appending
                launch_params = launch_params.strip()
                if launch_params:
                    args = f"{args} {launch_params}".strip()

            # Form the launch options string
            if is_windows:
                launch_options = f'/command=runGame /gameId={game_id} /path="{exe_path}" "{args}"'
            else:
                launch_options = f'STEAM_COMPAT_DATA_PATH="{logged_in_home}/.local/share/Steam/steamapps/compatdata/{gog_galaxy_launcher}/" %command% /command=runGame /gameId={game_id} /path="{exe_path}" "{args}"'

            return launch_options
        except ValueError as e:
            print(f"Error adjusting launch options: {e}")
            return launch_command
    else:
        # For non-DOSBox games, return the original launch command without trailing spaces
        launch_command = launch_command.strip()
        if is_windows:
            return f'/command=runGame /gameId={game_id} /path="{launch_command}"'
        else:
            return f'STEAM_COMPAT_DATA_PATH="{logged_in_home}/.local/share/Steam/steamapps/compatdata/{gog_galaxy_launcher}/" %command% /command=runGame /gameId={game_id} /path="{launch_command}"'

def gog_scanner(logged_in_home, gog_galaxy_launcher, create_new_entry):
    if platform.system() == "Windows":
        game_dict = getGogGameInfoWindows()
        exe_template = r"C:\Program Files (x86)\GOG Galaxy\GalaxyClient.exe"
        start_dir_template = r"C:\Program Files (x86)\GOG Galaxy"
        is_windows = True
    else:
        registry_file_path = f"{logged_in_home}/.local/share/Steam/steamapps/compatdata/{gog_galaxy_launcher}/pfx/system.reg"
        if not os.path.exists(registry_file_path):
            decky_plugin.logger.info(f"Registry file not found: {registry_file_path}. Skipping GOG Galaxy Games Scanner.")
            return  # Skip the scanner if the registry file doesn't exist on Linux

        game_dict = getGogGameInfo(registry_file_path)
        exe_template = f"\"{logged_in_home}/.local/share/Steam/steamapps/compatdata/{gog_galaxy_launcher}/pfx/drive_c/Program Files (x86)/GOG Galaxy/GalaxyClient.exe\""
        start_dir_template = f"\"{logged_in_home}/.local/share/Steam/steamapps/compatdata/{gog_galaxy_launcher}/pfx/drive_c/Program Files (x86)/GOG Galaxy/\""
        is_windows = False

    for game, game_info in game_dict.items():
        if game_info['id']:
            exe_path = game_info['exe'].strip()
            # Fetch the launch parameters from the registry (if they exist)
            launch_params = game_info.get('launchParams', None)
            # Adjust the launch options based on DOSBox and launchParams
            launch_options = adjust_dosbox_launch_options(game_info['exe'], game_info['id'], logged_in_home, gog_galaxy_launcher, is_windows, launch_params)
            exe_path = exe_template
            start_dir = start_dir_template
            create_new_entry(exe_path, game, launch_options, start_dir, "GOG Galaxy")
            track_game(game, "GOG Galaxy")

# End of Gog Galaxy Scanner
