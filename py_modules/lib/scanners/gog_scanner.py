import os
import re
import sqlite3
import decky_plugin
import platform
import time
from scanners.game_tracker import track_game


def getGogGameInfoDB(db_path, logged_in_home=None, gog_galaxy_launcher=None):
    if not os.path.exists(db_path):
        decky_plugin.logger.info(f"GOG Galaxy DB not found: {db_path}")
        return {}

    game_dict = {}

    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()

            # Pull only the *default* PlayTask using isPrimary = 1
            cursor.execute("""
                SELECT
                    ibp.productId,
                    ld.title,
                    ibp.installationPath,
                    ptl.executablePath,
                    ptl.commandLineArgs
                FROM InstalledBaseProducts ibp
                JOIN LimitedDetails ld
                    ON ibp.productId = ld.productId
                LEFT JOIN PlayTasks pt
                    ON pt.gameReleaseKey = 'gog_' || ibp.productId
                   AND pt.isPrimary = 1
                LEFT JOIN PlayTaskLaunchParameters ptl
                    ON ptl.playTaskId = pt.id
                WHERE ld.is_production = 1
            """)

            for pid, title, install_path, ptl_exe, ptl_args in cursor.fetchall():
                if not ptl_exe:
                    continue

                exe_win_path = ptl_exe.replace("/", "\\").strip()

                # Proton path translation
                if platform.system() != "Windows" and logged_in_home and gog_galaxy_launcher:
                    proton_root = (
                        f"{logged_in_home}/.local/share/Steam/steamapps/compatdata/"
                        f"{gog_galaxy_launcher}/pfx"
                    )
                    win_no_drive = re.sub(
                        r"^[A-Za-z]:/", "", exe_win_path.replace("\\", "/")
                    )
                    exe_proton_path = os.path.join(proton_root, "drive_c", win_no_drive)
                else:
                    exe_proton_path = exe_win_path

                if not os.path.exists(exe_proton_path):
                    decky_plugin.logger.info(
                        f"Skipping {title}: EXE not on disk -> {exe_proton_path}"
                    )
                    continue

                game_dict[title] = {
                    "id": pid,
                    "exe": exe_win_path,
                    "launchParams": ptl_args
                }

    except sqlite3.Error as e:
        decky_plugin.logger.error(f"SQLite error: {e}")

    return game_dict


def getGogGameInfoWindows():
    if platform.system() != "Windows":
        return {}
    db_path = r"C:\ProgramData\GOG.com\Galaxy\storage\galaxy-2.0.db"
    return getGogGameInfoDB(db_path)


def adjust_dosbox_launch_options(launch_command, game_id, logged_in_home, gog_galaxy_launcher, is_windows, launch_params=None):
    print(f"Adjusting launch options for command: {launch_command}")

    launch_lower = launch_command.lower()

    if "dosbox.exe" in launch_lower:
        try:
            idx = launch_lower.index("dosbox.exe")
            exe_path = launch_command[:idx] + "DOSBox.exe"
            args = launch_command[idx + len("dosbox.exe"):].strip()

            if launch_params:
                lp = launch_params.strip()
                if lp:
                    args = f"{args} {lp}".strip()

            if is_windows:
                return f'/command=runGame /gameId={game_id} /path="{exe_path}" "{args}"'

            return (
                f'STEAM_COMPAT_DATA_PATH="{logged_in_home}/.local/share/Steam/steamapps/'
                f'compatdata/{gog_galaxy_launcher}/" %command% /command=runGame '
                f'/gameId={game_id} /path="{exe_path}" "{args}"'
            )

        except Exception:
            return launch_command

    launch_command = launch_command.strip()

    if is_windows:
        return f'/command=runGame /gameId={game_id} /path="{launch_command}"'

    return (
        f'STEAM_COMPAT_DATA_PATH="{logged_in_home}/.local/share/Steam/steamapps/'
        f'compatdata/{gog_galaxy_launcher}/" %command% /command=runGame '
        f'/gameId={game_id} /path="{launch_command}"'
    )


def gog_scanner(logged_in_home, gog_galaxy_launcher, create_new_entry):

    is_windows = platform.system() == "Windows"

    if is_windows:
        game_dict = getGogGameInfoWindows()
        exe_template = r"C:\Program Files (x86)\GOG Galaxy\GalaxyClient.exe"
        start_dir_template = r"C:\Program Files (x86)\GOG Galaxy"
    else:
        db_path = (
            f"{logged_in_home}/.local/share/Steam/steamapps/compatdata/"
            f"{gog_galaxy_launcher}/pfx/drive_c/ProgramData/GOG.com/Galaxy/storage/galaxy-2.0.db"
        )

        if not os.path.exists(db_path):
            decky_plugin.logger.info(f"GOG DB not found: {db_path}")
            return

        game_dict = getGogGameInfoDB(db_path, logged_in_home, gog_galaxy_launcher)

        exe_template = (
            f"\"{logged_in_home}/.local/share/Steam/steamapps/compatdata/"
            f"{gog_galaxy_launcher}/pfx/drive_c/Program Files (x86)/GOG Galaxy/GalaxyClient.exe\""
        )
        start_dir_template = (
            f"\"{logged_in_home}/.local/share/Steam/steamapps/compatdata/"
            f"{gog_galaxy_launcher}/pfx/drive_c/Program Files (x86)/GOG Galaxy/\""
        )

    for game, game_info in game_dict.items():
        if game_info['id']:
            exe_path = game_info['exe'].strip()
            launch_params = game_info.get('launchParams', None)

            launch_options = adjust_dosbox_launch_options(
                exe_path,
                game_info['id'],
                logged_in_home,
                gog_galaxy_launcher,
                is_windows,
                launch_params
            )

            create_new_entry(
                exe_template,
                game,
                launch_options,
                start_dir_template,
                "GOG Galaxy"
            )

            track_game(game, "GOG Galaxy")
            time.sleep(0.1)
