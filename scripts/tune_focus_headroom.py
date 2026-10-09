"""Tune headroom only on four Adjustment Clips after burn-in QC."""
import argparse, json, time, zipfile
from pathlib import Path
from scripts.resolve_common import connect_resolve
PROJECT = 'aomimama-2026-09-p1-recovered-20261007'
TASKS = [(44, 'ทีมไฟต์ถูกชัตดาวน์-League of Legends-vdo', 1771, 1953, 3), (46, 'หัวยังไม่ฟู ตายก่อนเลย-League of Legends-vdo', 4029, 4135, 3), (47, 'ออกเมื่อไหร่มีตายเมื่อนั้น-League of Legends-vdo', 1699, 1760, 3)]
CENTER = {1: 1.15, 2: 0.9, 3: 0.0}

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
    results = []
    try:
        for n, name, start, end, track in TASKS:
            t = next((p.GetTimelineByIndex(i) for i in range(1, p.GetTimelineCount() + 1) if p.GetTimelineByIndex(i).GetName() == name))
            p.SetCurrentTimeline(t)
            time.sleep(1.0)
            clips = [x for x in t.GetItemListInTrack('video', track) or [] if x.GetType() == 'generator' and x.GetStart() == start and (x.GetEnd() == end)]
            assert len(clips) == 1
            locks = {(k, i): t.GetIsTrackLocked(k, i) for k in ('video', 'audio', 'subtitle') for i in range(1, t.GetTrackCount(k) + 1)}
            try:
                for (k, i), state in locks.items():
                    if not state:
                        t.SetTrackLock(k, i, True)
                c = clips[0].GetFusionCompByIndex(1)
                assert c
                tr = next((x for x in c.GetToolList().values() if x.GetAttrs().get('TOOLS_RegID') == 'Transform'))
                old = tr.GetInput('Center')
                tr.SetInput('Center', CENTER)
                new = tr.GetInput('Center')
                assert new == CENTER, (n, old, new)
                assert pm.SaveProject()
                results.append({'ordinal': n, 'timeline': name, 'adjustment_id': clips[0].GetUniqueId(), 'old_center': old, 'new_center': new, 'saved': True})
            finally:
                for (k, i), state in locks.items():
                    if i <= t.GetTrackCount(k):
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
    Path('.hermes/artifacts/vtuber-focus-review-2026-10-07/headroom-tune.json').write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(results, ensure_ascii=False, indent=2))
if __name__ == '__main__':
    main()
