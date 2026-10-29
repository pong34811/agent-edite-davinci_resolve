# Scripted adjustment-clip focus on existing Resolve timelines

Use this only when the user has approved adding adjustment clips above an existing edit. The public API's generator insertion behaves like an edit and may ripple *other* track types even when original video tracks are locked. For VTuber-focus requests, modify **only the approved Adjustment Clips**: do not transform, trim, move, or replace the underlying footage, audio, subtitles, or unrelated overlays. Treat subtitles as candidate cue markers, not proof of the ideal focus frame.

## Subtitle-led focus and composition requirements

- Review every named timeline; do not assume one timeline represents the batch. Inventory subtitle ranges and the associated VTuber/gameplay picture before proposing focus intervals.
- Select moments where a subtitle is already present and the character is visible and meaningfully speaking/reacting. Check the spoken/action context around each subtitle; do not mechanically zoom every cue or infer emotion from words alone.
- For each approved focus interval, use a new dedicated video track above the existing tracks and place/adjust only Adjustment Clips on that track. Keep the rest of the timeline structure and all underlying ranges unchanged.
- Make the VTuber the primary visual focal point: increase scale enough to read clearly, then adjust X/Y so the character is near frame center while showing approximately head through chest/hands, with a small amount of headroom.
- Never crop the head, face, or other important character features. Avoid covering subtitles, gameplay evidence, critical HUD, or hands needed to understand the moment. If all framing constraints cannot be met, reduce the zoom or flag the cue rather than forcing a crop.
- Derive the framing from the live source and timeline raster, not a guessed universal Zoom/Pan/Tilt value. Calibrate each distinct camera layout and inspect rendered pixels; an Inspector value alone is not visual verification.
- Before/after compare the exact original video, audio, subtitle, and unrelated-overlay ranges on every target timeline. If any changed, stop and roll back the batch before claiming the "Adjustment Clip only" scope passed.

## Starting from the user's selected Adjustment Clip

When the request says to use the Adjustment Clip already selected on the timeline ("ใช้ Adjustment Clip ที่เลือกอยู่บน Timeline"), treat that clip as the approved template. New focus clips still go on a new video track.

- Read the selection back. Don't assume it. `Timeline.GetSelectedClips` needs build 21.0.4+. On older builds, selection readback is best-effort and an empty or partial result looks the same as a small selection. If the readback is empty, ambiguous, or not an Adjustment Clip, ask the user to identify the clip by timeline, track, and start frame instead of guessing.
- Record the template's timeline ID, track type/index, `GetStart()`/`GetEnd()`, name, and any existing Fusion comp/Transform inputs before touching anything. The selected original is protected: never move, trim, retime, or restyle it unless the user explicitly names it as a target.
- Copy rather than move. Use the repo bridge's `duplicate_clips` (for example mode `track_above`) or `copy_properties` scoped to transform/composite groups, or insert a fresh `Adjustment Clip` generator and rebuild the template's Fusion Transform. Then re-time each copy to its planned cue interval on the dedicated new track. `move_clips` is duplicate-then-delete, which would remove the user's template, so don't use it.
- The template's zoom/position is a starting point only. Re-frame each cue against the live picture using the checklist below.
- Selection is per timeline. For "ทุก Timeline", confirm a usable template on each target timeline, or get approval to reuse one timeline's template values elsewhere after per-layout calibration.

## Per-cue framing checklist (record Pass/Fail per cue)

1. Cue association: a subtitle overlaps the interval, and the VTuber is visibly speaking or reacting there.
2. Placement: the Adjustment Clip sits on the new dedicated video track at the exact planned `[start, end)`. Nothing else was added or changed.
3. Prominence: the zoom makes the VTuber clearly the main subject of the frame.
4. Centering: Position X/Y (Fusion `Center`) places the VTuber near the middle of the frame.
5. Shot size: roughly head to chest/hands is visible.
6. Headroom: a small gap remains above the head, neither touching the top edge nor leaving a large empty band.
7. No crop: head, face, hair accessories/ears, and hands needed for the reaction are fully inside the frame. If this fails, reduce the zoom or defer the cue. Never accept a crop.
8. Overlap: the result doesn't hide the caption, critical HUD, or gameplay evidence, and shows no blank, stretched, or duplicated edge.
9. Scope audit: every original video/audio/subtitle range, and the selected template clip, matches the pre-edit snapshot.

## QC สำหรับ zoom focus ที่ใช้ซ้ำได้

1. **ยืนยันตัวตนในทุกช่วง** อ่านภาพที่อยู่ใต้ `Adjustment Clip` และยืนยันว่า VTuber เป็นคนที่ผู้ใช้ระบุ หากเป็นคนอื่น ให้ทำ focus ของช่วงนั้นเป็นกลางหรือส่งกลับให้ตัดสินใจ อย่าตัดสินจากชื่อ Timeline หรือ subtitle อย่างเดียว
2. **ตรวจเต็มเฟรมและความคมชัด** ดูภาพต้น กลาง และท้ายช่วงที่ zoom พร้อมขอบทั้งสี่ด้าน ตรวจว่าไม่มีขอบดำ พื้นที่ว่าง การยืด/ทำซ้ำขอบ หรือ blur ที่ focus เพิ่มขึ้น อ่านค่า `MotionBlur` กลับและเทียบรายละเอียดภาพกับเฟรมต้นทาง; ค่า 0 อย่างเดียวไม่ใช่หลักฐานภาพว่าไม่มี blur
3. **ตรวจการเคลื่อนของ transform** อ่าน `Center` และ `Size` ตลอดช่วง รวมถึง keyframe ของ input เหล่านี้และ `MotionBlur` ถ้ามี keyframe ให้ตรวจเฟรมระหว่างจุดและช่วงเคลื่อนไหวเพื่อหาการสั่นหรือ crop ระหว่างทาง ถ้ามีเพียงภาพนิ่ง ให้รายงานว่าไม่พบ keyframe ในค่าที่ตรวจ และยังไม่ได้พิสูจน์การเคลื่อนไหวทั้งช่วง
4. **เทียบ A/B ที่เวลาเดียวกัน** บันทึก timecode/record frame แล้วเทียบภาพขณะเปิดกับปิดเฉพาะ `Adjustment Clip` โดยคง source และ overlay เดิมไว้ หากส่วนศีรษะ/มือถูกตัดหรือถูก overlay บังอยู่ทั้งสองภาพ ให้ระบุว่าเป็นข้อจำกัดของ source/ภาพประกอบเดิม หากเกิดเฉพาะตอนเปิด ให้ปรับ focus หรือลด zoom แล้วตรวจซ้ำ
5. **บันทึกขอบเขตหลักฐาน** ระบุจำนวน clip/input ที่อ่านกลับ เฟรมที่ดู สถานะของ track และสิ่งที่ยังไม่ได้ตรวจ แยกผลภาพ still/A-B ออกจากผลดูวิดีโอ render เต็มช่วง ห้ามสรุปเรื่อง motion ทั้งหมดจากภาพนิ่ง

## Safe insertion and composition workflow

1. **Scope and recoverability.** Inventory every video, audio, and subtitle track's name, item name, start/end and lock state. Save/export a nonempty `.drp`, preferably work in a separately named import of a known-clean backup, and verify that import against the inventory before editing. Do not use a pilot copy as a clean base merely because its video tracks match; audio and subtitles can have been shifted. Capture the active timeline/timecode/page for restoration. Record the planned subtitle cue, exact half-open focus interval, target new track, and per-timeline pre-edit ranges so "only Adjustment Clip" can be audited.
2. **Insert one pilot safely.** Activate the exact target timeline, open the Edit page through Resolve scripting, and lock *all existing video, audio, and subtitle tracks*. Add and name a new video track above them; leave only that target track unlocked. For a planned half-open frame interval `[start, end)`, call `Timeline.SetMarkInOut(start, end-1)` and `Timeline.SetCurrentTimecode()` at `start` (convert frames with the timeline's actual FPS), then `Timeline.InsertGeneratorIntoTimeline('Adjustment Clip')`. Clear the mark in/out after insertion. Read `GetTrackTypeAndIndex()`, `GetStart()`, and `GetEnd()` and require the exact target track/range. Compare every original track's item names and ranges with the pre-insertion snapshot *before saving*. Preserve the original lock states when finished. Spacing and saving between edits reduces Resolve crash risk.
3. **Build the visual effect on the inserted clip, not underlying footage.** A scripted `Adjustment Clip` can report `GetType() == 'generator'`, empty `GetProperties()`, and `SetProperties()`/`SetSpeed()` false even while its Edit inspector displays controls. Use `item.AddFusionComp()` instead. Discover its `MediaIn` and `MediaOut` tools by `TOOLS_RegID`; add a Fusion `Transform`, connect `Transform.Input <- MediaIn` and `MediaOut.Input <- Transform`, then set `Size` and the point-valued `Center` via `SetInput()` **outside** `comp.Lock()`. Read the inputs back. Do not transplant an exemplar's numeric Inspector Pan/Tilt values into Fusion Center; its coordinate system differs. `Edges` on Fusion Transform is 0=Canvas, 1=Wrap, 2=Duplicate, 3=Mirror; choose only after inspecting a real export, since filling an uncovered edge can produce obvious stretching or a second avatar. Calibrate Center per footage layout and cue; where duplicated gameplay makes bright side stripes, preview a less-offset crop and accept it only if the avatar remains in the intended central region with head/hands intact. Restore the original setting when a probe is rejected.
4. **Review before batch and on retries.** Export a Resolve-rendered frame near the beginning, middle, and end of the pilot interval. After changing Fusion inputs, step the playhead to an adjacent frame and back before exporting the target frame, then inspect the pixels: a successful export and an identical file byte count do not prove the new graph rendered. Confirm the face/head/hands are intact, the avatar is prominent with headroom, and no blank or distracting repeated edge is visible. A still export may omit subtitle overlays; render a short range when caption overlap matters. Only after pilot and whole-track audit pass should the script insert remaining cues. On a retry, require existing focus ranges to be an exact prefix of planned ranges, skip insertion for those clips, and compare the *whole* present V3 range list against the plan prefix of length `max(current_cue_index, preexisting_count)` after each cue; comparing only through the current cue falsely fails when later clips were already present. Persist per-timeline progress, render-check at least one frame for every new focus cue and boundaries for motion-sensitive cues, and re-audit *all* original tracks after each insertion and final save.
5. **Validate the handoff.** Export the finished project as a portable `.drp` and check archive integrity. Perform a restore-test import only when authorized: import under a disposable project name and read back timeline/track inventories, all planned adjustment ranges, and Fusion input values. Restore the intended active project/timeline/timecode; remove the disposable import only if its cleanup was explicitly included in scope. If no restore test was authorized, retain the backup and report archive validation separately from untested restoration. A nonempty export alone does not prove the recipient can open the edited project.

## Single-timeline scripted route and framing geometry (verified 21.1.0.17)

`python -m scripts.apply_vtuber_zoom --plan plan.json --backup pre.drp [--in-place] --apply` adds
one track `VTuber Zoom` and N Adjustment Clips on a duplicate (or in place on explicit user
instruction), with a before/after signature of every original track. `scripts.retune_vtuber_zoom`
re-sets only those clips' Fusion Transform; `scripts.zoom_variant_stills` exports Resolve-rendered
stills (start/mid/end of each clip) for pixel QC.

Fusion Transform maths (Pivot 0.5): output `u` shows composite `0.5 + (u - Center)/Size`. For a
window `[top, bottom]` (fractions of frame height, 0 = top) centred at column `wx`:
`Size = 1/(bottom-top)`, `Center_x = 0.5 - Size*(wx-0.5)`, `Center_y = 0.5 - Size*((1-(top+bottom)/2)-0.5)`.
Window width equals its height in frame fractions (same aspect), so `wx <= 1 - (bottom-top)/2`
or a black band appears on the right.

A corner avatar cannot be centred without a band. Measured on a 16:9 facecam in the bottom-right:
source rows below ~96.6% are a black bar, so `bottom <= 0.964`; hair tip at ~57% of frame
height, so `top ~0.545` (Size ~2.39, `wx ~0.785`) kept head, ears, ahoge, mic and hand inside with a
few percent headroom. A first pass with `top 0.577` clipped the ahoge against the top edge: check
the hair tip, not just the face. Pixel-check stills for dark edge bands.

## DRT Track Injection & Automated Framing QC Tools

When timeline-item insertion via API is constrained or prone to track-offset bugs:
- **`scripts/drt_focus_track.py`**: Export timeline as `.drt`, inject a dedicated `VTuber Zoom` Adjustment Clip track with precise Fusion comps, and import back via `mediaPool.ImportTimelineFromFile()`. This preserves all existing tracks, subtitles, audio routings, and composite layers with 100% fidelity.
- **`scripts/drt_rebuild_focus_track.py`**: For N zoom ranges in one import, or to rebuild a track after the user dragged a clip head earlier (that clip's Fusion comp keeps its old length and the added head will not render), replace every clip on the named track with fresh template clips at the wanted ranges (`--create` adds the track first). After import: rename the timeline by unique ID (the import names it after the file), set the Fusion Transform, read it back, and probe-render each range.
- **`scripts/focus_frame_qc.py`**: Automates multi-frame visual and geometry verification (inspecting center offsets, headroom ~5–8%, avatar boundaries, and ensuring zero cropping of head/hands).
- **`scripts/deploy_climbing_focus.py`**: Deploys verified focus timelines directly into the main project.
- **`scripts/cleanup_and_rename_timelines.py`**: Deletes temporary backup timelines and applies standard clean Thai titles.

For a subtitle-led focus batch, the final acceptance record must cover **every target timeline and every planned cue**: subtitle cue association, exact Adjustment Clip track/range, visible framing (head, face, chest/hands, headroom), subtitle/HUD overlap, and unchanged original video/audio/subtitle/unrelated-overlay ranges. Report any infeasible cue as deferred rather than violating the crop or scope constraints.

Never infer success from a successful generator return, an Inspector screenshot, or a video-only comparison: all three can coexist with shifted captions/audio or a visually unusable frame.

## Verified run: day 24 (Katy404, 2560x1440 source on a 1920x1080 @ 60 fps timeline, 21.1.0.17)

One real timeline, no pre-selected Adjustment Clip (the Inspector showed the V1 video clip): per the template rule above, ask, then insert fresh generators. User chose in-place on the original after a verified `.drp`.

- Plan: `{"window_top": 0.545, "window_bottom": 0.964, "window_cx": 0.785}` -> Size 2.387, Center (-0.180, 1.107). Source black bar starts at row ~0.9625 of frame height, ahoge tip ~0.569, head x ~0.77-0.91. Window centre 0.785 puts the face ~12% right of centre; centring it would show a black band on the right, so the off-centre frame is the accepted result (see house-style). Headroom measured ~4% to the ahoge tip, slightly under the 5-8% target.
- Cue selection: 7 ranges (4-6 s each, ~38% of a 90 s clip) on number/goal/thanks/call-to-action/goodbye beats, not every cue. Ranges need `>= 90` frames and strict gaps (`e < next s`).
- Run: `python -m scripts.apply_vtuber_zoom --plan <plan.json> --backup <pre.drp> --in-place --apply`, then `python -m scripts.zoom_variant_stills "<timeline>" <out_dir>`. Readback matched all 7 ranges; V1/A1/subtitle signatures unchanged.
- Evidence limit: 8 of 21 exported stills were viewed; no A/B with the Adjustment Clip off and no rendered range, so motion stability is unproven (no keyframes were set).

## Fix: zoom "ใหญ่ผิดปกติ" from stacked comps (Sakuyako, 2026-10-29, 21.1.0.17)

Symptom: chibi blown up with a black band on the left. Cause: each Adjustment Clip carried 6 Fusion comps from repeated tuning attempts (each `AddFusionComp()` appends one and makes it active), and the last one, the one Resolve renders, was Size 4.24. When a zoom looks wrong, dump **every** comp per clip first (index, Transform Size/Center). Fix by editing only the last comp's Transform (`focus_apply_batch.set_transform_existing`), not by adding a seventh.

- Layout: 1280x720 Roblox capture with a pillarbox (black at x < 0.05 and x > 0.95). Chibi sits bottom-left: hair/flower top ~0.585, body base ~0.93, x ~0.08-0.235.
- Window `top 0.55, bottom 0.955, cx 0.255` gives Size 2.469, Center (1.105, 1.123). `cx` can't go below `0.05 + h/2` or the pillarbox shows, so the avatar stays left of centre (accepted, same rule as the corner-avatar note above).
- `scripts/zoom_variant_stills.py` is 60 fps only (the `timecode` helper refuses other rates). On 30 fps, export stills with `Project.ExportCurrentFrameAsStill` after stepping the playhead off and back.
