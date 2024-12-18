import { useState, useEffect } from 'react';

interface LauncherStatus {
  installedLaunchers: string[];  // List of installed launchers
}

export const useLauncherStatus = () => {
  const [launcherStatus, setLauncherStatus] = useState<LauncherStatus | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  // WebSocket connection to check for launcher status
  const fetchLauncherStatus = (): (() => void) => {
    setLoading(true);
    console.log("Connecting to WebSocket to check launcher status...");

    const socket = new WebSocket("ws://localhost:8675/launcher_status");

    socket.onopen = () => {
      console.log("WebSocket connected to check launcher status");
    };

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log("Received launcher status:", data);

      if (data.error) {
        setError(data.error);
      } else {
        const { installedLaunchers } = data;
        setLauncherStatus({
          installedLaunchers
        });
      }
      setLoading(false);
    };

    socket.onerror = (error) => {
      console.error("WebSocket error:", error);
      setError("WebSocket error occurred while checking for launcher status.");
      setLoading(false);
    };

    socket.onclose = () => {
      console.log("WebSocket connection closed");
    };

    return () => {
      socket.close();
    };
  };

  useEffect(() => {
    const socketCleanup = fetchLauncherStatus();
    return () => {
      socketCleanup();
    };
  }, []);

  return { launcherStatus, error, loading };
};