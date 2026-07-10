export function initGameWatcher(): void {
  const GRACE_PERIOD_MS = 90_000;

  const state = {
    gameId: null as string | null,
    launchTime: 0,
    inferredRunning: false,
    watchersEnabled: false,
    terminateScheduled: false,

    overlaySequence: [] as { time: number; active: number }[],
    lastOverlayActive: null as number | null,
    lastOverlayChange: 0,

    graceTimer: null as ReturnType<typeof setTimeout> | null,
    terminateTimer: null as ReturnType<typeof setTimeout> | null
  };

  const log = (label: string, data?: any) =>
    console.log(`%c[SteamDetect:${label}]`, "color:#00bcd4", data);


  function resetState(gameId: string) {
    if (state.graceTimer) {
      clearTimeout(state.graceTimer);
    }

    if (state.terminateTimer) {
      clearTimeout(state.terminateTimer);
    }

    state.gameId = gameId;
    state.launchTime = Date.now();
    state.inferredRunning = true;
    state.watchersEnabled = false;
    state.terminateScheduled = false;

    state.overlaySequence = [];
    state.lastOverlayActive = null;
    state.lastOverlayChange = 0;
  }


  function scheduleTermination() {
    if (!state.watchersEnabled) return;
    if (!state.gameId || state.terminateScheduled) return;

    state.terminateScheduled = true;

    const gameToTerminate = state.gameId;

    state.terminateTimer = setTimeout(() => {
      // Ignore stale termination
      if (state.gameId !== gameToTerminate) return;

      log("TerminateApp", { gameId: gameToTerminate });

      try {
        SteamClient.Apps.TerminateApp(gameToTerminate, false);
      } catch (e) {
        console.error("TerminateApp failed:", e);
      }

    }, 10_000);
  }


  try {
    SteamClient.Apps.RegisterForGameActionStart(
      (_actionId: any, gameId: string, action: string) => {
        if (action !== "LaunchApp") return;


        const nonSteamGameIds = new Set(
          appStore.allApps
            .filter(app => app.app_type === 1073741824)
            .map(app => String(app.m_gameid))
        );


        if (!nonSteamGameIds.has(String(gameId))) {
          log("IgnoredSteamGame", { gameId });
          return;
        }


        resetState(gameId);

        log("Launch", {
          gameId,
          gracePeriod: "90 Seconds"
        });


        state.graceTimer = setTimeout(() => {

          // Ignore old launches
          if (state.gameId !== gameId) return;

          state.watchersEnabled = true;

          log("GracePeriodEnded", { gameId });

        }, GRACE_PERIOD_MS);
      }
    );

  } catch (e) {
    console.error(e);
  }



  try {
    SteamClient.GameSessions.RegisterForAppLifetimeNotifications(evt => {

      if (!state.watchersEnabled) return;

      log("Lifetime", evt);


      if (
        evt.bRunning === false &&
        state.inferredRunning
      ) {
        state.inferredRunning = false;

        scheduleTermination();

        log("SteamEnded", evt.unAppID);
      }

    });

  } catch (e) {
    console.error(e);
  }



  try {
    const origSet = SteamClient.Overlay.SetOverlayState;


    SteamClient.Overlay.SetOverlayState = function (
      gameId: string,
      stateNum: number
    ) {

      if (!state.watchersEnabled) {
        return origSet.apply(this, arguments as any);
      }


      // Ignore other apps
      if (gameId !== state.gameId) {
        return origSet.apply(this, arguments as any);
      }


      const now = Date.now();


      log("Overlay", {
        gameId,
        stateNum
      });


      state.overlaySequence.push({
        time: now,
        active: stateNum
      });


      if (state.overlaySequence.length > 5) {
        state.overlaySequence.shift();
      }



      // More flexible exit detection
      if (
        state.inferredRunning &&
        stateNum === 3 &&
        now - state.launchTime > 30_000 &&
        !state.terminateScheduled
      ) {

        log(
          "Inference",
          "Overlay indicates possible exit"
        );

        scheduleTermination();
      }


      state.lastOverlayActive = stateNum;
      state.lastOverlayChange = now;


      return origSet.apply(this, arguments as any);
    };


  } catch (e) {
    console.error(e);
  }


  console.log(
    "%c[SteamDetect] Initialized",
    "color:#4caf50"
  );
}