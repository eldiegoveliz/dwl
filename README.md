# Personal dwl desktop

Native Wayland with Foot, Yambar, Fuzzel, Mako, Kanshi, and darkman. Terminals,
the bar, launcher, and notifications share a palette and use real background
blur. Blur samples the cached wallpaper to keep GPU work modest.

This repository contains configuration, session helpers, an installer, and two
small patches for layer-surface blur and window placement. Upstream compositor
source and downloaded community patches stay in `~/.cache/dwl-config-install/rice`.

## Configuration

| File | Controls |
| --- | --- |
| `theme/dark.conf`, `theme/light.conf` | Shared colors and transparency |
| `config.h` | Shortcuts, layouts, touchpad, gaps, and blur strength |
| `foot/foot.ini` | Terminal font, padding, cursor, and scrollback |
| `yambar/config.yml` | Tags, clock, music, disk, Tailscale, resources, audio, network, and battery |
| `fuzzel/fuzzel.ini` | Application launcher |
| `mako/config` | Notifications and grouped volume/brightness feedback |
| `kanshi/config` | Docked, laptop, and extended monitor profiles |
| `wallpaper.conf` | Dark and light wallpaper paths |

Darkman switches the bar, launcher, notifications, wallpaper, and open Foot
windows. The default bar hides CPU/RAM; full mode restores them. Battery status
combines both packs by stored energy rather than averaging their percentages.
New windows appear after the focused tiled window, preserving the existing
master. Opening from a floating window appends to the stack.

Music uses MPRIS players (including browsers) with MPD as a fallback. Left-click
to play/pause, right-click to open ncmpcpp, and scroll to change tracks. Disk
shows available space on the home filesystem and turns red below 10% free.
`TS 2` means Tailscale is connected with two peers online; click for status.
CAPS appears only while Caps Lock is enabled. Song and window titles shorten on
smaller displays to leave room for the right-side indicators.

Foot uses GeistMono Nerd Font at 10 pt. Edit `font=` in `foot/foot.ini`; the
terminal helper reads that line whenever it opens a window. Existing windows
can use Ctrl+- / Ctrl++ to change size and Ctrl+0 to reset it.

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
`build/layer-blur.patch` adds blur to the layer names used by Yambar, Fuzzel,
and Mako, including transparency masks and the global blur toggle.
`build/attach-below.patch` restores dwm's insertion order without changing the
focus order or the Super+Enter action that promotes a window to master.

The installer verifies download hashes, applies the patches, copies `config.h`,
builds a pacman-owned `dwl` package, and checks that XWayland is disabled.
See [INSTALL.md](INSTALL.md) to install or rebuild.
