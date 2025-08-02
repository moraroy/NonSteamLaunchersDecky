import os
import re
import json
import decky_plugin
from scanners.game_tracker import track_game


def geforcenow_scanner(logged_in_home, geforcenow_launcher, create_new_entry):
    def extract_block_info(block):
        full_game_name = None
        short_name = None
        parent_game_id = None

        for line in block:
            if not full_game_name:
                m = re.search(r"Add game to favorites for\s+(.+?)\s+\[", line)
                if m:
                    full_game_name = m.group(1).strip()

            if not short_name:
                m = re.search(r"Attempting add to favorite, game\s+(\S+)\[", line)
                if m:
                    short_name = m.group(1)

            if not parent_game_id:
                m = re.search(r"\[([0-9a-fA-F-]{36})\]", line)
                if m:
                    parent_game_id = m.group(1)

        return full_game_name, short_name, parent_game_id

    log_path = os.path.join(
        logged_in_home,
        ".var/app/com.nvidia.geforcenow/.local/state/NVIDIA/GeForceNOW/console.log"
    )

    if not os.path.exists(log_path):
        decky_plugin.logger.info(f"GeForce NOW log not found at: {log_path}")
        return

    try:
        with open(log_path) as f:
            lines = f.readlines()
    except Exception as e:
        decky_plugin.logger.error(f"Failed to read GeForce NOW log: {e}")
        return

    viewgame_events = []
    for i, line in enumerate(lines):
        if "JsEventsService" in line and "events request" in line:
            try:
                json_part = line.split("events request", 1)[1].strip()
                data = json.loads(json_part)
                for event in data.get("events", []):
                    if event.get("name") == "Click":
                        params = event.get("parameters", {})
                        if params.get("itemType") == "ViewGameDetails":
                            item_label = params.get("itemLabel")
                            if item_label and re.match(r"^\d+$", item_label):
                                viewgame_events.append({
                                    "line_index": i,
                                    "cmsId": item_label
                                })
            except Exception:
                continue

    favorites = []
    for i, line in enumerate(lines):
        if "UserGesture clicked on add to favorites" in line:
            block = lines[i:i+30]
            full_game_name, short_name, parent_game_id = extract_block_info(block)

            if not short_name or not parent_game_id:
                continue

            closest_view = None
            closest_distance = None
            for view in viewgame_events:
                distance = abs(view["line_index"] - i)
                if closest_distance is None or distance < closest_distance:
                    closest_distance = distance
                    closest_view = view

            cms_id = closest_view["cmsId"] if closest_view else None

            favorites.append({
                "shortName": short_name,
                "parentGameId": parent_game_id,
                "cmsId": cms_id,
                "fullGameName": full_game_name
            })

    for fav in favorites:
        if fav["cmsId"]:
            display_name = fav['fullGameName'] or fav['shortName']

            exe_path = '"/usr/bin/flatpak"'
            start_dir = '"/usr/bin/"'

            launch_options = (
                f"run --command=sh com.nvidia.geforcenow -c "
                f"\"/app/cef/GeForceNOW --url-route='#?cmsId={fav['cmsId']}"
                f"&launchSource=External&shortName={fav['shortName']}"
                f"&parentGameId={fav['parentGameId']}'\""
            )

            create_new_entry(exe_path, display_name, launch_options, start_dir, "NVIDIA GeForce NOW")
            #track_game(display_name, "NVIDIA GeForce NOW")
        else:
            decky_plugin.logger.warning(
                f"Missing cmsId for favorite game: {fav.get('fullGameName') or fav.get('shortName')}"
            )