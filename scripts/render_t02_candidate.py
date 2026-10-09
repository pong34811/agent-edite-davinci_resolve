"""Burn-in preview and metadata verification for the T05 candidate."""
from pathlib import Path
import json, subprocess, time
from scripts.resolve_common import connect_resolve
PILOT = 'aomimama-2026-09-p1-recovered-20261007'
ORIGINAL = 'aomimama-2026-09-p1'
NAME = 'เสียงร้องโอ๊ยๆ-League of Legends-vdo'
START, END = (2350, 2430)
OUT = Path('.hermes/artifacts/vtuber-focus-review-2026-10-07/pilot-qc/T30-zoom26-burnin').resolve()

def main():
    OUT.mkdir(parents=True, exist_ok=False)
    r = connect_resolve()
    assert r
    pm = r.GetProjectManager()
    entry = pm.GetCurrentProject()
    et = entry.GetCurrentTimeline().GetName()
    ec = entry.GetCurrentTimeline().GetCurrentTimecode()
    page = r.GetCurrentPage()
    assert entry.GetName() == ORIGINAL
    p = pm.LoadProject(PILOT)
    assert p and p.GetName() == PILOT and (not p.IsRenderingInProgress())
    preset = 'Hermes-T30-zoom26-render-restore-20261007'
    assert preset not in p.GetRenderPresetList() and p.SaveAsNewRenderPreset(preset)
    report = {'timeline': NAME, 'range': [START, END], 'subtitle': 'teacher to student.', 'burnin_requested': True}
    try:
        t = next((p.GetTimelineByIndex(i) for i in range(1, p.GetTimelineCount() + 1) if p.GetTimelineByIndex(i).GetName() == NAME))
        assert any((x.GetType() == 'generator' and x.GetStart() == START and (x.GetEnd() == END) for x in t.GetItemListInTrack('video', 2) or []))
        assert p.LoadRenderPreset('H.264 Master') and p.SetCurrentRenderFormatAndCodec('mp4', 'H264_NVIDIA') and p.SetCurrentRenderMode(1)
        assert p.SetRenderSettings({'TargetDir': str(OUT), 'CustomName': 'T30-zoom26-focus-burnin', 'SelectAllFrames': False, 'ExportVideo': True, 'ExportAudio': True, 'FormatWidth': 1280, 'FormatHeight': 720, 'FrameRate': 60.0, 'MarkIn': START, 'MarkOut': END - 1, 'ExportSubtitle': True, 'SubtitleFormat': 'BurnIn'})
        job = p.AddRenderJob()
        assert job and p.StartRendering([job], False)
        deadline = time.monotonic() + 300
        while p.IsRenderingInProgress():
            if time.monotonic() > deadline:
                raise RuntimeError('render timeout')
            time.sleep(2)
        status = p.GetRenderJobStatus(job)
        assert status.get('JobStatus') == 'Complete', status
        files = list(OUT.glob('*.mp4'))
        assert len(files) == 1 and files[0].stat().st_size > 0
        meta = json.loads(subprocess.run(['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(files[0])], check=True, capture_output=True, text=True).stdout)
        v = [x for x in meta['streams'] if x['codec_type'] == 'video']
        a = [x for x in meta['streams'] if x['codec_type'] == 'audio']
        assert len(v) == 1 and a and ((v[0]['width'], v[0]['height']) == (1280, 720)) and (abs(float(meta['format']['duration']) - (END - START) / 60) < 0.12)
        report.update({'status': status, 'output': str(files[0].resolve()), 'bytes': files[0].stat().st_size, 'duration': meta['format']['duration'], 'streams': meta['streams']})
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
        report.update({'render_settings_restored': restored, 'working_state_restored': state, 'no_project_save_called': True})
        (OUT / 'result.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
        assert state
    print(json.dumps(report, ensure_ascii=False, indent=2))
if __name__ == '__main__':
    main()
