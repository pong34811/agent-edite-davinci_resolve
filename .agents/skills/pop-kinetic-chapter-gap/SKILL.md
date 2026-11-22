---
name: pop-kinetic-chapter-gap
description: Give chapter cards a silent gap; rebuild the vertical cut.
version: 0.1.1
author: Hermes
license: MIT
platforms: [windows]
metadata:
  hermes:
    tags: [Resolve, HyperFrames, Chapters, Vertical, PopKinetic]
---

# Pop Kinetic Chapter Gap

Retrofit a finished Pop Kinetic explainer (full-screen CHAPTER cards on V3, continuous voice on A1) so every card plays in a silent gap and speech resumes only after the card has gone, then rebuild the 9:16 copy the same way and centre its graphics. It does not re-cut the content, re-transcribe, or re-style subtitles; the cut, cues and graphics keep their timing relative to the voice. Resolve scripting API through `scripts/resolve_common.py` plus HyperFrames renders through the `terminal` tool; the frame maths is `scripts/wipe_gap_plan.py`.

## When to Use

- "ตอนเปลี่ยนฉาก ... เปลี่ยนฉากให้เสร็จก่อน แล้วเริ่มต่อ" / "เสียงพูดเริ่มก่อนการ์ดจบ" / "ให้การ์ดเล่นเงียบ ๆ ก่อน"
- "ทำแนวตั้งใหม่ให้หน่อย" after the 16:9 got gaps, on an episode whose 9:16 copy predates them
- "รูปภาพประกอบย้ายให้อยู่ตรงกลาง" on a left-aligned 9:16 Pop Kinetic overlay
- Don't use for: a 0.5 s cut wipe (rejected look, see `house-style`), highlight cuts, or a timeline that already has gaps (ep2.5 onward were built with them).

## Prerequisites

- Resolve Studio 21.1 running with the project open; probe `resolve_control get_version` first (MCP-GAP: MCP import does not accept a patched `.drt`, so this workflow runs on the scripting API).
- `py -3.13` with PIL/numpy, `ffmpeg`/`ffprobe`, `npx hyperframes@0.8.191` cached.
- The episode's HyperFrames generator (Bunny Girl ep1: build_pop_overlays.py / build_pop_vertical.py in the gitignored one-off folder `scripts/scratch/bunny_pop/`; other episodes have their own) with `assets/fonts/Mitr-*.ttf` and `assets/gsap.min.js`. If the original project folder is gone, copy assets from any `.hermes/projects/bunny-girl-ep*/hf/`.
- Read `house-style` (CHAPTER card look, gap rule, centred 9:16 graphics) and `docs/channels/<channel>.md`.

## How to Run

Copy the working example into a new scratch folder and change its constants; invoke everything through the `terminal` tool.

```
py -3.13 -m scripts.scratch.bunny_ep1_gap.inv                        # read-only inventory of the current timeline
py -3.13 scripts/scratch/bunny_ep1_gap/pauses.py -40                 # 10 ms RMS map around every card
py -3.13 scripts/scratch/bunny_ep1_gap/build_pop_gap.py              # 16:9 overlays with the gap
py -3.13 scripts/scratch/bunny_ep1_gap/build_pop_vertical_gap.py     # 9:16 overlays (centred)
py -3.13 scripts/scratch/bunny_ep1_gap/render_gap.py [--v] [ids...]  # GAP_SUFFIX=_c for the centred re-render
py -3.13 -m scripts.scratch.bunny_ep1_gap.gap_edit baseline|patch|apply|verify   # GAP_VARIANT=v for 9:16
py -3.13 -m scripts.scratch.bunny_ep1_gap.swap_v3_centre            # swap overlays in place, no DRT round-trip
py -3.13 -m scripts.scratch.bunny_ep1_gap.promote                    # promote_v.py for the 9:16
py -3.13 -m scripts.scratch.bunny_ep4.render_full <timeline id> <out dir> <name> <w> <h>
py -3.13 scripts/scratch/bunny_ep1_gap/qc_render.py <render.mp4>
py -3.13 -m pytest -q tests/test_wipe_gap_plan.py
```

## Quick Reference

- `scripts/wipe_gap_plan.py`: `pick_cut(db, onset_s, gap_frames, fps)`, `item_shift`, `subtitle_shift`, `wipe_record`, `whoosh_record`, `wipe_ranges(wipes, chapter_starts, cuts, gap)`, `overlay_local`, `split_ranges`, `video_fillers`.
- Gap `G = 96` frames at 60 fps for a 1.55 s card; card exit ends at local 1.55 s.
- Overlay generator: `GAP = 1.6`, `CH_START_F` = each chapter's card/overlay start in ORIGINAL frames, `self.start = CH_START_F[n]/60`, `self.end = CH_START_F[n+1]/60`, `L(t) = t - start + shift`; `wipe()` runs with `shift = 0`, everything else with `shift = GAP`; `save()` duration = `end - start + gap`; `clip()`/`out()` clamp `b` to `self.end`.
- 9:16 centring CSS (zone x 100-980): `.slam{left:0;right:0;margin:0 auto;width:max-content;text-align:center;transform-origin:50% 100%}`, `.rc{left:100px;justify-content:center}` + `.rc>*{order:2} .rc>.head{order:0} .rc:not(.stk)::after{content:"";flex-basis:100%;height:0;order:1}` (drop `.head{margin-right:ZW}`), `.wtext{left:40px;right:40px;text-align:center}`, `.wears`/`.badge.rtop{left:0;right:0;margin:0 auto;width:max-content}`, single card `left:345px`, pair `left:100px`/`left:590px`.

## Procedure

1. Inventory with `inv.py`; record the timeline ID, every V3 overlay start, the V2 zoom windows, SFX/BGM starts and the cue list. Completion: `baseline.json` written and the current page/timeline/playhead saved.
2. Measure pauses (`pauses.py`): for each card find the last voice before it and the first onset after. Pick the cut with `pick_cut`; if the card's bound falls before a word ends, move the cut later inside the pause. Completion: every cut is inside a silent run; none is mid-word.
3. Choose each card's start separately from the cut: if the chapter's first cue starts before the cut, start the card at or before that cue (trim the previous overlay by the same frames, `out()` clamps its fade). Completion: shifted cue start >= card end.
4. Copy the generator, add `GAP`/`CH_START_F`, patch `L`, `wipe`, `save`, `clip`, `out` as in Quick Reference; run it and diff `STORYBOARD.md` against the delivered one. Completion: only the intended chapter bounds changed.
5. Render only the wiped chapters to NEW names (`chNN_gap.mov`); pixel-diff a mid-chapter frame of each against the old file at `local + shift`. Completion: mean diff < 0.01 and equal alpha pixel count.
6. `gap_edit baseline` (state + DRT + `.drp` backup via `backup_drp.export_verified`), `patch` (split V1/A1 at cuts, shift items by `item_shift`, cues by `subtitle_shift`, whoosh to `whoosh_record`, drop wiped V3 items, add `video_fillers`, extend the last BGM tail by `G*len(cuts)`), then `apply` (import as a NEW timeline, rename by ID, restore gains, append the gap overlays at `wipe_ranges`). Completion: `verify` prints 0 problems and `extra == planned`.
7. Render the test (`render_full`, burn-in subs), run `qc_render.py`, and inspect the wipe sheet with `vision_analyze`. Completion: no subtitle on any card, gaps ≈ -32 dB vs speech ≈ -16 dB, no black frames, loudness unchanged.
8. Restore page/timeline/playhead by hand (see Pitfalls), save, then promote only on the user's word: `promote.py` backs up, deletes the old timeline by ID, renames the variant, re-reads every track.
9. For the 9:16: `GAP_VARIANT=v` repeats steps 1-7 on the vertical timeline with `build_pop_vertical_gap.py` and `render_gap.py --v`. After import, render one frame WITH a subtitle and compare its position to the old render; if the `Mitr-short-001` position is gone, run `py -3.13 -m scripts.drt_clone_subtitle_style --timeline <variant> --new <variant>_mitr --styled .hermes/projects/bunny-girl-ep3/vertical/v916.drt --workdir <dir>` and promote that one.
10. Centring only (no timing change): edit the vertical CSS, regenerate, check layout with `snap_v.py chNN:<local seconds>` before rendering (alpha-column centre within ~30 px of 540), render all nine chapters as `chNN_c.mov` (`GAP_SUFFIX=_c`, three parallel `terminal` jobs of three ids), then `swap_v3_centre.py`. Completion: V3 items at the same ranges with the new names, every other track read back unchanged.

## Existing-media fallback when the generator is unavailable

Inspect the actual alpha overlay before choosing this route: its first 96 frames
must contain only the card/progress bar, with no early content graphics to lose.
On Resolve 21.1.0.17, the ep2 variant preserved existing media without an external
re-render: keep source 0–96 as the card in the new silent gap; hold clean source
frame 96 for 96 frames using native `SetSpeed` with Percentage 0 and both
RippleTimeline/StretchKeyframesToFit false; then play source 96 onward at the
voice-shifted time. This intentionally holds the progress bar for 1.6 s, rather
than replaying the card. Read back speed and exact ranges, and inspect a fresh
Resolve burn-in render of every card exit and held frame. Do not infer that all
overlays have a clean frame 96 or that all builds freeze identically.

Keep an outgoing subtitle on its outgoing speech segment: when it trails a cut
inside measured silence, trim only that silent tail rather than shifting the
whole outgoing cue to the next chapter. Patch each shifted cue's FieldsBlob
with `_patch_fields_blob(blob, old_start, new_start)` as well as its Start.

## Pitfalls

- A cue that starts a few frames before its word can sit on the card's exit even after the gap; that is why card start and cut are chosen separately (ep1 CHAPTER 04/05, 9 frames).
- A DRT round-trip of a 9:16 timeline can drop a `Mitr-short-001` style applied by the `Project.db` patch: subs jumped from y ~1020 to y ~330 over the head. The 16:9 `Mitr Font` survived. Always burn-in one subtitle frame after import; a swap without DRT keeps the style.
- `bunny_ep4/render_full.py` leaves the Deliver page and the rendered timeline active; restore page/timeline/playhead and delete only its own `final-tmp-<ts>` preset.
- `GetProperty` sometimes omits default-off audio keys (`AudioVoiceIsolation*`, `AudioDialogueLeveler*`); treat None/False/0 as equal when diffing, and compare floats with a tolerance (DRT keeps 15 digits).
- HyperFrames rounds a composition up to a whole frame (1135 planned -> 1136 rendered); place `endFrame` at the planned count.
- Never overwrite placed media; new renders get a suffix. Keep the old timeline until the user says to delete it, and back up first.
- `pick_cut` returns None when there is no pause: do not cut mid-word; report it instead.

## Verification

`gap_edit verify` prints `problems 0` and `extra == planned V3 gap overlays: True`; `qc_render.py` shows gaps ≈ -32 dB, no black frames and the expected frame count (`base end + G*len(cuts)`); `py -3.13 -m pytest -q tests/test_wipe_gap_plan.py tests/test_skill_bundle.py tests/test_agent_entrypoints.py` passes.
