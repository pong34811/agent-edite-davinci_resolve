---
name: vtuber-thumbnail-qc
description: QC Thai VTuber YouTube thumbnails with scored fix lists.
version: 0.1.0
author: Hermes
metadata:
  hermes:
    tags: [YouTube, Thumbnail, VTuber, Thai, QC, Design-Review]
---

# VTuber Thumbnail QC (Thai Audience)

Acts as Senior YouTube Thumbnail QC Director + VTuber Creative Director + Thai Audience Specialist: audits a finished (or draft) thumbnail against the clip content, the VTuber's identity, Thai typography, and mobile feed behaviour, then returns a fixed-format Thai report with severity-ranked, actionable fixes and a /100 score. It does NOT judge "pretty vs not pretty" and does NOT render or edit the image itself (hand fixes to the design/compositor workflow). Preview generation needs Python + Pillow only.

## When to Use

- "QC ปก", "ตรวจปกคลิป", "ตรวจ thumbnail", "ปกนี้ใช้ได้ไหม", "รีวิวปก VTuber"
- User sends a thumbnail (optionally + title, timeline, transcript, character ref, brand guide, old thumbnails)
- A/B/C thumbnail comparison, or "which moment should be the thumbnail?"
- Final gate before export/upload of a VTuber cover
- **Automatically, without being asked**, right after any thumbnail build finishes (davinci-thumbnails skill, `python -m cli.build`, Canva export) — see "Auto-QC after a build"

## Prerequisites

- `vision_analyze` for viewing images (required — never QC from filename/description alone).
- Python with Pillow for `scripts/qc_previews.py` (in the agent-thumbnail repo: `requirements.txt`).
- Optional context: title, timeline/transcript, character reference, channel's previous thumbnails.

## How to Run

1. Generate real test previews instead of "imagining" mobile/grayscale/squint — invoke through the `terminal` tool:
   `python <skill_dir>/scripts/qc_previews.py <thumb.jpg> [B.jpg C.jpg ...] --out <scratch>/thumb-qc`
2. `vision_analyze` the original at full size, then each preview (`*_mobile.png`, `*_gray.png`, `*_squint.png`, `*_badge.png`, `feed_sheet.png`). Use `region` to zoom on face, hair edges, hands, and every Thai text line.
3. Read `tech_report.json` for resolution / ratio / file size / mode.
4. Load the checklist: `skill_view(name="vtuber-thumbnail-qc", file_path="references/qc-checklist.md")`.
5. Write the answer using `templates/qc-report.md` (all 12 sections, in Thai).

## Quick Reference

- Preview script: `scripts/qc_previews.py` → mobile 10%/20%, grayscale, squint, duration-badge/Shorts danger overlay, feed sheet, `tech_report.json`
- Checklist (23 steps): `references/qc-checklist.md`
- Report skeleton + A/B/C comparison + 3-concept block: `templates/qc-report.md`
- Score: Character 15 · Expression 10 · Composition 10 · Text Readability 10 · Thai Typography 10 · Contrast 10 · Color 5 · Content Relevance 10 · Curiosity 10 · Mobile 5 · Brand 5 = 100
- Bands: 90–100 ready · 80–89 minor fixes · 70–79 usable, fix · 60–69 fix before publish · <60 rework
- Severity: 🔴 CRITICAL (must fix) · 🟠 IMPORTANT (hurts CTR) · 🟡 OPTIONAL (polish)
- Clickbait class: GOOD CURIOSITY · BORDERLINE · MISLEADING
- Landscape: 16:9, ≥1280×720; keep faces/text/logo out of bottom-right duration badge

## Procedure

1. **Content match first** (checklist step 1). If timeline/transcript exists, list candidate moments with timestamps and pick the 1–3 strongest; say whether the current thumbnail uses the best one.
2. **Character** (step 2): size, face, eyes, expression strength, pose, silhouette vs background, accuracy vs reference (hair/eye colour, outfit, accessories, horns/ears), hands/fingers, AI artifacts, awkward crops.
3. **Composition & space** (steps 3–4): main/secondary focus, eye flow, hierarchy; enforce **1 Thumbnail = 1 Main Idea**; with multiple characters name main vs supporting.
4. **Thai text** (steps 5–6): spell-check every word (consonant, vowel, tone mark, spacing, transliteration, game/character names) — load `thai-proofread` skill if unsure. Check stacked marks (สระบน/ล่าง, วรรณยุกต์) colliding or eaten by thick outline; target 1-second read, short punchy hook.
5. **Contrast / colour / background / extras** (steps 7–10): every arrow, circle, emoji, glow must have a job, else recommend deletion.
6. **Tests on real previews** (steps 11–15): safe area & badge, mobile 10–20%, grayscale, squint (2–4 blobs), first-1-second "what is this clip about?".
7. **Audience & marketing** (steps 16–22): curiosity gap (Understandable + Curious), repetition vs old thumbnails, brand identity, natural Thai wording (no translated-English feel), title pair (**Thumbnail = Emotion/Question, Title = Context**), clickworthiness among 10–20 feed neighbours, clickbait class.
8. **Technical** (step 23): resolution, compression, banding, halo, jagged cutout around hair tips/ears/horns/accessories/fingers.
9. Score, assign severities, then write the **prioritised export fix list** with concrete verbs + numbers (enlarge/shrink/move/delete/add/recolour/re-word, %, px, position).
10. Multiple versions → QC each with the same rubric, then the Comparison block. Weak thumbnail → 3 new concepts (Character/Emotion, Story/Situation, Minimal High-Impact) with Photoshop/Canva-ready layout.

### Auto-QC after a build

1. Trigger: every cover in the job is exported and `python -m cli.verify` (repo) passes. Don't wait for the user to ask.
2. Run `scripts/qc_previews.py` on ALL final JPGs in one call (feed sheet doubles as the repetition check, step 17); use the job's hook, timeline/subtitle and `delivery-manifest.json` as content evidence.
3. 1–3 covers → full 12-section report each. 4+ covers → one summary table (file · score · CRITICAL count · top fix) plus full reports only for covers with any 🔴 or score < 80; for large sets split covers across `delegate_task` children (same rubric, return the table row + report).
4. Fix every 🔴 CRITICAL, rebuild, re-verify, re-QC only the fixed covers; loop until none remain. Can't fix (missing asset/expression)? Stop and report — never mark it passed.
5. Package/deliver only after QC passes; include the QC summary in the handoff.

## Pitfalls

- Never flatter; never critique from personal taste — every point needs a reason tied to clarity, CTR, accuracy, or brand.
- Banned vague fixes: "ทำให้เด่นขึ้น", "ปรับให้ดีขึ้น". Write e.g. "ขยายใบหน้า VTuber ~20–30% และเลื่อนซ้ายให้ดวงตาอยู่ 1/3 บน".
- Don't add clutter (arrows/emoji/circles) to chase CTR; don't push mystery so far the clip becomes unreadable.
- Can't verify something (event in clip, correct outfit without reference)? Write "ไม่สามารถยืนยันจากข้อมูลที่มี" — never guess.
- Thai readability at thumbnail size is tested on `*_mobile.png`, not the full-res image; thick strokes that look fine at 1920px often swallow ั ิ ่ ้ at 168px.
- The badge overlay is an approximation of YouTube's duration badge position, not pixel-exact; treat overlap as WARNING unless key content sits squarely under it.
- On Windows/git-bash pass a native `--out` path (e.g. `C:/Users/<you>/AppData/Local/hermes/cache/scratch/thumb-qc`); `$TMPDIR`/`/tmp` silently lands in `C:\tmp`.
- Score is secondary — the fix list is the deliverable.
- In the agent-thumbnail repo, house conventions (AGENTS.md: hook 1–4 words, `#EC1C24` red/gold with ~8% black stroke, avatar right 35–50%, 0px-blur gameplay + left gradient mask, Shorts safe zone avoids bottom 25% / right 15%) count as the brand guide; `python -m cli.verify` covers the technical gate.

## Verification

`python <skill_dir>/scripts/qc_previews.py <thumb.jpg> --out <dir>` prints the tech report and the list of preview files; the final answer must contain all 12 template sections, a /100 total that equals the sum of the 11 sub-scores, and ≥3 alternative Thai texts when text changes are recommended.
