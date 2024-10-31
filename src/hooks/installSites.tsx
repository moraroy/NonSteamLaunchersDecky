import { ServerAPI } from "decky-frontend-lib";
import { createShortcut } from "./createShortcut";
import { Dispatch, SetStateAction } from "react";

export type Sites= {
    siteName: string,
    siteURL: string | undefined
}[]

type Props = {
    setProgress: Dispatch<SetStateAction<{percent: number; status: string; description: string; }>>;
  };

export const installSite = async (sites: Sites, serverAPI: ServerAPI, { setProgress }: Props , total: number) => {
    console.log('installSite called');
    
    try {
        const result = await serverAPI.callPluginMethod("install", {
            selected_options: '',
            install_chrome: true,
            separate_app_ids: false,
            start_fresh: false,
            update_proton_ge: false
        });

        if (result) {
            console.log('Installation successful!');
            await createSiteShortcut(sites, {setProgress}, total);
        } else {
            console.log('Installation failed.');
        }
    } catch (error) {
        console.error('Error calling _main method on server-side plugin:', error);
    }
    };

    async function createSiteShortcut(sites: Sites, { setProgress }: Props, total: number) {
    let customSiteWS: WebSocket;
    let installed = 0;
    customSiteWS = new WebSocket('ws://localhost:8675/customSite');

    customSiteWS.onopen = () => {
        console.log('NSL Custom Site WebSocket connection opened');
        if (customSiteWS.readyState === WebSocket.OPEN) {
            customSiteWS.send(JSON.stringify(sites));
        } else {
            console.log('Cannot send message, NSL Custom Site WebSocket connection is not open');
        }
    };

    customSiteWS.onmessage = (e) => {
        console.log(`Received custom site data from NSL server: ${e.data}`);
        if (e.data === 'NoShortcuts') {
            console.log('No shortcuts to add, unblocking UI');
            setProgress({ percent: 100, status:``, description: `` })
        }
        if (e.data[0] === '{' && e.data[e.data.length - 1] === '}') {
            try {
                const site = JSON.parse(e.data);
                installed++
                createShortcut(site);
                if (installed == total) {
                    setProgress({ percent: 100, status:``, description: `` });
                }
            } catch (error) {
                console.error(`Error parsing data as JSON: ${error}`);
            }
        }
    };

    customSiteWS.onerror = (e) => {
        const errorEvent = e as ErrorEvent;
        console.error(`NSL Custom Site WebSocket error: ${errorEvent.message}`);
    };

    customSiteWS.onclose = (e) => {
        console.log(`NSL Custom Site WebSocket connection closed, code: ${e.code}, reason: ${e.reason}`);
        setProgress({ percent: 100, status:``, description: `` });
    };
    }