"""Resume only manifest-owned Ready jobs after an interrupted preparation loop.

MCP-GAP: local manifest validation and output QC require Resolve Python.
"""
import json
import time
from scripts.resolve_common import require_resolve,preserved_state
from scripts.sakuyako_export_preflight import OUT,VDO
from scripts import p2_export_final as exporter

def main():
    exporter.OUT=OUT; exporter.VDO=str(VDO)
    manifest=OUT/'jobs.json'; jobs=json.loads(manifest.read_text(encoding='utf-8'))
    baseline={t['name']:t for t in json.loads((OUT/'baseline.json').read_text(encoding='utf-8'))['timelines']}
    r=require_resolve()
    with preserved_state(r):
        pm=r.GetProjectManager(); p=pm.GetCurrentProject(); mp=p.GetMediaPool()
        assert p.GetName()=='sakuyako-2026-09' and not p.IsRenderingInProgress()
        live={j['JobId']:j for j in p.GetRenderJobList()}
        ready=[]
        for j in jobs:
            if j.get('status')=='Complete':
                assert not exporter.verify_one(j,str(VDO)); continue
            assert j['job'] in live
            info=live[j['job']]
            assert info['TimelineName']==j.get('tmp',j['timeline'])
            assert p.GetRenderJobStatus(j['job'])['JobStatus']=='Ready'
            assert not exporter._output_matches(j['out_name'])
            t=exporter._find_timeline(p,j.get('tmp',j['timeline'])); assert t
            assert p.SetCurrentTimeline(t)
            b=baseline[j['timeline']]; offset=30 if j['vertical'] else 0
            assert t.GetEndFrame()==b['end']+offset
            for kind,tracks in b['tracks'].items():
                for n,tr in enumerate(tracks,1):
                    rows=[]
                    for x in t.GetItemListInTrack(kind,n) or []:
                        m=x.GetMediaPoolItem()
                        rows.append({'name':x.GetName(),'start':x.GetStart()-offset,'end':x.GetEnd()-offset,
                            'source':[x.GetSourceStartFrame(),x.GetSourceEndFrame()] if m else None,
                            'properties':x.GetProperty() if kind!='subtitle' else None})
                    for row, original in zip(rows,tr['items']):
                        if row['properties'] is not None:
                            row['properties']={k:row['properties'].get(k) for k in original['properties']}
                    assert rows==tr['items'],f'ready content changed {j["out_name"]} {kind}{n}'
            if j['vertical']:
                cover=t.GetItemListInTrack('video',t.GetTrackCount('video'))
                assert len(cover)==1 and cover[0].GetStart()==b['start'] and cover[0].GetEnd()==b['start']+30
                assert cover[0].GetName()==j['out_name']+'.jpg'
            ready.append(j)
        print('VERIFIED READY',len(ready),flush=True)
        assert pm.SaveProject()
        assert p.StartRendering([j['job'] for j in ready])
        pending={j['job']:j for j in ready}
        while pending:
            time.sleep(6)
            for jid in list(pending):
                st=p.GetRenderJobStatus(jid) or {}; status=st.get('JobStatus')
                if status in ('Complete','Failed','Cancelled'):
                    j=pending.pop(jid); j['status']=status; j['render_status']=st
                    with (OUT/'done.jsonl').open('a',encoding='utf-8') as fh: fh.write(json.dumps(j,ensure_ascii=False)+'\n')
                    manifest.write_text(json.dumps(jobs,ensure_ascii=False,indent=1),encoding='utf-8')
                    print('DONE',j['out_name'],status,st.get('Error',''),flush=True)
        for j in ready:
            errs=exporter.verify_one(j,str(VDO)) if j['status']=='Complete' else [j['render_status']]
            j['qc_errors']=errs
            if j.get('tmp') and not errs:
                t=exporter._find_timeline(p,j['tmp'])
                if t:
                    assert mp.DeleteTimelines([t]); time.sleep(1.3)
            print('FILE QC',j['out_name'],errs,flush=True)
        assert pm.SaveProject()
        manifest.write_text(json.dumps(jobs,ensure_ascii=False,indent=1),encoding='utf-8')
        assert all(j['status']=='Complete' and not j['qc_errors'] for j in ready)
        print('RESUMED COMPLETE',len(ready),flush=True)

if __name__=='__main__': main()
