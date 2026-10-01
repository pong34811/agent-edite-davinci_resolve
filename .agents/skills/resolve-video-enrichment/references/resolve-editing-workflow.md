# Resolve editing: from selects to a verified cut

## Scope and evidence
- Learning-only requests authorize research and skill updates, not opening or changing a Resolve project.
- This chapter covers selected parts of The Editor's Guide to DaVinci Resolve 20: lesson 1, Pacing the Soundbites (p. 46); lesson 2, trimming (pp. 84–98); lesson 3, split edits (pp. 185 onward).[6]
- These are documented Resolve 20 concepts, not proof of the installed build or scripting support.
- Local operating rules come from `AGENTS.md`, `.agents/skills/house-style/SKILL.md`, and `docs/OPERATING-NOTES.md` when present.
- Do not import the training book's sample assets, example timings, or aspect ratio into a real job as defaults.

## Deliverable contract
- Identify whether the request is advice, a cutlist, a rough cut, enrichment, captions, or delivery.
- Ask only for decisions that change the work; make reversible editorial proposals without blocking on low-stakes preferences.
- For an authorized edit, record target project and timeline IDs, source files, destination, audience, format, and must-preserve items.
- Keep Shorts and horizontal highlights as distinct creative deliverables; neither authorizes changing the other.
- An assembly means picture and source audio unless the user also asks for finishing.
- A finished exemplar constrains density, captions, mix, and placement; propose a bounded cue plan before importing or adding tracks.
- For batches, list every target and reconcile requested, inspected, changed, and verified counts programmatically.

## Read-only preflight
1. Read the exact Resolve product/build and the installed scripting reference before choosing an automation route.
2. Record the active project, timeline ID, playhead, page, Media Pool folder, track enable states, and relevant lock states.
3. Read timeline raster, `timelineFrameRate`, and `timelinePlaybackFrameRate` separately; compare them to the approved settings.
4. Inventory every video, audio, and subtitle track's items, ranges, media paths, and relevant properties.
5. Distinguish baked-in music/captions from editable tracks by listening and viewing, not track count alone.
6. Reuse existing transcripts, markers, cue maps, and analysis only if source identity and timeline state still match.
7. List evidence gaps before recommending exact cuts; sparse screenshots cannot establish a complete performance.
8. Stop before writes if the target or approved settings differ; obtain the user's decision rather than silently inheriting drift.

## Source review and selects
- Probe authorized media through `terminal` with `ffprobe -v error -print_format json -show_format -show_streams "<source-file>"`.
- Substitute the actual discovered source path; the angle-bracket text is a placeholder, not a runnable filename.
- Decode new scratch frames/WAVs only within analysis scope; never write into or replace originals.
- Use `vision_analyze` for extracted stills and an available playback/audio analysis route for the actual performance.
- Review transcript, picture, and sound together; a loud peak is only a candidate, not a good clip by itself.
- Mark source-relative IN/OUT, absolute timeline frames, handles, summary, payoff, confidence, and rights status.
- Keep source time, WAV-relative time, and timeline time distinct; retimes need their own mapping.
- Prefer one continuous source range for an initial highlight; mark any discontinuous assembly explicitly.
- Inspect exact IN/OUT frames and listen through both boundaries after every range adjustment.

## Audio-led assembly
- Build the idea first: premise, setup, turn, and final reaction/button.
- Keep the cause of a reaction; removing it may make the person seem angry at the wrong target.
- Preserve meaningful pauses and breathing space so speech stays natural and the audience can process it.[6]
- Compress repeated navigation, loading, redundant explanation, and genuine dead air only when they carry no setup or payoff.
- Hold an expressive avatar reaction when it is the point; do not cut merely to increase cut frequency.
- Do not repair a broken sentence with a flashy cutaway; rewrite the selection instead.
- Review the assembly without SFX, zooms, music, or animated text before sweetening.

## Choose the trim by what must stay fixed
| Need | Technique | Invariant to verify |
|---|---|---|
| Move a boundary between neighboring shots | Roll | Combined span remains; both source handles are valid |
| Change which source moment appears in a fixed slot | Slip | Record IN/OUT and duration remain unchanged |
| Remove time and close the downstream gap | Ripple trim | All intended linked/downstream material follows, nothing protected moves |
| Move a shot while adjusting its neighbors | Slide | Selected shot's content/duration and surrounding continuity remain valid |
| Hear the next speaker before seeing them | J-cut | Audio leads incoming picture without false speaker attribution |
| Hold outgoing speech while showing a reaction | L-cut | Picture changes first; reaction is truthful to the speech |

These operation meanings are documented in lessons 2–3; UI operations are not automatically scripting APIs.[6]
- The book documents `T` for Trim Edit mode, but only use a shortcut after confirming the live keymap and page.[6]
- Keep linked audio protected unless an intentional split edit requires a scoped exception.
- Preview around the cut, not only the frame under the playhead.
- Do not ripple a finished caption/music layout without explicitly approving and auditing downstream changes.
- If the bridge cannot perform the required edit, name the limitation and consult the current UI/manual; never guess an API or control location.

## Recoverable implementation
1. Present a compact plan: source ranges, story order, tracks, overlays, sound cues, caption scope, and what stays untouched.
2. Use recoverable variants by default; editing originals requires explicit scope and a fresh verified `.drp` backup.
3. Dry-run source-to-pool mappings and range calculations before placement.
4. Prove the smallest representative timeline through save, item readback, and rendered/viewer QC before batching.
5. Begin structural mutations at roughly 1.2-second spacing and serialize live Resolve calls; read back after each batch.
6. Keep cue placement idempotent using exact source path, record frame, and target track.
7. Load `references/automation-safety.md` for the existing build-specific enrichment, render, and restoration traps.
8. Never turn a relink, proxy, transcode, original promotion, archive deletion, or database patch into an implied subtask.

## Finish in separate passes
- Story pass: a new viewer can identify who, what happened, and why the reaction matters.
- Timing pass: complete words, natural breath, setup before payoff, enough time to perceive the reaction.
- Caption pass: exact Thai meaning, names, cue frames, native subtitle track, phone-size readability.
- Sound pass: speech remains intelligible; music/effects earn their place and do not mask punchlines.
- Framing pass: avatar head, face, hands where relevant, headroom, gameplay evidence, and captions coexist.
- Delivery pass: approved raster/FPS, valid streams, full duration, clean first/last frames, no offline composite.
- A pass can be deferred by scope; mark it unverified rather than claiming a finished edit.

## Practical learning exercise
1. Use a permission-cleared short source and identify one self-contained turn or reaction.
2. Produce a source-time cutlist and explain each proposed deletion.
3. Make an approved rough-cut variant with no decorative additions.
4. Compare a roll, a slip, and a ripple on recoverable practice variants; report exactly what stayed fixed.
5. Compare a straight cut with a justified J/L cut without moving the reaction out of context.
6. Add only the captions/framing/audio authorized for the exercise and review at actual playback speed.
7. Export only when requested; measure technical output and record unresolved editorial questions.
- This is an exercise design, not a claim that a project has already been edited or that one rhythm suits every creator.

## Acceptance check
- Compare every target against its source/range manifest and approval scope, then watch/listen to the actual cut.
- Require unchanged protected tracks, verified captions, successful `ProjectManager.SaveProject()`, and restored UI state for an edit.
- For a render, also require Complete job status, nonempty file, `ffprobe` agreement, and visual/listening QC.
- Report separate verdicts for structural correctness, readability, listening, and publication readiness.

## Sources

[6] https://documents.blackmagicdesign.com/UserManuals/DaVinci-Resolve-20-Editors-Guide.pdf?_v=1757574011000
