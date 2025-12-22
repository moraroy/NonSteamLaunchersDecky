let watcherInitialized = false;

// Prevent duplicate termination attempts per app
const terminatingApps = new Set<string>();

export function initGameWatcher() {
    if (watcherInitialized) return;
    watcherInitialized = true;

    if (!window.SteamClient?.Overlay || !window.SteamClient?.Apps) {
        console.warn("[Watcher] SteamClient not ready");
        return;
    }

    let currentAppId: string | null = null;
    let currentOverlayPIDs = new Set<number>();

    // -----------------------------
    // Game launch detection
    // -----------------------------
    SteamClient.Apps.RegisterForGameActionStart(
        (_gameActionId, gameId, action) => {
            if (!(gameId.length >= 18 && gameId.length <= 20)) return;

            if (action === "LaunchApp") {
                currentAppId = gameId;
                currentOverlayPIDs.clear();
                console.log("[Watcher] Non-Steam game launch detected:", gameId);
            }
        }
    );

    // -----------------------------
    // Safe terminate with 1 retry
    // -----------------------------
    const terminateWithRetry = (appId: string) => {
        if (terminatingApps.has(appId)) return;
        terminatingApps.add(appId);

        let attempts = 0;
        const maxAttempts = 2;

        const tryTerminate = async () => {
            attempts++;
            console.log(`[Watcher] Terminate attempt ${attempts} for AppID:`, appId);

            try {
                SteamClient.Apps.TerminateApp(appId, false);
            } catch (e) {
                console.warn("[Watcher] Terminate threw:", e);
            }

            // Verify after Steam settles
            setTimeout(async () => {
                try {
                    const runningApps = await SteamClient.Apps.GetRunningApps();
                    const stillRunning = runningApps.some(a => a.appid === appId);

                    if (stillRunning && attempts < maxAttempts) {
                        console.warn("[Watcher] App still running, retrying terminate");
                        tryTerminate();
                    } else if (stillRunning) {
                        console.error("[Watcher] Termination failed after retry:", appId);
                        terminatingApps.delete(appId);
                    } else {
                        console.log("[Watcher] App successfully terminated:", appId);
                        terminatingApps.delete(appId);
                    }
                } catch (e) {
                    console.error("[Watcher] Failed to verify running apps:", e);
                    terminatingApps.delete(appId);
                }
            }, 2000);
        };

        tryTerminate();
    };

    // -----------------------------
    // Overlay tracking
    // -----------------------------
    const checkOverlays = async () => {
        if (!currentAppId) return;

        try {
            const browsers = await SteamClient.Overlay.GetOverlayBrowserInfo();
            const seenPIDs = new Set(browsers.map(b => b.unPID));

            currentOverlayPIDs = seenPIDs;

            if (currentOverlayPIDs.size === 0 && currentAppId) {
                const appToTerminate = currentAppId;
                currentAppId = null;

                console.log(
                    "[Watcher] Last overlay removed for AppID:",
                    appToTerminate,
                    "- scheduling termination"
                );

                setTimeout(() => {
                    terminateWithRetry(appToTerminate);
                }, 8000);
            }
        } catch (e) {
            console.error("[Watcher] Failed to fetch overlay browser info:", e);
        }
    };

    SteamClient.Overlay.RegisterOverlayBrowserInfoChanged(checkOverlays);

    // Run once on init
    checkOverlays();

    console.log("[Watcher] Initialized with retry support");
}
