export async function initGameWatcher() {
    if (!window.SteamClient || !SteamClient.Overlay || !SteamClient.Apps) return;

    let currentAppId: string | null = null;
    let currentOverlayPIDs = new Set<number>();

    SteamClient.Apps.RegisterForGameActionStart((gameActionId, gameId, action) => {
        // Only run for non-Steam games (18-20 digit IDs)
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

            // Detect removed overlays
            for (const pid of Array.from(currentOverlayPIDs)) {
                if (!seenPIDs.has(pid)) {
                    currentOverlayPIDs.delete(pid);
                    console.log("[Watcher] Overlay browser removed:", pid, "AppID:", currentAppId, "at", performance.now());
                }
            }

            // Track new overlays
            for (const pid of seenPIDs) currentOverlayPIDs.add(pid);

            // Terminate game if all overlays removed
            if (currentOverlayPIDs.size === 0 && currentAppId) {
                console.log("[Watcher] Last overlay removed for AppID:", currentAppId, "- terminating in 8s...");
                const appToTerminate = currentAppId;
                currentAppId = null; // prevent double termination
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
