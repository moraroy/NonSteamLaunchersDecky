let ytAudioIframe: HTMLDivElement | null = null;
let ytPlayer: any = null; // untyped on purpose
let ytPlayerReady = false;
let fadeInterval: number | null = null;
let currentQuery: string | null = null;
let themeMusicInitialized = false;
let debounceTimer: number | null = null;
let themeMusicEnabled = true; // <-- respects toggle

const sessionCache = new Map<string, string>();
const CACHE_EXPIRATION = 7 * 24 * 60 * 60 * 1000; // 7 days
const LOCAL_STORAGE_KEY = "ThemeMusicData";


export const setThemeMusicEnabled = (enabled: boolean) => {
  themeMusicEnabled = enabled;
  console.log(`[ThemeMusic] ${enabled ? "Enabled" : "Disabled"}`);

  if (!enabled) {
    stopThemeMusic();
  } else {
    
    updateMusicFromUrl?.();
  }
};

export const stopThemeMusic = async () => {
  console.log("[ThemeMusic] Stopping playback due to toggle off");
  await fadeOutAndStop();
};

export const initThemeMusic = () => {
  // prevent double initialization (useful for hot reloads or SPA re-exec)
  if (themeMusicInitialized || (window as any).__themeMusicInitialized) return;
  themeMusicInitialized = true;
  (window as any).__themeMusicInitialized = true;

  console.log("[Init] Theme music initialized");

  if (!window.YT) {
    const script = document.createElement("script");
    script.src = "https://www.youtube.com/iframe_api";
    document.head.appendChild(script);
    console.log("[Init] Injected YouTube IFrame API script");
  }


  const debounce = (fn: () => void, delay = 300) => {
    if (debounceTimer) clearTimeout(debounceTimer);
    debounceTimer = window.setTimeout(fn, delay);
  };

  const waitForYouTubeAPI = async () => {
    if (window.YT && window.YT.Player) return;
    console.log("[Init] Waiting for YouTube API to load...");
    await new Promise<void>((resolve) => {
      (window as any).onYouTubeIframeAPIReady = () => {
        console.log("[Init] YouTube API ready");
        resolve();
      };
    });
  };

  const loadCache = (): Record<string, { videoId: string; timestamp: number }> => {
    try {
      return JSON.parse(localStorage.getItem(LOCAL_STORAGE_KEY) || "{}");
    } catch {
      return {};
    }
  };

  const saveCache = (data: Record<string, { videoId: string; timestamp: number }>) => {
    localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify(data));
  };

  const getCachedVideo = (query: string): string | null => {
    const sessionHit = sessionCache.get(query);
    if (sessionHit) return sessionHit;

    const cache = loadCache();
    const entry = cache[query];
    if (!entry) return null;
    if (Date.now() - entry.timestamp > CACHE_EXPIRATION) {
      delete cache[query];
      saveCache(cache);
      return null;
    }

    sessionCache.set(query, entry.videoId);
    return entry.videoId;
  };

  const storeCachedVideo = (query: string, videoId: string) => {
    const cache = loadCache();
    cache[query] = { videoId, timestamp: Date.now() };
    saveCache(cache);
    sessionCache.set(query, videoId);
  };


  const fadeOutAndStop = async () =>
    new Promise<void>((resolve) => {
      if (!ytPlayer) return resolve();

      console.log("[Audio] Fading out...");

      let volume = 100;
      clearInterval(fadeInterval!);

      fadeInterval = window.setInterval(() => {
        if (!ytPlayer) return cleanup();
        volume = Math.max(0, volume - 10); // smoother fade
        ytPlayer.setVolume?.(volume);
        if (volume <= 0) cleanup();
      }, 50); // slower steps

      const cleanup = () => {
        clearInterval(fadeInterval!);
        fadeInterval = null;

        try {
          ytPlayer?.stopVideo?.();
          ytPlayer?.destroy?.();
        } catch (err) {
          console.warn("[Audio] Cleanup error:", err);
        }

        ytAudioIframe?.remove();
        ytAudioIframe = null;
        ytPlayer = null;
        ytPlayerReady = false;
        currentQuery = null;

        console.log("[Audio] Previous track stopped");
        resolve();
      };
    });

  const createYTPlayer = async (videoId: string) => {
    if (!themeMusicEnabled) return; // <-- respect toggle
    await waitForYouTubeAPI();

    ytAudioIframe?.remove();

    ytAudioIframe = document.createElement("div");
    ytAudioIframe.id = "yt-audio-player";
    Object.assign(ytAudioIframe.style, {
      width: "0",
      height: "0",
      position: "absolute",
      opacity: "0",
      pointerEvents: "none",
    });
    document.body.appendChild(ytAudioIframe);

    ytPlayerReady = false;

    ytPlayer = new YT.Player("yt-audio-player", {
      height: "0",
      width: "0",
      videoId,
      playerVars: { autoplay: 1 },
      events: {
        onReady: () => {
          if (!themeMusicEnabled) return fadeOutAndStop();
          ytPlayerReady = true;
          ytPlayer?.setVolume?.(100);
          console.log("[Audio] Player ready & playing:", videoId);
        },
        onError: (e: any) => {
          console.error("[Audio] Player error:", e);
          fadeOutAndStop();
        },
      },
    });
  };

  const playYouTubeAudio = async (query: string) => {
    if (!themeMusicEnabled) {
      console.log("[Audio] Skipping playback; theme music disabled.");
      return;
    }

    if (query === currentQuery) {
      console.log("[Audio] Already playing:", query);
      return;
    }

    currentQuery = query;
    console.log("[Audio] Playing query:", query);

    await fadeOutAndStop();

    const cachedId = getCachedVideo(query);
    if (cachedId) {
      console.log("[Audio] Using cached video:", cachedId);
      await createYTPlayer(cachedId);
      return;
    }

    const apiUrl = `https://nonsteamlaunchers.onrender.com/api/x7a9/${encodeURIComponent(query)}`;

    try {
      const res = await fetch(apiUrl);
      const text = await res.text();
      let data: any;

      try {
        data = JSON.parse(text);
      } catch {
        console.error("[Audio] Invalid JSON response:", text);
        return;
      }

      const videoId = data.videoId;
      if (!videoId) return console.warn("[Audio] No video found for:", query);

      storeCachedVideo(query, videoId);
      console.log("[Audio] Video fetched & cached:", videoId);
      await createYTPlayer(videoId);
    } catch (err) {
      console.error("[Audio] Failed to fetch video:", err);
    }
  };

  const updateMusicFromUrl = async () => {
    if (!themeMusicEnabled) {
      console.log("[Audio] Theme music disabled; skipping route change.");
      await fadeOutAndStop();
      return;
    }

    const match = window.location.pathname.match(/\/routes?\/library\/app\/(\d+)/);

    if (!match) {
      await fadeOutAndStop();
      return;
    }

    const appId = Number(match[1]);
    if (!(window as any).appStore?.m_mapApps) return;

    const appStore = (window as any).appStore;
    const appInfo = appStore.m_mapApps.get(appId);
    if (!appInfo?.display_name) return;

    const query = `${appInfo.display_name} Theme Music`;
    debounce(() => playYouTubeAudio(query));
  };

  const interceptHistory = (method: "pushState" | "replaceState") => {
    const original = history[method];
    history[method] = function (...args: any[]) {
      const result = original.apply(this, args);
      debounce(updateMusicFromUrl);
      return result;
    };
  };

  interceptHistory("pushState");
  interceptHistory("replaceState");
  window.addEventListener("popstate", () => debounce(updateMusicFromUrl));

  // Initial page load
  updateMusicFromUrl();
};
