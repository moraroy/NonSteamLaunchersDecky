export function initGameWatcher(): void {
  const GRACE_PERIOD_MS = 90_000;

  const state = {
    gameId: null as string | null,
    launchTime: 0,
    inferredRunning: false,
    lastOverlayActive: null as number | null,
    lastOverlayChange: 0,
    overlaySequence: [] as { time: number; active: number }[],
    terminateScheduled: false,
    watchersEnabled: false
  };

  const log = (label: string, data?: any) =>
    console.log(`%c[SteamDetect:${label}]`, "color:#00bcd4", data);


  try {
    SteamClient.Apps.RegisterForGameActionStart(
      (_actionId: any, gameId: string, action: string) => {
        if (action !== "LaunchApp") return;

        state.gameId = gameId;
        state.launchTime = Date.now();
        state.inferredRunning = true;
        state.terminateScheduled = false;
        state.watchersEnabled = false;

        log("Launch", { gameId, gracePeriod: "90s" });

        setTimeout(() => {
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

      if (evt.bRunning === false && state.inferredRunning) {
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

      const now = Date.now();
      const delta = now - state.lastOverlayChange;

      log("SetOverlayState", arguments);

      state.overlaySequence.push({ time: now, active: stateNum });
      if (state.overlaySequence.length > 5) state.overlaySequence.shift();

      if (
        state.inferredRunning &&
        state.overlaySequence.length >= 2 &&
        !state.terminateScheduled
      ) {
        const last = state.overlaySequence[state.overlaySequence.length - 1];
        const prev = state.overlaySequence[state.overlaySequence.length - 2];

        if (
          last.active === 3 &&
          prev.active === 0 &&
          now - state.launchTime > 15_000 &&
          delta > 3_000
        ) {
          log(
            "Inference",
            "Overlay indicates game likely exited → scheduling termination"
          );
          scheduleTermination();
        }
      }

      state.lastOverlayActive = stateNum;
      state.lastOverlayChange = now;

      return origSet.apply(this, arguments as any);
    };
  } catch (e) {
    console.error(e);
  }


  function scheduleTermination(): void {
    if (!state.watchersEnabled) return;
    if (!state.gameId || state.terminateScheduled) return;

    state.terminateScheduled = true;

    setTimeout(() => {
      log("TerminateApp", { gameId: state.gameId });
      try {
        SteamClient.Apps.TerminateApp(state.gameId, false);
      } catch (e) {
        console.error("TerminateApp failed:", e);
      }
    }, 10_000);
  }

  console.log(
    "%c[SteamDetect] Initialized (90s hard grace after launch)",
    "color:#4caf50"
  );
}
