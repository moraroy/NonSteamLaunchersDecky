def get_plugin_dir():
    from pathlib import Path
    return Path(__file__).parent.resolve()

def add_plugin_to_path():
    import sys
    plugin_dir = get_plugin_dir()
    decky_plugin.logger.info(f"{plugin_dir}")
    directories = [["./"], ["py_modules"], ["py_modules", "lib"], ["py_modules", "externals"]]
    for dir in directories:
        sys.path.append(str(plugin_dir.joinpath(*dir)))

import decky_plugin
add_plugin_to_path()

import os
import logging
import re
import asyncio
import subprocess
import shutil
import json
import requests
from aiohttp import web
from decky_plugin import DECKY_PLUGIN_DIR, DECKY_USER_HOME
from py_modules.lib.scanner import scan, addCustomSite
from settings import SettingsManager
from subprocess import Popen, run

# Set up logging
logging.basicConfig(level=logging.DEBUG)

def camel_to_snake(s):
    """Convert camelCase to snake_case."""
    return re.sub(r'([a-z])([A-Z])', r'\1_\2', s).lower()

def camel_to_title(s):
    # Split the string into words using a regular expression
    words = re.findall(r'[A-Z]?[a-z]+|[A-Z]+(?=[A-Z]|$)', s)
    # Convert the first character of each word to uppercase and join the words with spaces
    return ' '.join(word.capitalize() for word in words)

class Plugin:
    scan_lock = asyncio.Lock()
    update_cache = {}

    async def _main(self):
        decky_plugin.logger.info("This is _main being called")
        self.settings = SettingsManager(name="config", settings_directory=decky_plugin.DECKY_PLUGIN_SETTINGS_DIR)
        decky_user_home = decky_plugin.DECKY_USER_HOME
        defaultSettings = {"autoscan": False, "customSites": "", "monitor": False}





        async def handleMonitor(request):
            ws = web.WebSocketResponse()
            await ws.prepare(request)
            self.decky_plugin.logger.info(f"Monitor WebSocket connection established.")

            # Start the monitor process as a background task, independent of WebSocket
            monitor_task = asyncio.create_task(self.monitor_process(ws))

            # Wait for WebSocket to close before stopping the monitor task
            await ws.wait_closed()

            # If WebSocket closes, stop the monitoring task if necessary (clean up if needed)
            monitor_task.cancel()
            self.decky_plugin.logger.info("WebSocket connection closed. Monitor task canceled.")
            return ws

        async def monitor_process(ws):
            """Monitors launcher and game processes based on the monitor setting."""
            settings = await self.settings.getSetting('settings', defaultSettings)

            while True:
                if not settings.get('monitor', False):
                    self.decky_plugin.logger.info("Monitor is disabled.")
                    await ws.send_str("Monitor is disabled.")
                    break  # Exit the loop if monitor is turned off

                # Monitoring logic here (same as before)
                self.decky_plugin.logger.info("Starting monitor process...")

                LAUNCHERS = [
                    "EpicGamesLauncher.exe",
                    "GalaxyClient.exe",
                    "EpicWebHelper.exe",
                    "GalaxyClient Helper.exe",
                    "GalaxyOverlay.exe",
                    "GalaxyClientService.exe",
                    "GalaxyCommunication.exe"
                ]
                TIMEOUT_LIMIT = 60  # Timeout limit in seconds

                async def kill_launcher_processes():
                    """Kills all processes related to Epic Games and GOG Galaxy launchers."""
                    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                        try:
                            cmdline = proc.info.get('cmdline', [])
                            if isinstance(cmdline, list) and any(launcher.lower() in " ".join(cmdline).lower() for launcher in LAUNCHERS):
                                self.decky_plugin.logger.info(f"Killing process {proc.info['name']} (PID: {proc.info['pid']})")
                                proc.kill()
                        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
                            self.decky_plugin.logger.warning(f"Error with process {proc.info['name']} (PID: {proc.info['pid']}): {str(e)}")

                async def is_process_running(process_names):
                    """Checks if any process in the list is running by its name in the command line."""
                    running_procs = {}
                    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                        try:
                            cmdline = proc.info.get('cmdline', [])
                            if isinstance(cmdline, list):
                                cmdline_str = " ".join(cmdline)
                                for process_name in process_names:
                                    if process_name.lower() in cmdline_str.lower():
                                        running_procs[process_name] = proc.info['pid']
                        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
                            self.decky_plugin.logger.warning(f"Error accessing process {proc.info['name']} (PID: {proc.info['pid']}): {str(e)}")
                    return running_procs

                async def monitor_launcher_games(launcher, pid):
                    """Monitors game processes launched by a specific launcher."""
                    self.decky_plugin.logger.info(f"{launcher} (PID: {pid}) is running. Monitoring for game processes...")
                    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                        try:
                            cmdline = proc.info.get('cmdline', [])
                            if isinstance(cmdline, list):
                                cmdline_str = " ".join(cmdline)
                                if launcher in cmdline_str:
                                    self.decky_plugin.logger.info(f"Found {launcher} with PID {proc.info['pid']}")
                                    # Look for the actual game process launched by the launcher
                                    for game_proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                                        game_cmdline = game_proc.info.get('cmdline', [])
                                        if isinstance(game_cmdline, list):
                                            game_cmdline_str = " ".join(game_cmdline)
                                            if game_proc.info['pid'] != proc.info['pid'] and (
                                                    'C:/Program Files/Epic Games/' in game_cmdline_str or
                                                    'GOG Galaxy/Games/' in game_cmdline_str):
                                                self.decky_plugin.logger.info(f"Game found: {game_proc.info['name']} (PID: {game_proc.info['pid']})")
                                                # Kill the launcher after game is found
                                                await kill_launcher_processes()

                                                # Now wait until the game process exits
                                                while await is_process_running([game_proc.info['name']]):
                                                    self.decky_plugin.logger.info(f"Waiting for game {game_proc.info['name']} (PID: {game_proc.info['pid']}) to exit...")
                                                    await asyncio.sleep(2)  # Check every 2 seconds if the game is still running
                                                self.decky_plugin.logger.info(f"Game {game_proc.info['name']} has exited. Resuming monitoring.")
                                                break
                        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
                            self.decky_plugin.logger.warning(f"Error with process {proc.info['name']} (PID: {proc.info['pid']}): {str(e)}")

                start_time = time.time()

                try:
                    while settings.get('monitor', False):
                        running_launchers = await is_process_running(["EpicGamesLauncher.exe", "GalaxyClient.exe"])
                        if not running_launchers:
                            self.decky_plugin.logger.info("Neither Epic Games Launcher nor GOG Galaxy client is running.")
                            await asyncio.sleep(5)  # Wait before re-checking the processes
                            continue

                        tasks = []
                        for launcher, pid in running_launchers.items():
                            tasks.append(monitor_launcher_games(launcher, pid))

                        await asyncio.gather(*tasks)
                        await ws.send_str("Monitor process running...")
                        await asyncio.sleep(10)

                except Exception as e:
                    self.decky_plugin.logger.error(f"Error during monitor process: {e}")



        # Function to fetch GitHub package.json
        async def fetch_github_version():
            github_url = "https://raw.githubusercontent.com/moraroy/NonSteamLaunchersDecky/refs/heads/main/package.json"
            loop = asyncio.get_event_loop()
            try:
                response = await loop.run_in_executor(None, requests.get, github_url)
                response.raise_for_status()
                decky_plugin.logger.info("Successfully fetched GitHub version")
                return response.json()  # This will return the parsed JSON directly
            except requests.exceptions.RequestException as e:
                decky_plugin.logger.error(f"Error fetching GitHub version: {e}")
                return None

        # Function to read the local package.json
        async def fetch_local_version():
            local_package_path = os.path.join(DECKY_PLUGIN_DIR, 'package.json')
            try:
                with open(local_package_path, "r") as file:
                    data = json.load(file)
                    return data["version"]
            except FileNotFoundError:
                decky_plugin.logger.error(f"Local {local_package_path} not found!")
                return None
            except json.JSONDecodeError:
                decky_plugin.logger.error(f"Failed to parse {local_package_path}")
                return None

        # Compare versions
        async def compare_versions():
            if Plugin.update_cache:  # Check if we have cached update info
                decky_plugin.logger.info("Returning cached update information.")
                return Plugin.update_cache

            local_version = await fetch_local_version()
            github_data = await fetch_github_version()

            if not local_version or not github_data:
                return {"error": "Could not fetch version information"}

            github_version = github_data.get("version")
            if not github_version:
                return {"error": "GitHub version not found"}

            decky_plugin.logger.info(f"Local Version: {local_version}, GitHub Version: {github_version}")

            if local_version == github_version:
                update_info = {"status": "Up-to-date", "local_version": local_version, "github_version": github_version}
            else:
                update_info = {"status": "Update available", "local_version": local_version, "github_version": github_version}

            Plugin.update_cache = update_info  # Cache the update info
            return update_info

        # WebSocket handler to check for updates
        async def handle_check_update(request):
            ws = web.WebSocketResponse()
            await ws.prepare(request)

            try:
                # Fetch and compare the versions
                version_info = await compare_versions()
                await ws.send_json(version_info)
            except Exception as e:
                decky_plugin.logger.error(f"Error handling update check: {e}")
                await ws.send_json({"error": "Internal error"})
            finally:
                await ws.close()




        async def handleAutoScan(request):
            await asyncio.sleep(5)
            ws = web.WebSocketResponse()
            await ws.prepare(request)
            decky_plugin.logger.info(f"AutoScan: {self.settings.getSetting('settings', defaultSettings)['autoscan']}")

            debounce_interval = 30
            last_scan_time = 0

            try:
                async with self.scan_lock:
                    while self.settings.getSetting('settings', defaultSettings)['autoscan']:
                        current_time = asyncio.get_event_loop().time()
                        if current_time - last_scan_time >= debounce_interval:
                            decky_shortcuts = scan()
                            last_scan_time = current_time

                            if not decky_shortcuts:
                                decky_plugin.logger.info(f"No shortcuts to send")
                            else:
                                for game in decky_shortcuts.values():
                                    if game.get('appname') is None or game.get('exe') is None:
                                        continue
                                    if ws.closed:
                                        decky_plugin.logger.info("WebSocket connection closed")
                                        break
                                    decky_plugin.logger.info(f"Sending game data to client")
                                    await ws.send_json(game)

                        await asyncio.sleep(1)

                    decky_plugin.logger.info("Exiting AutoScan loop")

            except Exception as e:
                decky_plugin.logger.error(f"Error during AutoScan: {e}")

            finally:
                await ws.close()

            return ws

        async def handleScan(request):
            ws = web.WebSocketResponse()
            await ws.prepare(request)
            decky_plugin.logger.info(f"Called Manual Scan")
            try:
                async with self.scan_lock:
                    decky_shortcuts = scan()
                    if not decky_shortcuts:
                        decky_plugin.logger.info(f"No shortcuts to send")
                    else:
                        for game in decky_shortcuts.values():
                            if game.get('appname') is None or game.get('exe') is None:
                                continue
                            decky_plugin.logger.info(f"Sending game data to client")
                            await ws.send_json(game)

                    if shutil.which("flatpak"):
                        decky_plugin.logger.info("Running Manual Game Save backup...")
                        process = await asyncio.create_subprocess_exec(
                            "flatpak", "run", "com.github.mtkennerly.ludusavi", "--config", f"{decky_user_home}/.var/app/com.github.mtkennerly.ludusavi/config/ludusavi/NSLconfig/", "backup", "--force",
                            stdout=asyncio.subprocess.DEVNULL,
                            stderr=asyncio.subprocess.STDOUT,
                            env={**os.environ, 'LD_LIBRARY_PATH': '/usr/lib:/lib'}
                        )

                        await process.wait()
                        decky_plugin.logger.info("Manual Game Save Backup completed")
                    else:
                        decky_plugin.logger.warning("Flatpak not found, skipping backup process")

                    # Send a message indicating the manual scan has completed
                    await ws.send_json({"status": "Manual scan completed"})

            except Exception as e:
                decky_plugin.logger.error(f"Error during Manual Scan: {e}")

            finally:
                await ws.close()

            return ws


        async def handleCustomSite(request):
            ws = web.WebSocketResponse()
            await ws.prepare(request)
            decky_plugin.logger.info(f"Called Custom Site")
            async for msg in ws:
                decky_plugin.logger.info(msg.data)
                decky_shortcuts = addCustomSite(msg.data)
                if not decky_shortcuts:
                    decky_plugin.logger.info(f"No shortcuts")
                    await ws.send_str("NoShortcuts")
                else:
                    for game in decky_shortcuts.values():
                        if game.get('appname') is None or game.get('exe') is None:
                            continue
                        if ws.closed:
                            decky_plugin.logger.info("WebSocket connection closed")
                            break
                        decky_plugin.logger.info(f"Sending game data to client")
                        try:
                            await ws.send_json(game)
                        except Exception as e:
                            decky_plugin.logger.error(f"Error sending game data: {e}")
                            break
            return ws

        async def handleLogUpdates(request):
            ws = web.WebSocketResponse()
            await ws.prepare(request)
            log_file_path = os.path.join(decky_user_home, 'Downloads', 'NonSteamLaunchers-install.log')

            def start_tail_process():
                return subprocess.Popen(['tail', '-n', '+1', '-f', log_file_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            process = start_tail_process()
            buffer = []

            try:
                while True:
                    if not os.path.exists(log_file_path):
                        process.terminate()
                        await asyncio.sleep(0.1)
                        process = start_tail_process()

                    line = await asyncio.get_event_loop().run_in_executor(None, process.stdout.readline)
                    if not line:
                        if buffer:
                            await ws.send_str('\n'.join(buffer))
                            buffer = []
                        await asyncio.sleep(0.1)
                        continue
                    line = line.decode('utf-8').strip()
                    buffer.append(line)
                    if len(buffer) >= 5:
                        if ws.closed:
                            decky_plugin.logger.info("WebSocket connection closed")
                            break
                        try:
                            await ws.send_str('\n'.join(buffer))
                        except Exception as e:
                            decky_plugin.logger.error(f"Error sending log data: {e}")
                            break
                        buffer = []
            except Exception as e:
                decky_plugin.logger.error(f"Error in handleLogUpdates: {e}")
            finally:
                process.terminate()
                await ws.close()

            return ws


       # WebSocket handler to check launcher status
        async def handle_launcher_status(request):
            ws = web.WebSocketResponse()
            await ws.prepare(request)

            launchers = [
                {"name": 'epicGames', "env_var": 'epic_games_launcher', "label": 'Epic Games'},
                {"name": 'gogGalaxy', "env_var": 'gog_galaxy_launcher', "label": 'Gog Galaxy'},
                {"name": 'uplay', "env_var": 'ubisoft_connect_launcher', "label": 'Ubisoft Connect'},
                {"name": 'battleNet', "env_var": 'bnet_launcher', "label": 'Battle.net'},
                {"name": 'amazonGames', "env_var": 'amazon_launcher', "label": 'Amazon Games'},
                {"name": 'eaApp', "env_var": 'ea_app_launcher', "label": 'EA App'},
                {"name": 'legacyGames', "env_var": 'legacy_launcher', "label": 'Legacy Games'},
                {"name": 'itchIo', "env_var": 'itchio_launcher', "label": 'Itch.io'},
                {"name": 'humbleGames', "env_var": 'humble_launcher', "label": 'Humble Games'},
                {"name": 'indieGala', "env_var": 'indie_launcher', "label": 'IndieGala Client'},
                {"name": 'rockstarGamesLauncher', "env_var": 'rockstar_launcher', "label": 'Rockstar Games Launcher'},
                {"name": 'psPlus', "env_var": 'psplus_launcher', "label": 'Playstation Plus'},
                {"name": 'hoyoPlay', "env_var": 'hoyoplay_launcher', "label": 'HoYoPlay'}
            ]

            installed_launchers = []

            # Path to the env_vars file for Linux
            env_vars_path = f"{decky_user_home}/.config/systemd/user/env_vars"
            env_vars = {}

            try:
                # Check if the env_vars file exists    
                if not os.path.exists(env_vars_path):
                    await ws.send_json({"installedLaunchers": []})
                    await ws.close()
                    return


                # Read the env_vars file
                with open(env_vars_path, 'r') as f:
                    lines = f.readlines()

                # Parse the lines and extract launcher-related environment variables
                for line in lines:
                    if line.startswith('export '):
                        line = line[7:].strip()  # Remove 'export '
                        if '=' in line:
                            name, value = line.split('=', 1)
                            if '_launcher' in name:
                                env_vars[name] = value

                # Iterate over the launchers list to check installed launchers
                for launcher in launchers:
                    launcher_name = launcher["name"]
                    launcher_env_var = launcher["env_var"]
                    if launcher_env_var in env_vars:
                        installed_launchers.append(launcher_name)

                # Send the installed launchers' names as a JSON response
                await ws.send_json({"installedLaunchers": installed_launchers})
                decky_plugin.logger.info(f"Installed Launchers: {installed_launchers}")

            except Exception as e:
                decky_plugin.logger.error(f"Error during launcher check: {e}")
                await ws.send_json({"error": "Internal error during launcher check"})

            finally:
                await ws.close()

        app = web.Application()
        app.router.add_get('/autoscan', handleAutoScan)
        app.router.add_get('/scan', handleScan)
        app.router.add_get('/customSite', handleCustomSite)
        app.router.add_get('/logUpdates', handleLogUpdates)
        app.router.add_get('/check_update', handle_check_update)
        app.router.add_get('/launcher_status', handle_launcher_status)
        app.router.add_get('/monitor_process', handleMonitor)


        runner = web.AppRunner(app)
        await runner.setup()
        decky_plugin.logger.info("Server runner setup")
        site = web.TCPSite(runner, 'localhost', 8675)
        await site.start()
        decky_plugin.logger.info("Server started at http://localhost:8675")




    async def _migration(self):

        decky_plugin.logger.info("Starting migration process")

        # Get the path to the Decky user's home directory
        decky_user_home = decky_plugin.DECKY_USER_HOME

        # Define the paths for the service file, symlink, and NSLGameScanner.py
        service_file = os.path.join(decky_user_home, '.config/systemd/user/nslgamescanner.service')
        symlink = os.path.join(decky_user_home, '.config/systemd/user/default.target.wants/nslgamescanner.service')
        nslgamescanner_py = os.path.join(decky_user_home, '.config/systemd/user/NSLGameScanner.py')

        # Flags to check if any action was taken
        service_file_deleted = False
        symlink_removed = False
        nslgamescanner_py_deleted = False

        # Delete the service file
        if os.path.exists(service_file):
            os.remove(service_file)
            service_file_deleted = True
            decky_plugin.logger.info(f"Deleted service file: {service_file}")
        else:
            decky_plugin.logger.info(f"Service file not found: {service_file}")

        # Remove the symlink
        if os.path.islink(symlink):
            os.unlink(symlink)
            symlink_removed = True
            decky_plugin.logger.info(f"Removed symlink: {symlink}")
        else:
            decky_plugin.logger.info(f"Symlink not found: {symlink}")

        # Delete the NSLGameScanner.py file
        if os.path.exists(nslgamescanner_py):
            os.remove(nslgamescanner_py)
            nslgamescanner_py_deleted = True
            decky_plugin.logger.info(f"Deleted NSLGameScanner.py: {nslgamescanner_py}")
        else:
            decky_plugin.logger.info(f"NSLGameScanner.py not found: {nslgamescanner_py}")

        # Reload the systemd daemon only if any action was taken
        if service_file_deleted or symlink_removed or nslgamescanner_py_deleted:
            subprocess.run(['systemctl', '--user', 'daemon-reload'])
            decky_plugin.logger.info("Reloaded systemd daemon")
        else:
            decky_plugin.logger.info("No changes made, skipping daemon reload")


        if shutil.which("flatpak"):
            decky_plugin.logger.info("Flatpak found, starting migration Game Save backup...")
            try:
                process = await asyncio.create_subprocess_exec(
                    "flatpak", "run", "com.github.mtkennerly.ludusavi", "--config",
                    f"{decky_user_home}/.var/app/com.github.mtkennerly.ludusavi/config/ludusavi/NSLconfig/",
                    "backup", "--force",
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    env={**os.environ, 'LD_LIBRARY_PATH': '/usr/lib:/lib'}
                )

                stdout, stderr = await process.communicate()

                await process.wait()
                decky_plugin.logger.info("Migration Game Save backup completed successfully")

            except Exception as e:
                decky_plugin.logger.error(f"Error during Flatpak migration backup: {e}")

        else:
            decky_plugin.logger.warning("Flatpak not found, skipping backup process")


    async def _unload(self):
        decky_plugin.logger.info("Plugin Unloaded!")
        pass

    async def set_setting(self, key, value):
        self.settings.setSetting(key, value)

    async def get_setting(self, key, default):
        return self.settings.getSetting(key, default)

    async def install(self, selected_options, install_chrome, separate_app_ids, start_fresh, nslgamesaves, update_proton_ge, operation="Install"):
        decky_plugin.logger.info('install was called')

        # Log the arguments for debugging
        decky_plugin.logger.info(f"selected_options: {selected_options}")
        decky_plugin.logger.info(f"separate_app_ids: {separate_app_ids}")
        decky_plugin.logger.info(f"start_fresh: {start_fresh}")
        decky_plugin.logger.info(f"install_chrome: {install_chrome}")
        decky_plugin.logger.info(f"update_proton_ge: {update_proton_ge}")
        decky_plugin.logger.info(f"nslgamesaves: {nslgamesaves}")



        # Convert the selected options mapping to a list of strings
        selected_option_nice = ""
        if selected_options in ['fortnite', 'xboxGamePass', 'geforceNow', 'amazonLuna', 'movieweb', 'netflix', 'hulu', 'disneyPlus', 'amazonPrimeVideo', 'youtube', 'twitch']:
            # Streaming site or game service option
            selected_option_nice = camel_to_title(selected_options).replace('Geforce', 'GeForce').replace('Disney Plus', 'Disney+').replace('movieweb', 'movie-web')
        elif selected_options != 'separateAppIds':
            # Launcher option (excluding the Separate App IDs option)
            selected_option_nice = camel_to_title(selected_options).replace('Ea App', 'EA App').replace('Uplay', 'Ubisoft Connect').replace('Gog Galaxy', 'GOG Galaxy').replace('Battle Net', 'Battle.net').replace('Itch Io', 'itch.io').replace('Humble Games', 'Humble Games Collection').replace('Indie Gala', 'IndieGala').replace('Rockstar', 'Rockstar Games Launcher').replace('Hoyo Play', 'HoYoPlay').replace('Glyph', 'Glyph Launcher').replace('Ps Plus', 'Playstation Plus').replace('DMM', 'DMM Games').replace('Remote Play Whatever', 'RemotePlayWhatever')

        # Log the selected_options_list
        decky_plugin.logger.info(f"selected_option_nice: {selected_option_nice}")


        # Make the script executable
        script_path = os.path.join(DECKY_PLUGIN_DIR, 'NonSteamLaunchers.sh')
        os.chmod(script_path, 0o755)

        # Temporarily disable access control for the X server
        run(['xhost', '+'])

        # Construct the command to run
        command_suffix = ' '.join(
            ([f'"{operation if operation == "Uninstall" else ""} {selected_option_nice}"'] if selected_option_nice != '' else []) +
            ([f'"Chrome"'] if install_chrome else []) +
            ([f'"SEPARATE APP IDS - CHECK THIS TO SEPARATE YOUR PREFIX"'] if separate_app_ids else []) +
            ([f'"Start Fresh"'] if start_fresh else []) +
            ([f'"NSLGameSaves"'] if nslgamesaves else []) +
            ([f'"Update Proton-GE"'] if update_proton_ge else []) +
            [f'"DeckyPlugin"']
        )
        command = f"{script_path} {command_suffix}"


        # Log the command for debugging
        decky_plugin.logger.info(f"Running command: {command}")

        # Set up the environment for the new process
        env = os.environ.copy()
        env['DISPLAY'] = ':0'
        env['XAUTHORITY'] = os.path.join(os.environ['HOME'], '.Xauthority')

        # Run the command in a new xterm window
        xterm_command = f"xterm -e {command}"
        process = Popen(xterm_command, shell=True, env=env)

        # Wait for the script to complete and get the exit code
        exit_code = process.wait()

        # Re-enable access control for the X server
        run(['xhost', '-'])

        # Log the exit code for debugging
        decky_plugin.logger.info(f"Command exit code: {exit_code}")

        return exit_code == 0