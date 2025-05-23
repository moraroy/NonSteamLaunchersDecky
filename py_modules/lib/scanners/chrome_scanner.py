import os
import json
import decky_plugin
from urllib.parse import quote

def chrome_scanner(logged_in_home, create_new_entry):
    # Path to the Chrome Bookmarks file
    bookmarks_file_path = f"{logged_in_home}/.var/app/com.google.Chrome/config/google-chrome/Default/Bookmarks"

    # Lists to store results
    geforce_now_urls = []
    xbox_urls = []
    luna_urls = []

    try:
        with open(bookmarks_file_path, 'r') as f:
            data = json.load(f)

        # Loop through the "Other bookmarks" folder
        for item in data['roots']['other']['children']:
            if item['type'] == "url":
                name = item['name'].strip()
                url = item['url']

                if not name:
                    continue

                # GeForce NOW
                if "play.geforcenow.com/games" in url:
                    if name == "GeForce NOW":
                        continue  # Skip generic folder/bookmark

                    # Clean the name by removing " on GeForce NOW"
                    if " on GeForce NOW" in name:
                        game_name = name.replace(" on GeForce NOW", "").strip()
                    else:
                        game_name = name

                    # Strip anything from &lang and onward
                    if "&" in url:
                        url = url.split("&")[0]

                    geforce_now_urls.append(("GeForce NOW", game_name, url))

                # Xbox Cloud Gaming
                elif "www.xbox.com/en-US/play/games/" in url:
                    # Clean up the name
                    if name.startswith("Play "):
                        game_name = name.replace("Play ", "").split(" |")[0].strip()
                    else:
                        game_name = name.split(" |")[0].strip()

                    if game_name:
                        xbox_urls.append(("Xbox", game_name, url))

                # Amazon Luna
                elif "luna.amazon.com/game/" in url:
                    # Clean up the name
                    if name.startswith("Play "):
                        game_name = name.replace("Play ", "").split(" |")[0].strip()
                    else:
                        game_name = name.split(" |")[0].strip()

                    if game_name:
                        luna_urls.append(("Amazon Luna", game_name, url))

        # Merge all platforms' URLs into a single list for processing
        all_urls = geforce_now_urls + xbox_urls + luna_urls

        for platform_name, game_name, url in all_urls:
            decky_plugin.logger.info(f"{platform_name}: {game_name} - {url}")

            # Encode URL to prevent issues with special characters
            encoded_url = quote(url, safe=":/?=&")

            chromelaunch_options = (
                f'run --branch=stable --arch=x86_64 --command=/app/bin/chrome --file-forwarding com.google.Chrome @@u @@ '
                f'--window-size=1280,800 --force-device-scale-factor=1.00 --device-scale-factor=1.00 '
                f'--start-fullscreen {encoded_url} --no-first-run --enable-features=OverlayScrollbar'
            )

            # Use double quotes around paths
            chromedirectory = f'"{os.environ.get("chromedirectory", "/usr/bin/flatpak")}"'
            chrome_startdir = f'"{os.environ.get("chrome_startdir", "/usr/bin")}"'

            create_new_entry(
                chromedirectory,
                game_name,
                chromelaunch_options,
                chrome_startdir,
                "Google Chrome"
            )

    except FileNotFoundError:
        decky_plugin.logger.info("Chrome Bookmarks not found. Skipping scanning for Bookmarks.")
