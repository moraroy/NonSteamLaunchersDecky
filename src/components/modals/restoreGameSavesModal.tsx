import {
  DialogHeader,
  DialogBodyText,
  DialogBody,
  ServerAPI,
  ModalRoot,
  SteamSpinner,
  ProgressBarWithInfo,
  DialogButton
} from "decky-frontend-lib";
import { useState, VFC } from "react";
import { notify } from "../../hooks/notify";

type RestoreGameSavesModalProps = {
  closeModal?: () => void,
  serverAPI: ServerAPI
};

export const RestoreGameSavesModal: VFC<RestoreGameSavesModalProps> = ({ closeModal, serverAPI }) => {
  const [progress, setProgress] = useState({ percent: 0, status: '', description: '' });

  const handleRestoreClick = async () => {
    console.log('handleRestoreClick called');
    setProgress({ percent: 0, status: 'Restoring game saves...', description: '' });
    try {
      const result = await serverAPI.callPluginMethod("install", {
        selected_options: '',
        install_chrome: false,
        separate_app_ids: false,
        start_fresh: false,
        update_proton_ge: false,
        nslgamesaves: true
      });

      if (result) {
        setProgress({ percent: 100, status: 'Game saves restored successfully!', description: '' });
        notify.toast("Game saves restored successfully!", "Your game saves have been restored.");
      } else {
        setProgress({ percent: 100, status: 'Restore failed.', description: '' });
        notify.toast("Restore failed", "Failed to restore game saves. Check your logs.");
      }
    } catch (error) {
      setProgress({ percent: 100, status: 'Restore failed.', description: '' });
      notify.toast("Restore Failed", "Failed to restore game saves. Check your logs.");
      console.error('Error calling restore method on server-side plugin:', error);
    }
    closeModal!();
  };

  return ((progress.status !== '' && progress.percent < 100) ?
    <ModalRoot>
      <DialogHeader>Restoring Game Saves</DialogHeader>
      <DialogBodyText>Restoring your game save backups...</DialogBodyText>
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
        <DialogButton onClick={closeModal} style={{ width: '25px' }}>
          Cancel
        </DialogButton>
      </DialogBody>
    </ModalRoot> :
    <ModalRoot style={{ width: '600px' }}>
      <DialogHeader>Restore Game Save Backups</DialogHeader>
      <DialogBody>
        <DialogBodyText style={{ fontSize: '14px' }}>This feature will restore all your game save backups all at once, currently only for the default NonSteamLaunchers prefix.</DialogBodyText>
        <DialogBodyText style={{ fontSize: '14px' }}>
          <strong>Ensure all necessary launchers are installed, but do not download the games,</strong> as this will avoid local conflicts. Only continue if you have wiped everything using Start Fresh and you know for a fact that your game saves are backed up at /home/deck/NSLGameSaves.
        </DialogBodyText>
        <DialogBodyText style={{ fontSize: '14px' }}>Some games don't have local save backups:</DialogBodyText>
        <ul>
          <li style={{ fontSize: '12px' }}>NSL uses Ludusavi to backup and restore your local game saves.</li>
          <li style={{ fontSize: '12px' }}>Some launchers handle local and cloud saves themselves so this will vary on a game to game basis.</li>
          <li style={{ fontSize: '12px', wordWrap: 'break-word' }}>Ludusavi may need manual configuration here if more paths are needed: /home/deck/.var/app/com.github.mtkennerly.ludusavi/config/ludusavi/NSLconfig/config.yaml</li>
        </ul>
        <DialogBodyText style={{ fontSize: '14px' }}>Press restore when ready.</DialogBodyText>
      </DialogBody>
      <DialogBody>
        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
          <DialogButton onClick={handleRestoreClick}>
            Restore Game Saves
          </DialogButton>
          <DialogButton onClick={closeModal}>
            Cancel
          </DialogButton>
        </div>
      </DialogBody>
    </ModalRoot>
  );
};
