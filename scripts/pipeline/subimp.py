import os,sys,re,json
exec(open(os.path.join(os.environ["TMPDIR"],"rlib.py"),encoding="utf-8").read())
D=1.2
def ts(s):
    h,m,r_=s.split(':');sec,ms=r_.split(',');return int(h)*3600+int(m)*60+int(sec)+int(ms)/1000
def cues(path):
    raw=open(path,encoding='utf-8-sig').read();out=[]
    for b in re.split(r'\r?\n\r?\n',raw.strip()):
        L=b.splitlines()
        if len(L)>=3:
            a,e=[ts(x.strip()) for x in L[1].split('-->')];out.append((a,e,''.join(L[2:])))
    return out
nums=[int(x) for x in sys.argv[1:]]
resf=os.path.join(W,"subimp_result.json")
res=json.load(open(resf)) if os.path.exists(resf) else {}
for n in nums:
    path=os.path.join(W,"asr",f"T{n}.srt").replace("/","\\")
    t=p.GetTimelineByIndex(n)
    activate(t)
    fps=float(t.GetSetting("timelineFrameRate")); st=t.GetStartFrame()
    if t.GetTrackCount("subtitle")>0:
        if any((t.GetItemListInTrack("subtitle",k) or []) for k in range(1,t.GetTrackCount("subtitle")+1)): print(n,"has cues, skip"); continue
        for k in range(t.GetTrackCount("subtitle"),0,-1): print(n,"del empty track",t.DeleteTrack("subtitle",k)); time.sleep(D)
    f=bin_folder(); mp.SetCurrentFolder(f); time.sleep(D)
    stale=[c for c in (f.GetClipList() or []) if c.GetClipProperty("File Path")==path or (c.GetClipProperty("Type")=="Subtitle" and c.GetClipProperty("File Name")==f"T{n}.srt")]
    if stale: mp.DeleteClips(stale); time.sleep(D)
    items=mp.ImportMedia([path]); time.sleep(D)
    print(n,"import",bool(items))
    print(n,"addtrack",t.AddTrack("subtitle")); time.sleep(D)
    print(n,"append",bool(mp.AppendToTimeline([{"mediaPoolItem":items[0]}]))); time.sleep(D)
    print("save",pm.SaveProject()); time.sleep(D)
    got=t.GetItemListInTrack("subtitle",1) or []
    exp=cues(path)
    txt_ok=sum(1 for g,e in zip(got,exp) if g.GetName()==e[2])
    drift=[abs((g.GetStart()-st)/fps-e[0]) for g,e in zip(got,exp)]
    res[str(n)]=dict(expected=len(exp),got=len(got),text_match=txt_ok,max_drift_s=max(drift) if drift else None,tl_len=t.GetEndFrame()-st)
    print(n,res[str(n)],flush=True)
    json.dump(res,open(resf,"w"),indent=1)
