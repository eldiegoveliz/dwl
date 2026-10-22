#!/bin/sh
# Keep upstream dwl and community patches in the cache; install only the result.
set -eu
repo=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cache=${XDG_CACHE_HOME:-$HOME/.cache}/dwl-config-install/rice
config=$HOME/.config/dwl
case ${1:-install} in install|build|link) action=${1:-install} ;; *) exit 2 ;; esac
if [ "$action" != build ] && { [ -e "$config" ] || [ -L "$config" ]; } \
    && [ "$(readlink -f "$config")" != "$repo" ]; then
    printf '%s belongs to another checkout. Move it before linking this one.\n' "$config" >&2
    exit 1
fi
privileged() {
    if sudo -n true 2>/dev/null; then
        sudo "$@"
    elif command -v pkexec >/dev/null 2>&1 && [ -n "${WAYLAND_DISPLAY:-}${DISPLAY:-}" ]; then
        pkexec "$@"
    else
        sudo "$@"
    fi
}
if [ "$action" = install ]; then
    privileged /usr/bin/pacman -S --needed --noconfirm foot fuzzel mako kanshi \
        scenefx wlroots0.20 swaybg wlr-randr grim slurp wl-clipboard jq gettext \
        darkman htop pavucontrol upower xdg-user-dirs python patch base-devel playerctl mpc waybar iw iproute2 \
        bluez bluez-utils blueman wtype
fi
if [ "$action" != link ]; then
    "$repo/scripts/dwl-build"
    [ "$action" != build ] || exit 0
    if pacman -Q dwl-personal >/dev/null 2>&1; then
        privileged /usr/bin/pacman -R --noconfirm dwl-personal
    fi
    package=$(python -c 'import json,sys; print(json.load(open(sys.argv[1]))["package"])' "$cache/build.json")
    privileged /usr/bin/pacman -U --noconfirm "$package"
fi
mkdir -p "$HOME/.config/systemd/user" "$HOME/.local/share/darkman" "$cache"
ln -sfn "$repo" "$config"
for unit in dwl-bar dwl-notifications dwl-wallpaper dwl-terminal dwl-monitors; do
    ln -sfn "$config/$unit.service" "$HOME/.config/systemd/user/$unit.service"
done
ln -sfn "$config/scripts/dwl-theme" "$HOME/.local/share/darkman/dwl-theme"
systemctl --user daemon-reload
sed "s|@CONFIG_DIR@|$config|g" "$repo/dwl.desktop" > "$cache/dwl.desktop"
if [ "$action" = install ]; then
    privileged /usr/bin/install -Dm644 "$cache/dwl.desktop" /usr/local/share/wayland-sessions/dwl.desktop
fi
printf 'Ready. Log out and select dwl in the login screen.\n'
