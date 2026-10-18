# House rules and release skills (2 skills)

## `house-style` — the accumulated editorial corrections (186 lines, v0.3.0)

Load before assembling, restructuring, or refining any cut so the same note does
not have to be given twice. `docs/guides/` describes editing in general; this
file describes how *this editor* wants it done.

**Capture protocol** — when the user corrects an editorial decision, fix it and
then add the rule here. A useful entry has three parts: the rule (stated as an
instruction, not an observation), why (in the user's terms), and the trap.
Write rules that are falsifiable — "cut on motion" is a rule, "make it feel
dynamic" is not. One-off situational corrections do not belong here. Edit an
entry when it turns out wrong or too broad: a stale rule confidently followed is
worse than no rule.

**Captured rules (as of v0.3.0):**

- **Pacing / Thai captions** — at most three short words and about 14 Thai
  characters per caption, ≤1.5 s on screen, shorter holds when speech is faster.
  Write Thai captions with no spaces between Thai words; spaces only around Latin
  terms. The trap is using spaces to show word grouping.
- **Subtitle track only** — dialogue captions go on native Resolve Subtitle
  tracks only. Not Text+/TextPlus, not Fusion titles, not text on video tracks.
  Historical Text+ captions are not permission to create more. A native-track
  preference is a creation rule, not permission to modify every historical Text+
  timeline. Confirm migration targets, preserve protected horizontal versions,
  and after verifying exact text and frames **disable** a captions-only legacy
  track rather than deleting its clips. Never disable a mixed track of titles and
  overlays. When the user handles fonts/styles, do not revive an older font plan.
- **Saved subtitle font presets** — load the exact approved saved Subtitle-track
  preset; do not guess font, size, stroke or position. Discover the saved name and
  source library; ask before substituting `Mitr Font` for `Mitr-Font`. A font
  request alone does not authorize SQL.
- **Names, numerals, cue length (Katy404 / KT)** — the channel name spoken as
  "เคที" is written **เคที่** (with the tone mark), never Latin "KT". Spoken
  numerals appear as digits ("1,950", "10,000") but get their real spoken
  duration: a digits-only cue defaulted to a 0.3 s hold while the speaker needed
  ~1.5 s, so the caption vanished mid-word. Check each cue's end against the audio.
- **Reaction GIFs and VTuber zoom framing** — GIFs get the saved **"vdo"**
  Inspector values (`scripts/apply_vdo_preset.py`), not a computed corner slot;
  place GIFs outside VTuber Zoom ranges. For a corner avatar prefer a frame with
  no black band and a slightly off-centre avatar over a perfectly centred frame
  with a visible black strip; keep the ahoge inside frame with a few percent of
  headroom. Delete only copies/variants you created or the user names; a backup
  `.drp` comes first.
- **VTuber Zoom Focus (Thai, 4 rules)** — confirm the subject is Armigon in every
  range before adjusting an `Adjustment Clip` (if it is another character, return
  that range's focus to neutral and record why); keep the full frame with no added
  black band or blur and no transform-induced shake (check `Center`/`Size`
  keyframes and `MotionBlur`, and view real frames at several points — one still
  does not prove there is no shake); keep Armigon dominant near centre, head to
  chest/hands, ~5–8% headroom, never cropping head, face, horns, ears, ornaments
  or hands needed for reactions; compare the same frame with the `Adjustment Clip`
  on and off to separate pre-existing crops/overlays from focus damage, and never
  report that a focus fix repaired source material that was already cropped.
- **Rejected by default** (seeded from `resolve-rough-cut`): titles, captions,
  text cards, transitions, effects and speed ramps, music beds, and grading on a
  cut that was asked for as an assembly.
- Sections still marked `_Not yet captured._`: shot selection, cut points,
  structure and openings, delivery conventions.

**Where personal grading taste lives**: not here. Colour and look preferences
live in the user-level `colorist-assistant` skill and in persistent memory, so
this file can travel with the repository.

## `agent-skill-repo-release` — version, tag, push, publish (122 lines)

Triggers: "git push and git add release", "เพิ่ม Releases ด้วย", "release new
version", "update skill and push" in a repo that ships `.agents/skills/`,
"git push ทั้งหมด" with many untracked files.

Procedure: inspect state through the `terminal` tool (`git fetch -q && git status
-sb`, `git tag`, `git log --oneline -5`, `gh release list`, read `VERSION` and
`CHANGELOG.md` with `read_file`, copy the format of the latest release body via
`gh release view <tag> --json body -q .body`) → "update skill" in a repo with no
skills yet means copying the current Hermes copies of the relevant skills into
`.agents/skills/<name>/` including `references/` and `scripts/`, excluding
`__pycache__`; search the copies for usernames, tokens and passwords before
publishing → choose the next minor after the highest tag (tags win over a stale
`VERSION`; no tags = `v0.1.0`) → edit `VERSION` with `patch`, add a `## vX.Y.Z`
section at the top of `CHANGELOG.md`.

Pitfalls worth remembering:

- A working tree can carry staged deletions from an earlier checkout, and a
  path-scoped `git add` + commit still picks them up — group them with
  `git diff --cached --name-only --diff-filter=D | wc -l` **before** committing.
- Never stage raster stills or media; verify with a count of staged
  `png/jpg/mp4/mov/drp` files and a >1 MB sweep, and report 0/0.
- `.gitignore` `*.drp` matches at any depth; use `*.drp` + `!backups/` +
  `!backups/*.drp` and verify with `git check-ignore -v` and `git add -n <path>`.
- Scan **staged additions** for `gho_`, `ghp_`, `sk-`, `AKIA`, private-key
  headers — not the whole repo.
- `gh release view --json` rejects unknown fields (`isLatest` is not a field);
  use `gh release list` for the Latest marker.
- A release that adds `VERSION`/`CHANGELOG.md` must re-run the manifest/validator
  step and stage the regenerated manifest in the SAME commit.
- Moving a pushed tag: get the user's OK, then `git tag -f vX.Y.Z <sha>`,
  `git push origin :refs/tags/vX.Y.Z`, `git push origin vX.Y.Z` — before creating
  the GitHub Release, which binds to the tag. Never amend or force-push `main`;
  add a follow-up `chore(release): …` commit.

Verification: `git ls-remote --tags origin vX.Y.Z` shows the intended sha,
`git show vX.Y.Z:VERSION` prints the new number,
`gh release view vX.Y.Z --json isDraft,url` reports `isDraft:false`.

## The repo-level rules these two skills assume (from `AGENTS.md`)

- **Allowed channels: Resolve MCP + Resolve Python API only.** Strictly
  prohibited: screenshots/GUI automation, keystroke macros, browser automation,
  non-Resolve editors. Permitted exceptions that are not Resolve control:
  `ffprobe`/`ffmpeg` for read-only media analysis and render QC, and last-resort
  offline SQLite inspection/patching when Resolve is closed and a verified `.drp`
  backup exists.
- **MCP first, scripting second** — and a mandatory `MCP-GAP: <tool/action checked>
  -> <reason for fallback>` line before writing any script.
- **Track architecture** — 16:9: V1 base footage, V2 `VTuber Zoom` (Adjustment
  Clip + Fusion Transform), V3 `REACTIONS`, Subtitle 1 native Thai. 9:16: V1
  `Game Top`, V2 `REACTIONS`, V3 `VTuber Bottom`, V4 `VTuber Zoom`, Subtitle 1.
- **VTuber zoom focus QC gate** — confirm the subject is Armigon before zooming;
  full frame with no black edges or added blur; read `Center`/`Size` keyframes and
  `MotionBlur`; A/B the same frame with the Adjustment Clip on/off.
- **DRT transfer pattern** for safe track injection — export DRT
  (`timeline.Export(path, resolve.EXPORT_DRT, resolve.EXPORT_NONE)`), inject with
  `scripts/drt_focus_track.py`, re-import with
  `media_pool.ImportTimelineFromFile`, then read back all original tracks against
  a baseline. Direct `InsertGeneratorIntoTimeline` can misplace clips across
  track indices on complex timelines.
- **Safety** — never overwrite source footage; export a verified `.drp` backup
  before batch operations; work in recoverable variants (`_focus_variant`, `_bak`)
  and only touch original masters on explicit instruction.
- **Verification and handoff** — `ProjectManager.SaveProject()`, read back every
  modified target, restore the original project/timeline/playhead/page/folder/
  track state, verify each batch item. Renders need Complete status, a nonempty
  output, ffprobe video/audio verification, and visual QC.
- **Discover before writing** — live project, timeline IDs, exact Resolve build,
  resolution, both frame-rate settings, media paths, and existing video/audio/
  subtitle coverage. Preserve the approved aspect ratio; never auto-convert 16:9
  to 9:16.

## Trust and loading (why a project skill may not fire)

- Project skills are discovered but not loaded until the repo is trusted:
  `hermes skills trust` (from inside the repo or with an explicit path),
  `hermes skills untrust` to revoke. Trusted roots live in
  `skills.trusted_project_dirs` in `~/.hermes/config.yaml`.
- `skills.project_discovery: false` disables scanning and the notice entirely.
- `skills.guard_agent_created: true` re-enables the dangerous-pattern scanner on
  agent skill writes (off by default); `skills.write_approval: true` stages every
  agent skill write under `~/.hermes/pending/skills/` for
  `/skills pending|diff|approve|reject`.
- In-repo authoring authority is `superpowers-writing-skills`; the Hermes-side
  conventions for a `SKILL.md` are in the profile's
  `hermes-agent-skill-authoring` skill.
