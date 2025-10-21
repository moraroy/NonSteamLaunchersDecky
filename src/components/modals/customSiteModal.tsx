import {
    ConfirmModal,
    DialogBody,
    DialogBodyText,
    DialogHeader,
    ModalRoot,
    PanelSection,
    ServerAPI,
    SteamSpinner,
    TextField,
    DialogButton,
    ToggleField,
} from "decky-frontend-lib";
import { useState, VFC, useEffect } from "react";
import { Sites, installSite } from "../../hooks/installSites";

type CustomSiteModalProps = {
    closeModal?: () => void,
    serverAPI: ServerAPI,
};

export const CustomSiteModal: VFC<CustomSiteModalProps> = ({ closeModal, serverAPI }) => {
    const [sites, setSites] = useState<Sites>([{ siteName: "", siteURL: "" }]);
    const [canSave, setCanSave] = useState<boolean>(false);
    const [progress, setProgress] = useState({ percent: 0, status: '', description: '' });

    const [selectedBrowser, setSelectedBrowser] = useState<string | null>(null);

    useEffect(() => {
        setCanSave(
            sites.every(site => site.siteName.trim() !== "") &&
            sites.every(site => site.siteURL?.trim() !== "")
        );
    }, [sites]);

    useEffect(() => {
        if (progress.percent === 100) {
            closeModal?.();
        }
    }, [progress, closeModal]);

    function onNameChange(siteName: string, e: React.ChangeEvent<HTMLInputElement>) {
        const newSites = sites.map(site => {
            if (site.siteName === siteName) {
                return {
                    ...site,
                    siteName: e.target.value
                };
            }
            return site;
        });
        setSites(newSites);
    }

    function onURLChange(siteName: string, e: React.ChangeEvent<HTMLInputElement>) {
        const newSites = sites.map(site => {
            if (site.siteName === siteName) {
                return {
                    ...site,
                    siteURL: e.target.value
                };
            }
            return site;
        });
        setSites(newSites);
    }

    function addSiteFields() {
        if (canSave) {
            setSites([
                ...sites,
                { siteName: '', siteURL: '' }
            ]);
        }
    }

    async function onSave() {
        if (canSave && selectedBrowser) {
            setProgress({ percent: 1, status: `Installing Custom Sites`, description: `` });
            await installSite(sites, serverAPI, { setProgress }, sites.length, selectedBrowser);
        }
    }

    const cancelOperation = () => {
        setProgress({ percent: 0, status: '', description: '' });
    };

    const handleBrowserSelect = (browser: string) => {
        setSelectedBrowser(browser);
    };

    const fadeStyle = {
        position: 'absolute' as const,
        top: 0,
        left: 0,
        width: '100%',
        height: '100%',
        opacity: 1,
        pointerEvents: 'none' as const,
        transition: 'opacity 1s ease-in-out'
    };

    return (progress.percent > 0 && progress.percent < 100) ? (
        <ModalRoot>
            <DialogHeader>Installing Custom Sites</DialogHeader>
            <DialogBodyText>Creating shortcuts for sites: {sites.map(site => site.siteName).join(', ')}</DialogBodyText>
            <DialogBody>
                <SteamSpinner />
                <img
                    src="https://cdn2.steamgriddb.com/thumb/d0fb992a3dc7f0014263653d6e2063fe.jpg"
                    alt="Overlay"
                    style={{ ...fadeStyle, opacity: 0.5 }}
                />
                <DialogButton onClick={cancelOperation} style={{ width: '25px' }}>Back</DialogButton>
            </DialogBody>
        </ModalRoot>
    ) : (
        <div>
            <ConfirmModal
                bAllowFullSize
                onCancel={closeModal}
                onEscKeypress={closeModal}
                strMiddleButtonText={'Add Another Site'}
                onMiddleButton={addSiteFields}
                bMiddleDisabled={!canSave}
                bOKDisabled={!canSave || !selectedBrowser}
                onOK={onSave}
                strOKButtonText="Create Shortcuts"
                strTitle="Enter Custom Websites"
            >
                {/* Browser Selection (using toggles) */}
                <DialogBody>
                    <div style={{ display: 'flex', flexDirection: 'row', gap: '1em', marginBottom: '1em', alignItems: 'center' }}>
                        <ToggleField
                            label="Google Chrome"
                            checked={selectedBrowser === "Google Chrome"}
                            onChange={() => handleBrowserSelect("Google Chrome")}
                        />
                        <ToggleField
                            label="Mozilla Firefox"
                            checked={selectedBrowser === "Mozilla Firefox"}
                            onChange={() => handleBrowserSelect("Mozilla Firefox")}
                        />
                        <ToggleField
                            label="Microsoft Edge"
                            checked={selectedBrowser === "Microsoft Edge"}
                            onChange={() => handleBrowserSelect("Microsoft Edge")}
                        />
                    </div>
                </DialogBody>

                <DialogBodyText>
                    NSL will install and use the selected browser to launch these sites. Non-Steam shortcuts will be created for each site entered.
                </DialogBodyText>

                <DialogBody>
                    {sites.map(({ siteName, siteURL }, index) => (
                        <PanelSection title={`Site ${index + 1}`} key={index}>
                            <TextField
                                label="Name"
                                value={siteName}
                                placeholder="The name you want to appear in the shortcut for your site."
                                onChange={(e) => onNameChange(siteName, e)}
                            />
                            <TextField
                                label="URL"
                                value={siteURL || ''}
                                placeholder="The URL for your site."
                                onChange={(e) => onURLChange(siteName, e)}
                            />
                        </PanelSection>
                    ))}
                </DialogBody>
            </ConfirmModal>
        </div>
    );
};
