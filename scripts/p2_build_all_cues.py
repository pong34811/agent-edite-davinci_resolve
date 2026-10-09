"""Turn reviewed per-timeline cue specs into measured cue sheets for p2 (offline, no Resolve).
Input : cue-specs/NN.json  {"ordinal","cues":[{"kind","file","frame","reason"}]}
Output: all-cues.json (same schema as sample-cues.json) + all-cues.md
BGM is chosen only from the user-approved list; SFX/GIF rights stay unconfirmed.
Run from repo root: python -m scripts.p2_build_all_cues
"""
from __future__ import annotations
import json
from pathlib import Path

from scripts.p2_build_sample_cues import ART, SFX, GIF, BGM, mean_db, duration

DONE = {1, 19, 23}
BATTLE = ('ศึก', 'ปะทะ', 'บอส', 'ไฟลุก', 'ศัตรู', 'บุก', 'แพ้', 'ป้องกัน', 'ด่านหิมะ')
MIN_GAP = 150  # frames (2.5 s) between SFX cues; GIFs may share an SFX frame
START_MIN = 180


def pick_bgm(name):
    names = {p.name: p for p in BGM.iterdir()}
    top50 = next(n for n in names if n.startswith('Top 50 NoCopyrightSounds'))
    if 'strinova' in name:
        return 'Gaming Music 2023 ♫ 1 Hour Gaming Music Mix ♫ Copyright Free Music.mp3'
    if 'Minecraft' in name:
        return '2025-02-04_-_Wishing_Well_-_www.FesliyanStudios.com_.mp3'
    if 'Becastled' in name and any(k in name for k in BATTLE):
        return top50
    return 'NCSน่ารัก.mp3'


def main():
    inv = json.loads((ART / 'inventory.json').read_text(encoding='utf-8'))
    out = {'schema_version': 1, 'status': 'proposal_pending_review',
           'rights_status': 'sfx_gif_unconfirmed; bgm user-approved list only',
           'evidence': 'subtitle (ASR) derived; not verified by watching/listening', 'timelines': []}
    for t in inv['timelines']:
        o = t['ordinal']
        if o in DONE:
            continue
        spec_path = ART / 'cue-specs' / f'{o:02d}.json'
        row_problems = []
        if not spec_path.is_file():
            spec = {'cues': []}
            row_problems.append('missing spec file')
        else:
            spec = json.loads(spec_path.read_text(encoding='utf-8'))
            if spec.get('ordinal') != o:
                row_problems.append('spec ordinal mismatch')
        fps = float(t['record_fps'])
        length = (t['end'] - t['start']) / fps
        a1 = next(i for tr in t['tracks'] if tr['kind'] == 'audio' for i in tr['items'])
        subs = {(i['start'], i['end']): i['name'] for tr in t['tracks'] if tr['kind'] == 'subtitle' for i in tr['items']}
        mixed = mean_db(a1['media_path'], (a1.get('source_start') or 0) / fps, length)
        bgm_name = pick_bgm(t['name'])
        bgm_path = BGM / bgm_name
        bgm_len = duration(bgm_path)
        bgm_mean = mean_db(bgm_path, None, length)
        row = {'ordinal': o, 'timeline_id': t['timeline_id'], 'name': t['name'], 'fps': fps,
               'start': t['start'], 'end': t['end'], 'length_s': round(length, 2), 'source_mean_db': mixed,
               'cues': [], 'problems': row_problems, 'note': spec.get('note')}
        if not bgm_len or bgm_len < length or mixed is None or bgm_mean is None:
            row['problems'].append('BGM unreadable/too short or source level unreadable')
        row['bgm'] = {'path': str(bgm_path), 'duration_s': bgm_len, 'record_start': t['start'],
                      'record_end': t['end'], 'mean_db': bgm_mean,
                      'gain_db': None if mixed is None or bgm_mean is None else round(max(-60, min(-12, mixed - 20 - bgm_mean)), 1),
                      'fade_in_frames': round(0.5 * fps), 'fade_out_frames': round(fps)}
        seen, sfx_frames, gif_ranges = set(), [], []
        for c in sorted(spec.get('cues', []), key=lambda c: (c['frame'], c['kind'])):
            kind, name, frame = c['kind'], c['file'], int(c['frame'])
            path = (SFX if kind == 'sfx' else GIF) / name
            cue = {'kind': kind, 'path': str(path), 'record_start': frame, 'reason': c['reason'],
                   'subtitle': next((s for (a, b), s in subs.items() if a <= frame < b), None)}
            d = duration(path) if path.is_file() and kind in ('sfx', 'gif') else None
            if kind not in ('sfx', 'gif') or d is None:
                row['problems'].append(f'{name}: bad kind or missing/unreadable file')
                continue
            if name in seen:
                row['problems'].append(f'{name}: used twice in one timeline')
            seen.add(name)
            if frame < START_MIN:
                row['problems'].append(f'{name}: frame {frame} < {START_MIN}')
            if kind == 'gif':
                hold = min(d, 2.5)
                cue.update(source_duration_s=d, hold_s=round(hold, 2), record_end=frame + round(hold * fps))
                if hold < 1.5:
                    row['problems'].append(f'{name}: GIF only {d:.2f}s')
                if any(frame < b and cue['record_end'] > a for a, b in gif_ranges):
                    row['problems'].append(f'{name}: GIF overlaps another GIF')
                gif_ranges.append((frame, cue['record_end']))
            else:
                hold = min(d, 1.0)
                cue.update(source_duration_s=d, record_end=frame + round(hold * fps))
                m = mean_db(path, None, min(d, 3.0))
                cue['mean_db'] = m
                if m is None or m < -50:
                    row['problems'].append(f'{name}: level unreadable/near-silent ({m} dB)')
                cue['gain_db'] = None if mixed is None or m is None else round(max(-60, min(-6, mixed - 6 - m)), 1)
                if any(abs(frame - f) < MIN_GAP for f in sfx_frames):
                    row['problems'].append(f'{name}: SFX closer than 2.5s to another SFX')
                sfx_frames.append(frame)
            if cue['record_end'] > t['end']:
                row['problems'].append(f'{name}: cue exceeds timeline end')
            row['cues'].append(cue)
        out['timelines'].append(row)
    (ART / 'all-cues.json').write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')
    lines = ['# Cue sheet ที่เหลือ (ข้อเสนอ)', '']
    for r in out['timelines']:
        lines += [f"## #{r['ordinal']} {r['name']} ({r['length_s']}s)",
                  f"- BGM `{Path(r['bgm']['path']).name[:40]}` gain {r['bgm']['gain_db']} dB" + (f" | หมายเหตุ: {r['note']}" if r['note'] else '')]
        for c in r['cues']:
            ex = f"gain {c['gain_db']} dB" if c['kind'] == 'sfx' else f"ถือ {c['hold_s']}s"
            lines.append(f"- {c['record_start'] / r['fps']:6.1f}s f{c['record_start']} **{c['kind'].upper()}** `{Path(c['path']).name}` {ex} - {c['reason']}")
        lines += [f'- ⚠ {p}' for p in r['problems']] + ['']
    (ART / 'all-cues.md').write_text('\n'.join(lines), encoding='utf-8')
    n_sfx = sum(c['kind'] == 'sfx' for r in out['timelines'] for c in r['cues'])
    n_gif = sum(c['kind'] == 'gif' for r in out['timelines'] for c in r['cues'])
    print(f"timelines {len(out['timelines'])} sfx {n_sfx} gif {n_gif} problems {sum(len(r['problems']) for r in out['timelines'])}")


if __name__ == '__main__':
    main()
