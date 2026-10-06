"""Export an exact closed project from current library; no project load or edits.
MCP-GAP: live davinci-resolve tool catalog absent; ExportProject API probed.
"""
import json
from datetime import datetime
from pathlib import Path
from scripts.resolve_common import connect_resolve

TARGET = 'aomimama-2026-09-p1'
ART = Path(__file__).resolve().parents[1] / '.hermes/artifacts/enrichment-review-2026-10-06-live2'
r = connect_resolve()
if r is None:
    raise RuntimeError('Resolve unavailable')
pm = r.GetProjectManager()
if 'ExportProject' not in dir(pm):
    raise RuntimeError('ExportProject unavailable')
if TARGET not in pm.GetProjectListInCurrentFolder():
    raise RuntimeError('Target not in current project folder')
folder = ART / 'backups'
folder.mkdir(exist_ok=True)
dest = folder / (TARGET + '-pre-enrichment-' + datetime.now().strftime('%Y%m%d-%H%M%S') + '.drp')
if dest.exists():
    raise RuntimeError('Refusing overwrite')
print('EXPORT_START', str(dest), flush=True)
returned = pm.ExportProject(TARGET, str(dest), False)
if not returned or not dest.is_file() or dest.stat().st_size == 0:
    raise RuntimeError('DRP export failed or empty')
report = {'project': TARGET, 'backup': str(dest), 'bytes': dest.stat().st_size,
          'export_return': returned, 'route': 'native scripting ExportProject',
          'status': 'nonempty_native_export_verified_not_restore_tested',
          'no_timeline_edits': True}
(ART / 'fresh-backup.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(report, ensure_ascii=False), flush=True)
