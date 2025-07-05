import {
  ButtonItem,
  definePlugin,
  PanelSection,
  PanelSectionRow,
  ServerAPI,
  staticClasses,
  ToggleField,
  showModal,
  Focusable,
} from "decky-frontend-lib";
import { useState, useEffect, VFC } from "react";
import { RxRocket } from "react-icons/rx";
import { notify } from "./hooks/notify";
import { CustomSiteModal } from "./components/modals/customSiteModal";
import { useSettings } from './hooks/useSettings';
import { LauncherInstallModal } from "./components/modals/launcherInstallModal";
import { StreamingInstallModal } from "./components/modals/streamingInstallModal";
import { StartFreshModal } from "./components/modals/startFreshModal";
import { UpdateRestartModal } from './components/modals/updateRestartModal';
import { RestoreGameSavesModal } from "./components/modals/restoreGameSavesModal";
import { useUpdateInfo } from "./hooks/getUpdate";
import { sitesList } from "./hooks/siteList";
import { autoscan, scan } from "./hooks/scan";
import { UpdateNotesModal } from "./components/modals/updateNotesModal";

const initialOptions = sitesList;

const Content: VFC<{ serverAPI: ServerAPI }> = ({ serverAPI }) => {
  console.log('Content rendered');

  const launcherOptions = initialOptions.filter((option) => option.streaming === false);
  const streamingOptions = initialOptions.filter((option) => option.streaming === true);

  const { settings, setAutoScan } = useSettings(serverAPI);

  // Random Greetings
  const greetings = [
    "Welcome to NSL!", "Hello, happy gaming!", "Good to see you again!",
    "Wow! You look amazing today...is that a new haircut?",
    "Why couldn't Ubisoft access the servers?... Cuz it couldnt 'Connect'.",
    "I hope you have a blessed day today!", "Just wanted to say, I love you to the sysmoon and back.", "Whats further? Half Life 3 or Gog Galaxy?",
    "I went on a date with a linux jedi once... it didnt work out cuz they kept kept trying to force compatability.",
    "You installed another launcher? ...pff, when are you going to learn bro?", "So how are we wasting our time today?",
    "“For God so loved the world, that he gave his only begotten Son, that whosoever believeth in him should not perish, but have everlasting life.” - John 3:16"
  ];

  const randomGreeting = greetings[Math.floor(Math.random() * greetings.length)];
  // End of Random Greetings

  const { updateInfo } = useUpdateInfo(); // Hook to get update information

  const [isFocused, setIsFocused] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [isManualScanComplete, setIsManualScanComplete] = useState(false);
  const [isAutoScanDisabled, setIsAutoScanDisabled] = useState(false);
  const [isUpdating, setIsUpdating] = useState(false); // Track if an update is in progress
  const [progress, setProgress] = useState({
    percent: 0,
    status: '',
    description: ''
  });

  const handleScanClick = async () => {
    setIsLoading(true); // Set loading state to true
    setIsAutoScanDisabled(true); // Disable the auto-scan toggle
    await scan(() => setIsManualScanComplete(true)); // Perform the scan action and set completion state
    setIsLoading(false); // Set loading state to false
    setIsAutoScanDisabled(false); // Re-enable the auto-scan toggle
  };

  // Handle update button click
  const handleUpdateClick = async () => {
    setIsUpdating(true); // Set updating state
    setProgress({ percent: 0, status: 'updating...', description: 'Please wait while the plugin updates...' });

    // Set a timeout for 3 seconds to restart Steam
    setTimeout(() => {
      console.log("3 seconds passed. Restarting Steam...");
      handleRestartSteam(); // Restart Steam instead of reloading the page
    }, 5000);

    try {
      // Notify the user that the update has started
      const result = await serverAPI.callPluginMethod("install", {
        selected_options: '',
        install_chrome: false,
        separate_app_ids: false,
        start_fresh: false,
        update_proton_ge: false,
        nslgamesaves: false,
        note: false,
        up: true,
      });

      if (result) {
        setProgress({ percent: 100, status: 'Update complete', description: 'The plugin has been updated successfully.' });
        notify.toast("Update complete", "The plugin has been updated successfully.");
      } else {
        setProgress({ percent: 0, status: 'Update failed', description: 'There was an issue with the update.' });
        notify.toast("Update failed", "There was an issue with the update.");
      }
    } catch (error) {
      console.error('Error calling install method on server-side plugin:', error);
      setProgress({ percent: 0, status: 'Update failed', description: 'An error occurred during the update.' });
      notify.toast("Update failed", "An error occurred during the update.");
    }
    setIsUpdating(false); // Reset updating state
  };

  const handleRestartSteam = () => {
    // Restart Steam
    SteamClient.User.StartRestart(false);
  };

  useEffect(() => {
    if (isManualScanComplete) {
      setIsManualScanComplete(false); // Reset the completion state
    }
  }, [isManualScanComplete]);

  return (
    <div className="decky-plugin">
      {/* Conditionally render the red card for update info */}
      {updateInfo && updateInfo.status === "Update available" ? (
        <PanelSectionRow style={{ fontSize: "16px", fontWeight: "bold", marginBottom: "10px", textAlign: "center" }}>
          <div
            style={{
              backgroundColor: "red",
              color: "white",
              padding: "1em",
              borderRadius: "8px",
              boxShadow: "0 4px 8px rgba(0, 0, 0, 0.2)",
              maxWidth: "80%",
              margin: "auto",
              lineHeight: 1.6,
              overflow: "hidden",
              wordWrap: "break-word",  // Word wrap
            }}
          >
            <div>New update found! :) Pressing update will restart Steam.</div>

            <ButtonItem layout="below" onClick={handleUpdateClick} disabled={isUpdating}>
              {isUpdating ? 'Updating...' : 'Update'}
            </ButtonItem>
            <div style={{ marginTop: "0.5em", fontSize: "14px", fontWeight: "normal" }}>
              <div>📌 <strong>Local version:</strong> {updateInfo.local_version}</div>
              <div>🚀 <strong>Latest version:</strong> {updateInfo.github_version}</div>
              <div style={{ marginTop: "0.5em" }}>
                <strong>📝 Patch Notes:</strong>
                <ul style={{
                  textAlign: "left", 
                  marginLeft: "1.5em", 
                  fontSize: "13px", 
                  listStyleType: "none", 
                  padding: "0"
                }}>
                  {Object.entries(updateInfo.patch_notes).map(([category, notes]) => (
                    <li key={category} style={{ marginBottom: "1em" }}>
                      <strong>{category}</strong>
                      <ul style={{ paddingLeft: "20px" }}>
                        {notes.map((note, idx) => (
                          <li key={idx} style={{
                            wordWrap: "break-word", 
                            overflow: "hidden", 
                            textOverflow: "ellipsis"
                          }}>
                            {note.formatted_note}
                          </li>
                        ))}
                      </ul>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        </PanelSectionRow>
      ) : (
        <PanelSectionRow style={{ fontSize: "10px", fontStyle: "italic", fontWeight: "bold", marginBottom: "10px", textAlign: "center" }}>
          <div
            style={{
              display: "inline-block",
              padding: "1em",
              borderRadius: "8px",
              border: "2px solid rgba(255, 255, 255, 0.3)",
              backgroundColor: "white",
              boxShadow: "0 4px 8px rgba(0, 0, 0, 0.2)",
              maxWidth: "80%",
              margin: "auto",
            }}
          >
            {randomGreeting}
          </div>
        </PanelSectionRow>
      )}

      <PanelSection title="Install">
        <ButtonItem layout="below" onClick={() => showModal(<UpdateNotesModal serverAPI={serverAPI} />)}>
          Send Notes!♥
        </ButtonItem>
        <ButtonItem layout="below" onClick={() => showModal(<LauncherInstallModal serverAPI={serverAPI} launcherOptions={launcherOptions} />)}>
          Game Launchers
        </ButtonItem>
        <ButtonItem layout="below" onClick={() => showModal(<StreamingInstallModal serverAPI={serverAPI} streamingOptions={streamingOptions} />)}>
          Streaming Sites
        </ButtonItem>
        <ButtonItem layout="below" onClick={() => showModal(<CustomSiteModal serverAPI={serverAPI} />)}>
          Custom Website Shortcut
        </ButtonItem>
        <ButtonItem layout="below" onClick={() => showModal(<StartFreshModal serverAPI={serverAPI} />)}>
          Start Fresh
        </ButtonItem>
        <ButtonItem layout="below" onClick={() => showModal(<UpdateRestartModal serverAPI={serverAPI} />)}>
          Update UMU/Proton-GE
        </ButtonItem>
        <ButtonItem layout="below" onClick={() => showModal(<RestoreGameSavesModal serverAPI={serverAPI} />)}>
          Restore Game Saves
        </ButtonItem>
      </PanelSection>

      <PanelSection title="Game Scanner">
        <PanelSectionRow style={{ fontSize: "12px", marginBottom: "10px" }}>
          NSL can automatically detect, add or remove shortcuts for the games you install or uninstall in your non-steam launchers in real time. Below, you can enable automatic scanning or trigger a manual scan. During a manual scan only, your game saves will be backed up here: /home/deck/NSLGameSaves.
        </PanelSectionRow>
        
        {/* Moved description of supported launchers */}
        <PanelSectionRow style={{ fontSize: "12px", marginBottom: "10px" }}>
          The NSLGameScanner currently supports Epic Games Launcher, Ubisoft Connect, Gog Galaxy, The EA App, Battle.net, Amazon Games, Itch.io, Legacy Games, VK Play, HoYoPlay, Game Jolt Client, Minecraft Launcher, IndieGala Client, STOVE Client and Humble Bundle as well as Chrome Bookmarks for Xbox Game Pass, GeForce Now & Amazon Luna games and Waydroid Applications.
        </PanelSectionRow>

        <ToggleField
          label="Auto Scan Games"
          checked={settings.autoscan}
          onChange={(value) => {
            setAutoScan(value);
            if (value === true) {
              console.log(`Autoscan is ${settings.autoscan}`);
              autoscan();
            }
          }}
          disabled={isAutoScanDisabled}
        />
        <ButtonItem layout="below" onClick={handleScanClick} disabled={isLoading || settings.autoscan}>
          {isLoading ? 'Scanning...' : 'Manual Scan'}
        </ButtonItem>
      </PanelSection>

      <PanelSection title="For Support and Donations">
        <div
          style={{
            backgroundColor: "transparent",
            display: "flex",
            flexDirection: "column",
            padding: "0.5em",
            width: "95%",
            margin: 0,
          }}
        >
          <div style={{ marginTop: '5px', textAlign: 'center', fontSize: "12px" }}>
            <p>NSL will always be free and open source...but if you're so inclined, all sponsors & donations are humbly appreciated and accepted. Thank you so much!</p>
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '10px' }}>
              <ButtonItem layout="below" onClick={() => window.open('https://www.patreon.com/moraroy', '_blank')}>
                <img src="https://seeklogo.com/images/P/patreon-logo-C0B52F951B-seeklogo.com.png" alt="Patreon" style={{ width: '20px', height: '20px', marginRight: '10px' }} />
                Patreon
              </ButtonItem>
              <ButtonItem layout="below" onClick={() => window.open('https://ko-fi.com/moraroy#checkoutModal', '_blank')}>
                <img src="https://cdn.prod.website-files.com/5c14e387dab576fe667689cf/64f1a9ddd0246590df69e9ef_ko-fi_logo_02-p-500.png" alt="Ko-fi" style={{ width: '20px', height: '20px', marginRight: '10px' }} />
                Ko-fi
              </ButtonItem>
              <ButtonItem layout="below" onClick={() => window.open('https://github.com/sponsors/moraroy', '_blank')}>
                <img src="https://cdn.pixabay.com/photo/2022/01/30/13/33/github-6980894_1280.png" alt="GitHub" style={{ width: '20px', height: '20px', marginRight: '10px' }} />
                GitHub
              </ButtonItem>
              <ButtonItem
                layout="below"
                onClick={() => window.open('https://github.com/moraroy/NonSteamLaunchers-On-Steam-Deck', '_blank')}
              >
                click here for more info!
              </ButtonItem>
            </div>
          </div>
        </div>
      </PanelSection>
    </div>
  );
};

export default definePlugin((serverApi: ServerAPI) => {
  autoscan();
  notify.setServer(serverApi);
  return {
    title: <div className={staticClasses.Title}>NonSteamLaunchers</div>,
    alwaysRender: true,
    content: (
      <Content serverAPI={serverApi} />
    ),
    icon: <RxRocket />,
  };
});