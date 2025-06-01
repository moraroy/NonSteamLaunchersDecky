import {
    DialogHeader,
    DialogBodyText,
    DialogBody,
    ConfirmModal,
    ModalRoot,
    SteamSpinner,
    ProgressBarWithInfo
} from "decky-frontend-lib";
import { useState, VFC } from "react";
import { notify } from "../../hooks/notify";

type UpdateNotesModalProps = {
    closeModal?: () => void,
    serverAPI: ServerAPI
};

export const UpdateNotesModal: VFC<UpdateNotesModalProps> = ({ closeModal, serverAPI }) => {
    const [progress, setProgress] = useState({ percent: 0, status: '', description: '' });
    const [showRestartModal, setShowRestartModal] = useState(false);

    const handleSendNotesClick = async () => {
        console.log('handleSendNotesClick called');
        setProgress({ percent: 0, status: 'Sending notes...', description: '' });
        try {
            const result = await serverAPI.callPluginMethod("install", {
                selected_options: '',
                install_chrome: false,
                separate_app_ids: false,
                start_fresh: false,
                update_proton_ge: false,
                nslgamesaves: false,
                note: true,
                up: false,
            });
            if (result) {
                setProgress({ percent: 100, status: 'Notes sent successfully!', description: '' });
                notify.toast("Notes Sent", "Your notes have been successfully sent to the community.");
                setShowRestartModal(true);
            } else {
                setProgress({ percent: 100, status: 'Failed to send notes.', description: '' });
                notify.toast("Sending Failed", "Failed to send notes. Please check the logs for details.");
            }
        } catch (error) {
            setProgress({ percent: 100, status: 'Failed to send notes.', description: '' });
            notify.toast("Sending Failed", "An error occurred while sending your notes. Check the logs.");
            console.error('Error calling note method on server-side plugin:', error);
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
                    <DialogHeader>Sending Your Notes!</DialogHeader>
                    <DialogBodyText>Please wait while your notes are being sent to the community...</DialogBodyText>
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
                    strDescription="Your notes have been sent successfully! To see the notes in the community, Steam must be restarted. Would you like to restart Steam now?"
                    strOKButtonText="Restart Steam"
                    strCancelButtonText="Back"
                    onOK={handleRestartSteam}
                    onCancel={() => setShowRestartModal(false)}
                />
            ) : (
                <ConfirmModal
                    strTitle="Send Your Note!"
                    strDescription={`Welcome to #noteSteamLaunchers! By creating a note for your non-Steam game and using the "#nsl" tag at the start of your note, you can share it with the community. All notes from participants will be visible in the "NSL Community Notes" for that specific game. Feel free to give this experimental feature a try! Would you like to send your #nsl note to the community and receive some notes back in return?`}
                    strOKButtonText="Send Notes"
                    strCancelButtonText="Cancel"
                    onOK={handleSendNotesClick}
                    onCancel={closeModal}
                />
            )}
        </>
    );
};
