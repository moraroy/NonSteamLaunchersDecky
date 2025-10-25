import { useEffect } from "react";

const STORAGE_KEY = "realPlaytimeData_Debug";

interface PlaytimeDataEntry {
  total: number;
  lastSessionEnd: number;
  missingCount?: number; // for safer cleanup handling
}

// ------------------------------
// Validation + Sanitization
// ------------------------------
function isValidPlaytimeDataEntry(entry: any): entry is PlaytimeDataEntry {
  return (
    typeof entry === "object" &&
    entry !== null &&
    typeof entry.total === "number" &&
    typeof entry.lastSessionEnd === "number"
  );
}

function sanitizePlaytimeData(data: any): Record<string, PlaytimeDataEntry> {
  if (typeof data !== "object" || data === null) return {};
  const cleaned: Record<string, PlaytimeDataEntry> = {};
  for (const [key, value] of Object.entries(data)) {
    if (isValidPlaytimeDataEntry(value)) {
      cleaned[key] = value;
    }
  }
  return cleaned;
}

// ------------------------------
// Local Storage I/O
// ------------------------------
function loadPlaytimeData(): Record<string, PlaytimeDataEntry> {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return {};
    const parsed = JSON.parse(raw);
    return sanitizePlaytimeData(parsed);
  } catch (err) {
    console.warn("[Playtime] Failed to load:", err);
    return {};
  }
}

// ------------------------------
// In-memory Cache System
// ------------------------------
let cachedPlaytimeData: Record<string, PlaytimeDataEntry> | null = null;
let saveTimeout: ReturnType<typeof setTimeout> | null = null;

function getPlaytimeData(): Record<string, PlaytimeDataEntry> {
  if (!cachedPlaytimeData) {
    cachedPlaytimeData = loadPlaytimeData();
  }
  return cachedPlaytimeData;
}

function scheduleSave() {
  if (saveTimeout) clearTimeout(saveTimeout);
  saveTimeout = setTimeout(() => {
    if (cachedPlaytimeData) {
      try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(cachedPlaytimeData));
        console.debug("[Playtime] Saved data to localStorage");
      } catch (err) {
        console.warn("[Playtime] Failed to save:", err);
      }
    }
  }, 1000); // Save at most once per second
}

// ------------------------------
// Environment Safety Checks
// ------------------------------
function isEnvironmentReady() {
  try {
    localStorage.setItem("__rp_test__", "1");
    localStorage.removeItem("__rp_test__");
    if (!window.appStore || typeof window.appStore.GetAppOverviewByAppID !== "function") return false;
    if (!window.appInfoStore) return false;
    return true;
  } catch {
    return false;
  }
}

// ------------------------------
// Core Logic
// ------------------------------
function restoreSavedPlaytimes() {
  const data = getPlaytimeData();
  if (!window.appStore?.GetAppOverviewByAppID) return;

  let modified = false;

  for (const [id, entry] of Object.entries(data)) {
    const ov = appStore.GetAppOverviewByAppID(Number(id));
    if (ov) {
      ov.minutes_playtime_forever = entry.total;
      ov.minutes_playtime_last_two_weeks = entry.total;
      ov.nPlaytimeForever = entry.total;
      if (typeof ov.TriggerChange === "function") {
        ov.TriggerChange();
      }
      if (entry.missingCount) delete entry.missingCount;
    } else {
      entry.missingCount = (entry.missingCount || 0) + 1;
      // Only delete if missing for 5+ restores
      if (entry.missingCount > 5) {
        delete data[id];
        modified = true;
      }
    }
  }

  if (modified) scheduleSave();
}

function applyRealSessionToOverview(appOverview: any): boolean {
  try {
    if (!appOverview || appOverview.app_type !== 1073741824) return false;

    const start = appOverview.rt_last_time_played;
    const end = appOverview.rt_last_time_locally_played;

    if (!start || !end || end <= start) return false;

    const sessionSeconds = end - start;
    const sessionMinutes = Math.floor(sessionSeconds / 60);
    if (sessionMinutes <= 0) return false;

    const data = getPlaytimeData();
    const appId = String(appOverview.appid || appOverview.appid?.() || appOverview.appId);
    const prevEntry = data[appId] || { total: 0, lastSessionEnd: 0 };

    // Prevent double-counting sessions
    if (end <= prevEntry.lastSessionEnd) return false;

    const newTotal = prevEntry.total + sessionMinutes;
    data[appId] = { total: newTotal, lastSessionEnd: end };

    appOverview.minutes_playtime_forever = newTotal;
    appOverview.minutes_playtime_last_two_weeks = newTotal;
    appOverview.nPlaytimeForever = newTotal;

    if (typeof appOverview.TriggerChange === "function") {
      appOverview.TriggerChange();
    }

    scheduleSave();
    return true;
  } catch (err) {
    console.warn("[Playtime] applyRealSessionToOverview error:", err);
    return false;
  }
}

// ------------------------------
// Patches
// ------------------------------
function patchAppStore() {
  if (!window.appStore?.m_mapApps) return;
  if (appStore.m_mapApps._originalSet) return;

  appStore.m_mapApps._originalSet = appStore.m_mapApps.set;
  appStore.m_mapApps.set = function (appId, appOverview) {
    const result = appStore.m_mapApps._originalSet.call(this, appId, appOverview);
    applyRealSessionToOverview(appOverview);
    return result;
  };
}

function patchAppInfoStore() {
  if (!window.appInfoStore) return;
  if (appInfoStore._originalOnAppOverviewChange) return;

  appInfoStore._originalOnAppOverviewChange = appInfoStore.OnAppOverviewChange;
  appInfoStore.OnAppOverviewChange = function (apps) {
    for (const a of apps || []) {
      const id = typeof a?.appid === "function" ? a.appid() : a?.appid;
      const overview = id && appStore?.GetAppOverviewByAppID
        ? appStore.GetAppOverviewByAppID(Number(id))
        : a;
      if (overview) applyRealSessionToOverview(overview);
    }
    return appInfoStore._originalOnAppOverviewChange.call(this, apps);
  };
}

function manualPatch() {
  try {
    const m = location.pathname.match(/\/library\/app\/(\d+)/);
    if (m) {
      const id = Number(m[1]);
      const ov = appStore.GetAppOverviewByAppID(id);
      if (ov) {
        applyRealSessionToOverview(ov);
        appInfoStore?.OnAppOverviewChange?.([ov]);
      }
    }
  } catch (err) {
    console.warn("[Playtime] manualPatch error:", err);
  }
}

// ------------------------------
// Initialization
// ------------------------------
export function initRealPlaytime(retryCount = 0) {
  if (!isEnvironmentReady()) {
    if (retryCount < 100) {
      setTimeout(() => initRealPlaytime(retryCount + 1), 1000);
    }
    return;
  }

  try {
    restoreSavedPlaytimes();
    patchAppStore();
    patchAppInfoStore();
    manualPatch();

    console.log("[Playtime] RealPlaytime initialized");
  } catch (err) {
    console.warn("[Playtime] Initialization failed:", err);
  }
}

