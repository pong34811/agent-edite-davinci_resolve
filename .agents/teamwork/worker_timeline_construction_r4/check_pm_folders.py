import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

os.environ['RESOLVE_SCRIPT_LIB'] = r'C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll'
sys.path.append(r'C:\Program Files\Blackmagic Design\DaVinci Resolve\ResolvePython\lib\modules')

import DaVinciResolveScript as dvr

resolve = dvr.scriptapp('Resolve')
pm = resolve.GetProjectManager()

print("Current Folder:", pm.GetCurrentFolder())
print("Projects in current folder:", pm.GetProjectListInCurrentFolder())
print("Folders in current folder:", pm.GetFolderListInCurrentFolder())

# Try opening folder Tygarina
if "Tygarina" in (pm.GetFolderListInCurrentFolder() or []):
    print("Opening folder Tygarina...")
    pm.OpenFolder("Tygarina")
    print("Now current folder:", pm.GetCurrentFolder())
    print("Projects in Tygarina folder:", pm.GetProjectListInCurrentFolder())
    proj = pm.LoadProject("tygarina_2026-09-30")
    print("Loaded project:", proj.GetName() if proj else "FAILED")
    if proj:
        print("Timeline count:", proj.GetTimelineCount())
