import json
import http.client
import socket
import os
import base64
import itertools
from urllib.parse import urlparse

# === CONFIGURATION ===
WS_HOST = "localhost"
WS_PORT = 8080
TARGET_TITLE = "SharedJSContext"  # ThemeMusic main injection target
TARGET_TITLE2 = "Steam"            # Steam window target
TARGET_TITLE3 = "Steam Big Picture Mode"




THEMEMUSIC_CODE = r"""(function () {
  const LOCAL_STORAGE_KEY = "ThemeMusicData";

  const themeMusicEvents = new EventTarget();
  const originalSetItem = localStorage.setItem.bind(localStorage);

  localStorage.setItem = function (key, value) {
    originalSetItem(key, value);
    if (key === LOCAL_STORAGE_KEY) {
      let enabled = true;
      try {
        const data = JSON.parse(value || "{}");
        enabled = !(data.themeMusic === false || data.themeMusic === "off");
      } catch {}
      themeMusicEvents.dispatchEvent(new CustomEvent("themeMusicToggle", { detail: { enabled } }));
    }
  };

  themeMusicEvents.addEventListener("themeMusicToggle", (e) => {
      console.log("Theme music toggled (same tab):", e.detail.enabled);
      if (!e.detail.enabled && ytPlayer) {
          // Stop the music first
          fadeOutAndStop().then(() => {
              // Clear the currently playing music data after it has stopped
              clearCurrentlyPlaying();
          });
      }
  });


  // Listen to changes from other tabs
  window.addEventListener("storage", (e) => {
    if (e.key === LOCAL_STORAGE_KEY) {
      let enabled = true;
      try {
        const data = JSON.parse(e.newValue || "{}");
        enabled = !(data.themeMusic === false || data.themeMusic === "off");
      } catch {}
      console.log("Theme music toggled (other tab):", enabled);
      if (!enabled && ytPlayer) fadeOutAndStop();
    }
  });

  function isThemeMusicEnabled() {
    try {
      const data = JSON.parse(localStorage.getItem(LOCAL_STORAGE_KEY) || "{}");
      return !(data.themeMusic === false || data.themeMusic === "off");
    } catch {
      return true; // default ON if parsing fails
    }
  }

  let stoppingMusic = false;
  let pausedForGame = false;

  if (window.SteamClient && SteamClient.Apps && SteamClient.Apps.RegisterForGameActionStart) {
    SteamClient.Apps.RegisterForGameActionStart((appID) => {
      if (stoppingMusic) return;
      stoppingMusic = true;

      console.log("Play clicked! Game starting… AppID:", appID);

      fadeOutAndStop().finally(() => { stoppingMusic = false; });

      var mgr = window.MainWindowBrowserManager;
      if (mgr) mgr.LoadURL("/library");
    });
  }

  var mgr = window.MainWindowBrowserManager;
  if (!mgr) return;

  var lastUrl = null;
  var lastAppID = null;

  var ytAudioIframe = null;
  var ytPlayer = null;
  var ytPlayerReady = false;
  var fadeInterval = null;
  var currentQuery = null;

  var sessionCache = new Map();
  const CACHE_EXPIRATION = 7 * 24 * 60 * 60 * 1000;

  if (!window.YT) {
    var tag = document.createElement('script');
    tag.src = "https://www.youtube.com/iframe_api";
    document.head.appendChild(tag);
  }

  function waitForYouTubeAPI() {
    if (window.YT && window.YT.Player) return Promise.resolve();
    return new Promise(function (resolve) {
      window.onYouTubeIframeAPIReady = function () { resolve(); };
    });
  }

  function loadCache() {
    try { return JSON.parse(localStorage.getItem(LOCAL_STORAGE_KEY) || "{}"); }
    catch { return {}; }
  }

  function saveCache(data) {
    localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify(data));
  }

  function getCachedVideo(query) {
      // First, check if there's a cached video ID in the session cache
      if (sessionCache.has(query)) {
          // Retrieve the session cache entry
          const sessionEntry = sessionCache.get(query);
          const cache = loadCache();  // Load the localStorage cache
          const localStorageEntry = cache[query];

          if (localStorageEntry && localStorageEntry.timestamp > sessionEntry.timestamp) {
              // If the timestamp in localStorage is newer, use the localStorage entry
              sessionCache.set(query, localStorageEntry);  // Update the session cache with the newer entry
              return localStorageEntry.videoId;
          }

          // If session cache is newer or no localStorage entry, return session cache ID
          return sessionEntry.videoId;
      }

      // If no session cache, check the localStorage cache
      var cache = loadCache();
      var entry = cache[query];
      if (!entry) return null;

      // If the entry exists in localStorage and it's not expired, use it
      sessionCache.set(query, entry);  // Store the localStorage entry in session cache
      return entry.videoId;
  }


  function storeCachedVideo(query, videoId) {
    var cache = loadCache();
    const entry = { videoId: videoId, timestamp: Date.now() };

    cache[query] = entry;
    saveCache(cache);


    sessionCache.set(query, entry);
  }

  function fadeOutAndStop() {
    return new Promise(function (resolve) {
      if (!ytPlayer) return resolve();
      pausedForGame = true;
      var volume = 100;
      clearInterval(fadeInterval);
      fadeInterval = setInterval(function () {
        if (!ytPlayer) return cleanup();
        volume = Math.max(0, volume - 10);
        if (ytPlayer.setVolume) ytPlayer.setVolume(volume);
        if (volume <= 0) cleanup();
      }, 50);

      function cleanup() {
        clearInterval(fadeInterval);
        fadeInterval = null;
        try { ytPlayer.stopVideo && ytPlayer.stopVideo(); ytPlayer.destroy && ytPlayer.destroy(); } catch (e) {}
        ytAudioIframe && ytAudioIframe.remove();
        ytAudioIframe = null;
        ytPlayer = null;
        ytPlayerReady = false;
        currentQuery = null;
        setTimeout(() => { pausedForGame = false; }, 2000);

        resolve();
      }
    });
  }

  function createYTPlayer(videoId) {
    if (!isThemeMusicEnabled()) return Promise.resolve();
    return waitForYouTubeAPI().then(function () {
      ytAudioIframe && ytAudioIframe.remove();
      ytAudioIframe = document.createElement("div");
      ytAudioIframe.id = "yt-audio-player";
      Object.assign(ytAudioIframe.style, { width: "0", height: "0", position: "absolute", opacity: "0", pointerEvents: "none" });
      document.body.appendChild(ytAudioIframe);
      ytPlayerReady = false;
      ytPlayer = new YT.Player("yt-audio-player", {
        height: "0",
        width: "0",
        videoId: videoId,
        playerVars: { autoplay: 1 },
        events: {
          onReady: function () { ytPlayerReady = true; ytPlayer.setVolume && ytPlayer.setVolume(100); },
          onError: function () { fadeOutAndStop(); }
        }
      });
    });
  }




  function updateCurrentlyPlaying(query, videoId) {
      try {
          const themeData = JSON.parse(localStorage.getItem(LOCAL_STORAGE_KEY) || "{}");
          themeData.currentlyPlaying = {
              name: query,
              videoId: videoId || "loading",  // Temporary placeholder while loading
              timestamp: Date.now()
          };
          localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify(themeData));

          // Dispatch an event to notify the update
          themeMusicEvents.dispatchEvent(new CustomEvent("currentlyPlayingUpdated", {
              detail: { name: query, videoId: videoId }
          }));
      } catch (e) {
          console.error("Error updating currentlyPlaying:", e);
      }
  }

  function playYouTubeAudio(query) {
      if (!isThemeMusicEnabled()) return;
      if (query === currentQuery) return;
      currentQuery = query;

      // Update "currentlyPlaying" state in localStorage immediately
      updateCurrentlyPlaying(query, "loading"); // Temporary placeholder for the videoId

      // Stop current track
      return fadeOutAndStop().then(function () {
          var cachedId = getCachedVideo(query);
          if (cachedId) {
              updateCurrentlyPlaying(query, cachedId);
              return createYTPlayer(cachedId);
          }

          // Fetch new track from API
          return fetch("https://nonsteamlaunchers.onrender.com/api/x7a9/" + encodeURIComponent(query))
              .then(function (res) { return res.json(); })
              .then(function (data) {
                  if (!data || !data.videoId) return;

                  // Cache the track
                  storeCachedVideo(query, data.videoId);

                  // Update "currentlyPlaying" state with the actual videoId
                  updateCurrentlyPlaying(query, data.videoId);

                  return createYTPlayer(data.videoId);
               })
               .catch(function () {
                   console.error("Theme music fetch failed");
                   updateCurrentlyPlaying(query, null); // optional: clear 'loading' state on error
               });
       });
  }

  // Handle the event when "currentlyPlaying" changes
  themeMusicEvents.addEventListener("currentlyPlayingUpdated", (e) => {
      const { name, videoId } = e.detail;
      console.log("Currently Playing:", name, videoId);
      // You can trigger UI updates or any other logic that depends on the new state here.
  });

  function clearCurrentlyPlaying() {
      try {
          const themeData = JSON.parse(localStorage.getItem(LOCAL_STORAGE_KEY) || "{}");
          themeData.currentlyPlaying = null;
          localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify(themeData));
          console.log("Currently playing data cleared");
      } catch (e) {
          console.error("Error clearing currentlyPlaying:", e);
      }
  }


  function handleAppId(appId) {
    if (!isThemeMusicEnabled()) return;
    if (pausedForGame) return;
    if (!window.appStore || !window.appStore.m_mapApps) return;
    var appInfo = window.appStore.m_mapApps.get(appId);
    if (!appInfo || !appInfo.display_name) return;
    var query = appInfo.display_name + " Theme Music";
    playYouTubeAudio(query);
  }

  function handleUrl(url) {
    if (!isThemeMusicEnabled()) return;
    var decoded = decodeURIComponent(url);
    var match = decoded.match(/\/library\/app\/(\d+)/);
    if (!match) match = window.location.pathname.match(/\/routes?\/library\/app\/(\d+)/);
    if (!match) return;
    var appId = Number(match[1]);
    if (appId === lastAppID) return;
    lastAppID = appId;
    handleAppId(appId);
  }

  lastUrl = mgr.m_URL;
  handleUrl(lastUrl);

  function watchUrl() {
    var current = mgr.m_URL;
    if (current && current !== lastUrl) {
      lastUrl = current;
      handleUrl(current);
    }
    requestAnimationFrame(watchUrl);
  }

  requestAnimationFrame(watchUrl);
})();"""







# === Utility functions ===

def fetch_targets(host, port):
    conn = http.client.HTTPConnection(host, port)
    conn.request("GET", "/json")
    resp = conn.getresponse()
    if resp.status != 200:
        raise Exception(f"Failed to fetch targets: {resp.status} {resp.reason}")
    data = resp.read()
    conn.close()
    return json.loads(data)


def get_ws_url_by_title(host, port, title):
    """Exact match version, kept for backward compatibility."""
    targets = fetch_targets(host, port)
    for target in targets:
        if target.get("title") == title:
            return target.get("webSocketDebuggerUrl")
    raise Exception(f"Target with title '{title}' not found.")


def find_target_ws_url(host, port, title_substring):
    """Returns first WebSocket URL whose title contains `title_substring`. Returns None if not found."""
    targets = fetch_targets(host, port)
    for target in targets:
        t_title = target.get("title", "")
        if title_substring.lower() in t_title.lower():
            print(f"Found target: '{t_title}'")
            return target.get("webSocketDebuggerUrl")
    print(f"No target containing '{title_substring}' found.")
    return None


def create_websocket_connection(ws_url):
    parsed = urlparse(ws_url)
    host = parsed.hostname
    port = parsed.port
    path = parsed.path + ("?" + parsed.query if parsed.query else "")

    sock = socket.create_connection((host, port))
    key = base64.b64encode(os.urandom(16)).decode('utf-8')
    headers = [
        f"GET {path} HTTP/1.1",
        f"Host: {host}:{port}",
        "Upgrade: websocket",
        "Connection: Upgrade",
        f"Sec-WebSocket-Key: {key}",
        "Sec-WebSocket-Version: 13",
        "\r\n"
    ]
    handshake = "\r\n".join(headers)
    sock.send(handshake.encode('utf-8'))

    resp = b""
    while b"\r\n\r\n" not in resp:
        chunk = sock.recv(4096)
        if not chunk:
            break
        resp += chunk

    if b"101" not in resp.split(b"\r\n")[0]:
        raise Exception("WebSocket upgrade failed:\n" + resp.decode('utf-8'))

    return sock


def send_ws_text(sock, message):
    frame = bytearray()
    frame.append(0x81)  # FIN + text frame opcode
    length = len(message)
    mask_bit = 0x80

    if length <= 125:
        frame.append(length | mask_bit)
    elif length <= 65535:
        frame.append(126 | mask_bit)
        frame += length.to_bytes(2, 'big')
    else:
        frame.append(127 | mask_bit)
        frame += length.to_bytes(8, 'big')

    mask_key = os.urandom(4)
    frame += mask_key

    msg_bytes = message.encode('utf-8')
    masked_bytes = bytearray(b ^ mask_key[i % 4] for i, b in enumerate(msg_bytes))
    frame += masked_bytes

    sock.send(frame)


def recv_ws_message(sock):
    first_byte = sock.recv(1)
    if not first_byte:
        return None
    fin = (first_byte[0] & 0x80) >> 7
    opcode = first_byte[0] & 0x0f

    if opcode == 0x8:
        return None  # Close frame
    if opcode != 0x1:
        return None  # Not text frame

    second_byte = sock.recv(1)
    masked = (second_byte[0] & 0x80) >> 7
    payload_len = second_byte[0] & 0x7f

    if payload_len == 126:
        extended = sock.recv(2)
        payload_len = int.from_bytes(extended, 'big')
    elif payload_len == 127:
        extended = sock.recv(8)
        payload_len = int.from_bytes(extended, 'big')

    if masked:
        mask_key = sock.recv(4)
    else:
        mask_key = None

    payload = bytearray()
    while len(payload) < payload_len:
        chunk = sock.recv(payload_len - len(payload))
        if not chunk:
            break
        payload.extend(chunk)

    if masked and mask_key:
        payload = bytearray(b ^ mask_key[i % 4] for i, b in enumerate(payload))

    return payload.decode('utf-8')


def recv_ws_message_for_id(sock, expected_id):
    while True:
        message = recv_ws_message(sock)
        if message is None:
            return None
        try:
            data = json.loads(message)
            if data.get("id") == expected_id:
                return data
        except Exception:
            continue


eval_id_counter = itertools.count(1000)

def inject_thememusic_code(ws_socket, code):
    inject_id = next(eval_id_counter)
    wrapped_code = f"(async () => {{ {code}; return 'Injection done'; }})()"

    send_ws_text(ws_socket, json.dumps({
        "id": inject_id,
        "method": "Runtime.evaluate",
        "params": {
            "expression": wrapped_code,
            "awaitPromise": True
        }
    }))

    response = recv_ws_message_for_id(ws_socket, inject_id)
    print("Injection response:", response)
    return response


### THEMEMUSIC ONLY
def inject_thememusic_code(ws_socket):
    inject_id = next(eval_id_counter)
    wrapped_code = f"(async () => {{ {THEMEMUSIC_CODE}; return 'ThemeMusic injection done'; }})()"

    send_ws_text(ws_socket, json.dumps({
        "id": inject_id,
        "method": "Runtime.evaluate",
        "params": {
            "expression": wrapped_code,
            "awaitPromise": True
        }
    }))

    response = recv_ws_message_for_id(ws_socket, inject_id)
    print("ThemeMusic injection response:", response)
    return response


# Usage for main ThemeMusic target
ws_url = get_ws_url_by_title(WS_HOST, WS_PORT, TARGET_TITLE)
ws_socket = create_websocket_connection(ws_url)

send_ws_text(ws_socket, json.dumps({"id": 1, "method": "Runtime.enable"}))
recv_ws_message_for_id(ws_socket, 1)

inject_thememusic_code(ws_socket)
# END OF THEMEMUSIC








### METADATA ONLY
METADATA_CODE = r"""
(function () {
    // Cache object to store game details
    const gameCache = {};

    async function getSteamGameDetails(gameName) {
        // Check if the game details are already in the cache
        if (gameCache[gameName]) {
            return gameCache[gameName];
        }
        try {
            const searchRes = await fetch(`https://store.steampowered.com/search/?term=${encodeURIComponent(gameName)}`, {
                credentials: "omit"
            });
            const searchHtml = await searchRes.text();
            const searchDoc = new DOMParser().parseFromString(searchHtml, "text/html");
            const results = [...searchDoc.querySelectorAll(".search_result_row")].map(r => ({
                appid: r.dataset.dsAppid,
                title: r.querySelector(".title")?.innerText.trim()
            }));
            if (!results.length) return null;
            let match = results.find(r => r.title?.toLowerCase() === gameName.toLowerCase()) || results[0];
            const appid = match.appid;
            const apiRes = await fetch(`https://store.steampowered.com/api/appdetails?appids=${appid}`);
            const apiData = await apiRes.json();
            const info = apiData[appid].data;
            if (!info) return null;
            const gameData = {
                appid: appid,
                about_the_game: info.short_description || null,
                developer: (info.developers?.join(", ") || null),
                publisher: (info.publishers?.join(", ") || null),
                release_date: info.release_date?.date || null,
                genres: info.genres?.map(g => g.description).join(", ") || null,
                platforms: info.platforms ? Object.entries(info.platforms).filter(([k,v]) => v).map(([k]) => k).join(", ") : null,
                image_url: info.screenshots?.[0]?.path_full || null
            };
            // Cache the data for future use
            gameCache[gameName] = gameData;
            return gameData;
        } catch (err) {
            console.error("Error fetching Steam details:", err);
            return null;
        }
    }

    function replaceText() {
        document.querySelectorAll("div").forEach(div => {
            if (
                div.childNodes.length === 1 &&
                div.firstChild.nodeType === Node.TEXT_NODE
            ) {
                const originalText = div.firstChild.nodeValue;
                const match = originalText.match(/Some detailed information on (.*?) is unavailable/i);
                if (match) {
                    const gameName = match[1];
                    const key = gameName.toUpperCase();
                    // Fetch game details from Steam (from cache or API)
                    getSteamGameDetails(gameName).then(gameData => {
                        if (!gameData) return;
                        const descriptionText = gameData.about_the_game || "No description available.";
                        const bgImage = gameData.image_url || "https://images-1.gog-statics.com/6f3d015c3029fea5221ccd9802de5e2f92c6afccc0196b15540677341936a656.jpg";
                        div.textContent = '';

                        //Check div
                        const currentDiv = div;

                        const nextDiv = currentDiv.nextElementSibling;

                        if (nextDiv) {
                            nextDiv.appendChild(currentDiv);
                        }


            // Main div styling
            div.style.position = "relative";
            div.style.overflow = "hidden";
            div.style.height = "250px";
            div.style.borderRadius = "6px";
            div.style.fontFamily = '"Roboto", "Segoe UI", Tahoma, Geneva, Verdana, sans-serif';
            div.style.color = "white";
            div.style.outline = "none";
            div.style.border = "none";

            // Background image
            const img = document.createElement('img');
            img.src = bgImage;
            img.alt = gameName;
            img.style.width = "100%";
            img.style.height = "100%";
            img.style.objectFit = "cover";
            img.style.position = "absolute";
            img.style.top = 0;
            img.style.left = 0;
            img.style.opacity = 0.5;

            // Overlay
            const overlay = document.createElement('div');
            overlay.style.position = "absolute";
            overlay.style.top = 0;
            overlay.style.left = 0;
            overlay.style.width = "100%";
            overlay.style.height = "100%";
            overlay.style.padding = "10px";
            overlay.style.display = "flex";
            overlay.style.flexDirection = "column";
            overlay.style.justifyContent = "flex-start";
            overlay.style.background =
              "linear-gradient(to bottom, rgba(0,0,0,0.3), rgba(0,0,0,0.7))";

            // Content row
            const contentRow = document.createElement('div');
            contentRow.style.display = "flex";
            contentRow.style.flexDirection = "row";
            contentRow.style.flex = "1 1 auto";

            // Left column (launcher icon + tags)
            const leftColumn = document.createElement('div');
            leftColumn.style.display = "flex";
            leftColumn.style.flexDirection = "column";
            leftColumn.style.alignItems = "flex-start";
            leftColumn.style.marginRight = "15px";
            leftColumn.style.flexShrink = "0";


            // Add these:
            leftColumn.style.maxWidth = "250px"; // or a % like "35%" depending on your layout
            leftColumn.style.overflow = "visible"; // ensures it doesn’t break layout

            // New method for obtaining launcher info
            let foundLauncher = null;
            let ancestor = div;
            for (let i = 0; i < 9; i++) {
              if (!ancestor.parentElement) break;
              ancestor = ancestor.parentElement;
            }

            if (ancestor) {
              const launcher = ancestor.querySelector('div[role="button"], div.Focusable');
              if (launcher) {
                foundLauncher = launcher.textContent.trim();
              }
            }

            // Launcher icons
            const launcherIcons = {
              "Epic Games": "https://cdn2.steamgriddb.com/icon/34ffeb359a192eb8174b6854643cc046/32/96x96.png",
              "GOG Galaxy": "https://cdn2.steamgriddb.com/icon/a928731e103dfc64c0027fa84709689e/32/96x96.png",
              "NonSteamLaunchers": "https://raw.githubusercontent.com/moraroy/NonSteamLaunchers-On-Steam-Deck/refs/heads/main/logo.png",
              "Ubisoft Connect": "https://cdn2.steamgriddb.com/icon/dabcff9ba10224b01fd2ce83f7d73ad6/32/96x96.png",
              "EA App": "https://cdn2.steamgriddb.com/icon/ff51fb7a9bcb22c595616b4fa368880a/32/96x96.png",
              "Amazon Games": "https://cdn2.steamgriddb.com/icon_thumb/6e88ec1459f337d5bea6353f8bff8026.png",
              "itch.io": "https://cdn2.steamgriddb.com/icon/2ad9e5e943e43cad612a7996c12a8796/32/96x96.png",
              "Battle.net": "https://cdn2.steamgriddb.com/icon/739465804a0e17d2a47c9bc9c805d60a/32/96x96.png",
              "Legacy Games": "https://cdn2.steamgriddb.com/icon_thumb/5225802cb9758f9fcd34a679bf9326ec.png",
              "VK Play": "https://cdn2.steamgriddb.com/icon_thumb/5d35998237b55b8778a75732afc080aa.png",
              "HoyoPlay": "https://cdn2.steamgriddb.com/icon/817fccd834f01fb5e1770c8679c0824e/32/256x256.png",
              "Game Jolt Client": "https://cdn2.steamgriddb.com/icon_thumb/17df67628bb89193838f83015a3e7d30.png",
              "Minecraft Launcher": "https://cdn2.steamgriddb.com/icon/0678c572b0d5597d2d4a6b5bd135754c/32/96x96.png",
              "Humble Games Collection": "https://cdn2.steamgriddb.com/icon_thumb/3126ed973cbecde2bbffe419f139f456.png",
              "NVIDIA GeForce NOW": "https://cdn2.steamgriddb.com/icon_thumb/f91ee142269ec908c23e1cd87286e254.png",
              "Waydroid": "https://cdn2.steamgriddb.com/icon_thumb/d6de4f0418bf4015017f5c65cdecc46e.png",
              "Google Chrome": "https://cdn2.steamgriddb.com/icon/3941c4358616274ac2436eacf67fae05/32/256x256.png",
              "Brave": "https://cdn2.steamgriddb.com/icon_thumb/192d80a88b27b3e4115e1a45a782fe1b.png",
              "Vivaldi": "https://cdn2.steamgriddb.com/icon_thumb/51934729f32d36841a17e43e9390483a.png",
              "Mozilla Firefox": "https://cdn2.steamgriddb.com/icon_thumb/fe998b49c41c4208c968bce204fa1cbb.png",
              "LibreWolf": "https://cdn2.steamgriddb.com/icon/791608b685d1c61fb2fe8acdc69dc6b5/32/128x128.png",
              "Microsoft Edge": "https://cdn2.steamgriddb.com/icon_thumb/714cb7478d98b1cb51d1f5f515f060c7.png",
            };

            const launcherName = foundLauncher;
            const launcherIcon = (launcherName && launcherIcons[launcherName]) || null;

            if (launcherIcon) {
              // Row that holds launcher icon + music button
              const launcherRow = document.createElement('div');
              launcherRow.style.display = "flex";
              launcherRow.style.alignItems = "center";
              launcherRow.style.gap = "8px";
              launcherRow.style.marginBottom = "8px";

              // Launcher icon
              const icon = document.createElement('img');
              icon.src = launcherIcon;
              icon.alt = launcherName;
              icon.style.width = "60px";
              icon.style.height = "60px";
              icon.style.objectFit = "contain";
              icon.onerror = () => icon.remove();

              launcherRow.appendChild(icon);

              // Placeholder music button (no logic)
              const musicBtn = document.createElement('button');
              musicBtn.textContent = "🎵";
              musicBtn.style.background = "rgba(36,40,47,0.7)";
              musicBtn.style.color = "white";
              musicBtn.style.border = "none";
              musicBtn.style.borderRadius = "12px";
              musicBtn.style.padding = "6px 10px";
              musicBtn.style.fontSize = "14px";
              musicBtn.style.lineHeight = "1";
              musicBtn.style.cursor = "pointer";
              musicBtn.style.display = "flex";
              musicBtn.style.alignItems = "center";
              musicBtn.style.justifyContent = "center";
              musicBtn.style.transition = "background 0.2s ease";


              launcherRow.appendChild(musicBtn);
              attachThemeMusicBehavior(musicBtn);


              // Add row to left column
              leftColumn.appendChild(launcherRow);
            }


            function createTag(text, fontSize) {
              const tag = document.createElement('span');
              tag.textContent = text;
              tag.style.fontSize = fontSize; // ← use the value passed in
              tag.style.background = "rgba(36,40,47,0.7)";
              tag.style.padding = "3px 8px";
              tag.style.borderRadius = "12px";
              tag.style.whiteSpace = "normal";
              tag.style.display = "inline-block";
              tag.style.wordBreak = "break-word";
              tag.style.marginRight = "4px";
              tag.style.marginBottom = "4px";
              return tag;
            }

            function createTagRow(items) {
              const row = document.createElement('div');
              row.style.display = "flex";
              row.style.flexWrap = "wrap";
              row.style.gap = "4px";

              // Determine font size based on number of items
              const fontSize = items.length > 3 ? "7.8px" : "12px";

              items.forEach(item => row.appendChild(createTag(item, fontSize)));
              return row;
            }


            leftColumn.appendChild(createTagRow((gameData.platforms || "Unknown").split(",").map(p => p.trim())));
            leftColumn.appendChild(createTagRow((gameData.developer || "Unknown").split(",").map(d => d.trim())));
            leftColumn.appendChild(createTagRow((gameData.publisher || "Unknown").split(",").map(p => p.trim())));
            leftColumn.appendChild(createTagRow([gameData.release_date || "Unknown"]));
            leftColumn.appendChild(createTagRow((gameData.genres || "Unknown").split(",").map(g => g.trim())));

            // Right column (description)
            const rightColumn = document.createElement('div');
            rightColumn.style.display = "flex";
            rightColumn.style.flexDirection = "column";
            rightColumn.style.flex = "1";

            const description = document.createElement('p');
            description.textContent = descriptionText;
            description.style.fontSize = "14px";
            description.style.lineHeight = "1.4";
            description.style.background = "rgba(36,40,47,0.7)";
            description.style.padding = "8px 12px";
            description.style.borderRadius = "12px";
            description.style.wordBreak = "break-word";
            description.style.overflowWrap = "break-word";

            rightColumn.appendChild(description);
            contentRow.appendChild(leftColumn);
            contentRow.appendChild(rightColumn);
            overlay.appendChild(contentRow);

            // Bottom links
            const bottomLinks = document.createElement('div');
            bottomLinks.style.position = "absolute";
            bottomLinks.style.bottom = "34px";
            bottomLinks.style.left = "10px";
            bottomLinks.style.right = "10px";
            bottomLinks.style.display = "flex";
            bottomLinks.style.flexWrap = "wrap";
            bottomLinks.style.gap = "6px";

            const searchSites = [
              { name: "Google", url: "https://www.google.com/search?q=", icon: "https://upload.wikimedia.org/wikipedia/commons/2/2f/Google_2015_logo.svg" },

              { name: "PCGW", url: "https://www.pcgamingwiki.com/w/index.php?search=", extra: "&title=Special%3ASearch", icon: "https://pbs.twimg.com/profile_images/876511628258418689/Joehp5YI_400x400.jpg" },
              { name: "HLTB", url: "https://howlongtobeat.com/?q=", icon: "https://howlongtobeat.com/favicon.ico" },
              { name: "SDHQ", url: "https://steamdeckhq.com/?s=", icon: "https://pbs.twimg.com/profile_images/1539310786614419459/5ohiy0ZX_400x400.jpg" },
              { name: "GameFAQs", url: "https://gamefaqs.gamespot.com/search?game=", icon: "https://gamefaqs.gamespot.com/favicon.ico" },
              { name: "AWACY", url: "https://areweanticheatyet.com/?search=", icon: "https://areweanticheatyet.com/icon.webp" },
              { name: "ProtonDB", url: "https://www.protondb.com/search?q=", icon: "https://www.protondb.com/sites/protondb/images/site-logo.svg"},
            ];

            searchSites.forEach(site => {
              const link = document.createElement('a');
              // Minimal change: only modify IsThereAnyDeal URL
              let gameUrl = site.url + encodeURIComponent(gameName) + (site.extra || "");
              if (site.name === "IsThereAnyDeal") {
                // Convert gameName into ITAD slug
                const slug = gameName
                  .toLowerCase()
                  .replace(/[^a-z0-9 ]/g, '') // remove special chars
                  .trim()
                  .replace(/\s+/g, '-');      // spaces → hyphens
                gameUrl = `${site.url}${slug}/info/`;
              }


              link.href = gameUrl;
              link.target = "_blank";
              link.style.display = "inline-flex";
              link.style.alignItems = "center";
              link.style.background = "rgba(36,40,47,0.7)";
              link.style.color = "white";
              link.style.fontSize = "13px";
              link.style.padding = "4px 4px";
              link.style.borderRadius = "6px";
              link.style.textDecoration = "none";
              link.style.transition = "background 0.2s"; // Smooth transition on hover

              // Set initial background on hover state using CSS
              link.onmouseover = () => {
                link.style.background = "rgba(80,80,80,0.9)";
              };
              link.onmouseout = () => {
                link.style.background = "rgba(36,40,47,0.7)";
              };

              const linkIcon = document.createElement('img');
              linkIcon.src = site.icon;
              linkIcon.style.width = "16px";
              linkIcon.style.height = "16px";
              linkIcon.style.marginRight = "4px";
              link.prepend(linkIcon);

              link.appendChild(document.createTextNode(site.name));
              bottomLinks.appendChild(link);
            });


            // --- ITAD button directly under description ---
            const itadSite = {
                name: "",
                url: "https://isthereanydeal.com/game/",
                icon: "https://isthereanydeal.com/public/assets/logo-GBHE6XF2.svg"
            };

            const slug = gameName.toLowerCase()
                .replace(/[^a-z0-9 ]/g, '')
                .trim()
                .replace(/\s+/g, '-');

            const itadUrl = `${itadSite.url}${slug}/info/`;

            const itadLink = document.createElement('a');
            itadLink.href = itadUrl;
            itadLink.target = "_blank";
            itadLink.style.display = "inline-flex";
            itadLink.style.alignItems = "center";
            itadLink.style.background = "rgba(36,40,47,0.7)";
            itadLink.style.color = "white";
            itadLink.style.fontSize = "13px";
            itadLink.style.padding = "6px 12px";
            itadLink.style.borderRadius = "12px";
            itadLink.style.textDecoration = "none";
            itadLink.style.width = "max-content"; // ← keeps button snug
            rightColumn.style.display = "flex";
            rightColumn.style.flexDirection = "column";
            rightColumn.style.alignItems = "flex-end"; // ← aligns all children (including ITAD) to the right


            itadLink.style.marginTop = "0px"; // spacing below description

            itadLink.onmouseover = () => itadLink.style.background = "rgba(80,80,80,0.9)";
            itadLink.onmouseout = () => itadLink.style.background = "rgba(36,40,47,0.7)";

            const itadIcon = document.createElement('img');
            itadIcon.src = itadSite.icon;
            itadIcon.style.width = "16px";
            itadIcon.style.height = "16px";
            itadIcon.style.marginRight = "6px";
            itadLink.prepend(itadIcon);

            itadLink.appendChild(document.createTextNode(itadSite.name));

            // append it **directly under description** in right column
            rightColumn.appendChild(itadLink);





            overlay.appendChild(bottomLinks);
            div.appendChild(img);
            div.appendChild(overlay);
          });
        }
      }
    });
  }


  function attachThemeMusicBehavior(musicBtn) {
      const KEY = "ThemeMusicData";

      const load = () => {
          try { return JSON.parse(localStorage.getItem(KEY) || "{}"); }
          catch { return {}; }
      };

      const save = (data) => {
          try { localStorage.setItem(KEY, JSON.stringify(data)); }
          catch(e){ console.error(e); }
      };

      let data = load();
      let on = data.themeMusic === undefined ? true : !!data.themeMusic;

      // --- Container ---
      const container = document.createElement("div");
      Object.assign(container.style, {
          display: "inline-flex",
          alignItems: "center",
          position: "relative"
      });
      musicBtn.parentElement.insertBefore(container, musicBtn);
      container.appendChild(musicBtn);

      // Initial icon
      musicBtn.textContent = on ? "🎵" : "🔇";

      // --- Bubble tooltip ---
      const bubble = document.createElement("div");
      bubble.innerHTML = "Don't like what you hear? Use paste!";
      Object.assign(bubble.style, {
          position: "absolute",
          bottom: "30px",       // ← move above the button
          top: "auto",           // reset top
          left: "0",
          background: musicBtn.style.background,
          color: musicBtn.style.color,
          border: "none",
          borderRadius: musicBtn.style.borderRadius,
          padding: musicBtn.style.padding,
          fontSize: musicBtn.style.fontSize,
          whiteSpace: "nowrap",
          opacity: "0",
          transform: "translateY(10px)", // ← nudge down slightly for animation
          transition: "opacity 0.3s ease, transform 0.3s ease",
          pointerEvents: "auto",
          zIndex: "1000",
          cursor: "default"
      });

      container.appendChild(bubble);

      const showBubble = (text, isError=false) => {
          if (!on) return;

          if (text) {
              bubble.innerHTML = text;
          } else {
              const themeData = load();
              const current = themeData.currentlyPlaying;
              let linkHTML = "hear";
              if (current?.videoId) {
                  const videoUrl = `https://youtu.be/${current.videoId}`;
                  linkHTML = `<a href="${videoUrl}" target="_blank" style="color:#0af;text-decoration:underline; cursor:pointer;">hear</a>`;
              }
              bubble.innerHTML = `Don't like what you ${linkHTML}? Use paste!`;
          }

          bubble.style.opacity = "1";
          bubble.style.transform = "translateY(0)";
          bubble.style.backgroundColor = isError ? "#F44336" : musicBtn.style.background;
      };

      const hideBubble = () => {
          bubble.style.opacity = "0";
          bubble.style.transform = "translateY(-10px)";
      };

      // --- Paste button (pill style like music button) ---
      const pasteBtn = document.createElement("button");
      pasteBtn.textContent = "📋";
      Object.assign(pasteBtn.style, {
          background: musicBtn.style.background,
          color: musicBtn.style.color,
          border: "none",
          borderRadius: musicBtn.style.borderRadius,  // pill shape
          padding: musicBtn.style.padding,
          fontSize: musicBtn.style.fontSize,
          cursor: "pointer",
          marginLeft: "6px",
          opacity: 0,
          pointerEvents: "none",
          transition: "opacity 0.3s"
      });
      container.appendChild(pasteBtn);

      // --- Paste button logic ---
      pasteBtn.onclick = async () => {
          try {
              const text = await navigator.clipboard.readText();
              const match = text.match(/(?:youtube\.com\/.*v=|youtu\.be\/)([a-zA-Z0-9_-]{11})/);
              if (!match) return showBubble("Invalid YouTube link!", true);

              const newVideoId = match[1];
              const themeData = load();
              const currentThemeName = themeData.currentlyPlaying?.name;
              if (!currentThemeName || !themeData[currentThemeName])
                  return showBubble("No theme currently playing!", true);

              themeData[currentThemeName].videoId = newVideoId;
              themeData[currentThemeName].timestamp = Date.now();
              save(themeData);

              musicBtn.textContent = "🎵";
              showBubble(`Updated "${currentThemeName}"!`);
              setTimeout(() => {
                  pasteBtn.style.opacity = "0";
                  pasteBtn.style.pointerEvents = "none";
              }, 3000);
          } catch (e) {
              console.error(e);
              showBubble("Failed to read clipboard.", true);
          }
      };

      // --- Hover logic (includes bubble itself) ---
      [musicBtn, pasteBtn, bubble].forEach(el => {
          el.addEventListener("mouseenter", () => {
              if (on) {
                  showBubble();
                  pasteBtn.style.opacity = "1";
                  pasteBtn.style.pointerEvents = "auto";
              }
          });
          el.addEventListener("mouseleave", () => {
              setTimeout(() => {
                  if (!on || ![musicBtn, pasteBtn, bubble].some(el => el.matches(':hover'))) {
                      hideBubble();
                      pasteBtn.style.opacity = "0";
                      pasteBtn.style.pointerEvents = "none";
                  }
              }, 200); // slightly longer delay to allow moving into bubble
          });
      });

      // --- Toggle music on/off ---
      musicBtn.onclick = () => {
          on = !on;
          musicBtn.textContent = on ? "🎵" : "🔇";
          const saved = load();
          saved.themeMusic = on;
          save(saved);
          if (!on) {
              hideBubble();
              pasteBtn.style.opacity = "0";
              pasteBtn.style.pointerEvents = "none";
          }
      };
  }

  replaceText();

  if (!window.steamEnhancerObserver) {
      const observer = new MutationObserver(replaceText);
      observer.observe(document.body, { childList: true, subtree: true });

      window.steamEnhancerObserver = observer;
  }

})();
"""

def inject_metadata_code(ws_socket):
    inject_id = next(eval_id_counter)

    wrapped_code = f"""
    (function () {{
        {METADATA_CODE}
    }})();
    """

    send_ws_text(ws_socket, json.dumps({
        "id": inject_id,
        "method": "Runtime.evaluate",
        "params": {
            "expression": wrapped_code,
            "awaitPromise": True
        }
    }))

    recv_ws_message(ws_socket)


for target in (TARGET_TITLE2, TARGET_TITLE3):
    try:
        ws_url = get_ws_url_by_title(WS_HOST, WS_PORT, target)
        ws_socket = create_websocket_connection(ws_url)

        send_ws_text(ws_socket, json.dumps({
            "id": 1,
            "method": "Runtime.enable"
        }))
        recv_ws_message(ws_socket)

        inject_metadata_code(ws_socket)

    except Exception as e:
        print(f"Metadata injection failed for {target}: {e}")

