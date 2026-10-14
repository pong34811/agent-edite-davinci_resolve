"""MCP-GAP: community MCP unavailable; Studio has no filesystem audit. Resolve Python preflight."""
import json
from pathlib import Path
from scripts.resolve_common import require_resolve, preserved_state
from scripts.backup_drp import export_verified

OUT = Path('exports/final-export/sakuyako-2026-09').resolve()
VDO = Path(r'I:\.shortcut-targets-by-id\1EfyfEGeG4UTUmNzTR2IDLUPjm386Fqlu\Projects\Sakuyako-Cheris\sakuyako-2026-09\vdo')

def main():
    r = require_resolve()
    with preserved_state(r):
        pm = r.GetProjectManager(); p = pm.GetCurrentProject()
        assert p.GetName() == 'sakuyako-2026-09' and not p.IsRenderingInProgress()
        OUT.mkdir(parents=True, exist_ok=True)
        data = {'version':r.GetVersionString(), 'settings':p.GetSetting(), 'timelines':[], 'media':{}}
        for i in range(1, (p.GetTimelineCount() or 0)+1):
            t = p.GetTimelineByIndex(i)
            assert p.SetCurrentTimeline(t)
            entry = {'name':t.GetName(), 'id':t.GetUniqueId(), 'start':t.GetStartFrame(), 'end':t.GetEndFrame(),
                     'settings':t.GetSetting(), 'tracks':{}}
            assert (VDO/(t.GetName()+'.jpg')).is_file()
            for typ in ['video','audio','subtitle']:
                entry['tracks'][typ] = []
                for n in range(1,t.GetTrackCount(typ)+1):
                    items=[]
                    for x in t.GetItemListInTrack(typ,n) or []:
                        m=x.GetMediaPoolItem()
                        items.append({'name':x.GetName(),'start':x.GetStart(),'end':x.GetEnd(),
                                      'source':[x.GetSourceStartFrame(),x.GetSourceEndFrame()] if m else None,
                                      'properties':x.GetProperty() if typ!='subtitle' else None})
                        if m and m.GetUniqueId() not in data['media']:
                            props=m.GetClipProperty(); path=props.get('File Path','')
                            data['media'][m.GetUniqueId()]={'name':m.GetName(),'properties':props,
                                'exists':Path(path).is_file() if path else None}
                    entry['tracks'][typ].append({'name':t.GetTrackName(typ,n),'enabled':t.GetIsTrackEnabled(typ,n),'locked':t.GetIsTrackLocked(typ,n),'items':items})
            data['timelines'].append(entry)
        bad=[v for v in data['media'].values() if v['exists'] is False]
        (OUT/'baseline.json').write_text(json.dumps(data,ensure_ascii=False,indent=1),encoding='utf-8')
        print('timelines',len(data['timelines']),'media',len(data['media']),'missing',bad,flush=True)
        assert not bad
        backup=Path('backups/sakuyako-2026-09_before-export-20261013.drp').resolve()
        print('BACKUP',str(backup),export_verified(pm,p,backup),flush=True)
        t=p.GetTimelineByIndex(36)
        assert t.Export(str(OUT/'pilot-source.drt'),r.EXPORT_DRT,r.EXPORT_NONE)
        print('DRT exported',flush=True)

if __name__=='__main__': main()
