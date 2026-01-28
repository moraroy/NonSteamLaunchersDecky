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