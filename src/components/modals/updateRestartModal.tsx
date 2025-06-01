import { DialogHeader, DialogBodyText, DialogBody, ConfirmModal, ModalRoot, SteamSpinner, ProgressBarWithInfo } from "decky-frontend-lib";
import { useState, VFC } from "react";
import { notify } from "../../hooks/notify";

type UpdateRestartModalProps = {
    closeModal?: () => void,
    serverAPI: ServerAPI
};

export const UpdateRestartModal: VFC<UpdateRestartModalProps> = ({ closeModal, serverAPI }) => {
    const [progress, setProgress] = useState({ percent: 0, status: '', description: '' });
    const [showRestartModal, setShowRestartModal] = useState(false);

    const handleUpdateProtonGEClick = async () => {
        console.log('handleUpdateProtonGEClick called');
        setProgress({ percent: 0, status: 'updating...', description: '' });
        try {
            const result = await serverAPI.callPluginMethod("install", {
                selected_options: '',
                install_chrome: false,
                separate_app_ids: false,
                start_fresh: false,
                update_proton_ge: true,
                nslgamesaves: false,
                note: false,
                up: false,
            });
            if (result) {
                setProgress({ percent: 100, status: 'Proton GE updated successfully.', description: '' });
                notify.toast("Proton GE Updated", "Proton GE has been updated successfully.");
                setShowRestartModal(true);
            } else {
                setProgress({ percent: 100, status: 'Update failed.', description: '' });
                notify.toast("Update Failed", "Proton GE update failed. Check your logs.");
            }
        } catch (error) {
            setProgress({ percent: 100, status: 'Update failed.', description: '' });
            notify.toast("Update Failed", "Proton GE update failed. Check your logs.");
            console.error('Error calling update_proton_ge method on server-side plugin:', error);
        }
    };

    const handleRestartSteam = () => {
        SteamClient.User.StartRestart(false);
        setShowRestartModal(false);
        closeModal!();
    };

    return (
        <>
            {progress.status !== '' && progress.percent < 100 ? (
                <ModalRoot>
                    <DialogHeader>Updating Proton GE</DialogHeader>
                    <DialogBodyText>Updating Proton GE to the latest version. Please wait...</DialogBodyText>
                    <DialogBody>
                        <SteamSpinner />
                        <ProgressBarWithInfo
                            layout="inline"
                            bottomSeparator="none"
                            sOperationText={progress.status}
                            description={progress.description}
                            nProgress={progress.percent}
                            indeterminate={true}
                        />
                    </DialogBody>
                </ModalRoot>
            ) : showRestartModal ? (
                <ConfirmModal
                    strTitle="Restart Steam"
                    strDescription="Updating Proton GE requires a restart of Steam for the changes to take effect. Would you like to restart Steam now?"
                    strOKButtonText="Restart"
                    strCancelButtonText="Back"
                    onOK={handleRestartSteam}
                    onCancel={() => setShowRestartModal(false)}
                />
            ) : (
                <ConfirmModal
                    strTitle="Update Proton GE"
                    strDescription="Would you like to update Proton GE to the latest version?"
                    strOKButtonText="Update"
                    strCancelButtonText="Cancel"
                    onOK={handleUpdateProtonGEClick}
                    onCancel={closeModal}
                />
            )}
        </>
    );
};
