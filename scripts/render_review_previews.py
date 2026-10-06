"""Authorized review-only previews. No source/timeline edits or SaveProject.
MCP render tool absent in live catalog; native methods probed first.
"""
from __future__ import annotations
import argparse
import json
import subprocess
import time
from datetime import datetime
from pathlib import Path
from scripts.resolve_common import connect_resolve

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / '.hermes/artifacts/enrichment-review-2026-10-06-live2'

def write(name, value):
    (ART / name).write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')

def required(obj, names):
    missing = [n for n in names if n not in dir(obj)]
    if missing:
        raise RuntimeError('Unavailable native methods: ' + ', '.join(missing))

def signature(tl):
    tracks = []
    for kind in ('video', 'audio', 'subtitle'):
        for k in range(1, tl.GetTrackCount(kind) + 1):
            tracks.append({'kind': kind, 'index': k,
                'enabled': tl.GetIsTrackEnabled(kind, k),
                'locked': tl.GetIsTrackLocked(kind, k),
                'items': [(x.GetUniqueId(), x.GetName(), x.GetStart(), x.GetEnd())
                          for x in (tl.GetItemListInTrack(kind, k) or [])]})
    return {'id': tl.GetUniqueId(), 'start': tl.GetStartFrame(), 'end': tl.GetEndFrame(),
            'fps': tl.GetSetting('timelineFrameRate'),
            'width': tl.GetSetting('timelineResolutionWidth'),
            'height': tl.GetSetting('timelineResolutionHeight'), 'tracks': tracks}

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--ordinals', required=True, help='comma-separated inventory ordinals or all')
    args = ap.parse_args()
    inventory = json.loads((ART / 'inventory.json').read_text(encoding='utf-8'))
    chosen = inventory['timelines'] if args.ordinals == 'all' else [
        t for t in inventory['timelines'] if t['ordinal'] in {int(n) for n in args.ordinals.split(',')}]
    if not chosen:
        raise RuntimeError('Empty selection')
    r = connect_resolve()
    if r is None:
        raise RuntimeError('No bridge')
    pm = r.GetProjectManager()
    p = pm.GetCurrentProject()
    if p.GetName() != inventory['project_name']:
        raise RuntimeError('Project mismatch')
    required(p, ['SaveAsNewRenderPreset','LoadRenderPreset','DeleteRenderPreset',
        'GetRenderPresetList','SetCurrentRenderFormatAndCodec','SetRenderSettings',
        'SetCurrentRenderMode','AddRenderJob','GetRenderJobList','GetRenderJobStatus',
        'StartRendering','IsRenderingInProgress'])
    if p.IsRenderingInProgress():
        raise RuntimeError('Existing render running; refusing interference')
    targets = {p.GetTimelineByIndex(k).GetUniqueId(): p.GetTimelineByIndex(k)
               for k in range(1, p.GetTimelineCount() + 1)}
    if set(targets) != {t['timeline_id'] for t in inventory['timelines']}:
        raise RuntimeError('Target set drift')
    entry = p.GetCurrentTimeline()
    entry_tc = entry.GetCurrentTimecode()
    page = r.GetCurrentPage()
    old_jobs = {j['JobId'] for j in p.GetRenderJobList()}
    restore_name = 'Hermes-review-restore-' + datetime.now().strftime('%Y%m%d-%H%M%S')
    if restore_name in p.GetRenderPresetList():
        raise RuntimeError('Restore preset name collision')
    if not p.SaveAsNewRenderPreset(restore_name):
        raise RuntimeError('Could not preserve render settings')
    if restore_name not in p.GetRenderPresetList():
        raise RuntimeError('Restore preset readback failed')
    write('preview-entry-' + restore_name + '.json', {'timeline_id':entry.GetUniqueId(),
          'timecode':entry_tc,'page':page,'existing_job_ids':sorted(old_jobs),
          'restore_preset':restore_name})
    results = []
    try:
        for row in chosen:
            tl = targets[row['timeline_id']]
            if not p.SetCurrentTimeline(tl):
                raise RuntimeError('Activate failed')
            time.sleep(1.2)
            if p.GetCurrentTimeline().GetUniqueId() != row['timeline_id']:
                raise RuntimeError('Wrong active target')
            tc = tl.GetCurrentTimecode()
            before = signature(tl)
            if before['end'] != row['end'] or before['start'] != row['start']:
                raise RuntimeError('Timeline bounds drift since snapshot')
            outdir = ART / 'previews' / (f"{row['ordinal']:02d}-" + datetime.now().strftime('%H%M%S'))
            outdir.mkdir(parents=True, exist_ok=False)
            if not p.LoadRenderPreset('H.264 Master'):
                raise RuntimeError('Video base preset failed')
            if not p.SetCurrentRenderFormatAndCodec('mp4', 'H264_NVIDIA'):
                raise RuntimeError('Verified NVIDIA codec rejected')
            if not p.SetCurrentRenderMode(1):
                raise RuntimeError('Single-clip mode rejected')
            settings = {'TargetDir':str(outdir), 'CustomName':row['timeline_id'],
                'SelectAllFrames':True, 'ExportVideo':True, 'ExportAudio':True,
                'FormatWidth':1280, 'FormatHeight':720, 'FrameRate':float(row['record_fps']),
                'ExportSubtitle':True, 'SubtitleFormat':'BurnIn'}
            if not p.SetRenderSettings(settings):
                raise RuntimeError('Preview settings rejected; no job queued')
            job = p.AddRenderJob()
            if not job:
                raise RuntimeError('Queue failed')
            queue = [j for j in p.GetRenderJobList() if j['JobId'] == job]
            if len(queue) != 1 or not queue[0]['IsExportVideo'] or not queue[0]['IsExportAudio']:
                raise RuntimeError('Queued export flags incorrect')
            if not p.StartRendering([job], False):
                raise RuntimeError('Start failed')
            deadline = time.monotonic() + 600
            while p.IsRenderingInProgress():
                if time.monotonic() > deadline:
                    raise RuntimeError('Render running beyond bound; do not launch another writer')
                time.sleep(2)
            status = p.GetRenderJobStatus(job)
            if status.get('JobStatus') != 'Complete':
                raise RuntimeError('Render incomplete: ' + str(status))
            files = list(outdir.glob('*.mp4'))
            if len(files) != 1 or files[0].stat().st_size == 0:
                raise RuntimeError('Output missing/ambiguous')
            probe = subprocess.run(['ffprobe','-v','error','-show_streams','-show_format',
                '-of','json',str(files[0])],check=True,capture_output=True,text=True)
            meta = json.loads(probe.stdout)
            vs = [s for s in meta['streams'] if s['codec_type']=='video']
            aud = [s for s in meta['streams'] if s['codec_type']=='audio']
            if len(vs)!=1 or not aud or vs[0]['width']!=1280 or vs[0]['height']!=720:
                raise RuntimeError('Output stream verification failed')
            expected = (row['end']-row['start']) / float(row['record_fps'])
            if abs(float(meta['format']['duration'])-expected)>0.1:
                raise RuntimeError('Output duration mismatch')
            after = signature(tl)
            if after != before:
                raise RuntimeError('Protected timeline structure changed')
            tl.SetCurrentTimecode(tc)
            time.sleep(1.2)
            if tl.GetCurrentTimecode()!=tc:
                raise RuntimeError('Target playhead restoration failed')
            result = {'ordinal':row['ordinal'],'timeline_id':row['timeline_id'],
                'path':str(files[0]),'job_id':job,'status':status,'ffprobe':meta,
                'structure_unchanged':True,'av_review_status':'not_reviewed'}
            results.append(result)
            write(f"preview-{row['ordinal']:02d}.json",result)
            print('PREVIEW VERIFIED',row['ordinal'],str(files[0]),flush=True)
    finally:
        restore_ok = p.LoadRenderPreset(restore_name)
        p.SetCurrentTimeline(entry)
        time.sleep(1.2)
        entry.SetCurrentTimecode(entry_tc)
        time.sleep(1.2)
        page_ok = r.GetCurrentPage()==page
        if not page_ok:
            r.OpenPage(page)
            time.sleep(1.2)
            page_ok = r.GetCurrentPage()==page
        existing_jobs_ok = old_jobs <= {j['JobId'] for j in p.GetRenderJobList()}
        restored = {'preset_load_return':restore_ok,'active_timeline_verified':
            p.GetCurrentTimeline().GetUniqueId()==entry.GetUniqueId(),
            'playhead_verified':entry.GetCurrentTimecode()==entry_tc,
            'page_verified':page_ok,'existing_jobs_preserved':existing_jobs_ok,
            'restore_preset_retained_for_recovery':restore_name,
            'no_project_save_called':True}
        write('preview-restoration-' + restore_name + '.json',restored)
        print('RESTORE',json.dumps(restored),flush=True)
    print('Completed previews:',len(results),flush=True)

if __name__ == '__main__':
    main()
