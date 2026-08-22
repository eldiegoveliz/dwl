# Diego's dwl build

This repository tracks a personal pure-Wayland dwl build for Arch Linux. The
`main` branch is based on Codeberg's `wlroots-next` branch and builds against
the official `wlroots0.20` package.

## Local dependencies

In addition to upstream dwl's dependencies, the built-in bar requires `fcft`,
`pixman`, and `tllist`. The session scripts use `swaybg`, `wlr-randr`, `jq`,
`grim`, `slurp`, and `wl-clipboard`.

## Build and install

```sh
make clean
make
sudo make PREFIX=/usr install
```

The installed SDDM entry launches `scripts/dwl-session`, which feeds slstatus
to the built-in bar and starts the Wayland session services.

## Upstream updates

Fetch Codeberg separately from the personal GitHub remote:

```sh
git fetch upstream
git merge upstream/wlroots-next
```

Review bar and gaps conflicts carefully before rebuilding. Both patches touch
monitor geometry, input handling, and drawing code in `dwl.c`.
