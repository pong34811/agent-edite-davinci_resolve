"""Build the 3 sample cue sheets for p2 (offline; ffprobe/ffmpeg only, no Resolve writes).
Run from repo root: python -m scripts.p2_build_sample_cues
Cue frames are absolute timeline frames from the saved read-only inventory; durations/gains
are measured from the real files. Output is a proposal for user approval, not a placement.
"""
from __future__ import annotations
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / '.hermes' / 'artifacts' / 'enrichment-p2-2026-10-09'
SFX = Path(r'G:\My Drive\Projects\2.1_sfx')
GIF = Path(r'G:\My Drive\Projects\3.gif')
BGM = Path(r'G:\My Drive\Projects\1.bgm')
APPROVED_BGM = ('NCSน่ารัก.mp3', '2025-02-04_-_Wishing_Well_-_www.FesliyanStudios.com_.mp3',
                'Gaming Music 2023 ♫ 1 Hour Gaming Music Mix ♫ Copyright Free Music.mp3')

# ordinal -> bgm, [(kind, file, record_frame, reason)]
SAMPLES = {
    1: ('Gaming Music 2023 ♫ 1 Hour Gaming Music Mix ♫ Copyright Free Music.mp3', [
        ('sfx', 'gen ตกใจ.mp3', 3269, 'ซับ "ไอเหี้ยตัวเหี้ย" = ตกใจ/โดนจู่โจม'),
        ('gif', 'ตกใจ - shocked-cat.gif', 3269, 'รีแอคชันตกใจตรงจังหวะเดียวกัน'),
        ('sfx', 'Sad Trombone.mp3', 3901, 'ซับ "สองตายอ่ะในท่ำ" = ตายในรอบ'),
        ('gif', 'เศร้า - cute-teary.gif', 3901, 'รีแอคชันเศร้าตอนตาย'),
        ('sfx', 'Bruh meme.mp3', 4175, 'ซับ "ไม่เจอเว้ยแม่ง" = หงุดหงิดหาไม่เจอ')]),
    19: ('2025-02-04_-_Wishing_Well_-_www.FesliyanStudios.com_.mp3', [
        ('sfx', 'Minecraft Hurt.mp3', 1538, 'ซับ "ไม่หนาวตาย" = เกือบตาย/โดนความหนาว'),
        ('sfx', 'minecraft dead sound.mp3', 2220, 'ซับ "พี่ตายด้วย" = ตายในเกม'),
        ('gif', 'Anime - Shocked Reaction.gif', 2220, 'รีแอคชันตกใจตอนตาย'),
        ('sfx', 'Wowwww.mp3', 3330, 'ซับ "โอ้โห" = ทึ่ง')]),
    23: ('NCSน่ารัก.mp3', [
        ('sfx', 'Hellou!.mp3', 368, 'ซับ "โอเคทุกคน" = ทักทายเปิดไลฟ์'),
        ('gif', 'ทักทาย - hi-there.gif', 368, 'ทักทายผู้ชม'),
        ('sfx', 'HUH cat meme.mp3', 1044, 'ซับ "อะไรอ่ะ" = งงชื่อเกม'),
        ('gif', 'งง - mochi-cat-what.gif', 1044, 'รีแอคชันงง'),
        ('sfx', 'Crowd Laughter (short).mp3', 4099, 'ซับ "โลว์ไลฟ์มั้ง" = มุกตลก')]),
}


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')


def probe(path, entries):
    r = run(['ffprobe', '-v', 'error', '-show_entries', entries, '-of', 'json', str(path)])
    return json.loads(r.stdout or '{}')


def mean_db(path, start=None, dur=None):
    cmd = ['ffmpeg', '-hide_banner', '-nostats']
    if start:  # -ss 0 makes ffmpeg fail to decode short mp3s
        cmd += ['-ss', f'{start:.3f}']
    if dur:
        cmd += ['-t', f'{dur:.3f}']
    cmd += ['-i', str(path), '-vn', '-af', 'volumedetect', '-f', 'null', '-']
    m = re.search(r'mean_volume: (-?[\d.]+) dB', run(cmd).stderr)
    return float(m.group(1)) if m else None


def duration(path):
    d = probe(path, 'format=duration').get('format', {}).get('duration')
    return float(d) if d else None


def main():
    inv = json.loads((ART / 'inventory.json').read_text(encoding='utf-8'))
    out = {'schema_version': 1, 'status': 'proposal_pending_user_approval',
           'rights_status': 'sfx_gif_unconfirmed; bgm user-approved list only',
           'evidence': 'subtitle (ASR) derived; not verified by watching/listening', 'timelines': []}
    for ordinal, (bgm_name, cues) in SAMPLES.items():
        t = inv['timelines'][ordinal - 1]
        fps = float(t['record_fps'])
        length = (t['end'] - t['start']) / fps
        v1 = next(i for tr in t['tracks'] if tr['kind'] == 'audio' for i in tr['items'])
        subs = {(i['start'], i['end']): i['name'] for tr in t['tracks'] if tr['kind'] == 'subtitle' for i in tr['items']}
        src_start = (v1.get('source_start') or 0) / fps
        mixed = mean_db(v1['media_path'], src_start, length)
        bgm_path = BGM / bgm_name
        bgm_len = duration(bgm_path)
        row = {'ordinal': ordinal, 'timeline_id': t['timeline_id'], 'name': t['name'], 'fps': fps,
               'start': t['start'], 'end': t['end'], 'length_s': round(length, 2),
               'source_mean_db': mixed, 'cues': [], 'problems': []}
        if bgm_name not in APPROVED_BGM or not bgm_path.is_file() or not bgm_len or bgm_len < length:
            row['problems'].append('BGM not approved/missing/too short')
        bgm_mean = mean_db(bgm_path, 0, length)
        row['bgm'] = {'path': str(bgm_path), 'duration_s': bgm_len, 'record_start': t['start'],
                      'record_end': t['end'], 'mean_db': bgm_mean,
                      'gain_db': None if mixed is None or bgm_mean is None else round(max(-60, min(-12, mixed - 20 - bgm_mean)), 1),
                      'fade_in_frames': round(0.5 * fps), 'fade_out_frames': round(fps)}
        for kind, name, frame, why in cues:
            path = (SFX if kind == 'sfx' else GIF) / name
            c = {'kind': kind, 'path': str(path), 'record_start': frame, 'reason': why,
                 'subtitle': next((s for (a, b), s in subs.items() if a <= frame < b), None)}
            d = duration(path) if path.is_file() else None
            if d is None:
                row['problems'].append(f'{name}: missing/unreadable')
            elif kind == 'gif':
                c['source_duration_s'] = d
                hold = min(d, 2.5)
                c['hold_s'] = round(hold, 2)
                if hold < 1.5:
                    row['problems'].append(f'{name}: GIF only {d:.2f}s (<1.5s hold) -> choose another')
                c['record_end'] = frame + round(hold * fps)
            else:
                hold = min(d, 1.0)
                c['source_duration_s'] = d
                c['record_end'] = frame + round(hold * fps)
                m = mean_db(path, 0, min(d, 3.0))
                c['mean_db'] = m
                if m is None or m < -50:
                    row['problems'].append(f'{name}: level unreadable or near-silent ({m} dB) -> choose another')
                c['gain_db'] = None if mixed is None or m is None else round(max(-60, min(-6, mixed - 6 - m)), 1)
            if c.get('record_end', 0) > t['end']:
                row['problems'].append(f'{name}: cue exceeds timeline end')
            row['cues'].append(c)
        out['timelines'].append(row)
    (ART / 'sample-cues.json').write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')
    lines = ['# Cue ตัวอย่าง 3 ชุด (ข้อเสนอ รอผู้ใช้อนุมัติ)', '']
    for r in out['timelines']:
        lines += [f"## #{r['ordinal']} {r['name']}  ({r['length_s']}s, {r['fps']:.0f}fps, frames {r['start']}-{r['end']})", '',
                  f"- BGM: `{Path(r['bgm']['path']).name}` ครอบคลุมทั้งคลิป gain {r['bgm']['gain_db']} dB, fade-in {r['bgm']['fade_in_frames']}f / fade-out {r['bgm']['fade_out_frames']}f",
                  f"- ระดับเสียงต้นฉบับเฉลี่ย {r['source_mean_db']} dB", '']
        for c in r['cues']:
            sec = c['record_start'] / r['fps']
            extra = f"gain {c['gain_db']} dB" if c['kind'] == 'sfx' else f"ถือ {c['hold_s']}s (vdo)"
            lines.append(f"- {sec:6.1f}s (f{c['record_start']}) **{c['kind'].upper()}** `{Path(c['path']).name}` {extra} - {c['reason']} [ซับ: {c['subtitle']}]")
        lines += [''] + [f'- ⚠ {p}' for p in r['problems']] + ['']
    (ART / 'sample-cues.md').write_text('\n'.join(lines), encoding='utf-8')
    print('written', sum(len(r['problems']) for r in out['timelines']), 'problems')


if __name__ == '__main__':
    main()
