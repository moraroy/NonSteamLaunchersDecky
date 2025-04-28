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
from collections import defaultdict
from datetime import datetime
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
        defaultSettings = {"autoscan": False, "customSites": ""}

        # Function to fetch GitHub commit history for patch notes
        async def fetch_patch_notes():
            owner = "moraroy"  # Repository owner
            repo = "NonSteamLaunchersDecky"  # Repository name
            url = f"https://api.github.com/repos/{owner}/{repo}/commits"

            try:
                response = requests.get(url)
                if response.status_code == 200:
                    commits = response.json()
                    return categorize_commits(commits)
                else:
                    decky_plugin.logger.error(f"Failed to fetch commits. HTTP Status Code: {response.status_code}")
                    return {"error": "Failed to fetch patch notes"}
            except Exception as e:
                decky_plugin.logger.error(f"Error fetching patch notes: {e}")
                return {"error": "Error fetching patch notes"}

        # Function to format the commit message for user-friendly patch notes
        def format_patch_note(commit):
            sha = commit['sha']
            message = commit['commit']['message']
            author_name = commit['commit']['author']['name']
            author_date = commit['commit']['author']['date']

            # Format the date into a more user-friendly format
            formatted_date = datetime.strptime(author_date, "%Y-%m-%dT%H:%M:%SZ").strftime("%B %d, %Y")

            # Truncate the message to fit within your red box, limiting it to 100 characters
            truncated_message = (message[:97] + '...') if len(message) > 100 else message

            # Return a single formatted string that can be used for the patch notes
            return {
                "formatted_note": f"- **{truncated_message}** (Commit by {author_name} on {formatted_date}",
                "date": author_date
            }

        # Function to categorize commits (you can customize this as needed)
        def categorize_commits(commits):
            categories = defaultdict(list)

            # Categorize commits based on message keywords (you can adjust as needed)
            for commit in commits:
                message = commit['commit']['message'].lower()

                if "fix" in message:
                    categories["Fixed"].append(format_patch_note(commit))
                elif "add" in message or "new" in message:
                    categories["Added"].append(format_patch_note(commit))
                elif "update" in message or "change" in message:
                    categories["Changed"].append(format_patch_note(commit))
                else:
                    categories["Other"].append(format_patch_note(commit))

            # Limit to the most recent commit in each category (you can adjust this number if needed)
            categories = {category: commits[:1] for category, commits in categories.items()}

            return categories

        # Function to compare versions
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

        # Function to fetch GitHub version info
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

        # WebSocket handler to check for updates and patch notes
        async def handle_check_update(request):
            ws = web.WebSocketResponse()
            await ws.prepare(request)

            try:
                # Fetch and compare the versions
                version_info = await compare_versions()

                # Fetch patch notes
                patch_notes = await fetch_patch_notes()

                # Combine the version info and patch notes
                response_data = {**version_info, "patch_notes": patch_notes}

                # Send the combined response to the frontend
                await ws.send_json(response_data)

            except Exception as e:
                decky_plugin.logger.error(f"Error handling update check: {e}")
                await ws.send_json({"error": "Internal error"})
            finally:
                await ws.close()
                return ws


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
                {"name": 'hoyoPlay', "env_var": 'hoyoplay_launcher', "label": 'HoYoPlay'},
                {"name": 'vkPlay', "env_var": 'vkplay_launcher', "label": 'VK Play'},
                {"name": 'gameJoltClient', "env_var": 'gamejolt_launcher', "label": 'Game Jolt Client'},
                {"name": 'artixGameLauncher', "env_var": 'artixgame_launcher', "label": 'Artix Game Launcher'},
                {"name": 'pokémonTradingCardGameLive', "env_var": 'poketcg_launcher', "label": 'Pokémon Trading Card Game Live'},
                {"name": 'minecraftLauncher', "env_var": 'minecraft_launcher', "label": 'Minecraft Launcher'},
                {"name": 'vfunLauncher', "env_var": 'vfun_launcher', "label": 'VFUN Launcher'},
                {"name": 'tempoLauncher', "env_var": 'tempo_launcher', "label": 'Tempo Launcher'},

                {"name": 'antstreamArcade', "env_var": 'antstream_launcher', "label": 'Antstream Arcade'},

                # exception
                {"name": 'remotePlayWhatever', "env_var": None, "label": 'RemotePlayWhatever', "file_check": f"{decky_user_home}/.local/share/applications/RemotePlayWhatever"}
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
                    launcher_file_check = launcher.get("file_check")

                    # Check if the launcher has a file check (like 'remotePlayWhatever')
                    if launcher_file_check:
                        if os.path.exists(launcher_file_check):
                            installed_launchers.append(launcher_name)

                    # Otherwise, check the environment variable (standard launchers)
                    elif launcher_env_var and launcher_env_var in env_vars:
                        installed_launchers.append(launcher_name)

                # Send the installed launchers' names as a JSON response
                await ws.send_json({"installedLaunchers": installed_launchers})
                decky_plugin.logger.info(f"Installed Launchers: {installed_launchers}")

            except Exception as e:
                decky_plugin.logger.error(f"Error during launcher check: {e}")
                await ws.send_json({"error": "Internal error during launcher check"})

            finally:
                await ws.close()
                return ws

        app = web.Application()
        app.router.add_get('/autoscan', handleAutoScan)
        app.router.add_get('/scan', handleScan)
        app.router.add_get('/customSite', handleCustomSite)
        app.router.add_get('/logUpdates', handleLogUpdates)
        app.router.add_get('/check_update', handle_check_update)
        app.router.add_get('/launcher_status', handle_launcher_status)

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

        # Define the paths for the service file, symlink, NSLGameScanner.py, and the env_vars file
        service_file = os.path.join(decky_user_home, '.config/systemd/user/nslgamescanner.service')
        symlink = os.path.join(decky_user_home, '.config/systemd/user/default.target.wants/nslgamescanner.service')
        nslgamescanner_py = os.path.join(decky_user_home, '.config/systemd/user/NSLGameScanner.py')
        env_vars_file = os.path.join(decky_user_home, '.config/systemd/user/env_vars')

        # Define the required directories leading up to the files
        required_dirs = [
            os.path.join(decky_user_home, '.config/systemd/user'),
            os.path.join(decky_user_home, '.config/systemd/user/default.target.wants')
        ]

        # Ensure required directories exist (but not the files themselves)
        for dir_path in required_dirs:
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)  # Create the directories if they do not exist
                decky_plugin.logger.info(f"Directory created: {dir_path}")
            else:
                decky_plugin.logger.info(f"Directory already exists: {dir_path}")

        # Check if the env_vars file exists, and create it if it doesn't
        if not os.path.exists(env_vars_file):
            with open(env_vars_file, 'w') as file:
                # Create an empty file
                pass
            decky_plugin.logger.info(f"env_vars file created at {env_vars_file}")
        else:
            decky_plugin.logger.info(f"env_vars file already exists at {env_vars_file}")

        # Define the environment variable entries to add
        env_vars_to_add = [
            f'export logged_in_home={decky_user_home}',
            'export chromedirectory="/usr/bin/flatpak"',
            'export chrome_startdir="/usr/bin"',
        ]

        # Read the existing env_vars file to check for duplicates
        with open(env_vars_file, 'r') as file:
            existing_lines = [line.strip() for line in file.readlines()]  # Remove trailing whitespace/newlines

        # Check if the environment variable lines already exist in the file
        for env_var in env_vars_to_add:
            env_var_clean = env_var.strip()  # Clean up leading/trailing spaces

            # Check if the environment variable already exists in the file
            if not any(env_var_clean == line.strip() for line in existing_lines):
                with open(env_vars_file, 'a') as file:
                    file.write(f"{env_var_clean}\n")
                decky_plugin.logger.info(f"Added {env_var_clean} to {env_vars_file}")
            else:
                decky_plugin.logger.info(f"{env_var_clean} already exists in {env_vars_file}")

        # Now process the Steam ID from loginusers.vdf
        paths = [
            os.path.join(decky_user_home, ".steam/root/config/loginusers.vdf"),
            os.path.join(decky_user_home, ".local/share/Steam/config/loginusers.vdf")
        ]

        # Find the first existing file
        file_path = next((p for p in paths if os.path.isfile(p)), None)

        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                users = re.findall(r'"(\d{17})"\s*{([^}]+)}', content, re.DOTALL)

                max_timestamp = 0
                current_user = ""
                current_steamid = ""

                for steamid, block in users:
                    account_match = re.search(r'"AccountName"\s+"([^"]+)"', block)
                    timestamp_match = re.search(r'"Timestamp"\s+"(\d+)"', block)

                    if account_match and timestamp_match:
                        account = account_match.group(1)
                        timestamp = int(timestamp_match.group(1))

                        if timestamp > max_timestamp:
                            max_timestamp = timestamp
                            current_user = account
                            current_steamid = steamid

                if current_user:
                    decky_plugin.logger.info(f"SteamID: {current_steamid}")
                    steamid3 = int(current_steamid) - 76561197960265728
                    userdata_path = os.path.join(decky_user_home, f".steam/root/userdata/{steamid3}")

                    if os.path.isdir(userdata_path):
                        decky_plugin.logger.info(f"Found userdata folder for user with SteamID {current_steamid}: {userdata_path}")

                        # Before writing steamid3, check if it already exists
                        if f'export steamid3={steamid3}' not in existing_lines:
                            with open(env_vars_file, "a") as file:
                                file.write(f'export steamid3={steamid3}\n')
                            decky_plugin.logger.info(f'Set steamid3="{steamid3}" in {env_vars_file}')
                        else:
                            decky_plugin.logger.info(f"steamid3={steamid3} already exists in {env_vars_file}")
                    else:
                        decky_plugin.logger.info(f"Could not find userdata folder for user with SteamID {current_steamid}")
                else:
                    decky_plugin.logger.info("No valid users found in the file.")
            except Exception as e:
                decky_plugin.logger.error(f"Error processing the loginusers.vdf file: {e}")
        else:
            decky_plugin.logger.info("Could not find loginusers.vdf file")
#End of Env_vars first run




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

#install chrome

        # Set the LD_LIBRARY_PATH to ensure correct OpenSSL libraries are used
        env_vars = {**os.environ, 'LD_LIBRARY_PATH': '/usr/lib:/lib'}

        # Check if Google Chrome is already installed and get the installation details
        check_chrome_command = "flatpak list | grep com.google.Chrome"
        result_check_chrome = subprocess.run(
            check_chrome_command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env_vars
        )

        result_output = result_check_chrome.stdout.decode().strip()

        if result_output:
            decky_plugin.logger.info(f"Google Chrome is already installed: {result_output}")
            return  # Skip installation if Chrome is already installed

        # Check if the Flathub repository exists
        check_flathub_command = "flatpak remote-list | grep flathub &> /dev/null"
        result_check_flathub = subprocess.run(
            check_flathub_command,
            shell=True,
            env=env_vars
        )

        if result_check_flathub.returncode != 0:
            decky_plugin.logger.info("Flathub repository not found. Adding Flathub repository.")
            add_flathub_command = "flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo"
            subprocess.run(add_flathub_command, shell=True, env=env_vars)

        # Install Google Chrome for the user
        decky_plugin.logger.info("Google Chrome is not installed. Proceeding with installation.")
        flatpak_install_command = "flatpak install --user flathub com.google.Chrome -y"
        result_install = subprocess.run(
            flatpak_install_command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env_vars
        )

        if result_install.returncode == 0:
            decky_plugin.logger.info("Google Chrome installed successfully!")

            # Run the flatpak override command
            override_command = "flatpak --user override --filesystem=/run/udev:ro com.google.Chrome"
            result_override = subprocess.run(
                override_command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env_vars
            )

            if result_override.returncode == 0:
                decky_plugin.logger.info("Flatpak override applied successfully.")
            else:
                decky_plugin.logger.error("Failed to apply Flatpak override.")
                decky_plugin.logger.error(f"Error Output: {result_override.stderr.decode()}")

        else:
            decky_plugin.logger.error("Installation failed.")
            decky_plugin.logger.error(f"Error Output: {result_install.stderr.decode()}")
            decky_plugin.logger.error(f"Standard Output: {result_install.stdout.decode()}")
            decky_plugin.logger.error(f"Exit Code: {result_install.returncode}")

            if "no permission" in result_install.stderr.decode().lower():
                decky_plugin.logger.error("It seems like there might be a permissions issue. Please check your user permissions.")
            elif "cannot find" in result_install.stderr.decode().lower():
                decky_plugin.logger.error("There might be an issue with the Flatpak repository or package name. Please check if the repository is added correctly.")
            else:
                decky_plugin.logger.error("An unknown error occurred during installation.")


#end of install chrome





    async def _unload(self):
        decky_plugin.logger.info("Plugin Unloaded!")
        pass

    async def set_setting(self, key, value):
        self.settings.setSetting(key, value)

    async def get_setting(self, key, default):
        return self.settings.getSetting(key, default)

    async def install(self, selected_options, install_chrome, separate_app_ids, start_fresh, nslgamesaves, update_proton_ge, note, up, operation="Install"):
        decky_plugin.logger.info('install was called')

        # Log the arguments for debugging
        decky_plugin.logger.info(f"selected_options: {selected_options}")
        decky_plugin.logger.info(f"separate_app_ids: {separate_app_ids}")
        decky_plugin.logger.info(f"start_fresh: {start_fresh}")
        decky_plugin.logger.info(f"install_chrome: {install_chrome}")
        decky_plugin.logger.info(f"update_proton_ge: {update_proton_ge}")
        decky_plugin.logger.info(f"nslgamesaves: {nslgamesaves}")
        decky_plugin.logger.info(f"note: {note}")
        decky_plugin.logger.info(f"up: {up}")


        # Convert the selected options mapping to a list of strings
        selected_option_nice = ""
        if selected_options in ['fortnite', 'xboxGamePass', 'geforceNow', 'amazonLuna', 'movieweb', 'netflix', 'hulu', 'disneyPlus', 'amazonPrimeVideo', 'youtube', 'twitch']:
            # Streaming site or game service option
            selected_option_nice = camel_to_title(selected_options).replace('Geforce', 'GeForce').replace('Disney Plus', 'Disney+').replace('movieweb', 'movie-web')
        elif selected_options != 'separateAppIds':
            # Launcher option (excluding the Separate App IDs option)
            selected_option_nice = camel_to_title(selected_options).replace('Ea App', 'EA App').replace('Uplay', 'Ubisoft Connect').replace('Gog Galaxy', 'GOG Galaxy').replace('Battle Net', 'Battle.net').replace('Itch Io', 'itch.io').replace('Humble Games', 'Humble Games Collection').replace('Indie Gala', 'IndieGala').replace('Rockstar', 'Rockstar Games Launcher').replace('Hoyo Play', 'HoYoPlay').replace('Vk Play', 'VK Play').replace('Glyph', 'Glyph Launcher').replace('Ps Plus', 'Playstation Plus').replace('DMM', 'DMM Games').replace('Remote Play Whatever', 'RemotePlayWhatever').replace('Pok Mon Trading Card Game Live', 'Pokémon Trading Card Game Live').replace('Vfun Launcher', 'VFUN Launcher')

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
            ([f'"❤️"'] if note else []) +
            ([f'"Up"'] if up else []) +
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