import {
    DialogHeader,
    ToggleField,
    DialogBodyText,
    DialogBody,
    DialogButton,
    Focusable,
    ServerAPI,
    ModalRoot,
    SteamSpinner,
    ProgressBarWithInfo
} from "decky-frontend-lib";
import { useState, VFC, useEffect, useRef } from "react";
import { notify } from "../../hooks/notify";
import { useSettings } from "../../hooks/useSettings";
import { scan, autoscan } from "../../hooks/scan";
import { useLogUpdates } from "../../hooks/useLogUpdates";

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

    useEffect(() => {
        const selectedLaunchers = options.filter(option => option.enabled && !option.streaming);
        if (selectedLaunchers.length > 0) {
            setCurrentLauncher(selectedLaunchers[0]);
        }
    }, [options]);

    useEffect(() => {
        if (logContainerRef.current) {
            logContainerRef.current.scrollTop = logContainerRef.current.scrollHeight;
        }
    }, [log]);

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
                update_proton_ge: false
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
<ModalRoot onCancel={cancelOperation}>
    <DialogHeader>
        {`${operation}ing Game Launchers`}
    </DialogHeader>
    <DialogBodyText>Selected options: {options.filter(option => option.enabled).map(option => option.label).join(', ')}</DialogBodyText>
    <DialogBody>
        <SteamSpinner />
        <div style={{ display: 'flex', alignItems: 'center' }}>
            <div ref={logContainerRef} style={{ flex: 1, marginRight: '10px', fontSize: 'small', whiteSpace: 'pre-wrap', overflowY: 'auto', maxHeight: '50px', height:'100px' }}>
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
            <img src={currentLauncher.urlimage} alt="Overlay" style={{ ...fadeStyle, opacity: 0.5 }} />
        )}
        <DialogButton onClick={cancelOperation} style={{ width: '25px', margin: 0, padding: '10px' }}>
            Back
        </DialogButton>
    </DialogBody>
</ModalRoot> :
<ModalRoot onCancel={closeModal}>
    <DialogHeader>
        Select Game Launchers
    </DialogHeader>
    <DialogBodyText>Here you choose your launchers you want to install and let NSL do the rest. Once installed, they will be added your library!</DialogBodyText>
    <DialogBody>
        {launcherOptions.map(({ name, label }) => (
            <ToggleField
                key={name}
                label={label}
                checked={options.find(option => option.name === name)?.enabled ? true : false}
                onChange={(value) => handleToggle(name, value)}
            />
        ))}
    </DialogBody>
    <p style={{ fontSize: 'small', marginTop: '16px' }}>
        Note: When installing a launcher, the latest Proton-GE will attempt to be installed. If your launchers don't start, make sure force compatibility is checked, shortcut properties are right, and your steam files are updated. Remember to also edit your controller layout configurations if necessary! If all else fails, restart your steam deck manually.
        </p>
        <p style={{ fontSize: 'small', marginTop: '16px' }}>
        Note²: Some games won't run right away using NSL. Due to easy anti-cheat or quirks, you may need to manually tinker to get some games working. NSL is simply another way to play! Happy Gaming!♥
        </p>
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
};