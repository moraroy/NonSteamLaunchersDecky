export function metaData() {
  if ((window as any).__nslMetaInjected) return;
  (window as any).__nslMetaInjected = true;
    const gameCache = {};

    async function getSteamGameDetails(gameName) {
        // Check if the game details are already in the cache
        if (gameCache[gameName]) {
            return gameCache[gameName];
        }
        try {
            const searchRes = await fetch(`https://store.steampowered.com/search/?term=${encodeURIComponent(gameName)}`, {
                credentials: "omit"
            });
            const searchHtml = await searchRes.text();
            const searchDoc = new DOMParser().parseFromString(searchHtml, "text/html");
            const results = [...searchDoc.querySelectorAll(".search_result_row")].map(r => ({
                appid: r.dataset.dsAppid,
                title: r.querySelector(".title")?.innerText.trim()
            }));
            if (!results.length) return null;
            let match = results.find(r => r.title?.toLowerCase() === gameName.toLowerCase()) || results[0];
            const appid = match.appid;
            const apiRes = await fetch(`https://store.steampowered.com/api/appdetails?appids=${appid}`);
            const apiData = await apiRes.json();
            const info = apiData[appid].data;
            if (!info) return null;
            const gameData = {
                appid: appid,
                about_the_game: info.short_description || null,
                developer: (info.developers?.join(", ") || null),
                publisher: (info.publishers?.join(", ") || null),
                release_date: info.release_date?.date || null,
                genres: info.genres?.map(g => g.description).join(", ") || null,
                platforms: info.platforms ? Object.entries(info.platforms).filter(([k,v]) => v).map(([k]) => k).join(", ") : null,
                image_url: info.screenshots?.[0]?.path_full || null
            };
            // Cache the data for future use
            gameCache[gameName] = gameData;
            return gameData;
        } catch (err) {
            console.error("Error fetching Steam details:", err);
            return null;
        }
    }

    function replaceText() {
        document.querySelectorAll("div").forEach(div => {
            if (
                div.childNodes.length === 1 &&
                div.firstChild.nodeType === Node.TEXT_NODE
            ) {
                const originalText = div.firstChild.nodeValue;
                const match = originalText.match(/Some detailed information on (.*?) is unavailable/i);
                if (match) {
                    const gameName = match[1];
                    console.log("[Game Detected]", gameName);
                    const key = gameName.toUpperCase();
                    // Fetch game details from Steam (from cache or API)
                    getSteamGameDetails(gameName).then(gameData => {
                        if (!gameData) return;
                        const descriptionText = gameData.about_the_game || "No description available.";
                        const bgImage = gameData.image_url || "https://images-1.gog-statics.com/6f3d015c3029fea5221ccd9802de5e2f92c6afccc0196b15540677341936a656.jpg";
                        div.textContent = '';

                        //Check div
                        const currentDiv = div;

                        const nextDiv = currentDiv.nextElementSibling;

                        if (nextDiv) {
                            nextDiv.appendChild(currentDiv);
                        }


            // Main div styling
            div.style.position = "relative";
            div.style.overflow = "hidden";
            div.style.height = "250px";
            div.style.borderRadius = "6px";
            div.style.fontFamily = '"Roboto", "Segoe UI", Tahoma, Geneva, Verdana, sans-serif';
            div.style.color = "white";
            div.style.outline = "none";
            div.style.border = "none";

            // Background image
            const img = document.createElement('img');
            img.src = bgImage;
            img.alt = gameName;
            img.style.width = "100%";
            img.style.height = "100%";
            img.style.objectFit = "cover";
            img.style.position = "absolute";
            img.style.top = 0;
            img.style.left = 0;
            img.style.opacity = 0.5;

            // Overlay
            const overlay = document.createElement('div');
            overlay.style.position = "absolute";
            overlay.style.top = 0;
            overlay.style.left = 0;
            overlay.style.width = "100%";
            overlay.style.height = "100%";
            overlay.style.padding = "10px";
            overlay.style.display = "flex";
            overlay.style.flexDirection = "column";
            overlay.style.justifyContent = "flex-start";
            overlay.style.background =
              "linear-gradient(to bottom, rgba(0,0,0,0.3), rgba(0,0,0,0.7))";

            // Content row
            const contentRow = document.createElement('div');
            contentRow.style.display = "flex";
            contentRow.style.flexDirection = "row";
            contentRow.style.flex = "1 1 auto";

            // Left column (launcher icon + tags)
            const leftColumn = document.createElement('div');
            leftColumn.style.display = "flex";
            leftColumn.style.flexDirection = "column";
            leftColumn.style.alignItems = "flex-start";
            leftColumn.style.marginRight = "15px";
            leftColumn.style.flexShrink = "0";


            // Add these:
            leftColumn.style.maxWidth = "250px"; // or a % like "35%" depending on your layout
            leftColumn.style.overflow = "visible"; // ensures it doesn’t break layout

            // New method for obtaining launcher info
            let foundLauncher = null;
            let ancestor = div;
            for (let i = 0; i < 9; i++) {
              if (!ancestor.parentElement) break;
              ancestor = ancestor.parentElement;
            }

            if (ancestor) {
              const launcher = ancestor.querySelector('div[role="button"], div.Focusable');
              if (launcher) {
                foundLauncher = launcher.textContent.trim();
              }
            }

            // Launcher icons
            const launcherIcons = {
              "Epic Games": "https://cdn2.steamgriddb.com/icon/34ffeb359a192eb8174b6854643cc046/32/96x96.png",
              "GOG Galaxy": "https://cdn2.steamgriddb.com/icon/a928731e103dfc64c0027fa84709689e/32/96x96.png",
              "NonSteamLaunchers": "https://raw.githubusercontent.com/moraroy/NonSteamLaunchers-On-Steam-Deck/refs/heads/main/logo.png",
              "Ubisoft Connect": "https://cdn2.steamgriddb.com/icon/dabcff9ba10224b01fd2ce83f7d73ad6/32/96x96.png",
              "EA App": "https://cdn2.steamgriddb.com/icon/ff51fb7a9bcb22c595616b4fa368880a/32/96x96.png",
              "Amazon Games": "https://cdn2.steamgriddb.com/icon_thumb/6e88ec1459f337d5bea6353f8bff8026.png",
              "itch.io": "https://cdn2.steamgriddb.com/icon/2ad9e5e943e43cad612a7996c12a8796/32/96x96.png",
              "Battle.net": "https://cdn2.steamgriddb.com/icon/739465804a0e17d2a47c9bc9c805d60a/32/96x96.png",
              "Legacy Games": "https://cdn2.steamgriddb.com/icon_thumb/5225802cb9758f9fcd34a679bf9326ec.png",
              "VK Play": "https://cdn2.steamgriddb.com/icon_thumb/5d35998237b55b8778a75732afc080aa.png",
              "HoyoPlay": "https://cdn2.steamgriddb.com/icon/817fccd834f01fb5e1770c8679c0824e/32/256x256.png",
              "Game Jolt Client": "https://cdn2.steamgriddb.com/icon_thumb/17df67628bb89193838f83015a3e7d30.png",
              "Minecraft Launcher": "https://cdn2.steamgriddb.com/icon/0678c572b0d5597d2d4a6b5bd135754c/32/96x96.png",
              "Humble Games Collection": "https://cdn2.steamgriddb.com/icon_thumb/3126ed973cbecde2bbffe419f139f456.png",
              "NVIDIA GeForce NOW": "https://cdn2.steamgriddb.com/icon_thumb/f91ee142269ec908c23e1cd87286e254.png",
              "Waydroid": "https://cdn2.steamgriddb.com/icon_thumb/d6de4f0418bf4015017f5c65cdecc46e.png",
              "Google Chrome": "https://cdn2.steamgriddb.com/icon/3941c4358616274ac2436eacf67fae05/32/256x256.png",
              "Brave": "https://cdn2.steamgriddb.com/icon_thumb/192d80a88b27b3e4115e1a45a782fe1b.png",
              "Vivaldi": "https://cdn2.steamgriddb.com/icon_thumb/51934729f32d36841a17e43e9390483a.png",
              "Mozilla Firefox": "https://cdn2.steamgriddb.com/icon_thumb/fe998b49c41c4208c968bce204fa1cbb.png",
              "LibreWolf": "https://cdn2.steamgriddb.com/icon/791608b685d1c61fb2fe8acdc69dc6b5/32/128x128.png",
              "Microsoft Edge": "https://cdn2.steamgriddb.com/icon_thumb/714cb7478d98b1cb51d1f5f515f060c7.png",
            };

            const launcherName = foundLauncher;
            const launcherIcon = (launcherName && launcherIcons[launcherName]) || null;

            if (launcherIcon) {
              // Row that holds launcher icon + music button
              const launcherRow = document.createElement('div');
              launcherRow.style.display = "flex";
              launcherRow.style.alignItems = "center";
              launcherRow.style.gap = "8px";
              launcherRow.style.marginBottom = "8px";

              // Launcher icon
              const icon = document.createElement('img');
              icon.src = launcherIcon;
              icon.alt = launcherName;
              icon.style.width = "60px";
              icon.style.height = "60px";
              icon.style.objectFit = "contain";
              icon.onerror = () => icon.remove();

              launcherRow.appendChild(icon);

              // Placeholder music button (no logic)
              const musicBtn = document.createElement('button');
              musicBtn.textContent = "🎵";
              musicBtn.style.background = "rgba(36,40,47,0.7)";
              musicBtn.style.color = "white";
              musicBtn.style.border = "none";
              musicBtn.style.borderRadius = "12px";
              musicBtn.style.padding = "6px 10px";
              musicBtn.style.fontSize = "14px";
              musicBtn.style.lineHeight = "1";
              musicBtn.style.cursor = "pointer";
              musicBtn.style.display = "flex";
              musicBtn.style.alignItems = "center";
              musicBtn.style.justifyContent = "center";
              musicBtn.style.transition = "background 0.2s ease";


              launcherRow.appendChild(musicBtn);
              attachThemeMusicBehavior(musicBtn);


              // Add row to left column
              leftColumn.appendChild(launcherRow);
            }


            function createTag(text, fontSize) {
              const tag = document.createElement('span');
              tag.textContent = text;
              tag.style.fontSize = fontSize; // ← use the value passed in
              tag.style.background = "rgba(36,40,47,0.7)";
              tag.style.padding = "3px 8px";
              tag.style.borderRadius = "12px";
              tag.style.whiteSpace = "normal";
              tag.style.display = "inline-block";
              tag.style.wordBreak = "break-word";
              tag.style.marginRight = "4px";
              tag.style.marginBottom = "4px";
              return tag;
            }

            function createTagRow(items) {
              const row = document.createElement('div');
              row.style.display = "flex";
              row.style.flexWrap = "wrap";
              row.style.gap = "4px";

              // Determine font size based on number of items
              const fontSize = items.length > 3 ? "7.8px" : "12px";

              items.forEach(item => row.appendChild(createTag(item, fontSize)));
              return row;
            }


            leftColumn.appendChild(createTagRow((gameData.platforms || "Unknown").split(",").map(p => p.trim())));
            leftColumn.appendChild(createTagRow((gameData.developer || "Unknown").split(",").map(d => d.trim())));
            leftColumn.appendChild(createTagRow((gameData.publisher || "Unknown").split(",").map(p => p.trim())));
            leftColumn.appendChild(createTagRow([gameData.release_date || "Unknown"]));
            leftColumn.appendChild(createTagRow((gameData.genres || "Unknown").split(",").map(g => g.trim())));

            // Right column (description)
            const rightColumn = document.createElement('div');
            rightColumn.style.display = "flex";
            rightColumn.style.flexDirection = "column";
            rightColumn.style.flex = "1";

            const description = document.createElement('p');
            description.textContent = descriptionText;
            description.style.fontSize = "14px";
            description.style.lineHeight = "1.4";
            description.style.background = "rgba(36,40,47,0.7)";
            description.style.padding = "8px 12px";
            description.style.borderRadius = "12px";
            description.style.wordBreak = "break-word";
            description.style.overflowWrap = "break-word";

            rightColumn.appendChild(description);
            contentRow.appendChild(leftColumn);
            contentRow.appendChild(rightColumn);
            overlay.appendChild(contentRow);

            // Bottom links
            const bottomLinks = document.createElement('div');
            bottomLinks.style.position = "absolute";
            bottomLinks.style.bottom = "34px";
            bottomLinks.style.left = "10px";
            bottomLinks.style.right = "10px";
            bottomLinks.style.display = "flex";
            bottomLinks.style.flexWrap = "wrap";
            bottomLinks.style.gap = "6px";

            const searchSites = [
              { name: "Google", url: "https://www.google.com/search?q=", icon: "https://upload.wikimedia.org/wikipedia/commons/2/2f/Google_2015_logo.svg" },

              { name: "PCGW", url: "https://www.pcgamingwiki.com/w/index.php?search=", extra: "&title=Special%3ASearch", icon: "https://pbs.twimg.com/profile_images/876511628258418689/Joehp5YI_400x400.jpg" },
              { name: "HLTB", url: "https://howlongtobeat.com/?q=", icon: "https://howlongtobeat.com/favicon.ico" },
              { name: "SDHQ", url: "https://steamdeckhq.com/?s=", icon: "https://pbs.twimg.com/profile_images/1539310786614419459/5ohiy0ZX_400x400.jpg" },
              { name: "GameFAQs", url: "https://gamefaqs.gamespot.com/search?game=", icon: "https://gamefaqs.gamespot.com/favicon.ico" },
              { name: "AWACY", url: "https://areweanticheatyet.com/?search=", icon: "https://areweanticheatyet.com/icon.webp" },
              { name: "ProtonDB", url: "https://www.protondb.com/search?q=", icon: "https://www.protondb.com/sites/protondb/images/site-logo.svg"},
            ];

            searchSites.forEach(site => {
              const link = document.createElement('a');
              // Minimal change: only modify IsThereAnyDeal URL
              let gameUrl = site.url + encodeURIComponent(gameName) + (site.extra || "");
              if (site.name === "IsThereAnyDeal") {
                // Convert gameName into ITAD slug
                const slug = gameName
                  .toLowerCase()
                  .replace(/[^a-z0-9 ]/g, '') // remove special chars
                  .trim()
                  .replace(/\s+/g, '-');      // spaces → hyphens
                gameUrl = `${site.url}${slug}/info/`;
              }


              link.href = gameUrl;
              link.target = "_blank";
              link.style.display = "inline-flex";
              link.style.alignItems = "center";
              link.style.background = "rgba(36,40,47,0.7)";
              link.style.color = "white";
              link.style.fontSize = "13px";
              link.style.padding = "4px 4px";
              link.style.borderRadius = "6px";
              link.style.textDecoration = "none";
              link.style.transition = "background 0.2s"; // Smooth transition on hover

              // Set initial background on hover state using CSS
              link.onmouseover = () => {
                link.style.background = "rgba(80,80,80,0.9)";
              };
              link.onmouseout = () => {
                link.style.background = "rgba(36,40,47,0.7)";
              };

              const linkIcon = document.createElement('img');
              linkIcon.src = site.icon;
              linkIcon.style.width = "16px";
              linkIcon.style.height = "16px";
              linkIcon.style.marginRight = "4px";
              link.prepend(linkIcon);

              link.appendChild(document.createTextNode(site.name));
              bottomLinks.appendChild(link);
            });


            // --- ITAD button directly under description ---
            const itadSite = {
                name: "",
                url: "https://isthereanydeal.com/game/",
                icon: "https://isthereanydeal.com/public/assets/logo-GBHE6XF2.svg"
            };

            const slug = gameName.toLowerCase()
                .replace(/[^a-z0-9 ]/g, '')
                .trim()
                .replace(/\s+/g, '-');

            const itadUrl = `${itadSite.url}${slug}/info/`;

            const itadLink = document.createElement('a');
            itadLink.href = itadUrl;
            itadLink.target = "_blank";
            itadLink.style.display = "inline-flex";
            itadLink.style.alignItems = "center";
            itadLink.style.background = "rgba(36,40,47,0.7)";
            itadLink.style.color = "white";
            itadLink.style.fontSize = "13px";
            itadLink.style.padding = "6px 12px";
            itadLink.style.borderRadius = "12px";
            itadLink.style.textDecoration = "none";
            itadLink.style.width = "max-content"; // ← keeps button snug
            rightColumn.style.display = "flex";
            rightColumn.style.flexDirection = "column";
            rightColumn.style.alignItems = "flex-end"; // ← aligns all children (including ITAD) to the right


            itadLink.style.marginTop = "0px"; // spacing below description

            itadLink.onmouseover = () => itadLink.style.background = "rgba(80,80,80,0.9)";
            itadLink.onmouseout = () => itadLink.style.background = "rgba(36,40,47,0.7)";

            const itadIcon = document.createElement('img');
            itadIcon.src = itadSite.icon;
            itadIcon.style.width = "16px";
            itadIcon.style.height = "16px";
            itadIcon.style.marginRight = "6px";
            itadLink.prepend(itadIcon);

            itadLink.appendChild(document.createTextNode(itadSite.name));

            // append it **directly under description** in right column
            rightColumn.appendChild(itadLink);





            overlay.appendChild(bottomLinks);
            div.appendChild(img);
            div.appendChild(overlay);
          });
        }
      }
    });
  }


  function attachThemeMusicBehavior(musicBtn) {
      const KEY = "ThemeMusicData";

      const load = () => {
          try { return JSON.parse(localStorage.getItem(KEY) || "{}"); }
          catch { return {}; }
      };

      const save = (data) => {
          try { localStorage.setItem(KEY, JSON.stringify(data)); }
          catch(e){ console.error(e); }
      };

      let data = load();
      let on = data.themeMusic === undefined ? true : !!data.themeMusic;

      // --- Container ---
      const container = document.createElement("div");
      Object.assign(container.style, {
          display: "inline-flex",
          alignItems: "center",
          position: "relative"
      });
      musicBtn.parentElement.insertBefore(container, musicBtn);
      container.appendChild(musicBtn);

      // Initial icon
      musicBtn.textContent = on ? "🎵" : "🔇";

      // --- Bubble tooltip ---
      const bubble = document.createElement("div");
      bubble.innerHTML = "Don't like what you hear? Use paste!";
      Object.assign(bubble.style, {
          position: "absolute",
          bottom: "30px",       // ← move above the button
          top: "auto",           // reset top
          left: "0",
          background: musicBtn.style.background,
          color: musicBtn.style.color,
          border: "none",
          borderRadius: musicBtn.style.borderRadius,
          padding: musicBtn.style.padding,
          fontSize: musicBtn.style.fontSize,
          whiteSpace: "nowrap",
          opacity: "0",
          transform: "translateY(10px)", // ← nudge down slightly for animation
          transition: "opacity 0.3s ease, transform 0.3s ease",
          pointerEvents: "auto",
          zIndex: "1000",
          cursor: "default"
      });

      container.appendChild(bubble);

      const showBubble = (text, isError=false) => {
          if (!on) return;

          if (text) {
              bubble.innerHTML = text;
          } else {
              const themeData = load();
              const current = themeData.currentlyPlaying;
              let linkHTML = "hear";
              if (current?.videoId) {
                  const videoUrl = `https://youtu.be/${current.videoId}`;
                  linkHTML = `<a href="${videoUrl}" target="_blank" style="color:#0af;text-decoration:underline; cursor:pointer;">hear</a>`;
              }
              bubble.innerHTML = `Don't like what you ${linkHTML}? Use paste!`;
          }

          bubble.style.opacity = "1";
          bubble.style.transform = "translateY(0)";
          bubble.style.backgroundColor = isError ? "#F44336" : musicBtn.style.background;
      };

      const hideBubble = () => {
          bubble.style.opacity = "0";
          bubble.style.transform = "translateY(-10px)";
      };

      // --- Paste button (pill style like music button) ---
      const pasteBtn = document.createElement("button");
      pasteBtn.textContent = "📋";
      Object.assign(pasteBtn.style, {
          background: musicBtn.style.background,
          color: musicBtn.style.color,
          border: "none",
          borderRadius: musicBtn.style.borderRadius,  // pill shape
          padding: musicBtn.style.padding,
          fontSize: musicBtn.style.fontSize,
          cursor: "pointer",
          marginLeft: "6px",
          opacity: 0,
          pointerEvents: "none",
          transition: "opacity 0.3s"
      });
      container.appendChild(pasteBtn);

      // --- Paste button logic ---
      pasteBtn.onclick = async () => {
          try {
              const text = await navigator.clipboard.readText();
              const match = text.match(/(?:youtube\.com\/.*v=|youtu\.be\/)([a-zA-Z0-9_-]{11})/);
              if (!match) return showBubble("Invalid YouTube link!", true);

              const newVideoId = match[1];
              const themeData = load();
              const currentThemeName = themeData.currentlyPlaying?.name;
              if (!currentThemeName || !themeData[currentThemeName])
                  return showBubble("No theme currently playing!", true);

              themeData[currentThemeName].videoId = newVideoId;
              themeData[currentThemeName].timestamp = Date.now();
              save(themeData);

              musicBtn.textContent = "🎵";
              showBubble(`Updated "${currentThemeName}"!`);
              setTimeout(() => {
                  pasteBtn.style.opacity = "0";
                  pasteBtn.style.pointerEvents = "none";
              }, 3000);
          } catch (e) {
              console.error(e);
              showBubble("Failed to read clipboard.", true);
          }
      };

      // --- Hover logic (includes bubble itself) ---
      [musicBtn, pasteBtn, bubble].forEach(el => {
          el.addEventListener("mouseenter", () => {
              if (on) {
                  showBubble();
                  pasteBtn.style.opacity = "1";
                  pasteBtn.style.pointerEvents = "auto";
              }
          });
          el.addEventListener("mouseleave", () => {
              setTimeout(() => {
                  if (!on || ![musicBtn, pasteBtn, bubble].some(el => el.matches(':hover'))) {
                      hideBubble();
                      pasteBtn.style.opacity = "0";
                      pasteBtn.style.pointerEvents = "none";
                  }
              }, 200); // slightly longer delay to allow moving into bubble
          });
      });

      // --- Toggle music on/off ---
      musicBtn.onclick = () => {
          on = !on;
          musicBtn.textContent = on ? "🎵" : "🔇";
          const saved = load();
          saved.themeMusic = on;
          save(saved);
          if (!on) {
              hideBubble();
              pasteBtn.style.opacity = "0";
              pasteBtn.style.pointerEvents = "none";
          }
      };
  }

  replaceText();

  if (!(window as any).steamEnhancerObserver) {
    const observer = new MutationObserver(replaceText);
    observer.observe(document.body, { childList: true, subtree: true });

    (window as any).steamEnhancerObserver = observer;
  }
}
