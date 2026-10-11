pkgname=dwl-personal
pkgver=0.9
pkgrel=1
pkgdesc="Diego's dwm workflow on native Wayland"
arch=('x86_64' 'aarch64')
url='https://github.com/eldiegoveliz/dwl'
license=('GPL-3.0-or-later')
depends=('wlroots0.20' 'wayland' 'libinput' 'libxkbcommon' 'fcft' 'pixman'
         'foot' 'wmenu' 'swaybg' 'wlr-randr' 'grim' 'slurp' 'wl-clipboard'
         'jq' 'xdg-user-dirs')
makedepends=('wayland-protocols' 'pkgconf' 'tllist' 'python')
optdepends=('dunst: notifications' 'polkit-gnome: graphical authentication'
            'slstatus: extended status bar')
provides=('dwl=0.9')
conflicts=('dwl')
options=('!debug' '!strip')

prepare() {
    mkdir -p "$srcdir/dwl"
    cp "$startdir"/{Makefile,config.mk,config.h,client.h,ime.h,util.h,dwl.c,drwl.h,dwl.1,dwl.desktop,foot.ini} "$srcdir/dwl/"
    cp -r "$startdir"/protocols "$startdir"/scripts "$srcdir/dwl/"
}

build() {
    make -C "$srcdir/dwl" -j2 XWAYLAND= XLIBS= VERSION=0.9-diego
}

check() {
    make -C "$srcdir/dwl" check-bindings XWAYLAND= XLIBS= VERSION=0.9-diego
    python "$startdir/scripts/smoke-test.py" "$srcdir/dwl/dwl"
}

package() {
    make -C "$srcdir/dwl" DESTDIR="$pkgdir" PREFIX=/usr install
    install -Dm755 "$srcdir/dwl/scripts/dwl-session" "$pkgdir/usr/bin/dwl-session"
    install -Dm644 "$srcdir/dwl/foot.ini" "$pkgdir/usr/share/dwl/foot.ini"
    for script in dwl-autostart dwl-status-mode dwl-monitor-toggle dwl-screenshot; do
        install -Dm755 "$srcdir/dwl/scripts/$script" "$pkgdir/usr/share/dwl/scripts/$script"
    done
}
