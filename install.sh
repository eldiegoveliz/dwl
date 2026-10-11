#!/bin/sh
# Build stock dwl with config.h, then link this configuration into your home.
set -eu
repo=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cache=${XDG_CACHE_HOME:-$HOME/.cache}/dwl-config-install/dwl-aur
config=$HOME/.config/dwl
case ${1:-install} in
    build|link|install) action=${1:-install} ;;
    *) printf 'usage: %s [build|link|install]\n' "$0" >&2; exit 2 ;;
esac
if [ "$action" != build ] && { [ -e "$config" ] || [ -L "$config" ]; } \
    && [ "$(readlink -f "$config")" != "$repo" ]; then
    printf '%s already exists. Move it before linking this checkout.\n' "$config" >&2
    exit 1
fi
if [ "$action" = install ]; then
    yay -S --needed kitty dunst wmenu swaybg wlr-randr grim slurp \
        wl-clipboard jq gettext darkman htop pavucontrol upower xdg-user-dirs
    if ! pacman -Q yambar >/dev/null 2>&1; then
        yay -S --needed meson ninja scdoc tllist
        bar_cache=${XDG_CACHE_HOME:-$HOME/.cache}/dwl-config-install/yambar-aur
        if [ ! -d "$bar_cache/.git" ]; then
            git clone https://aur.archlinux.org/yambar.git "$bar_cache"
        fi
        git -C "$bar_cache" show HEAD:PKGBUILD > "$bar_cache/PKGBUILD"
        # Yambar 1.11 treats warnings from newer GCC releases as errors.
        # This changes a compiler option, with upstream source left intact.
        sed -i '/--buildtype=release/a\        -Dwerror=false \\' "$bar_cache/PKGBUILD"
        curl --fail --silent --show-error \
            https://keys.openpgp.org/vks/v1/by-fingerprint/B19964FBBA09664CC81027ED5BBD4992C116573F | gpg --import
        (cd "$bar_cache" && makepkg --syncdeps --force --cleanbuild)
        sudo pacman -U "$bar_cache"/yambar-[0-9]*.pkg.tar.zst
    fi
fi
if [ "$action" != link ]; then
    mkdir -p "$cache"
    curl --fail --location --silent --show-error \
        'https://aur.archlinux.org/cgit/aur.git/plain/PKGBUILD?h=dwl' > "$cache/PKGBUILD"
    cp "$repo/config.h" "$cache/config.h"
    # The AUR recipe includes an empty config.h. Update only its checksum.
    empty_hash=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
    config_hash=$(sha256sum "$cache/config.h" | cut -d ' ' -f1)
    if ! grep --quiet "$empty_hash" "$cache/PKGBUILD"; then
        printf 'The AUR config.h recipe changed. Review %s before building.\n' "$cache/PKGBUILD" >&2
        exit 1
    fi
    sed -i "s/$empty_hash/$config_hash/" "$cache/PKGBUILD"
    sed -i 's/^\([[:space:]]*\)make$/\1make VERSION="$pkgver"/' "$cache/PKGBUILD"
    if [ "$action" = install ]; then
        (cd "$cache" && makepkg --syncdeps --force --cleanbuild)
    else
        (cd "$cache" && makepkg --force --cleanbuild)
    fi
    if [ "$action" = build ]; then exit 0; fi
    if pacman -Q dwl-personal >/dev/null 2>&1; then
        sudo pacman -R dwl-personal
    fi
    sudo pacman -U "$cache"/dwl-[0-9]*.pkg.tar.zst
fi
mkdir -p "$(dirname "$config")" "$HOME/.config/systemd/user" "$HOME/.local/share/darkman"
ln -sfn "$repo" "$config"
for unit in dwl-bar dwl-notifications dwl-wallpaper; do
    ln -sfn "$config/$unit.service" "$HOME/.config/systemd/user/$unit.service"
done
ln -sfn "$config/scripts/dwl-theme" "$HOME/.local/share/darkman/dwl-theme"
if [ "$(readlink "$HOME/.local/share/darkman/dwl-bar" 2>/dev/null || true)" = /usr/share/dwl/scripts/dwl-bar-theme ]; then
    rm "$HOME/.local/share/darkman/dwl-bar"
fi
systemctl --user daemon-reload
sed "s|@CONFIG_DIR@|$config|g" "$repo/dwl.desktop" > "$cache/dwl.desktop"
if [ "$action" = install ]; then
    sudo install -Dm644 "$cache/dwl.desktop" /usr/local/share/wayland-sessions/dwl.desktop
fi
printf 'Configuration linked to %s. Session entry: %s/dwl.desktop\n' "$config" "$cache"
