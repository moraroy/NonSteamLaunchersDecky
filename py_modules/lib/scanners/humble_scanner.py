import json
import os
import decky_plugin

def humble_scanner(logged_in_home, humble_launcher, create_new_entry):
    # Humble Games Collection Scanner (Humble Bundle, Humble Games, Humble Games Collection)
    proton_prefix = f"{logged_in_home}/.local/share/Steam/steamapps/compatdata/{humble_launcher}/pfx"

    # JSON config file path inside Proton prefix
    config_path = os.path.join(
        proton_prefix,
        "drive_c/users/steamuser/AppData/Roaming/Humble App/config.json"
    )

    # Convert Windows-style path to Linux path inside Proton prefix drive_c
    def windows_to_linux_path(win_path):
        if not win_path:
            return ""
        if win_path.startswith("C:\\"):
            rel_path = win_path.replace("C:\\", "").replace("\\", "/")
            return os.path.join(proton_prefix, "drive_c", rel_path)
        return win_path

    # Skip scanner if config doesn't exist
    if not os.path.isfile(config_path):
        decky_plugin.logger.info("Skipping Humble Games Scanner (config not found)")
    else:
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            decky_plugin.logger.info("Skipping Humble Games Scanner (invalid config)")
        else:
            games = data.get("game-collection-4", [])

            for idx, game in enumerate(games, 1):
                status = game.get("status")
                if status not in ("downloaded", "installed"):
                    continue

                game_name = game.get("gameName", "Unknown")
                win_install_path = game.get("filePath", "")
                exe_rel_path = game.get("executablePath", "")

                if not exe_rel_path or not win_install_path:
                    decky_plugin.logger.info("  Missing executable or install path, skipping")
                    continue

                linux_install_path = windows_to_linux_path(win_install_path)
                linux_exe_path = os.path.join(linux_install_path, exe_rel_path.replace("\\", "/"))

                if not os.path.isfile(linux_exe_path):
                    decky_plugin.logger.info("  Executable not found, skipping game")
                    continue

                start_dir = os.path.dirname(linux_exe_path)
                launch_options = f'STEAM_COMPAT_DATA_PATH="{proton_prefix}" %command%'

                create_new_entry(f'"{linux_exe_path}"', game_name, launch_options, f'"{start_dir}"', "Humble Bundle")
