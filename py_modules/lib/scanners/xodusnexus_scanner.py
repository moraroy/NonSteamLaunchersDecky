import os
import json
import decky_plugin
from scanners.game_tracker import track_game


def xodusnexus_scanner(logged_in_home, create_new_entry):
    xodus_config_dir = f"{logged_in_home}/.config/xodus-nexus"
    xodus_state_file = f"{logged_in_home}/.config/xodus-nexus/launcher-state.json"
    xodus_launcher = f"{logged_in_home}/.config/xodus-nexus/shortcuts/launch-game"

    if (
        not os.path.isfile(xodus_state_file)
        or not os.path.isfile(xodus_launcher)
    ):
        decky_plugin.logger.info(
            "[Xodus] Skipping scanner due to missing paths."
        )
        return

    decky_plugin.logger.info("[Xodus] Scanner starting.")

    try:
        with open(xodus_state_file, "r", encoding="utf-8") as file:
            xodus_state = json.load(file)

        if not isinstance(xodus_state, dict):
            decky_plugin.logger.warning(
                "[Xodus] Invalid launcher-state.json format."
            )
            return

    except (OSError, json.JSONDecodeError) as error:
        decky_plugin.logger.error(
            f"[Xodus] Failed to read state file: {error}"
        )
        return

    xodus_games = xodus_state.get("games", [])

    if not isinstance(xodus_games, list):
        decky_plugin.logger.warning(
            "[Xodus] Invalid games list in launcher-state.json."
        )
        return

    created_count = 0
    skipped_count = 0

    for game in xodus_games:
        if not isinstance(game, dict):
            skipped_count += 1
            continue

        display_name = game.get("title", "")
        game_id = game.get("id", "")
        game_path = game.get("path", "")

        if not all(
            isinstance(value, str)
            for value in (display_name, game_id, game_path)
        ):
            skipped_count += 1
            continue

        display_name = display_name.strip()
        game_id = game_id.strip()
        game_path = game_path.strip()

        if not display_name or not game_id:
            skipped_count += 1
            continue

        if not game_path or not os.path.isdir(game_path):
            skipped_count += 1
            continue

        if (
            len(game_id) != 16
            or any(c not in "0123456789abcdef" for c in game_id)
        ):
            skipped_count += 1
            continue

        exe_path = f'"{xodus_launcher}"'
        start_dir = f'"{xodus_config_dir}"'
        launch_options = game_id

        try:
            create_new_entry(
                exe_path,
                display_name,
                launch_options,
                start_dir,
                "Microsoft Windows"
            )

            track_game(display_name, "Microsoft Windows")
            created_count += 1

        except Exception as error:
            decky_plugin.logger.error(
                f"[Xodus] Error creating {display_name}: {error}"
            )

    decky_plugin.logger.info(
        f"[Xodus] Finished. Created: {created_count}; "
        f"skipped: {skipped_count}"
    )
