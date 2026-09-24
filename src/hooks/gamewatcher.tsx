export function initGameWatcher(): void {


    type RGB = {
        r: number;
        g: number;
        b: number;
    };

    type PaletteColor = [number, number, number];

    type SteamApp = {
        app_type?: number;
        m_gameid?: string | number;
        appid?: string | number;
        display_name?: string;
        icon_data?: string;
        icon_data_format?: string;
    };

    type LEDDevice = {
        id: string;
        effect?: string | null;
        color?: RGB[];
        effects_available?: string[];
    };

    type LEDStateResponse = {
        BSuccess(): boolean;
        Body(): {
            toObject(): {
                state?: {
                    devices?: LEDDevice[];
                };
            };
        };
    };

    type LEDManager = {
        GetState(args: Record<string, never>): Promise<LEDStateResponse>;
        SetColor(args: {
            device_id: string;
            color_index: number;
            color: RGB;
        }): unknown;
        SetEffect(args: {
            device_id: string;
            effect: string;
        }): unknown;
    };

    type SteamWebpackRequire = {
        (id: string): any;
        m: Record<string, unknown>;
    };

    type SteamGameActionCallback = (
        actionId: any,
        gameId: string,
        action: string
    ) => void;

    type SteamLifetimeEvent = {
        bRunning: boolean;
        unAppID?: string | number;
        [key: string]: any;
    };

    type SetOverlayStateFunction = (
        gameId: string,
        stateNum: number
    ) => any;

    type WatcherLedSnapshot = {
        id: string;
        effect: string | null | undefined;
        colors: RGB[];
    }[];



    const steamWindow = window as Window & {
        __watcherLedGeneration?: number;
        __steam_require?: SteamWebpackRequire;
        __watcherLedSnapshot?: WatcherLedSnapshot | null;
        webpackChunksteamui?: {
            push: (chunk: any[]) => void;
        };
    };



    const steamAppStore = appStore as {
        allApps: SteamApp[];
    };



    const runGameLEDPalette = async (
        gameId: string,
        gameName?: string | null
    ): Promise<void> => {
        const generation =
            (steamWindow.__watcherLedGeneration ?? 0) + 1;

        steamWindow.__watcherLedGeneration = generation;

        try {
            const [
                PALETTE_SIZE,
                QUANTIZE,
                MIN_DISTANCE,
                MAX_SAMPLES
            ] = [5, 16, 55, 2e4];

            const sleep = (ms: number): Promise<void> =>
                new Promise(resolve => setTimeout(resolve, ms));

            const req: SteamWebpackRequire =
                steamWindow.__steam_require ||
                await new Promise<SteamWebpackRequire>(
                    (resolve, reject) => {
                        if (
                            typeof steamWindow.webpackChunksteamui !==
                            "object"
                        ) {
                            reject(
                                Error(
                                    "Steam Webpack runtime not available"
                                )
                            );
                            return;
                        }

                        let done = 0;

                        const finish = (
                            value: SteamWebpackRequire | null,
                            error?: unknown
                        ): void => {
                            if (done) return;

                            done = 1;

                            if (error) {
                                reject(error);
                            } else {
                                steamWindow.__steam_require = value!;
                                resolve(value!);
                            }
                        };

                        try {
                            steamWindow.webpackChunksteamui!.push([
                                [Math.random()],
                                {},
                                (r: SteamWebpackRequire) =>
                                    finish(r)
                            ]);
                        } catch (e) {
                            finish(null, e);
                        }

                        setTimeout(
                            () =>
                                finish(
                                    null,
                                    Error(
                                        "Failed to acquire Steam Webpack runtime"
                                    )
                                ),
                            5e3
                        );
                    }
                );

            let LED: LEDManager | undefined;

            for (const id of Object.keys(req.m)) {
                try {
                    const m = req(id);

                    if (
                        m?.Om?.GetState &&
                        m.Om.SetColor &&
                        m.Om.SetEffect
                    ) {
                        LED = m.Om as LEDManager;
                        break;
                    }
                } catch {}
            }

            if (!LED) {
                throw Error("LEDManager module not found");
            }

            const getDevices = async (): Promise<LEDDevice[]> => {
                const r = await LED!.GetState({});

                if (!r.BSuccess()) {
                    throw Error("LEDManager.GetState failed");
                }

                return (
                    r
                        .Body()
                        .toObject()
                        ?.state
                        ?.devices ?? []
                );
            };

            const color = (
                id: string,
                i: number,
                c: RGB
            ): unknown =>
                LED!.SetColor({
                    device_id: id,
                    color_index: i,
                    color: c
                });

            const effect = (
                id: string,
                e: string
            ): unknown =>
                LED!.SetEffect({
                    device_id: id,
                    effect: e
                });

            const apps = steamAppStore.allApps.filter(
                a => a?.app_type === 1073741824
            );

            const gid = String(gameId);

            const app =
                apps.find(
                    a => String(a?.m_gameid) === gid
                ) ||
                apps.find(
                    a => String(a?.appid) === gid
                );

            if (!app) {
                throw Error(
                    `Non-Steam game not found: ${
                        gameName || gid
                    }`
                );
            }

            const {
                appid,
                display_name,
                icon_data,
                icon_data_format
            } = app;

            if (!icon_data) {
                throw Error(
                    `No icon_data found for ${
                        display_name ||
                        gameName ||
                        gid
                    } (${appid})`
                );
            }

            const format = String(
                icon_data_format || "png"
            ).toLowerCase();

            const mimeMap: Record<string, string> = {
                ico: "image/x-icon",
                jpg: "image/jpeg",
                jpeg: "image/jpeg",
                webp: "image/webp",
                gif: "image/gif",
                bmp: "image/bmp"
            };

            const mime =
                mimeMap[format] ||
                "image/png";

            const img = new Image();

            img.src =
                `data:${mime};base64,${icon_data}`;

            await new Promise<void>(
                (resolve, reject) => {
                    img.onload = () => resolve();

                    img.onerror = () =>
                        reject(
                            Error(
                                `Failed to decode Steam icon (${format})`
                            )
                        );
                }
            );

            const canvas =
                document.createElement("canvas");

            canvas.width =
                img.naturalWidth;

            canvas.height =
                img.naturalHeight;

            const ctx =
                canvas.getContext(
                    "2d",
                    {
                        willReadFrequently: true
                    }
                );

            if (!ctx) {
                throw Error(
                    "Failed to acquire canvas 2D context"
                );
            }

            ctx.drawImage(img, 0, 0);

            const { data } =
                ctx.getImageData(
                    0,
                    0,
                    canvas.width,
                    canvas.height
                );

            const total =
                canvas.width *
                canvas.height;

            const step = Math.max(
                1,
                Math.floor(
                    total / MAX_SAMPLES
                )
            );

            const colors =
                new Map<string, number>();

            const q = (
                v: number
            ): number =>
                Math.floor(
                    v / QUANTIZE
                ) *
                    QUANTIZE +
                QUANTIZE / 2;

            for (
                let p = 0;
                p < total;
                p += step
            ) {
                const o = p * 4;

                if (data[o + 3] < 128) {
                    continue;
                }

                const c: PaletteColor = [
                    q(data[o]),
                    q(data[o + 1]),
                    q(data[o + 2])
                ];

                const k = c.join(",");

                colors.set(
                    k,
                    (colors.get(k) || 0) + 1
                );
            }

            if (!colors.size) {
                throw Error(
                    "Icon contains no usable pixels"
                );
            }

            const dist = (
                a: PaletteColor | number[],
                b: PaletteColor | number[]
            ): number =>
                Math.hypot(
                    a[0] - b[0],
                    a[1] - b[1],
                    a[2] - b[2]
                );

            const palette: PaletteColor[] = [];

            for (
                const [k] of [
                    ...colors
                ].sort(
                    (a, b) =>
                        b[1] - a[1]
                )
            ) {
                const c =
                    k
                        .split(",")
                        .map(Number) as PaletteColor;

                if (
                    palette.every(
                        x =>
                            dist(
                                c,
                                x
                            ) >=
                            MIN_DISTANCE
                    )
                ) {
                    palette.push(c);

                    if (
                        palette.length ===
                        PALETTE_SIZE
                    ) {
                        break;
                    }
                }
            }

            if (!palette.length) {
                throw Error(
                    "Could not extract a usable color palette"
                );
            }

            const ledPalette: RGB[] =
                palette.map(
                    ([r, g, b]) => ({
                        r: r / 255,
                        g: g / 255,
                        b: b / 255
                    })
                );

            const devices =
                await getDevices();
                
            console.log(
                devices.length
                    ? `LEDs found: ${devices.length}`
                    : "No LEDs found"
            );

            if (!devices.length) {
                return;
            }

            if (
                !steamWindow.__watcherLedSnapshot
            ) {
                steamWindow.__watcherLedSnapshot =
                    devices.map(d => ({
                        id: d.id,
                        effect: d.effect,
                        colors:
                            (d.color ?? []).map(
                                ({
                                    r,
                                    g,
                                    b
                                }) => ({
                                    r,
                                    g,
                                    b
                                })
                            )
                    }));
            }

            if (
                generation !==
                steamWindow.__watcherLedGeneration
            ) {
                return;
            }

            await Promise.all(
                devices.flatMap(d => {
                    const n =
                        d.color?.length ??
                        0;

                    return Array.from(
                        {
                            length: n
                        },
                        (_, i) =>
                            color(
                                d.id,
                                i,
                                ledPalette[
                                    Math.min(
                                        Math.floor(
                                            i *
                                                palette.length /
                                                n
                                        ),
                                        ledPalette.length -
                                            1
                                    )
                                ]
                            )
                    );
                })
            );

            await Promise.all(
                devices
                    .filter(
                        d =>
                            d.effects_available?.includes(
                                "breath"
                            )
                    )
                    .map(
                        d =>
                            effect(
                                d.id,
                                "breath"
                            )
                    )
            );

            await sleep(30e3);

            if (
                generation !==
                steamWindow.__watcherLedGeneration
            ) {
                return;
            }

            const current =
                await getDevices();

            const snapshot =
                steamWindow.__watcherLedSnapshot;

            if (!snapshot) {
                return;
            }

            await Promise.all(
                snapshot.flatMap(s => {
                    const d =
                        current.find(
                            x =>
                                x.id === s.id
                        );

                    if (!d) {
                        return [];
                    }

                    return [
                        ...s.colors.map(
                            (c, i) =>
                                color(
                                    s.id,
                                    i,
                                    c
                                )
                        ),
                        ...(s.effect != null
                            ? [
                                  effect(
                                      s.id,
                                      s.effect
                                  )
                              ]
                            : [])
                    ];
                })
            );

            if (
                generation ===
                steamWindow.__watcherLedGeneration
            ) {
                steamWindow.__watcherLedSnapshot =
                    null;
            }
        } catch (e) {
            console.log(
                "Game LED palette error:",
                e
            );
        }
    };



    (() => {
        const originalConsoleLog =
            console.log;

        console.log = new Proxy(
            originalConsoleLog,
            {
                apply(
                    target,
                    thisArg,
                    args
                ) {
                    try {
                        const line =
                            args.join(" ");

                        if (
                            line.includes(
                                "OnGameActionUserRequest"
                            ) &&
                            line.includes(
                                "LaunchApp CreatingProcess"
                            )
                        ) {
                            const m =
                                line.match(
                                    /OnGameActionUserRequest:\s*(\d+)/
                                );

                            if (
                                m &&
                                m[1].length >=
                                    18 &&
                                m[1].length <=
                                    20
                            ) {
                                const app =
                                    steamAppStore.allApps.find(
                                        a =>
                                            String(
                                                a.m_gameid
                                            ) ===
                                            m[1]
                                    );

                                if (
                                    app?.app_type ===
                                    1073741824
                                ) {
                                    desktopGameRunning =
                                        true;

                                    desktopCurrentAppId =
                                        m[1];

                                    desktopCurrentGameName =
                                        app.display_name ||
                                        null;
                                }
                            }
                        }

                        if (
                            desktopGameRunning &&
                            (
                                line.includes(
                                    "Removing overlay browser window"
                                ) ||
                                line.includes(
                                    "NetworkDiagnosticsStore - unregistering for detailed connection state updates"
                                )
                            )
                        ) {
                            desktopGameRunning =
                                false;

                            const id =
                                desktopCurrentAppId;

                            if (id) {
                                setTimeout(
                                    () => {
                                        try {
                                            SteamClient.Apps.TerminateApp(
                                                id,
                                                false
                                            );

                                            if (
                                                desktopCurrentAppId ===
                                                id
                                            ) {
                                                desktopCurrentAppId =
                                                    desktopCurrentGameName =
                                                        null;
                                            }
                                        } catch {}
                                    },
                                    15e3
                                );
                            }
                        }
                    } catch {}

                    return Reflect.apply(
                        target,
                        thisArg,
                        args
                    );
                }
            }
        );
    })();


    (() => {
        const
            MIN_STATE_GAP_MS = 1e3,
            RAPID_TRANSITION_MS = 250,
            TERMINATION_DELAY_MS = 1e4,
            EXIT_CONFIRMATION_MS = 1e4,
            MIN_GAME_RUNTIME_MS = 3e4;

        type WatcherState = {
            gameId: string | null;
            gameName: string | null;
            launchTime: number;
            inferredRunning: boolean;
            watchersEnabled: boolean;
            terminateScheduled: boolean;
            possibleExit: boolean;
            exitCandidateTime: number;
            qamActive: boolean;
            lastOverlayActive: number | null;
            lastOverlayChange: number;
            terminateTimer:
                ReturnType<typeof setTimeout> | null;
            exitConfirmationTimer:
                ReturnType<typeof setTimeout> | null;
        };

        const s: WatcherState = {
            gameId: null,
            gameName: null,
            launchTime: 0,
            inferredRunning: false,
            watchersEnabled: false,
            terminateScheduled: false,
            possibleExit: false,
            exitCandidateTime: 0,
            qamActive: false,
            lastOverlayActive: null,
            lastOverlayChange: 0,
            terminateTimer: null,
            exitConfirmationTimer: null
        };

        const clearExit = (): void => {
            if (
                s.exitConfirmationTimer
            ) {
                clearTimeout(
                    s.exitConfirmationTimer
                );
            }

            s.exitConfirmationTimer =
                null;

            s.possibleExit = false;
            s.exitCandidateTime = 0;
        };

        const reset = (
            id: string,
            name?: string | null
        ): void => {
            if (s.terminateTimer) {
                clearTimeout(
                    s.terminateTimer
                );
            }

            clearExit();

            Object.assign(s, {
                gameId: String(id),
                gameName: name || null,
                launchTime: Date.now(),
                inferredRunning: true,
                watchersEnabled: true,
                terminateScheduled: false,
                possibleExit: false,
                exitCandidateTime: 0,
                qamActive: false,
                lastOverlayActive: null,
                lastOverlayChange: 0,
                terminateTimer: null
            });

            runGameLEDPalette(
                s.gameId,
                s.gameName
            );
        };

        const activateQAM = (): void => {
            if (!s.watchersEnabled) {
                return;
            }

            if (s.possibleExit) {
                clearExit();
            }

            s.qamActive = true;
        };

 

        try {
            const currentConsoleLog =
                console.log as typeof console.log & {
                    __steamDetectQAMHook?: boolean;
                };

            if (
                !currentConsoleLog.__steamDetectQAMHook
            ) {
                const original =
                    console.log;

                const hook =
                    function (
                        this: any,
                        ...args: any[]
                    ): any {
                        try {
                            if (
                                args
                                    .map(
                                        v => {
                                            try {
                                                return typeof v ===
                                                    "string"
                                                    ? v
                                                    : String(
                                                          v
                                                      );
                                            } catch {
                                                return "";
                                            }
                                        }
                                    )
                                    .join(" ")
                                    .includes(
                                        "onGlobalMenuButtonDown SP BPM_uid0"
                                    )
                            ) {
                                activateQAM();
                            }
                        } catch {}

                        return original.apply(
                            this,
                            args
                        );
                    } as typeof console.log & {
                        __steamDetectQAMHook?: boolean;
                    };

                hook.__steamDetectQAMHook =
                    true;

                console.log = hook;
            }
        } catch {}



        const terminate = (): void => {
            if (
                !s.watchersEnabled ||
                !s.gameId ||
                s.terminateScheduled
            ) {
                return;
            }

            s.terminateScheduled = true;

            const id = s.gameId;

            s.terminateTimer =
                setTimeout(() => {
                    s.terminateTimer =
                        null;

                    if (
                        s.gameId === id
                    ) {
                        try {
                            SteamClient.Apps.TerminateApp(
                                id,
                                false
                            );
                        } catch {}
                    }
                }, TERMINATION_DELAY_MS);
        };



        const confirmExit = (): void => {
            if (
                !s.watchersEnabled ||
                !s.gameId ||
                s.terminateScheduled ||
                s.possibleExit ||
                s.qamActive
            ) {
                return;
            }

            s.possibleExit = true;
            s.exitCandidateTime =
                Date.now();

            const id = s.gameId;
            const time =
                s.exitCandidateTime;

            s.exitConfirmationTimer =
                setTimeout(() => {
                    s.exitConfirmationTimer =
                        null;

                    if (
                        s.gameId !== id ||
                        !s.watchersEnabled ||
                        !s.possibleExit ||
                        s.exitCandidateTime !==
                            time
                    ) {
                        return;
                    }

                    if (
                        s.qamActive ||
                        !s.inferredRunning ||
                        s.lastOverlayActive ===
                            0
                    ) {
                        clearExit();
                        return;
                    }

                    s.possibleExit = false;
                    s.exitCandidateTime =
                        0;

                    terminate();
                }, EXIT_CONFIRMATION_MS);
        };


        try {
            SteamClient.Apps.RegisterForGameActionStart(
                (
                    _actionId: any,
                    id: string,
                    action: string
                ) => {
                    if (
                        action !==
                        "LaunchApp"
                    ) {
                        return;
                    }

                    const gameId =
                        String(id);

                    const app =
                        steamAppStore.allApps.find(
                            a =>
                                String(
                                    a.m_gameid
                                ) ===
                                gameId
                        );

                    if (
                        app?.app_type ===
                        1073741824
                    ) {
                        reset(
                            gameId,
                            app.display_name
                        );
                    }
                }
            );
        } catch {}



        try {
            SteamClient.GameSessions.RegisterForAppLifetimeNotifications(
                (
                    evt: SteamLifetimeEvent
                ) => {
                    if (
                        !s.watchersEnabled ||
                        String(
                            evt.unAppID
                        ) !==
                            String(
                                s.gameId
                            )
                    ) {
                        return;
                    }

                    if (
                        evt.bRunning ===
                            false &&
                        s.inferredRunning
                    ) {
                        s.inferredRunning =
                            false;

                        clearExit();
                    } else if (
                        evt.bRunning ===
                            true &&
                        !s.inferredRunning
                    ) {
                        s.inferredRunning =
                            true;
                    }
                }
            );
        } catch {}



        try {
            const original =
                SteamClient.Overlay
                    .SetOverlayState as SetOverlayStateFunction;

            SteamClient.Overlay.SetOverlayState =
                function (
                    this: any,
                    gameId: string,
                    stateNum: number
                ): any {
                    if (
                        !s.watchersEnabled ||
                        String(gameId) !==
                            String(
                                s.gameId
                            )
                    ) {
                        return original.apply(
                            this,
                            arguments as any
                        );
                    }

                    const now =
                        Date.now();

                    const prev =
                        s.lastOverlayActive;

                    const gap =
                        s.lastOverlayChange
                            ? now -
                              s.lastOverlayChange
                            : null;

                    if (s.qamActive) {
                        if (
                            stateNum === 0
                        ) {
                            s.qamActive =
                                false;
                        }
                    } else if (
                        gap === null ||
                        gap >=
                            RAPID_TRANSITION_MS
                    ) {
                        if (
                            s.inferredRunning &&
                            stateNum === 3 &&
                            prev === 0 &&
                            gap >=
                                MIN_STATE_GAP_MS &&
                            now -
                                s.launchTime >
                                MIN_GAME_RUNTIME_MS &&
                            !s.terminateScheduled &&
                            !s.possibleExit
                        ) {
                            confirmExit();
                        }

                        if (
                            s.possibleExit &&
                            stateNum === 0
                        ) {
                            clearExit();
                        }
                    } else if (
                        s.possibleExit
                    ) {
                        clearExit();
                    }

                    s.lastOverlayActive =
                        stateNum;

                    s.lastOverlayChange =
                        now;

                    return original.apply(
                        this,
                        arguments as any
                    );
                } as typeof SteamClient.Overlay.SetOverlayState;
        } catch {}
    })();
}
