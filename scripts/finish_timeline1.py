"""Finish Timeline 1: set measured gains and fades, apply vdo values, verify."""
import json
import re
import subprocess
import time
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from scripts.resolve_common import connect_resolve
from scripts.apply_video_style import capture_style, apply_style_batch

ART = ROOT / '.hermes/artifacts/enrichment-review-2026-10-06-live2'


def asset_mean(path):
    result = subprocess.run(['ffmpeg', '-hide_banner', '-i', str(path), '-vn', '-af', 'volumedetect',
                             '-f', 'null', '-'], capture_output=True, text=True, errors='replace',
                            check=True, timeout=60)
    found = re.search(r'mean_volume:\s*(-?[\d.]+)\s*dB', result.stderr)
    if not found:
        raise RuntimeError('No measurable asset audio: ' + str(path))
    return float(found[1])


def main():
    pilot = json.loads((ART / 'pilot-offline-01.json').read_text(encoding='utf-8'))
    report = json.loads((ART / 'promotion' / '01.json').read_text(encoding='utf-8'))
    packet = json.loads((ART / 'offline-review' / '01' / 'packet.json').read_text(encoding='utf-8'))
    mixed = packet['audio_metrics']['mixed_mean_dbfs']
    if mixed is None:
        raise RuntimeError('Missing measured mixed level; refusing to invent gains')
    style = json.loads((ART / 'vdo-current-project.json').read_text(encoding='utf-8'))
    r = connect_resolve()
    if r is None:
        raise RuntimeError('Resolve unavailable')
    pm = r.GetProjectManager()
    p = pm.GetCurrentProject()
    o = next(p.GetTimelineByIndex(i) for i in range(1, p.GetTimelineCount() + 1)
             if p.GetTimelineByIndex(i).GetUniqueId() == pilot['source_timeline_id'])
    entry, page = p.GetCurrentTimeline(), r.GetCurrentPage()
    tc = entry.GetCurrentTimecode()
    p.SetCurrentTimeline(o)
    time.sleep(0.5)
    if p.GetCurrentTimeline().GetUniqueId() != pilot['source_timeline_id']:
        raise RuntimeError('Wrong active timeline')
    fps = float(o.GetSetting('timelineFrameRate'))
    by_id = {}
    for kind in ('video', 'audio'):
        for k in range(1, o.GetTrackCount(kind) + 1):
            for item in o.GetItemListInTrack(kind, k) or []:
                by_id[item.GetUniqueId()] = item
    done = []
    for entry_row in report['added']:
        item = by_id.get(entry_row['item_id'])
        if item is None:
            raise RuntimeError('Inserted item missing: ' + entry_row['kind'])
        if entry_row['kind'] == 'gif':
            apply_style_batch([item], style, [item.GetUniqueId()], apply=True)
            done.append({'kind': 'gif', 'zoom': item.GetProperty('ZoomX')})
        else:
            distance, cap = (20.0, -12.0) if entry_row['kind'] == 'bgm' else (6.0, -6.0)
            path = {'bgm': r'G:\My Drive\Projects\1.bgm\NCSน่ารัก.mp3',
                    'sfx': r'G:\My Drive\Projects\2.1_sfx\10 ตกใจฉาก 10.mp3'}[entry_row['kind']]
            gain = max(-60.0, min(cap, mixed - distance - asset_mean(path)))
            item.SetProperty('AudioVolume', float(gain))
            if abs(float(item.GetProperty('AudioVolume')) - gain) > 0.01:
                raise RuntimeError('Volume readback failed: ' + entry_row['kind'])
            span = item.GetEnd() - item.GetStart()
            fades = {'FadeIn': round(0.5 * fps) if entry_row['kind'] == 'bgm' else 0,
                     'FadeOut': round(fps) if entry_row['kind'] == 'bgm' else min(round(0.15 * fps), span)}
            item.SetFades(fades)
            if item.GetFades() != fades:
                raise RuntimeError('Fade readback failed: ' + entry_row['kind'])
            done.append({'kind': entry_row['kind'], 'volume_db': gain, 'fades': fades})
    if not pm.SaveProject():
        raise RuntimeError('SaveProject failed')
    p.SetCurrentTimeline(entry)
    time.sleep(0.5)
    if p.GetCurrentTimeline().GetUniqueId() == entry.GetUniqueId():
        entry.SetCurrentTimecode(tc)
        time.sleep(0.3)
    if r.GetCurrentPage() != page:
        r.OpenPage(page)
        time.sleep(1.0)
    report.update({'status': 'timeline1_completed', 'applied': done,
                   'restoration_verified': (p.GetCurrentTimeline().GetUniqueId() == entry.GetUniqueId()
                                            and r.GetCurrentPage() == page)})
    (ART / 'promotion' / '01.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'applied': done, 'restoration_verified': report['restoration_verified']},
                     ensure_ascii=False, indent=2), flush=True)


if __name__ == '__main__':
    main()
