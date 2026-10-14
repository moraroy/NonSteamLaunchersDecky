
import os
import sqlite3
import decky_plugin
import platform
import time

from scanners.game_tracker import track_game


def itchio_games_scanner(logged_in_home, itchio_launcher, create_new_entry):
    is_windows = platform.system() == "Windows"

    # Set up the Itch database and launcher paths.
    if is_windows:
        itch_db_location = os.path.join(
            logged_in_home,
            "AppData",
            "Roaming",
            "itch",
            "db",
            "butler.db"
        )

        itch_setup_path = os.path.join(
            logged_in_home,
            "AppData",
            "Local",
            "itch",
            "itch-setup.exe"
        )

    else:
        compat_data_path = os.path.join(
            logged_in_home,
            ".local",
            "share",
            "Steam",
            "steamapps",
            "compatdata",
            str(itchio_launcher)
        )

        itch_db_location = os.path.join(
            compat_data_path,
            "pfx",
            "drive_c",
            "users",
            "steamuser",
            "AppData",
            "Roaming",
            "itch",
            "db",
            "butler.db"
        )

        itch_setup_path = os.path.join(
            compat_data_path,
            "pfx",
            "drive_c",
            "users",
            "steamuser",
            "AppData",
            "Local",
            "itch",
            "itch-setup.exe"
        )

    # Verify that the Itch database exists.
    if not os.path.isfile(itch_db_location):
        decky_plugin.logger.info(
            f"Path not found: {itch_db_location}. "
            "Aborting Itch.io scan..."
        )
        return

    # Verify that the Itch launcher executable exists.
    if not os.path.isfile(itch_setup_path):
        decky_plugin.logger.warning(
            f"Itch launcher executable not found: {itch_setup_path}. "
            "Aborting Itch.io scan..."
        )
        return

    # Collect installed Itch.io games.
    itchgames = []
    conn = None

    try:
        # Connect to the Butler database.
        conn = sqlite3.connect(itch_db_location)
        cursor = conn.cursor()

        # Fetch installed caves.
        cursor.execute("SELECT * FROM caves;")
        caves = cursor.fetchall()

        # Fetch game metadata.
        cursor.execute("SELECT * FROM games;")
        games = cursor.fetchall()

        # Index games by their game ID.
        games_dict = {
            game[0]: game
            for game in games
            if len(game) >= 3
        }

        # Match cave records to games and avoid duplicate IDs.
        seen_game_ids = set()

        for cave in caves:
            if len(cave) < 2:
                continue

            game_id = cave[1]

            if game_id not in games_dict:
                continue

            game_info = games_dict[game_id]
            game_title = game_info[2]

            if game_id in seen_game_ids:
                continue

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
        # Always close the database connection.
        if conn is not None:
            conn.close()

    # Configure the shortcut executable and start directory.
    exe_path = f'"{itch_setup_path}"'
    start_dir = f'"{os.path.dirname(itch_setup_path)}"'

    # Steam Deck/Linux needs its compatibility environment.
    # Windows uses neither STEAM_COMPAT_DATA_PATH nor %command%.
    if not is_windows:
        compat_data_path = os.path.join(
            logged_in_home,
            ".local",
            "share",
            "Steam",
            "steamapps",
            "compatdata",
            str(itchio_launcher)
        )

        launch_prefix = (
            f'STEAM_COMPAT_DATA_PATH="{compat_data_path}/" '
        )

    # Create shortcuts for each discovered game.
    for game_id, game_title in itchgames:
        if is_windows:
            launchoptions = (
                f'--appname itch --run-game {game_id}'
            )
        else:
            launchoptions = (
                f'{launch_prefix}%command% '
                f'--appname itch --run-game {game_id}'
            )

        try:
            # Register the game shortcut.
            create_new_entry(
                exe_path,
                game_title,
                launchoptions,
                start_dir,
                launcher_name="itch.io"
            )

            # Track the discovered game.
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


# End of Itch.io Scanner