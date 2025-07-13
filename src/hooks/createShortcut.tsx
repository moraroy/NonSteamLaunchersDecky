import { notify } from "./notify";

// Shortcut Creation Code
// Define the createShortcut function
export async function createShortcut(game: any) {
  const {
    appid,
    appname,
    exe,
    StartDir,
    LaunchOptions,
    CompatTool,
    Grid,
    WideGrid,
    Hero,
    Logo,
    Icon,
    LauncherIcon,
    Launcher,
    Icon64,
  } = game;

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

    let gameIconUrl: string;

    if (Icon) {
      SteamClient.Apps.SetShortcutIcon(appId, Icon); // Icon is now a file path
    }

    if (Icon64) {
      gameIconUrl = `data:image/x-icon;base64,${Icon64}`;
    } else {
      gameIconUrl = defaultIconUrl;
    }

    const launcherIconUrl = LauncherIcon ? `data:image/x-icon;base64,${LauncherIcon}` : null;  // Use the base64-encoded launcher icon or null

    // Pass both icons to the notification
    if (launcherIconUrl) {
      notify.toast(appname, "has been added to your library!", { gameIconUrl, launcherIconUrl });
    } else {
      notify.toast(appname, "has been added to your library!", { gameIconUrl });
    }

    console.log(`AppID for ${appname} = ${appId}`);
    SteamClient.Apps.SetShortcutName(appId, appname);
    SteamClient.Apps.SetAppLaunchOptions(appId, launchOptions);
    SteamClient.Apps.SetShortcutExe(appId, formattedExe);
    SteamClient.Apps.SetShortcutStartDir(appId, formattedStartDir);

    let AvailableCompatTools = await SteamClient.Apps.GetAvailableCompatTools(appId);
    let CompatToolExists: boolean = AvailableCompatTools.some((e: { strToolName: any }) => e.strToolName === CompatTool);
    if (CompatTool && CompatToolExists) {
      SteamClient.Apps.SpecifyCompatTool(appId, CompatTool);
    } else if (CompatTool) {
      SteamClient.Apps.SpecifyCompatTool(appId, 'proton_experimental');
    }

    SteamClient.Apps.SetCustomArtworkForApp(appId, Hero, 'png', 1);
    SteamClient.Apps.SetCustomArtworkForApp(appId, Logo, 'png', 2);
    SteamClient.Apps.SetCustomArtworkForApp(appId, Grid, 'png', 0);
    SteamClient.Apps.SetCustomArtworkForApp(appId, WideGrid, 'png', 3);
    //SteamClient.Apps.AddUserTagToApps([appId], "NonSteamLaunchers");

    //START: Add to or create launcher-based collection
    if (Launcher && typeof window !== 'undefined') {
      try {
        const tag = Launcher;
        const collectionStore = (window as any).g_CollectionStore || (window as any).collectionStore;
        if (!collectionStore) {
          console.error("No collection store found.");
        } else {
          const collectionId = collectionStore.GetCollectionIDByUserTag(tag);
          const collection =
            typeof collectionId === "string"
              ? collectionStore.GetCollection(collectionId)
              : collectionStore.NewUnsavedCollection(tag, undefined, []);

          if (collection) {
            if (!collectionId) {
              await collection.Save();
              console.log(`Created new collection "${tag}".`);
            }

            if (!collection.m_setApps.has(appId)) {
              collection.m_setApps.add(appId);
              collection.m_setAddedManually.add(appId);
              await collection.Save();
              console.log(`Added app ${appId} to collection "${tag}".`);
            } else {
              console.log(`App ${appId} already in collection "${tag}".`);
            }
          } else {
            console.error(`Could not get or create collection "${tag}".`);
          }
        }
      } catch (error) {
        console.error("Failed to create or update collection:", error);
      }
    }
    //End of Launcher-based collection logic

    return true;
  } else {
    console.log(`Failed to create shortcut for ${appname}`);
    return false;
  }
}
// End of Shortcut Creation Code
