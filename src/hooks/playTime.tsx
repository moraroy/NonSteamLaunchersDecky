import { useEffect } from "react";

const STORAGE_KEY = "realPlaytimeData";

function loadPlaytimeData(): Record<string, number> {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY) || "{}");
  } catch {
    return {};
  }
}

function savePlaytimeData(data: Record<string, number>) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
}

function restoreSavedPlaytimes() {
  const data = loadPlaytimeData();
  if (!window.appStore?.GetAppOverviewByAppID) return;
  for (const [id, total] of Object.entries(data)) {
    const ov = appStore.GetAppOverviewByAppID(Number(id));
    if (ov) {
      ov.minutes_playtime_forever = total;
      ov.minutes_playtime_last_two_weeks = total;
      ov.nPlaytimeForever = total;
    }
  }
  console.log("[RealPlaytime] Restored saved totals for", Object.keys(data).length, "apps");
}

function applyRealPlaytimeToOverview(appOverview: any): boolean {
  if (!appOverview) return false;
  if (appOverview.app_type !== 1073741824) return false; // non-Steam shortcuts only

  const start = appOverview.rt_last_time_played;
  const end = appOverview.rt_last_time_locally_played;

  if (!start || !end || end < start) return false;

  const sessionSeconds = end - start;
  const sessionMinutes = Math.floor(sessionSeconds / 60);
  if (sessionMinutes <= 0) return false;

  const data = loadPlaytimeData();
  const appId = String(appOverview.appid || appOverview.appid?.() || appOverview.appId);
  const prevTotal = data[appId] || 0;
  const newTotal = prevTotal + sessionMinutes;
  data[appId] = newTotal;
  savePlaytimeData(data);

  appOverview.minutes_playtime_forever = newTotal;
  appOverview.minutes_playtime_last_two_weeks = newTotal;
  appOverview.nPlaytimeForever = newTotal;

  console.log(
    `[RealPlaytime] +${sessionMinutes} min added to ${appOverview.display_name || "Unknown"} (${appId}). Total: ${newTotal} min`
  );

  return true;
}

// New helper: only updates the display, doesn't add session time
function updateOverviewDisplay(appOverview: any) {
  if (!appOverview) return;

  const data = loadPlaytimeData();
  const appId = String(appOverview.appid || appOverview.appid?.() || appOverview.appId);
  const total = data[appId] || 0;

  appOverview.minutes_playtime_forever = total;
  appOverview.minutes_playtime_last_two_weeks = total;
  appOverview.nPlaytimeForever = total;
}

function patchAppStore() {
  if (!window.appStore?.m_mapApps) return;
  if (appStore.m_mapApps._originalSet) return;

  appStore.m_mapApps._originalSet = appStore.m_mapApps.set;
  appStore.m_mapApps.set = function (appId, appOverview) {
    try {
      applyRealPlaytimeToOverview(appOverview);
    } catch (e) {
      console.warn("[RealPlaytime] Failed in appStore.set:", e);
    }
    return appStore.m_mapApps._originalSet.call(this, appId, appOverview);
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
        if (overview) applyRealPlaytimeToOverview(overview);
      }
    } catch (e) {
      console.warn("[RealPlaytime] Failed in OnAppOverviewChange:", e);
    }
    return appInfoStore._originalOnAppOverviewChange.call(this, apps);
  };
}

function manualPatch() {
  try {
    if (appStore?.GetAllApps) {
      const all = appStore.GetAllApps() || [];
      for (const ov of all) updateOverviewDisplay(ov); // only update UI
      if (typeof appInfoStore?.OnAppOverviewChange === "function") {
        appInfoStore.OnAppOverviewChange(all);
      }
    } else if (window.appStore && typeof appStore.GetAppOverviewByAppID === "function") {
      const m = location.pathname.match(/\/library\/app\/(\d+)/);
      if (m) {
        const id = Number(m[1]);
        const ov = appStore.GetAppOverviewByAppID(id);
        if (ov) {
          updateOverviewDisplay(ov); // only update UI
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
    restoreSavedPlaytimes(); // restore totals first
    patchAppStore();
    patchAppInfoStore();
    manualPatch();
    console.log("[RealPlaytime] Initialized and patches applied.");
  } catch (err) {
    console.error("[RealPlaytime] Failed to patch playtime data", err);
  }
}
