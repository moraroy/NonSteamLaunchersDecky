import subprocess
import json
import os
from pathlib import Path
import externals.xml.etree.ElementTree as ET
import platform
import time
import decky_plugin
from scanners.game_tracker import track_game

if platform.system() == "Windows":
    import winreg

def microsoftxbox_scanner(logged_in_home, microsoftxbox_launcher, create_new_entry):
    def get_appx_packages():
        command = [
            "powershell",
            "-Command",
            "Get-AppxPackage | Where-Object { -not $_.IsFramework } | ConvertTo-Json -Depth 3"
        ]
        try:
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            packages = json.loads(result.stdout)
            if isinstance(packages, dict):
                packages = [packages]
            return packages
        except subprocess.CalledProcessError as e:
            decky_plugin.logger.error(f"PowerShell command failed: {e}")
            return []
        except json.JSONDecodeError as e:
            decky_plugin.logger.error(f"Failed to parse JSON output from PowerShell: {e}")
            return []

    def parse_manifest(manifest_path):
        try:
            tree = ET.parse(manifest_path)
            root = tree.getroot()
            ns = {'uap': 'http://schemas.microsoft.com/appx/manifest/uap/windows10'}

            visual = root.find('.//uap:VisualElements', ns)
            visual_display_name = visual.attrib.get('DisplayName') if visual is not None else ""

            props = root.find('.//{*}Properties')
            general_display_name_node = props.find('{*}DisplayName') if props is not None else None
            general_display_name = general_display_name_node.text if general_display_name_node is not None else ""

            applications = root.find('.//{*}Applications')
            app_list = applications.findall('{*}Application') if applications is not None else []

            identity = root.find('.//{*}Identity')
            family_name = identity.attrib.get('Name') if identity is not None else ""

            return visual_display_name, general_display_name, app_list, root, family_name
        except Exception as e:
            decky_plugin.logger.error(f"Failed to parse manifest: {manifest_path}, error: {e}")
            return "", "", [], None, ""

    def is_game_app(config_path, app_list):
        if Path(config_path).exists():
            return True
        for app in app_list:
            app_id = app.attrib.get('Id', '')
            exe = app.attrib.get('Executable', '')
            if 'Game' in app_id or 'Game' in exe:
                return True
        return False

    if platform.system() == "Windows":
        # Native Windows scan
        packages = get_appx_packages()
        if not packages:
            decky_plugin.logger.warning("No AppX packages found or failed to retrieve them.")
            return

        for pkg in packages:
            install_location = pkg.get('InstallLocation')
            family_name = pkg.get('PackageFamilyName')

            if not install_location or not os.path.isdir(install_location):
                decky_plugin.logger.warning(f"Invalid install location: {install_location}")
                continue

            manifest_path = os.path.join(install_location, "AppxManifest.xml")
            config_path = os.path.join(install_location, "MicrosoftGame.config")

            if not os.path.exists(manifest_path):
                decky_plugin.logger.warning(f"Manifest not found: {manifest_path}")
                continue

            visual_name, general_name, app_list, _, _ = parse_manifest(manifest_path)

            if "DisplayName" in general_name or "ms-resource" in general_name:
                decky_plugin.logger.warning(f"Skipping app with unresolved display name: {general_name}")
                continue

            if not is_game_app(config_path, app_list):
                decky_plugin.logger.warning(f"Skipping non-game app: {install_location}")
                continue

            for app in app_list:
                app_id = app.attrib.get('Id')

                if not app_id:
                    decky_plugin.logger.warning(f"Missing App ID in app entry for package: {family_name}")
                    continue

                aumid = f"{family_name}!{app_id}"
                name = visual_name if visual_name and "DisplayName" not in visual_name and "ms-resource" not in visual_name else general_name

                if not name:
                    decky_plugin.logger.warning(f"Game name could not be determined for: {install_location}")
                    continue

                exe_path = "C:\\WINDOWS\\explorer.exe"
                start_dir = "C:\\WINDOWS"
                launch_options = f"shell:AppsFolder\\{aumid}"

                create_new_entry(exe_path, name, launch_options, start_dir, "Microsoft Xbox")
                track_game(name, "Microsoft Xbox")
                time.sleep(0.1)

    else:
        # Linux/Steam Deck scan in Proton prefix
        windows_apps_dir = f"{logged_in_home}/.local/share/Steam/steamapps/compatdata/{microsoftxbox_launcher}/pfx/drive_c/Program Files/WindowsApps"

        if not os.path.exists(windows_apps_dir):
            decky_plugin.logger.warning("WindowsApps folder not found in Proton prefix.")
            return

        for item in os.listdir(windows_apps_dir):
            item_path = os.path.join(windows_apps_dir, item)
            manifest_path = os.path.join(item_path, "AppxManifest.xml")
            config_path = os.path.join(item_path, "MicrosoftGame.config")

            if not os.path.exists(manifest_path):
                decky_plugin.logger.warning(f"Manifest file not found for: {item_path}")
                continue

            visual_name, general_name, app_list, _, family_name = parse_manifest(manifest_path)

            if not family_name:
                decky_plugin.logger.warning(f"Missing package family name in manifest: {manifest_path}")
                continue

            if "DisplayName" in general_name or "ms-resource" in general_name:
                decky_plugin.logger.warning(f"Skipping app with unresolved display name: {general_name}")
                continue

            if not is_game_app(config_path, app_list):
                decky_plugin.logger.warning(f"Non-game app skipped: {item_path}")
                continue

            for app in app_list:
                app_id = app.attrib.get("Id", "")
                if not app_id:
                    decky_plugin.logger.warning(f"Missing App ID in app entry for: {item_path}")
                    continue

                aumid = f"{family_name}!{app_id}"
                name = visual_name if visual_name and "DisplayName" not in visual_name and "ms-resource" not in visual_name else general_name

                if not name:
                    decky_plugin.logger.warning(f"Game name could not be determined in prefix: {item_path}")
                    continue

                exe_path = "C:\\WINDOWS\\explorer.exe"
                start_dir = "C:\\WINDOWS"
                launch_options = f'shell:AppsFolder\\{aumid}'

                create_new_entry(exe_path, name, launch_options, start_dir, "Microsoft Xbox")
                track_game(name, "Microsoft Xbox (Proton)")
                time.sleep(0.1)
