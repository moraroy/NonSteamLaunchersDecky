import os
import re
import json
import shutil
import platform
import urllib.parse
import decky_plugin
from scanners.game_tracker import track_game

HEROIC_LAUNCH_URL = re.compile(r'heroic://launch(?:\?[^"\s]*appName=([^&"\s]+)|/[^/"\s]+/([^/?"\s]+))')


def find_heroic(logged_in_home):
    # Prefer a distro-provided Heroic (e.g. ArmadaOS /usr/bin/heroic), then the AppImage NSL installs
    heroic_exe = shutil.which("heroic")
    if not heroic_exe and os.path.isfile("/usr/bin/heroic"):
        heroic_exe = "/usr/bin/heroic"
    if not heroic_exe:
        heroic_appimage = f"{logged_in_home}/.local/share/applications/Heroic.AppImage"
        if os.path.isfile(heroic_appimage):
            heroic_exe = heroic_appimage
    return heroic_exe


def read_heroic_json(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def get_heroic_games(config_dir):
    """(appName, runner, title) for each game installed through Heroic's Epic, GOG, Amazon and sideload stores"""
    games = []

    legendary = read_heroic_json(f"{config_dir}/legendaryConfig/legendary/installed.json") or {}
    for app_name, info in legendary.items():
        if not info.get("is_dlc"):
            games.append((app_name, "legendary", info.get("title") or app_name))

    gog_library = read_heroic_json(f"{config_dir}/store_cache/gog_library.json") or {}
    gog_titles = {g.get("app_name"): g.get("title") for g in gog_library.get("games", [])}
    gog_installed = read_heroic_json(f"{config_dir}/gog_store/installed.json") or {}
    for info in gog_installed.get("installed", []):
        app_name = info.get("appName")
        if app_name and not info.get("is_dlc"):
            title = gog_titles.get(app_name) or os.path.basename((info.get("install_path") or "").rstrip("/"))
            games.append((app_name, "gog", title or app_name))

    nile_library = read_heroic_json(f"{config_dir}/nile_config/nile/library.json") or []
    nile_titles = {g.get("id"): (g.get("product") or {}).get("title") for g in nile_library}
    for info in read_heroic_json(f"{config_dir}/nile_config/nile/installed.json") or []:
        app_name = info.get("id")
        if app_name:
            title = nile_titles.get(app_name) or os.path.basename((info.get("path") or "").rstrip("/"))
            games.append((app_name, "nile", title or app_name))

    sideloaded = read_heroic_json(f"{config_dir}/sideload_apps/library.json") or {}
    for info in sideloaded.get("games", []):
        if info.get("is_installed") and info.get("app_name"):
            games.append((info["app_name"], "sideload", info.get("title") or info["app_name"]))

    return games


def heroic_scanner(logged_in_home, create_new_entry, existing_shortcuts, update_shortcut):
    if platform.system() == "Windows":
        decky_plugin.logger.info("Running on Windows. Skipping Heroic scanner.")
        return

    # Add --no-gui to game shortcuts that go through Heroic (ours or Heroic's own "Add to Steam"), so Heroic
    # runs the game without opening its window
    existing_heroic_games = set()
    for s in existing_shortcuts:
        options = s.get('LaunchOptions') or ''
        for m in HEROIC_LAUNCH_URL.finditer(f"{s.get('exe') or s.get('Exe') or ''} {options}"):
            existing_heroic_games.add(urllib.parse.unquote(m.group(1) or m.group(2)))
        if 'heroic://launch' in options and '--no-gui' not in options:
            update_shortcut(s, re.sub(r'("?heroic://launch)', r'--no-gui \1', options, count=1))
            decky_plugin.logger.info(f"Adding --no-gui to Heroic shortcut {s.get('appname') or s.get('AppName')}.")

    heroic_exe = find_heroic(logged_in_home)
    if not heroic_exe:
        decky_plugin.logger.info("Skipping Heroic Games Launcher scanner — Heroic not found.")
        return

    try:
        # Keep Steam's overlay library out of Heroic: Electron SIGKILLs its helper processes on exit, and one
        # killed while the preloaded overlay holds Steam's IPC lock (SysMgrMutex) freezes the whole Steam UI.
        # --console opens Heroic's controller UI from Steam without the "Start in console mode" setting, which
        # also pops Heroic's window up on --no-gui game launches.
        create_new_entry(
            f'"{heroic_exe}"',
            "Heroic Games Launcher",
            "LD_PRELOAD= %command% --console",
            f'"{os.path.dirname(heroic_exe)}"',
            "NonSteamLaunchers"
        )
        track_game("Heroic Games Launcher", "Launcher")
        decky_plugin.logger.info("Added Heroic Games Launcher to shortcuts.")
    except Exception as e:
        decky_plugin.logger.error(f"Failed to create entry for Heroic Games Launcher: {str(e)}")

    for app_name, runner, title in get_heroic_games(f"{logged_in_home}/.config/heroic"):
        track_game(title, "Heroic Games Launcher")
        if app_name in existing_heroic_games:
            decky_plugin.logger.info(f"Heroic already has a Steam shortcut for {title}. Skipping creation.")
            continue
        try:
            # --no-gui runs the game without Heroic's window and closes Heroic when the game exits.
            # LD_PRELOAD is cleared for the same Steam UI freeze as the launcher shortcut above.
            create_new_entry(
                f'"{heroic_exe}"',
                title,
                f'LD_PRELOAD= %command% --no-gui --no-sandbox "heroic://launch?appName={urllib.parse.quote(app_name)}&runner={runner}"',
                f'"{os.path.dirname(heroic_exe)}"',
                "Heroic Games Launcher"
            )
        except Exception as e:
            decky_plugin.logger.error(f"Failed to create entry for {title}: {str(e)}")
