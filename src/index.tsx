import {
  ButtonItem,
  definePlugin,
  findSP,
  ModalRoot,
  ModalRootProps,
  PanelSection,
  PanelSectionRow,
  ServerAPI,
  showModal,
  staticClasses,
  TextField,
  ToggleField,
} from "decky-frontend-lib";
import { useContext, useEffect, useReducer, useState, VFC, createContext } from "react";
import { FaRocket } from "react-icons/fa";

// Define an action type for updating customWebsites
type UpdateCustomWebsitesAction = {
  type: 'UPDATE_CUSTOM_WEBSITES';
  customWebsites: string[];
};

// Define a reducer function for updating customWebsites
const customWebsitesReducer = (
  state: string[],
  action: UpdateCustomWebsitesAction
) => {
  console.log(`action: ${JSON.stringify(action)}`);
  switch (action.type) {
    case 'UPDATE_CUSTOM_WEBSITES':
      // Store the updated customWebsites in localStorage
      localStorage.setItem('customWebsites', JSON.stringify(action.customWebsites));
      return action.customWebsites;
    default:
      return state;
  }
};

// Create a context with an empty array as the default value
const CustomWebsitesContext = createContext<{
  customWebsites: string[];
  dispatch: React.Dispatch<UpdateCustomWebsitesAction>;
}>({
  customWebsites: [],
  dispatch: () => {},
});

// Create a provider component that takes in children as a prop
const CustomWebsitesProvider: React.FC = ({ children }) => {
  // Retrieve the customWebsites from localStorage on initial render
  const [customWebsites, dispatch] = useReducer(customWebsitesReducer, JSON.parse(localStorage.getItem('customWebsites') || '[]'));

  // Render the provider and pass in the customWebsites state and dispatch function as the value
  return (
    <CustomWebsitesContext.Provider value={{ customWebsites, dispatch }}>
      {children}
    </CustomWebsitesContext.Provider>
  );
};

type SearchModalProps = ModalRootProps & {
  setModalResult?(result: string[]): void;
  promptText: string;
};

const SearchModal: VFC<SearchModalProps> = ({
  closeModal,
  setModalResult,
  promptText
}) => {
  console.log('SearchModal rendered');

  const [searchText, setSearchText] = useState('');

  const handleTextChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchText(e.target.value);
  };

  const handleSubmit = () => {
    // Split the entered text by commas and trim any whitespace
    const websites = searchText.split(',').map((website) => website.trim());
    console.log(`websites: ${JSON.stringify(websites)}`);
    setModalResult && setModalResult(websites);
    closeModal && closeModal();
  };

  return (
    <ModalRoot closeModal={handleSubmit}>
      <form>
        <TextField
          focusOnMount={true}
          label="Websites"
          placeholder={promptText}
          onChange={handleTextChange}
        />
        <p>You can separate multiple websites by using commas.</p>
        <button type="button" onClick={handleSubmit}>Submit</button>
      </form>
    </ModalRoot>
  );
};

const Content: VFC<{ serverAPI: ServerAPI }> = ({ serverAPI }) => {
   console.log('Content rendered');

   // Use the useContext hook to access customWebsites and dispatch from the context
   const { customWebsites, dispatch } = useContext(CustomWebsitesContext);

   const [options, setOptions] = useState({
     epicGames: false,
     gogGalaxy: false,
     origin: false,
     uplay: false,
     battleNet: false,
     amazonGames: false,
     eaApp: false,
     legacyGames: false,
     itchIo: false,
     humbleGames: false,
     indieGala: false,
     rockstar: false,
     glyph: false,
     minecraft: false,
     psPlus: false,
     dmm: false,
     xboxGamePass: false,
     geforceNow: false,
     amazonLuna:false,
     netflix:false,
     hulu:false,
     disneyPlus:false,
     amazonPrimeVideo:false,
     youtube:false,
     twitch:false
   });

   const [progress, setProgress] = useState({ percent:0, status:'' });

   const [separateAppIds, setSeparateAppIds] = useState(false);

   const [clickedButton, setClickedButton] = useState('');

   useEffect(() => {
       console.log(`customWebsites updated:${JSON.stringify(customWebsites)}`);
   }, [customWebsites]);

   const handleButtonClick = (name:string) => {
       setOptions((prevOptions) => ({
           ...prevOptions,
           [name]: !prevOptions[name],
       }));
   };

   const handleInstallClick = async () => {
       console.log('handleInstallClick called');

       const selectedLaunchers = Object.entries(options)
           .filter(([_, isSelected]) => isSelected)
           .map(([name, _]) => name.charAt(0).toUpperCase() + name.slice(1))
           .join(', ');

       setProgress({ percent:0, status:`Calling serverAPI...please be patient...this can take some time... Downloading and Installing ${selectedLaunchers}... Steam will restart Automatically.` });

       console.log(`Selected options:${JSON.stringify(options)}`);
       console.log(`customWebsites:${JSON.stringify(customWebsites)}`);

       try {
           const result = await serverAPI.callPluginMethod("install", {
               selected_options: options,
               custom_websites: customWebsites,
               separate_app_ids: separateAppIds,
               start_fresh: false // Pass true for the start_fresh parameter
           });

           if (result) {
               setProgress({ percent:100, status:'Installation successful!' });
               alert('Installation successful!');
           } else {
               setProgress({ percent:100, status:'Installation failed.' });
               alert('Installation failed.');
           }
       } catch (error) {
           setProgress({ percent:100, status:'Installation failed.' });
           console.error('Error calling _main method on server-side plugin:', error);
       }
   };

   const handleStartFreshClick = async () => {
       console.log('handleStartFreshClick called');

       // Call the install method on the server-side plugin with the appropriate arguments
       try {
           const result = await serverAPI.callPluginMethod("install", {
               selected_options: options,
               custom_websites: customWebsites,
               separate_app_ids: separateAppIds,
               start_fresh: true // Pass true for the start_fresh parameter
           });

           if (result) {
               setProgress({ percent:100, status:'Installation successful!' });
               alert('Installation successful!');
           } else {
               setProgress({ percent:100, status:'Installation failed.' });
               alert('Installation failed.');
           }
       } catch (error) {
           setProgress({ percent:100, status:'Installation failed.' });
           console.error('Error calling _main method on server-side plugin:', error);
       }
   };

   const handleCreateWebsiteShortcutClick = async () => {
       console.log('handleCreateWebsiteShortcutClick called');

       setClickedButton('createWebsiteShortcut');

       showModal(
           <SearchModal
               promptText="Enter website"
               setModalResult={(result) => {
                   console.log(`result:${JSON.stringify(result)}`);
                   if (clickedButton === 'createWebsiteShortcut') {
                       // Handle result for createWebsiteShortcut button
                       dispatch({ type:'UPDATE_CUSTOM_WEBSITES', customWebsites:result });
                   }
               }}
           />,
           findSP()
       );
   };
   
   const optionsData = [
    { name: 'epicGames', label: 'Epic Games' },
    { name: 'gogGalaxy', label: 'Gog Galaxy' },
    { name: 'origin', label: 'Origin' },
    { name: 'uplay', label: 'Ubisoft Connect' },
    { name: 'battleNet', label: 'Battle.net' },
    { name: 'amazonGames', label: 'Amazon Games' },
    { name: 'eaApp', label: 'EA App' },
    { name: 'legacyGames', label: 'Legacy Games' },
    { name: 'itchIo', label: 'Itch.io' },
    { name: 'humbleGames', label: 'Humble Games' },
    { name: 'indieGala', label: 'IndieGala Client' },
    { name: 'rockstar', label: 'Rockstar Games Launcher' },
    { name: 'glyph', label: 'Glyph Laucnher' },
    { name: 'minecraft', label: 'Minecraft: Java Edition' },
    { name: 'psPlus', label: 'Playstation Plus' },
    { name: 'dmm', label: 'DMM Games' },
    { name: 'xboxGamePass', label: 'Xbox Game Pass' },
    { name: 'geforceNow', label: 'GeForce Now' },
    { name: 'amazonLuna', label: 'Amazon Luna' },
    { name: 'netflix', label: 'Netflix' },
    { name: 'hulu', label: 'Hulu' },
    { name: 'disneyPlus', label: 'Disney+' },
    { name: 'amazonPrimeVideo', label: 'Amazon Prime Video' },
    { name: 'youtube', label: 'Youtube' },
    { name: 'twitch', label: 'Twitch' }
  ];

  const launcherOptions = optionsData.filter(({name}) => ['epicGames', 'gogGalaxy', 'uplay', 'battleNet', 'amazonGames', 'eaApp', 'legacyGames', 'humbleGames', 'indieGala', 'minecraft', 'psPlus'].includes(name));
  const streamingOptions = optionsData.filter(({name}) => ['xboxGamePass','geforceNow','amazonLuna','netflix','hulu','disneyPlus','amazonPrimeVideo','youtube', 'twitch'].includes(name));
 
  return (
    <div className="decky-plugin">
      <PanelSectionRow style={{ fontSize: "16px", fontWeight: "bold", marginBottom: "10px" }}>
        Welcome to the decky plugin version of NonSteamLaunchers! I hope it works...
      </PanelSectionRow>
      <PanelSectionRow style={{ fontSize: "12px", marginBottom: "10px" }}>
        Thank you for everyone's support and contributions on the script itself, this is the plugin we have all been waiting for... installing your favorite launchers in the easiest way possible. Enjoy! P.S. A couple notes... Some launchers are not available due to user input, still looking for way around this, thank you and please be patient as i add more features from the original script!
      </PanelSectionRow>
  
      <PanelSectionRow>
        <ToggleField label="Separate App IDs" checked={separateAppIds} onChange={setSeparateAppIds} />
      </PanelSectionRow>
  
      <PanelSectionRow>
        <progress value={progress.percent} max={100} />
        <div>{progress.status}</div>
      </PanelSectionRow>
  
      <PanelSection>
        <ButtonItem layout="below" onClick={handleInstallClick}>
          Install
        </ButtonItem>
  
        <ButtonItem layout="below" onClick={handleStartFreshClick}>
          Start Fresh
        </ButtonItem>
        {/*
        <ButtonItem layout="below" onClick={handleCreateWebsiteShortcutClick}>
          Create Website Shortcut
        </ButtonItem>
        */}
      </PanelSection>
  
      <PanelSection title="Game Launchers">
        <PanelSectionRow style={{ fontSize: "12px", marginBottom: "10px" }}>
          Here you choose your launchers you want to install and let NSL do the rest. Once Steam restarts your launchers will be in your library! If they do not start up, restart your steam deck manually.
        </PanelSectionRow>
        <PanelSectionRow>
          {launcherOptions.map(({ name, label }) => (
            <ButtonItem
              className={options[name] ? 'selected' : ''}
              layout="below"
              onClick={() => handleButtonClick(name)}
            >
              <span className="checkmark">{options[name] ? '✓' : ''}</span>{' '}
              {label}
            </ButtonItem>
          ))}
        </PanelSectionRow>
      </PanelSection>
  
      <PanelSection title="Game and Movie Streaming">
        <PanelSectionRow style={{ fontSize: "12px", marginBottom: "10px" }}>
          Please install Google Chrome via the Discover Store in desktop mode first. NSL uses Chrome to launch these sites. Do NOT "Force Compatability" on these they will not open with proton.
        </PanelSectionRow>
        <PanelSectionRow>
          {streamingOptions.map(({ name, label }) => (
            <ButtonItem
              className={options[name] ? 'selected' : ''}
              layout="below"
              onClick={() => handleButtonClick(name)}
            >
              <span className="checkmark">{options[name] ? '✓' : ''}</span>{' '}
              {label}
            </ButtonItem>
          ))}
        </PanelSectionRow>
      </PanelSection>
  
      <style>
        {`
          .decky-plugin .checkmark {
            color: green;
          }
          .decky-plugin .selected {
            background-color: #eee;
          }
          .decky-plugin progress {
            display:block;
            width: 100%;
            margin-top: 5px;
            height: 20px;
          }
          .decky-plugin pre {
            white-space: pre-wrap;
          }
          .decky-plugin .decky-ButtonItem {
            margin-bottom: 10px;
            border-bottom: none;
          }
          .decky-plugin .decky-PanelSection {
            border-bottom: none;
          }
        `}
      </style>
    </div>
  );
  };
  
  export default definePlugin((serverApi: ServerAPI) => {
  return {
   title: <div className={staticClasses.Title}>NonSteamLaunchers</div>,
   content: (
     <CustomWebsitesProvider>
       <Content serverAPI={serverApi} />
     </CustomWebsitesProvider>
   ),
   icon: <FaRocket />,
  };
  });