import { createShortcut } from "./createShortcut";
import { notify } from "./notify";  // Make sure to import notify

async function setupWebSocket(url: string, onMessage: (data: any) => void, onComplete: () => void) {
    const ws = new WebSocket(url);

    ws.onopen = () => {
        console.log('NSL WebSocket connection opened');
        if (ws.readyState === WebSocket.OPEN) {
            ws.send('something');
        } else {
            console.log('Cannot send message, NSL WebSocket connection is not open');
        }
    };

    ws.onmessage = async (e) => {
        console.log(`Received data from NSL server: ${e.data}`);
        if (e.data[0] === '{' && e.data[e.data.length - 1] === '}') {
            try {
                const message = JSON.parse(e.data);
                if (message.status === "Manual scan completed") {
                    console.log('Manual scan completed');
                    onComplete();  // Trigger the completion callback
                } else if ('removed_games' in message) {
                    console.log('Removed games received:', message.removed_games);

                    // Count total removed games across all platforms
                    let totalRemoved = 0;
                    for (const platform in message.removed_games) {
                        totalRemoved += message.removed_games[platform].length;
                    }

                    if (totalRemoved > 0) {
                        notify.toast(
                          "Library Update",
                          `${totalRemoved} game${totalRemoved !== 1 ? 's' : ''} have been removed from your library!`
                        );
                    }

                } else {
                    await onMessage(message);  // Process each game entry one at a time
                }
            } catch (error) {
                console.error(`Error parsing data as JSON: ${error}`);
            }
        }
    };

    ws.onerror = (e) => {
        const errorEvent = e as ErrorEvent;
        console.error(`NSL WebSocket error: ${errorEvent.message}`);
    };

    ws.onclose = (e) => {
        console.log(`NSL WebSocket connection closed, code: ${e.code}, reason: ${e.reason}`);
        if (e.code !== 1000) {
            console.log(`Unexpected close of WS NSL connection, reopening`);
            setupWebSocket(url, onMessage, onComplete);
        }
    };

    return ws;
}

export async function scan(onComplete: () => void) {
    console.log('Starting NSL Scan');
    return new Promise<void>((resolve) => {
        const ws = setupWebSocket('ws://localhost:8675/scan', createShortcut, () => {
            console.log('NSL Scan completed');
            onComplete();  // Trigger the completion callback
            resolve();
        });
    });
}

export async function autoscan() {
    console.log('Starting NSL Autoscan');
    await setupWebSocket('ws://localhost:8675/autoscan', createShortcut, () => {});
}
