import { createShortcut } from "./createShortcut";
import { notify } from "./notify";

async function setupWebSocket(
    url: string,
    onMessage: (data: any) => void,
    onComplete: (removedGames?: Record<string, string[]>) => void
) {
    const ws = new WebSocket(url);

    ws.onopen = () => {
        console.log('NSL WebSocket connection opened');
        if (ws.readyState === WebSocket.OPEN) {
            ws.send('something'); // trigger backend if needed
        } else {
            console.log('Cannot send message, NSL WebSocket connection is not open');
        }
    };

    ws.onmessage = async (e) => {
        try {
            if (e.data[0] === '{' && e.data[e.data.length - 1] === '}') {
                const message = JSON.parse(e.data);

                if (message.status === "Manual scan completed") {
                    console.log('Manual scan completed');
                    onComplete();  
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
                    onComplete(message.removed_games);
                } else {
                    await onMessage(message);  
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
        if (e.code !== 1000) {
            console.log('Unexpected WS close, reopening...');
            setupWebSocket(url, onMessage, onComplete);
        }
    };

    return ws;
}

function cleanUpEmptyCollections(removedGames: Record<string, string[]>) {
    const collectionStore = (window as any).g_CollectionStore || (window as any).collectionStore;
    if (!collectionStore) return;

    Array.from(collectionStore.collectionsFromStorage.values()).forEach(c => {
        if ((c.visibleApps?.length || 0) === 0 && c.m_strName in removedGames) {
            collectionStore.DeleteCollection(c.m_strId);
            console.log(`Removed empty collection: ${c.m_strName}`);
        }
    });
}

export async function scan(onComplete: () => void) {
    console.log('Starting NSL Scan');

    return new Promise<void>((resolve) => {
        setupWebSocket('ws://localhost:8675/scan', async (message) => {
            await createShortcut(message); 
        }, (removedGames) => {
            if (removedGames) {
                cleanUpEmptyCollections(removedGames);
            }

            console.log('NSL Scan completed');
            onComplete();
            resolve();
        });
    });
}

export async function autoscan() {
    console.log('Starting NSL Autoscan');

    await setupWebSocket('ws://localhost:8675/autoscan', async (message) => {
        await createShortcut(message);
    }, (removedGames) => {
        if (removedGames) {
            cleanUpEmptyCollections(removedGames);
        }

        console.log('NSL Autoscan completed');
    });
}
