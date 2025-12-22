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
    let terminationScheduled = false;

    SteamClient.Apps.RegisterForGameActionStart((gameActionId, gameId, action) => {
        if (!(gameId.length >= 18 && gameId.length <= 20)) return;

        if (action === "LaunchApp") {
            currentAppId = gameId;
            currentOverlayPIDs.clear();
            terminationScheduled = false;
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

            console.log("[Watcher] Current overlays for AppID", currentAppId, ":", Array.from(currentOverlayPIDs));

            if (currentOverlayPIDs.size === 0 && currentAppId && !terminationScheduled) {
                terminationScheduled = true;
                console.log("[Watcher] Last overlay removed for AppID:", currentAppId, "- terminating in 8s...");
                const appToTerminate = currentAppId;

                setTimeout(() => {
                    console.log("[Watcher] Terminating app:", appToTerminate);
                    SteamClient.Apps.TerminateApp(appToTerminate, false);
                    currentAppId = null; // Now safe to clear
                    terminationScheduled = false;
                }, 8000);
            }

        } catch (e) {
            console.error("[Watcher] Failed to fetch overlay browser info:", e);
        }
    };

    SteamClient.Overlay.RegisterOverlayBrowserInfoChanged(checkOverlays);

    setTimeout(checkOverlays, 500);

    console.log("[Watcher] Non-Steam overlay removal watcher initialized.");
}
