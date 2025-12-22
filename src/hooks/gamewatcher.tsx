// Create a global flag to ensure the watcher runs only once
declare global {
    interface Window {
        __nslGameWatcherInitialized?: boolean;
    }
}

export async function initGameWatcher() {
    if (window.__nslGameWatcherInitialized) return;
    window.__nslGameWatcherInitialized = true;

    if (!window.SteamClient || !SteamClient.Overlay || !SteamClient.Apps) return;

    let currentAppId: string | null = null;
    let currentOverlayPIDs = new Set<number>();

    // --- Game launch detection ---
    SteamClient.Apps.RegisterForGameActionStart((gameActionId, gameId, action) => {
        if (!(gameId.length >= 18 && gameId.length <= 20)) return;

        if (action === "LaunchApp") {
            currentAppId = gameId;
            currentOverlayPIDs.clear();
            console.log("[Watcher] Non-Steam game launch detected:", gameId);
        }
    });

    const checkOverlays = async () => {
        if (!currentAppId) return;

        try {
            const browsers = await SteamClient.Overlay.GetOverlayBrowserInfo();
            const seenPIDs = new Set(browsers.map(b => b.unPID));

            for (const pid of Array.from(currentOverlayPIDs)) {
                if (!seenPIDs.has(pid)) {
                    currentOverlayPIDs.delete(pid);
                    console.log("[Watcher] Overlay browser removed:", pid, "AppID:", currentAppId, "at", performance.now());
                }
            }

            for (const pid of seenPIDs) currentOverlayPIDs.add(pid);

            if (currentOverlayPIDs.size === 0 && currentAppId) {
                console.log("[Watcher] Last overlay removed for AppID:", currentAppId, "- terminating in 8s...");
                const appToTerminate = currentAppId;
                currentAppId = null;
                setTimeout(() => {
                    console.log("[Watcher] Terminating app:", appToTerminate);
                    SteamClient.Apps.TerminateApp(appToTerminate, false);
                }, 8000);
            }

        } catch (e) {
            console.error("[Watcher] Failed to fetch overlay browser info:", e);
        }
    };

    SteamClient.Overlay.RegisterOverlayBrowserInfoChanged(checkOverlays);
    checkOverlays();

    console.log("[Watcher] Non-Steam overlay removal watcher initialized.");
}
