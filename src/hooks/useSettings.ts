import { useEffect, useState } from 'react';
import { ServerAPI } from 'decky-frontend-lib';

export type Settings = {
  autoscan: boolean;
  customSites: string;
  playtimeEnabled: boolean; // <-- new setting
};

export const useSettings = (serverApi: ServerAPI) => {
  const [settings, setSettings] = useState<Settings>({
    autoscan: false,
    customSites: "",
    playtimeEnabled: true, // default ON
  });

  // Load saved settings on mount
  useEffect(() => {
    const getData = async () => {
      const savedSettings = (
        await serverApi.callPluginMethod('get_setting', {
          key: 'settings',
          default: settings
        })
      ).result as Settings;
      setSettings(savedSettings);
    };
    getData();
  }, []);

  // Generic update helper
  async function updateSettings(
    key: keyof Settings,
    value: Settings[keyof Settings]
  ) {
    setSettings((oldSettings) => {
      const newSettings = { ...oldSettings, [key]: value };
      serverApi.callPluginMethod('set_setting', {
        key: 'settings',
        value: newSettings
      });
      return newSettings;
    });
  }

  // Existing setters
  function setAutoScan(value: Settings['autoscan']) {
    updateSettings('autoscan', value);
  }

  function setCustomSites(value: Settings['customSites']) {
    updateSettings('customSites', value);
  }

  // New setter for Playtime
  function setPlaytimeEnabled(value: Settings['playtimeEnabled']) {
    updateSettings('playtimeEnabled', value);
  }

  return { settings, setAutoScan, setCustomSites, setPlaytimeEnabled };
};
