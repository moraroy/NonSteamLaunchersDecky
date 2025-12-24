export function initGameWatcher() {
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
      overlaySequence: [], // track recent overlay states
      terminateScheduled: false
    };

    const log = (label, data) =>
      console.log(`%c[SteamDetect:${label}]`, "color:#00bcd4", data);

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
    } catch (e) {
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
    } catch (e) {
      console.error(e);
    }

    try {
      const origSet = SteamClient.Overlay.SetOverlayState;
      SteamClient.Overlay.SetOverlayState = function (gameId, stateNum) {
        const now = Date.now();
        const delta = now - state.lastOverlayChange;

        log("SetOverlayState", arguments);

        state.overlaySequence.push({ time: now, active: stateNum });
        if (state.overlaySequence.length > 5) state.overlaySequence.shift();

        if (
          state.inferredRunning &&
          state.overlaySequence.length >= 2
        ) {
          const last = state.overlaySequence[state.overlaySequence.length - 1];
          const prev = state.overlaySequence[state.overlaySequence.length - 2];

          if (
            last.active === 3 &&            // overlay fully active
            prev.active === 0 &&            // previous overlay inactive
            now - state.launchTime > 15000 && // more than 15s after launch
            delta > 3000 &&                 // overlay change >3s
            !state.terminateScheduled       // not already scheduled
          ) {
            log("Inference", "Overlay indicates game likely exited → scheduling termination");
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

      // wait 10s before terminating
      setTimeout(() => {
        log("TerminateApp", { gameId: state.gameId });
        try {
          SteamClient.Apps.TerminateApp(state.gameId, false);
        } catch (e) {
          console.error("TerminateApp failed:", e);
        }
      }, 10000);
    }

    console.log("%c[SteamDetect] Heuristic detection enabled", "color:#4caf50");
  })();
}
