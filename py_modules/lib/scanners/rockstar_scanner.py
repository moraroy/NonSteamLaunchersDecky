import os
import re
import platform
import decky_plugin
from scanners.game_tracker import track_game

if platform.system() == "Windows":
    import winreg

def rockstar_scanner(logged_in_home, rockstar_launcher, create_new_entry):
    is_windows = platform.system() == "Windows"

    if not is_windows and not rockstar_launcher:
        decky_plugin.logger.info(
            "Rockstar Games Launcher ID not provided. Skipping scanner."
        )
        return

    compat_path = ""
    rockstar_games = {}

    if is_windows:
        registry_paths = [
            r"SOFTWARE\WOW6432Node\Rockstar Games",
            r"SOFTWARE\Rockstar Games",
        ]

        for registry_path in registry_paths:
            try:
                with winreg.OpenKey(
                    winreg.HKEY_LOCAL_MACHINE, registry_path
                ) as root_key:
                    index = 0

                    while True:
                        try:
                            game_title = winreg.EnumKey(root_key, index)
                            index += 1
                        except OSError:
                            break

                        if game_title in (
                            "Launcher",
                            "Rockstar Games Social Club"
                        ):
                            continue

                        try:
                            with winreg.OpenKey(
                                root_key, game_title
                            ) as game_key:
                                install_folder, _ = winreg.QueryValueEx(
                                    game_key, "InstallFolder"
                                )

                            if os.path.isdir(install_folder):
                                rockstar_games[game_title] = install_folder

                        except OSError:
                            continue

            except OSError:
                continue

    else:
        compat_path = (
            f"{logged_in_home}/.local/share/Steam/steamapps/compatdata/"
            f"{rockstar_launcher}/"
        )

        rockstar_sys_reg = f"{compat_path}pfx/system.reg"

        if not os.path.isfile(rockstar_sys_reg):
            decky_plugin.logger.info(
                "Rockstar Games registry not found. Skipping scanner."
            )
            return

        current_game = None

        try:
            with open(
                rockstar_sys_reg,
                "r",
                encoding="utf-8",
                errors="replace"
            ) as registry:
                for line in registry:
                    section_match = re.search(
                        r'^\[Software\\\\Wow6432Node\\\\Rockstar Games\\\\([^\\]+)\]',
                        line
                    )

                    if section_match:
                        game_title = section_match.group(1)

                        if game_title in (
                            "Launcher",
                            "Rockstar Games Social Club"
                        ):
                            current_game = None
                        else:
                            current_game = game_title

                        continue

                    if current_game and '"InstallFolder"' in line:
                        folder_match = re.search(
                            r'"InstallFolder"="(.+)"',
                            line
                        )

                        if not folder_match:
                            continue

                        install_folder = folder_match.group(1)
                        windows_prefix = "C:\\"

                        if not install_folder.lower().startswith(
                            windows_prefix.lower()
                        ):
                            continue

                        relative_path = install_folder[
                            len(windows_prefix):
                        ].replace("\\", "/")

                        install_path = (
                            f"{compat_path}pfx/drive_c/{relative_path}"
                        )

                        if os.path.isdir(install_path):
                            rockstar_games.setdefault(
                                current_game, install_path
                            )

        except OSError as error:
            decky_plugin.logger.error(
                f"Failed to read Rockstar registry: {error}"
            )
            return

    if not rockstar_games:
        decky_plugin.logger.info(
            "No Rockstar games found in registry. Skipping scanner."
        )
        return

    for game_name, install_path in rockstar_games.items():
        try:
            exe_candidates = sorted(
                filename
                for filename in os.listdir(install_path)
                if filename.lower().endswith(".exe")
                and "uninstall" not in filename.lower()
            )
        except OSError as error:
            decky_plugin.logger.warning(
                f"Could not list game directory for {game_name}: {error}"
            )
            continue

        if not exe_candidates:
            decky_plugin.logger.warning(
                f"No executable found for {game_name} in {install_path}"
            )
            continue

        game_words = game_name.split()
        game_word = game_words[-1].lower() if game_words else ""

        game_exe = next(
            (
                filename for filename in exe_candidates
                if game_word and game_word in filename.lower()
            ),
            exe_candidates[0]
        )

        exe_path = f'"{install_path}/{game_exe}"'
        start_dir = f'"{install_path}"'

        launch_options = (
            f'STEAM_COMPAT_DATA_PATH="{compat_path}" %command%'
            if not is_windows else ""
        )

        try:
            create_new_entry(
                exe_path,
                game_name,
                launch_options,
                start_dir,
                "Rockstar Games Launcher"
            )

            track_game(game_name, "Rockstar Games Launcher")

            decky_plugin.logger.info(
                f"Added Rockstar game: {game_name}"
            )

        except Exception as error:
            decky_plugin.logger.error(
                f"Failed to add Rockstar game '{game_name}': {error}"
            )
