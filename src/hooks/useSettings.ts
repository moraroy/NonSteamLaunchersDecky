import { useEffect, useState } from 'react';
import { ServerAPI } from 'decky-frontend-lib';

export type Settings = {
  autoscan: boolean;
  customSites: string;
  playtimeEnabled: boolean;
  thememusicEnabled: boolean;
};

export const useSettings = (serverApi: ServerAPI) => {
  const [settings, setSettings] = useState<Settings>({
    autoscan: false,
    customSites: "",
    playtimeEnabled: true,
    thememusicEnabled: true,
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
  }, [serverApi]);

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

  // Setters
  function setAutoScan(value: Settings['autoscan']) {
    updateSettings('autoscan', value);
  }

  function setCustomSites(value: Settings['customSites']) {
    updateSettings('customSites', value);
  }

  function setPlaytimeEnabled(value: Settings['playtimeEnabled']) {
    updateSettings('playtimeEnabled', value);
  }

  function setThemeMusicEnabled(value: Settings['thememusicEnabled']) {
    updateSettings('thememusicEnabled', value);
  }

  return {
    settings,
    setAutoScan,
    setCustomSites,
    setPlaytimeEnabled,
    setThemeMusicEnabled,
  };
};
