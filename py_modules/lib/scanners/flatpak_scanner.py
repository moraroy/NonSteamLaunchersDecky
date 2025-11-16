import os
import subprocess
import decky_plugin
import platform
from scanners.game_tracker import track_game

def flatpak_scanner(logged_in_home, create_new_entry):

    if platform.system() == "Windows":
        decky_plugin.logger.info("Running on Windows. Skipping Flatpak scanner.")
        return

    env_vars = {**os.environ, 'LD_LIBRARY_PATH': '/usr/lib:/lib'}

    def is_flatpak_installed(app_id):
        for install_type in ["--user", "--system"]:
            try:
                subprocess.run(
                    ["flatpak", "info", install_type, app_id],
                    check=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    env=env_vars
                )
                return True
            except subprocess.CalledProcessError:
                continue
        return False

    geforce_app_id = "com.nvidia.geforcenow"
    if is_flatpak_installed(geforce_app_id):
        exe_path = '"/usr/bin/flatpak"'
        display_name = "NVIDIA GeForce NOW"
        app_name = f"run {geforce_app_id}"
        start_dir = '"/usr/bin"'

        try:
            create_new_entry(
                exe_path,
                display_name,
                app_name,
                start_dir,
                "NonSteamLaunchers"
            )
            track_game(display_name, "Launcher")
            decky_plugin.logger.info(f"Added {display_name} to shortcuts.")
        except Exception as e:
            decky_plugin.logger.error(f"Failed to create entry for {display_name}: {str(e)}")
    else:
        decky_plugin.logger.info(f"Skipping {geforce_app_id} scanner — Flatpak not found.")

    moonlight_app_id = "com.moonlight_stream.Moonlight"
    if is_flatpak_installed(moonlight_app_id):
        exe_path = '"/usr/bin/flatpak"'
        display_name = "Moonlight Game Streaming"

        app_name = (
            "run --branch=stable --arch=x86_64 --command=moonlight "
            "com.moonlight_stream.Moonlight"
        )
        start_dir = '"/usr/bin"'

        try:
            create_new_entry(
                exe_path,
                display_name,
                app_name,
                start_dir,
                "NonSteamLaunchers"
            )
            track_game(display_name, "Launcher")
            decky_plugin.logger.info(f"Added {display_name} to shortcuts.")
        except Exception as e:
            decky_plugin.logger.error(f"Failed to create entry for {display_name}: {str(e)}")
    else:
        decky_plugin.logger.info(f"Skipping {moonlight_app_id} scanner — Flatpak not found.")
