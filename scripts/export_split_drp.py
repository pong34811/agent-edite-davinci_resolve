"""Export every tygarina_2026-09-30_<group> project to .drp and verify the files exist."""
import os, sys
sys.stdout.reconfigure(encoding='utf-8')
os.environ['RESOLVE_SCRIPT_LIB'] = r'C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll'
sys.path.append(r'C:\Program Files\Blackmagic Design\DaVinci Resolve\ResolvePython\lib\modules')
import DaVinciResolveScript as dvr

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'exports', 'split_projects')
os.makedirs(OUT, exist_ok=True)
pm = dvr.scriptapp('Resolve').GetProjectManager()
names = [n for n in pm.GetProjectListInCurrentFolder() if n.startswith('tygarina_2026-09-30_')]
bad = 0
for n in sorted(names):
    path = os.path.join(OUT, n + '.drp')
    ok = pm.ExportProject(n, path, True)
    size = os.path.getsize(path) if os.path.exists(path) else 0
    print('OK ' if ok and size else 'BAD', n, size)
    bad += not (ok and size)
print('exported', len(names), 'bad', bad, '->', OUT)
sys.exit(1 if bad else 0)
