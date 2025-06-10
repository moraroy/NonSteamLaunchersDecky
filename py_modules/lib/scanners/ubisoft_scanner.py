import os
import re
import decky_plugin
import platform
from scanners.game_tracker import track_game


# Conditionally import winreg for Windows
if platform.system() == "Windows":
    import winreg

# Ubisoft Connect Scanner
def getUplayGameInfo(folderPath, filePath):
    # Get the game IDs from the folder
    listOfFiles = os.listdir(folderPath)
    uplay_ids = [re.findall(r'\d+', str(entry))[0] for entry in listOfFiles if re.findall(r'\d+', str(entry))]

    # Parse the registry file
    game_dict = {}
    with open(filePath, 'r') as file:
        uplay_id = None
        game_name = None
        uplay_install_found = False
        for line in file:
            line = line.replace("\\x2019", "’")
            if "Uplay Install" in line:
                uplay_id = re.findall(r'Uplay Install (\d+)', line)
                if uplay_id:
                    uplay_id = uplay_id[0]
                game_name = None  # Reset game_name
                uplay_install_found = True
            if "DisplayName" in line and uplay_install_found:
                game_name = re.findall(r'\"(.+?)\"', line.split("=")[1])
                if game_name:
                    game_name = game_name[0]
                uplay_install_found = False
            if uplay_id and game_name and uplay_id in uplay_ids:
                game_dict[game_name] = uplay_id
                uplay_id = None  # Reset uplay_id
                game_name = None  # Reset game_name

    return game_dict

def getUplayGameInfoWindows():
    game_dict = {}
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Ubisoft\Launcher\Installs") as key:
            i = 0
            while True:
                try:
                    subkey_name = winreg.EnumKey(key, i)
                    with winreg.OpenKey(key, subkey_name) as subkey:
                        uplay_id = subkey_name
                        try:
                            game_name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                        except FileNotFoundError:
                            game_name = os.path.basename(winreg.QueryValueEx(subkey, "InstallDir")[0])
                        game_dict[game_name] = uplay_id
                    i += 1
                except OSError:
                    break
    except OSError:
        decky_plugin.logger.info("No Ubisoft Connect entries found in the Windows registry. Skipping Ubisoft Games Scanner.")
    return game_dict

def ubisoft_scanner(logged_in_home, ubisoft_connect_launcher, create_new_entry):
    game_dict = {}  # Initialize game_dict to avoid uninitialized variable error

    if platform.system() == "Windows":
        data_folder_path = "C:\\Program Files (x86)\\Ubisoft\\Ubisoft Game Launcher\\data"
        registry_file_path = None  # Not needed for Windows
        if not os.path.exists(data_folder_path):
            decky_plugin.logger.info("Ubisoft Connect game data not found. Skipping Ubisoft Games Scanner.")
        else:
            game_dict = getUplayGameInfoWindows()
    else:
        data_folder_path = f"{logged_in_home}/.local/share/Steam/steamapps/compatdata/{ubisoft_connect_launcher}/pfx/drive_c/Program Files (x86)/Ubisoft/Ubisoft Game Launcher/data/"
        registry_file_path = f"{logged_in_home}/.local/share/Steam/steamapps/compatdata/{ubisoft_connect_launcher}/pfx/system.reg"
        if not os.path.exists(data_folder_path) or (registry_file_path and not os.path.exists(registry_file_path)):
            decky_plugin.logger.info("Ubisoft Connect game data not found. Skipping Ubisoft Games Scanner.")
        else:
            game_dict = getUplayGameInfo(data_folder_path, registry_file_path)

    for game, uplay_id in game_dict.items():
        if uplay_id:
            if platform.system() == "Windows":
                launch_options = f"uplay://launch/{uplay_id}/0"
                exe_path = "C:\\Program Files (x86)\\Ubisoft\\Ubisoft Game Launcher\\upc.exe"
                start_dir = "C:\\Program Files (x86)\\Ubisoft\\Ubisoft Game Launcher"
            else:
                launch_options = f"STEAM_COMPAT_DATA_PATH=\"{logged_in_home}/.local/share/Steam/steamapps/compatdata/{ubisoft_connect_launcher}/\" %command% \"uplay://launch/{uplay_id}/0\""
                exe_path = f"\"{logged_in_home}/.local/share/Steam/steamapps/compatdata/{ubisoft_connect_launcher}/pfx/drive_c/Program Files (x86)/Ubisoft/Ubisoft Game Launcher/upc.exe\""
                start_dir = f"\"{logged_in_home}/.local/share/Steam/steamapps/compatdata/{ubisoft_connect_launcher}/pfx/drive_c/Program Files (x86)/Ubisoft/Ubisoft Game Launcher/\""
            create_new_entry(exe_path, game, launch_options, start_dir, "Ubisoft Connect")
            track_game(game, "Ubisoft Connect")

# End of Ubisoft Game Scanner
