# dwl configuration

Personal configuration for [upstream dwl](https://codeberg.org/dwl/dwl), with
Yambar, Kitty, Dunst, wmenu, and darkman. Compositor source, patches, and build
artifacts are outside this repository.

The installed dwl is the upstream 0.9 release with this `config.h` compiled in.
XWayland is disabled. Nine tags, tile, floating, and monocle layouts use Super
shortcuts and a Latin American keyboard layout. Firefox starts on the current tag.

Yambar reads dwl's standard status output through its
[native dwl module](https://codeberg.org/dnkl/yambar/src/branch/master/doc/yambar-modules-dwl.5.scd).
The bar has live tags and titles, a clock, CPU and memory usage, Wi-Fi, audio,
both batteries, and a theme button. Each enabled monitor gets a bar.
Darkman changes the bar, notifications, and wallpaper; new Kitty windows use
the current palette. Existing Kitty windows keep their launch palette.

Stock dwl has no window gaps or built-in bar. Tags use keyboard shortcuts.
Yambar does not provide the previous Waybar hover tooltips or tray.
Status items open tools on click, and the audio item supports scrolling.

| File | Purpose |
| --- | --- |
| `config.h` | Compiled dwl shortcuts, rules, colors, and input settings |
| `yambar/config.yml` | Bar layout, labels, and click actions |
| `scripts/dwl-bar` | Bar palettes and monitor startup |
| `kitty/` | Terminal settings and palettes |
| `dunst/` | Notification settings and palettes |
| `wallpaper.conf` | Editable wallpaper paths |
| `scripts/` | Session startup, screenshots, display control, and theme actions |
| `*.service`, `dwl.desktop` | Session and user-service configuration |
| `install.sh` | Upstream package build and configuration links |

| Shortcut | Action |
| --- | --- |
| Super+Shift+Enter | Open Kitty |
| Super+P | Open wmenu |
| Super+1 through Super+9 | View a tag |
| Super+Shift+1 through Super+Shift+9 | Move a window to a tag |
| Super+B | Hide or show the bar |
| Super+S / Super+Shift+S | Full or compact bar |
| Super+Shift+D | Toggle the laptop display when another output is enabled |
| Super+Print / Super+Shift+Print | Full or region screenshot, saved and copied |
| Super+Shift+E | Toggle fullscreen |
| Super+Shift+Q | Exit dwl |

Clock clicks open calcurse, CPU and memory open htop, Wi-Fi opens iwctl, and
the batteries open upower details. Audio clicks open pavucontrol; middle-click
mutes, and scrolling changes volume. The theme button switches darkman modes.

Installation and rebuild commands are in [INSTALL.md](INSTALL.md).
