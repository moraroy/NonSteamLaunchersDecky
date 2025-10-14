import os
import json
import time
import decky_plugin
from urllib.parse import quote
from scanners.game_tracker import track_game

def chrome_scanner(logged_in_home, create_new_entry):
    # Path to the Chrome Bookmarks file
    bookmarks_file_path = f"{logged_in_home}/.var/app/com.google.Chrome/config/google-chrome/Default/Bookmarks"

    # Lists to store results
    geforce_now_urls = []
    xbox_urls = []
    luna_urls = []
    seen_urls = set()

    def process_bookmark_item(item):
        if item['type'] != "url":
            return

        name = item['name'].strip()
        url = item['url']

        if not name or url in seen_urls:
            return

        # GeForce NOW
        if "play.geforcenow.com/games" in url:
            if name == "GeForce NOW":
                return

            game_name = name.replace(" on GeForce NOW", "").strip()
            url = url.split("&")[0] if "&" in url else url

            if url not in seen_urls:
                geforce_now_urls.append(("GeForce NOW", game_name, url))
                seen_urls.add(url)

        # Xbox Cloud Gaming (supporting multiple regions and new URL structure)
        elif "xbox.com/" in url and ("/play/launch/" in url or "/play/games/" in url):
            if name.startswith("Play "):
                game_name = name.replace("Play ", "").split(" |")[0].strip()
            else:
                game_name = name.split(" |")[0].strip()

            if game_name and url not in seen_urls:
                xbox_urls.append(("Xbox", game_name, url))
                seen_urls.add(url)

        # Amazon Luna (supporting regional domains)
        elif "luna.amazon." in url and "/game/" in url:
            if name.startswith("Play "):
                game_name = name.replace("Play ", "").split(" |")[0].strip()
            else:
                game_name = name.split(" |")[0].strip()

            if game_name and url not in seen_urls:
                luna_urls.append(("Amazon Luna", game_name, url))
                seen_urls.add(url)

    def scan_children(children):
        for item in children:
            if item['type'] == "folder":
                scan_children(item.get('children', []))
            else:
                process_bookmark_item(item)

    try:
        if not os.path.exists(bookmarks_file_path):
            decky_plugin.logger.info("Chrome Bookmarks not found. Skipping scanning for Bookmarks.")
            return

        with open(bookmarks_file_path, 'r') as f:
            data = json.load(f)

        # Recursively scan all relevant bookmark folders
        roots = data.get('roots', {})
        scan_children(roots.get('bookmark_bar', {}).get('children', []))
        scan_children(roots.get('other', {}).get('children', []))
        scan_children(roots.get('synced', {}).get('children', []))

        # Merge and process
        all_urls = geforce_now_urls + xbox_urls + luna_urls

        for platform_name, game_name, url in all_urls:
            time.sleep(0.1)
            decky_plugin.logger.info(f"{platform_name}: {game_name} - {url}")

            # Encode URL safely
            encoded_url = quote(url, safe=":/?=&")

            chromelaunch_options = (
                f'run --branch=stable --arch=x86_64 --command=/app/bin/chrome --file-forwarding com.google.Chrome @@u @@ '
                f'--window-size=1280,800 --force-device-scale-factor=1.00 --device-scale-factor=1.00 '
                f'--start-fullscreen {encoded_url} --no-first-run --enable-features=OverlayScrollbar'
            )

            chromedirectory = f'"{os.environ.get("chromedirectory", "/usr/bin/flatpak")}"'
            chrome_startdir = f'"{os.environ.get("chrome_startdir", "/usr/bin")}"'

            create_new_entry(
                chromedirectory,
                game_name,
                chromelaunch_options,
                chrome_startdir,
                "Google Chrome"
            )

            track_game(game_name, "Google Chrome")

    except Exception as e:
        decky_plugin.logger.error(f"Error scanning Chrome bookmarks: {e}")