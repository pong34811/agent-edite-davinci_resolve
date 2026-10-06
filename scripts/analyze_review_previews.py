"""Analyze authorized Resolve preview derivatives via existing Gemini auth.
Does not connect to Resolve or change its project. No secrets read or printed.
Native adapter's image_url data carrier preserves actual video/mp4 MIME; the
video_url adapter currently drops video. This route was smoke-tested separately.
"""
from __future__ import annotations
import argparse
import base64
import json
import subprocess
import time
from pathlib import Path


def request_with_retry(operation, *, sleep=time.sleep):
    """Retry transient provider overload only, at most four total requests."""
    for attempt in range(4):
        try:
            return operation()
        except Exception as exc:
            status = getattr(exc, 'status_code', None)
            if status not in (500, 502, 503, 504) or attempt == 3:
                raise
            delay = 30 * (2 ** attempt)
            print(f'PROVIDER HTTP {status}; retry {attempt + 1}/3 in {delay}s', flush=True)
            sleep(delay)
    raise RuntimeError('Retry loop exhausted unexpectedly')

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / '.hermes/artifacts/enrichment-review-2026-10-06-live2'

def generation_options() -> dict:
    # Gemini thinking shares the answer token budget; reserve it for bounded JSON.
    return {
        'max_tokens': 8192,
        'response_format': {'type': 'json_object'},
        'extra_body': {'thinking_config': {'thinkingBudget': 0}},
    }


def partition_cues(cues: list, duration: float) -> tuple[list, list]:
    accepted, rejected = [], []
    for cue in cues:
        when = cue.get('relative_seconds') if isinstance(cue, dict) else None
        if (isinstance(when, bool) or not isinstance(when, (int, float))
                or not 0 <= when < duration):
            rejected.append({'cue': cue, 'reason': 'outside_timeline_or_invalid_timestamp'})
        elif cue.get('kind') not in ('sfx', 'illustration'):
            rejected.append({'cue': cue, 'reason': 'invalid_cue_kind'})
        else:
            accepted.append(cue)
    return accepted, rejected


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--ordinals', required=True)
    args = ap.parse_args()
    from agent.auxiliary_client import get_text_auxiliary_client
    inventory = json.loads((ART / 'inventory.json').read_text(encoding='utf-8'))
    chosen = inventory['timelines'] if args.ordinals == 'all' else [
        t for t in inventory['timelines'] if t['ordinal'] in {int(x) for x in args.ordinals.split(',')}]
    client, model = get_text_auxiliary_client('vision')
    if client is None or type(client).__name__ != 'GeminiNativeClient':
        raise RuntimeError('Verified Gemini native route is not active')
    result_dir = ART / 'av-analysis'
    result_dir.mkdir(exist_ok=True)
    for t in chosen:
        ordinal = t['ordinal']
        destination = result_dir / f'{ordinal:02d}.json'
        if destination.exists():
            saved = json.loads(destination.read_text(encoding='utf-8'))
            if saved['timeline_id'] != t['timeline_id']:
                raise RuntimeError('Existing analysis identity mismatch')
            print('EXISTING ANALYSIS', ordinal, flush=True)
            continue
        preview = json.loads((ART / f'preview-{ordinal:02d}.json').read_text(encoding='utf-8'))
        if preview['timeline_id'] != t['timeline_id'] or not preview['structure_unchanged']:
            raise RuntimeError('Unverified preview identity')
        raw = Path(preview['path'])
        small = raw.parent / 'analysis-960x540-15fps.mp4'
        if not small.exists():
            subprocess.run(['ffmpeg','-n','-i',str(raw),'-vf','fps=15,scale=960:540',
                '-c:v','libx264','-preset','veryfast','-crf','30','-c:a','aac','-b:a','64k',
                str(small),'-hide_banner','-loglevel','error'],check=True)
        meta = json.loads(subprocess.run(['ffprobe','-v','error','-show_streams',
            '-show_format','-of','json',str(small)],capture_output=True,text=True,check=True).stdout)
        if not any(s['codec_type']=='audio' for s in meta['streams']):
            raise RuntimeError('Analysis derivative lacks audio')
        expected = (t['end']-t['start'])/float(t['record_fps'])
        if abs(float(meta['format']['duration'])-expected)>0.15:
            raise RuntimeError('Analysis duration mismatch')
        if small.stat().st_size > 19_000_000:
            raise RuntimeError('Native inline video exceeds conservative limit')
        subs = [{'start':s['start'],'end':s['end'],'text':s['name']}
            for tr in t['tracks'] if tr['kind']=='subtitle' for s in tr['items']]
        prompt = (
            'Analyze the ACTUAL attached full MP4 and provide a Thai editorial review. '
            'Never claim exhaustive continuous picture or audio coverage from model sampling. '
            'Distinguish seen/heard evidence from subtitle inference and uncertainty. '
            'State whether audio really arrived; discuss existing music/game SFX and speech clarity. '
            'Preserve truth, Thai subtitles, 16:9 composition, original cuts/audio, no actual edits. '
            'Review opening/setup/turn/payoff/ending; do not force comedy where none exists. '
            'Return one JSON object with keys audio_available (boolean), coverage_limitations (list), '
            'observed_story (string), existing_sound (string), framing_notes (string), '
            'suggested_bgm_mood (string), cues (list). Each cue: relative_seconds (number), '
            'kind (sfx or illustration), observation (string), editorial_job (string), '
            'asset_search_terms (list), needs_parent_confirmation (true). '
            'Give 2–5 cues only when actual AV supports them, otherwise fewer/none with reasons. '
            'Timestamp precision is approximate and must be parent-refined, not invented exact frames. '
            'relative_seconds MUST be numeric TOTAL seconds, e.g. 82.0 for 01:22, NEVER 1.22. '
            'If unsure of time, omit the cue instead of guessing. '
            'Do not invent exact asset filenames, rights, duration, gains, preset transforms. '
            'Use Inspector Video Preset vdo as future placement constraint; intentional user '
            'overlay on avatar is not automatically a defect. '
            f'Target ID={t["timeline_id"]}; name={t["name"]}; duration={expected:.3f}s. '
            'Subtitle timing references are absolute 60fps record frames, not audio evidence: '
            + json.dumps(subs,ensure_ascii=False))
        data = 'data:video/mp4;base64,' + base64.b64encode(small.read_bytes()).decode('ascii')
        response = request_with_retry(lambda: client.chat.completions.create(model=model,
            messages=[{'role':'user','content':[{'type':'text','text':prompt},
                {'type':'image_url','image_url':{'url':data}}]}],
            temperature=0.1,timeout=240,**generation_options()))
        text = response.choices[0].message.content or ''
        destination.with_suffix('.response.json').write_text(json.dumps({
            'finish_reason': response.choices[0].finish_reason, 'raw_content': text
        }, ensure_ascii=False, indent=2), encoding='utf-8')
        clean = text.strip()
        if clean.startswith('```'):
            clean = clean.split('\n',1)[1].rsplit('```',1)[0].strip()
        try:
            parsed = json.loads(clean)
        except ValueError:
            parsed = None
        if not isinstance(parsed,dict):
            destination.with_suffix('.failed.txt').write_text(text,encoding='utf-8')
            raise RuntimeError('Model did not return usable JSON; response retained')
        if not isinstance(parsed.get('audio_available'),bool) or not isinstance(parsed.get('cues'),list):
            raise RuntimeError('Model response lacks coverage fields')
        accepted, rejected = partition_cues(parsed['cues'], expected)
        parsed['cues'] = accepted
        parsed['rejected_cues'] = rejected
        for cue in parsed['cues']:
            cue['needs_parent_confirmation'] = True
        result = {'ordinal':ordinal,'timeline_id':t['timeline_id'],'name':t['name'],
            'provider':'gemini','model':model,'route':'native inlineData video/mp4 via existing client',
            'preview_path':str(raw),'analysis_derivative':str(small),'ffprobe':meta,
            'review_status':'provider_av_analysis_pending_parent_qc',
            'coverage_warning':'Model-based video/audio analysis, not independently proved continuous viewing/listening',
            'analysis':parsed}
        destination.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
        print('AV ANALYSIS SAVED',ordinal,str(destination),flush=True)

if __name__ == '__main__':
    main()
