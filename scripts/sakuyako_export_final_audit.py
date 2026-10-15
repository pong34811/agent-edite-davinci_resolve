"""MCP-GAP: filesystem baseline comparison requires Resolve Python plus local JSON."""
import json
from scripts.resolve_common import require_resolve,preserved_state
from scripts.sakuyako_export_preflight import OUT

def main():
    baseline=json.loads((OUT/'baseline.json').read_text(encoding='utf-8'))
    r=require_resolve()
    with preserved_state(r):
        pm=r.GetProjectManager(); p=pm.GetCurrentProject()
        assert p.GetName()=='sakuyako-2026-09' and not p.IsRenderingInProgress()
        tls={p.GetTimelineByIndex(i).GetUniqueId():p.GetTimelineByIndex(i) for i in range(1,(p.GetTimelineCount() or 0)+1)}
        report={'originals':[],'project':p.GetName(),'version':r.GetVersionString(),'playback_fps':p.GetSetting('timelinePlaybackFrameRate')}
        for b in baseline['timelines']:
            t=tls[b['id']]; assert p.SetCurrentTimeline(t)
            assert t.GetName()==b['name'] and (t.GetStartFrame(),t.GetEndFrame())==(b['start'],b['end'])
            states={}
            for kind,tracks in b['tracks'].items():
                assert t.GetTrackCount(kind)==len(tracks)
                states[kind]=[]
                for n,track in enumerate(tracks,1):
                    got=[]
                    for x in t.GetItemListInTrack(kind,n) or []:
                        m=x.GetMediaPoolItem()
                        got.append({'name':x.GetName(),'start':x.GetStart(),'end':x.GetEnd(),
                            'source':[x.GetSourceStartFrame(),x.GetSourceEndFrame()] if m else None,
                            'properties':x.GetProperty() if kind!='subtitle' else None})
                    for row,original in zip(got,track['items']):
                        if row['properties'] is not None:
                            row['properties']={k:row['properties'].get(k) for k in original['properties']}
                    assert got==track['items'],f'original changed: {b["name"]} {kind}{n}'
                    assert t.GetTrackName(kind,n)==track['name']
                    states[kind].append({'enabled':t.GetIsTrackEnabled(kind,n),'locked':t.GetIsTrackLocked(kind,n)})
            for key in ['timelineResolutionWidth','timelineResolutionHeight','timelineFrameRate']:
                assert t.GetSetting(key)==b['settings'][key]
            report['originals'].append({'name':t.GetName(),'id':t.GetUniqueId(),'unchanged':True,'track_states':states})
        report['temporary_timelines']=[t.GetName() for t in tls.values() if '__cover_tmp' in t.GetName()]
        report['jobs']=[{'info':j,'status':p.GetRenderJobStatus(j['JobId'])} for j in p.GetRenderJobList()]
        assert not report['temporary_timelines']
        assert pm.SaveProject()
        (OUT/'final-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=1),encoding='utf-8')
        print('ORIGINALS VERIFIED',len(report['originals']),'jobs',len(report['jobs']),flush=True)

if __name__=='__main__': main()
