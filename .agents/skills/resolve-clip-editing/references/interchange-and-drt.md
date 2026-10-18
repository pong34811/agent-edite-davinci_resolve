# Interchange formats and offline `.drt` authoring

Source: `docs/guides/headless-edit-loop.md` (measured Studio 19.1.3.7, GUI and
`-nogui`, 2026-08-01), `docs/guides/native-drt-authoring.md`,
`docs/kernels/timeline-edit-kernel.md`.

## Format selection — there is no single best format

**Mode does not matter:** every measured result is byte-identical between GUI and
`-nogui`. Choose a format on its properties, never on whether you have a UI.

| what you need | format | why |
|---|---|---|
| **Full fidelity**, media staying put | **DRT** | the only format that kept *everything*: transforms, colours, flags, item and timeline markers |
| **Iterative loop**, media staying put | **FCP7 XML** or AAF | no media duplication, controllable timeline name — DRT has neither |
| **Media has MOVED** (real conform) | **FCP7 XML**, AAF, FCPXML 1.10 | the only three that relink. **DRT, OTIO and EDL all fail** |

Payload/tie-breakers for the same four-item test timeline:

| format | size | links from pool | name controllable | notes |
|---|---|---|---|---|
| **fcp7xml** | 42 KB | yes | yes | the recommended loop format |
| **aaf** | 315 KB | yes | yes | same behaviour, 7x the payload |
| **edl** | 512 B | yes | yes | frame-exact for a *flat single-track* conform of timecoded media only |
| drt | 19 KB | n/a (always re-imports) | no | native; one-shot hand-off |
| otio | 85 KB | **no — offline** | yes | needs `importSourceClips: True` |
| fcpxml_1_10 | 3 KB | yes | yes | writes a bundle directory |

What each format actually keeps on a real cut (2 video tracks, audio, per-item
transform, clip colours, flags, item and timeline markers):

| format | cut | tracks | transform | colour | flags | item markers | timeline markers |
|---|---|---|---|---|---|---|---|
| **drt** | kept | kept | **kept** | **kept** | kept | **kept** | kept |
| fcpxml_1_10 | kept | **lost an audio track** | kept | lost | kept | lost | lost |
| fcp7xml | kept | kept | lost **only FlipX** | lost | kept | lost | lost |
| aaf | kept | kept | **lost: all reset to defaults** | lost | kept | lost | kept |
| otio | **lost: source** | kept | kept | lost | lost | kept | kept |
| edl | **lost** | **1v1a** | n/a | lost | lost | lost | lost |

Two details worth having: **AAF resets the entire transform to defaults** while
**FCP7 XML preserves zoom, pan and rotation exactly** (drops only `FlipX`) — a
whole-dict comparison calls both "lost". Crop returning as 39.999936 against 40.0
is unit round-tripping, not loss. **FCPXML 1.10 silently drops an audio track**
(2v2a in, 2v1a out).

Relink test (media directory renamed so every baked-in path is dead): fcp7xml
3/3, aaf 3/3, fcpxml_1_10 3/3; drt 0/3 (items stay on the dead path); edl 0/3;
otio import returned `None`. "Frame-exact" stays true even where nothing
relinked — **the cut survives offline**, so a failed relink leaves a correct
timeline you can relink by other means rather than a wrong one.

## The round-trip traps, each measured

- **A repeated `timelineName` silently stops working.** Importing the same file
  three times with the same name: 1 succeeded, 2 and 3 **returned `None`** — no
  error, no exception. Make the name unique per iteration.
- **A unique `timelineName` is still not enough — the file's internal name wins.**
  Resolve honours the sequence name *inside* the interchange file over the option
  (issue #171, Studio 21.0.4.5): export → edit → re-import as `CUT_v002` while the
  XML still says `CUT_v001` and Resolve hands back the **existing** `CUT_v001`, so
  the loop operates on one timeline forever. Bump `<sequence><name>` inside the
  XML each iteration, or use `timeline.import_timeline_checked`, which rewrites
  the internal name and errors instead of reporting success on a collision.
- **DRT ignores `timelineName`, `importSourceClips` and `sourceClipsFolders`** —
  all invalid for DRT; passing them gets a failure that says nothing about the
  format. The imported timeline is named after the **file** and repeated imports
  auto-uniquify (`iter`, `iter 2`, `iter 3`). Because `importSourceClips` cannot
  be false, each DRT import **adds another copy of the source media** (three DRT
  imports grew the pool by four items, against one per import for the XML route).
  DRT is excellent for a one-shot hand-off and wrong for a loop that runs 100 times.
- **FCPXML 1.10 exports a *directory*, not a file.**
  `Timeline.Export(path, EXPORT_FCPXML_1_10, EXPORT_NONE)` returns True and creates
  a `.fcpxmld` bundle containing `Info.fcpxml`. `path.stat().st_size` reports the
  directory inode (96 bytes) so a size check reads it as near-empty, and
  `ImportTimelineFromFile(path)` fails because the path is a directory. Point the
  import at the member: `inner = next(Path(export_path).glob("*.fcpxml"))`.
- **OTIO with `importSourceClips: False` arrives fully offline** — with
  `reuse_pool` the timeline rebuilds with correct structure and all items offline.
  Use `importSourceClips: True` with a `sourceClipsPath` if you want OTIO.

## The iterative loop, headless

```python
options = {
    "timelineName": f"CUT_v{iteration:03d}",   # MUST be unique per import
    "importSourceClips": False,                 # reuse the pool, do not re-import
    "sourceClipsFolders": [pool.GetRootFolder()],
}
timeline = pool.ImportTimelineFromFile(path, options)
```

Verified: five consecutive imports all succeeded, source in-points preserved
exactly, and **no media duplicated** (the pool grew by exactly one item per
import — the imported timeline itself).

Precondition: **headless requires external scripting to connect without the GUI.**
Preflight in 30 seconds before committing a loop to `-nogui`:
`python scripts/resolve_headless.py run -- python -c "print('ok')"` — a clean `ok`
proves boot-to-scriptable; `FAILED: no scripting response` now cleans up the
instance it started, and `stop --force` TERM/KILLs a wedged one (unclean: expect
project locks and a slow next boot).

Rules for the whole loop: **never call `SaveProject()` without checking the
project name** (on the never-saved `Untitled Project` it blocks the entire
application in both modes and needs a force-kill); **verify structure, not return
values** — every finding above involved a call that returned success; teardown
order is `CloseProject` → `LoadProject(something named)` → `DeleteProject`.

## Native `.drt` authoring (advanced server, offline)

`drt.assemble` / `drt.assemble_from_interchange` write a **native-schema `.drt`**
— a real Resolve project archive `ImportTimelineFromFile` accepts — entirely
offline. Unlike XML/AAF/OTIO it arrives **linked and rendering**, because it
carries native media-pool descriptors captured from a live Resolve.

**Core doctrine: readback is blind, render is truth.** A structure can import
fine, read back fine through every API, and render black or silent. Structural
readback cannot detect: media clips without native pool descriptors (black),
Fusion title comps whose bytes were edited offline (black), audio clips cloned
from a donor with the donor's identity (silent), audio tracks added by cloning
(silent — no Fairlight strip), or a timemap in the wrong generation's encoding
(plays at 100%, no warning).

**Prerequisites:** per media file, once — `media_pool.capture_media_template`
(live Resolve required once), which caches the file's native pool `<Element>` +
MediaRef under `~/.config/davinci-resolve-mcp/media-templates/`. After that, all
assembly for that file is fully offline. Pass `targetAppVersion` (e.g. `"19.1.3"`)
when the importing host is pre-21.

**The laws:**

- **Fusion comp cache law** — on 19.x an imported comp renders only via the disk
  cache keyed to the comp blob's exact compressed bytes, so any offline byte
  change renders black. Offline title *text* cannot be authored for pre-21 hosts:
  assemble everything else offline, then set title text post-import with
  `timeline.set_title_text`. Generators are exempt (plain `Sm2TiGenerator`, no
  comp) and render everywhere.
- **Fairlight strip law** — audio tracks cannot be grown offline: the per-timeline
  Fairlight model holds one mixer strip per audio track, and a cloned track
  without a strip is mute. The r19 template is captured with 8 mono audio tracks;
  placements beyond track 8 refuse with instructions to re-capture a bigger one.
- **Timemap generation split** — `Sm2TimeMap` keyframes are protobuf on 21 but
  keyed-dicts on 19, and 19 *silently ignores* the protobuf form (clip plays
  100%). Reverse is the same map with the Y endpoints swapped.
- **Ramps are more keyframes, but easing is a crasher** — the keyframes' `interp`
  field must stay **0**: an `interp=2` keyframe crashed Resolve 19.1.3 outright
  on import. Eased ramps are not authorable.
- **Freezes are a third shape** — a flat line in the retime's *frame* domain reads
  back frozen but **renders moving**. The real freeze is a flat line in *seconds*:
  `YMin = YMax = Y = frozen position` (source frame / fps), `XMax = 60000` (a
  fixed sentinel), and the clip's `<In>` left empty.
- **Gaps are legitimate** — record gaps between placements render as clean black,
  so sparse turnovers assemble without synthetic filler.
- **Timeline origin** — template timelines start at frame 86400; clips placed
  before the origin are silently dropped on import.
- **Dissolve geometry / edge law** — a transition's rendered span follows
  `<Start>`/`<Duration>`; `AlignmentType` is cosmetic. **The clip boundary must
  sit strictly inside the span** — an edge-aligned span renders inert. EDL
  dissolves span `[cut, cut+dur)` with the boundary shifted +dur/2 (CMX
  convention); handles must follow the actual span.
- **Fade law** — a transition needs a physical item on BOTH sides of its junction;
  a hand-authored single-sided element refuses to import, and Resolve's own EDL
  importer silently drops dissolves involving the `BL` reel. The authorable form
  is a real clip↔Solid-Color-generator dissolve.
- **AAF overlap law** — an AAF transition CONSUMES record time: the incoming
  component legitimately overlaps the outgoing by the transition duration.

**Delivered-`.drt` verification checklist:** `timeline.import_timeline_checked`
(expect `linked == total` for media; for `.drt`/`.drp` it also cross-checks the
files items actually link against and warns `cross_link_warning` — `linked ==
total` alone cannot see a cross-link) → render a probe range and check frame luma
at cut boundaries, dissolve midpoints (expect the blend average) and retime
windows → RMS per window for audio (silence = `-inf` is a failed placement) →
never trust `created_new: false` (a same-named timeline is returned as "success") →
close the loop with `editorial.verify_roundtrip`, which parses the original
interchange against Resolve's own re-export and returns `pass: true` when the
authored timeline matches event-for-event.

## Offline editorial reasoning (no Resolve open)

- `editorial.parse_interchange` — EDL / OTIO / XMEML natively; **AAF via pyaaf2**
  (multi-layer Avid turnovers included; an honest refuse only when pyaaf2 is absent).
- `editorial.turnover_changelist` — moved / retimed / trimmed / replaced / new /
  gone between two cuts PLUS the junction diff (transitions added/dropped/changed,
  fade in/out, span deltas; CMX carriers and BL fade legs never read as sources),
  with timing silent-lie guards that flag what they cannot verify.
- `editorial.conform_manifest`, `editorial.marker_roundtrip`.
- `drt` — `.drt` timeline file authoring + structural diff.

Use these to answer "what changed between v3 and v4" or to hand a conform an
accurate change list without opening either timeline.
