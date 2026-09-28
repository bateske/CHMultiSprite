"""Build a variant, upload it, and capture the device's serial report.
usage: python bench.py <label> <seconds> [extra -D flags...] [--opt o2std] [--port COM8]

  python bench.py sweep 300 -DSWEEP_ON_BOOT=1     # full sweep, all four modes
  python bench.py batch 10                         # interactive build, 10 s of reports

Run from anywhere: it builds the sketch this file sits in unless
BENCH_SKETCH says otherwise. The capture stops early once the sweep's
summary table has been printed."""
import subprocess, sys, time, serial, os
label, secs = sys.argv[1], float(sys.argv[2])
args = sys.argv[3:]
opt, port = 'o2std', 'COM8'
if '--opt' in args:
    i = args.index('--opt'); opt = args[i+1]; del args[i:i+2]
if '--port' in args:
    i = args.index('--port'); port = args[i+1]; del args[i:i+2]
flags = ' '.join(args)
sketch = os.environ.get('BENCH_SKETCH', os.path.dirname(os.path.abspath(__file__)))
bp = os.path.join(os.environ.get('BENCH_BUILD', os.path.join(sketch, 'build_bench')), label)
fq = f'CHGame:ch32v:CHGame:opt={opt},rtlib=nano'
cmd = ['arduino-cli', 'compile', '-b', fq, '--build-path', bp]
if flags:   # an override, even an empty one, changes what the core links
    cmd += ['--build-property', f'compiler.cpp.extra_flags={flags}',
            '--build-property', f'compiler.c.extra_flags={flags}']
cmd += [sketch]
r = subprocess.run(cmd, capture_output=True, text=True)
size = [l for l in r.stdout.splitlines() if 'Sketch uses' in l or 'Global' in l]
if r.returncode: print(r.stdout[-3000:], r.stderr[-3000:]); sys.exit(1)
print(f'== {label}  opt={opt}  flags={flags or "(none)"}'); [print('  ' + l) for l in size]
r = subprocess.run(['arduino-cli', 'upload', '-b', 'CHGame:ch32v:CHGame', '-p', port,
                    '--input-dir', bp, sketch], capture_output=True, text=True)
if 'application is up' not in r.stdout: print(r.stdout[-2000:], r.stderr[-2000:]); sys.exit(1)
t = time.time(); s = None
while time.time() - t < 8:
    try: s = serial.Serial(port, 115200, timeout=0.2); break
    except Exception: time.sleep(0.05)
if s is None: print(f'could not open {port}'); sys.exit(1)
s.dtr = True; buf = b''; t = time.time()
while time.time() - t < secs:
    chunk = s.read(4096)
    if chunk:
        sys.stdout.write(chunk.decode(errors='replace')); sys.stdout.flush()
        buf += chunk
    k = buf.find(b'most walkers held')
    if k >= 0 and buf.count(b'\n', k) >= 5:     # header + one line per mode
        break
s.close()
