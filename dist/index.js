(function (deckyFrontendLib, React) {
  'use strict';

  function _interopDefaultLegacy (e) { return e && typeof e === 'object' && 'default' in e ? e : { 'default': e }; }

  var React__default = /*#__PURE__*/_interopDefaultLegacy(React);

  var DefaultContext = {
    color: undefined,
    size: undefined,
    className: undefined,
    style: undefined,
    attr: undefined
  };
  var IconContext = React__default["default"].createContext && React__default["default"].createContext(DefaultContext);

  var __assign = window && window.__assign || function () {
    __assign = Object.assign || function (t) {
      for (var s, i = 1, n = arguments.length; i < n; i++) {
        s = arguments[i];
        for (var p in s) if (Object.prototype.hasOwnProperty.call(s, p)) t[p] = s[p];
      }
      return t;
    };
    return __assign.apply(this, arguments);
  };
  var __rest = window && window.__rest || function (s, e) {
    var t = {};
    for (var p in s) if (Object.prototype.hasOwnProperty.call(s, p) && e.indexOf(p) < 0) t[p] = s[p];
    if (s != null && typeof Object.getOwnPropertySymbols === "function") for (var i = 0, p = Object.getOwnPropertySymbols(s); i < p.length; i++) {
      if (e.indexOf(p[i]) < 0 && Object.prototype.propertyIsEnumerable.call(s, p[i])) t[p[i]] = s[p[i]];
    }
    return t;
  };
  function Tree2Element(tree) {
    return tree && tree.map(function (node, i) {
      return React__default["default"].createElement(node.tag, __assign({
        key: i
      }, node.attr), Tree2Element(node.child));
    });
  }
  function GenIcon(data) {
    // eslint-disable-next-line react/display-name
    return function (props) {
      return React__default["default"].createElement(IconBase, __assign({
        attr: __assign({}, data.attr)
      }, props), Tree2Element(data.child));
    };
  }
  function IconBase(props) {
    var elem = function (conf) {
      var attr = props.attr,
        size = props.size,
        title = props.title,
        svgProps = __rest(props, ["attr", "size", "title"]);
      var computedSize = size || conf.size || "1em";
      var className;
      if (conf.className) className = conf.className;
      if (props.className) className = (className ? className + " " : "") + props.className;
      return React__default["default"].createElement("svg", __assign({
        stroke: "currentColor",
        fill: "currentColor",
        strokeWidth: "0"
      }, conf.attr, attr, svgProps, {
        className: className,
        style: __assign(__assign({
          color: props.color || conf.color
        }, conf.style), props.style),
        height: computedSize,
        width: computedSize,
        xmlns: "http://www.w3.org/2000/svg"
      }), title && React__default["default"].createElement("title", null, title), props.children);
    };
    return IconContext !== undefined ? React__default["default"].createElement(IconContext.Consumer, null, function (conf) {
      return elem(conf);
    }) : elem(DefaultContext);
  }

  // THIS FILE IS AUTO GENERATED
  function RxRocket (props) {
    return GenIcon({"tag":"svg","attr":{"viewBox":"0 0 15 15","fill":"none"},"child":[{"tag":"path","attr":{"fillRule":"evenodd","clipRule":"evenodd","d":"M6.85357 3.85355L7.65355 3.05353C8.2981 2.40901 9.42858 1.96172 10.552 1.80125C11.1056 1.72217 11.6291 1.71725 12.0564 1.78124C12.4987 1.84748 12.7698 1.97696 12.8965 2.10357C13.0231 2.23018 13.1526 2.50125 13.2188 2.94357C13.2828 3.37086 13.2779 3.89439 13.1988 4.44801C13.0383 5.57139 12.591 6.70188 11.9464 7.34645L7.49999 11.7929L6.35354 10.6465C6.15827 10.4512 5.84169 10.4512 5.64643 10.6465C5.45117 10.8417 5.45117 11.1583 5.64643 11.3536L7.14644 12.8536C7.34171 13.0488 7.65829 13.0488 7.85355 12.8536L8.40073 12.3064L9.57124 14.2572C9.65046 14.3893 9.78608 14.4774 9.9389 14.4963C10.0917 14.5151 10.2447 14.4624 10.3535 14.3536L12.3535 12.3536C12.4648 12.2423 12.5172 12.0851 12.495 11.9293L12.0303 8.67679L12.6536 8.05355C13.509 7.19808 14.0117 5.82855 14.1887 4.58943C14.2784 3.9618 14.2891 3.33847 14.2078 2.79546C14.1287 2.26748 13.9519 1.74482 13.6035 1.39645C13.2552 1.04809 12.7325 0.871332 12.2045 0.792264C11.6615 0.710945 11.0382 0.721644 10.4105 0.8113C9.17143 0.988306 7.80189 1.491 6.94644 2.34642L6.32322 2.96968L3.07071 2.50504C2.91492 2.48278 2.75773 2.53517 2.64645 2.64646L0.646451 4.64645C0.537579 4.75533 0.484938 4.90829 0.50375 5.0611C0.522563 5.21391 0.61073 5.34954 0.742757 5.42876L2.69364 6.59928L2.14646 7.14645C2.0527 7.24022 2.00002 7.3674 2.00002 7.50001C2.00002 7.63261 2.0527 7.75979 2.14646 7.85356L3.64647 9.35356C3.84173 9.54883 4.15831 9.54883 4.35357 9.35356C4.54884 9.1583 4.54884 8.84172 4.35357 8.64646L3.20712 7.50001L3.85357 6.85356L6.85357 3.85355ZM10.0993 13.1936L9.12959 11.5775L11.1464 9.56067L11.4697 11.8232L10.0993 13.1936ZM3.42251 5.87041L5.43935 3.85356L3.17678 3.53034L1.80638 4.90074L3.42251 5.87041ZM2.35356 10.3535C2.54882 10.1583 2.54882 9.8417 2.35356 9.64644C2.1583 9.45118 1.84171 9.45118 1.64645 9.64644L0.646451 10.6464C0.451188 10.8417 0.451188 11.1583 0.646451 11.3535C0.841713 11.5488 1.1583 11.5488 1.35356 11.3535L2.35356 10.3535ZM3.85358 11.8536C4.04884 11.6583 4.04885 11.3417 3.85359 11.1465C3.65833 10.9512 3.34175 10.9512 3.14648 11.1465L1.14645 13.1464C0.95119 13.3417 0.951187 13.6583 1.14645 13.8535C1.34171 14.0488 1.65829 14.0488 1.85355 13.8536L3.85358 11.8536ZM5.35356 13.3535C5.54882 13.1583 5.54882 12.8417 5.35356 12.6464C5.1583 12.4512 4.84171 12.4512 4.64645 12.6464L3.64645 13.6464C3.45119 13.8417 3.45119 14.1583 3.64645 14.3535C3.84171 14.5488 4.1583 14.5488 4.35356 14.3535L5.35356 13.3535ZM9.49997 6.74881C10.1897 6.74881 10.7488 6.1897 10.7488 5.5C10.7488 4.8103 10.1897 4.25118 9.49997 4.25118C8.81026 4.25118 8.25115 4.8103 8.25115 5.5C8.25115 6.1897 8.81026 6.74881 9.49997 6.74881Z","fill":"currentColor"}}]})(props);
  }

  class notify {
      /**
       * Sets the interop's serverAPI.
       * @param serv The ServerAPI for the interop to use.
       */
      static setServer(serv) {
          this.serverAPI = serv;
      }
      static toast(title, message, icons) {
          return (() => {
              try {
                  const gameIcon = icons ? (window.SP_REACT.createElement("img", { src: icons.gameIconUrl, alt: "Game Icon", style: {
                          width: '26px',
                          height: '26px',
                          borderRadius: '50%',
                          boxShadow: '0 0 15px rgba(0, 0, 0, 0.7)',
                          border: '2px solid #fff', // Added border
                      } })) : null;
                  const launcherIcon = icons?.launcherIconUrl ? (window.SP_REACT.createElement("div", { style: { flexGrow: 1, textAlign: 'center', marginLeft: '0px', marginTop: '-16px' } },
                      window.SP_REACT.createElement("img", { src: icons.launcherIconUrl, alt: "Launcher Icon", style: {
                              width: '12px',
                              height: '12px',
                              borderRadius: '10%',
                              boxShadow: '0 0 10px rgba(0, 0, 0, 0.5)',
                          } }))) : null;
                  return this.serverAPI.toaster.toast({
                      title: icons ? (window.SP_REACT.createElement("div", { style: { display: 'flex', justifyContent: 'flex-start', paddingLeft: '25px', width: '500px' } }, title)) : title,
                      body: icons ? (window.SP_REACT.createElement("div", { style: { display: 'flex', justifyContent: 'flex-start', paddingLeft: '35px', width: '0px' } }, message)) : message,
                      duration: 8000,
                      icon: (window.SP_REACT.createElement("div", { style: { display: 'flex', alignItems: 'center' } },
                          gameIcon,
                          launcherIcon)),
                  });
              }
              catch (e) {
                  console.log("Toaster Error", e);
              }
          })();
      }
  }

  const collectionLocks = new Map();
  async function withCollectionLock(collectionName, fn) {
      // Initialize queue for this collection if needed
      if (!collectionLocks.has(collectionName)) {
          collectionLocks.set(collectionName, Promise.resolve());
      }
      // Get last scheduled promise
      const previous = collectionLocks.get(collectionName);
      // Chain the next operation after it
      const next = previous.then(async () => {
          try {
              return await fn();
          }
          catch (e) {
              console.error("Collection lock error:", e);
          }
      });
      // Update queue
      collectionLocks.set(collectionName, next);
      return next;
  }
  // Shortcut Creation Code
  async function createShortcut(game) {
      const { appid, appname, exe, StartDir, LaunchOptions, CompatTool, Grid, WideGrid, Hero, Logo, Icon, LauncherIcon, Launcher, Icon64, } = game;
      const formattedExe = exe;
      const formattedStartDir = StartDir;
      const launchOptions = LaunchOptions;
      console.log(`Creating shortcut ${appname}`);
      console.log(`Game details: Name= ${appname}, ID=${appid}, exe=${formattedExe}, StartDir=${formattedStartDir}, launchOptions=${launchOptions}`);
      const appId = await SteamClient.Apps.AddShortcut(appname, formattedExe, formattedStartDir, launchOptions);
      if (!appId) {
          console.log(`Failed to create shortcut for ${appname}`);
          return false;
      }
      const defaultIconUrl = "https://raw.githubusercontent.com/moraroy/NonSteamLaunchersDecky/main/assets/logo.png";
      let gameIconUrl;
      if (Icon) {
          SteamClient.Apps.SetShortcutIcon(appId, Icon);
      }
      if (Icon64) {
          gameIconUrl = `data:image/x-icon;base64,${Icon64}`;
      }
      else {
          gameIconUrl = defaultIconUrl;
      }
      const launcherIconUrl = LauncherIcon ? `data:image/x-icon;base64,${LauncherIcon}` : null;
      if (launcherIconUrl) {
          notify.toast(appname, "has been added to your library!", { gameIconUrl, launcherIconUrl });
      }
      else {
          notify.toast(appname, "has been added to your library!", { gameIconUrl });
      }
      console.log(`AppID for ${appname} = ${appId}`);
      SteamClient.Apps.SetShortcutName(appId, appname);
      SteamClient.Apps.SetAppLaunchOptions(appId, launchOptions);
      SteamClient.Apps.SetShortcutExe(appId, formattedExe);
      SteamClient.Apps.SetShortcutStartDir(appId, formattedStartDir);
      const AvailableCompatTools = await SteamClient.Apps.GetAvailableCompatTools(appId);
      const CompatToolExists = AvailableCompatTools.some((e) => e.strToolName === CompatTool);
      if (CompatTool && CompatToolExists) {
          SteamClient.Apps.SpecifyCompatTool(appId, CompatTool);
      }
      else if (CompatTool) {
          SteamClient.Apps.SpecifyCompatTool(appId, 'proton_experimental');
      }
      SteamClient.Apps.SetCustomArtworkForApp(appId, Hero, 'png', 1);
      SteamClient.Apps.SetCustomArtworkForApp(appId, Logo, 'png', 2);
      SteamClient.Apps.SetCustomArtworkForApp(appId, Grid, 'png', 0);
      SteamClient.Apps.SetCustomArtworkForApp(appId, WideGrid, 'png', 3);
      await SteamClient.Apps.CreateDesktopShortcutForApp(appId);
      console.log("Desktop shortcut created for shortcut:", appId);
      // -------- Sort As --------
      if (Launcher && typeof Launcher === "string" && Launcher.trim().length > 0) {
          const sortName = `${appname} ${Launcher.trim()}`;
          await SteamClient.Apps.SetShortcutSortAs(appId, sortName);
          console.log("Sort As title set to:", sortName);
      }
      if (Launcher && typeof window !== 'undefined') {
          await withCollectionLock(Launcher, async () => {
              try {
                  const tag = Launcher;
                  const collectionStore = window.g_CollectionStore || window.collectionStore;
                  if (!collectionStore) {
                      console.error("No collection store found.");
                      return;
                  }
                  const collectionId = collectionStore.GetCollectionIDByUserTag(tag);
                  const collection = typeof collectionId === "string"
                      ? collectionStore.GetCollection(collectionId)
                      : collectionStore.NewUnsavedCollection(tag, undefined, []);
                  if (!collection) {
                      console.error(`Could not get or create collection "${tag}".`);
                      return;
                  }
                  if (!collectionId) {
                      await collection.Save();
                      console.log(`Created new collection "${tag}".`);
                  }
                  // Add app to collection
                  if (!collection.m_setApps.has(appId)) {
                      collection.m_setApps.add(appId);
                      collection.m_setAddedManually.add(appId);
                      await collection.Save();
                      console.log(`Added app ${appId} to collection "${tag}".`);
                  }
                  else {
                      console.log(`App ${appId} already in collection "${tag}".`);
                  }
              }
              catch (err) {
                  console.error("Failed to create or update collection:", err);
              }
          });
      }
      return true;
  }
  // End of Shortcut Creation Code

  const installSite = async (sites, serverAPI, { setProgress }, total, browser) => {
      console.log('installSite called');
      try {
          const result = await serverAPI.callPluginMethod("install", {
              selected_options: '',
              install_chrome: true,
              separate_app_ids: false,
              start_fresh: false,
              update_proton_ge: false,
              nslgamesaves: false
          });
          if (result) {
              console.log('Installation successful!');
              await createSiteShortcut(sites, browser, { setProgress }, total);
          }
          else {
              console.log('Installation failed.');
          }
      }
      catch (error) {
          console.error('Error calling _main method on server-side plugin:', error);
      }
  };
  async function createSiteShortcut(sites, browser, { setProgress }, total) {
      let installed = 0;
      const customSiteWS = new WebSocket('ws://localhost:8675/customSite');
      customSiteWS.onopen = () => {
          console.log('NSL Custom Site WebSocket connection opened');
          if (customSiteWS.readyState === WebSocket.OPEN) {
              // <--- send both sites AND browser info
              customSiteWS.send(JSON.stringify({
                  sites,
                  selectedBrowser: browser
              }));
          }
          else {
              console.log('Cannot send message, NSL Custom Site WebSocket connection is not open');
          }
      };
      customSiteWS.onmessage = (e) => {
          console.log(`Received custom site data from NSL server: ${e.data}`);
          if (e.data === 'NoShortcuts') {
              console.log('No shortcuts to add, unblocking UI');
              setProgress({ percent: 100, status: '', description: '' });
          }
          if (e.data[0] === '{' && e.data[e.data.length - 1] === '}') {
              try {
                  const site = JSON.parse(e.data);
                  installed++;
                  createShortcut(site);
                  if (installed === total) {
                      setProgress({ percent: 100, status: '', description: '' });
                  }
              }
              catch (error) {
                  console.error(`Error parsing data as JSON: ${error}`);
              }
          }
      };
      customSiteWS.onerror = (e) => {
          const errorEvent = e;
          console.error(`NSL Custom Site WebSocket error: ${errorEvent.message}`);
      };
      customSiteWS.onclose = (e) => {
          console.log(`NSL Custom Site WebSocket connection closed, code: ${e.code}, reason: ${e.reason}`);
          setProgress({ percent: 100, status: '', description: '' });
      };
  }

  const CustomSiteModal = ({ closeModal, serverAPI }) => {
      const [sites, setSites] = React.useState([{ siteName: "", siteURL: "" }]);
      const [canSave, setCanSave] = React.useState(false);
      const [progress, setProgress] = React.useState({ percent: 0, status: '', description: '' });
      const [selectedBrowser, setSelectedBrowser] = React.useState(null);
      React.useEffect(() => {
          setCanSave(sites.every(site => site.siteName.trim() !== "") &&
              sites.every(site => site.siteURL?.trim() !== ""));
      }, [sites]);
      React.useEffect(() => {
          if (progress.percent === 100) {
              closeModal?.();
          }
      }, [progress, closeModal]);
      function onNameChange(siteName, e) {
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
      function onURLChange(siteName, e) {
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
      const handleBrowserSelect = (browser) => {
          setSelectedBrowser(browser);
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
      const browserImageMap = {
          "Google Chrome": "https://cdn2.steamgriddb.com/thumb/d0fb992a3dc7f0014263653d6e2063fe.jpg",
          "Mozilla Firefox": "https://cdn2.steamgriddb.com/thumb/9384fe92aef7ea0128be2c916ed07cea.jpg",
          "Microsoft Edge": "https://cdn2.steamgriddb.com/thumb/ec0b830920c0efad2469c960b5dfae61.jpg",
          "Brave": "https://cdn2.steamgriddb.com/thumb/5ac7b3d023885d0d49e05a32f16c3d54.jpg",
      };
      return (progress.percent > 0 && progress.percent < 100) ? (window.SP_REACT.createElement(deckyFrontendLib.ModalRoot, null,
          window.SP_REACT.createElement(deckyFrontendLib.DialogHeader, null, "Installing Custom Sites"),
          window.SP_REACT.createElement(deckyFrontendLib.DialogBodyText, null,
              "Creating shortcuts for sites: ",
              sites.map(site => site.siteName).join(', ')),
          window.SP_REACT.createElement(deckyFrontendLib.DialogBody, null,
              window.SP_REACT.createElement(deckyFrontendLib.SteamSpinner, null),
              selectedBrowser && (window.SP_REACT.createElement("img", { src: browserImageMap[selectedBrowser], alt: `${selectedBrowser} Logo`, style: { ...fadeStyle, opacity: 0.5 } })),
              window.SP_REACT.createElement(deckyFrontendLib.DialogButton, { onClick: cancelOperation, style: { width: '25px' } }, "Back")))) : (window.SP_REACT.createElement("div", null,
          window.SP_REACT.createElement(deckyFrontendLib.ConfirmModal, { bAllowFullSize: true, onCancel: closeModal, onEscKeypress: closeModal, strMiddleButtonText: 'Add Another Site', onMiddleButton: addSiteFields, bMiddleDisabled: !canSave, bOKDisabled: !canSave || !selectedBrowser, onOK: onSave, strOKButtonText: "Create Shortcuts", strTitle: "Enter Custom Websites" },
              window.SP_REACT.createElement(deckyFrontendLib.DialogBody, null,
                  window.SP_REACT.createElement("div", { style: { display: 'flex', flexDirection: 'row', flexWrap: 'wrap', gap: '1em', marginBottom: '1em', alignItems: 'center' } },
                      window.SP_REACT.createElement(deckyFrontendLib.ToggleField, { label: "Google Chrome", checked: selectedBrowser === "Google Chrome", onChange: () => handleBrowserSelect("Google Chrome") }),
                      window.SP_REACT.createElement(deckyFrontendLib.ToggleField, { label: "Firefox", checked: selectedBrowser === "Mozilla Firefox", onChange: () => handleBrowserSelect("Mozilla Firefox") }),
                      window.SP_REACT.createElement(deckyFrontendLib.ToggleField, { label: "Microsoft Edge", checked: selectedBrowser === "Microsoft Edge", onChange: () => handleBrowserSelect("Microsoft Edge") }),
                      window.SP_REACT.createElement(deckyFrontendLib.ToggleField, { label: "Brave", checked: selectedBrowser === "Brave", onChange: () => handleBrowserSelect("Brave") }))),
              window.SP_REACT.createElement(deckyFrontendLib.DialogBodyText, null, "NSL will install and use the selected browser to launch these sites. Non-Steam shortcuts will be created for each site entered."),
              window.SP_REACT.createElement(deckyFrontendLib.DialogBody, null, sites.map(({ siteName, siteURL }, index) => (window.SP_REACT.createElement(deckyFrontendLib.PanelSection, { title: `Site ${index + 1}`, key: index },
                  window.SP_REACT.createElement(deckyFrontendLib.TextField, { label: "Name", value: siteName, placeholder: "The name you want to appear in the shortcut for your site.", onChange: (e) => onNameChange(siteName, e) }),
                  window.SP_REACT.createElement(deckyFrontendLib.TextField, { label: "URL", value: siteURL || '', placeholder: "The URL for your site.", onChange: (e) => onURLChange(siteName, e) }))))))));
  };

  const useSettings = (serverApi) => {
      const [settings, setSettings] = React.useState({
          autoscan: false,
          customSites: "",
          playtimeEnabled: true,
          thememusicEnabled: true,
      });
      // Load saved settings on mount
      React.useEffect(() => {
          const getData = async () => {
              const savedSettings = (await serverApi.callPluginMethod('get_setting', {
                  key: 'settings',
                  default: settings
              })).result;
              setSettings(savedSettings);
          };
          getData();
      }, [serverApi]);
      // Generic update helper
      async function updateSettings(key, value) {
          setSettings((oldSettings) => {
              const newSettings = { ...oldSettings, [key]: value };
              serverApi.callPluginMethod('set_setting', {
                  key: 'settings',
                  value: newSettings
              });
              return newSettings;
          });
      }
      // Setters
      function setAutoScan(value) {
          updateSettings('autoscan', value);
      }
      function setCustomSites(value) {
          updateSettings('customSites', value);
      }
      function setPlaytimeEnabled(value) {
          updateSettings('playtimeEnabled', value);
      }
      function setThemeMusicEnabled(value) {
          updateSettings('thememusicEnabled', value);
      }
      return {
          settings,
          setAutoScan,
          setCustomSites,
          setPlaytimeEnabled,
          setThemeMusicEnabled,
      };
  };

  async function setupWebSocket(url, onMessage, onComplete) {
      const ws = new WebSocket(url);
      ws.onopen = () => {
          console.log('NSL WebSocket connection opened');
          if (ws.readyState === WebSocket.OPEN) {
              ws.send('something'); // trigger backend if needed
          }
          else {
              console.log('Cannot send message, NSL WebSocket connection is not open');
          }
      };
      ws.onmessage = async (e) => {
          try {
              if (e.data[0] === '{' && e.data[e.data.length - 1] === '}') {
                  const message = JSON.parse(e.data);
                  if (message.status === "Manual scan completed") {
                      console.log('Manual scan completed');
                      onComplete();
                      ws.close();
                  }
                  else if ('removed_games' in message) {
                      console.log('Removed games received:', message.removed_games);
                      for (const platform in message.removed_games) {
                          const games = message.removed_games[platform];
                          for (const gameName of games) {
                              notify.toast(`${gameName} (${platform})`, 'has been removed from your library!');
                          }
                      }
                      onComplete(message.removed_games);
                  }
                  else {
                      await onMessage(message);
                  }
              }
          }
          catch (error) {
              console.error("Error processing WebSocket message:", error, e.data);
          }
      };
      ws.onerror = (e) => {
          const errorEvent = e;
          console.error(`NSL WebSocket error: ${errorEvent.message}`);
      };
      ws.onclose = (e) => {
          console.log(`NSL WebSocket connection closed, code: ${e.code}, reason: ${e.reason}`);
          if (e.code !== 1000) {
              console.log('Unexpected WS close, reopening...');
              setupWebSocket(url, onMessage, onComplete);
          }
      };
      return ws;
  }
  function cleanUpEmptyCollections(removedGames) {
      const collectionStore = window.g_CollectionStore || window.collectionStore;
      if (!collectionStore)
          return;
      Array.from(collectionStore.collectionsFromStorage.values()).forEach(c => {
          if ((c.visibleApps?.length || 0) === 0 && c.m_strName in removedGames) {
              collectionStore.DeleteCollection(c.m_strId);
              console.log(`Removed empty collection: ${c.m_strName}`);
          }
      });
  }
  async function scan(onComplete) {
      console.log('Starting NSL Scan');
      return new Promise((resolve) => {
          setupWebSocket('ws://localhost:8675/scan', async (message) => {
              await createShortcut(message);
          }, (removedGames) => {
              if (removedGames) {
                  cleanUpEmptyCollections(removedGames);
              }
              console.log('NSL Scan completed');
              onComplete();
              resolve();
          });
      });
  }
  async function autoscan() {
      console.log('Starting NSL Autoscan');
      await setupWebSocket('ws://localhost:8675/autoscan', async (message) => {
          await createShortcut(message);
      }, (removedGames) => {
          if (removedGames) {
              cleanUpEmptyCollections(removedGames);
          }
          console.log('NSL Autoscan completed');
      });
  }

  const useLogUpdates = (trigger) => {
      const [log, setLog] = React.useState([]);
      const logWsRef = React.useRef(null);
      React.useEffect(() => {
          if (trigger && !logWsRef.current) {
              logWsRef.current = new WebSocket('ws://localhost:8675/logUpdates');
              logWsRef.current.onmessage = (e) => {
                  setLog((prevLog) => [...prevLog, e.data]);
              };
              logWsRef.current.onerror = (e) => {
                  console.error(`WebSocket error: ${e}`);
              };
              logWsRef.current.onclose = (e) => {
                  console.log(`WebSocket closed: ${e.code} - ${e.reason}`);
                  // Attempt to reconnect after a delay
                  setTimeout(() => {
                      logWsRef.current = new WebSocket('ws://localhost:8675/logUpdates');
                  }, 5000);
              };
          }
          return () => {
              if (logWsRef.current) {
                  logWsRef.current.close();
                  logWsRef.current = null;
              }
          };
      }, [trigger]);
      return log;
  };

  const useLauncherStatus = () => {
      const [launcherStatus, setLauncherStatus] = React.useState(null);
      const [error, setError] = React.useState(null);
      const [loading, setLoading] = React.useState(true);
      // WebSocket connection to check for launcher status
      const fetchLauncherStatus = () => {
          setLoading(true);
          console.log("Connecting to WebSocket to check launcher status...");
          const socket = new WebSocket("ws://localhost:8675/launcher_status");
          socket.onopen = () => {
              console.log("WebSocket connected to check launcher status");
          };
          socket.onmessage = (event) => {
              const data = JSON.parse(event.data);
              console.log("Received launcher status:", data);
              if (data.error) {
                  setError(data.error);
              }
              else {
                  const { installedLaunchers } = data;
                  setLauncherStatus({
                      installedLaunchers
                  });
              }
              setLoading(false);
          };
          socket.onerror = (error) => {
              console.error("WebSocket error:", error);
              setError("WebSocket error occurred while checking for launcher status.");
              setLoading(false);
          };
          socket.onclose = () => {
              console.log("WebSocket connection closed");
          };
          return () => {
              socket.close();
          };
      };
      React.useEffect(() => {
          const socketCleanup = fetchLauncherStatus();
          return () => {
              socketCleanup();
          };
      }, []);
      return { launcherStatus, error, loading };
  };

  const LauncherInstallModal = ({ closeModal, launcherOptions, serverAPI }) => {
      const { launcherStatus, error, loading } = useLauncherStatus(); // Use the hook to get launcher status
      const [progress, setProgress] = React.useState({ percent: 0, status: '', description: '' });
      const { settings, setAutoScan } = useSettings(serverAPI);
      const [options, setOptions] = React.useState(launcherOptions);
      const [separateAppIds, setSeparateAppIds] = React.useState(false);
      const [operation, setOperation] = React.useState("");
      const [showLog, setShowLog] = React.useState(false);
      const [triggerLogUpdates, setTriggerLogUpdates] = React.useState(false);
      const log = useLogUpdates(triggerLogUpdates);
      const [currentLauncher, setCurrentLauncher] = React.useState(null);
      const logContainerRef = React.useRef(null);
      // Pagination state
      const [currentPage, setCurrentPage] = React.useState(1);
      const itemsPerPage = 7;
      const indexOfLastLauncher = currentPage * itemsPerPage;
      const indexOfFirstLauncher = indexOfLastLauncher - itemsPerPage;
      const currentLaunchers = launcherOptions.slice(indexOfFirstLauncher, indexOfLastLauncher);
      const handleToggle = (changeName, changeValue) => {
          const newOptions = options.map(option => {
              if (option.name === changeName) {
                  return {
                      ...option,
                      enabled: changeValue,
                  };
              }
              else {
                  return option;
              }
          });
          setOptions(newOptions);
      };
      const handleSeparateAppIdsToggle = (value) => {
          setSeparateAppIds(value);
      };
      const handleInstallClick = async (operation) => {
          setOperation(operation);
          setShowLog(true);
          setTriggerLogUpdates(true);
          // Add a small delay to ensure WebSocket connection is established
          await new Promise(resolve => setTimeout(resolve, 100));
          const selectedLaunchers = options.filter(option => option.enabled && !option.streaming);
          let i = 0;
          let previousAutoScan = settings.autoscan;
          for (const launcher of selectedLaunchers) {
              if (!launcher.streaming) {
                  setAutoScan(false);
                  const launcherParam = (launcher.name.charAt(0).toUpperCase() + launcher.name.slice(1));
                  setCurrentLauncher(launcher);
                  // Reset log updates for each launcher
                  setTriggerLogUpdates(false);
                  await new Promise(resolve => setTimeout(resolve, 500));
                  setTriggerLogUpdates(true);
                  await installLauncher(launcherParam, launcher.label, i, operation);
              }
              i++;
          }
          scan();
          setAutoScan(previousAutoScan);
          if (settings.autoscan) {
              autoscan();
          }
      };
      const installLauncher = async (launcher, launcherLabel, index, operation) => {
          const total = options.filter(option => option.enabled).length;
          const startPercent = index === 0 ? 0 : index / total * 100;
          const endPercent = (index + 1) / total * 100;
          setProgress({
              percent: startPercent,
              status: `${operation}ing Launcher ${index + 1} of ${total}`,
              description: `${launcherLabel}`
          });
          try {
              const result = await serverAPI.callPluginMethod("install", {
                  selected_options: launcher,
                  operation: operation,
                  install_chrome: false,
                  separate_app_ids: separateAppIds,
                  start_fresh: false,
                  update_proton_ge: false,
                  nslgamesaves: false,
                  note: false,
                  up: false,
              });
              if (result) {
                  setProgress({ percent: endPercent, status: `${operation} Selection ${index + 1} of ${total}`, description: `${launcher}` });
                  notify.toast(`Launcher ${operation}ed`, `${launcherLabel} was ${operation.toLowerCase()}ed successfully!`);
              }
              else {
                  setProgress({ percent: endPercent, status: `${operation} selection ${index + 1} of ${total} failed`, description: `${operation} ${launcher} failed. See logs.` });
                  notify.toast(`${operation} Failed`, `${launcherLabel} was not ${operation.toLowerCase()}ed.`);
              }
          }
          catch (error) {
              setProgress({ percent: endPercent, status: `Installing selection ${index + 1} of ${total} failed`, description: `Installing ${launcher} failed. See logs.` });
              notify.toast("Install Failed", `${launcherLabel} was not installed.`);
              console.error('Error calling _main method on server-side plugin:', error);
          }
      };
      const cancelOperation = () => {
          setProgress({ percent: 0, status: '', description: '' });
          setShowLog(false);
          setTriggerLogUpdates(false);
          setCurrentLauncher(null);
      };
      // Pulsating animation style for lights
      const pulseStyle = (offset) => ({
          width: '12px',
          height: '12px',
          borderRadius: '50%',
          marginRight: '10px',
          backgroundColor: 'gray',
          opacity: 0.5 + Math.sin((Date.now() + offset) / 300) * 0.5,
          transition: 'opacity 0.3s ease', // Smooth transition for opacity change
      });
      const nextPage = () => {
          if (currentPage * itemsPerPage < launcherOptions.length) {
              setCurrentPage(prevPage => prevPage + 1);
          }
      };
      const prevPage = () => {
          if (currentPage > 1) {
              setCurrentPage(prevPage => prevPage - 1);
          }
      };
      // **Only remove the spinner here when loading status is true**
      if (loading) {
          return (window.SP_REACT.createElement(deckyFrontendLib.ModalRoot, { onCancel: closeModal },
              window.SP_REACT.createElement(deckyFrontendLib.DialogHeader, null, "Loading Launcher Status..."),
              window.SP_REACT.createElement(deckyFrontendLib.DialogBodyText, null, "Checking installed launchers..."),
              window.SP_REACT.createElement(deckyFrontendLib.DialogBody, null,
                  window.SP_REACT.createElement("div", { style: { display: 'flex', alignItems: 'center' } },
                      window.SP_REACT.createElement("span", { style: pulseStyle(0) }),
                      window.SP_REACT.createElement("span", { style: pulseStyle(100) }),
                      window.SP_REACT.createElement("span", { style: pulseStyle(200) })))));
      }
      if (error) {
          return (window.SP_REACT.createElement(deckyFrontendLib.ModalRoot, { onCancel: closeModal },
              window.SP_REACT.createElement(deckyFrontendLib.DialogHeader, null, "Error"),
              window.SP_REACT.createElement(deckyFrontendLib.DialogBodyText, null, error),
              window.SP_REACT.createElement(deckyFrontendLib.DialogBody, null,
                  window.SP_REACT.createElement(deckyFrontendLib.DialogButton, { onClick: closeModal }, "Close"))));
      }
      return ((progress.status !== '' && progress.percent < 100) ? (window.SP_REACT.createElement(deckyFrontendLib.ModalRoot, { onCancel: cancelOperation },
          window.SP_REACT.createElement(deckyFrontendLib.DialogHeader, null, `${operation}ing Game Launchers`),
          window.SP_REACT.createElement(deckyFrontendLib.DialogBodyText, null,
              "Selected options: ",
              options.filter(option => option.enabled).map(option => option.label).join(', ')),
          window.SP_REACT.createElement(deckyFrontendLib.DialogBody, null,
              window.SP_REACT.createElement(deckyFrontendLib.SteamSpinner, null),
              window.SP_REACT.createElement("div", { style: { display: 'flex', alignItems: 'center' } },
                  window.SP_REACT.createElement("div", { ref: logContainerRef, style: { flex: 1, marginRight: '10px', fontSize: 'small', whiteSpace: 'pre-wrap', overflowY: 'auto', maxHeight: '50px', height: '100px' } }, showLog && log),
                  window.SP_REACT.createElement(deckyFrontendLib.ProgressBarWithInfo, { layout: "inline", bottomSeparator: "none", sOperationText: progress.status, description: progress.description, nProgress: progress.percent, indeterminate: true })),
              currentLauncher && (window.SP_REACT.createElement("img", { src: currentLauncher.urlimage, alt: "Overlay", style: { position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', opacity: 0.5 } })),
              window.SP_REACT.createElement(deckyFrontendLib.DialogButton, { onClick: cancelOperation, style: { width: '25px', margin: 0, padding: '10px' } }, "Back")))) : (window.SP_REACT.createElement(deckyFrontendLib.ModalRoot, { onCancel: closeModal },
          window.SP_REACT.createElement(deckyFrontendLib.DialogHeader, null, "Select Game Launchers"),
          window.SP_REACT.createElement(deckyFrontendLib.DialogBodyText, null, "Here you choose your launchers you want to install and let NSL do the rest. Once installed, they will be added to your library!"),
          window.SP_REACT.createElement(deckyFrontendLib.DialogBody, null,
              window.SP_REACT.createElement("div", { style: { display: 'flex', justifyContent: 'space-between', marginBottom: '10px' } },
                  window.SP_REACT.createElement(deckyFrontendLib.DialogButton, { onClick: prevPage, disabled: currentPage === 1 }, "Previous"),
                  window.SP_REACT.createElement(deckyFrontendLib.DialogButton, { onClick: nextPage, disabled: currentPage * itemsPerPage >= launcherOptions.length }, "Next")),
              currentLaunchers.map(({ name, label }) => (window.SP_REACT.createElement("div", { key: name, style: { display: 'flex', justifyContent: 'space-between', alignItems: 'center' } },
                  window.SP_REACT.createElement("div", { style: { display: 'flex', alignItems: 'center' } },
                      window.SP_REACT.createElement("span", null, label),
                      window.SP_REACT.createElement("span", { style: {
                              width: '12px',
                              height: '12px',
                              borderRadius: '50%',
                              marginLeft: '10px',
                              backgroundColor: launcherStatus?.installedLaunchers.includes(name) ? 'green' : 'red',
                          } })),
                  window.SP_REACT.createElement(deckyFrontendLib.ToggleField, { checked: options.find(option => option.name === name)?.enabled ? true : false, onChange: (value) => handleToggle(name, value) })))),
              window.SP_REACT.createElement(deckyFrontendLib.DialogBodyText, { style: { fontSize: 'small', marginTop: '16px' } },
                  window.SP_REACT.createElement("b", null, "Note:"),
                  " When installing a launcher, the latest UMU/Proton-GE will attempt to be installed. If your launchers don't start, make sure force compatibility is checked (except for umu), shortcut properties are right, and your steam files are updated. Remember to also edit your controller layout configurations if necessary! If all else fails, restart your steam deck manually."),
              window.SP_REACT.createElement(deckyFrontendLib.DialogBodyText, { style: { fontSize: 'small', marginTop: '16px' } },
                  window.SP_REACT.createElement("b", null, "Note\u00B2:"),
                  " Some games won't run right away using NSL. Due to easy anti-cheat or quirks, you may need to manually tinker to get some games working or even sign in through desktop. NSL is simply another way to play! Happy Gaming!\u2665")),
          window.SP_REACT.createElement(deckyFrontendLib.Focusable, null,
              window.SP_REACT.createElement("div", { style: { display: 'flex', justifyContent: 'space-between', alignItems: 'center' } },
                  window.SP_REACT.createElement("div", { style: { display: 'flex', alignItems: 'center' } },
                      window.SP_REACT.createElement(deckyFrontendLib.DialogButton, { style: { width: "fit-content" }, onClick: () => handleInstallClick("Install"), disabled: options.every(option => option.enabled === false) }, "Install"),
                      window.SP_REACT.createElement(deckyFrontendLib.DialogButton, { style: { width: "fit-content", marginLeft: "10px", marginRight: "10px" }, onClick: () => handleInstallClick("Uninstall"), disabled: options.every(option => option.enabled === false) }, "Uninstall")),
                  window.SP_REACT.createElement(deckyFrontendLib.ToggleField, { label: "Separate Launcher Folders", checked: separateAppIds, onChange: handleSeparateAppIdsToggle }))))));
  };

  const StreamingInstallModal = ({ closeModal, streamingOptions, serverAPI }) => {
      const [progress, setProgress] = React.useState({ percent: 0, status: '', description: '' });
      const [options, setOptions] = React.useState(streamingOptions);
      const [currentStreamingSites, setCurrentStreamingSites] = React.useState([]);
      const [selectedBrowser, setSelectedBrowser] = React.useState(null); // NEW
      // Pagination state
      const [currentPage, setCurrentPage] = React.useState(1);
      const itemsPerPage = 7;
      const indexOfLastSite = currentPage * itemsPerPage;
      const indexOfFirstSite = indexOfLastSite - itemsPerPage;
      const currentSites = streamingOptions.slice(indexOfFirstSite, indexOfLastSite);
      const handleInstallClick = async () => {
          const selectedStreamingSites = options
              .filter(option => option.enabled && option.streaming)
              .map(option => ({
              siteName: option.label,
              siteURL: option.URL
          }));
          if (selectedStreamingSites.length > 0 && selectedBrowser) {
              const total = selectedStreamingSites.length;
              setProgress({
                  percent: 0,
                  status: `Installing ${total} Streaming Sites`,
                  description: `${selectedStreamingSites.map(site => site.siteName).join(', ')}`
              });
              setCurrentStreamingSites(options.filter(option => option.enabled && option.streaming));
              await installSite(selectedStreamingSites, serverAPI, { setProgress }, total, selectedBrowser);
          }
      };
      const handleToggle = (changeName, changeValue) => {
          const newOptions = options.map(option => {
              if (option.name === changeName) {
                  return {
                      ...option,
                      enabled: changeValue,
                  };
              }
              else {
                  return option;
              }
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
      // Browser Image Cycling
      const [currentImageIndex, setCurrentImageIndex] = React.useState(0);
      React.useEffect(() => {
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
      return ((progress.status !== '' && progress.percent < 100) ? (window.SP_REACT.createElement(deckyFrontendLib.ModalRoot, null,
          window.SP_REACT.createElement(deckyFrontendLib.DialogHeader, null, "Installing Streaming Sites"),
          window.SP_REACT.createElement(deckyFrontendLib.DialogBodyText, null,
              "Selected options: ",
              options.filter(option => option.enabled).map(option => option.label).join(', ')),
          window.SP_REACT.createElement(deckyFrontendLib.DialogBody, null,
              window.SP_REACT.createElement(deckyFrontendLib.SteamSpinner, null),
              window.SP_REACT.createElement(deckyFrontendLib.ProgressBarWithInfo, { layout: "inline", bottomSeparator: "none", sOperationText: progress.status, description: progress.description, nProgress: progress.percent, indeterminate: true }),
              currentStreamingSites.length > 0 && (window.SP_REACT.createElement("div", { style: fadeStyle })),
              window.SP_REACT.createElement(deckyFrontendLib.DialogButton, { onClick: cancelOperation, style: { width: '25px' } }, "Back")))) : (window.SP_REACT.createElement(deckyFrontendLib.ModalRoot, { onCancel: closeModal },
          window.SP_REACT.createElement(deckyFrontendLib.DialogHeader, null, "Install Game/Media Streaming Sites"),
          window.SP_REACT.createElement(deckyFrontendLib.DialogBody, null,
              window.SP_REACT.createElement("div", { style: { display: 'flex', flexDirection: 'row', flexWrap: 'wrap', gap: '1em', marginBottom: '1em', alignItems: 'center' } },
                  window.SP_REACT.createElement(deckyFrontendLib.ToggleField, { label: "Google Chrome", checked: selectedBrowser === "Google Chrome", onChange: () => setSelectedBrowser("Google Chrome") }),
                  window.SP_REACT.createElement(deckyFrontendLib.ToggleField, { label: "Firefox", checked: selectedBrowser === "Mozilla Firefox", onChange: () => setSelectedBrowser("Mozilla Firefox") }),
                  window.SP_REACT.createElement(deckyFrontendLib.ToggleField, { label: "Microsoft Edge", checked: selectedBrowser === "Microsoft Edge", onChange: () => setSelectedBrowser("Microsoft Edge") }),
                  window.SP_REACT.createElement(deckyFrontendLib.ToggleField, { label: "Brave", checked: selectedBrowser === "Brave", onChange: () => setSelectedBrowser("Brave") }))),
          window.SP_REACT.createElement(deckyFrontendLib.DialogBodyText, null, "NSL will install and use the selected browser to launch these sites. Non-Steam shortcuts will be created."),
          window.SP_REACT.createElement(deckyFrontendLib.DialogBody, null,
              window.SP_REACT.createElement("div", { style: { display: 'flex', justifyContent: 'space-between', marginBottom: '10px' } },
                  window.SP_REACT.createElement(deckyFrontendLib.DialogButton, { onClick: prevPage, disabled: currentPage === 1 }, "Previous"),
                  window.SP_REACT.createElement(deckyFrontendLib.DialogButton, { onClick: nextPage, disabled: currentPage * itemsPerPage >= streamingOptions.length }, "Next")),
              currentSites.map(({ name, label }) => (window.SP_REACT.createElement(deckyFrontendLib.ToggleField, { key: name, label: label, checked: options.find(option => option.name === name)?.enabled || false, onChange: (value) => handleToggle(name, value) })))),
          window.SP_REACT.createElement(deckyFrontendLib.Focusable, { style: { display: "flex", alignItems: "center", gap: "10px" } },
              window.SP_REACT.createElement(deckyFrontendLib.DialogButton, { style: { width: "fit-content" }, onClick: handleInstallClick, disabled: options.every(option => option.enabled === false) || !selectedBrowser }, "Install"),
              window.SP_REACT.createElement(deckyFrontendLib.DialogBodyText, { style: { fontSize: "small" } }, "Note: Be sure your selected browser is installed from Discover Store or SteamOS Desktop Mode.")))));
  };

  /**
  * The modal for selecting launchers.
  */
  const StartFreshModal = ({ closeModal, serverAPI }) => {
      const [progress, setProgress] = React.useState({ percent: 0, status: '', description: '' });
      const [firstConfirm, setFirstConfirm] = React.useState(false);
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
              }
              else {
                  setProgress({ percent: 100, status: 'wipe failed.', description: '' });
                  notify.toast("...there wasn't...Dingleberries!", "NSL failed to wipe. Check your logs.");
              }
          }
          catch (error) {
              setProgress({ percent: 100, status: 'wipe failed.', description: '' });
              notify.toast("NSL Wipe Failed", "Non Steam Launchers failed to wipe. Check your logs.");
              console.error('Error calling _main method on server-side plugin:', error);
          }
          closeModal();
      };
      return ((progress.status !== '' && progress.percent < 100) ?
          window.SP_REACT.createElement(deckyFrontendLib.ModalRoot, null,
              window.SP_REACT.createElement(deckyFrontendLib.DialogHeader, null, "Starting Fresh"),
              window.SP_REACT.createElement(deckyFrontendLib.DialogBodyText, null, "Removing all launchers and installed games from NonSteamLaunchers"),
              window.SP_REACT.createElement(deckyFrontendLib.DialogBody, null,
                  window.SP_REACT.createElement(deckyFrontendLib.SteamSpinner, null),
                  window.SP_REACT.createElement(deckyFrontendLib.ProgressBarWithInfo, { layout: "inline", bottomSeparator: "none", sOperationText: progress.status, description: progress.description, nProgress: progress.percent, indeterminate: true }))) :
          firstConfirm ?
              window.SP_REACT.createElement(deckyFrontendLib.ConfirmModal, { strTitle: "Oops... That Might Have Been a Mistake", strDescription: "This is your last chance! By continuing, you will be totally deleting the prefixes, which include the launchers and the games you downloaded, as well as your games. If you aren't sure if your game saves are backed up or if you have downloaded a very large game and would not like to have to re-download, please DO NOT CONTINUE. Everything will be wiped!", strOKButtonText: "Yes, I'm sure!", strCancelButtonText: "No, go back!", onOK: handleStartFreshClick, onCancel: () => setFirstConfirm(false) }) :
              window.SP_REACT.createElement(deckyFrontendLib.ConfirmModal, { strTitle: "Are You Sure?", strDescription: "Pressing Start Fresh will essentially uninstall NSL. It will delete and wipe all installed launchers and their games along with your game saves and NSL files. This is irreversible! You'll need to manually remove any shortcuts created.", strOKButtonText: "Yes, wipe!", strCancelButtonText: "No, go back!", onOK: () => setFirstConfirm(true), onCancel: closeModal }));
  };

  const UpdateRestartModal = ({ closeModal, serverAPI }) => {
      const [progress, setProgress] = React.useState({ percent: 0, status: '', description: '' });
      const [showRestartModal, setShowRestartModal] = React.useState(false);
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
              }
              else {
                  setProgress({ percent: 100, status: 'Update failed.', description: '' });
                  notify.toast("Update Failed", "Proton GE update failed. Check your logs.");
              }
          }
          catch (error) {
              setProgress({ percent: 100, status: 'Update failed.', description: '' });
              notify.toast("Update Failed", "Proton GE update failed. Check your logs.");
              console.error('Error calling update_proton_ge method on server-side plugin:', error);
          }
      };
      const handleRestartSteam = () => {
          SteamClient.User.StartRestart(false);
          setShowRestartModal(false);
          closeModal();
      };
      return (window.SP_REACT.createElement(window.SP_REACT.Fragment, null, progress.status !== '' && progress.percent < 100 ? (window.SP_REACT.createElement(deckyFrontendLib.ModalRoot, null,
          window.SP_REACT.createElement(deckyFrontendLib.DialogHeader, null, "Updating Proton GE"),
          window.SP_REACT.createElement(deckyFrontendLib.DialogBodyText, null, "Updating Proton GE to the latest version. Please wait..."),
          window.SP_REACT.createElement(deckyFrontendLib.DialogBody, null,
              window.SP_REACT.createElement(deckyFrontendLib.SteamSpinner, null),
              window.SP_REACT.createElement(deckyFrontendLib.ProgressBarWithInfo, { layout: "inline", bottomSeparator: "none", sOperationText: progress.status, description: progress.description, nProgress: progress.percent, indeterminate: true })))) : showRestartModal ? (window.SP_REACT.createElement(deckyFrontendLib.ConfirmModal, { strTitle: "Restart Steam", strDescription: "Updating Proton GE requires a restart of Steam for the changes to take effect. Would you like to restart Steam now?", strOKButtonText: "Restart", strCancelButtonText: "Back", onOK: handleRestartSteam, onCancel: () => setShowRestartModal(false) })) : (window.SP_REACT.createElement(deckyFrontendLib.ConfirmModal, { strTitle: "Update Proton GE", strDescription: "Would you like to update Proton GE to the latest version?", strOKButtonText: "Update", strCancelButtonText: "Cancel", onOK: handleUpdateProtonGEClick, onCancel: closeModal }))));
  };

  const RestoreGameSavesModal = ({ closeModal, serverAPI }) => {
      const [progress, setProgress] = React.useState({ percent: 0, status: '', description: '' });
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
                  nslgamesaves: true,
                  note: false,
                  up: false,
              });
              if (result) {
                  setProgress({ percent: 100, status: 'Game saves restored successfully!', description: '' });
                  notify.toast("Game saves restored successfully!", "Your game saves have been restored.");
              }
              else {
                  setProgress({ percent: 100, status: 'Restore failed.', description: '' });
                  notify.toast("Restore failed", "Failed to restore game saves. Check your logs.");
              }
          }
          catch (error) {
              setProgress({ percent: 100, status: 'Restore failed.', description: '' });
              notify.toast("Restore Failed", "Failed to restore game saves. Check your logs.");
              console.error('Error calling restore method on server-side plugin:', error);
          }
          closeModal();
      };
      return ((progress.status !== '' && progress.percent < 100) ?
          window.SP_REACT.createElement(deckyFrontendLib.ModalRoot, null,
              window.SP_REACT.createElement(deckyFrontendLib.DialogHeader, null, "Restoring Game Saves"),
              window.SP_REACT.createElement(deckyFrontendLib.DialogBodyText, null, "Restoring your game save backups..."),
              window.SP_REACT.createElement(deckyFrontendLib.DialogBody, null,
                  window.SP_REACT.createElement(deckyFrontendLib.SteamSpinner, null),
                  window.SP_REACT.createElement(deckyFrontendLib.ProgressBarWithInfo, { layout: "inline", bottomSeparator: "none", sOperationText: progress.status, description: progress.description, nProgress: progress.percent, indeterminate: true }))) :
          window.SP_REACT.createElement(deckyFrontendLib.ConfirmModal, { strTitle: "Restore Game Save Backups", strDescription: window.SP_REACT.createElement(window.SP_REACT.Fragment, null,
                  window.SP_REACT.createElement("div", { style: { fontSize: '14px', marginBottom: '8px' } }, "This feature will restore all your game save backups all at once, currently only for the default NonSteamLaunchers prefix."),
                  window.SP_REACT.createElement("div", { style: { fontSize: '14px', marginBottom: '8px' } },
                      window.SP_REACT.createElement("strong", null, "Ensure all necessary launchers are installed, but do not download the games,"),
                      " as this will avoid local conflicts. Only continue if you have wiped everything using Start Fresh and you know for a fact that your game saves are backed up at /home/deck/NSLGameSaves."),
                  window.SP_REACT.createElement("div", { style: { fontSize: '14px', marginBottom: '8px' } },
                      "Some games don't have local save backups:",
                      window.SP_REACT.createElement("ul", { style: { paddingLeft: '16px' } },
                          window.SP_REACT.createElement("li", { style: { fontSize: '12px' } }, "NSL uses Ludusavi to backup and restore your local game saves."),
                          window.SP_REACT.createElement("li", { style: { fontSize: '12px' } }, "Some launchers handle local and cloud saves themselves so this will vary on a game to game basis."),
                          window.SP_REACT.createElement("li", { style: { fontSize: '12px', wordWrap: 'break-word' } }, "Ludusavi may need manual configuration here if more paths are needed: /home/deck/.var/app/com.github.mtkennerly.ludusavi/config/ludusavi/NSLconfig/config.yaml"))),
                  window.SP_REACT.createElement("div", { style: { fontSize: '14px' } }, "Press restore when ready.")), strOKButtonText: "Restore Game Saves", strCancelButtonText: "Cancel", onOK: handleRestoreClick, onCancel: closeModal }));
  };

  const useUpdateInfo = () => {
      const [updateInfo, setUpdateInfo] = React.useState(null);
      const [error, setError] = React.useState(null);
      const [loading, setLoading] = React.useState(true);
      // WebSocket connection to check for updates
      const fetchUpdateInfo = () => {
          setLoading(true);
          console.log("Connecting to WebSocket to check for updates...");
          const socket = new WebSocket("ws://localhost:8675/check_update");
          socket.onopen = () => {
              console.log("WebSocket connected to check update");
          };
          socket.onmessage = (event) => {
              const data = JSON.parse(event.data);
              console.log("Received update information:", data);
              if (data.error) {
                  setError(data.error);
              }
              else {
                  const { status, local_version, github_version, patch_notes } = data;
                  setUpdateInfo({
                      status,
                      local_version,
                      github_version,
                      patch_notes, // Now we also store the patch notes
                  });
              }
              setLoading(false);
          };
          socket.onerror = (error) => {
              console.error("WebSocket error:", error);
              setError("WebSocket error occurred while checking for updates.");
              setLoading(false);
          };
          socket.onclose = () => {
              console.log("WebSocket connection closed");
          };
          return () => {
              socket.close();
          };
      };
      React.useEffect(() => {
          const socketCleanup = fetchUpdateInfo();
          return () => {
              socketCleanup();
          };
      }, []);
      return { updateInfo, error, loading };
  };

  const sitesList = [
      {
          name: 'epicGames',
          label: 'Epic Games',
          URL: '',
          streaming: false,
          enabled: false,
          urlimage: 'https://cdn2.steamgriddb.com/hero_thumb/164fbf608021ece8933758ee2b28dd7d.jpg'
      },
      {
          name: 'gogGalaxy',
          label: 'Gog Galaxy',
          URL: '',
          streaming: false,
          enabled: false,
          urlimage: 'https://cdn2.steamgriddb.com/hero_thumb/ce016f59ecc2366a43e1c96a4774d167.jpg'
      },
      {
          name: 'uplay',
          label: 'Ubisoft Connect',
          URL: '',
          streaming: false,
          enabled: false,
          urlimage: 'https://cdn2.steamgriddb.com/hero_thumb/525d57e5f56f04be298e821454ced9bc.png'
      },
      {
          name: 'battleNet',
          label: 'Battle.net',
          URL: '',
          streaming: false,
          enabled: false,
          urlimage: 'https://cdn2.steamgriddb.com/hero_thumb/9f319422ca17b1082ea49820353f14ab.jpg'
      },
      {
          name: 'amazonGames',
          label: 'Amazon Games',
          URL: '',
          streaming: false,
          enabled: false,
          urlimage: 'https://cdn2.steamgriddb.com/hero_thumb/a70145bf8b173e4496b554ce57969e24.jpg'
      },
      {
          name: 'eaApp',
          label: 'EA App',
          URL: '',
          streaming: false,
          enabled: false,
          urlimage: 'https://cdn2.steamgriddb.com/hero_thumb/6458ed5e1bb03b8da47c065c2f647b26.jpg'
      },
      {
          name: 'legacyGames',
          label: 'Legacy Games',
          URL: '',
          streaming: false,
          enabled: false,
          urlimage: 'https://cdn2.steamgriddb.com/thumb/86cfeb447e7f474a00adb7423c605875.jpg'
      },
      {
          name: 'itchIo',
          label: 'Itch.io',
          URL: '',
          streaming: false,
          enabled: false,
          urlimage: 'https://i.pcmag.com/imagery/reviews/044PXMK6FlED1dNwOXkecXV-4.fit_scale.size_1028x578.v1597354669.jpg'
      },
      {
          name: 'humbleGames',
          label: 'Humble Bundle',
          URL: '',
          streaming: false,
          enabled: false,
          urlimage: 'https://cdn2.steamgriddb.com/thumb/4cb3ded67cb7a539395ab873354a01c1.jpg'
      },
      {
          name: 'indieGala',
          label: 'IndieGala Client',
          URL: '',
          streaming: false,
          enabled: false,
          urlimage: 'https://cdn2.steamgriddb.com/thumb/8348173ba70a643e9d0077c1605ce0ad.jpg'
      },
      {
          name: 'rockstarGamesLauncher',
          label: 'Rockstar Games Launcher',
          URL: '',
          streaming: false,
          enabled: false,
          urlimage: 'https://cdn2.steamgriddb.com/hero_thumb/60b4ddba6215df686ff6ab71d0c078e9.jpg'
      },
      {
          name: 'psPlus',
          label: 'Playstation Plus',
          URL: '',
          streaming: false,
          enabled: false,
          urlimage: 'https://cdn2.steamgriddb.com/thumb/6c037a13a7e2d089a0f88f86b6405daf.jpg'
      },
      {
          name: 'hoyoPlay',
          label: 'HoYoPlay',
          URL: '',
          streaming: false,
          enabled: false,
          urlimage: 'https://cdn2.steamgriddb.com/thumb/3a4cffbfa1ae7220344b83ea754c46c4.jpg'
      },
      {
          name: 'vkPlay',
          label: 'VK Play',
          URL: '',
          streaming: false,
          enabled: false,
          urlimage: 'https://cdn2.steamgriddb.com/thumb/b14d72b2a45fcf11d85120375d542982.jpg'
      },
      {
          name: 'gameJoltClient',
          label: 'Game Jolt Client',
          URL: '',
          streaming: false,
          enabled: false,
          urlimage: 'https://cdn2.steamgriddb.com/thumb/bfb3206155832047330e55a331d6734e.jpg'
      },
      {
          name: 'artixGameLauncher',
          label: 'Artix Game Launcher',
          URL: '',
          streaming: false,
          enabled: false,
          urlimage: 'https://cdn2.steamgriddb.com/thumb/95ecb48a87cec666759152b68ed9a272.jpg'
      },
      {
          name: 'pokémonTradingCardGameLive',
          label: 'Pokémon Trading Card Game Live',
          URL: '',
          streaming: false,
          enabled: false,
          urlimage: 'https://cdn2.steamgriddb.com/hero_thumb/6494a35bdfaec8c96f1a0103fa6c3fd7.jpg'
      },
      {
          name: 'minecraftLauncher',
          label: 'Minecraft Launcher',
          URL: '',
          streaming: false,
          enabled: false,
          urlimage: 'https://cdn2.steamgriddb.com/thumb/7469578bd8aad76c5351f927619d8e4a.jpg'
      },
      {
          name: 'antstreamArcade',
          label: 'Antstream Arcade',
          URL: '',
          streaming: false,
          enabled: false,
          urlimage: 'https://cdn2.steamgriddb.com/thumb/99778cb32ccfe54604d7aa2bc412b367.jpg'
      },
      {
          name: 'vfunLauncher',
          label: 'VFUN Launcher',
          URL: '',
          streaming: false,
          enabled: false,
          urlimage: 'https://file.qijisoft.com/Valofe_file/web/vfun/images/funny-download-gude.png'
      },
      {
          name: 'tempoLauncher',
          label: 'Tempo Launcher',
          URL: '',
          streaming: false,
          enabled: false,
          urlimage: 'https://cdn.tempogames.com/wp-content/uploads/2020/02/article-tempo-raise2.jpg'
      },
      {
          name: 'nvidiaGeForcenow',
          label: 'NVIDIA GeForce NOW',
          URL: '',
          streaming: false,
          enabled: false,
          urlimage: 'https://cdn2.steamgriddb.com/hero_thumb/b2619bbe281deeefea3675dfed719fd7.jpg'
      },
      {
          name: 'moonlightGameStreaming',
          label: 'Moonlight Game Streaming',
          URL: '',
          streaming: false,
          enabled: false,
          urlimage: 'https://cdn2.steamgriddb.com/thumb/c4733f77978b2975811dbd622d32553c.png'
      },
      {
          name: 'remotePlayWhatever',
          label: 'RemotePlayWhatever',
          URL: '',
          streaming: false,
          enabled: false,
          urlimage: 'https://opengraph.githubassets.com/68a584618d805217b103796afb7b13309abf7f9199e7299c9d31d4402184e963/m4dEngi/RemotePlayWhatever'
      },
      //these are streaming sites vvv
      {
          name: 'xboxGamePass',
          label: 'Xbox Game Pass',
          URL: 'https://www.xbox.com/play',
          streaming: true,
          enabled: false,
          urlimage: 'https://cdn2.steamgriddb.com/hero_thumb/167b7d08b38facb1c06185861a5845dd.jpg'
      },
      {
          name: 'xcloud',
          label: 'Better xCloud',
          URL: 'https://better-xcloud.github.io',
          streaming: true,
          enabled: false,
          urlimage: 'https://raw.githubusercontent.com/redphx/better-xcloud/refs/heads/typescript/resources/logos/better-xcloud.png'
      },
      {
          name: 'fortnite',
          label: 'Fortnite (xCloud)',
          URL: 'https://www.xbox.com/en-US/play/games/fortnite/BT5P2X999VH2',
          streaming: true,
          enabled: false,
          urlimage: 'https://cdn2.steamgriddb.com/hero_thumb/560cc70f255b94b8408709e810914593.jpg'
      },
      {
          name: 'venge',
          label: 'Venge',
          URL: 'https://www.venge.io',
          streaming: true,
          enabled: false,
          urlimage: 'https://cdn.webgamer.io/games/venge-io/venge-io.960x.50pc.avif'
      },
      {
          name: 'pokerogue',
          label: 'PokéRogue',
          URL: 'https://www.pokerogue.net',
          streaming: true,
          enabled: false,
          urlimage: 'https://cdn2.steamgriddb.com/thumb/a2ef91e05d923e48e5f1ad1826cb77de.jpg'
      },
      {
          name: 'geforceNow',
          label: 'GeForce Now',
          URL: 'https://play.geforcenow.com',
          streaming: true,
          enabled: false,
          urlimage: 'https://cdn2.steamgriddb.com/hero_thumb/5e7e6e76699ea804c65b0c37974c660c.jpg'
      },
      {
          name: 'amazonLuna',
          label: 'Amazon Luna',
          URL: 'https://luna.amazon.com',
          streaming: true,
          enabled: false,
          urlimage: 'https://cdn2.steamgriddb.com/thumb/5966577c1d725b37c26c3f7aa493dd9c.jpg'
      },
      {
          name: 'boosteroid',
          label: 'Boosteroid Cloud Gaming',
          URL: 'https://cloud.boosteroid.com',
          streaming: true,
          enabled: false,
          urlimage: 'https://cdn2.steamgriddb.com/thumb/6a9a434f1c711791a03757058f7539b2.jpg'
      },
      {
          name: 'stimio',
          label: 'Stim.io',
          URL: 'https://stim.io',
          streaming: true,
          enabled: false,
          urlimage: 'https://www.pixellair.ir/storage/images/general/2023/09/4nPPPbeckctibtF3QuSledSlWvCM4JlpyeB5YeLq.jpg'
      },
      {
          name: 'webRcade',
          label: 'WebRcade',
          URL: 'https://play.webrcade.com',
          streaming: true,
          enabled: false,
          urlimage: 'https://cdn2.steamgriddb.com/thumb/f9b8cc42051c6d1c1ddaf5260118d585.jpg'
      },
      {
          name: 'webRcadeeditor',
          label: 'WebRcade (Editor)',
          URL: 'https://editor.webrcade.com',
          streaming: true,
          enabled: false,
          urlimage: 'https://cdn2.steamgriddb.com/thumb/f9b8cc42051c6d1c1ddaf5260118d585.jpg'
      },
      {
          name: 'afterplay.io',
          label: 'Afterplay.io',
          URL: 'https://afterplay.io/play/recently-played',
          streaming: true,
          enabled: false,
          urlimage: 'https://cdn2.steamgriddb.com/thumb/4a756de6acd2c74629b778156dcdeaf6.jpg'
      },
      {
          name: 'oneplay',
          label: 'OnePlay',
          URL: 'https://www.oneplay.in/dashboard/home',
          streaming: true,
          enabled: false,
          urlimage: 'https://sm.ign.com/t/ign_in/screenshot/default/oneplay_vzqc.1280.jpg'
      },
      {
          name: 'airGPU',
          label: 'AirGPU',
          URL: 'https://app.airgpu.com',
          streaming: true,
          enabled: false,
          urlimage: 'https://miro.medium.com/v2/resize:fit:784/1*bddIlLtmPp1o2jIIROYmVg@2x.jpeg'
      },
      {
          name: 'cloudDeck',
          label: 'CloudDeck',
          URL: 'https://clouddeck.app',
          streaming: true,
          enabled: false,
          urlimage: 'https://clouddeck.app/images/og-banner.png'
      },
      {
          name: 'jioGamesCloud',
          label: 'JioGamesCloud',
          URL: 'https://cloudplay.jiogames.com',
          streaming: true,
          enabled: false,
          urlimage: 'https://www.itvoice.in/wp-content/uploads/2022/11/jiogamescloud-1.jpg'
      },
      {
          name: 'watchparty',
          label: 'WatchParty',
          URL: 'https://watchparty.me',
          streaming: true,
          enabled: false,
          urlimage: 'https://image.pitchbook.com/CeBku52aTdNEWfTYrYi6cJF7Wjw1685029685197_200x200'
      },
      {
          name: 'rocketcrab',
          label: 'Rocketcrab',
          URL: 'https://rocketcrab.com',
          streaming: true,
          enabled: false,
          urlimage: 'https://d4.alternativeto.net/zfCT_UX_vwVPJeNiyNJ_htkj1lXoP3XhOQFeim4X1kg/rs:fill:618:394:1/g:no:0:0/YWJzOi8vZGlzdC9zL3JvY2tldGNyYWJfMTU1NzExX2Z1bGwucG5n.jpg'
      },
      {
          name: 'netflix',
          label: 'Netflix',
          URL: 'https://www.netflix.com',
          streaming: true,
          enabled: false,
          urlimage: 'https://cdn2.steamgriddb.com/hero_thumb/119f6887f5ebfd6d5b40213819263e68.jpg'
      },
      {
          name: 'hulu',
          label: 'Hulu',
          URL: 'https://www.hulu.com/welcome',
          streaming: true,
          enabled: false,
          urlimage: 'https://cdn2.steamgriddb.com/thumb/4bbddbaea593148384a27a8dcf498d30.jpg'
      },
      {
          name: 'disneyPlus',
          label: 'Disney+',
          URL: 'https://www.disneyplus.com',
          streaming: true,
          enabled: false,
          urlimage: 'https://cdn2.steamgriddb.com/hero_thumb/0dad24dc5419076f64f2ba93833b354e.png'
      },
      {
          name: 'amazonPrimeVideo',
          label: 'Amazon Prime Video',
          URL: 'https://www.amazon.com/primevideo',
          streaming: true,
          enabled: false,
          urlimage: 'https://cdn2.steamgriddb.com/hero_thumb/5e7cefa9b606dcd7b0faa082d82cdb1d.jpg'
      },
      {
          name: 'plex',
          label: 'Plex',
          URL: 'https://app.plex.tv/desktop/#!',
          streaming: true,
          enabled: false,
          urlimage: 'https://cdn2.steamgriddb.com/thumb/7c8db737a231930514b03b61dda48c60.jpg'
      },
      {
          name: 'tubi',
          label: 'Tubi',
          URL: 'https://tubitv.com',
          streaming: true,
          enabled: false,
          urlimage: 'https://cdn2.steamgriddb.com/thumb/225608983dc66adb163c3a64b6b42f91.jpg'
      },
      {
          name: 'youtube',
          label: 'Youtube',
          URL: 'https://www.youtube.com',
          streaming: true,
          enabled: false,
          urlimage: 'https://cdn2.steamgriddb.com/thumb/786929ce1b2e187510aca9b04a0f7254.jpg'
      },
      {
          name: 'youtubetv',
          label: 'Youtube TV',
          URL: 'https://youtube.com/tv',
          streaming: true,
          enabled: false,
          urlimage: 'https://cdn2.steamgriddb.com/thumb/dcd0d3f52fb67634fabc703a77a67adf.jpg'
      },
      {
          name: 'crunchyroll',
          label: 'Crunchyroll',
          URL: 'https://www.crunchyroll.com',
          streaming: true,
          enabled: false,
          urlimage: 'https://cdn2.steamgriddb.com/thumb/b51869faee0c2357dc5c2c34e4229a80.jpg'
      },
      {
          name: 'appletv+',
          label: 'Apple TV+',
          URL: 'https://tv.apple.com',
          streaming: true,
          enabled: false,
          urlimage: 'https://cdn2.steamgriddb.com/thumb/305aefb84d348c156953f7a3d4aa3e04.jpg'
      },
      {
          name: 'twitch',
          label: 'Twitch',
          URL: 'https://www.twitch.tv',
          streaming: true,
          enabled: false,
          urlimage: 'https://cdn2.steamgriddb.com/thumb/72f0b767094fe8e24d620a2273bd0839.jpg'
      },
      {
          name: 'youtubetvop',
          label: 'Youtube TV On PC - Chrome Extention',
          URL: 'https://chromewebstore.google.com/detail/youtube-tv-on-pc/jldjbkccldgbegjpggphaeikombjmnkh',
          streaming: true,
          enabled: false,
          urlimage: 'https://lh3.googleusercontent.com/jfMbVQOIE7EDFxu-ra7Y46FDOH2nfI43FSryGSbEbroeCH6R6BSKwE8Kv1VXS95T4NrBKjDCW6sWd5zQNT--XF8PBw=s800-w800-h500'
      },
      {
          name: 'youtubetesb',
          label: 'SponsorBlock for YouTube - Chrome Extention',
          URL: 'https://chromewebstore.google.com/detail/sponsorblock-for-youtube/mnjggcdmjocbbbhaepdhchncahnbgone?hl=en',
          streaming: true,
          enabled: false,
          urlimage: 'https://lh3.googleusercontent.com/5DLjcuawqvkoKXDfF0c3xBrKjbb_7yQTrlIFcAYyYN8F8AX-96zWrgLo7oCPitwIYJRTJhvJFrh6GCfxOH3T_rPq9w=s1280-w1280-h800'
      },
      {
          name: 'tampermonkey',
          label: 'Tampermonkey - Chrome Extention',
          URL: 'https://chromewebstore.google.com/detail/tampermonkey/dhdgffkkebhmkfjojejmpbldmpobfkfo',
          streaming: true,
          enabled: false,
          urlimage: 'https://img.youtube.com/vi/8tyjJD65zws/hqdefault.jpg'
      },
      {
          name: 'ublockorigin',
          label: 'uBlock Origin Lite - Chrome Extention',
          URL: 'https://chromewebstore.google.com/detail/ublock-origin-lite/ddkjiahejlhfcafbddmgiahcphecmpfh',
          streaming: true,
          enabled: false,
          urlimage: 'https://lh3.googleusercontent.com/-N63B4vtE95U5gL54hJGsNbeWiIKZRLBRKi8BlIeXHLXP8rLuMAQ7zmHmUD4AVpS-lu2ObY_VFgvhaAsLWK9aG70be0=s800-w800-h500'
      },
      {
          name: 'adblock',
          label: 'AdBlock - Chrome Extention',
          URL: 'https://chromewebstore.google.com/detail/adblock-%E2%80%94-block-ads-acros/gighmmpiobklfepjocnamgkkbiglidom?hl=en-US',
          streaming: true,
          enabled: false,
          urlimage: 'https://lh3.googleusercontent.com/tLNJkVOBBNQ_Ux1_9bjgkPn66WJfZNRpzcnJdDMA1bW2FYN0qWqJro81KxtdYjcpSlJohQMJUR4RHPKSjbLV1i-iLQ=s800-w800-h500'
      },
  ];

  const UpdateNotesModal = ({ closeModal, serverAPI }) => {
      const [progress, setProgress] = React.useState({ percent: 0, status: '', description: '' });
      const [showRestartModal, setShowRestartModal] = React.useState(false);
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
              }
              else {
                  setProgress({ percent: 100, status: 'Failed to send notes.', description: '' });
                  notify.toast("Sending Failed", "Failed to send notes. Please check the logs for details.");
              }
          }
          catch (error) {
              setProgress({ percent: 100, status: 'Failed to send notes.', description: '' });
              notify.toast("Sending Failed", "An error occurred while sending your notes. Check the logs.");
              console.error('Error calling note method on server-side plugin:', error);
          }
      };
      const handleRestartSteam = () => {
          SteamClient.User.StartRestart(false);
          setShowRestartModal(false);
          closeModal();
      };
      return (window.SP_REACT.createElement(window.SP_REACT.Fragment, null, progress.status !== '' && progress.percent < 100 ? (window.SP_REACT.createElement(deckyFrontendLib.ModalRoot, null,
          window.SP_REACT.createElement(deckyFrontendLib.DialogHeader, null, "Sending Your Notes!"),
          window.SP_REACT.createElement(deckyFrontendLib.DialogBodyText, null, "Please wait while your notes are being sent to the community..."),
          window.SP_REACT.createElement(deckyFrontendLib.DialogBody, null,
              window.SP_REACT.createElement(deckyFrontendLib.SteamSpinner, null),
              window.SP_REACT.createElement(deckyFrontendLib.ProgressBarWithInfo, { layout: "inline", bottomSeparator: "none", sOperationText: progress.status, description: progress.description, nProgress: progress.percent, indeterminate: true })))) : showRestartModal ? (window.SP_REACT.createElement(deckyFrontendLib.ConfirmModal, { strTitle: "Restart Steam", strDescription: "Your notes have been sent successfully! To see the notes in the community, Steam must be restarted. Would you like to restart Steam now?", strOKButtonText: "Restart Steam", strCancelButtonText: "Back", onOK: handleRestartSteam, onCancel: () => setShowRestartModal(false) })) : (window.SP_REACT.createElement(deckyFrontendLib.ConfirmModal, { strTitle: "Send Your Note!", strDescription: `Welcome to #noteSteamLaunchers! By creating a note for your non-Steam game and using the "#nsl" tag at the start of your note, you can share it with the community. All notes from participants will be visible in the "NSL Community Notes" for that specific game. Feel free to give this experimental feature a try! Would you like to send your #nsl note to the community and receive some notes back in return?`, strOKButtonText: "Send Notes", strCancelButtonText: "Cancel", onOK: handleSendNotesClick, onCancel: closeModal }))));
  };

  const STORAGE_KEY = "realPlaytimeData";
  let memoryCache = null;
  const appliedSessions = {};
  let playtimeEnabled = true;
  // --- Utility functions ---
  function isValidPlaytimeDataEntry(entry) {
      return (typeof entry === "object" &&
          entry !== null &&
          typeof entry.total === "number" &&
          typeof entry.lastSessionEnd === "number");
  }
  function sanitizePlaytimeData(data) {
      if (typeof data !== "object" || data === null)
          return {};
      const cleaned = {};
      for (const [key, value] of Object.entries(data)) {
          if (isValidPlaytimeDataEntry(value))
              cleaned[key] = value;
      }
      return cleaned;
  }
  function loadPlaytimeData() {
      try {
          if (memoryCache)
              return memoryCache;
          const raw = localStorage.getItem(STORAGE_KEY);
          if (!raw) {
              memoryCache = {};
              return memoryCache;
          }
          const parsed = JSON.parse(raw);
          const cleaned = sanitizePlaytimeData(parsed);
          if (Object.keys(cleaned).length !== Object.keys(parsed || {}).length) {
              savePlaytimeData(cleaned);
          }
          memoryCache = cleaned;
          return memoryCache;
      }
      catch {
          memoryCache = {};
          return memoryCache;
      }
  }
  function savePlaytimeData(data) {
      try {
          const latestFromStorage = JSON.parse(localStorage.getItem(STORAGE_KEY) || "{}");
          const merged = { ...latestFromStorage, ...data };
          memoryCache = merged;
          localStorage.setItem(STORAGE_KEY, JSON.stringify(merged));
      }
      catch {
          memoryCache = data;
          localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
      }
  }
  function isEnvironmentReady() {
      try {
          localStorage.setItem("__rp_test__", "1");
          localStorage.removeItem("__rp_test__");
          if (!window.appStore || typeof window.appStore.GetAppOverviewByAppID !== "function")
              return false;
          if (!window.appInfoStore)
              return false;
          return true;
      }
      catch {
          return false;
      }
  }
  // --- Playtime logic ---
  function restoreSavedPlaytimes() {
      if (!playtimeEnabled)
          return;
      const data = loadPlaytimeData();
      if (!window.appStore?.GetAppOverviewByAppID)
          return;
      let removedCount = 0;
      for (const [id, entry] of Object.entries(data)) {
          const ov = appStore.GetAppOverviewByAppID(Number(id));
          if (ov) {
              ov.minutes_playtime_forever = Math.max(ov.minutes_playtime_forever || 0, entry.total);
              ov.minutes_playtime_last_two_weeks = Math.max(ov.minutes_playtime_last_two_weeks || 0, entry.total);
              ov.nPlaytimeForever = Math.max(ov.nPlaytimeForever || 0, entry.total);
              ov.TriggerChange?.();
          }
          else {
              delete data[id];
              removedCount++;
          }
      }
      if (removedCount > 0)
          savePlaytimeData(data);
  }
  function applyRealSessionToOverview(appOverview) {
      if (!playtimeEnabled)
          return false;
      try {
          if (!appOverview || appOverview.app_type !== 1073741824)
              return false;
          const start = appOverview.rt_last_time_played;
          const end = appOverview.rt_last_time_locally_played;
          if (!start || !end || end <= start)
              return false;
          const appId = String(appOverview.appid || appOverview.appid?.() || appOverview.appId);
          const sessionSeconds = end - start;
          const sessionMinutes = Math.floor(sessionSeconds / 60);
          if (sessionMinutes <= 0)
              return false;
          const data = loadPlaytimeData();
          const prevEntry = data[appId] || { total: 0, lastSessionEnd: 0 };
          const effectiveEnd = Math.max(prevEntry.lastSessionEnd, end);
          const addedMinutes = effectiveEnd > prevEntry.lastSessionEnd ? sessionMinutes : 0;
          const newTotal = prevEntry.total + addedMinutes;
          if (newTotal === prevEntry.total)
              return false;
          data[appId] = { total: newTotal, lastSessionEnd: effectiveEnd };
          savePlaytimeData(data);
          appliedSessions[appId] = effectiveEnd;
          appOverview.minutes_playtime_forever = newTotal;
          appOverview.minutes_playtime_last_two_weeks = newTotal;
          appOverview.nPlaytimeForever = newTotal;
          appOverview.TriggerChange?.();
          return true;
      }
      catch {
          return false;
      }
  }
  // --- Patch/unpatch functions ---
  function patchAppStore() {
      if (!window.appStore?.m_mapApps)
          return;
      if (appStore.m_mapApps._originalSet)
          return;
      appStore.m_mapApps._originalSet = appStore.m_mapApps.set;
      appStore.m_mapApps.set = function (appId, appOverview) {
          const result = appStore.m_mapApps._originalSet.call(this, appId, appOverview);
          restoreSavedPlaytimes();
          applyRealSessionToOverview(appOverview);
          return result;
      };
  }
  function unpatchAppStore() {
      if (window.appStore?.m_mapApps?._originalSet) {
          appStore.m_mapApps.set = appStore.m_mapApps._originalSet;
          delete appStore.m_mapApps._originalSet;
      }
  }
  function patchAppInfoStore() {
      if (!window.appInfoStore)
          return;
      if (appInfoStore._originalOnAppOverviewChange)
          return;
      appInfoStore._originalOnAppOverviewChange = appInfoStore.OnAppOverviewChange;
      appInfoStore.OnAppOverviewChange = function (apps) {
          for (const a of apps || []) {
              const id = typeof a?.appid === "function" ? a.appid() : a?.appid;
              const overview = id && appStore?.GetAppOverviewByAppID
                  ? appStore.GetAppOverviewByAppID(Number(id))
                  : a;
              if (overview) {
                  restoreSavedPlaytimes();
                  applyRealSessionToOverview(overview);
              }
          }
          return appInfoStore._originalOnAppOverviewChange.call(this, apps);
      };
  }
  function unpatchAppInfoStore() {
      if (window.appInfoStore?._originalOnAppOverviewChange) {
          appInfoStore.OnAppOverviewChange = appInfoStore._originalOnAppOverviewChange;
          delete appInfoStore._originalOnAppOverviewChange;
      }
  }
  function manualPatch() {
      if (!playtimeEnabled)
          return;
      try {
          const m = location.pathname.match(/\/library\/app\/(\d+)/);
          if (m) {
              const id = Number(m[1]);
              const ov = appStore.GetAppOverviewByAppID(id);
              if (ov) {
                  restoreSavedPlaytimes();
                  applyRealSessionToOverview(ov);
                  appInfoStore?.OnAppOverviewChange?.([ov]);
              }
          }
      }
      catch { }
  }
  // --- Public API ---
  function setPlaytimeEnabled(enabled) {
      playtimeEnabled = enabled;
      if (!enabled) {
          // unpatch if disabled
          unpatchAppStore();
          unpatchAppInfoStore();
      }
      else {
          // re-patch if enabled
          patchAppStore();
          patchAppInfoStore();
          manualPatch();
      }
  }
  function initRealPlaytime(enabled = true, retryCount = 0) {
      setPlaytimeEnabled(enabled);
      if (!isEnvironmentReady()) {
          if (retryCount < 100) {
              setTimeout(() => initRealPlaytime(enabled, retryCount + 1), 1000);
          }
          return;
      }
      try {
          setTimeout(() => {
              restoreSavedPlaytimes();
              patchAppStore();
              patchAppInfoStore();
              manualPatch();
          }, 100);
      }
      catch { }
  }

  let ytAudioIframe = null;
  let ytPlayer = null; // untyped on purpose
  let fadeInterval = null;
  let currentQuery = null;
  let themeMusicInitialized = false;
  let debounceTimer = null;
  const sessionCache = new Map();
  const CACHE_EXPIRATION = 7 * 24 * 60 * 60 * 1000; // 7 days
  const LOCAL_STORAGE_KEY = "ThemeMusicData";
  const initThemeMusic = () => {
      // prevent double initialization (useful for hot reloads or SPA re-exec)
      if (themeMusicInitialized || window.__themeMusicInitialized)
          return;
      themeMusicInitialized = true;
      window.__themeMusicInitialized = true;
      console.log("[Init] Theme music initialized");
      if (!window.YT) {
          const script = document.createElement("script");
          script.src = "https://www.youtube.com/iframe_api";
          document.head.appendChild(script);
          console.log("[Init] Injected YouTube IFrame API script");
      }
      const debounce = (fn, delay = 300) => {
          if (debounceTimer)
              clearTimeout(debounceTimer);
          debounceTimer = window.setTimeout(fn, delay);
      };
      const waitForYouTubeAPI = async () => {
          if (window.YT && window.YT.Player)
              return;
          console.log("[Init] Waiting for YouTube API to load...");
          await new Promise((resolve) => {
              window.onYouTubeIframeAPIReady = () => {
                  console.log("[Init] YouTube API ready");
                  resolve();
              };
          });
      };
      const loadCache = () => {
          try {
              return JSON.parse(localStorage.getItem(LOCAL_STORAGE_KEY) || "{}");
          }
          catch {
              return {};
          }
      };
      const saveCache = (data) => {
          localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify(data));
      };
      const getCachedVideo = (query) => {
          const sessionHit = sessionCache.get(query);
          if (sessionHit)
              return sessionHit;
          const cache = loadCache();
          const entry = cache[query];
          if (!entry)
              return null;
          if (Date.now() - entry.timestamp > CACHE_EXPIRATION) {
              delete cache[query];
              saveCache(cache);
              return null;
          }
          sessionCache.set(query, entry.videoId);
          return entry.videoId;
      };
      const storeCachedVideo = (query, videoId) => {
          const cache = loadCache();
          cache[query] = { videoId, timestamp: Date.now() };
          saveCache(cache);
          sessionCache.set(query, videoId);
      };
      const fadeOutAndStop = async () => new Promise((resolve) => {
          if (!ytPlayer)
              return resolve();
          console.log("[Audio] Fading out...");
          let volume = 100;
          clearInterval(fadeInterval);
          fadeInterval = window.setInterval(() => {
              if (!ytPlayer)
                  return cleanup();
              volume = Math.max(0, volume - 10); // smoother fade
              ytPlayer.setVolume?.(volume);
              if (volume <= 0)
                  cleanup();
          }, 50); // slower steps
          const cleanup = () => {
              clearInterval(fadeInterval);
              fadeInterval = null;
              try {
                  ytPlayer?.stopVideo?.();
                  ytPlayer?.destroy?.();
              }
              catch (err) {
                  console.warn("[Audio] Cleanup error:", err);
              }
              ytAudioIframe?.remove();
              ytAudioIframe = null;
              ytPlayer = null;
              currentQuery = null;
              console.log("[Audio] Previous track stopped");
              resolve();
          };
      });
      const createYTPlayer = async (videoId) => {
          await waitForYouTubeAPI();
          ytAudioIframe?.remove();
          ytAudioIframe = document.createElement("div");
          ytAudioIframe.id = "yt-audio-player";
          Object.assign(ytAudioIframe.style, {
              width: "0",
              height: "0",
              position: "absolute",
              opacity: "0",
              pointerEvents: "none",
          });
          document.body.appendChild(ytAudioIframe);
          ytPlayer = new YT.Player("yt-audio-player", {
              height: "0",
              width: "0",
              videoId,
              playerVars: { autoplay: 1 },
              events: {
                  onReady: () => {
                      ytPlayer?.setVolume?.(100);
                      console.log("[Audio] Player ready & playing:", videoId);
                  },
                  onError: (e) => {
                      console.error("[Audio] Player error:", e);
                      fadeOutAndStop();
                  },
              },
          });
      };
      const playYouTubeAudio = async (query) => {
          if (query === currentQuery) {
              console.log("[Audio] Already playing:", query);
              return;
          }
          currentQuery = query;
          console.log("[Audio] Playing query:", query);
          await fadeOutAndStop();
          const cachedId = getCachedVideo(query);
          if (cachedId) {
              console.log("[Audio] Using cached video:", cachedId);
              await createYTPlayer(cachedId);
              return;
          }
          const apiUrl = `https://nonsteamlaunchers.onrender.com/api/x7a9/${encodeURIComponent(query)}`;
          try {
              const res = await fetch(apiUrl);
              const text = await res.text();
              let data;
              try {
                  data = JSON.parse(text);
              }
              catch {
                  console.error("[Audio] Invalid JSON response:", text);
                  return;
              }
              const videoId = data.videoId;
              if (!videoId)
                  return console.warn("[Audio] No video found for:", query);
              storeCachedVideo(query, videoId);
              console.log("[Audio] Video fetched & cached:", videoId);
              await createYTPlayer(videoId);
          }
          catch (err) {
              console.error("[Audio] Failed to fetch video:", err);
          }
      };
      const updateMusicFromUrl = async () => {
          const match = window.location.pathname.match(/\/routes?\/library\/app\/(\d+)/);
          if (!match) {
              await fadeOutAndStop();
              return;
          }
          const appId = Number(match[1]);
          if (!window.appStore?.m_mapApps)
              return;
          const appStore = window.appStore;
          const appInfo = appStore.m_mapApps.get(appId);
          if (!appInfo?.display_name)
              return;
          const query = `${appInfo.display_name} Theme Music`;
          debounce(() => playYouTubeAudio(query));
      };
      const interceptHistory = (method) => {
          const original = history[method];
          history[method] = function (...args) {
              const result = original.apply(this, args);
              debounce(updateMusicFromUrl);
              return result;
          };
      };
      interceptHistory("pushState");
      interceptHistory("replaceState");
      window.addEventListener("popstate", () => debounce(updateMusicFromUrl));
      // Initial page load
      updateMusicFromUrl();
  };

  function initGameWatcher() {
      (function () {
          if (!window.SteamClient) {
              console.error("SteamClient not available");
              return;
          }
          const state = {
              gameId: null,
              launchTime: 0,
              inferredRunning: false,
              lastOverlayActive: null,
              lastOverlayChange: 0,
              overlaySequence: [],
              terminateScheduled: false
          };
          const log = (label, data) => console.log(`%c[SteamDetect:${label}]`, "color:#00bcd4", data);
          try {
              SteamClient.Apps.RegisterForGameActionStart((actionId, gameId, action) => {
                  if (action === "LaunchApp") {
                      state.gameId = gameId;
                      state.launchTime = Date.now();
                      state.inferredRunning = true;
                      state.terminateScheduled = false;
                      log("Launch", { gameId });
                      console.log("%c[SteamDetect] Launch detected, starting 90-second delay...", "color:orange");
                      setTimeout(() => {
                          console.log("%c[SteamDetect] 90 seconds passed. Continuing execution.", "color:green");
                      }, 90000); // 90 seconds
                  }
              });
          }
          catch (e) {
              console.error(e);
          }
          try {
              SteamClient.GameSessions.RegisterForAppLifetimeNotifications(evt => {
                  log("Lifetime", evt);
                  if (evt.bRunning === false && state.inferredRunning) {
                      state.inferredRunning = false;
                      scheduleTermination();
                      log("SteamEnded", evt.unAppID);
                  }
              });
          }
          catch (e) {
              console.error(e);
          }
          try {
              const origSet = SteamClient.Overlay.SetOverlayState;
              SteamClient.Overlay.SetOverlayState = function (gameId, stateNum) {
                  const now = Date.now();
                  const delta = now - state.lastOverlayChange;
                  log("SetOverlayState", arguments);
                  state.overlaySequence.push({ time: now, active: stateNum });
                  if (state.overlaySequence.length > 5)
                      state.overlaySequence.shift();
                  if (state.inferredRunning &&
                      state.overlaySequence.length >= 2) {
                      const last = state.overlaySequence[state.overlaySequence.length - 1];
                      const prev = state.overlaySequence[state.overlaySequence.length - 2];
                      if (last.active === 3 && // overlay fully active
                          prev.active === 0 && // previous overlay inactive
                          now - state.launchTime > 15000 && // more than 15s after launch
                          delta > 3000 && // overlay change >3s
                          !state.terminateScheduled // not already scheduled
                      ) {
                          log("Inference", "Overlay indicates game likely exited → scheduling termination");
                          scheduleTermination();
                      }
                  }
                  state.lastOverlayActive = stateNum;
                  state.lastOverlayChange = now;
                  return origSet.apply(this, arguments);
              };
          }
          catch (e) {
              console.error(e);
          }
          function scheduleTermination() {
              if (!state.gameId)
                  return;
              state.terminateScheduled = true;
              // wait 10s before terminating
              setTimeout(() => {
                  log("TerminateApp", { gameId: state.gameId });
                  try {
                      SteamClient.Apps.TerminateApp(state.gameId, false);
                  }
                  catch (e) {
                      console.error("TerminateApp failed:", e);
                  }
              }, 10000);
          }
          console.log("%c[SteamDetect] Heuristic detection enabled", "color:#4caf50");
      })();
  }

  const initialOptions = sitesList;
  const Content = ({ serverAPI }) => {
      console.log('Content rendered');
      const launcherOptions = initialOptions.filter((option) => option.streaming === false);
      const streamingOptions = initialOptions.filter((option) => option.streaming === true);
      const { settings, setAutoScan, setPlaytimeEnabled, setThemeMusicEnabled } = useSettings(serverAPI);
      // Random Greetings
      const greetings = [
          "Welcome to NSL!", "Hello, happy gaming!", "Good to see you again!",
          "Wow! You look amazing today...is that a new haircut?",
          "Why couldn't Ubisoft access the servers?... Cuz it couldnt 'Connect'.",
          "I hope you have a blessed day today!", "Just wanted to say, I love you to the sysmoon and back.", "Whats further? Half Life 3 or Gog Galaxy?",
          "I went on a date with a linux jedi once... it didnt work out cuz they kept kept trying to force compatability.",
          "You installed another launcher? ...pff, when are you going to learn bro?", "So how are we wasting our time today?",
          "“For God so loved the world, that he gave his only begotten Son, that whosoever believeth in him should not perish, but have everlasting life.” - John 3:16"
      ];
      const randomGreeting = greetings[Math.floor(Math.random() * greetings.length)];
      // End of Random Greetings
      const { updateInfo } = useUpdateInfo(); // Hook to get update information
      React.useState(false);
      const [isLoading, setIsLoading] = React.useState(false);
      const [isManualScanComplete, setIsManualScanComplete] = React.useState(false);
      const [isAutoScanDisabled, setIsAutoScanDisabled] = React.useState(false);
      const [isUpdating, setIsUpdating] = React.useState(false); // Track if an update is in progress
      const [progress, setProgress] = React.useState({
          percent: 0,
          status: '',
          description: ''
      });
      const handleScanClick = async () => {
          setIsLoading(true); // Set loading state to true
          setIsAutoScanDisabled(true); // Disable the auto-scan toggle
          await scan(() => setIsManualScanComplete(true)); // Perform the scan action and set completion state
          setIsLoading(false); // Set loading state to false
          setIsAutoScanDisabled(false); // Re-enable the auto-scan toggle
      };
      // Handle update button click
      const handleUpdateClick = async () => {
          setIsUpdating(true); // Set updating state
          setProgress({ percent: 0, status: 'updating...', description: 'Please wait while the plugin updates...' });
          // Set a timeout for 3 seconds to restart Steam
          setTimeout(() => {
              console.log("3 seconds passed. Restarting Steam...");
              handleRestartSteam(); // Restart Steam instead of reloading the page
          }, 5000);
          try {
              // Notify the user that the update has started
              const result = await serverAPI.callPluginMethod("install", {
                  selected_options: '',
                  install_chrome: false,
                  separate_app_ids: false,
                  start_fresh: false,
                  update_proton_ge: false,
                  nslgamesaves: false,
                  note: false,
                  up: true,
              });
              if (result) {
                  setProgress({ percent: 100, status: 'Update complete', description: 'The plugin has been updated successfully.' });
                  notify.toast("Update complete", "The plugin has been updated successfully.");
              }
              else {
                  setProgress({ percent: 0, status: 'Update failed', description: 'There was an issue with the update.' });
                  notify.toast("Update failed", "There was an issue with the update.");
              }
          }
          catch (error) {
              console.error('Error calling install method on server-side plugin:', error);
              setProgress({ percent: 0, status: 'Update failed', description: 'An error occurred during the update.' });
              notify.toast("Update failed", "An error occurred during the update.");
          }
          setIsUpdating(false); // Reset updating state
      };
      const handleRestartSteam = () => {
          // Restart Steam
          SteamClient.User.StartRestart(false);
      };
      React.useEffect(() => {
          if (isManualScanComplete) {
              setIsManualScanComplete(false); // Reset the completion state
          }
      }, [isManualScanComplete]);
      return (window.SP_REACT.createElement("div", { className: "decky-plugin" },
          updateInfo && updateInfo.status === "Update available" ? (window.SP_REACT.createElement(deckyFrontendLib.PanelSectionRow, { style: { fontSize: "16px", fontWeight: "bold", marginBottom: "10px", textAlign: "center" } },
              window.SP_REACT.createElement("div", { style: {
                      backgroundColor: "red",
                      color: "white",
                      padding: "1em",
                      borderRadius: "8px",
                      boxShadow: "0 4px 8px rgba(0, 0, 0, 0.2)",
                      maxWidth: "80%",
                      margin: "auto",
                      lineHeight: 1.6,
                      overflow: "hidden",
                      wordWrap: "break-word", // Word wrap
                  } },
                  window.SP_REACT.createElement("div", null, "Update found! :) Press Update to restart Steam. If it fails, run NSLPlugin.desktop or NSLPluginWindows.exe."),
                  window.SP_REACT.createElement(deckyFrontendLib.ButtonItem, { layout: "below", onClick: handleUpdateClick, disabled: isUpdating }, isUpdating ? 'Updating...' : 'Update'),
                  window.SP_REACT.createElement("div", { style: { marginTop: "0.5em", fontSize: "14px", fontWeight: "normal" } },
                      window.SP_REACT.createElement("div", null,
                          "\uD83D\uDCCC ",
                          window.SP_REACT.createElement("strong", null, "Local version:"),
                          " ",
                          updateInfo.local_version),
                      window.SP_REACT.createElement("div", null,
                          "\uD83D\uDE80 ",
                          window.SP_REACT.createElement("strong", null, "Latest version:"),
                          " ",
                          updateInfo.github_version),
                      window.SP_REACT.createElement("div", { style: { marginTop: "0.5em" } },
                          window.SP_REACT.createElement("strong", null, "\uD83D\uDCDD Patch Notes:"),
                          window.SP_REACT.createElement("ul", { style: {
                                  textAlign: "left",
                                  marginLeft: "1.5em",
                                  fontSize: "13px",
                                  listStyleType: "none",
                                  padding: "0"
                              } }, Object.entries(updateInfo.patch_notes).map(([category, notes]) => (window.SP_REACT.createElement("li", { key: category, style: { marginBottom: "1em" } },
                              window.SP_REACT.createElement("strong", null, category),
                              window.SP_REACT.createElement("ul", { style: { paddingLeft: "20px" } }, notes.map((note, idx) => (window.SP_REACT.createElement("li", { key: idx, style: {
                                      wordWrap: "break-word",
                                      overflow: "hidden",
                                      textOverflow: "ellipsis"
                                  } }, note.formatted_note))))))))))))) : (window.SP_REACT.createElement(deckyFrontendLib.PanelSectionRow, { style: { fontSize: "10px", fontStyle: "italic", fontWeight: "bold", marginBottom: "10px", textAlign: "center" } },
              window.SP_REACT.createElement("div", { style: {
                      display: "inline-block",
                      padding: "1em",
                      borderRadius: "8px",
                      border: "2px solid rgba(255, 255, 255, 0.3)",
                      backgroundColor: "white",
                      boxShadow: "0 4px 8px rgba(0, 0, 0, 0.2)",
                      maxWidth: "80%",
                      margin: "auto",
                  } }, randomGreeting))),
          window.SP_REACT.createElement(deckyFrontendLib.PanelSection, { title: "Install" },
              window.SP_REACT.createElement(deckyFrontendLib.ButtonItem, { layout: "below", onClick: () => deckyFrontendLib.showModal(window.SP_REACT.createElement(UpdateNotesModal, { serverAPI: serverAPI })) }, "Send Notes!\u2665"),
              window.SP_REACT.createElement(deckyFrontendLib.ButtonItem, { layout: "below", onClick: () => deckyFrontendLib.showModal(window.SP_REACT.createElement(LauncherInstallModal, { serverAPI: serverAPI, launcherOptions: launcherOptions })) }, "Game Launchers"),
              window.SP_REACT.createElement(deckyFrontendLib.ButtonItem, { layout: "below", onClick: () => deckyFrontendLib.showModal(window.SP_REACT.createElement(StreamingInstallModal, { serverAPI: serverAPI, streamingOptions: streamingOptions })) }, "Streaming Sites"),
              window.SP_REACT.createElement(deckyFrontendLib.ButtonItem, { layout: "below", onClick: () => deckyFrontendLib.showModal(window.SP_REACT.createElement(CustomSiteModal, { serverAPI: serverAPI })) }, "Custom Website Shortcut"),
              window.SP_REACT.createElement(deckyFrontendLib.ButtonItem, { layout: "below", onClick: () => deckyFrontendLib.showModal(window.SP_REACT.createElement(StartFreshModal, { serverAPI: serverAPI })) }, "Start Fresh"),
              window.SP_REACT.createElement(deckyFrontendLib.ButtonItem, { layout: "below", onClick: () => deckyFrontendLib.showModal(window.SP_REACT.createElement(UpdateRestartModal, { serverAPI: serverAPI })) }, "Update UMU/Proton-GE"),
              window.SP_REACT.createElement(deckyFrontendLib.ButtonItem, { layout: "below", onClick: () => deckyFrontendLib.showModal(window.SP_REACT.createElement(RestoreGameSavesModal, { serverAPI: serverAPI })) }, "Restore Game Saves")),
          window.SP_REACT.createElement(deckyFrontendLib.PanelSection, { title: "Game Scanner" },
              window.SP_REACT.createElement(deckyFrontendLib.PanelSectionRow, { style: { fontSize: "12px", marginBottom: "10px" } }, "NSL can automatically detect, add or remove shortcuts for the games you install or uninstall in your non-steam launchers in real time, track playtime, auto download boot videos and play game theme music. Below, you can enable automatic scanning or trigger a manual scan. During a manual scan only, your game saves will be backed up here: /home/deck/NSLGameSaves."),
              window.SP_REACT.createElement(deckyFrontendLib.PanelSectionRow, { style: { fontSize: "12px", marginBottom: "10px" } }, "The NSLGameScanner currently supports Epic Games Launcher, Ubisoft Connect, Gog Galaxy, The EA App, Battle.net, Amazon Games, Itch.io, Legacy Games, VK Play, HoYoPlay, Game Jolt Client, Minecraft Launcher, IndieGala Client, STOVE Client and Humble Bundle as well as Chrome Bookmarks for Xbox Game Pass, GeForce Now & Amazon Luna games, The Native Linux NVIDIA GeForce NOW App by favoriting the game \"\u2665\", Waydroid Applications and Native Xbox App Games on Windows OS."),
              window.SP_REACT.createElement(deckyFrontendLib.ToggleField, { label: "Auto Scan Games", checked: settings.autoscan, onChange: (value) => {
                      setAutoScan(value);
                      if (value === true) {
                          console.log(`Autoscan is ${settings.autoscan}`);
                          autoscan();
                      }
                  }, disabled: isAutoScanDisabled }),
              window.SP_REACT.createElement(deckyFrontendLib.ButtonItem, { layout: "below", onClick: handleScanClick, disabled: isLoading || settings.autoscan }, isLoading ? 'Scanning...' : 'Manual Scan'),
              window.SP_REACT.createElement(deckyFrontendLib.ToggleField, { label: "Playtime", checked: settings.playtimeEnabled, onChange: (value) => {
                      setPlaytimeEnabled(value);
                      if (value)
                          initRealPlaytime(true);
                  } }),
              window.SP_REACT.createElement(deckyFrontendLib.ToggleField, { label: "Game Theme Music", checked: settings.thememusicEnabled, onChange: (value) => {
                      setThemeMusicEnabled(value);
                      if (value) {
                          initThemeMusic();
                      }
                  } })),
          window.SP_REACT.createElement(deckyFrontendLib.PanelSection, { title: "For Support and Donations" },
              window.SP_REACT.createElement("div", { style: {
                      backgroundColor: "transparent",
                      display: "flex",
                      flexDirection: "column",
                      padding: "0.5em",
                      width: "95%",
                      margin: 0,
                  } },
                  window.SP_REACT.createElement("div", { style: { marginTop: '5px', textAlign: 'center', fontSize: "12px" } },
                      window.SP_REACT.createElement("p", null, "NSL will always be free and open source...but if you're so inclined, all sponsors & donations are humbly appreciated and accepted. Thank you so much!"),
                      window.SP_REACT.createElement("div", { style: { display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '10px' } },
                          window.SP_REACT.createElement(deckyFrontendLib.ButtonItem, { layout: "below", onClick: () => window.open('https://www.patreon.com/moraroy', '_blank') },
                              window.SP_REACT.createElement("img", { src: "https://seeklogo.com/images/P/patreon-logo-C0B52F951B-seeklogo.com.png", alt: "Patreon", style: { width: '20px', height: '20px', marginRight: '10px' } }),
                              "Patreon"),
                          window.SP_REACT.createElement(deckyFrontendLib.ButtonItem, { layout: "below", onClick: () => window.open('https://ko-fi.com/moraroy#checkoutModal', '_blank') },
                              window.SP_REACT.createElement("img", { src: "https://cdn.prod.website-files.com/5c14e387dab576fe667689cf/64f1a9ddd0246590df69e9ef_ko-fi_logo_02-p-500.png", alt: "Ko-fi", style: { width: '20px', height: '20px', marginRight: '10px' } }),
                              "Ko-fi"),
                          window.SP_REACT.createElement(deckyFrontendLib.ButtonItem, { layout: "below", onClick: () => window.open('https://github.com/sponsors/moraroy', '_blank') },
                              window.SP_REACT.createElement("img", { src: "https://cdn.pixabay.com/photo/2022/01/30/13/33/github-6980894_1280.png", alt: "GitHub", style: { width: '20px', height: '20px', marginRight: '10px' } }),
                              "GitHub"),
                          window.SP_REACT.createElement(deckyFrontendLib.ButtonItem, { layout: "below", onClick: () => window.open('https://github.com/moraroy/NonSteamLaunchers-On-Steam-Deck', '_blank') }, "click here for more info!")))))));
  };
  var index = deckyFrontendLib.definePlugin((serverApi) => {
      autoscan();
      notify.setServer(serverApi);
      initGameWatcher();
      // Fetch saved settings first, then decide whether to start Playtime or Theme Music
      (async () => {
          const savedSettings = (await serverApi.callPluginMethod('get_setting', {
              key: 'settings',
              default: {
                  autoscan: false,
                  customSites: "",
                  playtimeEnabled: true,
                  thememusicEnabled: true,
              },
          })).result;
          if (savedSettings.playtimeEnabled) {
              initRealPlaytime();
          }
          else {
              setPlaytimeEnabled(false);
          }
          if (savedSettings.thememusicEnabled) {
              initThemeMusic();
          }
      })();
      return {
          title: window.SP_REACT.createElement("div", { className: deckyFrontendLib.staticClasses.Title }, "NonSteamLaunchers"),
          alwaysRender: true,
          content: window.SP_REACT.createElement(Content, { serverAPI: serverApi }),
          icon: window.SP_REACT.createElement(RxRocket, null),
      };
  });

  return index;

})(DFL, SP_REACT);
