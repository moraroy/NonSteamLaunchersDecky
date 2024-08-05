import { useState, useEffect } from "react";

export const useLogMessages = () => {
    const [logMessages, setLogMessages] = useState<string[]>([]);

    useEffect(() => {
        const ws = new WebSocket('ws://localhost:8675/logUpdates');

        ws.onmessage = (event: MessageEvent) => {
            setLogMessages(prevMessages => [...prevMessages, event.data]);
        };

        ws.onerror = (error: Event) => {
            console.error('WebSocket error:', error);
        };

        ws.onclose = (event: CloseEvent) => {
            console.log('WebSocket closed:', event);
        };

        return () => {
            ws.close();
        };
    }, []);

    return logMessages;
};