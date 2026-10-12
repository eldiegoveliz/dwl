# Install the desktop

On Arch Linux, run this as your normal user:

```sh
./install.sh
```

The installer installs dependencies, builds the pinned dwl package in your
cache, and links this checkout to `~/.config/dwl`. Privileged commands use sudo
or the desktop authentication dialog. It creates a dwl session entry for SDDM.

Log out and select **dwl** in the login screen. Compositor changes, including
blur and keybindings, take effect after logging in again.

## Configure another laptop

1. Install GeistMono Nerd Font for the configured typography.
2. Set your wallpaper paths in `wallpaper.conf`.
3. Set the laptop and external-monitor identifiers in `kanshi/config`.
4. Adjust the extended display position for your laptop resolution.

Run `wlr-randr` to see connected display names and descriptions. Kanshi selects
the docked profile when the configured desk display is connected, and the laptop
profile when it is absent. Super+Shift+D switches to the extended profile and back.

## Rebuild after editing config.h

```sh
./install.sh
```

To build without installing the package or changing symlinks:

```sh
./install.sh build
```

To recreate symlinks and reload user-unit definitions without rebuilding:

```sh
./install.sh link
```

## Apply app configuration changes

After editing the shared palettes or app configs, regenerate them:

```sh
~/.config/dwl/scripts/dwl-render-theme
makoctl reload
systemctl --user restart dwl-bar.service
```

New launcher windows use the regenerated config. Foot's `font=` setting applies
to new windows immediately; existing windows support Ctrl+- / Ctrl++ / Ctrl+0.
For changes to Foot's padding or palette definitions, close its terminal
windows first, then run
`systemctl --user restart dwl-terminal.service`. Use darkman's light/dark switch
to change between the existing palettes without closing terminals.

After editing monitor profiles, reload Kanshi:

```sh
kanshictl reload
```
