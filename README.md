# Personal dwl desktop

Native Wayland with Foot, Waybar, Fuzzel, Mako, Kanshi, and darkman. Terminals,
the launcher, and notifications share a palette. The bar uses charcoal in dark
mode and translucent gray in light mode. All four use real
background blur.
Blur samples the cached wallpaper to keep GPU work modest.

This repository contains configuration, session helpers, an installer, and two
small patches for layer-surface blur and window placement. Upstream compositor
source and downloaded community patches stay in `~/.cache/dwl-config-install/rice`.

## Configuration

| File | Controls |
| --- | --- |
| `theme/dark.conf`, `theme/light.conf` | Shared colors and transparency |
| `theme/matugen.conf` | Enable wallpaper accents, scheme, and source-color index |
| `matugen/palette.conf` | Matugen template for accents and harmonized ANSI colors |
| `config.h` | Shortcuts, layouts, touchpad, gaps, and blur strength |
| `foot/foot.ini` | Terminal font, padding, cursor, and scrollback |
| `waybar/config.json`, `waybar/style.css` | Bar modules, hover details, click actions, and styling |
| `waybar/palette.conf` | Dark-mode bar colors and opacity; light mode uses `theme/light.conf` |
| `fuzzel/fuzzel.ini` | Application launcher |
| `mako/config` | Notifications and grouped volume/brightness feedback |
| `kanshi/config` | Docked, laptop, and extended monitor profiles |
| `wallpaper.conf` | Dark and light wallpaper paths |

Darkman switches the bar, launcher, notifications, wallpaper, and open Foot
windows. The default bar hides CPU/RAM; full mode restores them. Battery status
combines both packs by stored energy rather than averaging their percentages.
New windows appear after the focused tiled window, preserving the existing
master. Opening from a floating window appends to the stack.

Music sits at the center of the screen; date and time sit at the far right.
Resources, connectivity, and audio/power indicators form separate groups.
Music uses MPRIS players (including browsers) with MPD as a fallback. Click the
song to play/pause, use the adjacent previous/next buttons, or scroll to change
tracks. Long titles scroll while playing; hover lists all reported audio sources.
Apps without MPRIS use their active output-stream title, or their app name when
no title is supplied. Clicking these sources opens the audio mixer. Their
previous/next controls are unavailable because the app supplies no transport controls.
Right-click to open ncmpcpp. When no player is available, clicking opens ncmpcpp.
Wi-Fi shows an icon; hover shows the network name, signal, IP, gateway, and live
download/upload rates. CPU and RAM use icons in full mode with details on hover. Disk
shows available space on the home filesystem and turns red below 10% free.
`TS 2` means Tailscale is connected with two peers online; click for status.
Bluetooth shows power/connection state; hover lists connected devices and
battery levels when supplied. Click to open Blueman, or right-click for
bluetoothctl in a terminal. The bar displays the adapter's existing power state.
CAPS appears only while Caps Lock is enabled. Song and window titles occupy less
space on smaller displays to leave room for the right-side indicators.

Waybar reads tags, layout, and the focused title from dwl's existing stdout.
Click a tag to switch; right-click to toggle it alongside the selected tags.
Click the layout/title area to cycle layouts, right-click for monocle, and
middle-click to promote the focused window to master, as in the dwm workflow.
Tag shortcuts remain Super+1–9. The `panel` name uses the existing layer blur
support. Bar configuration changes do not require rebuilding dwl.

Foot uses GeistMono Nerd Font at 10 pt. Edit `font=` in `foot/foot.ini`; the
terminal helper reads that line whenever it opens a window. Existing windows
can use Ctrl+- / Ctrl++ to change size and Ctrl+0 to reset it.

Light-mode glass uses `background=e5e8ec`, `terminal_alpha=0.72`, and
`bar_alpha=0.74` in `theme/light.conf`. Lower alpha makes more wallpaper visible;
`1.0` is opaque. Blur strength is set separately in `config.h`.

With Matugen installed, changing a wallpaper and restarting
`dwl-wallpaper.service` also refreshes the bar, launcher, notifications, and
open Foot windows. Existing terminal sessions stay open. New terminals receive
both current palettes even when the Foot server predates the color change.
Darkman still selects light/dark mode. Generated palettes are cached under
`$XDG_RUNTIME_DIR/dwl/matugen`; backgrounds, foregrounds, and opacity remain
in the manual theme files. Set `enabled=0` in `theme/matugen.conf` to use the
manual accent and ANSI colors too. Matugen is optional on other laptops.

The template uses the [official Matugen workflow](https://iniox.github.io/#matugen/getting-started)
and its `harmonize` filter to coordinate terminal colors with the wallpaper.

## Shortcuts

| Shortcut | Action |
| --- | --- |
| Super+Shift+Enter | Open Foot |
| Super+P | Application launcher |
| Super+B | Show/hide the bar |
| Super+S / Super+Shift+S | Full/minimal status bar |
| Super+Ctrl+B | Toggle blur everywhere |
| Super+Ctrl+Shift+B | Toggle blur for the focused window |
| Super+G | Toggle gaps |
| Super+Shift+D | Switch between docked and extended displays |
| Super+T / Super+F / Super+M | Tile/floating/monocle |
| Super+1–9 / Super+Shift+1–9 | View a tag/move a window to a tag |
| Super+Shift+E | Fullscreen |
| Super+Shift+F / Super+Shift+T | Firefox Nightly/T3 Code |
| Super+E / Super+Shift+M / Super+C | lf/ncmpcpp/calcurse |
| Super+Print / Super+Shift+Print | Full/region screenshot, saved and copied |

The existing focus, master size, monitor, media, and volume shortcuts remain in
`config.h`. The bar clock opens calcurse, audio opens pavucontrol, and network
opens iwctl. Middle-click audio to mute. Scroll audio to adjust volume.

## Build inputs

`build/sources.json` pins an upstream dwl revision and the community
[blur](https://codeberg.org/dwl/dwl-patches/src/branch/main/patches/blur) and
[gaps](https://codeberg.org/dwl/dwl-patches/src/branch/main/patches/gaps) patches.
`build/layer-blur.patch` adds blur to the layer names used by Waybar, Fuzzel,
and Mako, including transparency masks and the global blur toggle.
`build/attach-below.patch` restores dwm's insertion order without changing the
focus order or the Super+Enter action that promotes a window to master.

The installer verifies download hashes, applies the patches, copies `config.h`,
builds a pacman-owned `dwl` package, and checks that XWayland is disabled.
See [INSTALL.md](INSTALL.md) to install or rebuild.
