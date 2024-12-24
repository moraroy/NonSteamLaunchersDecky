import { useState, useEffect } from 'react';

export function useMonitorConnection() {
  const [ws, setWs] = useState<WebSocket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [monitorStatus, setMonitorStatus] = useState<string>('Not Started');

  useEffect(() => {
    // Create a new WebSocket connection when the component mounts
    const socket = new WebSocket('ws://localhost:8675/monitor_process');

    socket.onopen = () => {
      setIsConnected(true);
      console.log('WebSocket connected!');
    };

    socket.onmessage = (event) => {
      // Handle incoming messages
      setMonitorStatus(event.data);
      console.log('Received:', event.data);
    };

    socket.onclose = () => {
      setIsConnected(false);
      console.log('WebSocket connection closed.');
    };

    socket.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    // Save WebSocket instance to state
    setWs(socket);

    // Cleanup on component unmount
    return () => {
      socket.close();
    };
  }, []);

  const sendMessage = (message: string) => {
    if (ws && isConnected) {
      ws.send(message);
    } else {
      console.error('WebSocket is not connected');
    }
  };

  return {
    isConnected,
    monitorStatus,
    sendMessage,
  };
}
