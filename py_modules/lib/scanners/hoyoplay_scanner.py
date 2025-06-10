import decky_plugin
import os
import json
from scanners.game_tracker import track_game

def hoyoplay_scanner(logged_in_home, hoyoplay_launcher, create_new_entry):

    file_path = f"{logged_in_home}/.local/share/Steam/steamapps/compatdata/{hoyoplay_launcher}/pfx/drive_c/users/steamuser/AppData/Roaming/Cognosphere/HYP/1_0/data/gamedata.dat"

    # Check if the file exists
    if not os.path.exists(file_path):
        print("Skipping HoYo Play scanner: File does not exist.")
    else:
        def extract_json_objects(data):
            decoder = json.JSONDecoder()
            json_objects = []

            decoded = data.decode("utf-8", errors="ignore")
            idx = 0
            length = len(decoded)

            while idx < length:
                try:
                    json_obj, end = decoder.raw_decode(decoded[idx:])
                    if isinstance(json_obj, dict):
                        json_objects.append(json_obj)
                    idx += end
                except json.JSONDecodeError:
                    idx += 1

            return json_objects

        with open(file_path, "rb") as f:
            f.read(8)
            raw_data = f.read()

        json_objects = extract_json_objects(raw_data)

        games = {}
        for entry in json_objects:
            exe = entry.get("gameInstallStatus", {}).get("gameExeName", "").strip()
            path = entry.get("installPath", "").strip()
            persist = entry.get("persistentInstallPath", "").strip()
            name = entry.get("gameShortcutName", "").strip()
            biz = entry.get("gameBiz", "").strip()

            if exe and path:
                key = name or exe
                if key not in games:
                    games[key] = {
                        "exe_name": exe,
                        "install_path": path,
                        "persistent_path": persist,
                        "shortcut_name": name,
                        "gamebiz": biz,
                    }

        if games:
            for game, details in sorted(games.items()):
                display_name = details["shortcut_name"] or game
                game_biz = details["gamebiz"]
                launch_options = f'STEAM_COMPAT_DATA_PATH="{logged_in_home}/.local/share/Steam/steamapps/compatdata/{hoyoplay_launcher}/" %command% "--game={game_biz}"'
                exe_path = f'"{logged_in_home}/.local/share/Steam/steamapps/compatdata/{hoyoplay_launcher}/pfx/drive_c/Program Files/HoYoPlay/launcher.exe"'
                start_dir = f'"{logged_in_home}/.local/share/Steam/steamapps/compatdata/{hoyoplay_launcher}/pfx/drive_c/Program Files/HoYoPlay"'

                if not details["install_path"] and not details["persistent_path"]:
                    continue

                create_new_entry(exe_path, display_name, launch_options, start_dir, "HoYoPlay")
                track_game(display_name, "HoYoPlay")

