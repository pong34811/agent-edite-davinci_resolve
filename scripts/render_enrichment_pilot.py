"""Render the exact approved enrichment pilot for local human QC, no APIs.
MCP-GAP: live Resolve MCP absent; same probed native render API as preview batch.
No source/timeline edits; preserve queue, render settings and navigation.
"""
import json
import subprocess
import time
from datetime import datetime
from fractions import Fraction
from pathlib import Path
from scripts.resolve_common import connect_resolve
from scripts.render_review_previews import required
from scripts.apply_video_style import snapshot_timeline

ART = Path(__file__).resolve().parents[1] / '.hermes/artifacts/enrichment-review-2026-10-06-live2'


def verify_media(meta, duration):
    video = [s for s in meta['streams'] if s['codec_type'] == 'video']
    audio = [s for s in meta['streams'] if s['codec_type'] == 'audio']
    if len(video) != 1 or not audio or video[0]['width'] != 1280 or video[0]['height'] != 720:
        raise ValueError('Preview must contain 1280x720 video and audio')
    if Fraction(video[0]['avg_frame_rate']) != 60 or abs(float(meta['format']['duration']) - duration) > 0.1:
        raise ValueError('Preview FPS/duration mismatch')


def main():
    pilot = json.loads((ART / 'pilot-offline-01.json').read_text(encoding='utf-8'))
    r = connect_resolve()
    if r is None:
        raise RuntimeError('Resolve unavailable')
    p = r.GetProjectManager().GetCurrentProject()
    if p.GetName() != pilot['project']:
        raise RuntimeError('Project mismatch')
    required(p, ['SaveAsNewRenderPreset', 'LoadRenderPreset', 'GetRenderPresetList', 'GetRenderFormats',
                 'GetRenderCodecs', 'SetCurrentRenderFormatAndCodec', 'SetCurrentRenderMode',
                 'SetRenderSettings', 'AddRenderJob', 'GetRenderJobList', 'StartRendering',
                 'IsRenderingInProgress', 'GetRenderJobStatus'])
    if p.IsRenderingInProgress():
        raise RuntimeError('Existing render running')
    tl = next(p.GetTimelineByIndex(i) for i in range(1, p.GetTimelineCount() + 1)
              if p.GetTimelineByIndex(i).GetUniqueId() == pilot['pilot_id'])
    entry = p.GetCurrentTimeline()
    entry_tc, page = entry.GetCurrentTimecode(), r.GetCurrentPage()
    pool = p.GetMediaPool()
    folder = pool.GetCurrentFolder()
    old_jobs = {j['JobId'] for j in p.GetRenderJobList()}
    stamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    restore_name = 'Hermes-pilot-restore-' + stamp
    if not p.SaveAsNewRenderPreset(restore_name) or restore_name not in p.GetRenderPresetList():
        raise RuntimeError('Cannot preserve render settings')
    report = {'timeline_id': tl.GetUniqueId(), 'status': 'preparing',
              'restore_preset': restore_name, 'av_qc': 'pending_human_picture_and_listening_review'}
    out = ART / 'pilot-renders' / stamp
    out.mkdir(parents=True, exist_ok=False)
    (ART / 'pilot-render-entry.json').write_text(json.dumps({
        'timeline_id': entry.GetUniqueId(), 'timecode': entry_tc, 'page': page,
        'folder_id': folder.GetUniqueId(), 'restore_preset': restore_name}, indent=2), encoding='utf-8')
    try:
        p.SetCurrentTimeline(tl)
        time.sleep(1.2)
        if p.GetCurrentTimeline().GetUniqueId() != pilot['pilot_id']:
            raise RuntimeError('Wrong active pilot')
        tc = tl.GetCurrentTimecode()
        before = snapshot_timeline(tl)
        if float(tl.GetSetting('timelineFrameRate')) != 60:
            raise RuntimeError('Pilot frame rate changed')
        if 'mp4' not in p.GetRenderFormats().values() or 'H264_NVIDIA' not in p.GetRenderCodecs('mp4').values():
            raise RuntimeError('Pinned preview codec unavailable')
        if not p.LoadRenderPreset('H.264 Master') or not p.SetCurrentRenderFormatAndCodec('mp4', 'H264_NVIDIA'):
            raise RuntimeError('Pinned video preset/codec rejected')
        if not p.SetCurrentRenderMode(1):
            raise RuntimeError('Single-clip mode rejected')
        if not p.SetRenderSettings({'TargetDir': str(out), 'CustomName': 'pilot-01-enriched-vdo',
            'SelectAllFrames': True, 'ExportVideo': True, 'ExportAudio': True,
            'FormatWidth': 1280, 'FormatHeight': 720, 'FrameRate': 60.0,
            'ExportSubtitle': True, 'SubtitleFormat': 'BurnIn'}):
            raise RuntimeError('Preview settings rejected')
        job = p.AddRenderJob()
        queued = [j for j in p.GetRenderJobList() if j['JobId'] == job]
        if len(queued) != 1 or not queued[0]['IsExportVideo'] or not queued[0]['IsExportAudio']:
            raise RuntimeError('Queued export flags wrong')
        report.update({'job_id': job, 'status': 'rendering'})
        (ART / 'pilot-render.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
        print('PILOT_RENDER_STARTED', job, flush=True)
        if not p.StartRendering([job], False):
            raise RuntimeError('Render start failed')
        deadline = time.monotonic() + 480
        while p.IsRenderingInProgress():
            if time.monotonic() > deadline:
                raise RuntimeError('Render exceeded bound; do not start another writer')
            time.sleep(2)
        state = p.GetRenderJobStatus(job)
        if state.get('JobStatus') != 'Complete':
            raise RuntimeError('Render incomplete: ' + str(state))
        files = list(out.glob('*.mp4'))
        if len(files) != 1 or files[0].stat().st_size == 0:
            raise RuntimeError('Output missing or ambiguous')
        meta = json.loads(subprocess.run(['ffprobe', '-v', 'error', '-show_streams', '-show_format',
             '-of', 'json', str(files[0])], check=True, capture_output=True, text=True).stdout)
        duration = (tl.GetEndFrame() - tl.GetStartFrame()) / float(tl.GetSetting('timelineFrameRate'))
        verify_media(meta, duration)
        if snapshot_timeline(tl) != before:
            raise RuntimeError('Pilot protected content changed during render')
        tl.SetCurrentTimecode(tc)
        time.sleep(0.5)
        if tl.GetCurrentTimecode() != tc:
            raise RuntimeError('Pilot playhead restoration failed')
        report.update({'status': 'complete_streams_and_structure_verified', 'path': str(files[0].resolve()),
                       'job_status': state, 'ffprobe': meta, 'protected_content_verified': True})
    finally:
        report['render_settings_restored'] = bool(p.LoadRenderPreset(restore_name))
        p.SetCurrentTimeline(entry)
        time.sleep(1.2)
        entry.SetCurrentTimecode(entry_tc)
        pool.SetCurrentFolder(folder)
        if r.GetCurrentPage() != page:
            r.OpenPage(page)
            time.sleep(1.2)
        report['working_state_restored'] = (p.GetCurrentTimeline().GetUniqueId() == entry.GetUniqueId()
            and p.GetCurrentTimeline().GetCurrentTimecode() == entry_tc
            and r.GetCurrentPage() == page and pool.GetCurrentFolder().GetUniqueId() == folder.GetUniqueId())
        report['old_jobs_preserved'] = old_jobs <= {j['JobId'] for j in p.GetRenderJobList()}
        (ART / 'pilot-render.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    if not all(report[k] for k in ('render_settings_restored', 'working_state_restored', 'old_jobs_preserved')):
        raise RuntimeError('Render restoration incomplete')
    print('PILOT_RENDER_VERIFIED', report['path'], flush=True)


if __name__ == '__main__':
    main()
