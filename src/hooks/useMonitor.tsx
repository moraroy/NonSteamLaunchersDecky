import { useState, useEffect } from "react";

interface MonitorState {
  isMonitoring: boolean;
  message: string;
  error?: string;
}

const useMonitor = () => {
  const [monitorState, setMonitorState] = useState<MonitorState>({
    isMonitoring: false,
    message: "Monitor is disabled.",
  });
  const [ws, setWs] = useState<WebSocket | null>(null); // WebSocket state to hold the connection

  useEffect(() => {
    if (monitorState.isMonitoring) {
      // If monitor is turned on, establish the WebSocket connection
      const websocket = new WebSocket("ws://localhost:8675/monitor_process"); // Adjust URL if needed

      websocket.onopen = () => {
        console.log("WebSocket connection established.");
      };

      websocket.onmessage = (event) => {
        console.log("Message from server:", event.data);
        // Update the monitorState with the message from the server
        setMonitorState((prevState) => ({
          ...prevState,
          message: event.data, // Set the message from the server
        }));
      };

      websocket.onerror = (error) => {
        console.error("WebSocket Error:", error);
        setMonitorState({
          isMonitoring: false,
          message: "WebSocket error",
          error: error.message,
        });
      };

      websocket.onclose = () => {
        console.log("WebSocket connection closed.");
        setMonitorState({ isMonitoring: false, message: "Monitor is disabled." });
      };

      // Save the WebSocket instance to state
      setWs(websocket);
    } else {
      // If monitor is turned off, close the WebSocket connection
      if (ws) {
        ws.close();
      }
    }

    // Cleanup WebSocket on component unmount or if monitor is turned off
    return () => {
      if (ws) {
        ws.close();
      }
    };
  }, [monitorState.isMonitoring]); // Effect runs when monitor state changes

  // Function to start monitoring
  const startMonitoring = () => {
    setMonitorState({ isMonitoring: true, message: "Starting monitor..." });
  };

  // Function to stop monitoring
  const stopMonitoring = () => {
    setMonitorState({ isMonitoring: false, message: "Stopping monitor..." });
  };

  return {
    monitorState,
    startMonitoring,
    stopMonitoring,
  };
};

export default useMonitor;

