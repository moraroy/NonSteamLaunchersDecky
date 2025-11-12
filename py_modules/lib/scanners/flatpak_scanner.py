import os
import subprocess
import decky_plugin
import platform
from scanners.game_tracker import track_game

def flatpak_scanner(logged_in_home, create_new_entry):
    # Skip scanner if running on Windows
    if platform.system() == "Windows":
        decky_plugin.logger.info("Running on Windows. Skipping Flatpak scanner.")
        return

    # Environment setup
    env_vars = {**os.environ, 'LD_LIBRARY_PATH': '/usr/lib:/lib'}

    def is_flatpak_installed(app_id):
        """Helper function to check if a Flatpak app is installed"""
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

    # Check if GeForce NOW is installed
    app_id = "com.nvidia.geforcenow"
    if not is_flatpak_installed(app_id):
        decky_plugin.logger.info(f"Skipping {app_id} scanner — Flatpak not found.")
        return

    # GeForce NOW is installed — create shortcut
    exe_path = '"/usr/bin/flatpak"'
    display_name = "NVIDIA GeForce NOW"
    app_name = f"run {app_id}"
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

