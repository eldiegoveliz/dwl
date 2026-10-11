# Personal dwl desktop

Native Wayland with Foot, Yambar, Fuzzel, Mako, Kanshi, and darkman. Terminals,
the bar, launcher, and notifications share a palette and use real background
blur. Blur samples the cached wallpaper to keep GPU work modest.

This repository contains configuration, session helpers, an installer, and one
86-line patch for layer-surface blur. Upstream compositor source and downloaded
community patches stay in `~/.cache/dwl-config-install/rice`.

## Configuration

| File | Controls |
| --- | --- |
| `theme/dark.conf`, `theme/light.conf` | Shared colors and transparency |
| `config.h` | Shortcuts, layouts, touchpad, gaps, and blur strength |
| `foot/foot.ini` | Terminal font, padding, cursor, and scrollback |
| `yambar/config.yml` | Tags, clock, audio, network, and combined battery indicator |
| `fuzzel/fuzzel.ini` | Application launcher |
| `mako/config` | Notifications and grouped volume/brightness feedback |
| `kanshi/config` | Docked, laptop, and extended monitor profiles |
| `wallpaper.conf` | Dark and light wallpaper paths |

Darkman switches the bar, launcher, notifications, wallpaper, and open Foot
windows. The default bar hides CPU/RAM; full mode restores them. Battery status
combines both packs by stored energy rather than averaging their percentages.

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

The installer verifies download hashes, applies the patches, copies `config.h`,
builds a pacman-owned `dwl` package, and checks that XWayland is disabled.
See [INSTALL.md](INSTALL.md) to install or rebuild.
