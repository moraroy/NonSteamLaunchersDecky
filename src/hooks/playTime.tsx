import { useEffect } from "react";

const STORAGE_KEY = "realPlaytimeData_Debug";

interface PlaytimeDataEntry {
  total: number;
  lastSessionEnd: number;
}

let playtimeCache: Record<string, PlaytimeDataEntry> | null = null;

const isValidEntry = (e: any): e is PlaytimeDataEntry =>
  e && typeof e.total === "number" && typeof e.lastSessionEnd === "number";

const loadPlaytimeData = (): Record<string, PlaytimeDataEntry> => {
  if (playtimeCache) return playtimeCache;
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    const parsed = raw ? JSON.parse(raw) : {};
    const cleaned: Record<string, PlaytimeDataEntry> = {};
    for (const [k, v] of Object.entries(parsed)) if (isValidEntry(v)) cleaned[k] = v;
    if (Object.keys(cleaned).length !== Object.keys(parsed).length)
      localStorage.setItem(STORAGE_KEY, JSON.stringify(cleaned));
    return (playtimeCache = cleaned);
  } catch {
    return (playtimeCache = {});
  }
};

const savePlaytimeData = (data: Record<string, PlaytimeDataEntry>) => {
  playtimeCache = data;
  localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
};

const isEnvironmentReady = () => {
  try {
    localStorage.setItem("__rp_test__", "1");
    localStorage.removeItem("__rp_test__");
    return window.appStore?.GetAppOverviewByAppID && window.appInfoStore;
  } catch {
    return false;
  }
};

const restoreSavedPlaytimes = () => {
  const data = loadPlaytimeData();
  if (!window.appStore?.GetAppOverviewByAppID) return;

  let removed = false;
  for (const [id, entry] of Object.entries(data)) {
    const ov = appStore.GetAppOverviewByAppID(Number(id));
    if (ov) {
      ov.minutes_playtime_forever = ov.minutes_playtime_last_two_weeks = ov.nPlaytimeForever = entry.total;
      ov.TriggerChange?.();
    } else {
      delete data[id];
      removed = true;
    }
  }
  if (removed) savePlaytimeData(data);
};

const applyRealSessionToOverview = (ov: any): boolean => {
  if (!ov || ov.app_type !== 1073741824) return false;

  const start = ov.rt_last_time_played;
  const end = ov.rt_last_time_locally_played;
  if (!start || !end || end <= start) return false;

  const mins = Math.floor((end - start) / 60);
  if (mins <= 0) return false;

  const data = loadPlaytimeData();
  const appId = String(ov.appid || ov.appid?.() || ov.appId);
  const prev = data[appId] || { total: 0, lastSessionEnd: 0 };
  if (end <= prev.lastSessionEnd) return false;

  const newTotal = prev.total + mins;
  data[appId] = { total: newTotal, lastSessionEnd: end };
  savePlaytimeData(data);

  ov.minutes_playtime_forever = ov.minutes_playtime_last_two_weeks = ov.nPlaytimeForever = newTotal;
  ov.TriggerChange?.();
  return true;
};

const patchAppStore = () => {
  if (!window.appStore?.m_mapApps || appStore.m_mapApps._originalSet) return;
  const map = appStore.m_mapApps;
  map._originalSet = map.set;
  map.set = function (id, ov) {
    const result = map._originalSet.call(this, id, ov);
    restoreSavedPlaytimes();
    applyRealSessionToOverview(ov);
    return result;
  };
};

const patchAppInfoStore = () => {
  if (!window.appInfoStore || appInfoStore._originalOnAppOverviewChange) return;
  appInfoStore._originalOnAppOverviewChange = appInfoStore.OnAppOverviewChange;
  appInfoStore.OnAppOverviewChange = function (apps) {
    for (const a of apps || []) {
      const id = typeof a?.appid === "function" ? a.appid() : a?.appid;
      const ov = id ? appStore.GetAppOverviewByAppID?.(Number(id)) ?? a : a;
      if (ov) {
        restoreSavedPlaytimes();
        applyRealSessionToOverview(ov);
      }
    }
    return appInfoStore._originalOnAppOverviewChange.call(this, apps);
  };
};

const manualPatch = () => {
  try {
    const m = location.pathname.match(/\/library\/app\/(\d+)/);
    if (!m) return;
    const ov = appStore.GetAppOverviewByAppID(Number(m[1]));
    if (ov) {
      restoreSavedPlaytimes();
      applyRealSessionToOverview(ov);
      appInfoStore?.OnAppOverviewChange?.([ov]);
    }
  } catch {}
};

export const initRealPlaytime = (retry = 0) => {
  if (!isEnvironmentReady()) {
    if (retry < 100) setTimeout(() => initRealPlaytime(retry + 1), 1000);
    return;
  }
  try {
    restoreSavedPlaytimes();
    patchAppStore();
    patchAppInfoStore();
    manualPatch();
  } catch {}
};
