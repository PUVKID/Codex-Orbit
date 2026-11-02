# Codex Orbit 2.10.0 · Quick guide

Run CodexOrbit.exe directly, or use CodexOrbit-Setup.exe to install it for the current Windows user. The installer supports Korean and English.

Choose 한국어 or English in the detail window's top language selector, or in the desktop widget's right-click menu. The selection is saved. Drag the widget to move it; drag its right or bottom edge to resize it. Click it to open change history.

Worldwide location and current temperature use the internet connection's approximate IP location. Windows Location Services are not required. Place names use Open-Meteo/GeoNames translations. If a translation or reliable match is unavailable, the original place name is shown. VPNs and mobile networks may point to a different region.

The GPU renders an actual 3840×2160 source and downsamples it to the widget size before transfer. Pacing targets 240 fps; measured development-window generation was approximately 233–235 fps, so fixed 240 fps has not been achieved. Rendered frames, GUI paint counts and physical monitor refresh rate are different measurements.

Usage bars show the account's remaining rate-limit percentage, not an exact token count. Chat titles, model IDs, role IDs and recorded public reasons remain unchanged when the interface language changes. Reasons not present in the source are not invented.

The uninstaller preserves user instructions, backups and history. Included default instructions are not applied silently. Do not share your account credentials, local chat data or personal instruction files with the application package.

Sources: https://open-meteo.com/ · https://www.geonames.org/ · https://ipwhois.io/


## Rotation speed

Use the Rotation speed slider near the top of the details window to select0.25×–3×. Reset to1× restores the default. You can also right-click the desktop widget and choose a speed preset. The choice is saved and restored on restart.

Speed changes preserve the current animation phase. They affect the rings and sculpture only; clock, date, weather and usage updates retain their real-time schedules. Rotation speed and the240fps pacing target are separate controls of the animation.


## Version 26 rotation speed

Use the detail window slider or widget context menu to select 0.25–3× speed. The setting persists across restarts. Korean and English are supported. Further work toward fixed 240fps was withdrawn by the user. Recent measurements were approximately 227–230 generated frames/s and 214–229 unique Qt paints/s; these are separate from physical display refresh.
