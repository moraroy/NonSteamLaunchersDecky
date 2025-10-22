import { useEffect } from "react";

let playtimeByAppId: Record<number, { total_seconds: number }> = {};

async function loadPlaytime() {
  return new Promise((resolve, reject) => {
    const ws = new WebSocket("ws://localhost:8675/playtime");

    ws.onmessage = (event) => {
      try {
        const rawData = JSON.parse(event.data);

        playtimeByAppId = {};
        for (const key in rawData) {
          const entry = rawData[key];
          if (entry.appid && entry.total_seconds !== undefined) {
            playtimeByAppId[entry.appid] = {
              total_seconds: entry.total_seconds,
            };
          }
        }

        ws.close();
        resolve(true);
      } catch (err) {
        reject(err);
      }
    };

    ws.onerror = (err) => {
      console.error("WebSocket error", err);
      reject(err);
    };

    ws.onclose = () => {
      // Optional: handle socket close if needed
    };
  });
}

function applyRealPlaytimeToOverview(appOverview: any): boolean {
  if (!appOverview) return false;
  if (appOverview.app_type !== 1073741824) return false; // non-Steam shortcuts only

  const appid = appOverview.appid || appOverview.id;
  if (!appid) return false;

  const playtimeEntry = playtimeByAppId[appid];
  if (!playtimeEntry) return false;

  const minutes = Math.floor(playtimeEntry.total_seconds / 60);

  appOverview.minutes_playtime_forever = minutes;
  appOverview.minutes_playtime_last_two_weeks = minutes;
  appOverview.nPlaytimeForever = minutes;

  return true;
}

function patchAppStore() {
  if (!window.appStore?.m_mapApps) return;
  if (appStore.m_mapApps._originalSet) return;

  appStore.m_mapApps._originalSet = appStore.m_mapApps.set;
  appStore.m_mapApps.set = function (appId, appOverview) {
    try {
      applyRealPlaytimeToOverview(appOverview);
    } catch {}
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
    } catch {}
    return appInfoStore._originalOnAppOverviewChange.call(this, apps);
  };
}

function manualPatch() {
  try {
    if (appStore?.GetAllApps) {
      const all = appStore.GetAllApps() || [];
      for (const ov of all) applyRealPlaytimeToOverview(ov);
      if (typeof appInfoStore?.OnAppOverviewChange === "function") {
        appInfoStore.OnAppOverviewChange(all);
      }
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
  loadPlaytime()
    .then(() => {
      patchAppStore();
      patchAppInfoStore();
      manualPatch();
    })
    .catch((err) => {
      console.error("Failed to load playtime data via WebSocket", err);
    });
}
