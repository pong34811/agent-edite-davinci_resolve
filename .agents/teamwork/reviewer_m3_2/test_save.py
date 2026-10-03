import os
import sys

os.environ['RESOLVE_SCRIPT_LIB'] = r'C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll'
sys.path.append(r'C:\Program Files\Blackmagic Design\DaVinci Resolve\ResolvePython\lib\modules')

import DaVinciResolveScript as dvr

resolve = dvr.scriptapp('Resolve')
pm = resolve.GetProjectManager()
project = pm.GetCurrentProject()

saved = pm.SaveProject()
print(f"pm.SaveProject() returned: {saved}")
