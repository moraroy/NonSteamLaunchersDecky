import { useEffect, useState } from 'react'
import { ServerAPI } from 'decky-frontend-lib'

export type Settings = {
  autoscan: boolean
  customSites: string
  monitor: boolean  // Added monitor setting
}

export const useSettings = (serverApi: ServerAPI) => {
  const [settings, setSettings] = useState<Settings>({
    autoscan: false,
    customSites: "",
    monitor: false,  // Default value for monitor
  })

  useEffect(() => {
    const getData = async () => {
      const savedSettings = (
        await serverApi.callPluginMethod('get_setting', {
          key: 'settings',
          default: settings
        })
      ).result as Settings
      setSettings(savedSettings)
    }
    getData()
  }, [])

  async function updateSettings(
    key: keyof Settings,
    value: Settings[keyof Settings]
  ) {
    setSettings((oldSettings) => {
      const newSettings = { ...oldSettings, [key]: value }
      serverApi.callPluginMethod('set_setting', {
        key: 'settings',
        value: newSettings
      })
      return newSettings
    })
  }

  // Function to update the autoscan setting
  function setAutoScan(value: Settings['autoscan']) {
    updateSettings('autoscan', value)
  }

  // Function to update the customSites setting
  function setCustomSites(value: Settings['customSites']) {
    updateSettings('customSites', value)
  }

  // Function to update the monitor setting
  function setMonitor(value: Settings['monitor']) {
    updateSettings('monitor', value)
  }

  return { settings, setAutoScan, setCustomSites, setMonitor }  // Return setMonitor as part of the hook
}
