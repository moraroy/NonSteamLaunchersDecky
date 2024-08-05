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
import aiofiles
from aiohttp import web
from decky_plugin import DECKY_PLUGIN_DIR
from py_modules.lib.scanner import scan, addCustomSite
from settings import SettingsManager
from subprocess import Popen, run 

# Set up logging
logging.basicConfig(level=logging.DEBUG)

def camel_to_title(s):
    # Split the string into words using a regular expression
    words = re.findall(r'[A-Z]?[a-z]+|[A-Z]+(?=[A-Z]|$)', s)
    # Convert the first character of each word to uppercase and join the words with spaces
    return ' '.join(word.capitalize() for word in words)

class Plugin:
    async def _main(self):
        decky_plugin.logger.info("This is _main being called")
        self.settings = SettingsManager(name="config", settings_directory=decky_plugin.DECKY_PLUGIN_SETTINGS_DIR)
        # Get the path to the Decky user's home directory
        decky_user_home = decky_plugin.DECKY_USER_HOME
        # Set default settings for fallback
        defaultSettings = {"autoscan": False, "customSites": ""}

        async def handleAutoScan(request):
            await asyncio.sleep(5)
            ws = web.WebSocketResponse()
            await ws.prepare(request)
            decky_plugin.logger.info(f"AutoScan: {self.settings.getSetting('settings', defaultSettings)['autoscan']}")
            while (self.settings.getSetting('settings', defaultSettings)['autoscan'] is True):
                decky_shortcuts = scan()
                if self.settings.getSetting('settings', defaultSettings)['autoscan'] is False:
                    decky_plugin.logger.info(f"Autoscan setting is false, stopping")
                    return ws
                if not decky_shortcuts:
                    decky_plugin.logger.info(f"No shortcuts to send")
                    await asyncio.sleep(5)  # Wait for 5 seconds before the next iteration
                    continue
                for game in decky_shortcuts.values():
                    if game.get('appname') is None or game.get('exe') is None:
                        continue
                    decky_plugin.logger.info(f"Sending game data to client")
                    # Send the game data to the client
                    await ws.send_json(game)
                await asyncio.sleep(5)
            decky_plugin.logger.info(f"Autoscan setting is false, stopping")
            return ws
        
        async def handleScan(request):
            ws = web.WebSocketResponse()
            await ws.prepare(request)
            decky_plugin.logger.info(f"Called Manual Scan")
            decky_shortcuts = scan()
            if not decky_shortcuts:
                decky_plugin.logger.info(f"No shortcuts")
            else:
                for game in decky_shortcuts.values():
                    if game.get('appname') is None or game.get('exe') is None:
                        continue
                    decky_plugin.logger.info(f"Sending game data to client")
                    # Send the game data to the client
                    await ws.send_json(game)
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
                        decky_plugin.logger.info(f"Sending game data to client")
                        # Send the game data to the client
                        await ws.send_json(game)
            return ws
        
        async def handleLogUpdates(request):
            ws = web.WebSocketResponse()
            await ws.prepare(request)
            self.log_ws = ws
            async for msg in ws:
                pass
            return ws

        # Create the server application
        app = web.Application()
        app.router.add_get('/autoscan', handleAutoScan)
        app.router.add_get('/scan', handleScan)
        app.router.add_get('/customSite', handleCustomSite)
        app.router.add_get('/logUpdates', handleLogUpdates)

        # Run the server
        runner = web.AppRunner(app)
        await runner.setup()
        decky_plugin.logger.info("Server runner setup")
        site = web.TCPSite(runner, 'localhost', 8675)
        await site.start()
        decky_plugin.logger.info("Server started at http://localhost:8675")

    async def _migration(self):
        decky_plugin.logger.info("No migration needed")
        
    async def _unload(self):
        decky_plugin.logger.info("Plugin Unloaded!")
        pass

    async def set_setting(self, key, value):
        self.settings.setSetting(key, value)

    async def get_setting(self, key, default):
        return self.settings.getSetting(key, default)
        
    async def install(self, selected_options, install_chrome, separate_app_ids, start_fresh, operation="Install"):
        decky_plugin.logger.info('install was called')

        # Log the arguments for debugging
        decky_plugin.logger.info(f"selected_options: {selected_options}")
        decky_plugin.logger.info(f"separate_app_ids: {separate_app_ids}")
        decky_plugin.logger.info(f"start_fresh: {start_fresh}")
        decky_plugin.logger.info(f"install_chrome: {install_chrome}")

        # Convert the selected options mapping to a list of strings
        selected_option_nice = ""
        if selected_options in ['fortnite', 'xboxGamePass', 'geforceNow', 'amazonLuna', 'movieweb', 'netflix', 'hulu', 'disneyPlus', 'amazonPrimeVideo', 'youtube', 'twitch']:
            # Streaming site or game service option
            selected_option_nice = camel_to_title(selected_options).replace('Geforce', 'GeForce').replace('Disney Plus', 'Disney+').replace('movieweb', 'movie-web')
        elif selected_options != 'separateAppIds':
            # Launcher option (excluding the Separate App IDs option)
            selected_option_nice = camel_to_title(selected_options).replace('Ea App', 'EA App').replace('Uplay', 'Ubisoft Connect').replace('Gog Galaxy', 'GOG Galaxy').replace('Battle Net', 'Battle.net').replace('Itch Io', 'itch.io').replace('Humble Games', 'Humble Games Collection').replace('Indie Gala', 'IndieGala').replace('Rockstar', 'Rockstar Games Launcher').replace('Glyph', 'Glyph Launcher').replace('Ps Plus', 'Playstation Plus').replace('DMM', 'DMM Games').replace('Remote Play Whatever', 'RemotePlayWhatever')

        decky_plugin.logger.info(f"selected_option_nice: {selected_option_nice}")

        script_path = os.path.join(DECKY_PLUGIN_DIR, 'NonSteamLaunchers.sh')
        os.chmod(script_path, 0o755)
        run(['xhost', '+'])
        command_suffix = ' '.join(([f'"{operation if operation == "Uninstall" else ""} {selected_option_nice}"'] if selected_option_nice != '' else []) + ([f'"Chrome"'] if install_chrome else []) + ([f'"SEPARATE APP IDS - CHECK THIS TO SEPARATE YOUR PREFIX"'] if separate_app_ids else []) + ([f'"Start Fresh"'] if start_fresh else []) + [f'"DeckyPlugin"'])
        command = f"{script_path} {command_suffix}"
        decky_plugin.logger.info(f"Running command: {command}")
        env = os.environ.copy()
        env['DISPLAY'] = ':0'
        env['XAUTHORITY'] = os.path.join(os.environ['HOME'], '.Xauthority')
        run(['xhost', '+'])
        xterm_command = f"xterm -e {command}"
        process = Popen(xterm_command, shell=True, env=env)

        # Read the log file in real-time and send updates
        log_file_path = '/home/deck/Downloads/NonSteamLaunchers-install.log'
        async with aiofiles.open(log_file_path, 'r') as log_file:
            while True:
                line = await log_file.readline()
                if not line:
                    await asyncio.sleep(1)
                    continue
                if hasattr(self, 'log_ws'):
                    await self.log_ws.send_str(line)

        exit_code = process.wait()
        run(['xhost', '-'])
        decky_plugin.logger.info(f"Command exit code: {exit_code}")

        if exit_code == 0:
            return True
        else:
            return False