"""Write per-timeline subtitle dumps and asset candidate lists for cue drafting (offline).
Run from repo root: python -m scripts.p2_dump_cue_inputs
"""
from __future__ import annotations
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / '.hermes' / 'artifacts' / 'enrichment-p2-2026-10-09'
DONE = {1, 19, 23}  # already applied from the approved samples


def main():
    inv = json.loads((ART / 'inventory.json').read_text(encoding='utf-8'))
    out = ART / 'cue-input'
    out.mkdir(exist_ok=True)
    for t in inv['timelines']:
        if t['ordinal'] in DONE:
            continue
        fps = float(t['record_fps'])
        lines = [f"ordinal: {t['ordinal']}", f"name: {t['name']}", f"fps: {fps:.0f}",
                 f"timeline_frames: {t['start']}-{t['end']} ({(t['end'] - t['start']) / fps:.1f}s)",
                 'subtitles (start_frame end_frame | seconds | text) - ASR, contains errors:']
        subs = [i for tr in t['tracks'] if tr['kind'] == 'subtitle' for i in tr['items']]
        for i in subs:
            lines.append(f"{i['start']} {i['end']} | {i['start'] / fps:.1f}s | {i['name']}")
        (out / f"{t['ordinal']:02d}.txt").write_text('\n'.join(lines), encoding='utf-8')
    gifs = []
    for line in (ART / 'gif-probe.txt').read_text(encoding='utf-8').splitlines():
        m = re.match(r"\('(.+\.gif)', ([\d.]+),", line)  # gifs only: mp4 may carry audio
        if m:
            gifs.append(f'{m[1]}\t{m[2]}s')
    (out / 'gif-candidates.txt').write_text('\n'.join(gifs), encoding='utf-8')
    print('inputs', len(list(out.glob('[0-9]*.txt'))), 'gifs', len(gifs))


if __name__ == '__main__':
    main()
