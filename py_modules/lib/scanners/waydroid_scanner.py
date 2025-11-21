import os
import shutil
import configparser
import decky_plugin
import time
import platform
from scanners.game_tracker import track_game

def waydroid_scanner(logged_in_home, create_new_entry):
    # Skip scanner if running on Windows
    if platform.system() == "Windows":
        decky_plugin.logger.info("Running on Windows. Skipping Waydroid scanner.")
        return

    # Check for Waydroid
    if shutil.which("waydroid") is None:
        decky_plugin.logger.info("Waydroid not found. Skipping Waydroid scanner.")
        return

    applications_dir = os.path.join(logged_in_home, ".local/share/applications/")
    ignored_files = {
        "waydroid.com.android.inputmethod.latin.desktop",
        "waydroid.com.android.gallery3d.desktop",
        "waydroid.com.android.documentsui.desktop",
        "waydroid.com.android.settings.desktop",
        "waydroid.org.lineageos.eleven.desktop",
        "waydroid.com.android.calculator2.desktop",
        "waydroid.com.android.contacts.desktop",
        "waydroid.org.lineageos.etar.desktop",
        "waydroid.org.lineageos.jelly.desktop",
        "waydroid.com.android.camera2.desktop",
        "waydroid.com.android.deskclock.desktop",
        "waydroid.org.lineageos.recorder.desktop",
        "waydroid.com.google.android.apps.messaging.desktop",
        "waydroid.com.google.android.contacts.desktop",
        "waydroid.org.lineageos.aperture.desktop",
    }

    if not os.path.isdir(applications_dir):
        decky_plugin.logger.info(f"Applications directory not found: {applications_dir}")
        return

    possible_launchers = [
        os.path.join(logged_in_home, "Android_Waydroid/Android_Waydroid_Cage.sh"),
        os.path.join(logged_in_home, "bin/waydroid-cage.sh"),
        os.path.join(logged_in_home, ".local/bin/waydroid-cage.sh"),
    ]

    launcher_path = None

    # 1. Check known installer paths
    for path in possible_launchers:
        if os.path.isfile(path):
            launcher_path = path
            break

    if launcher_path is None:
        search_dirs = [
            logged_in_home,
            "/run/media",
            "/mnt",
            "/media",
        ]

        decky_plugin.logger.info("Fast-searching for custom waydroid-cage.sh...")

        for base in search_dirs:
            if not os.path.isdir(base):
                continue

            for root, dirs, files in os.walk(base, topdown=True):
                # Skip large/unnecessary dirs
                dirs[:] = [
                    d for d in dirs
                    if d not in ("proc", "dev", "sys", "lost+found", "var", "boot", "etc", "run", "tmp")
                ]

                if "waydroid-cage.sh" in files:
                    launcher_path = os.path.join(root, "waydroid-cage.sh")
                    decky_plugin.logger.info(f"Found Waydroid launcher: {launcher_path}")
                    break

            if launcher_path:
                break

    # If found → configure to use cage launcher
    if launcher_path:
        use_cage = True
        exe_path = launcher_path
        start_dir = os.path.dirname(launcher_path)
    else:
        use_cage = False
        exe_path = None
        start_dir = None

    decky_plugin.logger.info(f"Waydroid Cage Detected: {use_cage}")
    decky_plugin.logger.info(f"Launcher Path: {exe_path}")

    for file_name in os.listdir(applications_dir):
        time.sleep(0.1)
        if not file_name.endswith(".desktop") or file_name in ignored_files:
            continue

        file_path = os.path.join(applications_dir, file_name)

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read().lower()
                if "waydroid" not in content:
                    continue

            parser = configparser.ConfigParser(strict=False)
            parser.read(file_path)

            display_name = parser.get("Desktop Entry", "Name", fallback=None)
            exec_cmd = parser.get("Desktop Entry", "Exec", fallback="")

            if not display_name or "waydroid app launch" not in exec_cmd:
                continue

            # Extract the Android package name
            parts = exec_cmd.strip().split()
            app_name = parts[-1] if len(parts) >= 3 else None
            if not app_name:
                continue

            if use_cage:
                target = f'"{exe_path}"'
                launch_opts = f'"{app_name}"'
                start_in = start_dir
            else:
                target = '"waydroid"'
                start_in = '"./"'
                launch_opts = f'"app" "launch" "{app_name}"'

            # Register entry
            create_new_entry(
                target,
                display_name,
                launch_opts,
                start_in,
                "Waydroid"
            )

            track_game(display_name, "Waydroid")

        except Exception as e:
            decky_plugin.logger.info(f"Failed to process {file_name}: {e}")
