# Editorial craft — where to cut

Source: `docs/guides/editorial-decision-guide.md` (the project-owned craft
reference), `docs/SKILL.md` (Editorial Memory), `.agents/skills/house-style/SKILL.md`.

## Core priorities (serve them in this order)

1. Emotion and story
2. Clarity of thought or action
3. Rhythm and timing
4. Eye trace and screen geography
5. Continuity and technical polish
6. Coverage variety

Good coverage is useful only when it helps the viewer understand, feel, or
anticipate something. **When those goals conflict, keep the moment that carries
the clearest emotional or narrative charge.**

## Pre-flight coverage check (required, and it changes the answer)

Before answering any cut, pacing, story-structure, or shot-selection question,
call `media_analysis(action="coverage_report")` against the target you are about
to reason about (timeline, bin, selection, or project). It is a pure read and
never triggers analysis.

The response carries an `evidence_base` string, e.g.
`"evidence base: 38/40 clips analyzed (95%), 1 stale, 1 reuse-blocked."`, plus a
per-clip breakdown (layer presence, source-trust tier, staleness, relink
supersedure, `recommended_action`).

- **Lead the reply with the `evidence_base` line — before any creative
  recommendation.** Do not silently answer from incomplete evidence.
- If coverage is below the threshold the question depends on, surface the gap
  first and offer to fill it ("3 of the clips on this timeline have no transcript;
  analyzing them first will materially change my cut-point suggestions — run it
  now?").
- When the gap is small and the user wants to proceed, still answer — but mark the
  answer **evidence-thin** so they can re-ask.
- **Do NOT auto-trigger analysis** to fix gaps unless the user explicitly asks.
- Clips with `superseded_by_relink=true` must never be reasoned about as if the
  prior analysis still describes them — re-analysis is required before the
  recommendation is grounded.
- Source-trust filtering: `coverage_report` accepts `min_source_trust` (`auto`,
  `filename`, `low`, `medium`, `high`). Use `medium` for routine work, `high` for
  shot-matching or look development.

## Analysis memory — reuse before re-running

Inspect what the project already knows first:
`media_analysis summarize`, `media_analysis get_report`,
`timeline probe_timeline_structure`, `timeline story_spine_report`,
`timeline source_range_report`, `timeline_markers get_all`,
`media_analysis review_timeline_markers` when marker imagery matters.

A new request for edit advice is **not** automatically a reason to re-run visual
analysis if the prior report already has current technical data, motion/keyframe
evidence, and useful visual descriptions. Add transcription, vision, marker review
or source-range checks only when that missing evidence changes the decision. Use
`force_refresh=true` only when the user asks or when the cache signatures show the
source, prompt, depth, or modality changed.

## Frame choice

Find the decisive frame, not just the technically clean frame. Useful cut points
often occur when a face changes intention, a hand completes a thought, a gaze
lands, a movement resolves, or the audience has received the needed information.

Dialogue and reaction:

- Prefer the reaction when it carries the meaning.
- **Let sound lead picture** when the incoming idea needs setup.
- **Let picture lead sound** when surprise, reveal, or anticipation matters.
- Avoid cutting away before a thought has landed unless compression is the point.

Movement:

- Cut on completed or motivated motion.
- Use motion peaks as candidates, then verify the frame visually.
- **Treat scene detection and variance as guardrails, not the editor.**

## Sound first

For interviews, dialogue, comedy, and short-form editorial, build the audio spine
before chasing visual variety: **premise** (what the viewer must understand first)
→ **setup** (pressure, context, contrast) → **turn** (new idea, contradiction,
reveal, escalation) → **button** (final image, line, beat, release).

When trimming, preserve complete thoughts and clean transitions in breath, tone,
and room sound. **Visual cutaways can hide picture edits, but they cannot fix a
broken idea.**

## Finished-video guardrails

When analyzing an already-finished video, **do not treat every detected cut as an
edit instruction**. Use black frames, flash frames, scene-change clusters, silence
and motion spikes to find regions that need verification. Output should be:
likely scene/section boundaries; ranges to avoid (black, flash, silence, corrupt
frames); audio-led story beats; visual evidence at markers and cut points; and
questions where the image contradicts the label or transcript.

## Markers are memory, not truth

When a marker name, note, or beat label matters, verify it against a
Resolve-rendered frame: generate a marker contact sheet, compare each label with
the visible frame, rename/move/downgrade markers that do not match, and keep notes
concrete enough that another editor can act on them. Use contact sheets for
orientation and review — `analyze_media` defaults to host_chat_paths vision
(actions return `frame_paths` + a schema and the host finalizes per-clip analysis
via `commit_vision`); pass `include_visuals=false` for a no-visual run.

## Variant safety

Before making or changing a variant: check timeline start frame and timecode;
prefer dry runs for range-based operations; keep source media untouched; use
positioned appends and explicit source ranges.

After: `timeline detect_gaps_overlaps`, `timeline source_range_report`, review
thumbnails at important markers and cut points, and confirm the audio spine still
reads.

## Response shape when reporting analysis

Editor-usable: what was analyzed; whether prior analysis was reused or refreshed;
technical warnings that affect editing; motion and variance summary; visual
content and best moments; transcript/sound notes; avoid ranges; concrete next
actions. **Avoid overclaiming from sparse evidence** — if the tool only sampled a
few frames, say so and recommend the specific next verification step.

## This project's captured house rules

From `house-style` (which travels with the repo; grading taste lives in the
user-level `colorist-assistant` skill instead):

- **Thai captions:** at most three short words and about 14 Thai characters per
  caption, ≤1.5 s on screen, shorter holds when speech is faster. No spaces
  between Thai words; spaces only around Latin terms — the trap is using spaces to
  show word grouping.
- **Subtitle track only:** dialogue captions go on native Resolve Subtitle tracks.
  Not Text+/TextPlus, not Fusion titles, not text on video tracks. A native-track
  preference is a creation rule, **not** permission to modify every historical
  Text+ timeline.
- **Saved subtitle font presets:** load the exact approved saved preset; discover
  the name and ask before substituting (`Mitr Font` exists, `Mitr-Font` does not).
  A font request alone does not authorize SQL.
- **Names and numerals:** the channel name spoken "เคที" is written **เคที่**,
  never Latin "KT". Spoken numerals appear as digits but get their real spoken
  duration — a digits-only cue defaulted to a 0.3 s hold while the speaker needed
  ~1.5 s, so the caption vanished mid-word. Check each cue's end against the audio.
- **Rejected by default in an assembly:** titles, captions, text cards,
  transitions, effects and speed ramps, music beds, and grading on a cut that was
  asked for as an assembly.
- **Reaction GIFs** get the saved "vdo" Inspector values
  (`scripts/apply_vdo_preset.py`), not a computed corner slot, and are placed
  outside VTuber Zoom ranges.
- **When corrected, fix it and then add the rule** to `house-style` — rule (as an
  instruction), why (in the user's terms), and the trap. Write falsifiable rules:
  "cut on motion" is a rule; "make it feel dynamic" is not. Edit an entry when it
  turns out wrong: a stale rule confidently followed is worse than no rule.
