---
name: house-style
description: The editorial and finishing preferences this project's work is judged against — cut rhythm, shot selection, delivery conventions, and the corrections that have already been given. Load before assembling, restructuring, or refining any cut so the same note does not have to be given twice.
version: 0.3.3
author: Warit (pong34811), Hermes Agent
license: MIT
platforms: [windows]
metadata:
  hermes:
    tags: [Editing, House-Style, Corrections, Workflow]
user-invocable: false
---

# House Style

The craft guides in `docs/guides/` describe editing in general. This file

describes **how this editor wants it done** — the accumulated, specific

corrections that would otherwise have to be repeated every session.

Read it before any edit task. Append to it whenever a correction is given.

## The capture protocol

This file is only worth what gets written into it. When the user corrects an

editorial decision — rejects a cut, changes a shot choice, adjusts a duration,

says "not like that" — do not just fix it. Fix it, then add the rule here.

A useful entry has three parts:

- **The rule**, stated as an instruction, not an observation.
- **Why**, in the user's terms — what it was in service of.
- **The trap**, if there is one: what makes it easy to get wrong.

Write rules that are falsifiable. "Cut on motion" is a rule; "make it feel

dynamic" is not. If a correction is one-off and situational, it does not belong

here — this file is for what generalizes.

When an entry turns out to be wrong or too broad, edit it. A stale rule

confidently followed is worse than no rule.

---

## Pacing and rhythm

<!-- Hold lengths, when to cut early, what "too long" means for this material. -->

For short-form subtitle passes, keep each Thai caption to at most three short

words and about 14 Thai characters, with no more than 1.5 seconds on screen.

Write Thai captions without spaces between Thai words; keep spaces only around

Latin terms such as names. Use shorter holds when the spoken words arrive

faster. The trap is using spaces to show word grouping, which makes Thai text

look unnaturally spread out.

Do not remove dead air or pauses from a talking recording unless the user asks
for tightening; a "basic edit" means hook, titles, zoom and illustrations on the
full take. Why: the user stopped the Aomi-mama flood updates and asked for the
silences back (2026-11-08). The trap: "make viewers keep watching" sounds like a
request to tighten.

## Subtitle track only

Create and continue dialogue captions only on native Resolve Subtitle tracks.

Do not use Text+ / TextPlus, Fusion titles, or text on video tracks as a

substitute, even if they offer easier styling. The user wants subtitles kept

in the existing Subtitle-track workflow. Historical Text+ captions are not

permission to create more; migrating existing captions must preserve their

text and timing and must not remove unrelated titles or overlays.

Treat a native-track preference as a creation rule, not permission to modify every historical Text+ timeline.

Confirm the migration targets; preserve protected horizontal versions. After

verifying exact text and frames, disable a captions-only legacy track rather

than deleting its clips. Never disable a mixed track of titles and overlays.

When the user handles fonts/styles, do not revive an older font/style plan;

report legibility problems without styling or retiming outside current scope.

For preserve-text-and-timing migrations, flag legacy house-style exceptions

instead of dropping words, shortening holds, or splitting cues automatically.

Take Thai subtitle text from a Descript transcript, not local Whisper, on every
clip length. The user rejected Whisper text on a long stream (Aomi-mama,
2026-11-07) and stopped a local Whisper pass on a 2-minute Bunny Girl episode
in favour of Descript (ep6, 2026-11-08). The trap is assuming a short clean read
is safe for local ASR; use the silence map only for timing.

When one SFX pushes a test render's peak above -0.5 dBFS, lower only that SFX
item (a pop on a loud word: -9 to -12 dB) and re-render under a new name; do not
drop A1 or every SFX (Bunny Girl ep6, 2026-11-08: -0.3 -> -1.1 dBFS).

## Saved subtitle font presets

When the user requests subtitle font styling by preset, load the exact approved
saved Subtitle-track preset instead of manually guessing font, size, stroke or
position. Discover the saved name and source library; ask before substituting
`Mitr Font` for `Mitr-Font` or borrowing a preset from another library. This
keeps the user's established style intact. Python-based SQL workarounds still
require explicit database-write approval and a verified backup; a font request
alone does not authorize SQL. Preserve every cue's text/timing and all original
video/audio ranges.

Prefer a preset method that keeps Resolve open. The user asked for an
alternative after the close/patch/relaunch cycle of `load_subtitle_preset_auto`
hung on a leftover `Resolve.exe` (Bunny Girl ep4, 2026-11-01). For a plain
track style such as `Mitr Font`, use `scripts/drt_clone_subtitle_style.py`: it
clones the styled Subtitle track from a reference DRT into a new timeline (user
chose this keep-open route, Bunny Girl ep5, 2026-11-07). The MCP
`timeline_ai set_subtitle_preset` only carries animated presets (Word
Highlight, Lollipop) and refuses `Mitr Font` with "No animation preset". Fall
back to the DB patch only if the clone fails, and still ask for approval.

## Names, numerals and cue length (Katy404 / KT)

Write the channel name spoken as "เคที" in Thai captions as **เคที่** (with the
tone mark), never as Latin "KT". The user corrected this by hand. Show a spoken
numeral as digits ("1,950", "10,000"), but give it its real spoken duration: a
digits-only cue defaulted to a 0.3 s hold while the speaker needed ~1.5 s, so
the caption vanished mid-word. The trap is trusting a length formula that only
counts Thai letters; check each cue's end against the audio and set it explicitly.

## Reaction GIFs and VTuber zoom framing

Reaction GIFs get the saved **"vdo"** Inspector values (`scripts/apply_vdo_preset.py`),
not a computed corner slot. Place GIFs outside VTuber Zoom ranges. For a corner
avatar, prefer a frame with no black band and a slightly off-centre avatar over a
perfectly centred frame with a visible black strip; keep the hair tip (ahoge)
inside the frame with a few percent of headroom. Delete only the copy/variant
timelines you created or that the user names; a backup `.drp` comes first.

In 9:16 copies, give every reaction GIF and illustration the saved **"short"**
video preset (Zoom 0.42, Position Y 403.2, Pan 0) instead of a computed slot,
even where a full-frame avatar crop puts it over the face. The user asked for
"short" on V4/V5 of every vertical timeline and kept it after seeing the face
overlap in the bedroom shots (Aomi-mama 2026-10, 2026-11-07). The trap is
re-placing overlays to dodge the face: report the overlap, do not move them.

## Shot selection

<!-- What earns a place in the cut; what gets dropped even when it's a good shot. -->

## Explainer graphics size

For a talking-host explainer, make keyword graphics large (a slam word at least a third of the frame width) and change them on the spoken cue. Do not hold one small corner card for a whole chapter. The user rejected nine small persistent cards as "too small and boring" and chose the Pop Kinetic style instead (Bunny Girl, 2026-10-17). The trap is a tidy card template that never moves.
When dialogue subtitles share the frame, a keyword must leave a visible gap to the subtitle; cap its width (640 px on a 1920 frame with centred `Mitr Font` subtitles) instead of letting the two touch (Bunny Girl, 2026-10-18).

When the user asks for a "transition" between chapters of a Pop Kinetic explainer, they mean the full-screen CHAPTER card (pink, gold `CHAPTER NN` tag, title, bunny ears) with its own 1.6 s silent gap and whoosh, not a short cut wipe. A 0.5 s colour-panel wipe over the cut was rejected for the CHAPTER 03 look (Bunny Girl ep3, 2026-10-25). The trap is reading "transition" as a cut effect.

## VTuber Zoom Focus

- Use the subject explicitly identified by the user as the focus target; do not assume every focus request means the VTuber. This project can use an in-game character shown in the user's reference image. The trap is letting the familiar lower-panel avatar override a different subject in the reference.
- เมื่อผู้ใช้ขอโฟกัส Armigon ให้ยืนยันตัวตนของ VTuber ในแต่ละช่วงก่อนปรับ `Adjustment Clip`; ถ้าภาพเป็นตัวละครอื่น ให้คืนค่า focus ของช่วงนั้นเป็นกลางและบันทึกเหตุผล อย่าใช้การซูมกับตัวละครผิดคน
- คงภาพเต็มเฟรมโดยไม่เพิ่มขอบดำหรือ blur และไม่สร้างการเคลื่อน/สั่นจากค่า transform ที่เปลี่ยนตามเวลา ตรวจค่า keyframe ของ `Center` และ `Size` รวมถึง `MotionBlur` แล้วดูภาพจริงหลายจุดเมื่อจำเป็น ภาพนิ่งเพียงภาพเดียวไม่พิสูจน์ว่าไม่มีอาการสั่นตลอดช่วง
- จัด Armigon ให้เด่นและอยู่ใกล้กลางเฟรม เห็นตั้งแต่ศีรษะถึงอก/มือ เว้น headroom ราว 5–8% โดยไม่ตัดศีรษะ ใบหน้า เขา หู เครื่องประดับ หรือมือที่จำเป็นต่อปฏิกิริยา ถ้าจัดไม่ได้ให้ลด zoom หรือค้างช่วงนั้นไว้เพื่อตรวจเพิ่ม
- เทียบเฟรมเวลาเดียวกันขณะเปิด/ปิด `Adjustment Clip` เพื่อระบุว่าขอบภาพที่ตัดหรือ overlay ที่บังตัวละครอยู่ใน source แล้วหรือเกิดจาก focus อย่ารายงานว่าการแก้ focus ซ่อม source ที่ถูกตัดหรือถูกบัง
- When the user hand-places an Adjustment Clip on a specific track and asks for "the same" there, clone that clip (its type and Inspector values) to every range on that track; do not keep or recreate the Fusion Transform version on another track. Why: the user disabled the Fusion `VTuber Zoom` V2 and set an Inspector zoom on V3 to replace it (Armigon favgames, 2026-10-31). Trap: the existing focus tools only build Fusion `Sm2TiGenerator` clips.

## Cut points

<!-- Cut on motion vs on rest, handles, how much air before and after a beat. -->

_Not yet captured._

## Structure and openings

<!-- How a piece starts, what the first frames have to do, how it lands. -->

_Not yet captured._

## Rejected by default

Things not to add unless explicitly asked. Seeded from the rough-cut deliverable

contract in the `resolve-rough-cut` skill, which exists because this work gets

thrown away:

- Titles, captions, and text cards
- Transitions (an assembly is hard cuts)
- Effects and speed ramps
- Music beds
- Grading on a cut that was asked for as an assembly

## Thumbnail simplicity

For Sakuyako cover templates, prefer a minimal composition: one short hook and
one clear character image. Avoid decorative frames, stickers, dot patterns,
diagonal ribbons and extra copy unless requested. The user asked to reduce
decoration in the landscape/portrait examples; the trap is treating generic
thumbnail embellishments as required branding.

## Delivery conventions

<!-- Aspect ratios, timeline naming, versioning, where renders go. -->

**Livestream highlight timelines** (merged from `agent-seacrh-virus-cut`, 2026-11-02):

- **Rule:** Name each highlight timeline in the format the live brief/`job.json` gives. The default is
  `{ชื่อคลิป}-{ชื่อเกม}-vdo`; the Sakuyako-Cheris 2026-09 job used `{ชื่อคลิป}-vdo`. No candidate/source
  IDs, categories, dates or extra suffixes; keep ID-to-timeline mappings in job artifacts.
- **Why:** The user wants only the clip title, game name and `vdo` suffix in the timeline name.
- **Trap:** Reusing `<id>_<category>_<title>`, assuming every segment shows the game in the source
  filename, or silently appending a number to a duplicate name (ask instead).
- Highlight timelines are assembly only (see "Rejected by default"). For renames: select each
  timeline by ID, rename only, save, then read the list back and check every name and the count.
  Details: `timeline-naming-convention` skill.

---

## Where personal grading taste lives

Colour and look preferences are **not** kept here — this file travels with the

repository. Grading taste lives in the user-level `colorist-assistant` skill and

in persistent memory. Load those for look selection, grade transfer, and the

Resolve API traps around them.

If any entry below would be specific to one person rather than to this project's

work, it belongs in the user-level skill instead, and this file should be

gitignored rather than committed.
