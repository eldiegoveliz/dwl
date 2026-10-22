"""Exercise real GTK dialogs on two headless dwl outputs without touching the session."""
import json
import os
from pathlib import Path
import signal
import subprocess as sp
import sys
import tempfile
import time

from PIL import Image, ImageChops

binary = Path(sys.argv[1]).resolve()
cache = Path(os.environ.get('XDG_CACHE_HOME', Path.home() / '.cache')) / 'dwl-config-install/dialog-centering-check'
cache.mkdir(parents=True, exist_ok=True)
work = Path(tempfile.mkdtemp(prefix='run-', dir=cache))
runtime = work / 'runtime'
runtime.mkdir(mode=0o700)
env = dict(os.environ, XDG_RUNTIME_DIR=str(runtime), WAYLAND_DISPLAY='wayland-0',
           WLR_BACKENDS='headless', WLR_HEADLESS_OUTPUTS='2', WLR_RENDERER='gles2',
           WLR_RENDER_DRM_DEVICE='/dev/dri/renderD128', GDK_BACKEND='wayland')
env.pop('DISPLAY', None)
processes = []


def start(args, name):
    log = (work / (name + '.log')).open('w')
    proc = sp.Popen(args, env=env, stdout=log, stderr=sp.STDOUT, start_new_session=True)
    log.close()
    processes.append(proc)
    return proc


def run(*args):
    return sp.check_output(args, env=env, text=True, stderr=sp.STDOUT, timeout=10)


def wait(predicate):
    deadline = time.monotonic() + 12
    while time.monotonic() < deadline:
        if predicate():
            return
        if compositor.poll() is not None:
            raise AssertionError((work / 'compositor.log').read_text())
        time.sleep(.1)
    raise AssertionError(f'Timed out; logs: {work}')


def selected():
    values = {}
    for line in (work / 'compositor.log').read_text().splitlines():
        parts = line.split()
        if len(parts) == 3 and parts[1] == 'selmon':
            values[parts[0]] = parts[2]
    return next((name for name, value in values.items() if value == '1'), None)


def focus(output):
    if selected() != output:
        run('wtype', '-M', 'logo', '-k', 'comma' if output == 'HEADLESS-1' else 'period', '-m', 'logo')
    wait(lambda: selected() == output)


gtk_app = r'''
import gi, sys
from pathlib import Path
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib
work = Path(sys.argv[1])
parent = Gtk.Window(title='Centering parent')
parent.set_default_size(600, 400)
parent.show_all()
def open_dialog():
    if not (work / 'show').exists():
        return True
    dialog = Gtk.Dialog(title='Centering dialog', transient_for=parent)
    dialog.set_name('centering-dialog')
    dialog.set_decorated(False)
    dialog.set_resizable(False)
    dialog.set_default_size(320, 180)
    css = Gtk.CssProvider()
    css.load_from_data(b'#centering-dialog, #centering-dialog box { background-image: none; background-color: #f020a0; }')
    Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), css, 900)
    dialog.show_all()
    GLib.timeout_add(300, lambda: ((work / 'shown').touch(), False)[1])
    return False
GLib.timeout_add(300, lambda: ((work / 'ready').touch(), False)[1])
GLib.timeout_add(100, open_dialog)
Gtk.main()
'''

try:
    compositor = start([str(binary)], 'compositor')
    wait(lambda: (runtime / 'wayland-0').exists())
    run('wlr-randr', '--output', 'HEADLESS-1', '--custom-mode', '1366x768@60', '--pos', '0,0',
        '--output', 'HEADLESS-2', '--custom-mode', '1920x1080@60', '--pos', '1366,0')
    bar_config = work / 'bar.json'
    bar_config.write_text(json.dumps({'layer': 'top', 'position': 'top', 'height': 40,
        'modules-left': ['custom/check'], 'custom/check': {'format': 'Dialog placement check'}}))
    bar_style = work / 'bar.css'
    bar_style.write_text('* { min-height: 0; padding: 0; margin: 0; }')
    start(['waybar', '-c', str(bar_config), '-s', str(bar_style)], 'bar')
    time.sleep(1)
    for index, (output, width, height) in enumerate((('HEADLESS-1', 1366, 768), ('HEADLESS-2', 1920, 1080))):
        case = work / output
        case.mkdir()
        # Select the parent's output, then move focus to the other output before opening its dialog.
        focus(output)
        app = start([sys.executable, '-c', gtk_app, str(case)], output)
        wait(lambda: (case / 'ready').exists())
        focus('HEADLESS-2' if index == 0 else 'HEADLESS-1')
        (case / 'show').touch()
        wait(lambda: (case / 'shown').exists())
        time.sleep(.3)
        screenshot = case / 'dialog.png'
        run('grim', '-o', output, str(screenshot))
        im = Image.open(screenshot).convert('RGB')
        # Only the dialog is magenta; find its real rendered bounds.
        channels = ImageChops.difference(im, Image.new('RGB', im.size, (240, 32, 160))).split()
        mask = ImageChops.lighter(ImageChops.lighter(channels[0], channels[1]), channels[2]).point(lambda v: 255 if v < 3 else 0)
        bounds = mask.getbbox()
        assert bounds, f'Dialog absent from parent output {output}; logs: {work}'
        x, y, right, bottom = bounds
        center = ((x + right) / 2, (y + bottom) / 2)
        expected = (width / 2, 40 + (height - 40) / 2)
        assert abs(center[0] - expected[0]) <= 1 and abs(center[1] - expected[1]) <= 1, (output, bounds, center, expected, str(work))
        print(f'{output}: dialog center {center}, expected {expected}; parent monitor retained despite focus change', flush=True)
        app.terminate()
        app.wait(timeout=5)
    print(f'PASS; screenshots and logs: {work}')
finally:
    for proc in reversed(processes):
        if proc.poll() is None:
            os.killpg(proc.pid, signal.SIGTERM)
            try:
                proc.wait(timeout=5)
            except sp.TimeoutExpired:
                os.killpg(proc.pid, signal.SIGKILL)
