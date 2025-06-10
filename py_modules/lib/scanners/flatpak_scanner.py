import os
import subprocess
import decky_plugin
from scanners.game_tracker import track_game


def flatpak_scanner(logged_in_home, create_new_entry):
    env_vars = {**os.environ, 'LD_LIBRARY_PATH': '/usr/lib:/lib'}

    # GeForce NOW Flatpak Scanner
    installed = False

    try:
        subprocess.run(
            ["flatpak", "info", "--user", "com.nvidia.geforcenow"],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            env=env_vars
        )
        installed = True
    except subprocess.CalledProcessError:
        try:
            subprocess.run(
                ["flatpak", "info", "--system", "com.nvidia.geforcenow"],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                env=env_vars  # Apply env override
            )
            installed = True
        except subprocess.CalledProcessError:
            pass

    if not installed:
        decky_plugin.logger.info("Skipping NVIDIA GeForce NOW scanner — Flatpak not found.")
        return

    # GeForce NOW is installed — create shortcut
    exe_path = '"/usr/bin/flatpak"'
    display_name = "NVIDIA GeForce NOW"
    app_name = "run com.nvidia.geforcenow"
    start_dir = '"/usr/bin"'

    create_new_entry(
        exe_path,
        display_name,
        app_name,
        start_dir,
        "GeForce NOW"
    )
    track_game(display_name, "GeForce NOW")
