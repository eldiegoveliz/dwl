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
        darkman htop pavucontrol upower xdg-user-dirs python patch base-devel
    if ! pacman -Q yambar >/dev/null 2>&1; then
        privileged /usr/bin/pacman -S --needed --noconfirm meson ninja scdoc tllist
        bar_cache=${XDG_CACHE_HOME:-$HOME/.cache}/dwl-config-install/yambar-aur
        if [ ! -d "$bar_cache/.git" ]; then
            git clone https://aur.archlinux.org/yambar.git "$bar_cache"
        fi
        git -C "$bar_cache" show HEAD:PKGBUILD > "$bar_cache/PKGBUILD"
        sed -i '/--buildtype=release/a\        -Dwerror=false \\' "$bar_cache/PKGBUILD"
        curl --fail --silent --show-error \
            https://keys.openpgp.org/vks/v1/by-fingerprint/B19964FBBA09664CC81027ED5BBD4992C116573F | gpg --import
        (cd "$bar_cache" && makepkg --force --cleanbuild)
        privileged /usr/bin/pacman -U --noconfirm "$bar_cache"/yambar-[0-9]*.pkg.tar.zst
    fi
fi
if [ "$action" != link ]; then
    "$repo/scripts/dwl-build"
    [ "$action" != build ] || exit 0
    if pacman -Q dwl-personal >/dev/null 2>&1; then
        privileged /usr/bin/pacman -R --noconfirm dwl-personal
    fi
    privileged /usr/bin/pacman -U --noconfirm "$cache"/dwl-[0-9]*.pkg.tar.zst
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
