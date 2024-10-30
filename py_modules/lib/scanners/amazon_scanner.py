import os
import sqlite3
import decky_plugin
import platform

# Amazon Games Scanner

def get_amazon_games(sqllite_path, launcher_path):
    result = []
    connection = sqlite3.connect(sqllite_path)
    cursor = connection.cursor()
    cursor.execute("SELECT Id, ProductTitle FROM DbSet WHERE Installed = 1")
    for row in cursor.fetchall():
        id, title = row
        result.append({"id": id, "title": title, "launcher_path": launcher_path})
    return result

def convert_unix_to_windows_path(unix_path):
    return unix_path.replace('/c/', 'C:\\').replace('/', '\\')

def amazon_scanner(logged_in_home, amazon_launcher, create_new_entry):
    if platform.system() == "Windows":
        sqllite_path = convert_unix_to_windows_path(f"{logged_in_home}/AppData/Local/Amazon Games/Data/Games/Sql/GameInstallInfo.sqlite")
        launcher_path = convert_unix_to_windows_path(f"{logged_in_home}/AppData/Local/Amazon Games/App/Amazon Games.exe")
    else:
        sqllite_path = f"{logged_in_home}/.local/share/Steam/steamapps/compatdata/{amazon_launcher}/pfx/drive_c/users/steamuser/AppData/Local/Amazon Games/Data/Games/Sql/GameInstallInfo.sqlite"
        launcher_path = f"{logged_in_home}/.local/share/Steam/steamapps/compatdata/{amazon_launcher}/pfx/drive_c/users/steamuser/AppData/Local/Amazon Games/App/Amazon Games.exe"

    if not os.path.exists(sqllite_path) or not os.path.exists(launcher_path):
        decky_plugin.logger.info("Skipping Amazon Games Scanner due to missing paths.")
        return

    amazon_games = get_amazon_games(sqllite_path, launcher_path)
    if amazon_games:
        for game in amazon_games:
            display_name = game['title']
            if platform.system() == "Windows":
                exe_path = convert_unix_to_windows_path(f"{logged_in_home}/AppData/Local/Amazon Games/App/Amazon Games.exe")
                start_dir = convert_unix_to_windows_path(f"{logged_in_home}/AppData/Local/Amazon Games/App/")
                launch_options = f"-amazon-games://play/{game['id']}"
            else:
                exe_path = f"\"{logged_in_home}/.local/share/Steam/steamapps/compatdata/{amazon_launcher}/pfx/drive_c/users/steamuser/AppData/Local/Amazon Games/App/Amazon Games.exe\""
                start_dir = f"\"{logged_in_home}/.local/share/Steam/steamapps/compatdata/{amazon_launcher}/pfx/drive_c/users/steamuser/AppData/Local/Amazon Games/App/\""
                launch_options = f"STEAM_COMPAT_DATA_PATH=\"{logged_in_home}/.local/share/Steam/steamapps/compatdata/{amazon_launcher}/\" %command% -'amazon-games://play/{game['id']}'"
            
            create_new_entry(exe_path, display_name, launch_options, start_dir, "Amazon Games")

# End of Amazon Games Scanner
