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

  if (!window.YT) {
    console.log("[Init] Loading YouTube IFrame API...");
    const tag = document.createElement('script');
    tag.src = "https://www.youtube.com/iframe_api";
    document.head.appendChild(tag);
  }

  // --- STOP WITH FADE OUT ---
  const stopPreviousAudio = () => {
    if (!ytPlayer) {
      currentQuery = null;
      return;
    }

    console.log("[Audio] Fading out previous YouTube player");

    if (fadeInterval) {
      clearInterval(fadeInterval);
      fadeInterval = null;
    }

    let volume = 100;
    fadeInterval = window.setInterval(() => {
      if (!ytPlayer || !ytPlayerReady) return;

      volume -= 5;
      if (volume <= 0) {
        clearInterval(fadeInterval!);
        fadeInterval = null;

        if (ytPlayer && typeof ytPlayer.stopVideo === "function") {
          ytPlayer.stopVideo();
        }

        ytPlayer.destroy?.();
        ytPlayer = null;
        ytPlayerReady = false;

        if (ytAudioIframe) {
          ytAudioIframe.remove();
          ytAudioIframe = null;
        }

        currentQuery = null;
        console.log("[Audio] Previous music stopped");
      } else {
        ytPlayer.setVolume(volume);
      }
    }, 50); // adjust fade speed here
  };
  // --- END FADE OUT ---

  // --- LOCAL STORAGE ---
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
  // --- END LOCAL STORAGE ---

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
  // --- END YOUTUBE PLAYER CREATION ---

  // --- PLAY AUDIO ---
  const playYouTubeAudio = (query: string) => {
    if (query === currentQuery) {
      console.log("[Audio] Already playing:", query);
      return;
    }

    console.log("[Audio] Requested:", query);
    stopPreviousAudio();
    currentQuery = query;

    if (sessionCache.has(query)) {
      console.log("[Audio] Playing from session cache:", query);
      createYTPlayer(sessionCache.get(query)!);
      return;
    }

    const cachedVideoId = loadFromLocalStorage(query);
    if (cachedVideoId) {
      console.log("[Audio] Playing from localStorage cache:", query);
      sessionCache.set(query, cachedVideoId);
      createYTPlayer(cachedVideoId);
      return;
    }

    const apiUrl = `https://nonsteamlaunchers.onrender.com/api/x7a9/${encodeURIComponent(query)}`;
    console.log("[Audio] Fetching video ID from API URL:", apiUrl);

    fetch(apiUrl)
      .then(res => res.json())
      .then(data => {
        const videoId = data.videoId;
        if (!videoId) return console.error("[Audio] No video found");

        sessionCache.set(query, videoId);
        saveToLocalStorage(query, videoId);
        console.log("[Audio] Video ID fetched and cached:", videoId);

        createYTPlayer(videoId);
      })
      .catch(err => console.error("[Audio] Failed to fetch video:", err));
  };
  // --- END PLAY AUDIO ---

  // --- URL HANDLING ---
  const updateMusicFromUrl = () => {
    const match = window.location.pathname.match(/\/routes?\/library\/app\/(\d+)/);
    if (!match) return stopPreviousAudio();

    const appId = Number(match[1]);
    if (!appStore?.m_mapApps) return;

    const appInfo = appStore.m_mapApps.get(appId);
    if (!appInfo?.display_name) return;

    const query = appInfo.display_name + " Theme Music";
    playYouTubeAudio(query);
  };

  const pushStateOrig = history.pushState;
  history.pushState = function (...args: any[]) {
    pushStateOrig.apply(this, args);
    updateMusicFromUrl();
  };
  window.addEventListener('popstate', () => updateMusicFromUrl());

  updateMusicFromUrl();
};
