import os
import sqlite3
import decky_plugin
import platform
import time

from scanners.game_tracker import track_game


def itchio_games_scanner(logged_in_home, itchio_launcher, create_new_entry):
    is_windows = platform.system() == "Windows"

    if is_windows:
        itch_db_location = (
            f"{logged_in_home}\\AppData\\Roaming\\itch\\db\\butler.db"
        )

        itch_setup_path = (
            f"{logged_in_home}\\AppData\\Local\\itch\\itch-setup.exe"
        )

        start_dir = (
            f'"{itch_setup_path.rsplit(chr(92), 1)[0]}"'
        )

    else:
        compat_data_path = (
            f"{logged_in_home}/.local/share/Steam/steamapps/"
            f"compatdata/{itchio_launcher}"
        )

        itch_db_location = (
            f"{compat_data_path}/pfx/drive_c/users/steamuser/"
            f"AppData/Roaming/itch/db/butler.db"
        )

        itch_setup_path = (
            f"{compat_data_path}/pfx/drive_c/users/steamuser/"
            f"AppData/Local/itch/itch-setup.exe"
        )

        start_dir = f'"{itch_setup_path.rsplit("/", 1)[0]}"'

    if not os.path.isfile(itch_db_location):
        decky_plugin.logger.info(
            f"Path not found: {itch_db_location}. "
            "Aborting Itch.io scan..."
        )
        return

    if not os.path.isfile(itch_setup_path):
        decky_plugin.logger.warning(
            f"Itch launcher executable not found: {itch_setup_path}. "
            "Aborting Itch.io scan..."
        )
        return

    itchgames = []
    conn = None

    try:
        conn = sqlite3.connect(itch_db_location)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM caves;")
        caves = cursor.fetchall()

        cursor.execute("SELECT * FROM games;")
        games = cursor.fetchall()

        games_dict = {
            game[0]: game
            for game in games
            if len(game) >= 3
        }

        seen_game_ids = set()

        for cave in caves:
            if len(cave) < 2:
                continue

            game_id = cave[1]

            if game_id not in games_dict:
                continue

            if game_id in seen_game_ids:
                continue

            game_title = games_dict[game_id][2]

            seen_game_ids.add(game_id)
            itchgames.append((game_id, game_title))

        decky_plugin.logger.info(
            f"Found {len(itchgames)} Itch.io games."
        )

    except sqlite3.Error as error:
        decky_plugin.logger.error(
            f"Failed to read Itch.io database: {error}"
        )
        return

    finally:
        if conn is not None:
            conn.close()

    exe_path = f'"{itch_setup_path}"'

    launch_prefix = ""

    if not is_windows:
        launch_prefix = (
            f'STEAM_COMPAT_DATA_PATH="{compat_data_path}/" '
        )

    for game_id, game_title in itchgames:
        if is_windows:
            launchoptions = (
                f"--appname itch --run-game {game_id}"
            )
        else:
            launchoptions = (
                f"{launch_prefix}%command% "
                f"--appname itch --run-game {game_id}"
            )

        try:
            create_new_entry(
                exe_path,
                game_title,
                launchoptions,
                start_dir,
                "itch.io"
            )

            track_game(game_title, "itch.io")

            decky_plugin.logger.info(
                f"Added Itch.io shortcut: {game_title} "
                f"(ID: {game_id})"
            )

        except Exception as error:
            decky_plugin.logger.error(
                f"Failed to create Itch.io shortcut for "
                f"{game_title}: {error}"
            )

        time.sleep(0.1)