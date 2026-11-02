# 🪐 Codex Orbit 3.0.1 · User guide

The original daily calendar sculpture is the default desktop view. Model notifications keep its date-based title and artwork. The 3D observatory remains available as an explicit display-mode choice.

Run the portable `CodexOrbit.exe` or install `CodexOrbit-Setup.exe` for the current Windows user. Do not run both against the same data directory. Click the transparent widget for history and account usage; drag to move and use the right/bottom edges to resize.

## Notifications

Notifications show the chat title, previous model and reasoning effort, current model and reasoning effort, and a short explanation. Decorative emoji are removed from the displayed title without renaming the original chat. ☀️ Sol, ✨ Astra, 🌍 Terra and 🌙 Luna retain exact model IDs. Effort levels use distinct emoji. Unknown values and unpublished reasons are never invented.

Each change is presented independently. Hover pauses dismissal; pin keeps a card open; bookmark saves it in history. Changes beyond the visible-card limit remain in history. Assignment and resumed work are distinguished from setting changes.

## Live 3D observatory

Three thick metallic rings rotate on independent axes with actual depth and lighting. Model cores use a sun, crystal, globe or crescent; an unknown model uses a neutral core. Observed workers appear as satellites. Click a satellite or list entry to open its history. Pinned chats take priority, with up to 24 satellites and all workers available in the list.

Only explicit local records supply running, completed, waiting, error or aborted states. Selected settings and observed execution settings are shown separately. Previous and current values have equal emphasis; only changed fields are highlighted.

The history slider replays saved events without changing Codex settings. Since-last-visit summaries and bookmarks help find changes. Direct chat navigation is not claimed; copying a chat ID is available instead.

## Display controls

Choose English or Korean, observatory or calendar mode, rotation speed, pause, reduced motion, and Eco/Balanced/High quality. Text scale is independent of widget size. Use the left navigation to view the observatory, activity or usage separately, including in smaller windows. Edge docking folds the widget into a handle near a screen edge and expands it on hover. Monitor changes correct off-screen positions.

High-quality source frames are 3840×2160 and are delivered at the required display size. A fixed 240 fps is not promised or newly targeted. Pausing motion keeps monitoring, notifications and the clock active.

Broadcast mode immediately masks titles and work descriptions in existing notifications and the open detail view, while preserving stored originals. Optional short notification sounds are off by default.

## Usage, temperature and time

Remaining usage is the actual account-limit percentage provided through the signed-in Codex installation, **not an exact remaining-token count**. Numbers, bars and the 3D container distinguish unavailable data from 0%. Stale data retain an explicit status.

The widget shows the time, current temperature and IP-estimated location worldwide where the services provide data. Windows Location Services are not required. VPNs and network routing may change the estimated region.

Calendar mode retains 888 monthly themes for 2026–2099 and procedural daily subjects. See the monthly-theme Markdown and CSV. This does not mean that every date has a separately hand-built model file.

## MD, diagnostics and updates

`기본_지침.md` is a shareable starter. Remove personal conversations, contact information and secrets before sharing your own Markdown. To apply instructions in Codex, use a supported instruction file in the intended project; this widget does not force instructions into all chats or expose private reasoning.

Save diagnostics ZIP writes only whitelisted, non-sensitive diagnostics locally. It excludes conversation/event originals, credentials and personal paths, and never sends the archive automatically.

Check for updates uses only official `PUVKID/Codex-Orbit` HTTPS releases. Downloads are SHA-256 verified before the user installs and restarts. A failed restart check restores the previous executable. Personal settings and Markdown are preserved. Source runs do not install themselves as a distributed EXE.

## Requirements and limits

Windows 10/11 x64 with an OpenGL 3.3 graphics driver. Monitoring uses locally available Codex records and settings, not server identity proof or private reasoning. Unrecorded reasons, previous values and activity states remain unknown. Monitor interruption/recovery notifications are emitted only when the state changes. Personal data stay in the user's AppData/CodexOrbit folder; uninstall does not silently erase them. Bundled license notices cover redistribution.
