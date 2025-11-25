import { notify } from "./notify";

const collectionLocks = new Map<string, Promise<any>>();

async function withCollectionLock(collectionName: string, fn: () => Promise<any>) {
  // Initialize queue for this collection if needed
  if (!collectionLocks.has(collectionName)) {
    collectionLocks.set(collectionName, Promise.resolve());
  }

  // Get last scheduled promise
  const previous = collectionLocks.get(collectionName)!;

  // Chain the next operation after it
  const next = previous.then(async () => {
    try {
      return await fn();
    } catch (e) {
      console.error("Collection lock error:", e);
    }
  });

  // Update queue
  collectionLocks.set(collectionName, next);
  return next;
}

// Shortcut Creation Code
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

  let gameIconUrl: string;

  if (Icon) {
    SteamClient.Apps.SetShortcutIcon(appId, Icon);
  }

  if (Icon64) {
    gameIconUrl = `data:image/x-icon;base64,${Icon64}`;
  } else {
    gameIconUrl = defaultIconUrl;
  }

  const launcherIconUrl = LauncherIcon ? `data:image/x-icon;base64,${LauncherIcon}` : null;

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

  const AvailableCompatTools = await SteamClient.Apps.GetAvailableCompatTools(appId);
  const CompatToolExists: boolean = AvailableCompatTools.some((e: { strToolName: any }) => e.strToolName === CompatTool);

  if (CompatTool && CompatToolExists) {
    SteamClient.Apps.SpecifyCompatTool(appId, CompatTool);
  } else if (CompatTool) {
    SteamClient.Apps.SpecifyCompatTool(appId, 'proton_experimental');
  }

  SteamClient.Apps.SetCustomArtworkForApp(appId, Hero, 'png', 1);
  SteamClient.Apps.SetCustomArtworkForApp(appId, Logo, 'png', 2);
  SteamClient.Apps.SetCustomArtworkForApp(appId, Grid, 'png', 0);
  SteamClient.Apps.SetCustomArtworkForApp(appId, WideGrid, 'png', 3);

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
        const collectionStore =
          (window as any).g_CollectionStore || (window as any).collectionStore;

        if (!collectionStore) {
          console.error("No collection store found.");
          return;
        }

        const collectionId = collectionStore.GetCollectionIDByUserTag(tag);
        const collection =
          typeof collectionId === "string"
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
        } else {
          console.log(`App ${appId} already in collection "${tag}".`);
        }

      } catch (err) {
        console.error("Failed to create or update collection:", err);
      }
    });
  }

  return true;
}
// End of Shortcut Creation Code
