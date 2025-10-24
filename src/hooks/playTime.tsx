import { useEffect } from "react";

const STORAGE_KEY = "realPlaytimeData";

interface PlaytimeDataEntry {
  total: number;
  lastSessionEnd: number;
}

function loadPlaytimeData(): Record<string, PlaytimeDataEntry> {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY) || "{}");
  } catch {
    return {};
  }
}

function savePlaytimeData(data: Record<string, PlaytimeDataEntry>) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
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
      if (typeof ov.TriggerChange === "function") ov.TriggerChange(); // force UI update
    } else {
      // App no longer exists → remove from local storage
      delete data[id];
      removedCount++;
    }
  }

  if (removedCount > 0) {
    savePlaytimeData(data);
    console.log(`[RealPlaytime] Removed ${removedCount} deleted apps from Local Storage`);
  }

  console.log("[RealPlaytime] Restored saved totals for", Object.keys(data).length, "apps");
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

    // Update UI immediately
    appOverview.minutes_playtime_forever = newTotal;
    appOverview.minutes_playtime_last_two_weeks = newTotal;
    appOverview.nPlaytimeForever = newTotal;

    if (typeof appOverview.TriggerChange === "function") appOverview.TriggerChange();

    console.log(`[RealPlaytime] +${sessionMinutes} min added to ${appOverview.display_name || "Unknown"} (${appId}). Total: ${newTotal} min`);
    return true;
  } catch (e) {
    console.warn("[RealPlaytime] Failed in applyRealSessionToOverview:", e);
    return false;
  }
}


function patchAppStore() {
  if (!window.appStore?.m_mapApps) return;
  if (appStore.m_mapApps._originalSet) return;

  appStore.m_mapApps._originalSet = appStore.m_mapApps.set;
  appStore.m_mapApps.set = function (appId, appOverview) {
    const result = appStore.m_mapApps._originalSet.call(this, appId, appOverview);
    try {
      // Always restore saved totals after Steam sets the object
      restoreSavedPlaytimes();
      // Also add any new session time if available
      applyRealSessionToOverview(appOverview);
    } catch (e) {
      console.warn("[RealPlaytime] Failed in appStore.set patch:", e);
    }
    return result;
  };
}


function patchAppInfoStore() {
  if (!window.appInfoStore) return;
  if (appInfoStore._originalOnAppOverviewChange) return;

  appInfoStore._originalOnAppOverviewChange = appInfoStore.OnAppOverviewChange;
  appInfoStore.OnAppOverviewChange = function (apps) {
    try {
      for (const a of apps || []) {
        const id = typeof a?.appid === "function" ? a.appid() : a?.appid;
        const overview =
          id !== undefined && appStore?.GetAppOverviewByAppID
            ? appStore.GetAppOverviewByAppID(Number(id))
            : a;
        if (overview) {
          restoreSavedPlaytimes(); // ensure saved totals are always applied
          applyRealSessionToOverview(overview);
        }
      }
    } catch (e) {
      console.warn("[RealPlaytime] Failed in OnAppOverviewChange patch:", e);
    }
    return appInfoStore._originalOnAppOverviewChange.call(this, apps);
  };
}


function manualPatch() {
  try {
    if (window.appStore && typeof appStore.GetAppOverviewByAppID === "function") {
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
    }
  } catch (e) {
    console.warn("[RealPlaytime] Manual patch error:", e);
  }
}


export function initRealPlaytime() {
  try {
    restoreSavedPlaytimes();
    patchAppStore();
    patchAppInfoStore();
    manualPatch();
    console.log("[RealPlaytime] Initialized and patches applied.");
  } catch (err) {
    console.error("[RealPlaytime] Failed to patch playtime data", err);
  }
}
