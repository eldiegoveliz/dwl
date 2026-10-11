#!/usr/bin/env python3
"""Run dwl, a terminal, clipboard, and screenshot on an isolated Wayland display."""
import argparse
import json
import os
import pathlib
import signal
import struct
import subprocess
import tempfile
import time

ROOT = pathlib.Path(__file__).resolve().parents[1]


def run(binary):
    subprocess.run(["foot", "--check-config", "--config", str(ROOT / "foot.ini")], check=True)
    artifact = pathlib.Path(tempfile.mkdtemp(prefix="dwl-smoke-"))
    runtime = artifact / "runtime"
    runtime.mkdir(mode=0o700)
    env = os.environ.copy()
    for key in ("DISPLAY", "XAUTHORITY", "WAYLAND_DISPLAY", "WAYLAND_SOCKET"):
        env.pop(key, None)
    env.update(XDG_RUNTIME_DIR=str(runtime), WLR_BACKENDS="headless",
               WLR_HEADLESS_OUTPUTS="1", WLR_RENDERER="pixman")
    clients = []
    server = None
    with (artifact / "runtime.log").open("wb") as log:
        try:
            server = subprocess.Popen([str(binary)], env=env, stdin=subprocess.PIPE,
                                      stdout=log, stderr=log, start_new_session=True)
            deadline = time.monotonic() + 10
            sockets = []
            while time.monotonic() < deadline:
                sockets = [path for path in runtime.glob("wayland-*") if not path.name.endswith(".lock")]
                if sockets or server.poll() is not None:
                    break
                time.sleep(0.1)
            if not sockets or server.poll() is not None:
                raise RuntimeError("Compositor did not start")
            env["WAYLAND_DISPLAY"] = sockets[0].name
            server.stdin.write(b"DWL NATIVE WAYLAND CHECK\n")
            server.stdin.flush()
            outputs = json.loads(subprocess.check_output(["wlr-randr", "--json"], env=env, timeout=5))
            assert any(output["enabled"] for output in outputs), "No enabled output"

            terminal = subprocess.Popen([
                "foot", "--config", str(ROOT / "foot.ini"),
                "--app-id", "dwl-port-check", "--title", "dwl native Wayland check",
                "sh", "-c", "printf 'dwl 0.9 native Wayland\\n\\nTerminal, bar, and gaps are running.\\n'; exec sleep 30",
            ], env=env, stdout=log, stderr=log, start_new_session=True)
            clients.append(terminal)
            time.sleep(1)
            assert terminal.poll() is None, "Native terminal failed"

            clipboard = subprocess.Popen(["wl-copy", "--foreground", "dwl-native-clipboard"],
                                         env=env, stdout=log, stderr=log, start_new_session=True)
            clients.append(clipboard)
            time.sleep(0.2)
            pasted = subprocess.check_output(["wl-paste", "--no-newline"], env=env, timeout=5)
            assert pasted == b"dwl-native-clipboard", "Clipboard round trip failed"
            screenshot = artifact / "screen.png"
            subprocess.run(["grim", str(screenshot)], env=env, check=True, timeout=5)
            data = screenshot.read_bytes()
            assert data[:8] == b"\x89PNG\r\n\x1a\n", "Screenshot is not a PNG"
            width, height = struct.unpack(">II", data[16:24])
            assert width > 100 and height > 100 and len(data) > 2000, "Screenshot is empty"
            assert server.poll() is None, "Compositor exited during the check"
            server.terminate()
            assert server.wait(timeout=5) == 0, "Compositor did not shut down cleanly"
            print("PASS: headless Wayland compositor, native foot, clipboard round trip, screenshot, clean shutdown.")
            print(f"Screenshot: {screenshot}")
        except Exception:
            log.flush()
            print((artifact / "runtime.log").read_text(errors="replace"))
            raise
        finally:
            for process in clients + ([server] if server else []):
                try:
                    os.killpg(process.pid, signal.SIGTERM)
                except ProcessLookupError:
                    pass
                try:
                    process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid, signal.SIGKILL)
                    process.wait()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("binary", nargs="?", type=pathlib.Path, default=ROOT / "dwl")
    args = parser.parse_args()
    run(args.binary.resolve())
