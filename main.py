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
import platform
import desktopC
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

            debounce_interval = 30
            last_scan_time = 0
            processed_games = set()

            try:
                async with self.scan_lock:
                    while self.settings.getSetting('settings', defaultSettings)['autoscan']:
                        current_time = asyncio.get_event_loop().time()
                        if current_time - last_scan_time >= debounce_interval:
                            decky_shortcuts, removed_apps = scan()
                            last_scan_time = current_time

                            sent_games = []

                            if removed_apps:
                                await ws.send_json({"removed_games": removed_apps})

                            if not decky_shortcuts:
                                decky_plugin.logger.info("No shortcuts to send")
                            else:
                                for game in decky_shortcuts.values():
                                    if game.get("appname") is None or game.get("exe") is None:
                                        continue

                                    if ws.closed:
                                        decky_plugin.logger.info("WebSocket connection closed")
                                        break

                                    decky_plugin.logger.info("Sending game data to client")
                                    await ws.send_json(game)
                                    sent_games.append(game)

                            # Only process new games for desktopC
                            if sent_games:
                                await asyncio.sleep(2)
                                logged_in_home = decky_plugin.DECKY_USER_HOME
                                for game in sent_games:
                                    cache_key = (game.get("appname"), game.get("exe"))
                                    if cache_key not in processed_games:
                                        desktopC.create_exec_line_from_entry(logged_in_home, game)
                                        processed_games.add(cache_key)

                        await asyncio.sleep(1)

                    decky_plugin.logger.info("Exiting AutoScan loop")

                    try:
                        import desktopTM
                        decky_plugin.logger.info("desktopTM imported successfully")
                    except ImportError:
                        decky_plugin.logger.warning(
                            "desktopTM module not found, skipping import"
                        )

            except Exception as e:
                decky_plugin.logger.error(f"Error during AutoScan: {e}")

            finally:
                await ws.close()

            return ws


        async def handleScan(request):
            ws = web.WebSocketResponse()
            await ws.prepare(request)
            decky_plugin.logger.info("Called Manual Scan")

            sent_games = []

            try:
                async with self.scan_lock:
                    decky_shortcuts, removed_apps = scan()

                    if removed_apps and not ws.closed:
                        await ws.send_json({"removed_games": removed_apps})

                    if not decky_shortcuts:
                        decky_plugin.logger.info("No shortcuts to send")
                    else:
                        for game in decky_shortcuts.values():
                            if game.get("appname") is None or game.get("exe") is None:
                                continue

                            sent_games.append(game)
                            decky_plugin.logger.info(
                                f"Sending game data to client: {game.get('appname')}"
                            )

                            if not ws.closed:
                                await ws.send_json(game)

                    if shutil.which("flatpak"):
                        decky_plugin.logger.info("Running Manual Game Save backup...")
                        process = await asyncio.create_subprocess_exec(
                            "flatpak",
                            "run",
                            "com.github.mtkennerly.ludusavi",
                            "--config",
                            f"{decky_user_home}/.var/app/com.github.mtkennerly.ludusavi/config/ludusavi/NSLconfig/",
                            "backup",
                            "--force",
                            stdout=asyncio.subprocess.DEVNULL,
                            stderr=asyncio.subprocess.STDOUT,
                            env={**os.environ, "LD_LIBRARY_PATH": "/usr/lib:/lib"},
                        )

                        try:
                            await asyncio.wait_for(process.wait(), timeout=300)
                            decky_plugin.logger.info("Manual Game Save Backup completed")
                        except asyncio.TimeoutError:
                            decky_plugin.logger.error("Manual Game Save Backup timed out")
                    else:
                        decky_plugin.logger.warning("Flatpak not found, skipping backup process")

                    if not ws.closed:
                        await ws.send_json({"status": "Manual scan completed"})

            except Exception as e:
                decky_plugin.logger.error(f"Error during Manual Scan: {e}")

            finally:
                logged_in_home = decky_plugin.DECKY_USER_HOME
                for entry in sent_games:
                    desktopC.create_exec_line_from_entry(logged_in_home, entry)

                if not ws.closed:
                    await ws.close()

            return ws






        async def handleCustomSite(request):
            ws = web.WebSocketResponse()
            await ws.prepare(request)

            decky_plugin.logger.info(f"Called Custom Site")

            env_vars = {**os.environ, 'LD_LIBRARY_PATH': '/usr/lib:/lib'}

            def check_and_install_flatpak(package_name: str, flatpak_id: str, override_paths: list = []):
                # Check if flatpak package installed
                check_cmd = f"flatpak list | grep {flatpak_id}"
                result_check = subprocess.run(
                    check_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env_vars
                )
                installed = bool(result_check.stdout.decode().strip())

                # Check/add Flathub repo
                check_flathub_cmd = "flatpak remote-list | grep flathub &> /dev/null"
                result_flathub = subprocess.run(check_flathub_cmd, shell=True, env=env_vars)
                if result_flathub.returncode != 0:
                    decky_plugin.logger.info("Flathub repository not found. Adding Flathub repository.")
                    add_flathub_cmd = "flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo"
                    subprocess.run(add_flathub_cmd, shell=True, env=env_vars)

                if installed:
                    decky_plugin.logger.info(f"{package_name} is already installed: {result_check.stdout.decode().strip()}")
                else:
                    decky_plugin.logger.info(f"{package_name} is not installed. Proceeding with installation.")
                    install_cmd = f"flatpak install --user flathub {flatpak_id} -y"
                    result_install = subprocess.run(
                        install_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env_vars
                    )
                    if result_install.returncode != 0:
                        decky_plugin.logger.error(f"Installation failed for {package_name}.")
                        decky_plugin.logger.error(f"Error Output: {result_install.stderr.decode()}")
                        decky_plugin.logger.error(f"Standard Output: {result_install.stdout.decode()}")
                        decky_plugin.logger.error(f"Exit Code: {result_install.returncode}")

                        if "no permission" in result_install.stderr.decode().lower():
                            decky_plugin.logger.error("It seems like there might be a permissions issue. Please check your user permissions.")
                        elif "cannot find" in result_install.stderr.decode().lower():
                            decky_plugin.logger.error("There might be an issue with the Flatpak repository or package name. Please check if the repository is added correctly.")
                        else:
                            decky_plugin.logger.error("An unknown error occurred during installation.")
                        return False

                # Apply overrides regardless of install or not
                for path in override_paths:
                    override_cmd = f"flatpak --user override --filesystem={path} {flatpak_id}"
                    result_override = subprocess.run(
                        override_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env_vars
                    )
                    if result_override.returncode == 0:
                        decky_plugin.logger.info(f"Flatpak override applied successfully for {path}.")
                    else:
                        decky_plugin.logger.error(f"Failed to apply Flatpak override for {path}.")
                        decky_plugin.logger.error(f"Error Output: {result_override.stderr.decode()}")
                        # Optionally handle failure here

                return True

            async for msg in ws:
                decky_plugin.logger.info(f"Received WS message: {msg.data}")

                try:
                    data = json.loads(msg.data)
                    sites = data.get("sites")
                    selected_browser = data.get("selectedBrowser")

                    decky_plugin.logger.info(f"Selected Browser: {selected_browser}")
                    decky_plugin.logger.info(f"Sites data: {sites}")

                    # Browser install logic
                    if selected_browser:
                        browser_lower = selected_browser.lower()
                        if "chrome" in browser_lower:
                            check_and_install_flatpak(
                                "Google Chrome",
                                "com.google.Chrome",
                                override_paths=["/run/udev:ro"]
                            )
                        elif "firefox" in browser_lower:
                            check_and_install_flatpak(
                                "Mozilla Firefox",
                                "org.mozilla.firefox",
                                override_paths=["/run/udev:ro"]
                            )
                        elif "edge" in browser_lower:
                            check_and_install_flatpak(
                                "Microsoft Edge",
                                "com.microsoft.Edge",
                                override_paths=["/run/udev:ro"]
                            )
                        elif "brave" in browser_lower:
                            check_and_install_flatpak(
                                "Brave",
                                "com.brave.Browser",
                                override_paths=["/run/udev:ro"]
                            )

                    for site in sites:
                        site["browser"] = selected_browser

                    # Now proceed with adding custom sites
                    decky_shortcuts = addCustomSite(sites, selected_browser)

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

                except json.JSONDecodeError as e:
                    decky_plugin.logger.error(f"Error decoding JSON: {e}")
                    await ws.send_str("Invalid JSON")
                    continue

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
                {"name": 'remotePlayWhatever', "env_var": None, "label": 'RemotePlayWhatever', "file_check": f"{decky_user_home}/.local/share/applications/RemotePlayWhatever"},
                {"name": 'nvidiaGeForcenow', "env_var": None, "label": 'NVIDIA GeForce NOW', "file_check": f"{decky_user_home}/.local/share/flatpak/app/com.nvidia.geforcenow/x86_64/master/active/files/bin/GeForceNOW"},
                {"name": 'moonlightGameStreaming', "env_var": None, "label": 'Moonlight', "file_check": f"{decky_user_home}/.local/share/flatpak/app/com.moonlight_stream.Moonlight/x86_64/stable/active/files/bin/moonlight"},
                {"name": 'hytale', "env_var": None, "label": 'Hytale', "file_check": f"{decky_user_home}/.local/share/flatpak/app/com.hypixel.HytaleLauncher/current/active/files/bin/hytale-launcher-wrapper"},
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

        # Required directories
        required_dirs = [
            os.path.join(decky_user_home, '.config/systemd/user'),
            os.path.join(decky_user_home, '.config/systemd/user/default.target.wants')
        ]

        for dir_path in required_dirs:
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
                decky_plugin.logger.info(f"Directory created: {dir_path}")
            else:
                decky_plugin.logger.info(f"Directory already exists: {dir_path}")

        # Create env_vars file if missing
        if not os.path.exists(env_vars_file):
            with open(env_vars_file, 'w', encoding='utf-8') as file:
                pass
            decky_plugin.logger.info(f"env_vars file created at {env_vars_file}")
        else:
            decky_plugin.logger.info(f"env_vars file already exists at {env_vars_file}")

        env_vars_to_add = [
            f'export logged_in_home={decky_user_home}',
            'export chromedirectory="/usr/bin/flatpak"',
            'export chrome_startdir="/usr/bin"',
        ]

        try:
            with open(env_vars_file, 'r', encoding='utf-8') as file:
                existing_lines = [line.strip() for line in file.readlines()]
        except Exception as e:
            decky_plugin.logger.error(f"Error reading env_vars file: {e}")
            existing_lines = []

        for env_var in env_vars_to_add:
            env_var_clean = env_var.strip()
            if env_var_clean not in existing_lines:
                try:
                    with open(env_vars_file, 'a', encoding='utf-8') as file:
                        file.write(f"{env_var_clean}\n")
                    decky_plugin.logger.info(f"Added {env_var_clean} to {env_vars_file}")
                except Exception as e:
                    decky_plugin.logger.error(f"Error writing to env_vars file: {e}")
            else:
                decky_plugin.logger.info(f"{env_var_clean} already exists in {env_vars_file}")

        system = platform.system()
        current_user = ""
        current_steamid = ""
        steamid3 = None

        # --- Windows Steam detection ---
        if system == "Windows":
            try:
                import winreg
            except ImportError:
                decky_plugin.logger.error("Failed to import winreg on Windows environment")
                winreg = None

            possible_paths = [
                os.path.join(os.environ.get("PROGRAMFILES(X86)", r"C:\Program Files (x86)"), "Steam", "config", "loginusers.vdf"),
                os.path.join(os.environ.get("PROGRAMFILES", r"C:\Program Files"), "Steam", "config", "loginusers.vdf"),
            ]
            file_path = next((p for p in possible_paths if os.path.isfile(p)), None)

            if file_path:
                decky_plugin.logger.info(f"Found loginusers.vdf: {file_path}")
                try:
                    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                        content = f.read()
                    users = re.findall(r'"(\d{17})"\s*{([^}]+)}', content, re.DOTALL)

                    max_timestamp = 0
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
                except Exception as e:
                    decky_plugin.logger.error(f"Error processing loginusers.vdf: {e}")

            # Registry fallback if vdf missing or empty
            if not current_steamid and winreg:
                try:
                    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam\ActiveProcess")
                    steamid_reg, _ = winreg.QueryValueEx(key, "SteamID")
                    current_steamid = str(steamid_reg)
                    current_user = "Unknown"
                    decky_plugin.logger.info(f"SteamID64 found from registry: {current_steamid}")
                except FileNotFoundError:
                    decky_plugin.logger.warning("No SteamID found in registry")
                except Exception as e:
                    decky_plugin.logger.error(f"Registry read error: {e}")

        # --- Linux / macOS Steam detection ---
        else:
            possible_paths = [
                os.path.join(decky_user_home, ".steam", "root", "config", "loginusers.vdf"),
                os.path.join(decky_user_home, ".local", "share", "Steam", "config", "loginusers.vdf")
            ]
            file_path = next((p for p in possible_paths if os.path.isfile(p)), None)

            if file_path:
                decky_plugin.logger.info(f"Found loginusers.vdf: {file_path}")
                try:
                    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                        content = f.read()
                    users = re.findall(r'"(\d{17})"\s*{([^}]+)}', content, re.DOTALL)

                    max_timestamp = 0
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
                except Exception as e:
                    decky_plugin.logger.error(f"Error processing loginusers.vdf: {e}")

        # Convert to SteamID3
        if current_steamid:
            try:
                steamid3 = int(current_steamid) - 76561197960265728
                if f'export steamid3={steamid3}' not in existing_lines:
                    with open(env_vars_file, "a", encoding="utf-8") as file:
                        file.write(f'export steamid3={steamid3}\n')
                    decky_plugin.logger.info(f"Set steamid3={steamid3} in {env_vars_file}")
                else:
                    decky_plugin.logger.info(f"steamid3={steamid3} already exists in {env_vars_file}")
            except Exception as e:
                decky_plugin.logger.error(f"Error converting SteamID to steamid3: {e}")

        # --- Clean up service files ---
        service_file_deleted = False
        symlink_removed = False
        nslgamescanner_py_deleted = False

        if os.path.exists(service_file):
            try:
                os.remove(service_file)
                service_file_deleted = True
                decky_plugin.logger.info(f"Deleted service file: {service_file}")
            except Exception as e:
                decky_plugin.logger.error(f"Error deleting service file: {e}")

        if os.path.islink(symlink):
            try:
                os.unlink(symlink)
                symlink_removed = True
                decky_plugin.logger.info(f"Removed symlink: {symlink}")
            except Exception as e:
                decky_plugin.logger.error(f"Error removing symlink: {e}")

        if os.path.exists(nslgamescanner_py):
            try:
                os.remove(nslgamescanner_py)
                nslgamescanner_py_deleted = True
                decky_plugin.logger.info(f"Deleted NSLGameScanner.py: {nslgamescanner_py}")
            except Exception as e:
                decky_plugin.logger.error(f"Error deleting NSLGameScanner.py: {e}")

        if service_file_deleted or symlink_removed or nslgamescanner_py_deleted:
            if system != "Windows":
                try:
                    subprocess.run(['systemctl', '--user', 'daemon-reload'], check=True)
                    decky_plugin.logger.info("Reloaded systemd daemon")
                except Exception as e:
                    decky_plugin.logger.error(f"Error reloading systemd daemon: {e}")
            else:
                decky_plugin.logger.info("Windows detected; skipping systemd daemon reload")
        else:
            decky_plugin.logger.info("No changes made, skipping daemon reload")

        # --- Flatpak backup for Linux ---
        if system != "Windows":
            if shutil.which("flatpak"):
                decky_plugin.logger.info("Flatpak found, starting backup...")
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
                    decky_plugin.logger.error(f"Error during Flatpak backup: {e}")
            else:
                decky_plugin.logger.warning("Flatpak not found, skipping backup process")
        else:
            decky_plugin.logger.info("Windows detected; skipping Flatpak migration backup")

        decky_plugin.logger.info("Migration process completed")


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
            selected_option_nice = camel_to_title(selected_options).replace('Ea App', 'EA App').replace('Uplay', 'Ubisoft Connect').replace('Gog Galaxy', 'GOG Galaxy').replace('Battle Net', 'Battle.net').replace('Itch Io', 'itch.io').replace('Humble Games', 'Humble Games Collection').replace('Indie Gala', 'IndieGala').replace('Rockstar', 'Rockstar Games Launcher').replace('Hoyo Play', 'HoYoPlay').replace('Vk Play', 'VK Play').replace('Glyph', 'Glyph Launcher').replace('Ps Plus', 'Playstation Plus').replace('DMM', 'DMM Games').replace('Remote Play Whatever', 'RemotePlayWhatever').replace('Pok Mon Trading Card Game Live', 'Pokémon Trading Card Game Live').replace('Vfun Launcher', 'VFUN Launcher').replace('Nvidia Ge Forcenow', 'NVIDIA GeForce NOW')


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
        env.update({
            'DISPLAY': ':0',
            'XAUTHORITY': os.path.join(os.environ['HOME'], '.Xauthority'),
            'PATH': '/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin',
            'LD_LIBRARY_PATH': '/usr/lib:/lib:/usr/lib32:/lib32'
        })

        # Check if xterm exists before attempting to use it
        try:
            xterm_check = subprocess.run(['which', 'xterm'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if xterm_check.returncode == 0:
                # xterm is found, use it only if necessary
                decky_plugin.logger.info("xterm found. Running command in xterm.")
                process = Popen(f"xterm -e {command}", shell=True, env=env)
            else:
                # xterm not found, run command directly
                decky_plugin.logger.info("xterm not found. Running command directly.")
                process = Popen(command, shell=True, env=env)
        except Exception as e:
            decky_plugin.logger.error(f"Error checking xterm: {e}")
            # Fallback to running the command directly if there was an error checking xterm
            decky_plugin.logger.info("Error checking xterm, falling back to subprocess.")
            process = Popen(command, shell=True, env=env)

        # Wait for the script to complete and get the exit code
        exit_code = process.wait()

        # Re-enable access control for the X server
        run(['xhost', '-'])

        # Log the exit code for debugging
        decky_plugin.logger.info(f"Command exit code: {exit_code}")

        return exit_code == 0
