import os
import shutil
import subprocess
import decky_plugin
import platform
from scanners.game_tracker import track_game
from scanners.host_arch import FLATPAK_ARCH

def flatpak_scanner(logged_in_home, create_new_entry):

    if platform.system() == "Windows":
        decky_plugin.logger.info("Running on Windows. Skipping Flatpak scanner.")
        return

    env_vars = {**os.environ, 'LD_LIBRARY_PATH': '/usr/lib:/lib'}

    def is_flatpak_installed(app_id):
        for install_type in ["--user", "--system"]:
            try:
                subprocess.run(
                    ["flatpak", "info", install_type, app_id],
                    check=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    env=env_vars
                )
                return True
            except subprocess.CalledProcessError:
                continue
        return False

    # List of Flatpak apps to scan
    flatpak_apps = [
        {
            "id": "com.nvidia.geforcenow",
            "display_name": "NVIDIA GeForce NOW",
            "launch_options": lambda app_id: f"run {app_id}"
        },
        {
            "id": "com.moonlight_stream.Moonlight",
            "display_name": "Moonlight Game Streaming",
            "launch_options": lambda app_id: (
                f"run --branch=stable --arch={FLATPAK_ARCH} --command=moonlight "
                f"{app_id}"
            )
        },
        {
            "id": "com.hypixel.HytaleLauncher",
            "display_name": "Hytale",
            "launch_options": lambda app_id: (
                "run --branch=master --arch=x86_64 --command=hytale-launcher-wrapper "
                f"{app_id}"
            )
        },
        {
            "id": "org.prismlauncher.PrismLauncher",
            "display_name": "Prism Launcher",
            "launch_options": lambda app_id: f"run {app_id}"
        }
    ]

    exe_path = '"/usr/bin/flatpak"'
    start_dir = '"/usr/bin"'

    for app in flatpak_apps:
        app_id = app["id"]
        display_name = app["display_name"]
        app_name = app["launch_options"](app_id)

        if not is_flatpak_installed(app_id):
            decky_plugin.logger.info(f"Skipping {display_name} scanner — Flatpak not found.")
            continue

        try:
            create_new_entry(
                exe_path,
                display_name,
                app_name,
                start_dir,
                "NonSteamLaunchers"
            )
            track_game(display_name, "Launcher")
            decky_plugin.logger.info(f"Added {display_name} to shortcuts.")
        except Exception as e:
            decky_plugin.logger.error(f"Failed to create entry for {display_name}: {str(e)}")

    heroic_scanner(logged_in_home, create_new_entry)


def heroic_scanner(logged_in_home, create_new_entry):
    # Prefer a distro-provided Heroic (e.g. ArmadaOS /usr/bin/heroic), then the AppImage NSL installs
    heroic_exe = shutil.which("heroic")
    if not heroic_exe and os.path.isfile("/usr/bin/heroic"):
        heroic_exe = "/usr/bin/heroic"
    if not heroic_exe:
        heroic_appimage = f"{logged_in_home}/.local/share/applications/Heroic.AppImage"
        if os.path.isfile(heroic_appimage):
            heroic_exe = heroic_appimage

    if not heroic_exe:
        decky_plugin.logger.info("Skipping Heroic Games Launcher scanner — Heroic not found.")
        return

    try:
        # Keep Steam's overlay library out of Heroic: Electron SIGKILLs its helper processes on exit, and one
        # killed while the preloaded overlay holds Steam's IPC lock (SysMgrMutex) freezes the whole Steam UI
        create_new_entry(
            f'"{heroic_exe}"',
            "Heroic Games Launcher",
            "LD_PRELOAD= %command%",
            f'"{os.path.dirname(heroic_exe)}"',
            "NonSteamLaunchers"
        )
        track_game("Heroic Games Launcher", "Launcher")
        decky_plugin.logger.info("Added Heroic Games Launcher to shortcuts.")
    except Exception as e:
        decky_plugin.logger.error(f"Failed to create entry for Heroic Games Launcher: {str(e)}")
