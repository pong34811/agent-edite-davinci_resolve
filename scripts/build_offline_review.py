"""Offline preview review packets; no network, ASR, Resolve, or timeline writes."""
from __future__ import annotations
import argparse
import html
import json
import re
import subprocess
from pathlib import Path

ART = Path(__file__).resolve().parents[1] / '.hermes/artifacts/enrichment-review-2026-10-06-live2'
OUT = ART / 'offline-review'


def caption_map(row):
    fps = float(row['record_fps'])
    if fps <= 0:
        raise ValueError('Invalid timeline FPS')
    return [{'track': tr['index'], 'text': x['name'],
             'absolute_start_frame': x['start'], 'absolute_end_frame': x['end'],
             'relative_start_seconds': (x['start'] - row['start']) / fps,
             'relative_end_seconds': (x['end'] - row['start']) / fps}
            for tr in row['tracks'] if tr['kind'] == 'subtitle' for x in tr['items']]


def audio_metrics(log):
    def volume(label):
        found = re.search(label + r':\s*(-?[\d.]+|[-+]?inf)\s*dB', log)
        return float(found[1]) if found and 'inf' not in found[1] else None
    silences = []
    starts = re.findall(r'silence_start:\s*([\d.]+)', log)
    ends = re.findall(r'silence_end:\s*([\d.]+)\s*\|\s*silence_duration:\s*([\d.]+)', log)
    for start, (end, duration) in zip(starts, ends):
        silences.append({'start': float(start), 'end': float(end), 'duration': float(duration)})
    return {'mixed_mean_dbfs': volume('mean_volume'), 'mixed_max_dbfs': volume('max_volume'),
            'silences': silences, 'measurement_limit': 'Mixed preview audio, not isolated speech; no LUFS or intelligibility verdict'}


def run(args):
    return subprocess.run(args, capture_output=True, text=True, encoding='utf-8', errors='replace',
                          check=True, timeout=180)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--first', type=int, default=13)
    parser.add_argument('--last', type=int, default=49)
    args = parser.parse_args()
    inv = json.loads((ART / 'inventory.json').read_text(encoding='utf-8'))
    targets = [t for t in inv['timelines'] if args.first <= t['ordinal'] <= args.last]
    if not targets:
        raise RuntimeError('Empty selection')
    OUT.mkdir(exist_ok=True)
    collected = []
    for row in targets:
        ordinal = row['ordinal']
        dest = OUT / f'{ordinal:02d}'
        dest.mkdir(exist_ok=True)
        packet_path = dest / 'packet.json'
        if packet_path.exists():
            old = json.loads(packet_path.read_text(encoding='utf-8'))
            if old['timeline_id'] != row['timeline_id']:
                raise RuntimeError('Existing packet identity mismatch')
            if all(Path(f['path']).is_file() for f in old['sampled_frames']):
                collected.append(old)
                print('EXISTING OFFLINE PACKET', ordinal, flush=True)
                continue
        preview = json.loads((ART / f'preview-{ordinal:02d}.json').read_text(encoding='utf-8'))
        if preview['timeline_id'] != row['timeline_id'] or not preview['structure_unchanged']:
            raise RuntimeError('Preview identity mismatch')
        source = Path(preview['path'])
        meta = json.loads(run(['ffprobe', '-v', 'error', '-show_format', '-show_streams', '-of', 'json', str(source)]).stdout)
        duration = float(meta['format']['duration'])
        expected = (row['end'] - row['start']) / float(row['record_fps'])
        if abs(duration - expected) > 0.15:
            raise RuntimeError('Duration mismatch')
        if not any(s['codec_type'] == 'audio' for s in meta['streams']):
            raise RuntimeError('Preview missing audio')
        measured = run(['ffmpeg', '-hide_banner', '-i', str(source), '-vn', '-af',
                        'volumedetect,silencedetect=noise=-35dB:d=0.4', '-f', 'null', '-']).stderr
        (dest / 'audio-analysis.log').write_text(measured, encoding='utf-8')
        caps = caption_map(row)
        # Context + distributed samples. Captions only nominate candidate review times.
        times = {0.0, *(round((duration - 0.1) * n / 5, 3) for n in range(1, 6))}
        review_candidates = []
        terms = ('ตกใจ', 'ทำไม', 'เฮ้ย', 'โอ้', 'ตาย', 'ขำ', 'หาย', 'งง', 'ดีนะ')
        for cue in caps:
            matched = [term for term in terms if term in cue['text']]
            if matched and 0 <= cue['relative_start_seconds'] < duration:
                review_candidates.append({**cue, 'matched_terms': matched,
                                          'status': 'subtitle_inference_only_needs_picture_and_listening_review'})
        for cue in review_candidates[:6]:
            times.add(round(cue['relative_start_seconds'], 3))
        frames = []
        for n, when in enumerate(sorted(times), 1):
            frame = dest / f'frame-{n:02d}-{when:.3f}s.jpg'
            run(['ffmpeg', '-y', '-hide_banner', '-loglevel', 'error', '-ss', str(when),
                 '-i', str(source), '-frames:v', '1', '-vf', 'scale=960:-2', str(frame)])
            if not frame.is_file() or frame.stat().st_size == 0:
                raise RuntimeError('Missing sampled frame')
            frames.append({'relative_seconds': when, 'path': str(frame.resolve())})
        packet = {'ordinal': ordinal, 'timeline_id': row['timeline_id'], 'name': row['name'],
                  'preview_path': str(source), 'duration_seconds': duration, 'record_fps': row['record_fps'],
                  'route': 'offline ffprobe/ffmpeg + saved native subtitle snapshot; no media API',
                  'status': 'offline_evidence_prepared_not_final_audiovisual_QC',
                  'freshness': 'live_timeline_match_not_yet_verified',
                  'audio_metrics': audio_metrics(measured), 'captions': caps,
                  'candidate_review_points': review_candidates, 'sampled_frames': frames,
                  'limitations': ['Frames are samples, not continuous visual coverage.',
                                  'Audio measurements do not prove speech, music identity, humor, or asset timing.',
                                  'No ASR used: offline Thai smoke transcription was unreliable.',
                                  'No timeline edits or asset placements.']}
        packet_path.write_text(json.dumps(packet, ensure_ascii=False, indent=2), encoding='utf-8')
        collected.append(packet)
        print('OFFLINE PACKET SAVED', ordinal, 'frames', len(frames), flush=True)
        (OUT / 'index.json').write_text(json.dumps({'requested_ids': [t['timeline_id'] for t in targets],
            'collected_ids': [t['timeline_id'] for t in collected], 'complete': len(collected) == len(targets)}, indent=2), encoding='utf-8')
    # Read back and reconcile every packet instead of counting output messages.
    rows = [json.loads((OUT / f'{t["ordinal"]:02d}' / 'packet.json').read_text(encoding='utf-8')) for t in targets]
    if {r['timeline_id'] for r in rows} != {t['timeline_id'] for t in targets}:
        raise RuntimeError('Final coverage mismatch')
    blocks = ['<!doctype html><meta charset="utf-8"><title>Offline review</title>',
              '<style>body{background:#171717;color:#eee;font:16px sans-serif;margin:24px}img{width:320px}figure{display:inline-block;margin:6px}table{border-collapse:collapse}td{border:1px solid #666;padding:6px}</style>',
              '<h1>Offline review — หลักฐานเบื้องต้น ไม่ใช่ QC ที่ตรวจรับแล้ว</h1>',
              '<p>ภาพเป็นการสุ่มตัวอย่าง; เสียงวัดรวมจาก Preview; ซับเดิมไม่แก้ไข; ยังไม่ยืนยันตรงกับ Resolve ปัจจุบัน</p>']
    for row in rows:
        blocks += [f'<h2>{row["ordinal"]:02d} — {html.escape(row["name"])}</h2>',
                   f'<p>Timeline ID: {row["timeline_id"]} · {row["duration_seconds"]:.2f}s</p>',
                   f'<p>Mixed audio: {html.escape(str(row["audio_metrics"]))}</p>']
        for frame in row['sampled_frames']:
            rel = Path(frame['path']).relative_to(OUT).as_posix()
            blocks.append(f'<figure><img src="{html.escape(rel)}"><figcaption>{frame["relative_seconds"]:.3f}s</figcaption></figure>')
        blocks.append('<details><summary>ซับและเวลาเดิม</summary><table>')
        for cue in row['captions']:
            blocks.append(f'<tr><td>{cue["relative_start_seconds"]:.3f}–{cue["relative_end_seconds"]:.3f}s</td><td>{html.escape(cue["text"])}</td></tr>')
        blocks.append('</table></details>')
    (OUT / 'review.html').write_text('\n'.join(blocks), encoding='utf-8')
    print('OFFLINE REVIEW COMPLETE', len(rows), 'frames', sum(len(r['sampled_frames']) for r in rows), str((OUT / 'review.html').resolve()), flush=True)


if __name__ == '__main__':
    main()
