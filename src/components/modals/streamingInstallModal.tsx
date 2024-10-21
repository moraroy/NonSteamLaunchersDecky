import {
  ModalRoot,
  ToggleField,
  DialogHeader,
  DialogBodyText,
  DialogBody,
  ServerAPI,
  SteamSpinner,
  ProgressBarWithInfo,
  Focusable,
  DialogButton
} from "decky-frontend-lib";
import { VFC, useState } from "react";
import { Sites, installSite } from "../../hooks/installSites";

type StreamingInstallModalProps = {
  closeModal?: () => void,
  streamingOptions: {
      name: string;
      label: string;
      URL: string;
      streaming: boolean;
      enabled: boolean;
      urlimage: string; // Add this line
  }[],
  serverAPI: ServerAPI
};

/**
 * The modal for selecting launchers.
 */
export const StreamingInstallModal: VFC<StreamingInstallModalProps> = ({closeModal, streamingOptions, serverAPI}) => {

  const [progress, setProgress] = useState({ percent:0, status:'', description: '' });
  const [options, setOptions ] = useState(streamingOptions);
  const [currentStreamingSite, setCurrentStreamingSite] = useState<typeof streamingOptions[0] | null>(null);

  const handleInstallClick = async () => {
    console.log('handleInstallClick called');
    const selectedStreamingSites: Sites = options
        .filter(option => option.enabled && option.streaming)
        .map(option => {
          return {
            siteName: option.label,
            siteURL: option.URL
          }   
        })
    if (selectedStreamingSites.length > 0) {
      const total = (options.filter(option => option.enabled && option.streaming).length)
      const startPercent = 0
      setProgress({ 
        percent: startPercent, 
        status:`Installing ${selectedStreamingSites.length} Streaming Sites`, 
        description: `${selectedStreamingSites.map(site => site.siteName).join(', ')}`
      });
      setCurrentStreamingSite(options.find(option => option.enabled && option.streaming) || null);
      await installSite(selectedStreamingSites, serverAPI, { setProgress }, total)
    }
   }

  const handleToggle = (changeName:string, changeValue: boolean) => {
      const newOptions = options.map(option => {
        if (option.name === changeName) {
          return {
            ...option,
            enabled: changeValue,
          };
        } else {
          return option;
        }
      });
      setOptions(newOptions);
     };

  const cancelOperation = () => {
    setProgress({ percent: 0, status: '', description: '' });
    setCurrentStreamingSite(null);
  };

  const fadeStyle = {
    position: 'absolute',
    top: 0,
    left: 0,
    width: '100%',
    height: '100%',
    opacity: 1,
    pointerEvents: 'none',
    transition: 'opacity 1s ease-in-out'
  };

  return ((progress.status != '' && progress.percent < 100) ?
  <ModalRoot>
    <DialogHeader>
        Installing Streaming Sites
    </DialogHeader>
    <DialogBodyText>Selected options: {options.filter(option => option.enabled).map(option => option.label).join(', ')}</DialogBodyText>
    <DialogBody>
        <SteamSpinner/>
        <ProgressBarWithInfo
            layout="inline"
            bottomSeparator="none"
            sOperationText={progress.status}
            description={progress.description}
            nProgress={progress.percent}
        />
        {currentStreamingSite && (
            <img src={currentStreamingSite.urlimage} alt="Overlay" style={{ ...fadeStyle, opacity: 0.5 }} />
        )}
        <DialogButton onClick={cancelOperation} style={{ width: '25px' }}>Back</DialogButton>
    </DialogBody>
  </ModalRoot>:
    <ModalRoot
      onCancel = {closeModal}
    >
      <DialogHeader>
          Install Game/Media Streaming Sites
      </DialogHeader>
      <DialogBodyText>NSL will install and use Chrome to launch these sites. Non-Steam shortcuts will be created for each selection. Before installing, toggle Auto Scan "on" for these.</DialogBodyText>
      <DialogBody>
        {streamingOptions.map(({ name, label }) => (
            <ToggleField
            label={label}
            checked={options.find(option => option.name === name)?.enabled ? true : false}
            onChange={(value) => handleToggle(name, value)}
            />
        ))}
      </DialogBody>
      <p></p>
      <Focusable style={{ display: "flex", alignItems: "center", gap: "10px" }}>
        <DialogButton
          style={{ width: "fit-content" }}
          onClick={handleInstallClick}
          disabled={options.every(option => option.enabled === false)}
        >
          Install
        </DialogButton>
        <DialogBodyText style={{ fontSize: "small" }}>Note: NSL will attempt to install Google Chrome. Be sure that Google Chrome is installed from the Discover Store in Desktop Mode first or from SteamOS.</DialogBodyText>
      </Focusable>
    </ModalRoot>
  )
};