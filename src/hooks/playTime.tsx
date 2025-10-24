import { useEffect } from "react";

const STORAGE_KEY = "realPlaytimeData";
const lastEndTimes: Record<string, number> = {};

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

function applyRealPlaytimeToOverview(appOverview: any): boolean {
  if (!appOverview || appOverview.app_type !== 1073741824) return false;

  const appId = String(appOverview.appid || appOverview.appid?.() || appOverview.appId);
  const start = appOverview.rt_last_time_played;
  const end = appOverview.rt_last_time_locally_played;

  if (!start || !end || end < start) return false;

  // Prevent double-counting
  if (lastEndTimes[appId] === end) return false;
  lastEndTimes[appId] = end;

  const sessionMinutes = Math.floor((end - start) / 60);
  if (sessionMinutes <= 0) return false;

  const data = loadPlaytimeData();
  const prevTotal = data[appId] || 0;
  const newTotal = prevTotal + sessionMinutes;
  data[appId] = newTotal;
  savePlaytimeData(data);

  // Update app overview fields
  appOverview.minutes_playtime_forever = newTotal;
  appOverview.minutes_playtime_last_two_weeks = newTotal;
  appOverview.nPlaytimeForever = newTotal;

  console.log(`[RealPlaytime] +${sessionMinutes} min added to ${appOverview.display_name || "Unknown"} (${appId}). Total: ${newTotal} min`);

  return true;
}

function patchAppStore() {
  if (!window.appStore?.m_mapApps || appStore.m_mapApps._originalSet) return;

  appStore.m_mapApps._originalSet = appStore.m_mapApps.set;
  appStore.m_mapApps.set = function (appId, appOverview) {
    try {
      applyRealPlaytimeToOverview(appOverview);
    } catch {}
    return appStore.m_mapApps._originalSet.call(this, appId, appOverview);
  };
}

function patchAppInfoStore() {
  if (!window.appInfoStore || appInfoStore._originalOnAppOverviewChange) return;

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
    } catch {}
    return appInfoStore._originalOnAppOverviewChange.call(this, apps);
  };
}

function manualPatch() {
  try {
    if (appStore?.GetAllApps) {
      const all = appStore.GetAllApps() || [];
      for (const ov of all) applyRealPlaytimeToOverview(ov);
      appInfoStore?.OnAppOverviewChange?.(all);
    } else if (window.appStore && typeof appStore.GetAppOverviewByAppID === "function") {
      const m = location.pathname.match(/\/library\/app\/(\d+)/);
      if (m) {
        const id = Number(m[1]);
        const ov = appStore.GetAppOverviewByAppID(id);
        if (ov) {
          applyRealPlaytimeToOverview(ov);
          appInfoStore?.OnAppOverviewChange?.([ov]);
        }
      }
    }
  } catch {}
}

export function initRealPlaytime() {
  try {
    patchAppStore();
    patchAppInfoStore();
    manualPatch();
    console.log("[RealPlaytime] Initialized and patches applied.");
  } catch (err) {
    console.error("Failed to patch playtime data", err);
  }
}
