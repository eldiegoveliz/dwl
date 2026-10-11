# Install Diego's dwl setup

This tree uses dwl 0.9 and wlroots 0.20. The port adds a dwm-style built-in bar
and tiled gaps. XWayland support is disabled.

`config.h` contains the current dwm shortcuts, nine tags, layouts, colors,
GeistMono font, and 10-pixel gaps. The keyboard layout is `latam`.
The additional `Super+Shift+E` shortcut toggles fullscreen.

## Build and install on Arch Linux

Install the dependencies listed in `PKGBUILD`, then run:

```sh
makepkg --force --cleanbuild
sudo pacman -U ./dwl-personal-0.9-1-*.pkg.tar.zst
```

The build checks the actual keybinding resolver and runs the compositor with
a native terminal, clipboard, and screenshot on an isolated headless Wayland
display. It does not start services in your current desktop session.

Select **dwl** in SDDM after logging out. The session starts its wallpaper,
notification daemon, authentication agent, and status producer. `Super+Shift+Enter`
opens foot. `Super+P` opens wmenu. `Super+B` toggles the bar.

The package installs the session launcher at `/usr/bin/dwl-session` and its
helper scripts and terminal settings under `/usr/share/dwl`. It does not
depend on the checkout location or a particular username.

An existing slstatus installation supplies the full and compact status modes.
Those processes run with `-s`, which writes to stdout without opening an X
display. If slstatus is unavailable, the bar shows a clock.
Set `DWL_WALLPAPER` to override the wallpaper path used by the session.

## Regenerate the configuration

The checked-in `config.h` can be built directly on another laptop.
To import a newer copy of the original dwm configuration, run:

```sh
python scripts/port-dwm.py /path/to/dwm/config.h --layout latam
makepkg --force --cleanbuild
```

The generator translates X11 key symbols and modifier names, replaces the
desktop-specific commands, and preserves the original bindings. Rules use
Wayland app IDs. Changes to the compiled configuration take effect at the
next dwl login.

`patches/dwm-bar-gaps-0.9.patch` records the source changes against the
upstream `v0.9` tag. The bar implementation comes from the community bar patch
by sewn and the existing bar/gaps change in commit `e64e0ec` of this repository.
The port retains dwl 0.9's input-method, focus, and capture support.

## Uninstall

```sh
sudo pacman -R dwl-personal
```
