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
    DialogButton
  } from "decky-frontend-lib";
  import { useState, VFC, useEffect } from "react";
  import { Sites, installSite } from "../../hooks/installSites";
  
  type CustomSiteModalProps = {
    closeModal?: () => void,
    serverAPI: ServerAPI,
  };
  
  /**
  * The modal for updating custom sites.
  */
  export const CustomSiteModal: VFC<CustomSiteModalProps> = ({closeModal, serverAPI}) => {
    const [sites, setSites] = useState<Sites>([{siteName: "", siteURL: ""}])
    const [canSave, setCanSave] = useState<boolean>(false);
    const [progress, setProgress] = useState({ percent:0, status:'', description: '' });
  
    useEffect(() => {
        setCanSave(sites.every(site => site.siteName != "") && sites.every(site => site.siteURL != ""));
    }, [sites]);
  
    useEffect(() => {
        if (progress.percent === 100) {
            closeModal!();
        }
    }, [progress]);
  
    function onNameChange(siteName: string, e: React.ChangeEvent<HTMLInputElement>) {
        const newSites = sites.map(site => {
            if (site.siteName === siteName) {
                return {
                ...site,
                siteName: e?.target.value
                };
            } else {
                return site;
            }
        });
        setSites(newSites);
    }
  
    function onURLChange(siteName: string, e: React.ChangeEvent<HTMLInputElement>) {
        const newSites = sites.map(site => {
            if (site.siteName === siteName) {
                return {
                ...site,
                siteURL: e?.target.value
                };
            } else {
                return site;
            }
        });
        setSites(newSites);
    }
  
    function addSiteFields() {
        if (canSave) {
            setSites( // Replace the state
            [ // with a new array
                ...sites, // that contains all the old items
                { siteName: '', siteURL: '' } // and one new item at the end
            ]
            );
        }
    }
  
    async function onSave() {
        if (canSave) {
            setProgress({ percent: 1, status:`Installing Custom Sites`, description: `` });
            await installSite(sites, serverAPI, {setProgress}, sites.length);
        } 
    }
  
    const cancelOperation = () => {
        setProgress({ percent: 0, status: '', description: '' });
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
  
    return ((progress.percent > 0 && progress.percent < 100) ?
        <ModalRoot>
            <DialogHeader>
                Installing Custom Sites
            </DialogHeader>
            <DialogBodyText>Creating shortcuts for sites: {sites.map(site => site.siteName).join(', ')}</DialogBodyText>
            <DialogBody>
                <SteamSpinner/>
                <img src="https://cdn2.steamgriddb.com/thumb/d0fb992a3dc7f0014263653d6e2063fe.jpg" alt="Overlay" style={{ ...fadeStyle, opacity: 0.5 }} />
                <DialogButton onClick={cancelOperation} style={{ width: '25px' }}>Back</DialogButton>
            </DialogBody>
        </ModalRoot> :
        <div>
            <ConfirmModal
                bAllowFullSize
                onCancel={closeModal}
                onEscKeypress={closeModal}
                strMiddleButtonText={'Add Another Site'}
                onMiddleButton={addSiteFields}
                bMiddleDisabled={!canSave}
                bOKDisabled={!canSave}
                onOK={onSave}
                strOKButtonText="Create Shortcuts"
                strTitle = "Enter Custom Websites"
            >
                <DialogBodyText>NSL will install and use Chrome to launch these sites. Non-Steam shortcuts will be created for each site entered. Before installing, toggle Auto Scan "on" for these.</DialogBodyText>
                <DialogBody>
                    {sites.map(({siteName, siteURL}, index) =>
                        <>
                            <PanelSection title={`Site ${index + 1}`}>
                                <TextField label = "Name" value={siteName} placeholder="The name you want to appear in the shortcut for your site." onChange={(e) => onNameChange(siteName, e)} />
                                <TextField label = "URL" value={siteURL} placeholder="The URL for your site." onChange={(e) => onURLChange(siteName, e)} />
                            </PanelSection>
                        </>
                    )}
                </DialogBody>
            </ConfirmModal>
        </div>
    )
  };