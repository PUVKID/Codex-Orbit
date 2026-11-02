# 🪐 Codex Orbit 2.10.0 · Quick guide

Run `CodexOrbit.exe` without installation, or install for the current Windows user with `CodexOrbit-Setup.exe`. Windows 10/11 x64 is required. Python is bundled. The animated 3D widget requires an OpenGL 3.3 capable graphics driver; loading and failures are shown separately.

Drag the transparent widget to move it. Drag its right/bottom edges or bottom-right corner to resize it. Click to open details. Position and size persist. Select Korean or English in the details header or widget context menu.

Use the rotation speed slider or context menu to select 0.25–3×. Reset restores 1×. The setting persists and preserves animation phase; clock, weather and usage refresh intervals remain unchanged.

Model and reasoning changes show **before → after** separately. Worker assignments and resumptions are distinct event types. Recorded chat titles, tasks and public reasons are preserved. Missing previous values or reasons are shown as unavailable; private reasoning is not reconstructed.

Monitoring observes local selection state before message submission once locally recorded. Remote/cloud chats, unrecorded UI choices and server model identity are outside its assurance. Limits include 4,096 files, 2MiB records and a per-cycle read budget. Up to eight notices are visible; older notices are hidden while the latest 500 history entries are retained. First launch establishes a baseline without replaying old events.

The clock uses PC local time. Approximate worldwide location uses the connection IP without Windows Location Services. Temperature refreshes every five minutes using Open-Meteo; IP location uses ipwho.is. VPNs and carrier networks may report a different region. Failed/stale readings are identified.

Usage bars show the account's actual **remaining rate-limit percentage**, not an exact remaining token count. The read-only account query refreshes every 30 seconds. Missing readings are not replaced with invented values.

Daily sculptures cover 27,028 Korean-calendar dates across 2026–2099, using 888 year/month motif combinations and shared geometry rules. These are not individually handcrafted models. Daily art changes at Korean midnight, while the displayed clock follows PC local time.

The GPU source is 3840×2160, downsampled to widget size. Fixed 240fps was not achieved; further attempts were withdrawn. Generated frames, Qt paints and physical display refresh are different measurements. EXE/shortcut icons are static; motion appears in the running widget.

User settings, MD instructions, backups and history remain in `%LOCALAPPDATA%/CodexOrbit`. Settings, My Instructions and Help tabs are not exposed. Included instructions are not applied silently or injected into every chat. The uninstaller preserves user instructions, backups and history. Never share credentials, local chats or personal instruction files.

Check downloads against `SHA256SUMS.txt`; dependency licenses are in `Licenses.zip`. Public source and 87 public tests are available in the [repository](https://github.com/PUVKID/Codex-Orbit). GitHub's automatic source ZIP contains public repository files only; the private local full-source archive is not distributed.
