import { useState, useEffect } from 'react';

interface UpdateInfo {
  status: string;  // "Up-to-date" or "Update available"
  local_version: string;
  github_version: string;
  patch_notes: Record<string, { formatted_note: string }[]>;  // New structure for patch notes
}

export const useUpdateInfo = () => {
  const [updateInfo, setUpdateInfo] = useState<UpdateInfo | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  // WebSocket connection to check for updates
  const fetchUpdateInfo = (): (() => void) => {
    setLoading(true);
    console.log("Connecting to WebSocket to check for updates...");

    const socket = new WebSocket("ws://localhost:8675/check_update");

    socket.onopen = () => {
      console.log("WebSocket connected to check update");
    };

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log("Received update information:", data);

      if (data.error) {
        setError(data.error);
      } else {
        const { status, local_version, github_version, patch_notes } = data;
        setUpdateInfo({
          status,
          local_version,
          github_version,
          patch_notes,  // Now we also store the patch notes
        });
      }
      setLoading(false);
    };

    socket.onerror = (error) => {
      console.error("WebSocket error:", error);
      setError("WebSocket error occurred while checking for updates.");
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
    const socketCleanup = fetchUpdateInfo();
    return () => {
      socketCleanup();
    };
  }, []);

  return { updateInfo, error, loading };
};
