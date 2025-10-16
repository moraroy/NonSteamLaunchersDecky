import os
import json

class SettingsManager:
    def __init__(self, name="config", settings_directory="."):
        self.filename = f"{name}.json"
        self.settings_directory = settings_directory
        self.settings_path = os.path.join(settings_directory, self.filename)

        # Ensure settings directory exists
        os.makedirs(self.settings_directory, exist_ok=True)

        self.settings = self._load_settings()

    def _load_settings(self):
        if os.path.isfile(self.settings_path):
            try:
                with open(self.settings_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"[SettingsManager] Failed to load settings: {e}")
        return {}

    def save_settings(self):
        try:
            with open(self.settings_path, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            print(f"[SettingsManager] Failed to save settings: {e}")

    #Match what's called in main.py
    def getSetting(self, key, default=None):
        return self.settings.get(key, default)

    def setSetting(self, key, value):
        self.settings[key] = value
        self.save_settings()