"""QC pilot for one candidate timeline; only creates a new Adjustment Clip."""
import argparse,json,time,zipfile
from pathlib import Path
from scripts.resolve_common import connect_resolve
PROJECT='aomimama-2026-09-p1-recovered-20261007'
NAME='เสียงร้องโอ๊ยๆ-League of Legends-vdo'
START,END=2350,2430; SUB='teacher to student.'; TRACK='VTUBER_FOCUS_T30'
ZOOM=2.6; CENTER={1:1.3,2:.924,3:0.0}; EDGES=0
OUT=Path('.hermes/artifacts/vtuber-focus-review-2026-10-07').resolve()
def tc(f):
 s,n=divmod(f,60); h,s=divmod(s,3600); m,sec=divmod(s,60); return f'{h:02d}:{m:02d}:{sec:02d}:{n:02d}'
def snap(t):
 return [(k,i,t.GetTrackName(k,i),[(x.GetUniqueId(),x.GetName(),x.GetStart(),x.GetEnd(),x.GetType(),x.GetProperty()) for x in (t.GetItemListInTrack(k,i) or [])]) for k in ('video','audio','subtitle') for i in range(1,t.GetTrackCount(k)+1)]
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--backup',type=Path,required=True); a=ap.parse_args(); b=a.backup.resolve(); assert b.is_file() and zipfile.ZipFile(b).testzip() is None
 r=connect_resolve(); assert r; pm=r.GetProjectManager(); entry=pm.GetCurrentProject(); en=entry.GetName(); et=entry.GetCurrentTimeline().GetName(); ec=entry.GetCurrentTimeline().GetCurrentTimecode(); page=r.GetCurrentPage()
 p=entry if en==PROJECT else pm.LoadProject(PROJECT); assert p and p.GetName()==PROJECT
 t=next(p.GetTimelineByIndex(i) for i in range(1,p.GetTimelineCount()+1) if p.GetTimelineByIndex(i).GetName()==NAME); p.SetCurrentTimeline(t); time.sleep(1.2); assert p.GetCurrentTimeline().GetName()==NAME
 subs=[x for x in (t.GetItemListInTrack('subtitle',1) or []) if x.GetStart()<END and x.GetEnd()>START]; assert any(SUB in x.GetName() for x in subs)
 assert not any(t.GetTrackName('video',i)==TRACK for i in range(1,t.GetTrackCount('video')+1))
 before=snap(t); vcount=t.GetTrackCount('video'); locks={(k,i):t.GetIsTrackLocked(k,i) for k in ('video','audio','subtitle') for i in range(1,t.GetTrackCount(k)+1)}
 try:
  for (k,i),locked in locks.items():
   if not locked:t.SetTrackLock(k,i,True)
  time.sleep(1.25); t.AddTrack('video'); time.sleep(1.25); idx=t.GetTrackCount('video'); assert idx==vcount+1
  t.SetTrackName('video',idx,TRACK); t.SetTrackLock('video',idx,False); time.sleep(1.25); t.SetMarkInOut(START,END-1); t.SetCurrentTimecode(tc(START)); time.sleep(1.25); assert t.GetCurrentTimecode()==tc(START)
  assert t.InsertGeneratorIntoTimeline('Adjustment Clip'); time.sleep(1.25); t.ClearMarkInOut()
  clips=[x for x in (t.GetItemListInTrack('video',idx) or []) if x.GetType()=='generator' and x.GetStart()==START and x.GetEnd()==END]; assert len(clips)==1
  c=clips[0].AddFusionComp(); assert c; mi=mo=None
  for x in c.GetToolList().values():
   a=x.GetAttrs(); rid=str(a.get('TOOLS_RegID','')); nm=str(a.get('TOOLS_Name',''))
   if rid=='MediaIn' or nm.startswith('MediaIn'):mi=x
   elif rid=='MediaOut' or nm.startswith('MediaOut'):mo=x
  assert mi and mo; tr=c.AddTool('Transform',-32768,-32768); assert tr and tr.ConnectInput('Input',mi) and mo.ConnectInput('Input',tr)
  tr.SetInput('Size',float(ZOOM)); tr.SetInput('Center',CENTER); tr.SetInput('Edges',EDGES)
  assert float(tr.GetInput('Size'))==ZOOM and tr.GetInput('Center')==CENTER and int(float(tr.GetInput('Edges')))==EDGES
  after=snap(t)
  for row in before: assert next((x for x in after if x[0]==row[0] and x[1]==row[1]),None)==row,('protected changed',row[:3])
  assert pm.SaveProject(); record={'timeline':NAME,'cue':[START,END],'subtitle':SUB,'track':idx,'track_name':TRACK,'adjustment_id':clips[0].GetUniqueId(),'transform':{'size':ZOOM,'center':CENTER,'edges':EDGES},'protected_tracks_verified':True,'saved':True,'backup':str(b)}
  (OUT/'T30-zoom26-pilot.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8'); print(json.dumps(record,ensure_ascii=False),flush=True)
 finally:
  t.ClearMarkInOut()
  for (k,i),locked in locks.items():t.SetTrackLock(k,i,locked)
  p0=pm.LoadProject(en); assert p0; t0=next(p0.GetTimelineByIndex(i) for i in range(1,p0.GetTimelineCount()+1) if p0.GetTimelineByIndex(i).GetName()==et); p0.SetCurrentTimeline(t0); time.sleep(1); t0.SetCurrentTimecode(ec); time.sleep(.5)
  if r.GetCurrentPage()!=page:r.OpenPage(page);time.sleep(.5)
  ok=pm.GetCurrentProject().GetName()==en and pm.GetCurrentProject().GetCurrentTimeline().GetName()==et and pm.GetCurrentProject().GetCurrentTimeline().GetCurrentTimecode()==ec and r.GetCurrentPage()==page; print('RESTORATION_VERIFIED',ok,flush=True); assert ok
if __name__=='__main__':main()
