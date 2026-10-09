"""Apply one lower-left VTuber focus pilot on a recovered Resolve copy."""
from pathlib import Path
import argparse, json, time, zipfile
from scripts.resolve_common import connect_resolve
PROJECT = 'aomimama-2026-09-p1-recovered-20261007'
ZOOM = 1.5
CENTER = {1: 0.25, 2: 0.47, 3: 0.0}
EDGES = 0
TASKS = [{'n': 9, 'name': 'คุยกับแชทช่วงต้นไลฟ์ เล่าว่าเล่นเกมนี้มาหล-alien shooter-vdo', 'start': 2820, 'end': 3072, 'subtitle': 'ซึ่งนั่นแหละนะเดี๋ยววันนี้มาเล่นกันถือว่าเป็น'}]
OUT = Path('.hermes/artifacts/vtuber-focus-review-2026-10-07').resolve()

def tc(f):
    s, n = divmod(f, 60)
    h, s = divmod(s, 3600)
    m, sec = divmod(s, 60)
    return f'{h:02d}:{m:02d}:{sec:02d}:{n:02d}'

def snap(t):
    return [(k, i, t.GetTrackName(k, i), [(x.GetUniqueId(), x.GetName(), x.GetStart(), x.GetEnd(), x.GetType(), x.GetProperty()) for x in t.GetItemListInTrack(k, i) or []]) for k in ('video', 'audio', 'subtitle') for i in range(1, t.GetTrackCount(k) + 1)]

def add_transform(item):
    c = item.AddFusionComp()
    assert c
    mi = mo = None
    for x in c.GetToolList().values():
        a = x.GetAttrs()
        rid = str(a.get('TOOLS_RegID', ''))
        nm = str(a.get('TOOLS_Name', ''))
        if rid == 'MediaIn' or nm.startswith('MediaIn'):
            mi = x
        elif rid == 'MediaOut' or nm.startswith('MediaOut'):
            mo = x
    assert mi and mo
    tr = c.AddTool('Transform', -32768, -32768)
    assert tr and tr.ConnectInput('Input', mi) and mo.ConnectInput('Input', tr)
    tr.SetInput('Size', float(ZOOM))
    tr.SetInput('Center', CENTER)
    tr.SetInput('Edges', EDGES)
    assert float(tr.GetInput('Size')) == ZOOM and tr.GetInput('Center') == CENTER and (int(float(tr.GetInput('Edges'))) == EDGES)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--backup', type=Path, required=True)
    a = ap.parse_args()
    b = a.backup.resolve()
    assert b.is_file() and zipfile.ZipFile(b).testzip() is None
    r = connect_resolve()
    assert r
    pm = r.GetProjectManager()
    entry = pm.GetCurrentProject()
    en = entry.GetName()
    et = entry.GetCurrentTimeline().GetName()
    ec = entry.GetCurrentTimeline().GetCurrentTimecode()
    page = r.GetCurrentPage()
    p = entry if en == PROJECT else pm.LoadProject(PROJECT)
    assert p and p.GetName() == PROJECT
    records = []
    try:
        for task in TASKS:
            t = next((p.GetTimelineByIndex(i) for i in range(1, p.GetTimelineCount() + 1) if p.GetTimelineByIndex(i).GetName() == task['name']))
            p.SetCurrentTimeline(t)
            time.sleep(1.2)
            assert p.GetCurrentTimeline().GetName() == task['name']
            s, e = (task['start'], task['end'])
            subs = [x for x in t.GetItemListInTrack('subtitle', 1) or [] if x.GetStart() < e and x.GetEnd() > s]
            assert subs and any((task['subtitle'] in x.GetName() for x in subs))
            track = f"VTUBER_FOCUS_T{task['n']:02d}"
            assert not any((t.GetTrackName('video', i) == track for i in range(1, t.GetTrackCount('video') + 1)))
            before = snap(t)
            vcount = t.GetTrackCount('video')
            locks = {(k, i): t.GetIsTrackLocked(k, i) for k in ('video', 'audio', 'subtitle') for i in range(1, t.GetTrackCount(k) + 1)}
            try:
                for (k, i), state in locks.items():
                    if not state:
                        t.SetTrackLock(k, i, True)
                time.sleep(1.25)
                t.AddTrack('video')
                time.sleep(1.25)
                idx = t.GetTrackCount('video')
                assert idx == vcount + 1
                t.SetTrackName('video', idx, track)
                t.SetTrackLock('video', idx, False)
                time.sleep(1.25)
                t.SetMarkInOut(s, e - 1)
                t.SetCurrentTimecode(tc(s))
                time.sleep(1.25)
                assert t.GetCurrentTimecode() == tc(s)
                assert t.InsertGeneratorIntoTimeline('Adjustment Clip')
                time.sleep(1.25)
                t.ClearMarkInOut()
                clips = [x for x in t.GetItemListInTrack('video', idx) or [] if x.GetType() == 'generator' and x.GetStart() == s and (x.GetEnd() == e)]
                assert len(clips) == 1
                add_transform(clips[0])
                after = snap(t)
                for row in before:
                    assert next((x for x in after if x[0] == row[0] and x[1] == row[1]), None) == row, ('protected changed', row[:3])
                assert pm.SaveProject()
                rec = {'timeline': task['name'], 'ordinal': task['n'], 'cue': [s, e], 'subtitle': task['subtitle'], 'track': idx, 'track_name': track, 'adjustment_id': clips[0].GetUniqueId(), 'transform': {'size': ZOOM, 'center': CENTER, 'edges': EDGES}, 'protected_tracks_verified': True, 'saved': True, 'backup': str(b)}
                (OUT / f"T{task['n']:02d}-pilot.json").write_text(json.dumps(rec, ensure_ascii=False, indent=2), encoding='utf-8')
                records.append(rec)
                print('APPLIED', task['n'], flush=True)
            finally:
                t.ClearMarkInOut()
                for (k, i), state in locks.items():
                    t.SetTrackLock(k, i, state)
    finally:
        p0 = pm.LoadProject(en)
        assert p0
        t0 = next((p0.GetTimelineByIndex(i) for i in range(1, p0.GetTimelineCount() + 1) if p0.GetTimelineByIndex(i).GetName() == et))
        p0.SetCurrentTimeline(t0)
        time.sleep(1)
        t0.SetCurrentTimecode(ec)
        time.sleep(0.5)
        if r.GetCurrentPage() != page:
            r.OpenPage(page)
            time.sleep(0.5)
        ok = pm.GetCurrentProject().GetName() == en and pm.GetCurrentProject().GetCurrentTimeline().GetName() == et and (pm.GetCurrentProject().GetCurrentTimeline().GetCurrentTimecode() == ec) and (r.GetCurrentPage() == page)
        print('RESTORATION_VERIFIED', ok, flush=True)
        assert ok
    print(json.dumps(records, ensure_ascii=False, indent=2))
if __name__ == '__main__':
    main()
