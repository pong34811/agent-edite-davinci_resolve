"""Render midpoint QC after headroom-only transform adjustments."""
from pathlib import Path
import json, subprocess, time
from scripts.resolve_common import connect_resolve
PILOT = 'aomimama-2026-09-p1-recovered-20261007'
ORIGINAL = 'aomimama-2026-09-p1'
TASKS = [(44, 'ทีมไฟต์ถูกชัตดาวน์-League of Legends-vdo', 1771, 1953, 3), (46, 'หัวยังไม่ฟู ตายก่อนเลย-League of Legends-vdo', 4029, 4135, 3), (47, 'ออกเมื่อไหร่มีตายเมื่อนั้น-League of Legends-vdo', 1699, 1760, 3)]
OUT = Path('.hermes/artifacts/vtuber-focus-review-2026-10-07/pilot-qc/headroom-tune-burnin-rerun').resolve()

def main():
    OUT.mkdir(parents=True, exist_ok=False)
    r = connect_resolve()
    assert r
    pm = r.GetProjectManager()
    entry = pm.GetCurrentProject()
    et = entry.GetCurrentTimeline().GetName()
    ec = entry.GetCurrentTimeline().GetCurrentTimecode()
    page = r.GetCurrentPage()
    assert entry.GetName() == ORIGINAL and (not entry.IsRenderingInProgress())
    p = pm.LoadProject(PILOT)
    assert p and p.GetName() == PILOT
    preset = 'Hermes-headroom-tune-rerun-restore-20261007'
    assert preset not in p.GetRenderPresetList() and p.SaveAsNewRenderPreset(preset)
    out = []
    try:
        for n, name, s, e, track in TASKS:
            t = next((p.GetTimelineByIndex(i) for i in range(1, p.GetTimelineCount() + 1) if p.GetTimelineByIndex(i).GetName() == name))
            p.SetCurrentTimeline(t)
            time.sleep(1)
            assert p.GetCurrentTimeline().GetName() == name
            assert any((x.GetType() == 'generator' and x.GetStart() == s and (x.GetEnd() == e) for x in t.GetItemListInTrack('video', track) or []))
            dest = OUT / f'T{n:02d}'
            dest.mkdir()
            assert p.LoadRenderPreset('H.264 Master') and p.SetCurrentRenderFormatAndCodec('mp4', 'H264_NVIDIA') and p.SetCurrentRenderMode(1)
            assert p.SetRenderSettings({'TargetDir': str(dest), 'CustomName': f'T{n:02d}-headroom-burnin', 'SelectAllFrames': False, 'ExportVideo': True, 'ExportAudio': True, 'FormatWidth': 1280, 'FormatHeight': 720, 'FrameRate': 60.0, 'MarkIn': s, 'MarkOut': e - 1, 'ExportSubtitle': True, 'SubtitleFormat': 'BurnIn'})
            job = p.AddRenderJob()
            assert job and p.StartRendering([job], False)
            deadline = time.monotonic() + 300
            while p.IsRenderingInProgress():
                if time.monotonic() > deadline:
                    raise RuntimeError(f'T{n} render timeout')
                time.sleep(2)
            status = p.GetRenderJobStatus(job)
            assert status.get('JobStatus') == 'Complete', status
            files = list(dest.glob('*.mp4'))
            assert len(files) == 1 and files[0].stat().st_size > 0
            meta = json.loads(subprocess.run(['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(files[0])], check=True, capture_output=True, text=True).stdout)
            v = [x for x in meta['streams'] if x['codec_type'] == 'video']
            a = [x for x in meta['streams'] if x['codec_type'] == 'audio']
            assert len(v) == 1 and a and ((v[0]['width'], v[0]['height']) == (1280, 720))
            out.append({'ordinal': n, 'timeline': name, 'range': [s, e], 'status': status, 'file': str(files[0].resolve()), 'bytes': files[0].stat().st_size, 'duration': meta['format']['duration']})
            print('COMPLETE', n, flush=True)
    finally:
        restored = bool(p.LoadRenderPreset(preset))
        p0 = pm.LoadProject(ORIGINAL)
        assert p0
        t0 = next((p0.GetTimelineByIndex(i) for i in range(1, p0.GetTimelineCount() + 1) if p0.GetTimelineByIndex(i).GetName() == et))
        p0.SetCurrentTimeline(t0)
        time.sleep(1)
        t0.SetCurrentTimecode(ec)
        time.sleep(0.5)
        if r.GetCurrentPage() != page:
            r.OpenPage(page)
            time.sleep(0.5)
        state = pm.GetCurrentProject().GetName() == ORIGINAL and pm.GetCurrentProject().GetCurrentTimeline().GetName() == et and (pm.GetCurrentProject().GetCurrentTimeline().GetCurrentTimecode() == ec) and (r.GetCurrentPage() == page)
        report = {'renders': out, 'render_settings_restored': restored, 'working_state_restored': state, 'no_project_save_called': True}
        (OUT / 'result.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
        assert state
    print(json.dumps(report, ensure_ascii=False, indent=2))
if __name__ == '__main__':
    main()
