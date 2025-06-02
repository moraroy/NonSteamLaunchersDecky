import {
  ConfirmModal,
  ToggleField,
  DialogBodyText,
  DialogBody,
  ServerAPI,
  SteamSpinner,
  ProgressBarWithInfo,
  Focusable,
  DialogButton
} from "decky-frontend-lib";
import { VFC, useState, useEffect } from "react";
import { Sites, installSite } from "../../hooks/installSites";

type StreamingInstallModalProps = {
  closeModal?: () => void,
  streamingOptions: {
    name: string;
    label: string;
    URL: string;
    streaming: boolean;
    enabled: boolean;
    urlimage: string;
  }[],
  serverAPI: ServerAPI
};

export const StreamingInstallModal: VFC<StreamingInstallModalProps> = ({ closeModal, streamingOptions, serverAPI }) => {

  const [progress, setProgress] = useState({ percent: 0, status: '', description: '' });
  const [options, setOptions] = useState(streamingOptions);
  const [currentStreamingSites, setCurrentStreamingSites] = useState<typeof streamingOptions[0][]>([]);

  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 7;
  const indexOfLastSite = currentPage * itemsPerPage;
  const indexOfFirstSite = indexOfLastSite - itemsPerPage;
  const currentSites = streamingOptions.slice(indexOfFirstSite, indexOfLastSite);

  const handleInstallClick = async () => {
    const selectedStreamingSites: Sites = options
      .filter(option => option.enabled && option.streaming)
      .map(option => ({
        siteName: option.label,
        siteURL: option.URL
      }));

    if (selectedStreamingSites.length > 0) {
      const total = selectedStreamingSites.length;
      setProgress({
        percent: 0,
        status: `Installing ${total} Streaming Sites`,
        description: selectedStreamingSites.map(site => site.siteName).join(', ')
      });

      setCurrentStreamingSites(options.filter(option => option.enabled && option.streaming));

      await installSite(selectedStreamingSites, serverAPI, { setProgress }, total);
    }
  };

  const handleToggle = (changeName: string, changeValue: boolean) => {
    const newOptions = options.map(option => {
      if (option.name === changeName) {
        return { ...option, enabled: changeValue };
      }
      return option;
    });
    setOptions(newOptions);
  };

  const cancelOperation = () => {
    setProgress({ percent: 0, status: '', description: '' });
    setCurrentStreamingSites([]);
  };

  const nextPage = () => {
    if (currentPage * itemsPerPage < streamingOptions.length) {
      setCurrentPage(prevPage => prevPage + 1);
    }
  };

  const prevPage = () => {
    if (currentPage > 1) {
      setCurrentPage(prevPage => prevPage - 1);
    }
  };

  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  useEffect(() => {
    if (currentStreamingSites.length > 0) {
      const interval = setInterval(() => {
        setCurrentImageIndex(prevIndex => (prevIndex + 1) % currentStreamingSites.length);
      }, 7000);
      return () => clearInterval(interval);
    }
  }, [currentStreamingSites]);

  const fadeStyle = {
    position: 'absolute',
    top: 0,
    left: 0,
    width: '100%',
    height: '100%',
    opacity: 0.5,
    pointerEvents: 'none',
    transition: 'background-image 1s ease-in-out',
    backgroundImage: `url(${currentStreamingSites[currentImageIndex]?.urlimage})`,
    backgroundSize: 'cover',
    backgroundPosition: 'center'
  };

  // While installing
  if (progress.status !== '' && progress.percent < 100) {
    return (
      <ConfirmModal
        strTitle="Installing Streaming Sites"
        onCancel={cancelOperation}
        onEscKeypress={cancelOperation}
        bOKDisabled={true}
      >
        <DialogBodyText>
          Selected options: {options.filter(option => option.enabled).map(option => option.label).join(', ')}
        </DialogBodyText>
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
          {currentStreamingSites.length > 0 && (
            <div style={fadeStyle} />
          )}
        </DialogBody>
      </ConfirmModal>
    );
  }

  // Main selection modal
  return (
    <ConfirmModal
      bAllowFullSize
      onCancel={closeModal}
      onEscKeypress={closeModal}
      strOKButtonText="Install"
      strCancelButtonText="Cancel"
      bOKDisabled={options.every(option => !option.enabled)}
      onOK={handleInstallClick}
      strTitle="Install Game/Media Streaming Sites"
    >
      <DialogBodyText>
        NSL will install and use Chrome to launch these sites. Non-Steam shortcuts will be created for each selection.
      </DialogBodyText>
      <DialogBody>

        <Focusable style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '10px' }}>
          <DialogButton onClick={prevPage} disabled={currentPage === 1}>Previous</DialogButton>
          <DialogButton onClick={nextPage} disabled={currentPage * itemsPerPage >= streamingOptions.length}>Next</DialogButton>
        </Focusable>

        {currentSites.map(({ name, label }) => (
          <ToggleField
            key={name}
            label={label}
            checked={options.find(option => option.name === name)?.enabled || false}
            onChange={(value) => handleToggle(name, value)}
          />
        ))}

        <Focusable style={{ display: "flex", alignItems: "center", gap: "10px", marginTop: "10px" }}>
          <DialogBodyText style={{ fontSize: "small" }}>
            Note: NSL will attempt to install Google Chrome. Be sure that Google Chrome is installed from the Discover Store in Desktop Mode first or from SteamOS.
          </DialogBodyText>
        </Focusable>

      </DialogBody>
    </ConfirmModal>
  );
};
