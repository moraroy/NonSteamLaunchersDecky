import decky_plugin
import os
import time
from scanners.game_tracker import track_game

logger = decky_plugin.logger

def gryphlink_scanner(logged_in_home, gryphlink_launcher, create_new_entry):

    endfield_exe = (
        f"{logged_in_home}/.local/share/Steam/steamapps/compatdata/{gryphlink_launcher}/"
        "pfx/drive_c/Program Files/GRYPHLINK/games/EndField Game/Endfield.exe"
    )

    if not os.path.exists(endfield_exe):
        logger.info("Skipping GRYPHLINK scanner — Endfield.exe not found")
        return

    logger.info(f"GRYPHLINK game found: {endfield_exe}")

    display_name = "Arknights: Endfield"
    launch_options = (
        f'STEAM_COMPAT_DATA_PATH="{logged_in_home}/.local/share/Steam/'
        f'steamapps/compatdata/{gryphlink_launcher}/" %command%'
    )

    exe_path = f'"{endfield_exe}"'
    start_dir = f'"{os.path.dirname(endfield_exe)}"'

    create_new_entry(
        exe_path,
        display_name,
        launch_options,
        start_dir,
        launcher_name="Gryphlink"
    )

    track_game(display_name, "Gryphlink")
    time.sleep(0.1)
