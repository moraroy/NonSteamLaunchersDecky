import { useEffect } from "react";

const STORAGE_KEY = "realPlaytimeData";

interface PlaytimeDataEntry {
  total: number;           // total minutes played
  lastSessionEnd: number;  // timestamp of last counted session
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

  for (const [id, entry] of Object.entries(data)) {
    const ov = appStore.GetAppOverviewByAppID(Number(id));
    if (ov) injectTotals(ov, entry.total);
  }

  console.log("[RealPlaytime] Restored totals for", Object.keys(data).length, "apps");
}


function injectTotals(appOverview: any, total: number) {
  if (!appOverview) return;

  // Wrap expected functions if missing
  if (typeof appOverview.appid !== "function") {
    const originalId = appOverview.appid;
    appOverview.appid = () => originalId;
  }
  if (typeof appOverview.icon_hash !== "function") {
    appOverview.icon_hash = () => null;
  }

  appOverview.minutes_playtime_forever = total;
  appOverview.minutes_playtime_last_two_weeks = total;
  appOverview.nPlaytimeForever = total;
}


function applyRealPlaytimeToOverview(appOverview: any): boolean {
  if (!appOverview || appOverview.app_type !== 1073741824) return false; // non-Steam only

  const start = appOverview.rt_last_time_played;
  const end = appOverview.rt_last_time_locally_played;

  if (!start || !end || end <= start) return false;

  const sessionMinutes = Math.floor((end - start) / 60);
  if (sessionMinutes <= 0) return false;

  const data = loadPlaytimeData();
  const appId = String(appOverview.appid?.());

  const prevEntry = data[appId] || { total: 0, lastSessionEnd: 0 };

  // Prevent double counting
  if (end <= prevEntry.lastSessionEnd) return false;

  const newTotal = prevEntry.total + sessionMinutes;

  data[appId] = { total: newTotal, lastSessionEnd: end };
  savePlaytimeData(data);

  injectTotals(appOverview, newTotal);

  console.log(`[RealPlaytime] +${sessionMinutes} min for ${appOverview.display_name || "Unknown"} (${appId}). Total: ${newTotal}`);
  return true;
}


function patchAppStore() {
  if (!window.appStore?.m_mapApps || appStore.m_mapApps._patched) return;

  const originalSet = appStore.m_mapApps.set.bind(appStore.m_mapApps);
  appStore.m_mapApps.set = function (appId, appOverview) {
    try { applyRealPlaytimeToOverview(appOverview); } 
    catch (e) { console.warn("[RealPlaytime] appStore.set patch error:", e); }

    return originalSet(appId, appOverview);
  };

  appStore.m_mapApps._patched = true;
}


function patchAppInfoStore() {
  if (!window.appInfoStore || appInfoStore._patched) return;

  const originalOnChange = appInfoStore.OnAppOverviewChange.bind(appInfoStore);
  appInfoStore.OnAppOverviewChange = function (apps: any[]) {
    try {
      for (const a of apps || []) {
        const overview = a.appid ? appStore.GetAppOverviewByAppID(Number(a.appid())) || a : a;
        if (overview) applyRealPlaytimeToOverview(overview);
      }
    } catch (e) {
      console.warn("[RealPlaytime] OnAppOverviewChange patch error:", e);
    }
    return originalOnChange(apps);
  };

  appInfoStore._patched = true;
}


function manualPatch() {
  try {
    if (appStore?.GetAllApps) {
      const all = appStore.GetAllApps() || [];
      for (const ov of all) {
        const total = loadPlaytimeData()[String(ov.appid?.())]?.total || 0;
        injectTotals(ov, total);
      }
      appInfoStore?.OnAppOverviewChange?.(all);
    }
  } catch (e) {
    console.warn("[RealPlaytime] manualPatch error:", e);
  }
}


export function initRealPlaytime() {
  try {
    restoreSavedPlaytimes();
    patchAppStore();
    patchAppInfoStore();
    manualPatch();
    console.log("[RealPlaytime] Initialized. Event-driven updates active.");
  } catch (err) {
    console.error("[RealPlaytime] Failed to initialize:", err);
  }
}
