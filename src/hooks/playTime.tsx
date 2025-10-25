import { useEffect } from "react";

const STORAGE_KEY = "realPlaytimeData_Debug";

interface PlaytimeDataEntry {
  total: number;
  lastSessionEnd: number;
}

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

function loadPlaytimeData(): Record<string, PlaytimeDataEntry> {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return {};

    const parsed = JSON.parse(raw);
    const cleaned = sanitizePlaytimeData(parsed);

    if (Object.keys(cleaned).length !== Object.keys(parsed || {}).length) {
      savePlaytimeData(cleaned);
    }

    return cleaned;
  } catch {
    return {};
  }
}

function savePlaytimeData(data: Record<string, PlaytimeDataEntry>) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
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

function restoreSavedPlaytimes() {
  const data = loadPlaytimeData();
  if (!window.appStore?.GetAppOverviewByAppID) return;

  let removedCount = 0;

  for (const [id, entry] of Object.entries(data)) {
    const ov = appStore.GetAppOverviewByAppID(Number(id));
    if (ov) {
      ov.minutes_playtime_forever = entry.total;
      ov.minutes_playtime_last_two_weeks = entry.total;
      ov.nPlaytimeForever = entry.total;
      if (typeof ov.TriggerChange === "function") {
        ov.TriggerChange();
      }
    } else {
      delete data[id];
      removedCount++;
    }
  }

  if (removedCount > 0) {
    savePlaytimeData(data);
  }
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

    const data = loadPlaytimeData();
    const appId = String(appOverview.appid || appOverview.appid?.() || appOverview.appId);
    const prevEntry = data[appId] || { total: 0, lastSessionEnd: 0 };

    if (end <= prevEntry.lastSessionEnd) return false;

    const newTotal = prevEntry.total + sessionMinutes;
    data[appId] = { total: newTotal, lastSessionEnd: end };
    savePlaytimeData(data);

    appOverview.minutes_playtime_forever = newTotal;
    appOverview.minutes_playtime_last_two_weeks = newTotal;
    appOverview.nPlaytimeForever = newTotal;
    if (typeof appOverview.TriggerChange === "function") {
      appOverview.TriggerChange();
    }

    return true;
  } catch {
    return false;
  }
}

function patchAppStore() {
  if (!window.appStore?.m_mapApps) return;
  if (appStore.m_mapApps._originalSet) return;

  appStore.m_mapApps._originalSet = appStore.m_mapApps.set;
  appStore.m_mapApps.set = function (appId, appOverview) {
    const result = appStore.m_mapApps._originalSet.call(this, appId, appOverview);
    restoreSavedPlaytimes();
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
      if (overview) {
        restoreSavedPlaytimes();
        applyRealSessionToOverview(overview);
      }
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
        restoreSavedPlaytimes();
        applyRealSessionToOverview(ov);
        appInfoStore?.OnAppOverviewChange?.([ov]);
      }
    }
  } catch {}
}

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
  } catch {}
}
