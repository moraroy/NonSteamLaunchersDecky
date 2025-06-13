import gzip
import os
import json
import sqlite3
import decky_plugin
import platform
import time
from scanners.game_tracker import track_game


def convert_unix_to_windows_path(unix_path):
    return unix_path.replace('/c/', 'C:\\').replace('/', '\\')


def itchio_games_scanner(logged_in_home, itchio_launcher, create_new_entry):
    if platform.system() == "Windows":
        itch_db_location = convert_unix_to_windows_path(f"{logged_in_home}\\AppData\\Roaming\\itch\\db\\butler.db")
    else:
        itch_db_location = os.path.join(logged_in_home, ".local", "share", "Steam", "steamapps", "compatdata", itchio_launcher, "pfx", "drive_c", "users", "steamuser", "AppData", "Roaming", "itch", "db", "butler.db")

    if not os.path.exists(itch_db_location):
        decky_plugin.logger.info(f"Path not found: {itch_db_location}. Aborting Itch.io scan...")
        return

    conn = sqlite3.connect(itch_db_location)
    cursor = conn.cursor()

    # Parse the 'caves' table
    cursor.execute("SELECT * FROM caves;")
    caves = cursor.fetchall()

    # Parse the 'games' table
    cursor.execute("SELECT * FROM games;")
    games = cursor.fetchall()

    # Create a dictionary to store game information
    games_dict = {game[0]: game for game in games}

    # Match game_id between 'caves' and 'games' tables
    itchgames = []
    for cave in caves:
        game_id = cave[1]
        if game_id in games_dict:
            game_info = games_dict[game_id]
            base_path = json.loads(cave[11])['basePath']
            candidates = json.loads(cave[11])['candidates']

            # Check if 'candidates' is not None and has at least one element
            if candidates and isinstance(candidates, list) and len(candidates) > 0:
                executable_path = candidates[0].get('path')  # Use `.get()` to avoid KeyError
                if executable_path and executable_path.endswith('.html'):
                    decky_plugin.logger.info(f"Skipping browser game: {game_info[2]}")
                    continue
                game_title = game_info[2]
                itchgames.append((base_path, executable_path, game_title))
            else:
                decky_plugin.logger.warning(f"No candidates found for game: {game_info[2]}")

    for game in itchgames:
        base_path, executable, game_title = game
        if platform.system() == "Windows":
            exe_path = os.path.join(base_path, executable)
            start_dir = base_path
            launchoptions = ""
        else:
            base_path_linux = base_path.replace("C:\\", logged_in_home + "/.local/share/Steam/steamapps/compatdata/" + itchio_launcher + "/pfx/drive_c/").replace("\\", "/")
            exe_path = "\"" + os.path.join(base_path_linux, executable).replace("\\", "/") + "\""
            start_dir = "\"" + base_path_linux + "\""
            launchoptions = "STEAM_COMPAT_DATA_PATH=\"" + logged_in_home + "/.local/share/Steam/steamapps/compatdata/" + itchio_launcher + "/\" %command%"
        create_new_entry(exe_path, game_title, launchoptions, start_dir, "itch.io")
        track_game(game_title, "itch.io")
        time.sleep(0.1)

    conn.close()


# End of Itchio Scanner
