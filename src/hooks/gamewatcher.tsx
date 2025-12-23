// gamewatcher.tsx

declare global {
  interface Window {
    __gameWatcherInit?: boolean;
    __steamWatcherCore?: boolean;
    WatcherCore?: WatcherCoreType;
  }
}

type WatcherCoreType = {
  setActiveApp: (appId: string, source: string) => void;
  scheduleTermination: (source: string, delay?: number) => void;
};

/*****************************************************
 * PUBLIC ENTRY POINT
 *****************************************************/
export function initGameWatcher(): void {
  if (window.__gameWatcherInit) return;
  window.__gameWatcherInit = true;

  initWatcherCore();
  initGameModeWatcher();
  initDesktopModeWatcher();

  console.log("[GameWatcher] Unified watcher initialized");
}

/*****************************************************
 * WATCHER CORE — single authority
 *****************************************************/
function initWatcherCore(): void {
  if (window.__steamWatcherCore) return;
  window.__steamWatcherCore = true;

  const core = {
    activeAppId: null as string | null,
    terminationScheduled: false,

    setActiveApp(appId: string, source: string) {
      if (!appId) return;

      if (this.activeAppId !== appId) {
        this.activeAppId = appId;
        this.terminationScheduled = false;
        console.log(`[WatcherCore] Active app set by ${source}:`, appId);
      }
    },

    scheduleTermination(source: string, delay = 10000) {
      if (!this.activeAppId || this.terminationScheduled) return;

      this.terminationScheduled = true;
      console.log(`[WatcherCore] Termination scheduled by ${source}`);

      setTimeout(() => {
        try {
          (window as any).SteamClient?.Apps?.TerminateApp(
            this.activeAppId,
            false
          );
          console.log("[WatcherCore] App terminated:", this.activeAppId);
        } catch (e) {
          console.error("[WatcherCore] Termination failed:", e);
        } finally {
          this.activeAppId = null;
          this.terminationScheduled = false;
        }
      }, delay);
    }
  };

  window.WatcherCore = core;
}

/*****************************************************
 * GAME MODE WATCHER (Overlay + lifetime heuristics)
 *****************************************************/
function initGameModeWatcher(): void {
  const SteamClient = (window as any).SteamClient;
  if (!SteamClient?.Apps) return;

  const state = {
    gameId: null as string | null,
    launchTime: 0,
    inferredRunning: false,
    overlaySequence: [] as { time: number; active: number }[],
    lastOverlayChange: 0
  };

  try {
    SteamClient.Apps.RegisterForGameActionStart(
      (_actionId: any, gameId: string, action: string) => {
        if (action !== "LaunchApp") return;

        state.gameId = gameId;
        state.launchTime = Date.now();
        state.inferredRunning = true;

        window.WatcherCore?.setActiveApp(gameId, "GameMode");
        console.log("[GameMode] Launch detected:", gameId);

        // Delay to allow game to stabilize
        setTimeout(() => {
          try {
            SteamClient.GameSessions?.RegisterForAppLifetimeNotifications(
              (evt: any) => {
                if (evt.bRunning === false && state.inferredRunning) {
                  state.inferredRunning = false;
                  window.WatcherCore?.scheduleTermination(
                    "GameMode:SteamEnded"
                  );
                }
              }
            );
          } catch {}

          try {
            const originalSet = SteamClient.Overlay.SetOverlayState;

            SteamClient.Overlay.SetOverlayState = function (
              appId: string,
              overlayState: number
            ) {
              const now = Date.now();

              state.overlaySequence.push({
                time: now,
                active: overlayState
              });
              if (state.overlaySequence.length > 5) {
                state.overlaySequence.shift();
              }

              if (
                state.inferredRunning &&
                state.overlaySequence.length >= 2
              ) {
                const last =
                  state.overlaySequence[state.overlaySequence.length - 1];
                const prev =
                  state.overlaySequence[state.overlaySequence.length - 2];

                if (
                  last.active === 3 &&
                  prev.active === 0 &&
                  now - state.launchTime > 15000 &&
                  now - state.lastOverlayChange > 3000
                ) {
                  window.WatcherCore?.scheduleTermination(
                    "GameMode:OverlayExit"
                  );
                }
              }

              state.lastOverlayChange = now;
              return originalSet.apply(this, arguments as any);
            };
          } catch {}

          console.log("[GameMode] Heuristic watcher active");
        }, 90000);
      }
    );
  } catch (e) {
    console.error("[GameMode] Init failed:", e);
  }
}

/*****************************************************
 * DESKTOP MODE WATCHER (console.log parsing)
 *****************************************************/
function initDesktopModeWatcher(): void {
  let gameRunning = false;

  const originalLog = console.log;

  console.log = function (...args: any[]) {
    originalLog.apply(console, args);

    try {
      const line = args.join(" ");

      // Launch detection
      if (
        line.includes("OnGameActionUserRequest") &&
        line.includes("LaunchApp CreatingProcess")
      ) {
        const match = line.match(/OnGameActionUserRequest:\s*(\d+)/);
        if (match) {
          const appId = match[1];
          if (appId.length >= 18 && appId.length <= 20) {
            gameRunning = true;
            window.WatcherCore?.setActiveApp(appId, "DesktopMode");
            originalLog("[DesktopMode] Launch detected:", appId);
          }
        }
      }

      // Exit detection
      if (
        gameRunning &&
        (line.includes("Removing overlay browser window") ||
          line.includes(
            "NetworkDiagnosticsStore - unregistering"
          ))
      ) {
        gameRunning = false;
        window.WatcherCore?.scheduleTermination(
          "DesktopMode:ExitSignal"
        );
      }
    } catch (e) {
      originalLog("[DesktopMode] Watcher error:", e);
    }
  };
}
