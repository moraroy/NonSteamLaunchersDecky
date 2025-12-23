let watcherInitialized = false;

export function initGameWatcher() {
  if (watcherInitialized) return;
  watcherInitialized = true;

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

  try {
    SteamClient.Apps.RegisterForGameActionStart((actionId, gameId, action) => {
      if (action === "LaunchApp") {
        state.gameId = gameId;
        state.launchTime = Date.now();
        state.inferredRunning = true;
        state.terminateScheduled = false;
        console.log(`%c[SteamDetect:Launch]`, "color:#00bcd4", { gameId });

        setTimeout(() => {
          try {
            SteamClient.GameSessions.RegisterForAppLifetimeNotifications(evt => {
              if (evt.bRunning === false && state.inferredRunning) {
                state.inferredRunning = false;
                scheduleTermination();
                console.log(`%c[SteamDetect:SteamEnded]`, "color:#00bcd4", evt.unAppID);
              }
            });
          } catch (e) {
            console.error(e);
          }

          try {
            const origSet = SteamClient.Overlay.SetOverlayState;
            SteamClient.Overlay.SetOverlayState = function (gameId, stateNum) {
              const now = Date.now();
              const delta = now - state.lastOverlayChange;

              state.overlaySequence.push({ time: now, active: stateNum });
              if (state.overlaySequence.length > 5) state.overlaySequence.shift();

              if (
                state.inferredRunning &&
                state.overlaySequence.length >= 2
              ) {
                const last = state.overlaySequence[state.overlaySequence.length - 1];
                const prev = state.overlaySequence[state.overlaySequence.length - 2];

                if (
                  last.active === 3 &&
                  prev.active === 0 &&
                  now - state.launchTime > 15000 &&
                  delta > 3000 &&
                  !state.terminateScheduled
                ) {
                  scheduleTermination();
                }
              }

              state.lastOverlayActive = stateNum;
              state.lastOverlayChange = now;

              return origSet.apply(this, arguments);
            };
          } catch (e) {
            console.error(e);
          }

          function scheduleTermination() {
            if (!state.gameId) return;

            state.terminateScheduled = true;

            setTimeout(() => {
              console.log(`%c[SteamDetect:Termination] Game detected to have exited. Running termination command for gameId: ${state.gameId}`, "color:#ff5722");
              try {
                SteamClient.Apps.TerminateApp(state.gameId, false);
              } catch (e) {
                console.error("TerminateApp failed:", e);
              }
            }, 10000);
          }

          console.log("%c[SteamDetect] Heuristic detection enabled", "color:#4caf50");
        }, 90000);
      }
    });
  } catch (e) {
    console.error(e);
  }
}
