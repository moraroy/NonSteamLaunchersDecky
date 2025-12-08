import {
    DialogHeader,
    DialogBodyText,
    DialogBody,
    ServerAPI,
    ConfirmModal,
    ModalRoot,
    SteamSpinner,
    ProgressBarWithInfo
} from "decky-frontend-lib";
import { useState, VFC } from "react";
import { notify } from "../../hooks/notify";

type startFreshModalProps = {
    closeModal?: () => void,
    serverAPI: ServerAPI
};

/**
* The modal for selecting launchers.
*/
export const StartFreshModal: VFC<startFreshModalProps> = ({ closeModal, serverAPI }) => {

    const [progress, setProgress] = useState({ percent: 0, status: '', description: '' });
    const [firstConfirm, setFirstConfirm] = useState(false);

    const handleStartFreshClick = async () => {
        console.log('handleStartFreshClick called');
        setProgress({ percent: 0, status: 'wiping...if there is enough toilet paper...', description: '' });
        try {
            const result = await serverAPI.callPluginMethod("install", {
                selected_options: '',
                install_chrome: false,
                separate_app_ids: false,
                start_fresh: true,
                update_proton_ge: false,
                nslgamesaves: false,
                note: false,
                up: false,
            });

            if (result) {
                setProgress({ percent: 100, status: 'NSL has been wiped. Remember to delete your shortcuts!', description: '' });
                notify.toast("...there was...NSL has been wiped.", "Remember to delete your shortcuts!");
            } else {
                setProgress({ percent: 100, status: 'wipe failed.', description: '' });
                notify.toast("...there wasn't...Dingleberries!", "NSL failed to wipe. Check your logs.");
            }
        } catch (error) {
            setProgress({ percent: 100, status: 'wipe failed.', description: '' });
            notify.toast("NSL Wipe Failed", "Non Steam Launchers failed to wipe. Check your logs.");
            console.error('Error calling _main method on server-side plugin:', error);
        }
        closeModal!();
    };

    return ((progress.status !== '' && progress.percent < 100) ?
        <ModalRoot>
            <DialogHeader>Starting Fresh</DialogHeader>
            <DialogBodyText>Removing all launchers and installed games from NonSteamLaunchers</DialogBodyText>
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
        </ModalRoot> :
        firstConfirm ?
            <ConfirmModal
                strTitle="Oops... That Might Have Been a Mistake"
                strDescription="This is your last chance! By continuing, you will be totally deleting the prefixes, which include the launchers and the games you downloaded, as well as your games. If you aren't sure if your game saves are backed up or if you have downloaded a very large game and would not like to have to re-download, please DO NOT CONTINUE. Everything will be wiped!"
                strOKButtonText="Yes, I'm sure!"
                strCancelButtonText="No, go back!"
                onOK={handleStartFreshClick}
                onCancel={() => setFirstConfirm(false)}
            /> :
            <ConfirmModal
                strTitle="Are You Sure?"
                strDescription="Pressing Start Fresh will essentially uninstall NSL. It will delete and wipe all installed launchers and their games along with your game saves and NSL files. This is irreversible! You'll need to manually remove any shortcuts created."
                strOKButtonText="Yes, wipe!"
                strCancelButtonText="No, go back!"
                onOK={() => setFirstConfirm(true)}
                onCancel={closeModal}
            />
    );
};