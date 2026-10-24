import { useEffect } from "react";

interface PlaytimeCacheEntry {
  forever: number;
  twoWeeks: number;
  lastPlayed: number;
}

const pending = new Set<number>();
const playtimeCache = new Map<number, PlaytimeCacheEntry>();
const runningStates = new Map<number, boolean>();
let playtimeEnabled = true;

try {
  if (localStorage.getItem("realPlaytimeData") !== null) {
    localStorage.removeItem("realPlaytimeData");
    console.log("Removed deprecated 'realPlaytimeData' from localStorage.");
  }
} catch {}

async function fetchAndCachePlaytime(appId: number) {
  if (pending.has(appId)) return;
  pending.add(appId);
  try {
    const steamClient = (window as any).SteamClient;
    const playtime = await steamClient?.Apps?.GetPlaytime?.(appId);
    if (playtime) {
      playtimeCache.set(appId, {
        forever: Number(playtime.nPlaytimeForever) || 0,
        twoWeeks: Number(playtime.nPlaytimeLastTwoWeeks) || 0,
        lastPlayed: Number(playtime.rtLastTimePlayed) || 0,
      });
    }
  } catch (err) {
    console.warn("Steam playtime fetch failed:", err);
  } finally {
    pending.delete(appId);
  }
}

function applyPlaytime(appOverview: any) {
  if (!playtimeEnabled || !appOverview || appOverview.app_type !== 1073741824) return;

  const rawId = typeof appOverview.appid === "function"
    ? appOverview.appid()
    : appOverview.appid ?? appOverview.appId;

  const appId = Number(rawId);
  if (!Number.isFinite(appId) || appId <= 0) return;

  const isRunning = !!appOverview.bIsRunning;
  const wasRunning = runningStates.get(appId) || false;

  if (wasRunning && !isRunning) {
    playtimeCache.delete(appId);
  }
  runningStates.set(appId, isRunning);

  if (!playtimeCache.has(appId)) {
    fetchAndCachePlaytime(appId).then(() => {
      appOverview.TriggerChange?.();
    });
  }

  const cached = playtimeCache.get(appId);
  if (cached) {
    appOverview.minutes_playtime_forever = cached.forever;
    appOverview.nPlaytimeForever = cached.forever;

    appOverview.minutes_playtime_last_two_weeks = cached.twoWeeks;
    appOverview.nPlaytimeLastTwoWeeks = cached.twoWeeks;

    if (cached.lastPlayed > 0) {
      appOverview.rt_last_time_played = cached.lastPlayed;
    }

    appOverview.TriggerChange?.();
  }
}

function patchAppStore() {
  const store = (window as any).appStore;
  if (!store) return;

  if (typeof store.GetAppOverviewByAppID === "function" && !store._originalGetAppOverviewByAppID) {
    store._originalGetAppOverviewByAppID = store.GetAppOverviewByAppID;
    store.GetAppOverviewByAppID = function (appId: number) {
      const overview = store._originalGetAppOverviewByAppID.call(this, appId);
      applyPlaytime(overview);
      return overview;
    };
  }

  if (store.m_mapApps && !store.m_mapApps._originalSet) {
    store.m_mapApps._originalSet = store.m_mapApps.set;
    store.m_mapApps.set = function (appId: any, overview: any) {
      applyPlaytime(overview);
      return store.m_mapApps._originalSet.call(this, appId, overview);
    };
  }
}

function unpatchAppStore() {
  const store = (window as any).appStore;
  if (!store) return;

  if (store._originalGetAppOverviewByAppID) {
    store.GetAppOverviewByAppID = store._originalGetAppOverviewByAppID;
    delete store._originalGetAppOverviewByAppID;
  }

  if (store.m_mapApps?._originalSet) {
    store.m_mapApps.set = store.m_mapApps._originalSet;
    delete store.m_mapApps._originalSet;
  }
}

function patchAppInfoStore() {
  const info = (window as any).appInfoStore;
  if (!info || typeof info.OnAppOverviewChange !== "function" || info._originalOnAppOverviewChange) return;

  info._originalOnAppOverviewChange = info.OnAppOverviewChange;
  info.OnAppOverviewChange = function (apps: any[]) {
    for (const app of apps || []) {
      const rawId = typeof app?.appid === "function" ? app.appid() : app?.appid;
      const overview = rawId != null
        ? (window as any).appStore?.GetAppOverviewByAppID?.(Number(rawId)) || app
        : app;
      applyPlaytime(overview);
    }
    return info._originalOnAppOverviewChange.apply(this, arguments as any);
  };
}

function unpatchAppInfoStore() {
  const info = (window as any).appInfoStore;
  if (info?._originalOnAppOverviewChange) {
    info.OnAppOverviewChange = info._originalOnAppOverviewChange;
    delete info._originalOnAppOverviewChange;
  }
}

function isEnvironmentReady() {
  try {
    if (!(window as any).appStore || typeof (window as any).appStore.GetAppOverviewByAppID !== "function") return false;
    if (!(window as any).appInfoStore) return false;
    if (!(window as any).SteamClient?.Apps?.GetPlaytime) return false;
    return true;
  } catch {
    return false;
  }
}

export function setPlaytimeEnabled(enabled: boolean) {
  playtimeEnabled = enabled;
  if (!enabled) {
    unpatchAppStore();
    unpatchAppInfoStore();
  } else {
    patchAppStore();
    patchAppInfoStore();
    if ((window as any).appStore?.m_mapApps) {
      for (const overview of (window as any).appStore.m_mapApps.values()) {
        applyPlaytime(overview);
      }
    }
  }
}

export function initRealPlaytime(enabled = true, retryCount = 0) {
  setPlaytimeEnabled(enabled);

  if (!isEnvironmentReady()) {
    if (retryCount < 100) {
      setTimeout(() => initRealPlaytime(enabled, retryCount + 1), 1000);
    }
    return;
  }

  try {
    setTimeout(() => {
      patchAppStore();
      patchAppInfoStore();
      if ((window as any).appStore?.m_mapApps) {
        for (const overview of (window as any).appStore.m_mapApps.values()) {
          applyPlaytime(overview);
        }
      }
    }, 100);
  } catch {}
}