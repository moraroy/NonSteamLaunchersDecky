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

  // Shortcut Creation Code
  // Define the createShortcut function
  async function createShortcut(game) {
      const { appid, appname, exe, StartDir, LaunchOptions, CompatTool, Grid, WideGrid, Hero, Logo, Icon, LauncherIcon, Launcher } = game;
      // No need to format exe and StartDir here as it's already done in Python
      const formattedExe = exe;
      const formattedStartDir = StartDir;
      const launchOptions = LaunchOptions;
      console.log(`Creating shortcut ${appname}`);
      console.log(`Game details: Name= ${appname}, ID=${appid}, exe=${formattedExe}, StartDir=${formattedStartDir}, launchOptions=${launchOptions}`);
      // Use the addShortcut method directly
      const appId = await SteamClient.Apps.AddShortcut(appname, formattedExe, formattedStartDir, launchOptions);
      if (appId) {
          const defaultIconUrl = "https://raw.githubusercontent.com/moraroy/NonSteamLaunchersDecky/main/assets/logo.png";
          const gameIconUrl = Icon ? `data:image/x-icon;base64,${Icon}` : defaultIconUrl; // Use the base64-encoded icon or default icon
          const launcherIconUrl = LauncherIcon ? `data:image/x-icon;base64,${LauncherIcon}` : null; // Use the base64-encoded launcher icon or null
          // Pass both icons to the notification
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
          // Explicitly set the icon for the shortcut
          if (Icon) {
              SteamClient.Apps.SetShortcutIcon(appId, `data:image/x-icon;base64,${Icon}`);
          }
          let AvailableCompatTools = await SteamClient.Apps.GetAvailableCompatTools(appId);
          let CompatToolExists = AvailableCompatTools.some((e) => e.strToolName === CompatTool);
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
          //SteamClient.Apps.AddUserTagToApps([appId], "NonSteamLaunchers");
          return true;
      }
      else {
          console.log(`Failed to create shortcut for ${appname}`);
          return false;
      }
  }
  // End of Shortcut Creation Code

  const installSite = async (sites, serverAPI, { setProgress }, total) => {
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
              await createSiteShortcut(sites, { setProgress }, total);
          }
          else {
              console.log('Installation failed.');
          }
      }
      catch (error) {
          console.error('Error calling _main method on server-side plugin:', error);
      }
  };
  async function createSiteShortcut(sites, { setProgress }, total) {
      let customSiteWS;
      let installed = 0;
      customSiteWS = new WebSocket('ws://localhost:8675/customSite');
      customSiteWS.onopen = () => {
          console.log('NSL Custom Site WebSocket connection opened');
          if (customSiteWS.readyState === WebSocket.OPEN) {
              customSiteWS.send(JSON.stringify(sites));
          }
          else {
              console.log('Cannot send message, NSL Custom Site WebSocket connection is not open');
          }
      };
      customSiteWS.onmessage = (e) => {
          console.log(`Received custom site data from NSL server: ${e.data}`);
          if (e.data === 'NoShortcuts') {
              console.log('No shortcuts to add, unblocking UI');
              setProgress({ percent: 100, status: ``, description: `` });
          }
          if (e.data[0] === '{' && e.data[e.data.length - 1] === '}') {
              try {
                  const site = JSON.parse(e.data);
                  installed++;
                  createShortcut(site);
                  if (installed == total) {
                      setProgress({ percent: 100, status: ``, description: `` });
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
          setProgress({ percent: 100, status: ``, description: `` });
      };
  }

  /**
  * The modal for updating custom sites.
  */
  const CustomSiteModal = ({ closeModal, serverAPI }) => {
      const [sites, setSites] = React.useState([{ siteName: "", siteURL: "" }]);
      const [canSave, setCanSave] = React.useState(false);
      const [progress, setProgress] = React.useState({ percent: 0, status: '', description: '' });
      React.useEffect(() => {
          setCanSave(sites.every(site => site.siteName != "") && sites.every(site => site.siteURL != ""));
      }, [sites]);
      React.useEffect(() => {
          if (progress.percent === 100) {
              closeModal();
          }
      }, [progress]);
      function onNameChange(siteName, e) {
          const newSites = sites.map(site => {
              if (site.siteName === siteName) {
                  return {
                      ...site,
                      siteName: e?.target.value
                  };
              }
              else {
                  return site;
              }
          });
          setSites(newSites);
      }
      function onURLChange(siteName, e) {
          const newSites = sites.map(site => {
              if (site.siteName === siteName) {
                  return {
                      ...site,
                      siteURL: e?.target.value
                  };
              }
              else {
                  return site;
              }
          });
          setSites(newSites);
      }
      function addSiteFields() {
          if (canSave) {
              setSites(// Replace the state
              [
                  ...sites,
                  { siteName: '', siteURL: '' } // and one new item at the end
              ]);
          }
      }
      async function onSave() {
          if (canSave) {
              setProgress({ percent: 1, status: `Installing Custom Sites`, description: `` });
              await installSite(sites, serverAPI, { setProgress }, sites.length);
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
          window.SP_REACT.createElement(deckyFrontendLib.ModalRoot, null,
              window.SP_REACT.createElement(deckyFrontendLib.DialogHeader, null, "Installing Custom Sites"),
              window.SP_REACT.createElement(deckyFrontendLib.DialogBodyText, null,
                  "Creating shortcuts for sites: ",
                  sites.map(site => site.siteName).join(', ')),
              window.SP_REACT.createElement(deckyFrontendLib.DialogBody, null,
                  window.SP_REACT.createElement(deckyFrontendLib.SteamSpinner, null),
                  window.SP_REACT.createElement("img", { src: "https://cdn2.steamgriddb.com/thumb/d0fb992a3dc7f0014263653d6e2063fe.jpg", alt: "Overlay", style: { ...fadeStyle, opacity: 0.5 } }),
                  window.SP_REACT.createElement(deckyFrontendLib.DialogButton, { onClick: cancelOperation, style: { width: '25px' } }, "Back"))) :
          window.SP_REACT.createElement("div", null,
              window.SP_REACT.createElement(deckyFrontendLib.ConfirmModal, { bAllowFullSize: true, onCancel: closeModal, onEscKeypress: closeModal, strMiddleButtonText: 'Add Another Site', onMiddleButton: addSiteFields, bMiddleDisabled: !canSave, bOKDisabled: !canSave, onOK: onSave, strOKButtonText: "Create Shortcuts", strTitle: "Enter Custom Websites" },
                  window.SP_REACT.createElement(deckyFrontendLib.DialogBodyText, null, "NSL will install and use Chrome to launch these sites. Non-Steam shortcuts will be created for each site entered."),
                  window.SP_REACT.createElement(deckyFrontendLib.DialogBody, null, sites.map(({ siteName, siteURL }, index) => window.SP_REACT.createElement(window.SP_REACT.Fragment, null,
                      window.SP_REACT.createElement(deckyFrontendLib.PanelSection, { title: `Site ${index + 1}` },
                          window.SP_REACT.createElement(deckyFrontendLib.TextField, { label: "Name", value: siteName, placeholder: "The name you want to appear in the shortcut for your site.", onChange: (e) => onNameChange(siteName, e) }),
                          window.SP_REACT.createElement(deckyFrontendLib.TextField, { label: "URL", value: siteURL, placeholder: "The URL for your site.", onChange: (e) => onURLChange(siteName, e) }))))))));
  };

  const useSettings = (serverApi) => {
      const [settings, setSettings] = React.useState({
          autoscan: false,
          customSites: ""
      });
      React.useEffect(() => {
          const getData = async () => {
              const savedSettings = (await serverApi.callPluginMethod('get_setting', {
                  key: 'settings',
                  default: settings
              })).result;
              setSettings(savedSettings);
          };
          getData();
      }, []);
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
      function setAutoScan(value) {
          updateSettings('autoscan', value);
      }
      function setCustomSites(value) {
          updateSettings('customSites', value);
      }
      return { settings, setAutoScan, setCustomSites };
  };

  async function setupWebSocket(url, onMessage, onComplete) {
      const ws = new WebSocket(url);
      ws.onopen = () => {
          console.log('NSL WebSocket connection opened');
          if (ws.readyState === WebSocket.OPEN) {
              ws.send('something');
          }
          else {
              console.log('Cannot send message, NSL WebSocket connection is not open');
          }
      };
      ws.onmessage = async (e) => {
          console.log(`Received data from NSL server: ${e.data}`);
          if (e.data[0] === '{' && e.data[e.data.length - 1] === '}') {
              try {
                  const message = JSON.parse(e.data);
                  if (message.status === "Manual scan completed") {
                      console.log('Manual scan completed');
                      onComplete(); // Trigger the completion callback
                  }
                  else {
                      await onMessage(message); // Process each game entry one at a time
                  }
              }
              catch (error) {
                  console.error(`Error parsing data as JSON: ${error}`);
              }
          }
      };
      ws.onerror = (e) => {
          const errorEvent = e;
          console.error(`NSL WebSocket error: ${errorEvent.message}`);
      };
      ws.onclose = (e) => {
          console.log(`NSL WebSocket connection closed, code: ${e.code}, reason: ${e.reason}`);
          if (e.code !== 1000) {
              console.log(`Unexpected close of WS NSL connection, reopening`);
              setupWebSocket(url, onMessage, onComplete);
          }
      };
      return ws;
  }
  async function scan(onComplete) {
      console.log('Starting NSL Scan');
      return new Promise((resolve) => {
          setupWebSocket('ws://localhost:8675/scan', createShortcut, () => {
              console.log('NSL Scan completed');
              onComplete(); // Trigger the completion callback
              resolve();
          });
      });
  }
  async function autoscan() {
      console.log('Starting NSL Autoscan');
      await setupWebSocket('ws://localhost:8675/autoscan', createShortcut, () => { });
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

  const LauncherInstallModal = ({ closeModal, launcherOptions, serverAPI }) => {
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
      React.useEffect(() => {
          const selectedLaunchers = options.filter(option => option.enabled && !option.streaming);
          if (selectedLaunchers.length > 0) {
              setCurrentLauncher(selectedLaunchers[0]);
          }
      }, [options]);
      React.useEffect(() => {
          if (logContainerRef.current) {
              logContainerRef.current.scrollTop = logContainerRef.current.scrollHeight;
          }
      }, [log]);
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
                  update_proton_ge: false
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
      return ((progress.status != '' && progress.percent < 100) ?
          window.SP_REACT.createElement(deckyFrontendLib.ModalRoot, { onCancel: cancelOperation },
              window.SP_REACT.createElement(deckyFrontendLib.DialogHeader, null, `${operation}ing Game Launchers`),
              window.SP_REACT.createElement(deckyFrontendLib.DialogBodyText, null,
                  "Selected options: ",
                  options.filter(option => option.enabled).map(option => option.label).join(', ')),
              window.SP_REACT.createElement(deckyFrontendLib.DialogBody, null,
                  window.SP_REACT.createElement(deckyFrontendLib.SteamSpinner, null),
                  window.SP_REACT.createElement("div", { style: { display: 'flex', alignItems: 'center' } },
                      window.SP_REACT.createElement("div", { ref: logContainerRef, style: { flex: 1, marginRight: '10px', fontSize: 'small', whiteSpace: 'pre-wrap', overflowY: 'auto', maxHeight: '50px', height: '100px' } }, showLog && log),
                      window.SP_REACT.createElement(deckyFrontendLib.ProgressBarWithInfo, { layout: "inline", bottomSeparator: "none", sOperationText: progress.status, description: progress.description, nProgress: progress.percent, indeterminate: true })),
                  currentLauncher && (window.SP_REACT.createElement("img", { src: currentLauncher.urlimage, alt: "Overlay", style: { ...fadeStyle, opacity: 0.5 } })),
                  window.SP_REACT.createElement(deckyFrontendLib.DialogButton, { onClick: cancelOperation, style: { width: '25px', margin: 0, padding: '10px' } }, "Back"))) :
          window.SP_REACT.createElement(deckyFrontendLib.ModalRoot, { onCancel: closeModal },
              window.SP_REACT.createElement(deckyFrontendLib.DialogHeader, null, "Select Game Launchers"),
              window.SP_REACT.createElement(deckyFrontendLib.DialogBodyText, null, "Here you choose your launchers you want to install and let NSL do the rest. Once installed, they will be added your library!"),
              window.SP_REACT.createElement(deckyFrontendLib.DialogBody, null, launcherOptions.map(({ name, label }) => (window.SP_REACT.createElement(deckyFrontendLib.ToggleField, { key: name, label: label, checked: options.find(option => option.name === name)?.enabled ? true : false, onChange: (value) => handleToggle(name, value) })))),
              window.SP_REACT.createElement("p", { style: { fontSize: 'small', marginTop: '16px' } }, "Note: When installing a launcher, the latest Proton-GE will attempt to be installed. If your launchers don't start, make sure force compatibility is checked, shortcut properties are right, and your steam files are updated. Remember to also edit your controller layout configurations if necessary! If all else fails, restart your steam deck manually."),
              window.SP_REACT.createElement("p", { style: { fontSize: 'small', marginTop: '16px' } }, "Note\u00B2: Some games won't run right away using NSL. Due to easy anti-cheat or quirks, you may need to manually tinker to get some games working. NSL is simply another way to play! Happy Gaming!\u2665"),
              window.SP_REACT.createElement(deckyFrontendLib.Focusable, null,
                  window.SP_REACT.createElement("div", { style: { display: 'flex', justifyContent: 'space-between', alignItems: 'center' } },
                      window.SP_REACT.createElement("div", { style: { display: 'flex', alignItems: 'center' } },
                          window.SP_REACT.createElement(deckyFrontendLib.DialogButton, { style: { width: "fit-content" }, onClick: () => handleInstallClick("Install"), disabled: options.every(option => option.enabled === false) }, "Install"),
                          window.SP_REACT.createElement(deckyFrontendLib.DialogButton, { style: { width: "fit-content", marginLeft: "10px", marginRight: "10px" }, onClick: () => handleInstallClick("Uninstall"), disabled: options.every(option => option.enabled === false) }, "Uninstall")),
                      window.SP_REACT.createElement(deckyFrontendLib.ToggleField, { label: "Separate Launcher Folders", checked: separateAppIds, onChange: handleSeparateAppIdsToggle })))));
  };

  /**
   * The modal for selecting launchers.
   */
  const StreamingInstallModal = ({ closeModal, streamingOptions, serverAPI }) => {
      const [progress, setProgress] = React.useState({ percent: 0, status: '', description: '' });
      const [options, setOptions] = React.useState(streamingOptions);
      const [currentStreamingSite, setCurrentStreamingSite] = React.useState(null);
      const handleInstallClick = async () => {
          console.log('handleInstallClick called');
          const selectedStreamingSites = options
              .filter(option => option.enabled && option.streaming)
              .map(option => {
              return {
                  siteName: option.label,
                  siteURL: option.URL
              };
          });
          if (selectedStreamingSites.length > 0) {
              const total = (options.filter(option => option.enabled && option.streaming).length);
              const startPercent = 0;
              setProgress({
                  percent: startPercent,
                  status: `Installing ${selectedStreamingSites.length} Streaming Sites`,
                  description: `${selectedStreamingSites.map(site => site.siteName).join(', ')}`
              });
              setCurrentStreamingSite(options.find(option => option.enabled && option.streaming) || null);
              await installSite(selectedStreamingSites, serverAPI, { setProgress }, total);
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
          setCurrentStreamingSite(null);
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
      return ((progress.status != '' && progress.percent < 100) ?
          window.SP_REACT.createElement(deckyFrontendLib.ModalRoot, null,
              window.SP_REACT.createElement(deckyFrontendLib.DialogHeader, null, "Installing Streaming Sites"),
              window.SP_REACT.createElement(deckyFrontendLib.DialogBodyText, null,
                  "Selected options: ",
                  options.filter(option => option.enabled).map(option => option.label).join(', ')),
              window.SP_REACT.createElement(deckyFrontendLib.DialogBody, null,
                  window.SP_REACT.createElement(deckyFrontendLib.SteamSpinner, null),
                  window.SP_REACT.createElement(deckyFrontendLib.ProgressBarWithInfo, { layout: "inline", bottomSeparator: "none", sOperationText: progress.status, description: progress.description, nProgress: progress.percent, indeterminate: true }),
                  currentStreamingSite && (window.SP_REACT.createElement("img", { src: currentStreamingSite.urlimage, alt: "Overlay", style: { ...fadeStyle, opacity: 0.5 } })),
                  window.SP_REACT.createElement(deckyFrontendLib.DialogButton, { onClick: cancelOperation, style: { width: '25px' } }, "Back"))) :
          window.SP_REACT.createElement(deckyFrontendLib.ModalRoot, { onCancel: closeModal },
              window.SP_REACT.createElement(deckyFrontendLib.DialogHeader, null, "Install Game/Media Streaming Sites"),
              window.SP_REACT.createElement(deckyFrontendLib.DialogBodyText, null, "NSL will install and use Chrome to launch these sites. Non-Steam shortcuts will be created for each selection. Before installing, toggle Auto Scan \"on\" for these."),
              window.SP_REACT.createElement(deckyFrontendLib.DialogBody, null, streamingOptions.map(({ name, label }) => (window.SP_REACT.createElement(deckyFrontendLib.ToggleField, { label: label, checked: options.find(option => option.name === name)?.enabled ? true : false, onChange: (value) => handleToggle(name, value) })))),
              window.SP_REACT.createElement("p", null),
              window.SP_REACT.createElement(deckyFrontendLib.Focusable, { style: { display: "flex", alignItems: "center", gap: "10px" } },
                  window.SP_REACT.createElement(deckyFrontendLib.DialogButton, { style: { width: "fit-content" }, onClick: handleInstallClick, disabled: options.every(option => option.enabled === false) }, "Install"),
                  window.SP_REACT.createElement(deckyFrontendLib.DialogBodyText, { style: { fontSize: "small" } }, "Note: NSL will attempt to install Google Chrome. Be sure that Google Chrome is installed from the Discover Store in Desktop Mode first or from SteamOS."))));
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
                  update_proton_ge: false
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
              window.SP_REACT.createElement(deckyFrontendLib.ConfirmModal, { strTitle: "Oops... That Might Have Been a Mistake", strDescription: "This is your last chance! By continuing, you will be totally deleting the prefixes, which include the launchers and the games you downloaded, as well as your game saves. If you aren't sure if your game saves are backed up or if you have downloaded a very large game and would not like to have to re-download, please DO NOT CONTINUE. Everything will be wiped!", strOKButtonText: "Yes, I'm sure!", strCancelButtonText: "No, go back!", onOK: handleStartFreshClick, onCancel: () => setFirstConfirm(false) }) :
              window.SP_REACT.createElement(deckyFrontendLib.ConfirmModal, { strTitle: "Are You Sure?", strDescription: "Starting fresh will wipe all installed launchers and their games along with your game saves and NSL files. This is irreversible! You'll need to manually remove any shortcuts created.", strOKButtonText: "Yes, wipe!", strCancelButtonText: "No, go back!", onOK: () => setFirstConfirm(true), onCancel: closeModal }));
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
                  update_proton_ge: true
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
              window.SP_REACT.createElement(deckyFrontendLib.ProgressBarWithInfo, { layout: "inline", bottomSeparator: "none", sOperationText: progress.status, description: progress.description, nProgress: progress.percent, indeterminate: true })))) : showRestartModal ? (window.SP_REACT.createElement(deckyFrontendLib.ModalRoot, null,
          window.SP_REACT.createElement(deckyFrontendLib.DialogHeader, null, "Restart Steam"),
          window.SP_REACT.createElement(deckyFrontendLib.DialogBodyText, null, "Updating Proton GE requires a restart of Steam for the changes to take effect. Would you like to restart Steam now?"),
          window.SP_REACT.createElement(deckyFrontendLib.DialogBody, null,
              window.SP_REACT.createElement("div", { style: { display: 'flex', justifyContent: 'space-between' } },
                  window.SP_REACT.createElement(deckyFrontendLib.DialogButton, { onClick: () => setShowRestartModal(false) }, "Back"),
                  window.SP_REACT.createElement(deckyFrontendLib.DialogButton, { onClick: handleRestartSteam }, "Restart"))))) : (window.SP_REACT.createElement(deckyFrontendLib.ModalRoot, null,
          window.SP_REACT.createElement(deckyFrontendLib.DialogHeader, null, "Update Proton GE"),
          window.SP_REACT.createElement(deckyFrontendLib.DialogBodyText, null, "Would you like to update Proton GE to the latest version?"),
          window.SP_REACT.createElement(deckyFrontendLib.DialogBody, null,
              window.SP_REACT.createElement("div", { style: { display: 'flex', justifyContent: 'space-between' } },
                  window.SP_REACT.createElement(deckyFrontendLib.DialogButton, { onClick: closeModal }, "Cancel"),
                  window.SP_REACT.createElement(deckyFrontendLib.DialogButton, { onClick: handleUpdateProtonGEClick }, "Update")))))));
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
          label: 'Humble Games',
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
          name: 'fortnite',
          label: 'Fortnite (xCloud)',
          URL: 'https://www.xbox.com/en-US/play/games/fortnite/BT5P2X999VH2/',
          streaming: true,
          enabled: false,
          urlimage: 'https://cdn2.steamgriddb.com/hero_thumb/560cc70f255b94b8408709e810914593.jpg'
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
          URL: 'https://luna.amazon.com/',
          streaming: true,
          enabled: false,
          urlimage: 'https://cdn2.steamgriddb.com/thumb/5966577c1d725b37c26c3f7aa493dd9c.jpg'
      },
      {
          name: 'webRcade',
          label: 'WebRcade',
          URL: 'https://play.webrcade.com/',
          streaming: true,
          enabled: false,
          urlimage: 'https://cdn2.steamgriddb.com/thumb/f9b8cc42051c6d1c1ddaf5260118d585.jpg'
      },
      {
          name: 'webRcadeeditor',
          label: 'WebRcade (Editor)',
          URL: 'https://editor.webrcade.com/',
          streaming: true,
          enabled: false,
          urlimage: 'https://cdn2.steamgriddb.com/thumb/f9b8cc42051c6d1c1ddaf5260118d585.jpg'
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
          URL: 'https://www.plex.tv/',
          streaming: true,
          enabled: false,
          urlimage: 'https://cdn2.steamgriddb.com/thumb/7c8db737a231930514b03b61dda48c60.jpg'
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
          name: 'crunchyroll',
          label: 'Crunchyroll',
          URL: 'https://www.crunchyroll.com/',
          streaming: true,
          enabled: false,
          urlimage: 'https://cdn2.steamgriddb.com/thumb/b51869faee0c2357dc5c2c34e4229a80.jpg'
      },
      {
          name: 'appletv+',
          label: 'Apple TV+',
          URL: 'https://tv.apple.com/',
          streaming: true,
          enabled: false,
          urlimage: 'https://cdn2.steamgriddb.com/thumb/305aefb84d348c156953f7a3d4aa3e04.jpg'
      },
      {
          name: 'twitch',
          label: 'Twitch',
          URL: 'https://www.twitch.tv/',
          streaming: true,
          enabled: false,
          urlimage: 'https://cdn2.steamgriddb.com/thumb/72f0b767094fe8e24d620a2273bd0839.jpg'
      }
  ];

  const initialOptions = sitesList;
  const Content = ({ serverAPI }) => {
      console.log('Content rendered');
      const launcherOptions = initialOptions.filter((option) => option.streaming === false);
      const streamingOptions = initialOptions.filter((option) => option.streaming === true);
      const { settings, setAutoScan } = useSettings(serverAPI);
      // Random Greetings
      const greetings = ["Is it just me? Or does the Rog Ally kinda s... actually, nevermind.", "Welcome to NSL!", "Hello, happy gaming!", "Good to see you again!", "Wow! You look amazing today...is that a new haircut?", "Hey! Thinkin' of changing the name of NSL to 'Nasty Lawn Chairs'. What do you think?", "'A'... that other handheld is a little 'Sus' if you ask me. I don't trust him.", "What the heck is a Lenovo anyway? It needs to 'Go' and get outta here.", "Why couldn't Ubisoft access the servers?... Cuz it couldnt 'Connect'.", "Some said it couldnt be done, making a plugin like this... haters gonna hate, haters gonna marinate.", "I hope you have a blessed day today!", "Just wanted to say, I love you to the sysmoon and back.", "Whats further? Half Life 3 or Gog Galaxy?", "I went on a date with a linux jedi once... it didnt work out cuz they kept kept trying to force compatability.", "NSL has updated succesfully. It now has more launchers than Elon Musk.", "You installed another launcher? ...pff, when are you going to learn bro?", "So how are we wasting our time today?"];
      const randomGreeting = greetings[Math.floor(Math.random() * greetings.length)];
      // End of Random Greetings
      const [isFocused, setIsFocused] = React.useState(false);
      const [isLoading, setIsLoading] = React.useState(false);
      const [isManualScanComplete, setIsManualScanComplete] = React.useState(false);
      const [isAutoScanDisabled, setIsAutoScanDisabled] = React.useState(false);
      const handleScanClick = async () => {
          setIsLoading(true); // Set loading state to true
          setIsAutoScanDisabled(true); // Disable the auto-scan toggle
          await scan(() => setIsManualScanComplete(true)); // Perform the scan action and set completion state
          setIsLoading(false); // Set loading state to false
          setIsAutoScanDisabled(false); // Re-enable the auto-scan toggle
      };
      React.useEffect(() => {
          if (isManualScanComplete) {
              setIsManualScanComplete(false); // Reset the completion state
          }
      }, [isManualScanComplete]);
      return (window.SP_REACT.createElement("div", { className: "decky-plugin" },
          window.SP_REACT.createElement(deckyFrontendLib.PanelSectionRow, { style: { fontSize: "10px", fontStyle: "italic", fontWeight: "bold", marginBottom: "10px", textAlign: "center" } }, randomGreeting),
          window.SP_REACT.createElement(deckyFrontendLib.PanelSection, { title: "Install" },
              window.SP_REACT.createElement(deckyFrontendLib.ButtonItem, { layout: "below", onClick: () => deckyFrontendLib.showModal(window.SP_REACT.createElement(LauncherInstallModal, { serverAPI: serverAPI, launcherOptions: launcherOptions })) }, "Game Launchers"),
              window.SP_REACT.createElement(deckyFrontendLib.ButtonItem, { layout: "below", onClick: () => deckyFrontendLib.showModal(window.SP_REACT.createElement(StreamingInstallModal, { serverAPI: serverAPI, streamingOptions: streamingOptions })) }, "Streaming Sites"),
              window.SP_REACT.createElement(deckyFrontendLib.ButtonItem, { layout: "below", onClick: () => deckyFrontendLib.showModal(window.SP_REACT.createElement(CustomSiteModal, { serverAPI: serverAPI })) }, "Custom Website Shortcut"),
              window.SP_REACT.createElement(deckyFrontendLib.ButtonItem, { layout: "below", onClick: () => deckyFrontendLib.showModal(window.SP_REACT.createElement(StartFreshModal, { serverAPI: serverAPI })) }, "Start Fresh"),
              window.SP_REACT.createElement(deckyFrontendLib.ButtonItem, { layout: "below", onClick: () => deckyFrontendLib.showModal(window.SP_REACT.createElement(UpdateRestartModal, { serverAPI: serverAPI })) }, "Update Proton-GE")),
          window.SP_REACT.createElement(deckyFrontendLib.PanelSection, { title: "Game Scanner" },
              window.SP_REACT.createElement(deckyFrontendLib.PanelSectionRow, { style: { fontSize: "12px", marginBottom: "10px" } }, "NSL can automatically detect and add shortcuts for the games you install in your non-steam launchers in real time. Below, you can enable automatic scanning or trigger a manual scan. During a manual scan only, your game saves will be backed up here: /home/deck/NSLGameSaves."),
              window.SP_REACT.createElement(deckyFrontendLib.ToggleField, { label: "Auto Scan Games", checked: settings.autoscan, onChange: (value) => {
                      setAutoScan(value);
                      if (value === true) {
                          console.log(`Autoscan is ${settings.autoscan}`);
                          autoscan();
                      }
                  }, disabled: isAutoScanDisabled }),
              window.SP_REACT.createElement(deckyFrontendLib.ButtonItem, { layout: "below", onClick: handleScanClick, disabled: isLoading || settings.autoscan }, isLoading ? 'Scanning...' : 'Manual Scan')),
          window.SP_REACT.createElement("div", { style: {
                  backgroundColor: "transparent",
                  display: "flex",
                  flexDirection: "column",
                  padding: "0.5em",
                  width: "95%",
                  margin: 0,
              } },
              window.SP_REACT.createElement("span", { style: { fontSize: "12px", marginBottom: "10px", textAlign: "center" } },
                  "The NSLGameScanner currently supports Epic Games Launcher, Ubisoft Connect, Gog Galaxy, The EA App, Battle.net, Amazon Games, Itch.io and Legacy Games.",
                  window.SP_REACT.createElement(deckyFrontendLib.Focusable, { focusWithinClassName: "gpfocuswithin", onFocus: () => setIsFocused(true), onBlur: () => setIsFocused(false), onActivate: () => { window.open('https://github.com/moraroy/NonSteamLaunchers-On-Steam-Deck', '_blank'); } },
                      window.SP_REACT.createElement("a", { style: { textDecoration: 'underline', color: 'inherit', outline: isFocused ? '2px solid rgba(255, 255, 255, 0.5)' : 'none' } }, "click here for more info!")))),
          window.SP_REACT.createElement(deckyFrontendLib.PanelSection, { title: "Support and Donations vvv" },
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
                              "GitHub")))))));
  };
  var index = deckyFrontendLib.definePlugin((serverApi) => {
      autoscan();
      notify.setServer(serverApi);
      return {
          title: window.SP_REACT.createElement("div", { className: deckyFrontendLib.staticClasses.Title }, "NonSteamLaunchers"),
          alwaysRender: true,
          content: (window.SP_REACT.createElement(Content, { serverAPI: serverApi })),
          icon: window.SP_REACT.createElement(RxRocket, null),
      };
  });

  return index;

})(DFL, SP_REACT);
