"""Native Resolve Python batch enrichment on copies, not originals.
MCP-GAP: live Resolve MCP absent; uses shared connect_resolve and probed APIs.
Default dry-run. --apply --accept-provisional explicitly accepts draft cues/QC limits.
No UI automation, video-analysis API, source replacements, or database patches.
"""
from __future__ import annotations
import argparse
from datetime import datetime
import json
import math
from pathlib import Path
import sys
import time
import zipfile

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from scripts.resolve_common import connect_resolve
from scripts.apply_offline_enrichment_pilot import (
    source_frames, validate_range, contents, pool_available_frames, asset_mean, check,
)
from scripts.apply_video_style import validate_style, apply_style_batch
from scripts.apply_vdo_python import validate_reference

ART = ROOT / '.hermes/artifacts/enrichment-review-2026-10-06-live2'


def make_plan(row, exists=None):
    exists = exists or (lambda path: Path(path).is_file())
    preferred = ('NCSน่ารัก.mp3', '2025-02-04_-_Wishing_Well_-_www.FesliyanStudios.com_.mp3',
                 'FREE BGM 4 LOOP.wav', 'Gaming Music 2023 ♫ 1 Hour Gaming Music Mix ♫ Copyright Free Music.mp3')
    music = [a for a in row['bgm_candidates'] if a['name'] in preferred
             and a['duration_seconds'] >= row['duration_seconds'] and exists(a['path'])]
    music.sort(key=lambda a: preferred.index(a['name']))
    if not music:
        raise ValueError('No verified-duration BGM candidate covers timeline ' + str(row['ordinal']))
    greeting = any(term in row['name'] for term in ('เปิดสตรีม', 'ทักทาย', 'ขอบคุณ', 'ลาสตรีม'))
    chosen = music[0] if greeting else music[(row['ordinal'] - 1) % len(music)]
    effects = []
    for cue in row['cue_points']:
        groups = cue['asset_candidates']
        effects.append({'record_frame': cue['absolute_start_frame'], 'text': cue['text'],
                        'sfx_candidates': [a['path'] for a in groups['sfx'] if exists(a['path'])],
                        'gif_candidates': [a['path'] for a in groups['illustration'] if exists(a['path'])]})
    return {'ordinal': row['ordinal'], 'source_id': row['timeline_id'], 'source_name': row['name'],
            'copy_name': row['name'] + ' [ENRICHMENT DRAFT OFFLINE]', 'duration_seconds': row['duration_seconds'],
            'bgm': chosen, 'effects': effects, 'status': 'provisional_draft_only',
            'cue_evidence': 'subtitle-derived search shortlist, not verified audiovisual accent',
            'no_cue_note': 'No invented SFX/GIF; BGM-only draft' if not effects else None,
            'rights_status': 'unknown_private_draft_not_publication_cleared'}


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')


def activate(project, timeline):
    project.SetCurrentTimeline(timeline)
    time.sleep(0.5)
    if project.GetCurrentTimeline().GetUniqueId() != timeline.GetUniqueId():
        raise RuntimeError('Timeline activation mismatch')


def apply_copy(r, project, source, plan, style, backup, audio_cache):
    pm, mp = r.GetProjectManager(), project.GetMediaPool()
    report_path = ART / 'batch-python' / f'{plan["ordinal"]:02d}.json'
    check(source, ['DuplicateTimeline', 'SetTrackLock', 'GetIsTrackLocked', 'AddTrack', 'SetTrackName'])
    activate(project, source)
    fps = float(source.GetSetting('timelineFrameRate'))
    start, end = source.GetStartFrame(), source.GetEndFrame()
    if abs((end-start)/fps-plan['duration_seconds']) > 0.15:
        raise RuntimeError('Timeline duration changed after plan')
    validate_reference(style, project.GetUniqueId(), [source.GetSetting('timelineResolutionWidth'),
                                                    source.GetSetting('timelineResolutionHeight')])
    counts = {k: source.GetTrackCount(k) for k in ('video', 'audio', 'subtitle')}
    before = contents(source, counts)
    inventory = json.loads((ART/'inventory.json').read_text(encoding='utf-8'))
    saved = next(t for t in inventory['timelines'] if t['timeline_id']==source.GetUniqueId())
    expected_tracks = [{'kind':tr['kind'],'index':tr['index'],'name':tr['name'],'enabled':tr['enabled'],
                        'items':[{k:v for k,v in x.items() if k!='id'} for x in tr['items']]}
                       for tr in saved['tracks']]
    if before != expected_tracks:
        raise RuntimeError('Source content changed since approved preview; regenerate its evidence first')
    existing_gif_ranges = [(x['start'], x['end']) for tr in before if tr['kind']=='video'
                           for x in tr['items'] if str(x['media_path'] or '').lower().endswith('.gif')]
    root = mp.GetRootFolder()
    folder = next((f for f in root.GetSubFolderList() if f.GetName()=='OfflineEnrichment_20261006'), None)
    if folder is None:
        folder = mp.AddSubFolder(root, 'OfflineEnrichment_20261006')
        time.sleep(1.2)
    if folder is None or not mp.SetCurrentFolder(folder):
        raise RuntimeError('Task bin unavailable')
    def media(path):
        match = [x for x in folder.GetClipList() if str(Path(x.GetClipProperty('File Path'))).casefold()==str(Path(path)).casefold()]
        if len(match)>1:
            raise RuntimeError('Duplicate task-bin asset; reconcile manually')
        loaded = match or mp.ImportMedia([path])
        time.sleep(1.2)
        if not loaded or len(loaded)!=1:
            raise RuntimeError('Asset import failed: '+path)
        pool = loaded[0]
        mfps = float(pool.GetClipProperty('FPS'))
        return pool, mfps, pool_available_frames(pool, mfps)
    bgm_pool, bgm_fps, bgm_available = media(plan['bgm']['path'])
    bgm_frames = source_frames(end-start, fps, bgm_fps)
    if bgm_frames>bgm_available:
        raise RuntimeError('BGM native source range too short')
    jobs = [{'kind':'bgm', 'pool':bgm_pool, 'path':plan['bgm']['path'], 'at':start,
             'source_frames':bgm_frames, 'duration':end-start}]
    skipped = []
    for cue in plan['effects']:
        at = cue['record_frame']
        if not start<=at<end:
            raise RuntimeError('Cue outside live timeline')
        for kind, paths in [('sfx',cue['sfx_candidates']), ('gif',cue['gif_candidates'])]:
            if kind=='gif' and any(a<at+round(2*fps) and b>at for a,b in existing_gif_ranges):
                skipped.append({'kind':kind,'at':at,'reason':'existing_GIF_overlap_preserved'})
                continue
            placed = False
            for path in paths:
                pool, mfps, available = media(path)
                record_cap = min(round((2 if kind=='gif' else 1)*fps), end-at)
                n = min(source_frames(record_cap,fps,mfps), available)
                duration = math.floor(n*fps/mfps)
                if duration<=0 or (kind=='gif' and not 1.5<=duration/fps<=2.5):
                    skipped.append({'kind':kind,'path':path,'at':at,'reason':'source_or_remaining_hold_too_short'})
                    continue
                validate_range(start,end,at,duration)
                jobs.append({'kind':kind,'pool':pool,'path':path,'at':at,'source_frames':n,'duration':duration})
                placed=True
                break
            if not placed:
                skipped.append({'kind':kind,'at':at,'reason':'no_usable_candidate'})
    packet = json.loads((ART / 'offline-review' / f'{plan["ordinal"]:02d}' / 'packet.json').read_text(encoding='utf-8'))
    mixed_mean = packet['audio_metrics']['mixed_mean_dbfs']
    if mixed_mean is None:
        raise RuntimeError('Missing mixed audio reference; do not invent gains')
    for job in jobs:
        if job['kind']!='gif':
            if job['path'] not in audio_cache:
                audio_cache[job['path']] = asset_mean(job['path'])
            distance, cap = (20,-12) if job['kind']=='bgm' else (6,-6)
            job['gain'] = max(-60.0,min(float(cap),mixed_mean-distance-audio_cache[job['path']]))
    copy = source.DuplicateTimeline(plan['copy_name'])
    time.sleep(1.2)
    if copy is None:
        raise RuntimeError('DuplicateTimeline failed')
    report = {'ordinal':plan['ordinal'],'source_id':source.GetUniqueId(),'copy_id':copy.GetUniqueId(),
              'copy_name':plan['copy_name'],'backup':backup,'status':'partial_do_not_blindly_retry',
              'inserted':[],'skipped':skipped, 'qc':'pending_human_visual_and_listening_review',
              'gain_basis':'mixed preview level, not isolated speech normalization',
              'vdo_method':'Python copies exposed values captured after native UI vdo load'}
    write_json(report_path,report)
    activate(project,copy)
    if contents(copy,counts)!=before:
        raise RuntimeError('Copy protected content mismatch')
    locks=[]
    try:
        for kind,count in counts.items():
            for index in range(1,count+1):
                locks.append((kind,index,copy.GetIsTrackLocked(kind,index)))
                copy.SetTrackLock(kind,index,True)
        tracks={}
        for kind,tt in [('bgm','audio'),('sfx','audio'),('gif','video')]:
            if not any(j['kind']==kind for j in jobs):
                continue
            if not copy.AddTrack(tt):
                raise RuntimeError('AddTrack failed')
            time.sleep(1.2)
            index=copy.GetTrackCount(tt)
            copy.SetTrackName(tt,index,'OFFLINE_DRAFT_'+kind.upper())
            tracks[kind]=index
        for job in jobs:
            kind=job['kind']
            result=mp.AppendToTimeline([{'mediaPoolItem':job['pool'],'startFrame':0,'endFrame':job['source_frames'],
                'mediaType':1 if kind=='gif' else 2,'trackIndex':tracks[kind],'recordFrame':job['at']}])
            time.sleep(1.2)
            if not result or len(result)!=1:
                raise RuntimeError('Append failed; inspect partial copy before retry')
            clip=result[0]
            actual=clip.GetEnd()-clip.GetStart()
            report['inserted'].append({'kind':kind,'item_id':clip.GetUniqueId(),'path':job['path'],
                                      'start':clip.GetStart(),'end':clip.GetEnd(),'track':tracks[kind]})
            write_json(report_path,report)
            if clip.GetStart()!=job['at'] or clip.GetEnd()>end:
                raise RuntimeError('Append range mismatch')
            if kind=='bgm' and (clip.GetStart()!=start or clip.GetEnd()!=end):
                raise RuntimeError('BGM must cover exact timeline')
            if kind=='gif':
                if not 1.5<=actual/fps<=2.5:
                    raise RuntimeError('Conformed GIF outside approved hold')
                apply_style_batch([clip],style,[clip.GetUniqueId()],apply=True)
            else:
                if abs(actual-job['duration'])>1:
                    raise RuntimeError('Conformed SFX duration mismatch')
                clip.SetProperty('AudioVolume',float(job['gain']))
                if abs(float(clip.GetProperty('AudioVolume'))-job['gain'])>0.01:
                    raise RuntimeError('Audio gain readback failed')
                fades={'FadeIn':round(0.5*fps) if kind=='bgm' else 0,
                       'FadeOut':round(fps) if kind=='bgm' else min(round(0.15*fps),actual)}
                clip.SetFades(fades)
                if clip.GetFades()!=fades:
                    raise RuntimeError('Fade readback mismatch')
        if contents(copy,counts)!=before or copy.GetEndFrame()!=end:
            raise RuntimeError('Protected copy content changed')
        for kind,index,state in locks:
            copy.SetTrackLock(kind,index,state)
        locks.clear()
        if not pm.SaveProject():
            raise RuntimeError('SaveProject failed')
        activate(project,source)
        if contents(source,counts)!=before:
            raise RuntimeError('Original changed')
        report.update({'status':'saved_provisional_copy','original_unchanged':True,'protected_copy_verified':True})
    except Exception as exc:
        report['error']=str(exc)
        raise
    finally:
        if locks:
            activate(project,copy)
            for kind,index,state in locks:
                copy.SetTrackLock(kind,index,state)
        write_json(report_path,report)
    return report


def main(argv=None):
    ap=argparse.ArgumentParser(description=__doc__)
    group=ap.add_mutually_exclusive_group(required=True)
    group.add_argument('--all',action='store_true')
    group.add_argument('--ordinals',help='Explicit inventory ordinals, e.g. 2,3,4')
    ap.add_argument('--project-id',required=True)
    ap.add_argument('--style-json',type=Path,default=ART/'vdo-current-project.json')
    ap.add_argument('--apply',action='store_true')
    ap.add_argument('--accept-provisional',action='store_true',help='Accept draft cues; not final AV QC')
    args=ap.parse_args(argv)
    if args.apply and not args.accept_provisional:
        ap.error('--apply requires --accept-provisional; user pilot review is pending')
    draft=json.loads((ART/'offline-review/asset-draft.json').read_text(encoding='utf-8'))
    chosen=draft['timelines']
    if args.ordinals:
        wanted={int(x) for x in args.ordinals.split(',')}
        chosen=[t for t in chosen if t['ordinal'] in wanted]
        if {t['ordinal'] for t in chosen}!=wanted:
            raise ValueError('Requested ordinal missing')
    plans=[make_plan(t) for t in chosen]
    style=json.loads(args.style_json.read_text(encoding='utf-8'))
    validate_style(style)
    r=connect_resolve()
    if r is None:
        raise RuntimeError('Resolve unavailable')
    pm=r.GetProjectManager()
    p=pm.GetCurrentProject()
    if p is None or p.GetUniqueId()!=args.project_id or p.GetName()!='aomimama-2026-09-p1':
        raise RuntimeError('Exact project mismatch')
    if p.IsRenderingInProgress():
        raise RuntimeError('Existing render running')
    timelines=[p.GetTimelineByIndex(i) for i in range(1,p.GetTimelineCount()+1)]
    by_id={t.GetUniqueId():t for t in timelines}
    if len(by_id)!=len(timelines) or any(t['source_id'] not in by_id for t in plans):
        raise RuntimeError('Live original target ID mismatch')
    result={'dry_run':not args.apply,'project_id':args.project_id,'target_count':len(plans),
            'effect_review_points':sum(len(t['effects']) for t in plans),'plans':plans,
            'modified_originals':False,'native_named_preset_loaded_by_python':False,
            'av_qc':'pending_human_review','completed':[]}
    report_path=ART/'batch-python'/'last-run.json'
    entry=p.GetCurrentTimeline()
    tc,page=entry.GetCurrentTimecode(),r.GetCurrentPage()
    mp=p.GetMediaPool()
    folder=mp.GetCurrentFolder()
    try:
        for plan in plans:
            source=by_id[plan['source_id']]
            activate(p,source)
            validate_reference(style,p.GetUniqueId(),[source.GetSetting('timelineResolutionWidth'),source.GetSetting('timelineResolutionHeight')])
            expected=plan['duration_seconds']
            duration=(source.GetEndFrame()-source.GetStartFrame())/float(source.GetSetting('timelineFrameRate'))
            if source.GetName()!=plan['source_name'] or abs(duration-expected)>0.15:
                raise RuntimeError('Live name/duration mismatch')
        if not args.apply:
            write_json(report_path,result)
            print('DRY_RUN_VERIFIED',len(plans),'TIMELINES',result['effect_review_points'],'PROVISIONAL_POINTS',flush=True)
            return 0
        # Refuse partial/existing drafts rather than creating duplicate appends.
        names={t.GetName() for t in timelines}
        pilot=json.loads((ART/'pilot-offline-01.json').read_text(encoding='utf-8'))
        for plan in plans:
            if plan['copy_name'] in names:
                raise RuntimeError('Draft already exists; reconcile its report before rerun')
            if plan['source_id']==pilot['source_timeline_id']:
                if pilot['pilot_id'] not in by_id:
                    raise RuntimeError('Existing pilot missing')
                plan['existing_pilot_id']=pilot['pilot_id']
        backup_dir=ART/'backups'
        backup_dir.mkdir(exist_ok=True)
        backup=backup_dir/('before_python_batch_'+datetime.now().strftime('%Y%m%d-%H%M%S-%f')+'.drp')
        if not pm.SaveProject() or not pm.ExportProject(p.GetName(),str(backup),False):
            raise RuntimeError('Fresh project backup failed')
        with zipfile.ZipFile(backup) as archive:
            if archive.testzip() is not None:
                raise RuntimeError('DRP archive failed validation')
        result['backup']=str(backup)
        cache={}
        for plan in plans:
            if 'existing_pilot_id' in plan:
                result['completed'].append({'ordinal':plan['ordinal'],'existing_pilot_id':plan['existing_pilot_id'],'status':'existing_pilot_retained_no_duplicate'})
            else:
                result['completed'].append(apply_copy(r,p,by_id[plan['source_id']],plan,style,str(backup),cache))
            write_json(report_path,result)
            print('COPY_BATCH_PROGRESS',plan['ordinal'],flush=True)
    finally:
        activate(p,entry)
        entry.SetCurrentTimecode(tc)
        time.sleep(0.3)
        mp.SetCurrentFolder(folder)
        if r.GetCurrentPage()!=page:
            r.OpenPage(page)
            time.sleep(1)
        result['restoration_verified']=(p.GetCurrentTimeline().GetUniqueId()==entry.GetUniqueId()
            and entry.GetCurrentTimecode()==tc and r.GetCurrentPage()==page
            and mp.GetCurrentFolder().GetUniqueId()==folder.GetUniqueId())
        write_json(report_path,result)
        if not result['restoration_verified']:
            raise RuntimeError('Working state restoration failed')
    print('BATCH_FINISHED',len(result['completed']), 'COPIES; HUMAN_QC_PENDING',flush=True)
    return 0


if __name__=='__main__':
    raise SystemExit(main())
