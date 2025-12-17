import os
import re
import shlex
import decky_plugin

def create_exec_line_from_entry(logged_in_home, new_entry):
    try:
        appname = new_entry.get('appname')
        exe_path = new_entry.get('exe')
        launch_options = new_entry.get('LaunchOptions', '')
        launcher_name = new_entry.get('Launcher', '')
        compattool = new_entry.get('CompatTool')

        #decky_plugin.logger.info(f"desktopC: Processing game '{appname}' with exe '{exe_path}'")
        #decky_plugin.logger.info(f"desktopC: Launch Options: {launch_options}")
        #decky_plugin.logger.info(f"desktopC: Launcher Name: {launcher_name}")
        #decky_plugin.logger.info(f"desktopC: Compat Tool: {compattool}")

        m = re.search(r'GAMEID="(\d+)"', launch_options)
        umugameid = m.group(1) if m else None
        #decky_plugin.logger.info(f"desktopC: UMU GameID: {umugameid}")

        compat_match = re.search(r'STEAM_COMPAT_DATA_PATH="([^"]+)"', launch_options)
        if not compat_match:
            decky_plugin.logger.error("desktopC: ERROR - no STEAM_COMPAT_DATA_PATH in launch options")
            return None

        compat_data_prefix = os.path.basename(compat_match.group(1).rstrip("/"))
        #decky_plugin.logger.info(f"desktopC: Compat prefix: {compat_data_prefix}")

        proton_path = None
        dir_path = os.path.expanduser("~/.steam/root/compatibilitytools.d")
        pattern = re.compile(r"UMU-Proton-(\d+(?:\.\d+)*)(?:-(\d+(?:\.\d+)*))?")

        try:
            umu_folders = [
                (tuple(map(int, (m.group(1) + '.' + (m.group(2) or '0')).split('.'))), name)
                for name in os.listdir(dir_path)
                if (m := pattern.match(name)) and os.path.isdir(os.path.join(dir_path, name))
            ]
            latest_umu = max(umu_folders)[1] if umu_folders else None
            if latest_umu:
                decky_plugin.logger.info(f"desktopC: Found latest UMU Proton: {latest_umu}")
        except Exception as e:
            decky_plugin.logger.error(f"desktopC: Error reading UMU Proton folders: {e}")
            latest_umu = None

        if compattool and not compattool.lower().startswith("umu"):
            proton_path = os.path.join(logged_in_home, f".local/share/Steam/compatibilitytools.d/{compattool}")
        elif latest_umu:
            proton_path = os.path.join(logged_in_home, f".local/share/Steam/compatibilitytools.d/{latest_umu}")

        #decky_plugin.logger.info(f"desktopC: Final Proton Path: {proton_path}")

        desktop_dir = os.path.join(logged_in_home, "Desktop")
        if not os.path.isdir(desktop_dir):
            decky_plugin.logger.error("desktopC: Desktop directory not found")
            return None

        found = False
        for filename in os.listdir(desktop_dir):
            if not filename.endswith(".desktop"):
                continue

            path = os.path.join(desktop_dir, filename)
            if not os.path.isfile(path):
                decky_plugin.logger.warning(f"desktopC: Skipping missing .desktop file: {path}")
                continue

            try:
                content = open(path).read()
            except Exception as e:
                decky_plugin.logger.warning(f"desktopC: Failed to read {path}: {e}")
                continue


            if appname not in content:
                continue

            found = True
            decky_plugin.logger.info(f"desktopC: Found .desktop: {path}")

            UMU = os.path.join(logged_in_home, "bin/umu-run")
            tokens = shlex.split(exe_path)
            first = os.path.basename(tokens[0])
            final_exe_path = exe_path if first == "umu-run" else f"{UMU} {exe_path}"
            final_exe_path = re.sub(r'^"(/.*?umu-run)"', r'\1', final_exe_path)

            #decky_plugin.logger.info(f"desktopC: Final Exe Path: {final_exe_path}")

            env_vars = (
                f'STEAM_COMPAT_DATA_PATH="{logged_in_home}/.local/share/Steam/steamapps/compatdata/{compat_data_prefix}/" '
                f'WINEPREFIX="{logged_in_home}/.local/share/Steam/steamapps/compatdata/{compat_data_prefix}/pfx"'
            )

            if umugameid:
                env_vars += f' GAMEID={umugameid}'
            if proton_path:
                env_vars += f' PROTONPATH="{proton_path}"'

            #decky_plugin.logger.info(f"desktopC: Env Vars: {env_vars}")

            game_id = None

            # GOG
            m = re.search(r'/gameId=(\d+)', launch_options)
            if m:
                game_id = m.group(1)
                #decky_plugin.logger.info(f"desktopC: Found GOG gameId: {game_id}")

            # Epic
            if not game_id:
                m = re.search(r'com\.epicgames\.launcher://apps/([^/?&]+)', launch_options)
                if m:
                    game_id = m.group(1)
                    #decky_plugin.logger.info(f"desktopC: Found Epic gameId: {game_id}")

            # Amazon
            if not game_id:
                m = re.search(r'amazon-games://play/([a-zA-Z0-9\-\.]+)', launch_options)
                if m:
                    game_id = m.group(1)
                    #decky_plugin.logger.info(f"desktopC: Found Amazon gameId: {game_id}")

            # Origin
            if not game_id:
                m = re.search(r'origin2://game/launch\?offerIds=([a-zA-Z0-9\-]+)', launch_options)
                if m:
                    game_id = m.group(1)
                    #decky_plugin.logger.info(f"desktopC: Found Origin gameId: {game_id}")

            # Ubisoft Connect
            m = re.search(r'(uplay://launch/\d+(?:/\d+)?)', launch_options)
            uplay_launch_url = m.group(1) if m else None
            if uplay_launch_url:
                #decky_plugin.logger.info(f"desktopC: Found Ubisoft launch URL: {uplay_launch_url}")
                runner_cmd = f'{final_exe_path} {uplay_launch_url}'



            # GOG path
            m = re.search(r'/path="([^"]+)"', launch_options)
            gog_game_path = m.group(1) if m else None
            if gog_game_path:
                decky_plugin.logger.info(f"desktopC: GOG Game Path: {gog_game_path}")

            # Optional DOSBox / extra GOG args (quoted block after /path)
            extra_gog_args = None
            m = re.search(r'/path="[^"]+"\s+"([^"]+)"', launch_options)
            if m:
                extra_gog_args = m.group(1)
                decky_plugin.logger.info(f"desktopC: GOG Extra Args: {extra_gog_args}")


            if "com.epicgames.launcher://" in launch_options and game_id:
                runner_cmd = f'{final_exe_path} -com.epicgames.launcher://apps/{game_id}?action=launch&silent=true'

            elif "origin2://" in launch_options and game_id:
                runner_cmd = f'{final_exe_path} origin2://game/launch?offerIds={game_id}'

            elif "amazon-games://" in launch_options and game_id:
                runner_cmd = f'{final_exe_path} -amazon-games://play/{game_id}'

            elif uplay_launch_url:
                runner_cmd = f'{final_exe_path} {uplay_launch_url}'


            elif gog_game_path and game_id:
                runner_cmd = (
                    f'{final_exe_path} '
                    f'/command=runGame /gameId={game_id} '
                    f'/path="{gog_game_path}"'
                )

                if extra_gog_args:
                    runner_cmd += f' "{extra_gog_args}"'


            else:
                runner_cmd = final_exe_path

            #decky_plugin.logger.info(f"desktopC: Runner Cmd: {runner_cmd}")

            # ---------------- EXEC LINE ----------------
            original_exec = re.search(r'^Exec=(.*)', content, re.MULTILINE).group(1)

            exec_line = (
                "Exec=sh -c '"
                "if command -v kdialog >/dev/null; then "
                f"CHOICE=$(kdialog --yesno \"Standalone or with Steam?\" "
                f"--yes-label \"UMU + {launcher_name}\" --no-label \"Steam\"); "
                "exit_code=$?; "
                "if [ $exit_code -eq 2 ]; then exit 0; fi; "
                "if [ $exit_code -eq 0 ]; then "
                f"CHOICE={launcher_name.lower()}; "
                "elif [ $exit_code -eq 1 ]; then "
                "CHOICE=steam; "
                "fi; "
                "else CHOICE=steam; fi; "
                f"if [ \"$CHOICE\" = \"steam\" ]; then {original_exec}; "
                f"else \"pkill -9 -f wineserver\"; {env_vars} {runner_cmd}; fi'"
            )

            content = re.sub(
                r'^Exec=.*',
                lambda _: exec_line,
                content,
                flags=re.MULTILINE
            )

            content = content.replace(
                "Comment=Play this game on Steam",
                "Comment=Play this game on Steam or Standalone"
            )

            with open(path, "w") as file:
                file.write(content)

            #decky_plugin.logger.info(f"desktopC: Updated Exec line in {path}")

            applications_dir = os.path.join(logged_in_home, ".local/share/applications/")
            os.makedirs(applications_dir, exist_ok=True)

            if os.path.isfile(path):
                symlink_path = os.path.join(applications_dir, filename)
                if os.path.exists(symlink_path):
                    os.remove(symlink_path)
                os.symlink(path, symlink_path)
                decky_plugin.logger.info(f"desktopC: Created symlink {symlink_path} -> {path}")
            else:
                decky_plugin.logger.warning(f"desktopC: Cannot create symlink, file missing: {path}")

        if not found:
            decky_plugin.logger.info("desktopC: No matching .desktop file found")

        decky_plugin.logger.info("desktopC: Finished processing all games")

    except Exception as e:
        decky_plugin.logger.error(f"desktopC: Error creating Exec line: {e}")
