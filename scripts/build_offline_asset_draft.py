"""Local asset shortlist and human review player; not an executable placement plan."""
import html
import json
import os
import subprocess
from pathlib import Path

ART = Path(__file__).resolve().parents[1] / '.hermes/artifacts/enrichment-review-2026-10-06-live2'
OUT = ART / 'offline-review'


def search_terms(text):
    # Text-only search hints, not observed emotions or a verified punchline.
    if any(word in text for word in ('เฮ้ย', 'ตกใจ', 'โอ้')):
        return ['ตกใจ', 'shocked', 'surprised']
    if any(word in text for word in ('ทำไม', 'งง', 'หาย')):
        return ['งง', 'confused', 'what']
    if 'ขำ' in text:
        return ['ขำ', 'laugh', 'ตบมุก']
    if 'ตาย' in text:
        return ['เศร้า', 'sad', 'crying']
    if 'ดีนะ' in text:
        return ['ดีใจ', 'happy', 'ding']
    return []


def choose_points(rows):
    selected = []
    for row in sorted(rows, key=lambda r: r['relative_start_seconds']):
        if search_terms(row['text']) and (not selected or row['relative_start_seconds'] - selected[-1]['relative_start_seconds'] >= 20):
            selected.append(row)
        if len(selected) == 3:
            break
    return selected


def main():
    inv = json.loads((ART / 'inventory.json').read_text(encoding='utf-8'))
    assets = json.loads((ART / 'assets.json').read_text(encoding='utf-8'))['assets']
    allowed = {'.mp3', '.wav', '.m4a', '.ogg', '.gif', '.mp4', '.jpg', '.png'}
    existing = [a for a in assets if a['extension'] in allowed and Path(a['path']).is_file()]
    bgm = []
    deferred_bgm = []
    for a in existing:
        if a['kind'] != 'bgm':
            continue
        try:
            probe = subprocess.run(['ffprobe', '-v', 'error', '-show_format', '-of', 'json', a['path']],
                                   capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=15)
        except subprocess.TimeoutExpired:
            deferred_bgm.append({'path': a['path'], 'reason': 'ffprobe_timeout_no_verified_duration'})
            continue
        if probe.returncode != 0:
            deferred_bgm.append({'path': a['path'], 'reason': 'ffprobe_failed_no_verified_duration'})
            continue
        meta = json.loads(probe.stdout)
        bgm.append({'name': a['name'], 'path': a['path'], 'duration_seconds': float(meta['format']['duration']),
                    'rights_status': 'unknown', 'status': 'audition_required_not_selected'})
    plans = []
    for tl in inv['timelines']:
        packet = json.loads((OUT / f'{tl["ordinal"]:02d}' / 'packet.json').read_text(encoding='utf-8'))
        if packet['timeline_id'] != tl['timeline_id']:
            raise RuntimeError('Packet ID mismatch')
        points = []
        for cue in choose_points(packet['candidate_review_points']):
            terms = search_terms(cue['text'])
            candidates = {}
            for kind in ('sfx', 'illustration'):
                matched = [a for a in existing if a['kind'] == kind and any(t in a['name'].lower() for t in terms)]
                # Filename match is a shortlist only; never guess an exact sound/meaning.
                candidates[kind] = [{'name': a['name'], 'path': a['path'], 'rights_status': 'unknown',
                                      'status': 'filename_match_only_needs_audition'} for a in matched[:2]]
            points.append({**cue, 'search_terms': terms, 'asset_candidates': candidates,
                           'decision': 'pending', 'exact_accent_frame': None,
                           'gain_db': None, 'status': 'draft_not_authorized_for_append'})
        plans.append({'ordinal': tl['ordinal'], 'timeline_id': tl['timeline_id'], 'name': tl['name'],
                      'preview_path': packet['preview_path'], 'duration_seconds': packet['duration_seconds'],
                      'cue_points': points, 'bgm_candidates': [a for a in bgm if a['duration_seconds'] >= packet['duration_seconds']],
                      'overlay_constraint': 'User preset vdo; not loaded/captured/verified in this task',
                      'freshness': 'live_content_verification_required',
                      'status': 'draft_only_no_timeline_mutations'})
    result = {'route': 'offline only; no media API', 'timelines': plans, 'deferred_bgm': deferred_bgm,
              'limitations': ['Subtitle keywords do not prove emotions or funny timing.',
                              'No automatic gains: mixed-audio measurements are not isolated dialogue loudness.',
                              'BGM candidates verified for file duration only; not selected or license cleared.',
                              'No Resolve connection or edits in this script.']}
    (OUT / 'asset-draft.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    blocks = ['<!doctype html><meta charset="utf-8"><title>ตรวจจุดเอฟเฟกต์ออฟไลน์</title>',
              '<style>body{background:#181818;color:#eee;font:16px sans-serif;margin:24px}video{width:min(900px,100%)}button,select{padding:8px;margin:4px}section{border-top:1px solid #555;padding:20px 0}li{margin:12px 0}small{color:#bbb}</style>',
              '<h1>ตรวจจุดเอฟเฟกต์ออฟไลน์ — แผนร่าง</h1>',
              '<p>กดดู–ฟัง ±3 วินาทีรอบจุดจากซับ เลือกเก็บ/ตัด/แก้เวลา และส่งออกบันทึกเมื่อจบ ไม่มีการเรียก API หรือแก้ Resolve</p>',
              '<p>ไฟล์ต้องอยู่ในโฟลเดอร์เดิม เปิดด้วย Chrome/Edge; หากเสียงซ้ำหรือมุกไม่ชัดให้เลือกตัด ไม่ต้องเติมเอฟเฟกต์ทุกคลิป</p>',
              '<button onclick="exportReview()">บันทึกผลตรวจเป็น JSON</button>']
    for tl in plans:
        n = tl['ordinal']
        video = os.path.relpath(tl['preview_path'], OUT).replace('\\', '/')
        blocks += [f'<section><h2>{n:02d} — {html.escape(tl["name"])}</h2>',
                   f'<video id="video-{n}" controls preload="none" src="{html.escape(video)}"></video>', '<ol>']
        for k, cue in enumerate(tl['cue_points']):
            when = cue['relative_start_seconds']
            asset_text = '; '.join(f'{kind}: '+ ', '.join(a['name'] for a in items) for kind, items in cue['asset_candidates'].items())
            blocks.append(f'<li><button onclick="playWindow({n},{when})">▶ {when:.3f}s</button> {html.escape(cue["text"])}<br><small>{html.escape(asset_text or "ยังไม่มี asset ที่ชื่อเข้ากัน")}</small><br><select id="decision-{n}-{k}"><option value="pending">ยังไม่ตรวจ</option><option value="keep">เก็บเป็น candidate (ยังไม่วาง)</option><option value="reject">ตัดออก</option><option value="retime">ต้องแก้เวลา</option></select><input id="note-{n}-{k}" placeholder="เหตุผล / เวลาที่ถูกต้อง" size="48"></li>')
        if not tl['cue_points']:
            blocks.append('<li>ไม่มีจุดจากซับที่เพียงพอ — ไม่ฝืนเพิ่มเอฟเฟกต์ ต้องดูคลิปจริงเพื่อหา visual-only beat</li>')
        blocks += ['</ol>', f'<details><summary>BGM ที่ยาวพอ {len(tl["bgm_candidates"])} ไฟล์ — ต้องฟังก่อนเลือก</summary><ul>']
        blocks += [f'<li>{html.escape(a["name"])} · {a["duration_seconds"]:.1f}s · สิทธิ์ยังไม่ยืนยัน</li>' for a in tl['bgm_candidates']]
        blocks += ['</ul></details></section>']
    payload = json.dumps(result, ensure_ascii=False).replace('<', '\\u003c')
    javascript = """function playWindow(n,t){
 const v=document.getElementById('video-'+n);
 document.querySelectorAll('video').forEach(x=>{if(x!==v)x.pause()});
 const stop=()=>{if(v.currentTime>=Math.min(v.duration,t+3)){v.pause();v.removeEventListener('timeupdate',stop)}};
 if(v._reviewStop)v.removeEventListener('timeupdate',v._reviewStop);
 v._reviewStop=stop;v.addEventListener('timeupdate',stop);
 v.currentTime=Math.max(0,t-3);v.play().catch(e=>alert(e.message));
}
function exportReview(){
 const out=JSON.parse(JSON.stringify(draft));
 out.timelines.forEach(t=>t.cue_points.forEach((c,k)=>{
 c.decision=document.getElementById('decision-'+t.ordinal+'-'+k).value;
 c.reviewer_note=document.getElementById('note-'+t.ordinal+'-'+k).value;
 }));
 out.status='human_notes_not_automatic_edit_authorization';
 const url=URL.createObjectURL(new Blob([JSON.stringify(out,null,2)],{type:'application/json'}));
 const a=document.createElement('a');a.href=url;a.download='offline-review-decisions.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),2000);
}
"""
    blocks += ['<script>const draft=' + payload + ';\n' + javascript + '</script>']
    (OUT / 'cue-review.html').write_text('\n'.join(blocks), encoding='utf-8')
    (OUT / 'cue-review.js').write_text('const draft=' + payload + ';\n' + javascript, encoding='utf-8')
    print(json.dumps({'timelines': len(plans), 'draft_cue_points': sum(len(t['cue_points']) for t in plans),
                      'checked_bgm_files': len(bgm), 'review_path': str((OUT/'cue-review.html').resolve())}, ensure_ascii=False))


if __name__ == '__main__':
    main()
