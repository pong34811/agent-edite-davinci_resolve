# End-to-end task recipe skills (10 skills)

These walk a whole job rather than routing a domain. Each states its own
deliverable contract; violating that contract is the most common way the work
gets thrown away.

## `resolve-session` — start a working session (124 lines)

Triggers: `/resolve-session`, "start a Resolve session", before any editing.

1. Connect and identify the host: `resolve_control(action="get_version")` —
   capture Resolve version, Studio vs free edition, and whether the connection is
   external scripting or the in-app bridge (`Workspace > Scripts > resolve_bridge`).
   If it fails, read the error's own `remediation` field and follow it; a
   connection error does **not** mean the free edition is unsupported.
2. Report a short block: version + edition, project, current timeline with its
   format, pool summary, warnings, and anything `check_version_support` reported
   missing. Then stop — do not start editing off the back of this.

Notes: if Resolve is not running the MCP tools will launch it and the first call
can take up to 60 seconds — say so rather than appearing to hang. Do not open,
create, or switch projects unless asked. Ships `agents/openai.yaml`.

## `resolve-rough-cut` — additive assembly (360 lines)

Triggers: "rough cut", "first cut", "assembly", "make me a timeline" from a
folder of footage (day-in-the-life, BTS, process, product shoot) for Reels /
TikTok / Shorts.

**Deliverable contract**: deliver an assembled timeline. Do **not** add titles,
captions, text cards, effects, transitions, music, or grading unless explicitly
asked — styling is the editor's, and graphics work gets thrown away.

Sections: workflow, shot finding at scale, verified traps, assembly shape,
source-media safety. Common mistakes: reframing vertical-flagged footage into a
vertical timeline (double-rotating material that already fits); setting the
timeline frame rate *after* creating the timeline (it is ignored); trusting
`detect_gaps_overlaps` alone (also confirm total duration and inspect
representative frames); reporting a render when the timeline is the deliverable.

## `resolve-tighten-recording` — subtractive (262 lines)

Triggers: tighten a recording, remove silences/dead air, cut the pauses out of a
long take, raw one-take recording → first cut. Counterpart to `resolve-rough-cut`
(which selects shots from many clips; this removes time from one clip).

**Deliverable contract**: a tightened **variant** timeline, plan → review →
confirm. No grading, captions, or additions — pure subtraction. The variant runs
generous on purpose: recovering over-cut material is slow and invisible,
trimming further is fast and visible.

**Coordinate trap** — plan and execute describe ranges in different systems and
both look like plausible frame pairs:

| Field | Coordinate system | Verified |
|---|---|---|
| plan `keep_ranges` `start_frame`/`end_frame` | **Source** frames, `end_frame` exclusive | frame-exact against `clip_where` readback |
| `structural_diff.added` `in_frame`/`out_frame` | **Record** (timeline) frames of the variant | matches variant item record spans |
| variant record positions | cumulative sum of keep-range durations | `record[i] = Σ(end−start)(j<i)` |

What silence-driven tightening cannot hear: `plan_tighten` measures the
microphone, not the meaning. Audible fillers and tight restarts need
`plan_transcript_tighten` (word-level; emits the same `keep_ranges` shape).
Common mistakes: trusting `detect_gaps_overlaps` alone (proves gapless, not that
the right frames were kept); verifying audio by "the response said success" —
count the variant's audio items.

## `resolve-trim-to-length` — cut to a target length (30 lines)

Triggers: shorten timelines to a target length; `<name>_150s` variant.

1. Read-only audit: `(GetEndFrame-GetStartFrame)/timelineFrameRate` per timeline;
   list over-length ones. Never eyeball.
2. ONE clarify before editing: target ("2.50 min" = 2:30 or 2:50?) and cut
   location (head / tail / user-chosen). Default: tail trim into a `<name>_150s`
   variant, originals untouched.
3. `backup_drp.export_verified` a `.drp`, then `src.DuplicateTimeline(name+"_150s")`;
   sleep ~1.3 s between mutations (rapid ops crash Resolve).
4. In the duplicate: delete clips starting at/after the cut; delete subtitle cues
   touching the cut (`DeleteClips` works on subtitle items; cues cannot be
   re-timed); delete straddling video/audio items and re-append the same media
   pool item with `mediaType` 1/2, same `trackIndex`/`recordFrame`, reduced
   `endFrame`.
5. Restore transform/crop/opacity (video) and Volume/Pan (audio) via
   `SetProperty`; read back; assert the new item ends exactly at the cut.
6. Verify per track against the clipped expectation (start/end/Zoom/Pan/Crop);
   variant length == target; originals unchanged. On failure delete the partial
   duplicate with `MediaPool.DeleteTimelines`. SaveProject.
7. Report deleted subtitle cues/SFX past the cut, and that the cut is mechanical
   (not on a sentence end).

Traps: `GetSourceStartFrame/EndFrame` are in the SOURCE clip's fps, not the
timeline's (scale by `(se-ss)/(e-s)` or the clip lands short); re-append drops
grades, Fusion comps and links; do not trust a verify script that counts trimmed
items as tail items.

## `resolve-batch-export` — batch render with the user's preset (127 lines)

Triggers: batch-export timelines with a preset; "which timeline did this file
come from?". Ships `references/provenance-audit.md`.

Steps: read-only preflight (`GetRenderPresetList()` contains the named preset;
no existing output names; covers/assets exist) → one clarify for ambiguities →
`LoadRenderPreset(name)` before **every** job, then override `SelectAllFrames`,
`TargetDir`, `CustomName` **and every setting the user explicitly asked for that
the preset does not guarantee** (overriding only the three shipped a batch with
captions as sidecar files) → vertical covers via a `DuplicateTimeline` copy named
`<name>__cover_tmp` with the jpg on a new top video track at the first frame.

Traps: interrupting a batch means kill → clean up (read the queue, delete only
job ids you created, delete every `__cover_tmp`, delete partial outputs,
`SaveProject()`, confirm `IsRenderingInProgress()` is False) **before** re-running;
kill by PID, never by command-line match (a filter matching your own script
matches the wrapper shell and kills itself); an ad-hoc audit that calls
`LoadProject` still moves the user's session — put Resolve back and report which
project you left open.

## `resolve-folder-cover-batch` — covers for a whole Resolve folder (56 lines)

**External dependency**: needs a separate `agent-thumbnail` project that is NOT
in this bundle. Locate that repo and read its own `AGENTS.md` before use; if
unavailable, stop before any Resolve or file mutation and report the missing
prerequisite.

Scope = **projects, not timelines** (each project holds N landscape + N `_9x16`
timelines; report pairs × 2 before building). Read names from the live folder,
never from screenshots or OCR. Split hook planning across ~5 subagents by
project, writing a shared `BRIEF.md` into `reports/<channel>/<date>/` *before*
dispatching. Hooks come from subtitle cues only; ASR is often garbled, so
children set `flag` (`subs doubtful` / `title-only`) instead of inventing text.
TDD the mapping; check assets before the full build (placeholder coloured boxes
in a Channel Kit `CHECKLIST.md` must never ship; mixed 1920×1080 / 1280×720
source frames must be resized before fixed crop boxes). Verify with
`py -m cli.verify --jpg-dir ... --manifest ...`, then QC in parallel subagents
and fix every CRITICAL.

## `vtuber-cover-batch-pipeline` — project → 16:9 + 9:16 JPGs (48 lines)

Same external `agent-thumbnail` dependency and the same stop-if-missing rule.
Adds: check for an existing batch first (if the open project's timeline names
already equal a mapping's name set and every `<name>.jpg` exists, re-verify and
report instead of rebuilding); landscape = width 1920, the 9:16 twin's name
already ends in `_9x16` so the twin check is `name in portrait_names`; extract
one frame per timeline at `src_start + frame_tl`; reject inventory/menu screens,
Minecraft F3 overlays (server name + coordinates), end-of-mission banners,
desktop shares showing a username, near-black frames, calm game-start frames for
fight hooks.

## `resolve-offline-media-repair` — media offline though the file exists (34 lines)

1. Confirm the path exists, then `ffprobe` read-only (codec, fps, duration) and
   compare with a known-online sibling. A correct path does not prove Resolve can
   decode the media.
2. If a replacement is reported, compare content hashes (file size as a quick
   check) — timestamps, including ctime, do not prove bytes changed.
3. Do not transcode with FFmpeg or replace source media through an external
   editor. Check the MCP for a supported relink/repair action first; otherwise
   record `MCP-GAP:` and use only a verified Resolve scripting-API method. Never
   invent `ReplaceClip`; check the installed API stub and probe read-only first.
4. If recovery needs optimized/proxy media the MCP/API cannot create, stop with
   `BLOCKED` and ask the user to generate it in Resolve.
5. Resume exports only after the batch exporter confirms a prior `Complete` job.

Pitfalls: pool entries with an empty File Path are timelines, not offline media;
keep Resolve probe/mutation scripts under this repo's `scripts/`, connect through
`scripts/resolve_common.py`, and use `preserved_state(resolve)` for mutations —
never put Resolve mutation scripts in Hermes scratch. **When the user says
"continue" with no context**: do not ask or guess — run `session_search` (query
by filename/topic, newest first) and read the matching prior session.

## `resolve-mitr-subtitle-presets` — batch-apply a saved subtitle preset (133 lines)

Triggers: "load preset Mitr Font ให้ทุก timeline", "จัดการ font mitr แนวนอน /
แนวตั้ง", "ซับ shorts ใช้ Mitr-short-001". Ships `scripts/load_subtitle_preset.py`.

| Orientation | Raster | Preset | Font in preset |
|---|---|---|---|
| horizontal (แนวนอน) | 1920x1080 | `Mitr Font` | Mitr SemiBold, default position |
| vertical (แนวตั้ง) | 1080x1920 | `Mitr-short-001` | Mitr Bold + custom position |
| (unused/basic) | any | `mitr`, `mitr-short` | Mitr Regular, identical bytes |

```
python load_subtitle_preset.py --list
python load_subtitle_preset.py --preset "Mitr Font" --orientation horizontal
python load_subtitle_preset.py --preset "Mitr-short-001" --orientation vertical
```

Preset names are case- and punctuation-sensitive: if the requested name differs
from the saved name (`Mitr-Font` vs `Mitr Font`), show both and ask — never
silently substitute. A mixed project needs **two** runs; never `--all-timelines`
one preset over a mixed project. **`--apply` is deliberately unavailable** — it
stops before writing because it cannot verify Resolve fully exited; a future
writer must create and verify a durable `.drp`, save/close the project, confirm
no Resolve process holds the DB, and verify every changed row. Never bypass the
gate by calling SQL directly. `No target timeline has a subtitle track` is
normal for a 16:9-only project, not a bug; `DB has N subtitle tracks but Resolve
reports M` means unsaved new tracks — save and rerun.

## `video-footage-review` — first-pass cutlist from footage (222 lines)

Triggers: review footage, produce a first-pass edit cutlist. Ships
`references/whisper-transcription.md`.

Output (in the language of the request): footage inventory table → content
summary → first-pass cutlist table (# | start | end | duration | reason) → keep
list → notes on audio/language/structural issues.

Pitfalls: Whisper `base` produces unusable output on mixed-language Thai — use
`small` minimum, `medium` for publication grade; do not trust a single
context-starved pass (re-transcribe a 4–10 s window with neighbours and 1–3 s
margins, `language="th"`, `condition_on_previous_text=False`, temperature
fallback); the folder may contain a single file, not multiple clips; ffmpeg
`fps=1/10` yields frames at 10 s boundaries starting from 0 (a 196 s video gives
20 frames, so the last ~6 s have no frame); vision analysis needs absolute
`C:/...` or `file:///C:/...` paths on Windows.

## `video-provider-smoke-qc` — validate a video provider first (24 lines)

Trigger: validating a video analysis provider before batch QC. Tiny gate skill —
run it before trusting any provider's batch output.
