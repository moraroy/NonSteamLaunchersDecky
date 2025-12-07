import { createShortcut } from "./createShortcut";
import { notify } from "./notify";  // Make sure to import notify

async function setupWebSocket(
    url: string,
    onMessage: (data: any) => void,
    onComplete: () => void,
    launcherNames: Set<string>
) {
    const ws = new WebSocket(url);

    ws.onopen = () => {
        console.log('NSL WebSocket connection opened');
        if (ws.readyState === WebSocket.OPEN) {
            ws.send('something'); // just to trigger backend if needed
        } else {
            console.log('Cannot send message, NSL WebSocket connection is not open');
        }
    };

    ws.onmessage = async (e) => {
        try {
            // Parse only if it's valid JSON
            if (e.data[0] === '{' && e.data[e.data.length - 1] === '}') {
                const message = JSON.parse(e.data);

                if (message.status === "Manual scan completed") {
                    console.log('Manual scan completed');
                    onComplete();  // Trigger the completion callback
                    ws.close();
                } else if ('removed_games' in message) {
                    console.log('Removed games received:', message.removed_games);
                    for (const platform in message.removed_games) {
                        const games = message.removed_games[platform];
                        for (const gameName of games) {
                            notify.toast(
                                `${gameName} (${platform})`,
                                'has been removed from your library!'
                            );
                        }
                    }
                } else {
                    // Track launcher name for collection cleanup
                    if (message.Launcher) {
                        launcherNames.add(message.Launcher);
                    }
                    await onMessage(message);  // Process each game entry
                }
            }
        } catch (error) {
            console.error("Error processing WebSocket message:", error, e.data);
        }
    };

    ws.onerror = (e) => {
        const errorEvent = e as ErrorEvent;
        console.error(`NSL WebSocket error: ${errorEvent.message}`);
    };

    ws.onclose = (e) => {
        console.log(`NSL WebSocket connection closed, code: ${e.code}, reason: ${e.reason}`);
        // If not normal closure, try reconnect
        if (e.code !== 1000) {
            console.log('Unexpected WS close, reopening...');
            setupWebSocket(url, onMessage, onComplete, launcherNames);
        }
    };

    return ws;
}


export async function scan(onComplete: () => void) {
    console.log('Starting NSL Scan');
    const launcherNames = new Set<string>();

    return new Promise<void>((resolve) => {
        setupWebSocket('ws://localhost:8675/scan', async (message) => {
            await createShortcut(message); // create shortcut
            if (message.Launcher) {
                launcherNames.add(message.Launcher);
            }
        }, () => {
            console.log('NSL Scan completed');

            // Delete empty collections for the scanned launchers
            const collectionStore = (window as any).g_CollectionStore || (window as any).collectionStore;
            if (collectionStore) {
                Array.from(collectionStore.collectionsFromStorage.values()).forEach(c => {
                    if (launcherNames.has(c.m_strName)) {
                        if ((c.visibleApps?.length || 0) === 0) {
                            collectionStore.DeleteCollection(c.m_strId);
                            console.log(`Removed empty collection: ${c.m_strName}`);
                        } else {
                            console.log(`Collection not empty, skipped: ${c.m_strName} (Apps count: ${c.visibleApps.length})`);
                        }
                    }
                });
            }

            onComplete();
            resolve();
        }, launcherNames);
    });
}


export async function autoscan() {
    console.log('Starting NSL Autoscan');
    const launcherNames = new Set<string>();

    await setupWebSocket('ws://localhost:8675/autoscan', async (message) => {
        await createShortcut(message);
        if (message.Launcher) {
            launcherNames.add(message.Launcher);
        }
    }, () => {
        console.log('NSL Autoscan completed');


        const collectionStore = (window as any).g_CollectionStore || (window as any).collectionStore;
        if (collectionStore) {
            Array.from(collectionStore.collectionsFromStorage.values()).forEach(c => {
                if (launcherNames.has(c.m_strName) && (c.visibleApps?.length || 0) === 0) {
                    collectionStore.DeleteCollection(c.m_strId);
                    console.log(`Removed empty collection: ${c.m_strName}`);
                }
            });
        }
    }, launcherNames);
}
