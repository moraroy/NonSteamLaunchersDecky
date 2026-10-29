import os
import json
import time
import decky_plugin
from scanners.game_tracker import track_game
from scanners.host_arch import FLATPAK_ARCH


def chrome_scanner(logged_in_home, create_new_entry):
    # Chrome profile paths (matching the desktop version)
    chrome_app_paths = [
        os.path.join(
            logged_in_home,
            ".var/app/com.google.Chrome/config/google-chrome/Default"
        ),
        os.path.join(
            logged_in_home,
            ".var/app/com.google.chrome/config/google-chrome/Default"
        ),
    ]

    # Support both regular and account bookmarks
    possible_bookmark_files = [
        os.path.join(profile_path, filename)
        for profile_path in chrome_app_paths
        for filename in ("Bookmarks", "AccountBookmarks")
    ]

    bookmarks_file_path = next(
        (
            path for path in possible_bookmark_files
            if os.path.isfile(path)
        ),
        None
    )

    # Lists to store results
    geforce_now_urls = []
    xbox_urls = []
    luna_urls = []
    boosteroid_urls = []
    webrcade_urls = []

    seen_urls = set()

    def process_bookmark_item(item):
        if item.get('type') != "url":
            return

        name = item.get('name', '').strip()
        url = item.get('url', '')

        if not name or not url or url in seen_urls:
            return

        # GeForce NOW
        if "play.geforcenow.com/games" in url:
            if name == "GeForce NOW":
                return

            game_name = name.replace(" on GeForce NOW", "").strip()
            url = url.split("&")[0] if "&" in url else url

            if url not in seen_urls:
                geforce_now_urls.append(
                    ("GeForce NOW", game_name, url)
                )
                seen_urls.add(url)

        # Xbox Cloud Gaming
        elif "xbox.com/" in url and (
            "/play/launch/" in url or "/play/games/" in url
        ):
            if name.startswith("Play "):
                game_name = name.replace("Play ", "").split(" |")[0].strip()
            else:
                game_name = name.split(" |")[0].strip()

            if game_name and url not in seen_urls:
                xbox_urls.append(("Xbox", game_name, url))
                seen_urls.add(url)

        # Amazon Luna
        elif "luna.amazon." in url and "/game/" in url:
            if name.startswith("Play "):
                game_name = name.replace("Play ", "").split(" |")[0].strip()
            else:
                game_name = name.split(" |")[0].strip()

            if game_name and url not in seen_urls:
                luna_urls.append(("Amazon Luna", game_name, url))
                seen_urls.add(url)

        # Boosteroid
        elif "cloud.boosteroid.com/application/" in url:
            boosteroid_urls.append(("Boosteroid", name, url))
            seen_urls.add(url)

        # Boosteroid (Session format)
        elif (
            "cloud.boosteroid.com/static/streaming/streaming.html" in url
            and "sessionId=" in url
        ):
            boosteroid_urls.append(("Boosteroid", name, url))
            seen_urls.add(url)

        # WebRcade
        elif "play.webrcade.com/app/" in url:
            webrcade_urls.append(("WebRcade", name, url))
            seen_urls.add(url)

    def scan_children(children):
        for item in children:
            if item.get('type') == "folder":
                scan_children(item.get('children', []))
            else:
                process_bookmark_item(item)

    try:
        if not bookmarks_file_path:
            decky_plugin.logger.info(
                "Chrome Bookmarks not found. Skipping scanning for Bookmarks."
            )
            return

        with open(bookmarks_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        decky_plugin.logger.info(
            f"Scanning Chrome bookmarks: {bookmarks_file_path}"
        )

        # Recursively scan all relevant bookmark folders
        roots = data.get('roots', {})

        for root_name in ('bookmark_bar', 'other', 'synced'):
            root = roots.get(root_name, {})
            scan_children(root.get('children', []))

        # Merge and process
        all_urls = (
            geforce_now_urls
            + xbox_urls
            + luna_urls
            + boosteroid_urls
            + webrcade_urls
        )

        for platform_name, game_name, url in all_urls:
            time.sleep(0.1)
            decky_plugin.logger.info(
                f"{platform_name}: {game_name} - {url}"
            )

            # Keep existing Chrome launch options
            encoded_url = url

            chromelaunch_options = (
                f'run --branch=stable --arch={FLATPAK_ARCH} '
                f'--command=/app/bin/chrome --file-forwarding '
                f'com.google.Chrome @@u @@ '
                f'--window-size=1280,800 '
                f'--force-device-scale-factor=1.00 '
                f'--device-scale-factor=1.00 '
                f'--start-fullscreen "{encoded_url}" '
                f'--no-first-run --enable-features=OverlayScrollbar'
            )

            chromedirectory = (
                f'"{os.environ.get("chromedirectory", "/usr/bin/flatpak")}"'
            )
            chrome_startdir = (
                f'"{os.environ.get("chrome_startdir", "/usr/bin")}"'
            )

            create_new_entry(
                chromedirectory,
                game_name,
                chromelaunch_options,
                chrome_startdir,
                platform_name
            )

            track_game(game_name, "Google Chrome")

    except Exception as e:
        decky_plugin.logger.error(
            f"Error scanning Chrome bookmarks: {e}"
        )