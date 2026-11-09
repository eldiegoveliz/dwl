#!/usr/bin/env python3
"""Exercise the toggle with a fake bluetoothctl; never touch the real adapter."""
import json
import os
from pathlib import Path
import subprocess
import tempfile

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/dwl-bluetooth'
FAKE = '''#!/usr/bin/env python3
import json, os, sys
from pathlib import Path
p = Path(os.environ['BT_STATE'])
s = json.loads(p.read_text())
a = sys.argv[1:]
s['calls'].append(a)
code = 0
if a == ['show']:
    print('Powered: ' + ('yes' if s['powered'] else 'no'))
elif a[:1] == ['power']:
    code = int(s.get('power_failure', False))
    if not code:
        s['powered'] = a[1] == 'on'
elif 'scan' in a:
    if s.get('off_during_scan'):
        s['powered'] = False
elif a == ['devices', 'Paired']:
    print('Device AA:AA:AA:AA:AA:AA Earbuds')
    print('Device BB:BB:BB:BB:BB:BB Speaker')
    print('Device CC:CC:CC:CC:CC:CC Phone')
elif a[:1] == ['info']:
    print('Connected: ' + ('yes' if a[1].startswith('BB') else 'no'))
elif 'connect' in a:
    code = int(a[-1].startswith('AA'))
else:
    raise RuntimeError(a)
p.write_text(json.dumps(s))
sys.exit(code)
'''

with tempfile.TemporaryDirectory() as directory:
    root = Path(directory)
    fake = root / 'bluetoothctl'
    fake.write_text(FAKE)
    fake.chmod(0o755)
    state = root / 'state.json'
    env = dict(os.environ, PATH=f'{root}:{os.environ["PATH"]}', BT_STATE=str(state))
    for scenario in [dict(powered=True), dict(powered=False),
                     dict(powered=False, off_during_scan=True),
                     dict(powered=False, power_failure=True)]:
        state.write_text(json.dumps(dict(scenario, calls=[])))
        result = subprocess.run([str(SCRIPT)], env=env, capture_output=True, text=True)
        calls = json.loads(state.read_text())['calls']
        if scenario['powered']:
            assert calls == [['show'], ['power', 'off']], calls
        elif scenario.get('power_failure'):
            assert result.returncode != 0
            assert calls == [['show'], ['power', 'on']], calls
        elif scenario.get('off_during_scan'):
            assert not any('connect' in call for call in calls), calls
            assert calls.count(['power', 'on']) == 1, calls
        else:
            assert ['--timeout', '8', 'scan', 'on'] in calls, calls
            connects = [call for call in calls if 'connect' in call]
            assert connects == [
                ['--timeout', '5', 'connect', 'AA:AA:AA:AA:AA:AA'],
                ['--timeout', '5', 'connect', 'CC:CC:CC:CC:CC:CC'],
            ], calls
        if not scenario.get('power_failure'):
            assert result.returncode == 0, result.stderr
print('PASS: off only powers off; on scans and reconnects; connected devices skipped;')
print('unavailable devices do not block others; power failures and off during scan handled.')
