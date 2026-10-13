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







THEMEMUSIC_CODE = r"""
(function () {
    "use strict";

    if (window.__THEMEMUSIC_LOADED__) return;
    window.__THEMEMUSIC_LOADED__ = true;

    const LOCAL_STORAGE_KEY = "ThemeMusicData";
    const PLAYER_ID = "steam-theme-youtube";
    const YOUTUBE_ID_REGEX = /^[A-Za-z0-9_-]{11}$/;
    const MAX_SESSION_SONGS = 10;

    const sessionSongQueues = new Map();
    const reactPropsKeys = new WeakMap();
    const reactFiberKeys = new WeakMap();

    let ytAudioIframe = null;
    let detectedGame = null;
    let currentQuery = null;
    let currentVideoId = null;
    let searchingForGame = null;
    let observerScheduled = false;

    let gameModeContainer = null;
    let gameModeContainerValid = false;
    let cachedGameModeGame = null;
    let cachedDesktopGame = null;
    let cachedDesktopGameKey = null;

    let desktopControlState = null;
    let desktopControlStateTime = 0;
    let gameModeControlState = null;
    let gameModeControlStateTime = 0;

    let cacheData = null;
    let isNavigatingThemeMusic = false;

    const getThemeKey = (name) => {
        if (!name) return "";
        return name.endsWith(" Theme Music") ? name : `${name} Theme Music`;
    };

    function getReactKey(el, weakMap, prefix) {
        if (!el) return null;
        const cached = weakMap.get(el);
        if (cached !== undefined) return cached;
        const key = Object.keys(el).find(k => k.startsWith(prefix)) || null;
        weakMap.set(el, key);
        return key;
    }

    const getReactPropsKey = (el) => getReactKey(el, reactPropsKeys, "__reactProps");
    const getReactFiberKey = (el) => getReactKey(el, reactFiberKeys, "__reactFiber");

    function loadCache() {
        try {
            const raw = localStorage.getItem(LOCAL_STORAGE_KEY);
            if (raw === null) return (cacheData = {});
            const parsed = JSON.parse(raw);
            cacheData = (parsed && typeof parsed === "object" && !Array.isArray(parsed)) ? parsed : {};
        } catch {
            cacheData = {};
        }
        return cacheData;
    }

    function saveCache(data) {
        cacheData = data;
        try {
            localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify(data));
        } catch {}
    }

    function masterMusicEnabled() {
        const themeData = loadCache();
        return themeData.themeMusic === undefined ? true : (themeData.themeMusic === true || themeData.themeMusic === "true");
    }

    function currentGameMuted(game = null) {
        const themeData = loadCache();
        const name = game?.name ? getThemeKey(game.name) : (window.__THEMEMUSIC_CURRENT_GAME_NAME__ || themeData.currentlyPlaying?.name);
        if (!name) return false;
        const entry = themeData[name];
        return !!(entry && (entry.muted === true || entry.muted === "true"));
    }

    function isThemeMusicAllowed(game = null) {
        if (!masterMusicEnabled()) return false;
        return !currentGameMuted(game);
    }

    function setCurrentlyPlaying(game, videoId) {
        const cache = loadCache();
        const key = getThemeKey(game.name);
        if (!cache[key]) cache[key] = { muted: false };
        cache[key].videoId = videoId;
        cache[key].timestamp = Date.now();
        cache.currentlyPlaying = {
            name: key,
            videoId,
            timestamp: Date.now()
        };
        saveCache(cache);
    }

    function clearCurrentlyPlaying() {
        const cache = loadCache();
        delete cache.currentlyPlaying;
        saveCache(cache);
    }

    function getCachedVideo(gameName) {
        const cache = loadCache();
        const entry = cache[getThemeKey(gameName)];
        return (entry && typeof entry.videoId === "string" && YOUTUBE_ID_REGEX.test(entry.videoId)) ? entry : null;
    }

    function cacheVideo(game, video) {
        const cache = loadCache();
        const key = getThemeKey(game.name);
        const existing = cache[key] || {};

        cache[key] = {
            ...existing,
            muted: existing.muted ?? false,
            videoId: video.videoId,
            timestamp: Date.now()
        };
        saveCache(cache);
    }

    function getGameOverviewFromFiber(start) {
        let node = start;
        for (let depth = 0; node && depth < 8; depth++) {
            const result = node?.stateNode?.props?.children?.props?.children?.[0]?.props?.overview;
            if (typeof result?.display_name === "string" && result.appid != null) {
                return result;
            }
            node = node.return;
        }
        return null;
    }

    function inspectGameModeContainer(el) {
        const propsKey = getReactPropsKey(el);
        if (!propsKey) return null;
        const innerRef = el[propsKey]?.children?.[0]?.ref?.current?.props?.innerRef?.current;
        if (!innerRef) return null;
        const fiberKey = getReactFiberKey(innerRef);
        return fiberKey ? getGameOverviewFromFiber(innerRef[fiberKey]) : null;
    }

    function getDesktopAppId() {
        const path = window.location?.pathname || "";
        const match = path.match(/\/library\/app\/(\d+)/);
        if (match) return match[1];

        const hash = window.location?.hash || "";
        const hashMatch = hash.match(/\/library\/app\/(\d+)/);
        return hashMatch ? hashMatch[1] : null;
    }

    function getDesktopGame() {
        try {
            const id = getDesktopAppId();
            if (!id) {
                cachedDesktopGame = null;
                cachedDesktopGameKey = null;
                return null;
            }

            if (cachedDesktopGame && cachedDesktopGameKey === id) {
                return cachedDesktopGame;
            }

            const cells = document.querySelectorAll('[role="gridcell"]');
            for (const el of cells) {
                const propsKey = getReactPropsKey(el);
                if (!propsKey) continue;

                const game = el[propsKey]?.children?.[1]?.props?.item;
                if (game?.appid != null && String(game.appid) === id && typeof game.display_name === "string") {
                    cachedDesktopGame = { mode: "desktop", name: game.display_name, appid: String(game.appid) };
                    cachedDesktopGameKey = id;
                    return cachedDesktopGame;
                }
            }

            cachedDesktopGame = null;
            cachedDesktopGameKey = id;
            return null;
        } catch {
            return null;
        }
    }

    function getGameModeContainer() {
        if (gameModeContainerValid && gameModeContainer && document.documentElement.contains(gameModeContainer)) {
            return gameModeContainer;
        }

        gameModeContainer = null;
        gameModeContainerValid = false;

        let bestElement = null;
        let bestArea = 0;

        for (const el of document.querySelectorAll("body *")) {
            const overview = inspectGameModeContainer(el);
            if (!overview) continue;

            const rect = el.getBoundingClientRect();
            if (rect.width <= 0 || rect.height <= 0 || rect.bottom <= 0 || rect.right <= 0) continue;

            const area = rect.width * rect.height;
            if (area > bestArea) {
                bestArea = area;
                bestElement = el;
            }
        }

        if (bestElement) {
            gameModeContainer = bestElement;
            gameModeContainerValid = true;
        }

        return gameModeContainer;
    }

    function getGameModeGame() {
        const container = getGameModeContainer();
        if (!container) {
            cachedGameModeGame = null;
            return null;
        }

        try {
            const overview = inspectGameModeContainer(container);
            if (overview && typeof overview.display_name === "string" && overview.appid != null) {
                cachedGameModeGame = { mode: "game", name: overview.display_name, appid: String(overview.appid) };
                return cachedGameModeGame;
            }
            cachedGameModeGame = null;
            return null;
        } catch {
            return null;
        }
    }

    function getCurrentGame() {
        return getDesktopGame() || getGameModeGame();
    }

    function scanControlState() {
        let foundPlay = false, foundStop = false, foundResume = false;
        const controls = document.querySelectorAll("[role='button'], button, [tabindex]");

        for (const el of controls) {
            const text = (el.innerText || el.textContent || "").replace(/\s+/g, " ").trim().toUpperCase();
            if (!["PLAY", "STOP", "RESUME"].includes(text)) continue;

            const rect = el.getBoundingClientRect();
            if (rect.width <= 0 || rect.height <= 0 || rect.bottom <= 0 || rect.right <= 0) continue;

            if (text === "PLAY") foundPlay = true;
            if (text === "STOP") foundStop = true;
            if (text === "RESUME") foundResume = true;

            if (foundPlay && foundStop && foundResume) break;
        }

        return { foundPlay, foundStop, foundResume };
    }

    function getCachedControlState(currentState, lastTime, ttl) {
        const now = performance.now();
        if (currentState && (now - lastTime < ttl)) return { state: currentState, time: lastTime };
        return { state: scanControlState(), time: now };
    }

    function getDesktopControlState() {
        const res = getCachedControlState(desktopControlState, desktopControlStateTime, 50);
        desktopControlState = res.state;
        desktopControlStateTime = res.time;
        return desktopControlState;
    }

    function getGameModeControlState() {
        const res = getCachedControlState(gameModeControlState, gameModeControlStateTime, 100);
        gameModeControlState = res.state;
        gameModeControlStateTime = res.time;
        return gameModeControlState;
    }

    function invalidateControlState() {
        desktopControlState = null;
        desktopControlStateTime = 0;
        gameModeControlState = null;
        gameModeControlStateTime = 0;
    }

    function checkGameRunning(getStateFn) {
        const state = getStateFn();
        if (state.foundStop || state.foundResume) return true;
        if (state.foundPlay) return false;
        return null;
    }

    const getDesktopGameRunning = () => checkGameRunning(getDesktopControlState);
    const getGameModeGameRunning = () => checkGameRunning(getGameModeControlState);

    async function fetchSearchResults(query) {
        const EXCLUDED_PATTERNS = /\b(how\s+to\s+play|tutorial|guitar\s+lesson|piano\s+lesson|cover|remix)\b/i;

        try {
            const r = await fetch("https://search.tiago.zip/api", {
                method: "POST",
                mode: "cors",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ query, type: "web", page: 0 })
            });

            if (!r.ok) return [];

            const data = await r.json();
            const results = data.results?.web?.results || [];
            const parsedResults = [];

            for (const result of results) {
                const { title = "", url = "", description = "", snippet = "" } = result;

                if (url.match(/(\/playlist\?|\/channel\/|\/@|\/shorts\/)/)) continue;

                const fullText = `${title} ${description} ${snippet}`;
                if (EXCLUDED_PATTERNS.test(fullText)) continue;

                let parsed;
                try { parsed = new URL(url); } catch { continue; }

                let videoId = null;
                const host = parsed.hostname;
                const pathParts = parsed.pathname.split("/").filter(Boolean);

                if (["www.youtube.com", "youtube.com", "music.youtube.com"].includes(host)) {
                    if (parsed.pathname === "/watch") videoId = parsed.searchParams.get("v");
                    else if (pathParts.length === 2 && pathParts[0] === "watch") videoId = pathParts[1];
                } else if (host === "youtu.be" && pathParts.length === 1) {
                    videoId = pathParts[0];
                }

                if (videoId && YOUTUBE_ID_REGEX.test(videoId)) {
                    parsedResults.push({
                        title,
                        videoId,
                        url: `https://www.youtube.com/watch?v=${videoId}`
                    });
                }
            }
            return parsedResults;
        } catch {
            return [];
        }
    }

    async function findYouTubeVideo(gameName) {
        const searches = [
            `${gameName} Game Theme Music site:youtube.com`,
            `${gameName} Original Theme site:youtube.com`,
            `${gameName} Main Theme site:youtube.com`,
            `${gameName} Original Main Theme site:youtube.com`
        ];

        for (const query of searches) {
            const results = await fetchSearchResults(query);
            if (results.length > 0) return results[0];
        }
        return null;
    }

    async function findYouTubeVideos(gameName) {
        const searches = [
            `${gameName} Game Theme Music site:youtube.com`,
            `${gameName} Original Theme site:youtube.com`,
            `${gameName} Main Theme site:youtube.com`,
            `${gameName} Original Main Theme site:youtube.com`
        ];

        const songs = [];
        const seen = new Set();

        for (const query of searches) {
            if (songs.length >= MAX_SESSION_SONGS) break;

            const results = await fetchSearchResults(query);
            for (const song of results) {
                if (songs.length >= MAX_SESSION_SONGS) break;
                if (!seen.has(song.videoId)) {
                    seen.add(song.videoId);
                    songs.push(song);
                }
            }
        }
        return songs;
    }

    function createYTPlayer(videoId) {
        if (!videoId) return;

        const existing = document.getElementById(PLAYER_ID);
        if (existing) {
            if (existing.getAttribute("src")?.includes(`/embed/${videoId}`)) {
                ytAudioIframe = existing;
                return;
            }
            existing.remove();
            if (ytAudioIframe === existing) ytAudioIframe = null;
        }

        const iframe = document.createElement("iframe");
        iframe.id = PLAYER_ID;
        iframe.src = `https://www.youtube.com/embed/${encodeURIComponent(videoId)}?autoplay=1&loop=1&playlist=${encodeURIComponent(videoId)}&controls=0&rel=0`;
        iframe.allow = "autoplay; encrypted-media";

        Object.assign(iframe.style, {
            position: "fixed",
            width: "1px",
            height: "1px",
            left: "0",
            top: "0",
            border: "0",
            opacity: "0",
            pointerEvents: "none",
            zIndex: "2147483647"
        });

        document.body.appendChild(iframe);
        ytAudioIframe = iframe;
    }

    function stopMusic() {
        if (ytAudioIframe) {
            try { ytAudioIframe.remove(); } catch {}
            ytAudioIframe = null;
        }

        document.getElementById(PLAYER_ID)?.remove();

        currentQuery = null;
        currentVideoId = null;
        clearCurrentlyPlaying();
    }

    function startSong(game, videoId) {
        if (!isThemeMusicAllowed(game)) {
            stopMusic();
            return;
        }

        if (ytAudioIframe) stopMusic();

        currentQuery = game.name;
        currentVideoId = videoId;
        setCurrentlyPlaying(game, videoId);
        createYTPlayer(videoId);
    }

    async function playThemeMusic(game) {
        if (!game) return;

        if (!isThemeMusicAllowed(game)) {
            if (ytAudioIframe) stopMusic();
            return;
        }

        const appid = String(game.appid);
        if (currentQuery === game.name && ytAudioIframe) return;

        const cached = getCachedVideo(game.name);
        if (cached) {
            if (currentVideoId === cached.videoId && ytAudioIframe) {
                currentQuery = game.name;
                setCurrentlyPlaying(game, cached.videoId);
                return;
            }
            startSong(game, cached.videoId);
            return;
        }

        if (searchingForGame === appid) return;
        searchingForGame = appid;

        const found = await findYouTubeVideo(game.name);

        if (searchingForGame !== appid) return;
        searchingForGame = null;

        if (!found || !isThemeMusicAllowed(game)) return;

        const current = getCurrentGame();
        if (!current || String(current.appid) !== appid) return;

        const isRunning = current.mode === "desktop" ? getDesktopGameRunning() : getGameModeGameRunning();
        if (isRunning === true) return;

        cacheVideo(game, found);
        startSong(game, found.videoId);
    }

    async function navigateThemeMusic(direction) {
        const game = detectedGame;
        if (!game || !isThemeMusicAllowed(game) || ![1, -1].includes(direction)) return;

        const appid = String(game.appid);
        let queue = sessionSongQueues.get(appid);

        if (!queue) {
            queue = { songs: [], index: -1, loading: true };
            sessionSongQueues.set(appid, queue);

            if (currentVideoId) {
                queue.songs.push({ videoId: currentVideoId, title: "Currently playing" });
                queue.index = 0;
            }

            try {
                const results = await findYouTubeVideos(game.name);
                const current = getCurrentGame();

                if (String(detectedGame?.appid) !== appid || !current?.appid || String(current.appid) !== appid) {
                    sessionSongQueues.delete(appid);
                    return;
                }

                const seen = new Set(queue.songs.map(song => song.videoId));
                for (const song of results) {
                    if (queue.songs.length >= MAX_SESSION_SONGS) break;
                    if (!seen.has(song.videoId)) {
                        seen.add(song.videoId);
                        queue.songs.push(song);
                    }
                }
            } catch (error) {
                console.error("[ThemeMusic] Failed to build song queue:", error);
                sessionSongQueues.delete(appid);
                return;
            } finally {
                queue.loading = false;
            }
        }

        if (sessionSongQueues.get(appid) !== queue || queue.loading || queue.songs.length === 0) return;
        if (!isThemeMusicAllowed(game)) return;

        const playingIndex = queue.songs.findIndex(song => song.videoId === currentVideoId);
        if (playingIndex >= 0) queue.index = playingIndex;

        let nextIndex = queue.index;
        let song = null;

        for (let i = 0; i < queue.songs.length; i++) {
            nextIndex = (nextIndex + direction + queue.songs.length) % queue.songs.length;
            const candidate = queue.songs[nextIndex];
            if (candidate?.videoId && candidate.videoId !== currentVideoId) {
                song = candidate;
                break;
            }
        }

        if (!song) return;
        queue.index = nextIndex;

        const current = getCurrentGame();
        if (!current || String(current.appid) !== appid || !isThemeMusicAllowed(game)) return;

        startSong(game, song.videoId);

        cacheVideo(game, song);
        setCurrentlyPlaying(game, song.videoId);

        selectedSong = {
            name: getThemeKey(game.name),
            videoId: song.videoId
        };

        updateButtonsUI();
    }

    function handleDetectedGame(game) {
        if (!game) return;

        window.__THEMEMUSIC_CURRENT_GAME_NAME__ = getThemeKey(game.name);
        const appid = String(game.appid);
        const changed = !detectedGame || String(detectedGame.appid) !== appid || detectedGame.mode !== game.mode;

        if (changed) {
            if (ytAudioIframe) stopMusic();
            detectedGame = { mode: game.mode, appid, name: game.name };
            searchingForGame = null;
            selectedSong = null;
        }

        updateButtonsUI();

        if (!isThemeMusicAllowed(game)) {
            if (ytAudioIframe) stopMusic();
            return;
        }

        const running = game.mode === "desktop" ? getDesktopGameRunning() : getGameModeGameRunning();

        if (running === true) {
            if (ytAudioIframe) stopMusic();
            return;
        }

        if (running === null) return;

        if (!ytAudioIframe && !isNavigatingThemeMusic) {
            playThemeMusic(game);
        }
    }

    function processGameState() {
        updateButtonsUI();

        if (!masterMusicEnabled()) {
            if (ytAudioIframe) stopMusic();
            return;
        }

        const desktopAppId = getDesktopAppId();
        if (desktopAppId) {
            const desktopGame = getDesktopGame();
            if (desktopGame) {
                handleDetectedGame(desktopGame);
                if (currentGameMuted(desktopGame) && ytAudioIframe) {
                    stopMusic();
                }
                return;
            }
        }

        const gameModeGame = getGameModeGame();
        if (gameModeGame) {
            handleDetectedGame(gameModeGame);
            if (currentGameMuted(gameModeGame) && ytAudioIframe) {
                stopMusic();
            }
            return;
        }

        if (detectedGame?.mode === "game") {
            stopMusic();
            detectedGame = null;
            searchingForGame = null;
            cachedGameModeGame = null;
            gameModeContainer = null;
            gameModeContainerValid = false;
        }
    }

    function scheduleStateCheck() {
        if (observerScheduled) return;
        observerScheduled = true;

        requestAnimationFrame(() => {
            observerScheduled = false;
            invalidateControlState();
            processGameState();
        });
    }

    const IDS = {
        left: "my-custom-left-arrow",
        music: "my-custom-music-button",
        mute: "my-custom-mute-button",
        right: "my-custom-right-arrow",
        message: "my-custom-paste-message"
    };

    const LABEL = "Configure Controller";

    window.music?.cleanup?.();
    window.customPaste?.cleanup?.();

    const el = n => n?.Element || n?.m_element || null;
    const kids = n => Array.isArray(n?.m_rgChildren) ? n.m_rgChildren : [];
    const par = n => n?.Parent || n?.m_Parent || null;

    const listeners = new AbortController();
    const opts = { signal: listeners.signal };

    const buttons = {};
    const navNodes = [];

    let parent;
    let originalStyle;
    let parentNode;
    let message;

    const restoreStyle = () => {
        if (!parent) return;
        if (originalStyle === null) parent.removeAttribute("style");
        else parent.setAttribute("style", originalStyle);
    };

    const cleanup = () => {
        listeners.abort();
        navNodes.forEach(node => {
            try { node.OnUnmount?.(); } catch {}
        });

        Object.values(buttons).forEach(button => button.remove());
        message?.remove();
        restoreStyle();

        if (window.music?.element === buttons.music) delete window.music;
        if (window.customPaste?.cleanup === cleanup) delete window.customPaste;
    };

    const makeButton = (source, id, label, content) => {
        const button = source.cloneNode(true);

        button.id = id;
        button.tabIndex = 0;
        button.setAttribute("aria-label", label);
        button.removeAttribute("aria-describedby");
        button.removeAttribute("disabled");
        button.removeAttribute("aria-disabled");

        button.querySelectorAll("[id],[aria-label]").forEach(node => {
            node.removeAttribute("id");
            node.removeAttribute("aria-label");
        });

        button.replaceChildren();

        const span = document.createElement("span");
        Object.assign(span.style, {
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            width: "100%",
            height: "100%",
            font: "500 1.1em/1 sans-serif",
            pointerEvents: "none",
            userSelect: "none",
            whiteSpace: "nowrap"
        });

        span.textContent = content;
        button.append(span);

        return button;
    };

    const registerNavigation = (button, navKey, tree, parentNode, referenceNode) => {
        if (!tree || !referenceNode) return null;

        const node = new referenceNode.constructor(tree, parentNode, null);
        node.SetProperties({
            layout: referenceNode.m_Properties?.layout ?? 0,
            focusable: true,
            preferredFocus: false,
            autoFocus: false,
            noFocusRing: referenceNode.m_Properties?.noFocusRing ?? true,
            navKey
        });

        node.OnMount(button);
        navNodes.push(node);

        return node;
    };

    const wireFocus = button => {
        ["focus", "blur", "vgp_onfocus", "vgp_onblur"].forEach((evt, i) => {
            button.addEventListener(evt, () => {
                button.style.filter = i % 2 === 0 ? "brightness(1.15)" : "";
            }, opts);
        });
    };

    const specs = [
        ["left", IDS.left, "Previous theme song", "❮", "custom-left-arrow"],
        ["music", IDS.music, "Music options", "🎵", "custom-music"],
        ["mute", IDS.mute, "Toggle master theme music", "🔇", "custom-mute"],
        ["right", IDS.right, "Next theme song", "❯", "custom-right-arrow"]
    ];

    let selectedSong = null;
    let isHoldingMusic = false;
    let holdStarted = false;
    let holdTimer = null;
    let holdActionInProgress = false;
    let suppressNextClick = false;
    let holdPointerId = null;

    const musicIsAudibleEnabled = () => masterMusicEnabled() && !currentGameMuted();

    const getMasterMuteIcon = () => masterMusicEnabled() ? "🔊" : "🔇";
    const getMusicActionIcon = () => currentGameMuted() ? "🔕" : "🎵";

    const showInlineMessage = (text, isError = false, persistent = false) => {
        if (!message) return;
        message.textContent = text;
        message.style.color = isError ? "#e05252" : "#ffffff";
        message.style.display = "inline-flex";

        if (!persistent) {
            setTimeout(() => {
                if (!holdStarted && !isHoldingMusic && message) {
                    message.style.display = "none";
                }
            }, 3000);
        }
    };

    const updateButtonsUI = () => {
        if (!buttons.mute || !buttons.music) return;

        const muteSpan = buttons.mute.querySelector("span");
        if (muteSpan) muteSpan.textContent = getMasterMuteIcon();
        buttons.mute.setAttribute("aria-label", masterMusicEnabled() ? "Disable master theme music" : "Enable master theme music");

        const musicSpan = buttons.music.querySelector("span");
        if (musicSpan) {
            if (isHoldingMusic && holdStarted) {
                musicSpan.textContent = selectedSong?.videoId ? "💾" : "📋";
                buttons.music.setAttribute("aria-label", selectedSong?.videoId ? "Release to save this theme song" : "Release to paste a YouTube link");
            } else {
                musicSpan.textContent = getMusicActionIcon();
                buttons.music.setAttribute("aria-label", currentGameMuted() ? "Unmute this game's theme music" : "Mute this game's theme music");
            }
        }

        if (!isHoldingMusic || !holdStarted) {
            if (message) message.style.display = "none";
        }
    };

    let isNavigating = false;
    const setNavigationBusy = (busy) => {
        isNavigating = busy;
        [buttons.left, buttons.right].forEach(btn => {
            if (!btn) return;
            btn.disabled = busy;
            btn.style.opacity = busy ? "0.4" : "1";
            btn.style.cursor = busy ? "wait" : "pointer";
        });
    };

    const triggerPreviousSong = async () => {
        if (isNavigating) return;
        setNavigationBusy(true);
        await navigateThemeMusic(-1);
        setNavigationBusy(false);
    };

    const triggerNextSong = async () => {
        if (isNavigating) return;
        setNavigationBusy(true);
        await navigateThemeMusic(1);
        setNavigationBusy(false);
    };

    const performPasteOrSave = async () => {
        if (holdActionInProgress || !musicIsAudibleEnabled()) return;
        holdActionInProgress = true;

        try {
            const themeData = loadCache();
            if (selectedSong?.videoId) {
                const gameName = selectedSong.name || window.__THEMEMUSIC_CURRENT_GAME_NAME__ || themeData.currentlyPlaying?.name;

                if (!gameName) {
                    showInlineMessage("No active game detected!", true);
                    return;
                }

                if (!themeData[gameName]) {
                    themeData[gameName] = { muted: false };
                }

                themeData[gameName].videoId = selectedSong.videoId;
                themeData[gameName].timestamp = Date.now();
                saveCache(themeData);
                showInlineMessage("Theme song saved to storage!");
                selectedSong = null;
                return;
            }

            const text = await navigator.clipboard.readText();
            if (!musicIsAudibleEnabled()) return;

            const match = text.match(/(?:youtube\.com\/.*v=|youtu\.be\/)([a-zA-Z0-9_-]{11})/);
            if (!match) {
                showInlineMessage("Invalid YouTube link!", true);
                return;
            }

            const newVideoId = match[1];
            const currentThemeName = window.__THEMEMUSIC_CURRENT_GAME_NAME__ || themeData.currentlyPlaying?.name;

            if (!currentThemeName) {
                showInlineMessage("No theme currently playing!", true);
                return;
            }

            if (!themeData[currentThemeName]) {
                themeData[currentThemeName] = { muted: false };
            }

            themeData[currentThemeName].videoId = newVideoId;
            themeData[currentThemeName].timestamp = Date.now();
            saveCache(themeData);

            if (detectedGame && getThemeKey(detectedGame.name) === currentThemeName && isThemeMusicAllowed(detectedGame)) {
                startSong(detectedGame, newVideoId);
            }

            updateButtonsUI();
            showInlineMessage(`Pasted & saved "${currentThemeName}"!`);
        } catch (e) {
            console.error(e);
            showInlineMessage("Failed to read clipboard.", true);
        } finally {
            holdActionInProgress = false;
            isHoldingMusic = false;
            holdStarted = false;
            holdPointerId = null;
            updateButtonsUI();
        }
    };

    const toggleMasterMute = () => {
        const saved = loadCache();
        const newState = !masterMusicEnabled();
        saved.themeMusic = newState;
        saveCache(saved);

        updateButtonsUI();

        if (!newState) {
            stopMusic();
        } else {
            scheduleStateCheck();
        }
    };

    const toggleGameMute = () => {
        if (suppressNextClick || holdStarted || holdActionInProgress) {
            suppressNextClick = false;
            return;
        }

        const saved = loadCache();
        const gameName = window.__THEMEMUSIC_CURRENT_GAME_NAME__ || saved.currentlyPlaying?.name;
        if (!gameName) return;

        if (!saved[gameName]) {
            saved[gameName] = { muted: false };
        }

        const currentMuted = !!(saved[gameName].muted === true || saved[gameName].muted === "true");
        saved[gameName].muted = !currentMuted;

        saveCache(saved);
        updateButtonsUI();

        if (saved[gameName].muted) {
            stopMusic();
        } else {
            scheduleStateCheck();
        }
    };

    function injectButtons() {
        if (document.getElementById(IDS.music)?.isConnected) return;

        const trees = window.opener?.g_WindowFocusCoordinator?.m_rgTrees ?? [];
        const tree = trees.find(entry => entry.tree?.m_ID === "GamepadUI_Full_Root")?.tree;

        const walk = root => {
            const stack = [root];
            const seen = new Set();
            while (stack.length) {
                const n = stack.pop();
                if (!n || seen.has(n)) continue;
                seen.add(n);
                if (el(n)?.getAttribute?.("aria-label") === LABEL) return n;
                stack.push(...kids(n));
            }
            return null;
        };

        const referenceNode = tree?.Root ? walk(tree.Root) : null;
        const fallback = !tree || !referenceNode;

        const source = fallback ? document.querySelectorAll('[aria-label="Manage"]')[1] : el(referenceNode);
        if (!source || (!fallback && !par(referenceNode))) return;

        if (!fallback) parentNode = par(referenceNode);
        parent = source.parentElement;
        if (!parent) return;

        originalStyle = parent.getAttribute("style");
        parent.style.display = "flex";

        navNodes.length = 0;

        specs.forEach(([key, id, label, content, navKey]) => {
            document.getElementById(id)?.remove();
            const button = makeButton(source, id, label, content);
            buttons[key] = button;
            parent.insertBefore(button, source);
            if (!fallback && navKey) registerNavigation(button, navKey, tree, parentNode, referenceNode);
            wireFocus(button);
        });

        buttons.left.addEventListener("click", triggerPreviousSong, opts);
        buttons.left.addEventListener("vgp_onbuttondown", event => {
            if (event.detail?.button === 1 && event.detail.is_repeat !== true) {
                triggerPreviousSong();
            }
        }, opts);

        buttons.right.addEventListener("click", triggerNextSong, opts);
        buttons.right.addEventListener("vgp_onbuttondown", event => {
            if (event.detail?.button === 1 && event.detail.is_repeat !== true) {
                triggerNextSong();
            }
        }, opts);

        buttons.mute.addEventListener("click", (e) => {
            if (e.detail !== 0) toggleMasterMute();
        }, opts);
        buttons.mute.addEventListener("vgp_onbuttondown", event => {
            if (event.detail?.button === 1 && event.detail.is_repeat !== true) {
                toggleMasterMute();
            }
        }, opts);

        if (fallback) {
            const startMusicHold = (event) => {
                if (event.button !== undefined && event.button !== 0) return;
                if (!musicIsAudibleEnabled() || isHoldingMusic) return;

                clearTimeout(holdTimer);
                isHoldingMusic = true;
                holdStarted = false;
                holdPointerId = event.pointerId ?? null;

                holdTimer = setTimeout(() => {
                    if (!isHoldingMusic || !musicIsAudibleEnabled()) {
                        isHoldingMusic = false;
                        holdStarted = false;
                        updateButtonsUI();
                        return;
                    }

                    holdStarted = true;
                    updateButtonsUI();
                    showInlineMessage(selectedSong?.videoId ? "Release to save this theme song." : "Release to paste a YouTube link.", false, true);
                }, 450);
            };

            const endMusicHold = (event) => {
                if (!isHoldingMusic) return;
                if (holdPointerId !== null && event?.pointerId !== undefined && event.pointerId !== holdPointerId) return;

                clearTimeout(holdTimer);
                const wasFourthState = holdStarted;
                isHoldingMusic = false;
                holdStarted = false;
                holdPointerId = null;

                if (wasFourthState) {
                    suppressNextClick = true;
                    setTimeout(() => { suppressNextClick = false; }, 0);
                    if (musicIsAudibleEnabled()) performPasteOrSave();
                    else updateButtonsUI();
                    return;
                }

                updateButtonsUI();
            };

            buttons.music.addEventListener("pointerdown", startMusicHold, opts);
            window.addEventListener("pointerup", endMusicHold, opts);
            window.addEventListener("pointercancel", endMusicHold, opts);
            buttons.music.addEventListener("click", (e) => {
                if (e.detail !== 0) toggleGameMute();
            }, opts);
            buttons.music.addEventListener("contextmenu", event => {
                if (holdStarted) event.preventDefault();
            }, opts);
        } else {
            let controllerHoldTimer = null;
            let isButtonDown = false;

            buttons.music.addEventListener("vgp_onbuttondown", event => {
                if (event.detail?.button === 1 && event.detail.is_repeat !== true) {
                    isButtonDown = true;
                    isHoldingMusic = true;
                    holdStarted = false;
                    clearTimeout(controllerHoldTimer);

                    if (musicIsAudibleEnabled()) {
                        controllerHoldTimer = setTimeout(() => {
                            if (!isButtonDown || !musicIsAudibleEnabled()) return;
                            holdStarted = true;
                            updateButtonsUI();
                            showInlineMessage(selectedSong?.videoId ? "Release to save this theme song." : "Release to paste a YouTube link.", false, true);
                        }, 450);
                    }
                }
            }, opts);

            buttons.music.addEventListener("vgp_onbuttonup", event => {
                if (event.detail?.button === 1) {
                    if (!isButtonDown) return;
                    isButtonDown = false;
                    clearTimeout(controllerHoldTimer);

                    const wasFourthState = holdStarted;
                    holdStarted = false;
                    isHoldingMusic = false;

                    if (wasFourthState) {
                        suppressNextClick = true;
                        setTimeout(() => { suppressNextClick = false; }, 0);

                        if (musicIsAudibleEnabled()) performPasteOrSave();
                        else updateButtonsUI();
                        return;
                    }

                    updateButtonsUI();
                    toggleGameMute();
                }
            }, opts);
        }

        document.getElementById(IDS.message)?.remove();
        message = document.createElement("span");
        message.id = IDS.message;
        message.textContent = "";

        Object.assign(message.style, {
            display: "none",
            alignItems: "center",
            alignSelf: "center",
            marginRight: "10px",
            color: "#e05252",
            font: '500 13px/1.2 "Motiva Sans", Arial, sans-serif',
            whiteSpace: "nowrap",
            pointerEvents: "none",
            userSelect: "none"
        });

        parent.insertBefore(message, buttons.left);
        updateButtonsUI();
    }

    new MutationObserver(mutations => {
        if (mutations.some(m => m.type === "childList")) {
            invalidateControlState();
            gameModeContainerValid = false;
            scheduleStateCheck();
            injectButtons();
        }
    }).observe(document.body, { childList: true, subtree: true });

    window.music = {
        get element() { return buttons.music; },
        cleanup,
        get state() { return getMusicActionIcon(); },
        diagnose: () => ({
            buttonsConnected: Object.fromEntries(Object.entries(buttons).map(([k, b]) => [k, b?.isConnected])),
            musicState: getMusicActionIcon(),
            pasteMessageVisible: message?.style.display !== "none",
            navigationNodes: navNodes.length
        })
    };

    window.customPaste = {
        get left() { return buttons.left; },
        get right() { return buttons.right; },
        get message() { return message; },
        cleanup,
        diagnose: window.music.diagnose
    };

    injectButtons();
    processGameState();

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








### METADATA ONLY
METADATA_CODE = r"""
(function () {
    if (window.__MY_METADATA_SCRIPT_LOADED__) return;
    window.__MY_METADATA_SCRIPT_LOADED__ = true;

    const gameCache = {};
    const playerCache = {};
    const hltbCache = {};

    async function getSteamPlayerCount(appId) {
        const now = Date.now();
        if (playerCache[appId] && now - playerCache[appId].timestamp < 30000) {
            return playerCache[appId].value;
        }
        try {
            const res = await fetch(`https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/?appid=${appId}`);
            if (!res.ok) return null;
            const data = await res.json();
            const value = data?.response?.player_count ?? null;
            playerCache[appId] = { value, timestamp: now };
            return value;
        } catch {
            return null;
        }
    }

    async function getSteamGameDetails(gameName) {
        if (gameCache[gameName]) return gameCache[gameName];
        try {
            const searchRes = await fetch(`https://store.steampowered.com/search/?term=${encodeURIComponent(gameName)}`, { credentials: "omit" });
            const searchHtml = await searchRes.text();
            const searchDoc = new DOMParser().parseFromString(searchHtml, "text/html");
            const results = [...searchDoc.querySelectorAll("a.search_result_row")].map(r => ({
                appid: r.dataset.dsAppid,
                title: r.querySelector(".title")?.innerText.trim()
            }));

            if (!results.length) return await getWikipediaGameDetails(gameName);

            const normalize = str => str?.toLowerCase().replace(/[-()]/g, "").replace(/\s+/g, " ").trim();
            const match = results.find(r => normalize(r.title) === normalize(gameName));
            if (!match) return await getWikipediaGameDetails(gameName);

            const appid = match.appid;
            const apiRes = await fetch(`https://store.steampowered.com/api/appdetails?appids=${appid}`);
            const apiData = await apiRes.json();
            const info = apiData[appid]?.data;

            if (info) {
                const platformsStr = info.platforms ? Object.entries(info.platforms).filter(([k,v]) => v).map(([k]) => k).join(", ") : null;
                const gameData = {
                    appid,
                    about_the_game: info.short_description || null,
                    developer: info.developers?.join(", ") || null,
                    publisher: info.publishers?.join(", ") || null,
                    release_date: info.release_date?.date || null,
                    genres: info.genres?.map(g => g.description).join(", ") || null,
                    platforms: platformsStr,
                    metacritic_score: info.metacritic?.score || null,
                    metacritic_url: info.metacritic?.url || null,
                    image_url: info.screenshots?.[0]?.path_full || null,
                    discounted_price: info.price_overview?.discount_percent > 0 ? info.price_overview.final_formatted : null,
                    discount_percent: info.price_overview?.discount_percent > 0 ? info.price_overview.discount_percent : null,
                    current_players: await getSteamPlayerCount(appid)
                };
                gameCache[gameName] = gameData;
                return gameData;
            }
            return await getWikipediaGameDetails(gameName);
        } catch {
            return await getWikipediaGameDetails(gameName);
        }
    }

    async function getWikipediaGameDetails(gameName) {
        if (gameCache[gameName]) return gameCache[gameName];
        try {
            let gameTitle = gameName.replace(/\s+/g, "_");
            let res = await fetch(`https://en.wikipedia.org/api/rest_v1/page/summary/${encodeURIComponent(gameTitle)}`);
            if (!res.ok) {
                const searchRes = await fetch(`https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch=${encodeURIComponent(gameName)}&format=json&origin=*`);
                const searchData = await searchRes.json();
                if (!searchData.query.search.length) return null;
                gameTitle = searchData.query.search[0].title.replace(/\s+/g, "_");
                res = await fetch(`https://en.wikipedia.org/api/rest_v1/page/summary/${encodeURIComponent(gameTitle)}`);
                if (!res.ok) return null;
            }
            const data = await res.json();
            const sentences = data.extract?.match(/[^.!?]+[.!?]+/g) || [];
            const game = {
                appid: null,
                displayTitle: data.displaytitle?.replace(/<[^>]+>/g, "").replace(/\//g, "").trim(),
                about_the_game: sentences.slice(0, 2).join(" ").trim() || data.extract || null,
                developer: null,
                publisher: null,
                release_date: null,
                genres: null,
                platforms: null,
                metacritic_score: null,
                metacritic_url: null,
                image_url: data.originalimage?.source || null
            };

            const wikidataId = data.wikibase_item;
            if (wikidataId) {
                const wdRes = await fetch(`https://www.wikidata.org/wiki/Special:EntityData/${wikidataId}.json`);
                const wdData = await wdRes.json();
                const claims = wdData.entities[wikidataId].claims;
                const getClaimId = prop => claims?.[prop]?.[0]?.mainsnak?.datavalue?.value?.id || null;
                const getClaimTime = prop => claims?.[prop]?.[0]?.mainsnak?.datavalue?.value?.time || null;
                const getClaimIdList = prop => claims?.[prop]?.map(c => c.mainsnak.datavalue.value.id) || [];

                const developerId = getClaimId("P178");
                const publisherId = getClaimId("P123");
                const releaseTime = getClaimTime("P577");
                const genreIds = getClaimIdList("P136");
                const platformIds = getClaimIdList("P400");
                const idsToResolve = [developerId, publisherId, ...genreIds, ...platformIds].filter(Boolean);

                let labelsData = {};
                if (idsToResolve.length) {
                    const labelsRes = await fetch(`https://www.wikidata.org/w/api.php?action=wbgetentities&ids=${idsToResolve.join("|")}&props=labels&languages=en&format=json&origin=*`);
                    labelsData = (await labelsRes.json()).entities || {};
                }

                game.developer = developerId ? labelsData[developerId]?.labels?.en?.value ?? null : null;
                game.publisher = publisherId ? labelsData[publisherId]?.labels?.en?.value ?? null : null;
                game.release_date = releaseTime ? releaseTime.match(/\d{4}/)[0] : null;
                if (genreIds.length) {
                    game.genres = labelsData[genreIds[0]]?.labels?.en?.value?.replace(/\s*\(.*?\)\s*/g, "").trim() || null;
                }
                const platformsClean = platformIds.map(id => labelsData[id]?.labels?.en?.value).filter(Boolean).map(l => l.replace(/\s*\(.*?\)\s*/g, "").trim());
                game.platforms = platformsClean.length ? platformsClean.join(", ") : null;
            }
            gameCache[gameName] = game;
            return game;
        } catch {
            return null;
        }
    }

    async function hltbSearch(query) {
        const r = await fetch("https://search.tiago.zip/api", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ query, type: "web", page: 0 })
        });
        if (!r.ok) throw new Error();
        const data = await r.json();
        return data.results?.web?.results || [];
    }

    function getMainStory(result) {
        const text = [result.title || "", result.description || "", result.snippet || ""].join(" ").replace(/<[^>]*>/g, " ").replace(/\s+/g, " ").trim();
        const match = text.match(/(\d+(?:\.\d+)?[¼½¾]?)\s*Hours?\s*[.\s]*Main Story/i) || text.match(/main objectives.*?about\s+(\d+(?:\.\d+)?[¼½¾]?)\s*Hours?/i);
        return match ? `${match[1]} Hours` : null;
    }

    async function howLongToBeat(gameName) {
        if (hltbCache[gameName]) return hltbCache[gameName];
        const queries = [
            `site:howlongtobeat.com/game/ "${gameName}" "Main Story"`,
            `site:howlongtobeat.com/game/ "${gameName}"`,
            `site:howlongtobeat.com/game/ "${gameName.replace(/ - /g, ': ')}"`,
            `site:howlongtobeat.com/game/ "${gameName.split(" - ")[0]}"`
        ];
        for (const query of queries) {
            const results = await hltbSearch(query);
            for (const result of results) {
                const url = result.url || "";
                if (!/^https:\/\/howlongtobeat\.com\/game\/\d+\/?$/.test(url)) continue;
                const mainStory = getMainStory(result);
                if (mainStory) {
                    const resObj = { game: gameName, mainStory, url };
                    hltbCache[gameName] = resObj;
                    return resObj;
                }
            }
        }
        const resObj = { game: gameName, mainStory: null, url: null };
        hltbCache[gameName] = resObj;
        return resObj;
    }

    function replaceText() {
        document.querySelectorAll("div").forEach(div => {
            if (div.childNodes.length === 1 && div.firstChild.nodeType === Node.TEXT_NODE) {
                const match = div.firstChild.nodeValue.match(/Some detailed information on (.*?) is unavailable/i);
                if (!match) return;
                const gameName = match[1];

                getSteamGameDetails(gameName).then(gameData => {
                    if (!gameData) return;
                    div.textContent = '';
                    const nextDiv = div.nextElementSibling;
                    if (nextDiv) nextDiv.appendChild(div);

                    div.style.position = "relative";
                    div.style.overflow = "hidden";
                    div.style.height = "250px";
                    div.style.borderRadius = "6px";
                    div.style.fontFamily = '"Roboto", "Segoe UI", Tahoma, Geneva, Verdana, sans-serif';
                    div.style.color = "white";
                    div.style.outline = "none";
                    div.style.border = "none";

                    const img = document.createElement('img');
                    img.src = gameData.image_url || "https://images-1.gog-statics.com/6f3d015c3029fea5221ccd9802de5e2f92c6afccc0196b15540677341936a656.jpg";
                    img.alt = gameName;
                    Object.assign(img.style, { width: "100%", height: "100%", objectFit: "cover", position: "absolute", top: "0", left: "0", opacity: "0.5" });

                    const overlay = document.createElement('div');
                    Object.assign(overlay.style, {
                        position: "absolute", top: "0", left: "0", width: "100%", height: "100%",
                        padding: "10px", display: "flex", flexDirection: "column", justifyContent: "flex-start",
                        background: "linear-gradient(to bottom, rgba(0,0,0,0.3), rgba(0,0,0,0.7))"
                    });

                    const contentRow = document.createElement('div');
                    Object.assign(contentRow.style, { display: "flex", flexDirection: "row", flex: "1 1 auto" });

                    const leftColumn = document.createElement('div');
                    Object.assign(leftColumn.style, { display: "flex", flexDirection: "column", alignItems: "flex-start", marginRight: "15px", flexShrink: "0", maxWidth: "250px", overflow: "visible" });

                    let ancestor = div;
                    for (let i = 0; i < 7 && ancestor.parentElement; i++) ancestor = ancestor.parentElement;

                    let foundLauncher = null;
                    for (const child of ancestor.querySelectorAll("div, span, button, a")) {
                        let text = child.textContent?.trim();
                        if (!text || text.length >= 50) continue;
                        text = text.replace(/^Found in these collections/i, "").replace(/\s*\(.*?\)/g, "").trim();
                        if (text) { foundLauncher = text; break; }
                    }

                    const launcherIcons = {
                        "Epic Games": { icon: "https://cdn2.steamgriddb.com/icon/34ffeb359a192eb8174b6854643cc046/32/96x96.png", getUrl: name => `https://store.epicgames.com/browse?q=${encodeURIComponent(name.trim())}&sortBy=relevancy&sortDir=DESC&count=40` },
                        "GOG Galaxy": { icon: "https://cdn2.steamgriddb.com/icon/a928731e103dfc64c0027fa84709689e/32/96x96.png", getUrl: name => `https://www.gog.com/en/game/${name.toLowerCase().replace(/[^a-z0-9 ]/g, "").trim().replace(/\s+/g, "_")}` },
                        "Ubisoft Connect": { icon: "https://cdn2.steamgriddb.com/icon/dabcff9ba10224b01fd2ce83f7d73ad6/32/96x96.png", getUrl: name => `https://www.ubisoft.com/en-us/search?gss-q=${encodeURIComponent(name.trim())}` },
                        "EA App": { icon: "https://cdn2.steamgriddb.com/icon/ff51fb7a9bcb22c595616b4fa368880a/32/96x96.png" },
                        "Amazon Games": "https://cdn2.steamgriddb.com/icon_thumb/6e88ec1459f337d5bea6353f8bff8026.png",
                        "itch.io": "https://cdn2.steamgriddb.com/icon/2ad9e5e943e43cad612a7996c12a8796/32/96x96.png",
                        "Battle.net": "https://cdn2.steamgriddb.com/icon/739465804a0e17d2a47c9bc9c805d60a/32/96x96.png",
                        "Legacy Games": "https://cdn2.steamgriddb.com/icon_thumb/5225802cb9758f9fcd34a679bf9326ec.png",
                        "VK Play": "https://cdn2.steamgriddb.com/icon_thumb/5d35998237b55b8778a75732afc080aa.png",
                        "HoYoPlay": "https://cdn2.steamgriddb.com/icon/817fccd834f01fb5e1770c8679c0824e/32/256x256.png",
                        "Game Jolt Client": "https://cdn2.steamgriddb.com/icon_thumb/17df67628bb89193838f83015a3e7d30.png",
                        "Minecraft Launcher": "https://cdn2.steamgriddb.com/icon/0678c572b0d5597d2d4a6b5bd135754c/32/96x96.png",
                        "Humble Games Collection": "https://cdn2.steamgriddb.com/icon_thumb/3126ed973cbecde2bbffe419f139f456.png",
                        "NVIDIA GeForce NOW": "https://cdn2.steamgriddb.com/icon_thumb/f91ee142269ec908c23e1cd87286e254.png",
                        "Amazon Luna": "https://cdn2.steamgriddb.com/icon/408cebdf5e2849adedc881583586e74d/32/256x256.png",
                        "Xbox Game Pass": "https://cdn2.steamgriddb.com/icon_thumb/ecc6d2386883febda6306bb70216c846.png",
                        "Boosteroid Cloud Gaming": "https://cdn2.steamgriddb.com/icon_thumb/e3998932e2e851de8a24b733628c29de.png",
                        "Waydroid": "https://cdn2.steamgriddb.com/icon_thumb/d6de4f0418bf4015017f5c65cdecc46e.png",
                        "Google Chrome": "https://cdn2.steamgriddb.com/icon/3941c4358616274ac2436eacf67fae05/32/256x256.png",
                        "Brave": "https://cdn2.steamgriddb.com/icon_thumb/192d80a88b27b3e4115e1a45a782fe1b.png",
                        "Vivaldi": "https://cdn2.steamgriddb.com/icon_thumb/51934729f32d36841a17e43e9390483a.png",
                        "Mozilla Firefox": "https://cdn2.steamgriddb.com/icon_thumb/fe998b49c41c4208c968bce204fa1cbb.png",
                        "LibreWolf": "https://cdn2.steamgriddb.com/icon/791608b685d1c61fb2fe8acdc69dc6b5/32/128x128.png",
                        "Microsoft Edge": "https://cdn2.steamgriddb.com/icon_thumb/714cb7478d98b1cb51d1f5f515f060c7.png",
                        "Gryphlink": "https://i.namu.wiki/i/1CZOhlpjxh3owDKXC9axrnMHtotdDaoFMmnzBvQ0yOqCDOL3rIZpH2DyLfX2UCRul9CxIH0gCn1DmRodHnKr6-IUmEzSZpZ6p4r9zRbDvwPe94gZnek0VaIvKfsWsx6L28czwaiz0Mj1NNayAkypNQ.webp",
                        "WebRcade": "https://cdn2.steamgriddb.com/icon_thumb/4916ba26c0ec4e43588dcc3e019ede51.png",
                        "Nintendo": "https://cdn2.steamgriddb.com/icon_thumb/17b6114b9a9b8d8602ec9d9dfeb6a15f.png",
                        "Super Nintendo": "https://cdn2.steamgriddb.com/icon_thumb/d4dcf709a96dca127d0429d73c443afb.png",
                        "Nintendo 64": "https://cdn2.steamgriddb.com/icon_thumb/328de839e30893a67fc55ee2bf2ff5ae.png",
                        "Nintendo GameCube": "https://cdn2.steamgriddb.com/icon/3caf2d9b17ad63105399b122e2061eb1/32/256x256.png",
                        "Nintendo Wii": "https://cdn2.steamgriddb.com/icon_thumb/4c220c393016798aed81f9350e68f61c.png",
                        "Nintendo Wii U": "https://cdn2.steamgriddb.com/icon_thumb/c6c02ef92aa0dcb6c333a27cfb22d47c.png",
                        "Nintendo Switch": "https://cdn2.steamgriddb.com/icon_thumb/3b05af2c48dbaf6656fdf2d2f905b3b6.png",
                        "PlayStation": "https://cdn2.steamgriddb.com/icon_thumb/f6a81f703854985705a0cc479d221282.png",
                        "PlayStation 2": "https://cdn2.steamgriddb.com/icon/5e3600417e9ac9abf5a6fea026f9b05a/32/256x256.png",
                        "NonSteamLaunchers": "https://raw.githubusercontent.com/moraroy/NonSteamLaunchers-On-Steam-Deck/refs/heads/main/logo.png"
                    };

                    const aliasGroups = {
                        "Super Nintendo": ["SNES", "Super NES", "SuperNintendo", "Super Nintendo Entertainment System"],
                        "Nintendo 64": ["N64", "Nintendo64"],
                        "Epic Games": ["Epic Game Store", "Epic Store", "EGS"],
                        "PlayStation": ["PS", "PS1", "Sony PlayStation", "PSX", "PS one", "PSOne", "playstation"],
                        "Nintendo GameCube": ["GC", "NGC", "Gamecube", "NintendoGameCube"],
                        "Nintendo Wii": ["Wii", "NintendoWii", "RVL"],
                        "Nintendo Wii U": ["WiiU", "NintendoWiiU", "Wii U", "Cafe"],
                        "Nintendo Switch": ["Switch", "NintendoSwitch", "NS", "NSW", "HAC"],
                        "NVIDIA GeForce NOW": ["GeForce NOW", "Geforce Now"],
                        "Xbox Game Pass": ["Xbox Game Streaming", "Xbox", "Xbox Cloud Gaming", "Microsoft Xbox"],
                        "Boosteroid Cloud Gaming": ["Boosteroid"]
                    };

                    const launcherAliases = {};
                    for (const [canonical, aliases] of Object.entries(aliasGroups)) {
                        for (const alias of aliases) launcherAliases[alias.trim().toLowerCase()] = canonical;
                        launcherAliases[canonical.trim().toLowerCase()] = canonical;
                    }
                    if (foundLauncher?.includes("NonSteamLaunchers")) foundLauncher = "NonSteamLaunchers";
                    const launcherName = foundLauncher;
                    const resolvedLauncher = launcherName ? (launcherAliases[launcherName.trim().toLowerCase()] || launcherName) : null;
                    const launcherIcon = resolvedLauncher ? launcherIcons[resolvedLauncher] : null;

                    const launcherRow = document.createElement('div');
                    Object.assign(launcherRow.style, { display: "flex", alignItems: "center", gap: "8px", marginBottom: "8px", position: "relative" });

                    if (launcherIcon) {
                        const launcherLink = document.createElement('a');
                        if (typeof launcherIcon !== "string" && launcherIcon.getUrl) {
                            launcherLink.href = launcherIcon.getUrl(gameName);
                            launcherLink.target = "_blank";
                        }
                        Object.assign(launcherLink.style, { display: "inline-flex", alignItems: "center", justifyContent: "center", borderRadius: "10px", transition: "transform 0.15s ease", cursor: "pointer" });
                        launcherLink.onmouseover = () => launcherLink.style.transform = "scale(1.06)";
                        launcherLink.onmouseout = () => launcherLink.style.transform = "scale(1)";

                        const icon = document.createElement('img');
                        icon.src = typeof launcherIcon === "string" ? launcherIcon : launcherIcon.icon;
                        icon.alt = launcherName;
                        Object.assign(icon.style, { width: "60px", height: "60px", objectFit: "contain" });
                        icon.onerror = () => launcherLink.remove();

                        launcherLink.appendChild(icon);
                        launcherRow.appendChild(launcherLink);
                    } else {
                        const blankIcon = document.createElement('div');
                        Object.assign(blankIcon.style, { width: "60px", height: "60px", flexShrink: "0" });
                        launcherRow.appendChild(blankIcon);
                    }

                    leftColumn.appendChild(launcherRow);

                    function createTag(text, fontSize) {
                        const tag = document.createElement('span');
                        tag.textContent = text;
                        Object.assign(tag.style, { fontSize, background: "rgba(36,40,47,0.7)", padding: "3px 8px", borderRadius: "12px", whiteSpace: "normal", display: "inline-block", wordBreak: "break-word", marginRight: "4px", marginBottom: "4px" });
                        return tag;
                    }

                    function createTagRow(items) {
                        const row = document.createElement('div');
                        Object.assign(row.style, { display: "flex", flexWrap: "wrap", gap: "4px" });
                        const fontSize = items.length > 3 ? "7.8px" : "12px";
                        items.forEach(item => row.appendChild(createTag(item, fontSize)));
                        return row;
                    }

                    if (gameData.platforms) leftColumn.appendChild(createTagRow(gameData.platforms.split(",").map(p => p.trim())));
                    if (gameData.developer) leftColumn.appendChild(createTagRow(gameData.developer.split(",").map(d => d.trim())));
                    if (gameData.publisher) leftColumn.appendChild(createTagRow(gameData.publisher.split(",").map(p => p.trim())));
                    if (gameData.release_date) leftColumn.appendChild(createTagRow([gameData.release_date]));
                    if (gameData.genres) leftColumn.appendChild(createTagRow(gameData.genres.split(",").map(g => g.trim())));

                    const rightColumn = document.createElement('div');
                    Object.assign(rightColumn.style, { display: "flex", flexDirection: "column", flex: "1" });

                    const descriptionWrapper = document.createElement('div');
                    Object.assign(descriptionWrapper.style, { position: "relative", width: "100%" });

                    const description = document.createElement('p');
                    description.textContent = gameData.about_the_game || "No description available.";
                    Object.assign(description.style, { fontSize: "14px", lineHeight: "1.4", background: "rgba(36,40,47,0.7)", padding: "8px 12px", borderRadius: "12px", wordBreak: "break-word", overflowWrap: "break-word" });
                    descriptionWrapper.appendChild(description);

                    if (gameData.metacritic_score && gameData.metacritic_url) {
                        const metaTab = document.createElement('a');
                        metaTab.href = gameData.metacritic_url;
                        metaTab.target = "_blank";
                        Object.assign(metaTab.style, {
                            position: "absolute", top: "14px", left: "-18px", display: "flex", flexDirection: "column",
                            alignItems: "center", justifyContent: "center", background: "rgba(36,40,47,0.85)", color: "white",
                            fontSize: "12px", padding: "4px 6px", borderRadius: "8px", textDecoration: "none", cursor: "pointer",
                            boxShadow: "0 2px 6px rgba(0,0,0,0.3)", zIndex: "10"
                        });
                        metaTab.onmouseover = () => metaTab.style.background = "rgba(80,80,80,0.9)";
                        metaTab.onmouseout = () => metaTab.style.background = "rgba(36,40,47,0.85)";

                        const metaLogo = document.createElement('img');
                        metaLogo.src = "https://static.wikia.nocookie.net/logopedia/images/1/1f/Metacritic_2.svg";
                        Object.assign(metaLogo.style, { width: "16px", height: "16px", marginBottom: "2px" });

                        const scoreText = document.createElement('span');
                        scoreText.textContent = gameData.metacritic_score;
                        Object.assign(scoreText.style, { fontWeight: "bold", fontSize: "12px" });

                        const score = parseInt(gameData.metacritic_score, 10);
                        if (score >= 0 && score <= 49) scoreText.style.color = "rgb(139, 75, 90)";
                        else if (score >= 50 && score <= 79) scoreText.style.color = "rgb(166, 106, 58)";
                        else if (score >= 80) scoreText.style.color = "rgb(75, 139, 90)";

                        metaTab.appendChild(metaLogo);
                        metaTab.appendChild(scoreText);
                        descriptionWrapper.appendChild(metaTab);
                    }

                    rightColumn.appendChild(descriptionWrapper);
                    contentRow.appendChild(leftColumn);
                    contentRow.appendChild(rightColumn);
                    overlay.appendChild(contentRow);

                    const bottomLinks = document.createElement('div');
                    Object.assign(bottomLinks.style, {
                        position: "absolute", bottom: "34px", left: "42px", right: "42px",
                        display: "flex", flexWrap: "nowrap", gap: "6px", overflow: "hidden",
                        whiteSpace: "nowrap", scrollBehavior: "smooth", alignItems: "flex-end",
                        height: "42px", paddingLeft: "1px", paddingRight: "6px"
                    });

                    const searchSites = [
                        { name: "Google", url: "https://www.google.com/search?q=", icon: "https://upload.wikimedia.org/wikipedia/commons/2/2f/Google_2015_logo.svg" },
                        { name: "PCGW", url: "https://www.pcgamingwiki.com/w/index.php?search=", extra: "&title=Special%3ASearch", icon: "https://pbs.twimg.com/profile_images/876511628258418689/Joehp5YI_400x400.jpg" },
                        { name: "HLTB", url: "https://howlongtobeat.com/?q=", icon: "https://howlongtobeat.com/favicon.ico" },
                        { name: "SDHQ", url: "https://steamdeckhq.com/?s=", icon: "https://pbs.twimg.com/profile_images/1539310786614419459/5ohiy0ZX_400x400.jpg" },
                        { name: "GOS", url: "https://gamingonsteam.com/?post_type=post&s=", extra: "&btnSubmit=", icon: "https://gamingonsteam.com/wp-content/uploads/2025/12/X-BS-1-e1765643013126.png" },
                        { name: "SteamCharts", url: "https://steamcharts.com/search/?q=", icon: "https://pbs.twimg.com/profile_images/473239151924346880/5k2c-3Hv_400x400.png" },
                        { name: "ProtonDB", url: "https://www.protondb.com/search?q=", icon: "https://www.protondb.com/sites/protondb/images/site-logo.svg" },
                        { name: "SteamInputDB", url: "https://www.steaminputdb.com/config/search?searchtext=", extra: "&sort-by=vote", icon: "https://raw.githubusercontent.com/Alia5/steaminputdb.com/refs/heads/main/logo_mono.svg" },
                        { name: "AWACY", url: "https://areweanticheatyet.com/?search=", icon: "https://areweanticheatyet.com/icon.webp" },
                        { name: "GameFAQs", url: "https://gamefaqs.gamespot.com/search?game=", icon: "https://gamefaqs.gamespot.com/favicon.ico" },
                        { name: "SRC", url: "https://www.speedrun.com/search?q=", icon: "https://avatars.githubusercontent.com/u/11006616?s=200&v=4" }
                    ];

                    searchSites.forEach(site => {
                        const link = document.createElement('a');
                        let gameUrl = site.url + encodeURIComponent(gameName) + (site.extra || "");
                        if (site.name === "SRC") {
                            const slug = gameName.replace(/:/g, '').replace(/[^\w\s]/g, '').trim().replace(/\s+/g, '_');
                            gameUrl = `https://www.speedrun.com/${slug}`;
                        }
                        link.href = gameUrl;
                        link.target = "_blank";
                        Object.assign(link.style, { display: "inline-flex", alignItems: "center", background: "rgba(36,40,47,0.7)", color: "white", fontSize: "13px", padding: "4px 4px", borderRadius: "6px", textDecoration: "none", transition: "background 0.2s" });
                        link.onmouseover = () => link.style.background = "rgba(80,80,80,0.9)";
                        link.onmouseout = () => link.style.background = "rgba(36,40,47,0.7)";

                        const linkIcon = document.createElement('img');
                        linkIcon.src = site.icon;
                        Object.assign(linkIcon.style, { width: "16px", height: "16px", marginRight: "4px" });
                        link.prepend(linkIcon);
                        link.appendChild(document.createTextNode(site.name));

                        if (site.name === "HLTB") {
                            const hltbContainer = document.createElement('div');
                            Object.assign(hltbContainer.style, { position: "relative", display: "inline-flex", alignItems: "center", flexShrink: "0" });

                            const hltbLabel = document.createElement('div');
                            hltbLabel.textContent = "";
                            Object.assign(hltbLabel.style, {
                                position: "absolute", bottom: "100%", left: "50%", transform: "translateX(-50%)",
                                color: "white", fontSize: "10px", fontWeight: "600", lineHeight: "12px",
                                background: "rgba(100, 35, 45, 0.9)", padding: "2px 6px", borderRadius: "6px",
                                whiteSpace: "nowrap", textAlign: "center", boxShadow: "0 2px 4px rgba(0,0,0,0.4)"
                            });

                            hltbContainer.appendChild(hltbLabel);
                            hltbContainer.appendChild(link);
                            bottomLinks.appendChild(hltbContainer);

                            howLongToBeat(gameName).then(res => {
                                if (res?.mainStory) hltbLabel.textContent = res.mainStory;
                            }).catch(() => {});
                        } else if (site.name === "SteamCharts") {
                            const chartContainer = document.createElement('div');
                            Object.assign(chartContainer.style, { position: "relative", display: "inline-flex", alignItems: "center", flexShrink: "0" });

                            const chartLabel = document.createElement('div');
                            chartLabel.textContent = gameData.current_players != null ? "👥 Loading..." : "";
                            Object.assign(chartLabel.style, {
                                position: "absolute", bottom: "100%", left: "50%", transform: "translateX(-50%)",
                                color: "white", fontSize: "10px", fontWeight: "600", lineHeight: "12px",
                                background: "rgba(35, 120, 70, 0.9)", padding: "2px 6px", borderRadius: "6px",
                                whiteSpace: "nowrap", textAlign: "center", boxShadow: "0 2px 4px rgba(0,0,0,0.4)"
                            });

                            chartContainer.appendChild(chartLabel);
                            chartContainer.appendChild(link);
                            bottomLinks.appendChild(chartContainer);

                            if (gameData.current_players != null) {
                                let current = 0, raf;
                                const to = gameData.current_players;
                                const start = performance.now();
                                function frame(now) {
                                    const p = Math.min((now - start) / 1000, 1);
                                    current = Math.round(0 + to * (1 - Math.pow(1 - p, 3)));
                                    chartLabel.textContent = `👥 ${current.toLocaleString()} online`;
                                    if (p < 1) raf = requestAnimationFrame(frame);
                                }
                                raf = requestAnimationFrame(frame);
                            }
                        } else {
                            bottomLinks.appendChild(link);
                        }
                    });

                    if (gameData.discounted_price && gameData.discount_percent) {
                        const slug = gameName.toLowerCase().replace(/[^a-z0-9 ]/g, '').trim().replace(/\s+/g, '-');
                        const itadLink = document.createElement('a');
                        itadLink.href = `https://isthereanydeal.com/game/${slug}/info/`;
                        itadLink.target = "_blank";
                        Object.assign(itadLink.style, {
                            position: "absolute", top: "-2px", right: "12px", zIndex: "10",
                            display: "inline-flex", alignItems: "center", gap: "6px",
                            background: "rgba(36,40,47,0.7)", color: "white", fontSize: "12px",
                            padding: "6px 10px", borderRadius: "10px", textDecoration: "none",
                            width: "max-content", cursor: "pointer", transition: "background 0.2s ease"
                        });
                        itadLink.onmouseover = () => itadLink.style.background = "rgba(80,80,80,0.9)";
                        itadLink.onmouseout = () => itadLink.style.background = "rgba(36,40,47,0.7)";

                        const itadText = document.createElement('span');
                        itadText.textContent = `${gameData.discounted_price} (-${gameData.discount_percent}%)`;
                        Object.assign(itadText.style, { fontWeight: "bold", fontSize: "12px", color: "rgb(75, 139, 90)" });

                        const itadIcon = document.createElement('img');
                        itadIcon.src = "https://isthereanydeal.com/public/assets/logo-GBHE6XF2.svg";
                        Object.assign(itadIcon.style, { width: "16px", height: "16px" });

                        itadLink.appendChild(itadText);
                        itadLink.appendChild(itadIcon);
                        overlay.appendChild(itadLink);
                    }

                    const scrollAmount = 140;
                    const leftArrow = document.createElement('div');
                    leftArrow.innerHTML = "❮";
                    Object.assign(leftArrow.style, {
                        position: "absolute", left: "10px", bottom: "34px", width: "22px", height: "24px",
                        display: "flex", alignItems: "center", justifyContent: "center", cursor: "pointer",
                        color: "white", fontSize: "14px", background: "rgba(36,40,47,0.7)", borderRadius: "6px", zIndex: "10"
                    });
                    leftArrow.onmouseover = () => leftArrow.style.background = "rgba(80,80,80,0.9)";
                    leftArrow.onmouseout = () => leftArrow.style.background = "rgba(36,40,47,0.7)";
                    leftArrow.onclick = () => bottomLinks.scrollBy({ left: -scrollAmount, behavior: "smooth" });

                    const rightArrow = document.createElement('div');
                    rightArrow.innerHTML = "❯";
                    Object.assign(rightArrow.style, {
                        position: "absolute", right: "18px", bottom: "34px", width: "22px", height: "24px",
                        display: "flex", alignItems: "center", justifyContent: "center", cursor: "pointer",
                        color: "white", fontSize: "14px", background: "rgba(36,40,47,0.7)", borderRadius: "6px", zIndex: "10"
                    });
                    rightArrow.onmouseover = () => rightArrow.style.background = "rgba(80,80,80,0.9)";
                    rightArrow.onmouseout = () => rightArrow.style.background = "rgba(36,40,47,0.7)";
                    rightArrow.onclick = () => bottomLinks.scrollBy({ left: scrollAmount, behavior: "smooth" });

                    overlay.appendChild(leftArrow);
                    overlay.appendChild(rightArrow);
                    overlay.appendChild(bottomLinks);
                    div.appendChild(img);
                    div.appendChild(overlay);
                });
            }
        });
    }

    replaceText();
    if (!window.steamEnhancerObserver) {
        const observer = new MutationObserver(replaceText);
        observer.observe(document.body, { childList: true, subtree: true });
        window.steamEnhancerObserver = observer;
    }
})();
"""
### METADATA ONLY
def inject_thememusic_code(ws_socket):
    inject_id = next(eval_id_counter)

    wrapped_code = f"""
    (async () => {{
        {THEMEMUSIC_CODE}
        return 'ThemeMusic injection done';
    }})()
    """

    send_ws_text(ws_socket, json.dumps({
        "id": inject_id,
        "method": "Runtime.evaluate",
        "params": {
            "expression": wrapped_code,
            "awaitPromise": True
        }
    }))

    response = recv_ws_message_for_id(
        ws_socket,
        inject_id
    )

    print(
        "ThemeMusic injection response:",
        response
    )

    return response


def run_thememusic():
    for target in (
        TARGET_TITLE2,
        TARGET_TITLE3
    ):
        try:
            ws_url = get_ws_url_by_title(
                WS_HOST,
                WS_PORT,
                target
            )

            ws_socket = create_websocket_connection(
                ws_url
            )

            send_ws_text(ws_socket, json.dumps({
                "id": 1,
                "method": "Runtime.enable"
            }))

            recv_ws_message_for_id(ws_socket, 1)

            inject_thememusic_code(ws_socket)

        except Exception as e:
            print(
                f"ThemeMusic injection failed for "
                f"{target}: {e}"
            )


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


def run_metadata():
    for target in (
        TARGET_TITLE2,
        TARGET_TITLE3
    ):
        try:
            ws_url = get_ws_url_by_title(
                WS_HOST,
                WS_PORT,
                target
            )

            ws_socket = create_websocket_connection(
                ws_url
            )

            send_ws_text(ws_socket, json.dumps({
                "id": 1,
                "method": "Runtime.enable"
            }))

            recv_ws_message(ws_socket)

            inject_metadata_code(ws_socket)

        except Exception as e:
            print(
                f"Metadata injection failed for "
                f"{target}: {e}"
            )


def start():

    run_thememusic()
    run_metadata()
