# CTC retime delivery: verify -> fix -> variant -> QC

Proven 2026-11-20 on Laffy แนะนำตัว 3 นาที (146.9 s @ 30 fps, 151 -> 150 cues).
Evidence: `docs/channels/laffy.md`, `scripts/scratch/laffy_intro/` (gitignored),
`edit\v2\sync\` artifacts. Load this when a Whisper- or Descript-timed Thai
subtitle track must be verified against the audio and re-delivered.

## Gate: a Whisper-timed track is NOT verified

- Second CTC run on the intro found 35/151 starts off by > 0.2 s: worst 1.3 s
  early (`อะไรก็ตาม` @ 58.1 s, shown during an `อ่าม` filler before the word)
  and 1.07 s late (`มีผู้ชายคน` @ 25.5 s).
- A frame readback proves track == SRT, never SRT == speech. Run the CTC check
  before calling any Whisper-timed track synced.

## 1. Measure (read-only on footage)

- Extract 16 kHz mono WAV from the rendered source with ffmpeg (new scratch
  file; source media stays read-only).
- 10 ms RMS map -> `rms_db_10ms.npy`; speech = > -40 dB. `sync_check.py [TH]`
  closes gaps < 80 ms, drops blips < 50 ms, then flags per cue: appears > 0.2 s
  before speech, starts > 0.15 s after speech began (uncovered), silence > 0.4 s
  inside. Read each flag before calling it a miss (mid-cue pauses, -37 dB blips).
- `forced_align.py`: `airesearch/wav2vec2-large-xlsr-53-th` (HF, Thai char
  vocab, 20 ms frames), `torchaudio.functional.forced_align`, 20 s chunks on
  GPU -> `aligned_cues.json` with `a_s`, `a_e`, `score` per cue. Map Latin
  names to spoken Thai and drop `ๆ` before aligning.

## 2. Text suspects: greedy decode + candidate scoring

- Greedy CTC decode per cue -> `ctc_greedy.json`; list cues where the decode
  differs from the Descript text.
- Score candidates with `local_ctc.py jobs.json` where jobs =
  `[[start_s, end_s, ["text1", "text2", ...]], ...]`. The intro copy is
  jobs-file ONLY (its docstring still shows `START END "text"`; the code reads
  `sys.argv[1]` as JSON). Model loads once; prints greedy decode, mean
  log-prob per token (higher = better fit) and word start times.
- Verified fixes: `นี้` -> `เนี้ย` (-8.3 vs -10.9), `บ้าง` -> `มั่ง`
  (-4.0 vs -6.3; `เป็นคลิปบ้าง` -7.3 vs -9.7).
- A near-tie is NOT evidence: keep the Descript text (`มีชื่อว่า` -4.2 vs
  `ไม่เชื่อว่า` -4.0; `ถ้าอยากทำอะนะ` vs `ทำมานะ`; `เป็นซะ`/`ไปซะ` equal).
  Record kept-uncertain cues in the channel doc.
- A real filler (`อ่า` @ 80.1 s) may stay uncaptioned when adding it would
  break the 14-char house rule.

## 3. Retime plan (`retime.py` -> `cues_v2.json`)

Constants: `FPS=30, LEAD=0.04, HOLD=0.25, GAP_JOIN=0.5, MAXF=45, MINF=8`.

- start = aligned start - LEAD, snapped back to an energy onset within 0.15 s;
  starts monotonic (>= previous start + 4 f).
- end = next start when the gap < GAP_JOIN, else aligned end + HOLD; cap MAXF,
  floor MINF.
- `score < 0.35` or no alignment -> keep the old time, unless a MANUAL_START
  from `local_ctc.py` word starts (`บ๊ายบาย` score 0.23 -> 145.87 s).
- Apply text fixes through an asserted old -> new map (assert the old text
  matches before replacing).
- Flash-cue merge: a 7-frame `น่ะ` merged into the previous cue ->
  `สัมผัสมันเฉยๆน่ะ` (12 visible chars together, <= 14); 151 -> 150 cues.
  Merge only when the combined text stays <= 14 chars.
- Assert no overlap and end > start; print shift stats (median, count
  |> 0.2 s|, max) and every changed cue before writing the plan.

## 4. Non-destructive apply (`apply_subs_v2.py` pattern)

Route: DRP snapshot -> DRT clone -> import as a NEW timeline -> full readback.
The source `_edit` timeline is never modified.

1. `export_verified(pm, p, <job>/edit/v2/sync/before_subs_v2.drp)` — verified
   backup BEFORE any mutation; check the project ID first.
2. Refuse if the `_v2` name already exists. Export the source timeline DRT
   (`EXPORT_DRT`, `EXPORT_NONE`); sleep ~1 s.
3. `clone_styled_subtitle_track(drt_src, drt_src, drt_out, cues)` — the style
   source is the timeline's OWN DRT, so the approved `Mitr Font` survives.
4. `mp.ImportTimelineFromFile(drt_out, {"importSourceClips": False})`;
   sleep ~2 s; `SetName("<variant>_v2")`.
5. Snapshot BOTH timelines and diff: every video/audio track item — name,
   start/end relative to `GetStartFrame()`, `GetLeftOffset()`, `AudioVolume`
   (audio), V2 Fusion Transform Size/Center rounded to 6 dp (zoom adjustment
   clips). The diff must be empty (V1-V3, A1-A3 intact).
6. Subtitle readback: the (start, end, text) list must equal `cues_v2.json`
   exactly (150 cues), not just the count.
7. `SaveProject()`; restore the entry timeline and its timecode.

## 5. Render + deliverable QC

- Burn-in subtitles (`render_qc.py` settings): `SelectAllFrames: True`,
  `ExportVideo/ExportAudio: True`, `ExportSubtitle: True`,
  `SubtitleFormat: "BurnIn"`, 1920x1080 @ 30. The intro deliverable was
  `render\laffy_intro_edit_v6.mov` (H.264 video + AAC).
- Require Complete status, then verify read-only:
  - ffprobe frame count == source (4407 frames).
  - Integrated loudness unchanged (-14.4 LUFS):
    `ffmpeg -i <out> -vn -af ebur128=peak=true -f null -`.
- Visual QC: 6 sample stills WITH burned-in subs —
  `python -m scripts.render_subtitle_stills --suffix _edit_v2 --frames <6 record frames> --out <dir>`
  (native still export omits subtitles). Include on-word and in-pause frames.
  Inspect with `vision_analyze`: caption visible, correct text, no overlap
  with cards/HUD, on-frame.

## 6. Record + release

- Channel doc (`docs/channels/<channel>.md`): new timeline name/id, cue count,
  text fixes with timestamps, merged cue, render name + specs, backup path,
  scripts used, and the kept-uncertain items.
- Bump `thai-subtitles-resolve` version, refresh the skill manifest, run the
  bundle check, write Thai release notes, publish via `scripts/release.py`.

## Pitfalls

- Do not retime the master timeline; the variant + DRP snapshot is the
  recoverable unit.
- ImportMedia is path-cached and Resolve stores SRT line breaks as U+2028 —
  see the main SKILL.md before any replace/re-import.
- Descript splits can put the previous sentence's `ครับ` at the start of the
  next cue (laffy_reason run); check cue boundaries against the decode.
- CTC keeps names/meaning where the greedy decode mishears; score candidates
  instead of trusting the decode string.
