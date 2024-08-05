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
import { useState, useEffect, VFC } from "react";
import { notify } from "../../hooks/notify";
import { useSettings } from "../../hooks/useSettings";
import { scan, autoscan } from "../../hooks/scan";

type LauncherInstallModalProps = {
    closeModal?: () => void,
    launcherOptions: {
        name: string;
        label: string;
        URL: string;
        streaming: boolean;
        enabled: boolean;
    }[],
    serverAPI: ServerAPI
};

/**
* The modal for selecting launchers.
*/
export const LauncherInstallModal: VFC<LauncherInstallModalProps> = ({ closeModal, launcherOptions, serverAPI }) => {

    const [progress, setProgress] = useState({ percent: 0, status: '', description: '' });
    const { settings, setAutoScan } = useSettings(serverAPI);
    const [options, setOptions] = useState(launcherOptions);
    const [separateAppIds, setSeparateAppIds] = useState(false);
    const [operation, setOperation] = useState("");
    const [logMessages, setLogMessages] = useState<string[]>([]);

    useEffect(() => {
        const ws = new WebSocket('ws://localhost:8675/logUpdates');
        ws.onmessage = (event) => {
            setLogMessages(prevMessages => [...prevMessages, event.data]);
        };
        return () => {
            ws.close();
        };
    }, []);

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
        console.log('handleInstallClick called');
        const selectedLaunchers = options
            .filter(option => option.enabled && !option.streaming)
        console.log(`Selected options: ${selectedLaunchers.join(', ')}`);
        let i = 0
        let previousAutoScan = settings.autoscan
        for (const launcher of selectedLaunchers) {
            if (!launcher.streaming) {
                setAutoScan(false)
                console.log(`Calling ${operation} launcher method for ${launcher}`)
                const launcherParam: string = (launcher.name.charAt(0).toUpperCase() + launcher.name.slice(1))
                await installLauncher(launcherParam, launcher.label, i, operation)
            }
            i++
        }
        scan()
        setAutoScan(previousAutoScan)
        if (settings.autoscan) { autoscan() }
    }

    const installLauncher = async (launcher: string, launcherLabel: string, index: number, operation: string) => {
        const total = options.filter(option => option.enabled).length
        const startPercent = index === 0 ? 0 : index / total * 100
        const endPercent = (index + 1) / total * 100
        console.log(`${operation} Launcher: ${launcherLabel}, Index: ${index}, StartPercent: ${startPercent}, EndPercent: ${endPercent}`)
        setProgress({
            percent: startPercent,
            status: `${operation}ing Launcher ${index + 1} of ${total}`,
            description: `${launcherLabel}`
        })
        try {
            const result = await serverAPI.callPluginMethod("install", {
                selected_options: launcher,
                operation: operation,
                install_chrome: false,
                separate_app_ids: separateAppIds,
                start_fresh: false // Pass true for the start_fresh parameter
            });

            if (result) {
                setProgress({ percent: endPercent, status: `${operation} Selection ${index + 1} of ${total}`, description: `${launcher}` });
                notify.toast(`Launcher ${operation}ed`, `${launcherLabel} was ${operation.toLowerCase()}ed successfully!`)
            } else {
                setProgress({ percent: endPercent, status: `${operation} selection ${index + 1} of ${total} failed`, description: `${operation} ${launcher} failed. See logs.` });
                notify.toast(`${operation} Failed`, `${launcherLabel} was not ${operation.toLowerCase()}ed.`)
            }
        } catch (error) {
            setProgress({ percent: endPercent, status: `Installing selection ${index + 1} of ${total} failed`, description: `Installing ${launcher} failed. See logs.` });
            notify.toast("Install Failed", `${launcherLabel} was not installed.`)
            console.error('Error calling _main method on server-side plugin:', error);
        }
    };

    return ((progress.status != '' && progress.percent < 100) ?
        <ModalRoot>
            <DialogHeader>
                {`${operation}ing Game Launchers`}
            </DialogHeader>
            <DialogBodyText>Selected options: {options.filter(option => option.enabled).map(option => option.label).join(', ')}</DialogBodyText>
            <DialogBody>
                <SteamSpinner />
                <ProgressBarWithInfo
                    layout="inline"
                    bottomSeparator="none"
                    sOperationText={progress.status}
                    description={progress.description}
                    nProgress={progress.percent}
                />
                <div style={{ marginTop: '20px', maxHeight: '200px', overflowY: 'auto', backgroundColor: '#f0f0f0', padding: '10px', borderRadius: '5px' }}>
                    {logMessages.map((message, index) => (
                        <p key={index} style={{ fontSize: 'small', margin: '5px 0' }}>{message}</p>
                    ))}
                </div>
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
                        label={label}
                        checked={options.find(option => option.name === name)?.enabled ? true : false}
                        onChange={(value) => handleToggle(name, value)}
                    />
                ))}
            </DialogBody>
            <p style={{ fontSize: 'small', marginTop: '20px' }}>
                Note: If your launchers don't start, make sure force compatibility is checked, shortcut properties are right and your steam files are updated. Remember to also edit your controller layout configurations if necessary! If all else fails, restart your steam deck manually.
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