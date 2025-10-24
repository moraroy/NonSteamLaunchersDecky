import { useEffect } from "react";

const STORAGE_KEY = "realPlaytimeData_Debug";

// ---- Utility for timestamped logging ----
function log(...args: any[]) {
  const time = new Date().toISOString().split("T")[1].split("Z")[0];
  console.log(`[${time}]`, ...args);
}

interface PlaytimeDataEntry {
  total: number;
  lastSessionEnd: number;
}

// ---- Validation helpers ----
function isValidPlaytimeDataEntry(entry: any): entry is PlaytimeDataEntry {
  const valid =
    typeof entry === "object" &&
    entry !== null &&
    typeof entry.total === "number" &&
    typeof entry.lastSessionEnd === "number";
  if (!valid) log("[validate] Invalid entry detected:", entry);
  return valid;
}

function sanitizePlaytimeData(data: any): Record<string, PlaytimeDataEntry> {
  if (typeof data !== "object" || data === null) return {};
  const cleaned: Record<string, PlaytimeDataEntry> = {};
  for (const [key, value] of Object.entries(data)) {
    if (isValidPlaytimeDataEntry(value)) {
      cleaned[key] = value;
    } else {
      log(`[sanitize] Removed invalid data for app ${key}`);
    }
  }
  return cleaned;
}

// ---- Local storage handling ----
function loadPlaytimeData(): Record<string, PlaytimeDataEntry> {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) {
      log("[load] No stored data found.");
      return {};
    }

    const parsed = JSON.parse(raw);
    const cleaned = sanitizePlaytimeData(parsed);

    if (Object.keys(cleaned).length !== Object.keys(parsed || {}).length) {
      log("[load] Some data repaired. Updating storage...");
      savePlaytimeData(cleaned);
    }

    log("[load] Loaded playtime data:", cleaned);
    return cleaned;
  } catch (err) {
    log("[load] Failed to parse localStorage:", err);
    return {};
  }
}

function savePlaytimeData(data: Record<string, PlaytimeDataEntry>) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
  log("[save] Data persisted to localStorage:", data);
}

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

/**
 * Restore saved playtime totals into the current appOverview objects.
 */
function restoreSavedPlaytimes() {
  const data = loadPlaytimeData();
  if (!window.appStore?.GetAppOverviewByAppID) return;

  let removedCount = 0;

  for (const [id, entry] of Object.entries(data)) {
    const ov = appStore.GetAppOverviewByAppID(Number(id));
    if (ov) {
      log(`[restore] Applying totals to ${ov.display_name || id}: ${entry.total} min`);
      ov.minutes_playtime_forever = entry.total;
      ov.minutes_playtime_last_two_weeks = entry.total;
      ov.nPlaytimeForever = entry.total;
      if (typeof ov.TriggerChange === "function") {
        ov.TriggerChange();
        log(`[UI] TriggerChange() fired for ${ov.display_name || id}`);
      }
    } else {
      delete data[id];
      removedCount++;
      log(`[restore] Removed stale app ${id}`);
    }
  }

  if (removedCount > 0) {
    savePlaytimeData(data);
  }

  log("[restore] Completed restore for", Object.keys(data).length, "apps");
}

/**
 * Add real session time to the saved totals.
 */
function applyRealSessionToOverview(appOverview: any): boolean {
  try {
    if (!appOverview || appOverview.app_type !== 1073741824) return false;

    const start = appOverview.rt_last_time_played;
    const end = appOverview.rt_last_time_locally_played;
    log(`[session] Checking ${appOverview.display_name || "Unknown"}: start=${start}, end=${end}`);

    if (!start || !end || end <= start) return false;

    const sessionSeconds = end - start;
    const sessionMinutes = Math.floor(sessionSeconds / 60);
    if (sessionMinutes <= 0) return false;

    const data = loadPlaytimeData();
    const appId = String(appOverview.appid || appOverview.appid?.() || appOverview.appId);
    const prevEntry = data[appId] || { total: 0, lastSessionEnd: 0 };

    if (end <= prevEntry.lastSessionEnd) {
      log(`[session] Ignored duplicate session for ${appId}`);
      return false;
    }

    const newTotal = prevEntry.total + sessionMinutes;
    data[appId] = { total: newTotal, lastSessionEnd: end };
    savePlaytimeData(data);

    appOverview.minutes_playtime_forever = newTotal;
    appOverview.minutes_playtime_last_two_weeks = newTotal;
    appOverview.nPlaytimeForever = newTotal;
    if (typeof appOverview.TriggerChange === "function") {
      appOverview.TriggerChange();
      log(`[UI] TriggerChange() fired for ${appOverview.display_name || appId}`);
    }

    log(`[RealPlaytime] +${sessionMinutes} min → ${appOverview.display_name || "Unknown"} (${appId}). Total = ${newTotal}`);
    return true;
  } catch (e) {
    log("[session] Error applying session:", e);
    return false;
  }
}

/**
 * Patch appStore
 */
function patchAppStore() {
  if (!window.appStore?.m_mapApps) return;
  if (appStore.m_mapApps._originalSet) return;

  appStore.m_mapApps._originalSet = appStore.m_mapApps.set;
  appStore.m_mapApps.set = function (appId, appOverview) {
    log(`[patchAppStore] Intercepted appStore.set(${appId})`);
    const result = appStore.m_mapApps._originalSet.call(this, appId, appOverview);
    restoreSavedPlaytimes();
    applyRealSessionToOverview(appOverview);
    return result;
  };

  log("[patchAppStore] Hooked appStore.m_mapApps.set()");
}

/**
 * Patch appInfoStore
 */
function patchAppInfoStore() {
  if (!window.appInfoStore) return;
  if (appInfoStore._originalOnAppOverviewChange) return;

  appInfoStore._originalOnAppOverviewChange = appInfoStore.OnAppOverviewChange;
  appInfoStore.OnAppOverviewChange = function (apps) {
    log(`[patchInfoStore] OnAppOverviewChange triggered with ${apps?.length || 0} apps`);
    for (const a of apps || []) {
      const id = typeof a?.appid === "function" ? a.appid() : a?.appid;
      const overview = id && appStore?.GetAppOverviewByAppID
        ? appStore.GetAppOverviewByAppID(Number(id))
        : a;
      if (overview) {
        restoreSavedPlaytimes();
        applyRealSessionToOverview(overview);
      }
    }
    return appInfoStore._originalOnAppOverviewChange.call(this, apps);
  };

  log("[patchInfoStore] Hooked appInfoStore.OnAppOverviewChange()");
}

/**
 * Manual patch for current game page
 */
function manualPatch() {
  try {
    const m = location.pathname.match(/\/library\/app\/(\d+)/);
    if (m) {
      const id = Number(m[1]);
      const ov = appStore.GetAppOverviewByAppID(id);
      if (ov) {
        log(`[manualPatch] Running manual patch for app ${id}`);
        restoreSavedPlaytimes();
        applyRealSessionToOverview(ov);
        appInfoStore?.OnAppOverviewChange?.([ov]);
      }
    }
  } catch (e) {
    log("[manualPatch] Error:", e);
  }
}

/**
 * Initialize
 */
export function initRealPlaytime(retryCount = 0) {
  if (!isEnvironmentReady()) {
    if (retryCount < 100) {
      log(`[init] Environment not ready (attempt ${retryCount + 1}), retrying...`);
      setTimeout(() => initRealPlaytime(retryCount + 1), 1000);
    } else {
      log("[init] Gave up waiting for environment.");
    }
    return;
  }

  try {
    log("[init] Environment ready, applying patches...");
    restoreSavedPlaytimes();
    patchAppStore();
    patchAppInfoStore();
    manualPatch();
    log("[init] ✅ RealPlaytime (Playtime Launch 2) fully initialized.");
  } catch (err) {
    log("[init] Failed to initialize:", err);
  }
}
