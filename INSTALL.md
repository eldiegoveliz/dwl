# Install the configuration on Arch Linux

1. Install `base-devel`, `git`, and `yay` before running the installer.
2. Clone this repository:

   ```sh
   git clone https://github.com/eldiegoveliz/dwl.git
   cd dwl
   ```

3. Edit `wallpaper.conf` for your image paths. If an image is missing, the
   wallpaper uses a solid background. Edit the battery modules in
   `yambar/config.yml` to match `/sys/class/power_supply` on this laptop.
4. Run the installer as your normal user:

   ```sh
   ./install.sh
   ```

5. Set your location in `~/.config/darkman/config.yaml` for sunrise and sunset.
6. Log out and select **dwl** in SDDM.

The installer downloads the AUR dwl recipe, verifies the upstream release
archive, and builds a pacman package with your `config.h`. Sources and packages
stay in `~/.cache/dwl-config-install`. Yambar uses its upstream release with
compiler warnings allowed on recent GCC versions. Neither program's source is patched.

The checkout is linked to `~/.config/dwl`; user services and the darkman handler
are linked into your home. The SDDM entry is installed under
`/usr/local/share/wayland-sessions/dwl.desktop`, ahead of the packaged stock entry.
If `~/.config/dwl` already belongs to another setup, move it before installation.

After editing `config.h`, run `./install.sh` and start a new dwl session.
For a build without installation, run `./install.sh build`.
To recreate home-directory links, run `./install.sh link`.
After editing bar settings, run `systemctl --user restart dwl-bar.service`.
