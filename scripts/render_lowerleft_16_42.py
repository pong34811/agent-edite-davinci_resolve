"""Burn-in renders for the 16 lower-left pilot candidates T16–T42."""
from pathlib import Path
import json, subprocess, time
from scripts.resolve_common import connect_resolve
PILOT = 'aomimama-2026-09-p1-recovered-20261007'
ORIGINAL = 'aomimama-2026-09-p1'
TASKS = [(16, 'หนาวติดลบ 16 ต้องถือลาวา-Minecraft-vdo', 3258, 3330, 3), (17, 'ถือถังลาวาไว้กันหนาว-Minecraft-vdo', 2480, 2629, 3), (18, 'พี่น้องไม่เคยช่วยอะไรเลย-Minecraft-vdo', 1964, 2165, 3), (27, 'ในที่สุดแชร์จอเหมือนคนปกติได้แล้ว-alien shooter 2-vdo', 2520, 2640, 2), (28, 'ปรับความละเอียด 1024x768 ไอ้เฮีย-alien shooter 2-vdo', 3600, 3837, 3), (31, 'ดับเบิลคิลแล้วโดนฝัง-League of Legends-vdo', 3480, 3540, 2), (33, 'เมาท์เรื่องสายเล่นเกม-League of Legends-vdo', 2580, 2820, 3), (36, 'ลืมเปิดเสียงเพื่อน คุยกับผีมาตั้งนาน-Minecraft-vdo', 1590, 1677, 3), (37, 'ลืมเอาอาหาร ต้องกินเนื้อซอมบี้-Minecraft-vdo', 3456, 3612, 3), (38, 'ซอมบี้มาได้ไงวะ!-Minecraft-vdo', 1849, 2070, 3), (39, 'อยากเปลี่ยนร่าง เอาคนไม่มีเสียงในหัวมาเล่นแทน-Minecraft-vdo', 1560, 1737, 3), (40, 'พี่จ๋าช่วยด้วย เรือไปไหนวะ-Minecraft-vdo', 2700, 2877, 3), (41, 'วิ่งหนีมอนตอนมืดจนเห็นบ้าน-Minecraft-vdo', 4508, 4564, 3), (42, 'ออกไม่ได้เลยวะ ฮ่าๆๆ-Minecraft-vdo', 1991, 2272, 3)]
OUT = Path('.hermes/artifacts/vtuber-focus-review-2026-10-07/pilot-qc/lowerleft-16-42-rerun').resolve()

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
    preset = 'Hermes-lowerleft-16-42-rerun-render-restore-20261007'
    assert preset not in p.GetRenderPresetList() and p.SaveAsNewRenderPreset(preset)
    records = []
    try:
        for n, name, s, e, track in TASKS:
            t = next((p.GetTimelineByIndex(i) for i in range(1, p.GetTimelineCount() + 1) if p.GetTimelineByIndex(i).GetName() == name))
            p.SetCurrentTimeline(t)
            time.sleep(0.8)
            assert any((x.GetType() == 'generator' and x.GetStart() == s and (x.GetEnd() == e) for x in t.GetItemListInTrack('video', track) or [])), (n, track)
            dest = OUT / f'T{n:02d}'
            dest.mkdir()
            assert p.LoadRenderPreset('H.264 Master') and p.SetCurrentRenderFormatAndCodec('mp4', 'H264_NVIDIA') and p.SetCurrentRenderMode(1)
            assert p.SetRenderSettings({'TargetDir': str(dest), 'CustomName': f'T{n:02d}-focus-burnin', 'SelectAllFrames': False, 'ExportVideo': True, 'ExportAudio': True, 'FormatWidth': 1280, 'FormatHeight': 720, 'FrameRate': 60.0, 'MarkIn': s, 'MarkOut': e - 1, 'ExportSubtitle': True, 'SubtitleFormat': 'BurnIn'})
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
            records.append({'ordinal': n, 'timeline': name, 'range': [s, e], 'output': str(files[0].resolve()), 'bytes': files[0].stat().st_size, 'duration': meta['format']['duration'], 'status': status})
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
        report = {'renders': records, 'render_settings_restored': restored, 'working_state_restored': state, 'no_project_save_called': True}
        (OUT / 'result.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
        assert state
    print(json.dumps(report, ensure_ascii=False, indent=2))
if __name__ == '__main__':
    main()
