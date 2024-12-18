import {
  DialogHeader,
  ToggleField,
  DialogBodyText,
  DialogBody,
  DialogButton,
  Focusable,
  ServerAPI,
  SteamSpinner,
  ModalRoot,
  ProgressBarWithInfo
} from "decky-frontend-lib";
import { useState, VFC, useRef } from "react";
import { notify } from "../../hooks/notify";
import { useSettings } from "../../hooks/useSettings";
import { scan, autoscan } from "../../hooks/scan";
import { useLogUpdates } from "../../hooks/useLogUpdates";
import { useLauncherStatus } from "../../hooks/useLauncherStatus";

type LauncherInstallModalProps = {
  closeModal?: () => void,
  launcherOptions: {
    name: string;
    label: string;
    URL: string;
    streaming: boolean;
    enabled: boolean;
    urlimage: string;
  }[],
  serverAPI: ServerAPI
};

export const LauncherInstallModal: VFC<LauncherInstallModalProps> = ({ closeModal, launcherOptions, serverAPI }) => {
  const { launcherStatus, error, loading } = useLauncherStatus();  // Use the hook to get launcher status
  const [progress, setProgress] = useState({ percent: 0, status: '', description: '' });
  const { settings, setAutoScan } = useSettings(serverAPI);
  const [options, setOptions] = useState(launcherOptions);
  const [separateAppIds, setSeparateAppIds] = useState(false);
  const [operation, setOperation] = useState("");
  const [showLog, setShowLog] = useState(false);
  const [triggerLogUpdates, setTriggerLogUpdates] = useState(false);
  const log = useLogUpdates(triggerLogUpdates);
  const [currentLauncher, setCurrentLauncher] = useState<typeof launcherOptions[0] | null>(null);
  const logContainerRef = useRef<HTMLDivElement>(null);

  // Pagination state
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 7;

  const indexOfLastLauncher = currentPage * itemsPerPage;
  const indexOfFirstLauncher = indexOfLastLauncher - itemsPerPage;
  const currentLaunchers = launcherOptions.slice(indexOfFirstLauncher, indexOfLastLauncher);

  const handleToggle = (changeName: string, changeValue: boolean) => {
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

  const handleSeparateAppIdsToggle = (value: boolean) => {
    setSeparateAppIds(value);
  };

  const handleInstallClick = async (operation: string) => {
    setOperation(operation);
    setShowLog(true);
    setTriggerLogUpdates(true);

    // Add a small delay to ensure WebSocket connection is established
    await new Promise(resolve => setTimeout(resolve, 100));

    const selectedLaunchers = options.filter(option => option.enabled && !option.streaming);
    let i = 0;
    let previousAutoScan = settings.autoscan;
    for (const launcher of selectedLaunchers) {
      if (!launcher.streaming) {
        setAutoScan(false);
        const launcherParam: string = (launcher.name.charAt(0).toUpperCase() + launcher.name.slice(1));
        setCurrentLauncher(launcher);

        // Reset log updates for each launcher
        setTriggerLogUpdates(false);
        await new Promise(resolve => setTimeout(resolve, 500));
        setTriggerLogUpdates(true);

        await installLauncher(launcherParam, launcher.label, i, operation);
      }
      i++;
    }
    scan();
    setAutoScan(previousAutoScan);
    if (settings.autoscan) { autoscan(); }
  };

  const installLauncher = async (launcher: string, launcherLabel: string, index: number, operation: string) => {
    const total = options.filter(option => option.enabled).length;
    const startPercent = index === 0 ? 0 : index / total * 100;
    const endPercent = (index + 1) / total * 100;
    setProgress({
      percent: startPercent,
      status: `${operation}ing Launcher ${index + 1} of ${total}`,
      description: `${launcherLabel}`
    });
    try {
      const result = await serverAPI.callPluginMethod("install", {
        selected_options: launcher,
        operation: operation,
        install_chrome: false,
        separate_app_ids: separateAppIds,
        start_fresh: false,
        update_proton_ge: false,
        nslgamesaves: false
      });

      if (result) {
        setProgress({ percent: endPercent, status: `${operation} Selection ${index + 1} of ${total}`, description: `${launcher}` });
        notify.toast(`Launcher ${operation}ed`, `${launcherLabel} was ${operation.toLowerCase()}ed successfully!`);
      } else {
        setProgress({ percent: endPercent, status: `${operation} selection ${index + 1} of ${total} failed`, description: `${operation} ${launcher} failed. See logs.` });
        notify.toast(`${operation} Failed`, `${launcherLabel} was not ${operation.toLowerCase()}ed.`);
      }
    } catch (error) {
      setProgress({ percent: endPercent, status: `Installing selection ${index + 1} of ${total} failed`, description: `Installing ${launcher} failed. See logs.` });
      notify.toast("Install Failed", `${launcherLabel} was not installed.`);
      console.error('Error calling _main method on server-side plugin:', error);
    }
  };

  const cancelOperation = () => {
    setProgress({ percent: 0, status: '', description: '' });
    setShowLog(false);
    setTriggerLogUpdates(false);
    setCurrentLauncher(null);
  };

  // Pulsating animation style for lights
  const pulseStyle = (offset: number) => ({
    width: '12px',
    height: '12px',
    borderRadius: '50%',
    marginRight: '10px',
    backgroundColor: 'gray', // Neutral color while loading
    opacity: 0.5 + Math.sin((Date.now() + offset) / 300) * 0.5, // Pulsing effect via opacity
    transition: 'opacity 0.3s ease', // Smooth transition for opacity change
  });

  const nextPage = () => {
    if (currentPage * itemsPerPage < launcherOptions.length) {
      setCurrentPage(prevPage => prevPage + 1);
    }
  };

  const prevPage = () => {
    if (currentPage > 1) {
      setCurrentPage(prevPage => prevPage - 1);
    }
  };

  // **Only remove the spinner here when loading status is true**
  if (loading) {
    return (
      <ModalRoot onCancel={closeModal}>
        <DialogHeader>Loading Launcher Status...</DialogHeader>
        <DialogBodyText>Checking installed launchers...</DialogBodyText>
        <DialogBody>
          <div style={{ display: 'flex', alignItems: 'center' }}>
            <span style={pulseStyle(0)} />
            <span style={pulseStyle(100)} />
            <span style={pulseStyle(200)} />
          </div>
        </DialogBody>
      </ModalRoot>
    );
  }

  if (error) {
    return (
      <ModalRoot onCancel={closeModal}>
        <DialogHeader>Error</DialogHeader>
        <DialogBodyText>{error}</DialogBodyText>
        <DialogBody>
          <DialogButton onClick={closeModal}>Close</DialogButton>
        </DialogBody>
      </ModalRoot>
    );
  }

  return (
    (progress.status !== '' && progress.percent < 100) ? (
      <ModalRoot onCancel={cancelOperation}>
        <DialogHeader>{`${operation}ing Game Launchers`}</DialogHeader>
        <DialogBodyText>Selected options: {options.filter(option => option.enabled).map(option => option.label).join(', ')}</DialogBodyText>
        <DialogBody>
          <SteamSpinner />
          <div style={{ display: 'flex', alignItems: 'center' }}>
            <div ref={logContainerRef} style={{ flex: 1, marginRight: '10px', fontSize: 'small', whiteSpace: 'pre-wrap', overflowY: 'auto', maxHeight: '50px', height: '100px' }}>
              {showLog && log}
            </div>
            <ProgressBarWithInfo
              layout="inline"
              bottomSeparator="none"
              sOperationText={progress.status}
              description={progress.description}
              nProgress={progress.percent}
              indeterminate={true}
            />
          </div>
          {currentLauncher && (
            <img src={currentLauncher.urlimage} alt="Overlay" style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', opacity: 0.5 }} />
          )}
          <DialogButton onClick={cancelOperation} style={{ width: '25px', margin: 0, padding: '10px' }}>
            Back
          </DialogButton>
        </DialogBody>
      </ModalRoot>
    ) : (
      <ModalRoot onCancel={closeModal}>
        <DialogHeader>Select Game Launchers</DialogHeader>
        <DialogBodyText>Here you choose your launchers you want to install and let NSL do the rest. Once installed, they will be added to your library!</DialogBodyText>
        <DialogBody>
          {currentLaunchers.map(({ name, label }) => (
            <div key={name} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div style={{ display: 'flex', alignItems: 'center' }}>
                <span>{label}</span>
                <span
                  style={{
                    width: '12px',
                    height: '12px',
                    borderRadius: '50%',
                    marginLeft: '10px',
                    backgroundColor:
                      launcherStatus?.installedLaunchers.includes(name) ? 'green' : 'red',
                  }}
                />
              </div>
              <ToggleField
                checked={options.find(option => option.name === name)?.enabled ? true : false}
                onChange={(value) => handleToggle(name, value)}
              />
            </div>
          ))}
          
          {/* Helpful Notes moved above the pagination controls */}
          <DialogBodyText style={{ fontSize: 'small', marginTop: '16px' }}>
            <b>Note:</b> When installing a launcher, the latest UMU/Proton-GE will attempt to be installed. If your launchers don't start, make sure force compatibility is checked, shortcut properties are right, and your steam files are updated. Remember to also edit your controller layout configurations if necessary! If all else fails, restart your steam deck manually.
          </DialogBodyText>
          <DialogBodyText style={{ fontSize: 'small', marginTop: '16px' }}>
            <b>Note²:</b> Some games won't run right away using NSL. Due to easy anti-cheat or quirks, you may need to manually tinker to get some games working. NSL is simply another way to play! Happy Gaming!♥
          </DialogBodyText>
        </DialogBody>

        {/* Pagination controls */}
        <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '10px' }}>
          <DialogButton onClick={prevPage} disabled={currentPage === 1}>Previous</DialogButton>
          <DialogButton onClick={nextPage} disabled={currentPage * itemsPerPage >= launcherOptions.length}>Next</DialogButton>
        </div>

        <Focusable>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div style={{ display: 'flex', alignItems: 'center' }}>
              <DialogButton
                style={{ width: "fit-content" }}
                onClick={() => handleInstallClick("Install")}
                disabled={options.every(option => option.enabled === false)}
              >
                Install
              </DialogButton>
              <DialogButton
                style={{ width: "fit-content", marginLeft: "10px", marginRight: "10px" }}
                onClick={() => handleInstallClick("Uninstall")}
                disabled={options.every(option => option.enabled === false)}
              >
                Uninstall
              </DialogButton>
            </div>
            <ToggleField label="Separate Launcher Folders" checked={separateAppIds} onChange={handleSeparateAppIdsToggle} />
          </div>
        </Focusable>
      </ModalRoot>
    )
  );
};