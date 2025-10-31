let ytAudioIframe: HTMLDivElement | null = null;
let ytPlayer: YT.Player | null = null;
let ytPlayerReady = false;
let fadeInterval: number | null = null;

const sessionCache = new Map<string, string>();
const CACHE_EXPIRATION = 7 * 24 * 60 * 60 * 1000; // 7 days
let themeMusicInitialized = false;
let currentQuery: string | null = null;

const LOCAL_STORAGE_KEY = "ThemeMusicData"; // single key for all theme music

export const initThemeMusic = () => {
  if (themeMusicInitialized) return;
  themeMusicInitialized = true;

  // --- LOAD YOUTUBE IFRAME API ---
  if (!window.YT) {
    console.log("[Init] Loading YouTube IFrame API...");
    const tag = document.createElement('script');
    tag.src = "https://www.youtube.com/iframe_api";
    document.head.appendChild(tag);
  }

  // --- STOP PREVIOUS AUDIO (ASYNC WITH FADE) ---
  const stopPreviousAudio = async () => {
    if (!ytPlayer) {
      currentQuery = null;
      return;
    }

    console.log("[Audio] Fading out previous YouTube player");

    return new Promise<void>((resolve) => {
      if (fadeInterval) {
        clearInterval(fadeInterval);
        fadeInterval = null;
      }

      let volume = 100;

      fadeInterval = window.setInterval(() => {
        if (!ytPlayer) {
          clearInterval(fadeInterval!);
          fadeInterval = null;
          cleanup();
          resolve();
          return;
        }

        volume -= 5;
        ytPlayer.setVolume?.(Math.max(0, volume));

        if (volume <= 0) {
          clearInterval(fadeInterval!);
          fadeInterval = null;
          cleanup();
          resolve();
        }
      }, 50);

      const cleanup = () => {
        try {
          ytPlayer?.stopVideo?.();
          ytPlayer?.destroy?.();
        } catch (err) {
          console.warn("[Audio] Cleanup error:", err);
        }

        ytPlayer = null;
        ytPlayerReady = false;

        ytAudioIframe?.remove();
        ytAudioIframe = null;

        currentQuery = null;
        console.log("[Audio] Previous music stopped");
      };
    });
  };

  // --- LOCAL STORAGE HELPERS ---
  const saveToLocalStorage = (query: string, videoId: string) => {
    const rawData = localStorage.getItem(LOCAL_STORAGE_KEY);
    const data = rawData ? JSON.parse(rawData) : {};
    data[query] = { videoId, timestamp: Date.now() };
    localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify(data));
  };

  const loadFromLocalStorage = (query: string): string | null => {
    const rawData = localStorage.getItem(LOCAL_STORAGE_KEY);
    if (!rawData) return null;
    try {
      const data = JSON.parse(rawData) as Record<string, { videoId: string; timestamp: number }>;
      const entry = data[query];
      if (!entry) return null;
      if (Date.now() - entry.timestamp > CACHE_EXPIRATION) {
        console.log("[Audio] LocalStorage cache expired for:", query);
        delete data[query];
        localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify(data));
        return null;
      }
      return entry.videoId;
    } catch {
      return null;
    }
  };

  // --- YOUTUBE PLAYER CREATION ---
  const createYTPlayer = (videoId: string) => {
    console.log("[Audio] Creating iframe player for video ID:", videoId);

    ytAudioIframe = document.createElement("div");
    ytAudioIframe.id = "yt-audio-player";
    Object.assign(ytAudioIframe.style, {
      width: "0",
      height: "0",
      position: "absolute",
      opacity: "0",
      pointerEvents: "none"
    });
    document.body.appendChild(ytAudioIframe);

    ytPlayerReady = false;

    ytPlayer = new YT.Player("yt-audio-player", {
      height: '0',
      width: '0',
      videoId,
      playerVars: { autoplay: 1 },
      events: {
        onReady: () => {
          console.log("[Audio] Player ready, playing video...");
          ytPlayerReady = true;
          ytPlayer?.setVolume?.(100);
        },
        onStateChange: (e) => console.log("[Audio] Player state changed:", e.data),
        onError: (e) => {
          console.error("[Audio] YouTube Player error:", e);
          stopPreviousAudio();
        }
      }
    });
  };

  // --- PLAY AUDIO (WITH AWAITED CLEANUP) ---
  const playYouTubeAudio = async (query: string) => {
    if (query === currentQuery) {
      console.log("[Audio] Already playing:", query);
      return;
    }

    console.log("[Audio] Requested:", query);
    await stopPreviousAudio(); // wait until old music fully stops

    currentQuery = query;

    // Check session cache first
    if (sessionCache.has(query)) {
      console.log("[Audio] Playing from session cache:", query);
      createYTPlayer(sessionCache.get(query)!);
      return;
    }

    // Check local storage cache
    const cachedVideoId = loadFromLocalStorage(query);
    if (cachedVideoId) {
      console.log("[Audio] Playing from localStorage cache:", query);
      sessionCache.set(query, cachedVideoId);
      createYTPlayer(cachedVideoId);
      return;
    }

    // Fetch new video
    const apiUrl = `https://nonsteamlaunchers.onrender.com/api/x7a9/${encodeURIComponent(query)}`;
    console.log("[Audio] Fetching video ID from API URL:", apiUrl);

    try {
      const res = await fetch(apiUrl);
      const data = await res.json();
      const videoId = data.videoId;
      if (!videoId) return console.error("[Audio] No video found");

      sessionCache.set(query, videoId);
      saveToLocalStorage(query, videoId);
      console.log("[Audio] Video ID fetched and cached:", videoId);

      createYTPlayer(videoId);
    } catch (err) {
      console.error("[Audio] Failed to fetch video:", err);
    }
  };

  // --- DETECT AND HANDLE URL CHANGES ---
  const updateMusicFromUrl = async () => {
    const match = window.location.pathname.match(/\/routes?\/library\/app\/(\d+)/);

    if (!match) {
      // If leaving a game page, stop music
      await stopPreviousAudio();
      return;
    }

    const appId = Number(match[1]);
    if (!appStore?.m_mapApps) return;

    const appInfo = appStore.m_mapApps.get(appId);
    if (!appInfo?.display_name) return;

    const query = appInfo.display_name + " Theme Music";
    playYouTubeAudio(query);
  };

  // Monkey patch history methods to detect all navigations
  const interceptHistory = (method: 'pushState' | 'replaceState') => {
    const original = history[method];
    history[method] = function (...args: any[]) {
      const result = original.apply(this, args);
      updateMusicFromUrl();
      return result;
    };
  };

  interceptHistory('pushState');
  interceptHistory('replaceState');

  // Also handle browser back/forward buttons
  window.addEventListener('popstate', () => updateMusicFromUrl());

  // Initial page load
  updateMusicFromUrl();
};