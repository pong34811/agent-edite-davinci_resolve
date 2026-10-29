# Resolve operating notes for this project

These rules reconcile the imported skills; they preserve previously observed behavior and are not new live tests on the current Resolve session. Read before an edit. Current user instructions take precedence for scope.

## Local skills and activation

Active skills live under `.agents/skills/`: 17 curated core editing skills plus 29 supporting workflow/reference skills. The supporting set includes profile imports and namespaced Superpowers copies; their presence does not prove they were used for a Resolve edit. Hermes officially supports this project-local directory, with project > profile-local > external precedence. The repository must be trusted before automatic discovery. From this directory, the supported command is `hermes skills trust`; then start a new session. Trust was intentionally not changed by the collection task. Reading a local SKILL.md with `read_file` works without pretending that it is already registered. No global skills/configuration or other profiles were modified.

The backend remains the existing `davinci-resolve-mcp` installation. This repository includes skills, manuals and the source-safe contact-sheet helper, not `src/server.py`, its Python environment, Node server or MCP credentials. A command in an imported backend manual must be run from the backend installation, not assumed available here. Probe the actual attached MCP tool catalog first; use the Resolve scripting bridge only when the MCP is shown not to cover the task (see `AGENTS.md` "Tool selection" and `scripts/resolve_preflight.py`).

## Reconciled rules

When you learn a new rule, add a row here (see `.agents/skills/project-learning/SKILL.md`). Script catalogue: `scripts/INDEX.md`.

| Topic | This project's rule | Why |
|---|---|---|
| Tool selection | MCP catalog first; scripting-API script only after a stated `MCP-GAP:` line; shared `scripts/resolve_common.py` | Agents skipped the MCP and wrote ad-hoc scripts, each with its own copy of the connect code. |
| MCP updater path | If `scripts/check_mcp_update.py` reports the configured checkout is missing, verify the active install and correct `.mcp.json` before updating; do not clone or guess a replacement path | A stale Desktop path caused a `FileNotFoundError` before the updater could compare versions. |
| Skill manifest refresh | Keep an existing checksum when `verify_skill_bundle.checksum_matches` accepts it, including LF/CRLF-only differences; rehash only when content truly differs | Raw rehashes on a different checkout platform rewrote 225 valid file hashes in a refresh. |
| Offline intake and gates | Use `prepare_edit.py` and `edit_workflow.py`; see `docs/EDIT-WORKFLOW.md`. Prepared intake, valid plans and reconciled reviewer evidence are separate verdicts; never promote them to live audiovisual QC. | Reusing one manifest and explicit gate reduces repeated probes and prevents missing measurements being treated as passes. |
| Intake cache and coverage | Reject malformed cache/probe/receipt JSON; `--refresh` bypasses probe cache; fingerprint actual selected frame paths; skip Windows symlinks/junctions while allowing cloud placeholders; reject unparsed SRT blocks. | Review reproduced stale sheets for external frame paths, skipped broken cues and junction traversal outside the source tree. |
| Thai cue duration | At most 1.5s, three short words / about 14 Thai characters | Current house style is stricter than the imported subtitle skill's generic 2.2s example. |
| Thai typography | No inter-word spaces; preserve only appropriate Latin boundaries | Token grouping is for timing, not displayed spacing. |
| SRT placement | Empty subtitle track, bare mediaPoolItem payload | Extra placement fields can shift cues to timeline-end plus SRT offsets. |
| Corrected SRT | Remove stale pool cache entry before re-import, then verify style as well as cues | Same-path ImportMedia can reuse old parsed text. |
| Mutation rate | Start with ~1.2s between structural edits, save and verify | A historical 0.35–0.45s append-only delay is not a reliable DeleteTrack/AddTrack/Append batch policy. |
| Backup cleanup | Retain and report archives; delete only with explicit approval and a new verified backup | The rough-cut source said to clean archives automatically; other workflows correctly require permission. |
| Missing illustration source recovery | Before relinking or editing a timeline, inspect its documented project bundle and known generation archive; restore recoverable files at the exact referenced paths, verify bytes/media metadata, then read back online status and all clip ranges. Regenerate only missing sources. | Restoring the original paths brought all 23 Armigon placements online and preserved later user moves without timeline mutations. |
| Restored-media property cache | If Resolve says a restored same-path clip is Online but `GetClipProperty` codec disagrees with `ffprobe`, verify an exported Resolve frame before considering relink/reimport; do not treat cached codec metadata alone as offline evidence. | The rebuilt vertical plate decoded and rendered in Resolve as ProRes 4444 while the existing pool item still reported its former PNG codec. |
| Channel profile script references | Only cite reusable scripts that exist at `scripts/*.py`; describe one-off `scripts/scratch/` helpers by purpose or full nested path. | `test_profiles_reference_only_existing_scripts` checks bare `.py` names against only the indexed top-level scripts. |
| HyperFrames CLI version lookup | If `npx` advertises a latest version that the registry cannot resolve (`ETARGET`), pin the newest available version that runs successfully and record the pin with the deliverable. | The registry advertised 0.8.196 but only 0.8.195 could be resolved for this rebuild. |
| Playback FPS | Read separately from timeline FPS; set in verified Resolve UI if necessary | Playback frame rate is not script-settable in the observed build. |
| API methods | Exact build, installed README/typed stub, then a read-only or isolated probe | Older manuals' blanket API gaps may be stale; do not treat absence from a catalog as proof. |
| Resolve 21.1 reference routing | Read `docs/guides/resolve211-agent-guide.md`; version-scope speed, transition, multicam and DCTL limits; distinguish documented APIs, attached actions and live validation | Older skills denied APIs that the 21.1 stub and current catalog expose; an empty version-gate list does not verify their behavior. |
| Vendor stub hashes | Compare raw bytes and CRLF-to-LF normalized bytes before declaring a stale reference; retain original provenance | The Windows 21.1 stub matched Studio MCP byte-for-byte; its raw CRLF hash differed from the recorded LF hash while normalized content matched. |
| Audio level | AudioVolume in dB on observed builds; enumerate/read back actual properties | Volume/Gain/Level guesses can return False silently. |
| Caption QC | Viewer screenshot or short burn-in render | ExportCurrentFrameAsStill can omit subtitle overlays. |
| Native captions | Subtitle track only; migrate only exact authorized targets | A creation preference does not authorize modifying protected legacy timelines. |
| User-owned styling | If the user handles fonts/styles, verify insertion and report legibility separately | Older font plans or easier SQL styling cannot override the current scope. |
| Playhead readback | Activate each timeline before GetCurrentTimecode; capture fresh state on resume | Inactive timeline reads can return the active timeline's playhead. |
| Page restoration | Serialize live calls; wait and read GetCurrentPage after OpenPage | A True return can precede completion of the page switch. |
| Adjustment Clip | Scripted pilot; lock all original video/audio/subtitle tracks; full range audit and rendered frames | Generator insertion can ripple other track types even when V1 looks unchanged. |
| Zoom Focus QC | ยืนยัน Armigon ทุกช่วง; ตรวจภาพเต็มเฟรม/ขอบดำ/blur; อ่าน `Center`/`Size` keyframe และ `MotionBlur`; เทียบเฟรมเดียวกันเมื่อเปิด/ปิด `Adjustment Clip` | ต้องแยก source crop หรือ overlay ที่บังอยู่เดิมออกจากผลของ zoom และห้ามสรุปว่า motion ไม่มีอาการสั่นจากภาพ still เพียงอย่างเดียว |
| Enrichment sequence | Draft on copies first, verify, then promote into originals; keep one idempotent apply path | Direct-to-original batch edits leave no reviewable stage and cannot be re-run safely. |
| Promotion identity | Match an existing placement by (asset name, record frame) and skip verified items | A rerun after a partial failure would otherwise duplicate clips. |
| GIF conform | Read the appended range and enforce 1.5–2.5s on the real range, allowing a few frames of conform drift | Resolve conformed a GIF 2 frames shorter than the requested hold and a strict equality check aborted a good promotion. |
| Subtitle items | Native subtitle items have no Media Pool entry; never flag them as offline | Treating a legitimate null as a media fault produced ~960 false "high" findings. |
| Thai cue length | Check every cue's end against the audio; numerals and digits-only cues need an explicit end | A "1,950" cue defaulted to 0.3 s while spoken for ~1.5 s. |
| MCP timeline mutators | Expect an auto-archived `Timeline N_archived_vNN` per mutating call; report it, delete only on request | `timeline.add_track` created a copy and left the Media Pool on `Archive`. |
| Preset backup path | Pass `--backup-dir` as an absolute path (now resolved in the helper) | Resolve's ExportProject fails silently on a relative path. |
| Whisper model | `large-v3` on the raw audio; distrust `large-v3-turbo` on game audio | Turbo invented ~20 s of text; check `avg_logprob` and re-run the window alone. |
| GIF hold | Validate every GIF (Resolve 25 fps, >= 1.5 s) before mutating the timeline | A 1-second GIF aborted a run after BGM/SFX were already placed. |
| Zoom framing | Corner avatar: no black band, slight off-centre; keep the hair tip inside | Centre-exact framing shows a band; the first pass clipped the ahoge. |
| Font audit | Scan subtitle cue blobs as UTF-16 as well as ASCII | A track marked Mitr Bold still carried hidden Open Sans metadata in some cues; an ASCII-only audit missed it. |
| Fusion Text+ reads | Read exported `.drp`/DRT, not live Fusion tools, on Aomi-mama-class projects | A live TextPlus read probe hung Resolve (Aomi debut project, 2026-09-30). |
| Archive deletion | Export one fresh verified `.drp`, report the exact files and bytes removed, and say there is no longer a rollback point | Deleting archives on request is fine; deleting them silently is not. |
| Enrichment re-run | After an aborted `apply_enrichment_d22` reset the Media Pool folder and pre-validate GIFs with PIL (>= 1.5 s after conform) | The script imports into its bin and leaves the current folder there before it checks GIF length. |
| Focus insert on 21.1.0.17 | `InsertGeneratorIntoTimeline` goes to V1 (ripples it) if V1 is unlocked and fails if V1 is locked; for N clips on a new track use DRT injection (`drt_focus_track` internals, clone Element per range), import, then set Fusion Transform | `apply_vtuber_zoom --apply` failed at the first insert on day 25; a manual unlocked insert split V1 on the throwaway copy. |
| Enrichment append on one audio track | Two SFX whose trimmed ranges overlap on the same track push the later one to the earlier one's end (day 25: clap 1885 -> 1936); keep SFX >= their trimmed length apart or use another track. `ExportCurrentFrameAsStill` needs an absolute path | `AppendToTimeline` does not overlap on a track; a relative still path returns False silently. |
| DRT import name | `ImportTimelineFromFile(drt, {'timelineName': X})` on 21.1.0.17 names the timeline after the file (`patched`); rename by unique ID right after import and read the name back | A stage keyed on the requested name hit KeyError on the Bunny Girl copy (2026-10-17). |
| Overlay append range | `AppendToTimeline` endFrame is exclusive for MOV video and MP3 audio on 21.1.0.17: pass `endFrame = duration` for back-to-back chapter overlays, then read GetStart/GetEnd | `endFrame = duration - 1` left a 1-frame gap after every chapter overlay. |
| BGM loop splice | Loop a short BGM by finding its repeat lag (spectral self-similarity, then sample cross-correlation) and cutting both pieces at a near-silent frame inside the repeated section; set `SetFades` for the head/tail only | Two pieces can't overlap on one audio track, so a crossfade isn't possible there; a silent-break splice in a repeating section gave no click (Bunny Girl, 2026-10-17). |
| Adjustment Clip head extension | An Adjustment Clip whose head is dragged earlier keeps a Fusion comp sized to its old length ("No frame available for MediaOut1"); a new `AddFusionComp` still fails to render the added head. Rebuild the track from fresh template clips at the hand-set ranges via DRT (`scripts/drt_rebuild_focus_track.py`), then probe-render each range | Bunny Girl V2 clip 5104-5352 rendered only its original 5206+ part (2026-10-17). Tail extension and trimming were fine. |
| Hand-copied zoom clips | Before a final render, rebuild every Fusion Adjustment Clip the user copied, trimmed or extended from fresh template clones via DRT (`assemble.py rezoom2` keeps Inspector-only clips); give every probe render a timeout and `StopRendering` | A copied-then-trimmed clip rendered its first ~40 frames, then failed the full render at 82% and hung a probe at 0% until scripting stopped answering (Bunny Girl, 2026-10-17). |
| Skill manifest refresh | `refresh_skill_manifest.py` / `verify_skill_bundle.py` skip gitignored files (`scripts/scratch/*`) and drop declarations of removed skills; move uninstalled upstream skills out before a release rather than hand-editing the manifest | Scratch files were listed in the manifest, so every scratch edit broke the bundle check (2026-10-17). |
| HyperFrames CLI pin | When `npx --no-install hyperframes` asks for a newer release than the one cached, run the cached `npm-cache/_npx/<hash>/node_modules/hyperframes/bin/hyperframes.mjs` with `node` instead of downloading | A new upstream release (0.8.169) made `npx --no-install` refuse to run the cached 0.8.168 overnight (2026-10-18). |
| 9:16 from a 16:9 VTuber shot | Duplicate the finished timeline, apply `p2_9x16_build.RASTER`, set V1 Zoom = 1920/607.5 and Pan for the face column, re-aim Fusion zooms (1.2x is enough on a narrow frame), then confirm the preset really applied (`load_subtitle_preset_auto` dry run says `already_matches=True`) before burn-in-rendering a short range to measure the subtitle position | The position is not readable from the preset bytes. A UI preset load did not stick, so the first burn-in test measured the default style (y 1500-1620); with Mitr-short-001 applied the cues sit at y ~990-1060 (Bunny Girl, 2026-10-18). |
| Resolve Thai ASR | Set `transcriptionLanguage` to `th` (`Thai` is rejected) before `MediaPoolItem.TranscribeAudio`; if a long clip degrades into a repeated token, cut that window to a WAV, import it into a scratch bin, transcribe it alone and delete the bin | Auto-detect returned English; the 95 s pass repeated "ฟรรรม" over 61-89 s while the 32 s window alone came out clean (Bunny Girl ep2, 2026-10-18). |
| DRT zoom template without Fusion | `.hermes/day23-drt/template.drt` Adjustment Clips import with no Fusion comp and no Inspector properties; run `AddFusionComp`, add one Transform between MediaIn/MediaOut, then set `window_transform` values and read back | `retune_vtuber_zoom` failed "clip has no Fusion comp"; `SetProperty('ZoomX')` read back 0 (Bunny Girl ep2, 2026-10-18). |
| Preset auto relaunch | After `load_subtitle_preset_auto --apply`, if the relaunched Resolve shows the project but scripting returns None, ask the user to quit and reopen Resolve; then confirm with the dry run (`already_matches=True`) | The script's relaunched instance never answered scripting for 15+ minutes; a user restart fixed it (2026-10-18). |
| Mix headroom | Measure the source dialogue peak first; with a -1.2 dBFS voice, BGM -19 dB + SFX reached +0.01 dBFS, so drop A1 by 1 dB rather than the SFX | Lowering the whoosh 2 dB did not move the peak; A1 -1 dB gave -0.6 dBFS / -15.2 LUFS (Bunny Girl ep2). |
| BGM gain by script on 21.1 | `SetProperty('AudioVolume', dB)` works on 21.1.0.17 (readback and render agree) although the MCP api_truth ledger says audio volume is not scriptable (21.0); a WAV pool item has empty `Frames`, so take its length from `Duration` | Sakuyako 2026-06 BGM: -31.1 dB set, rendered residual -40.8 LUFS vs -40.7 target (2026-10-30). |
| Reaction GIF length and reused SFX | Probe each GIF's frame count/fps before planning (`ffprobe -count_frames`) and de-duplicate the `ImportMedia` path list when one SFX is placed several times | 6 of 15 cute GIFs ran under 1.5 s (5-13 frames), and importing `Minecraft Click.mp3` three times would fail the import-count check (Katy404 day 26, 2026-10-18). |
| Replacing a placed media file | Never overwrite a file that is already in the Media Pool; write the new render under a new name (`ch01b.mov`), delete the old timeline clips and pool items, import the new file and place it at the same record frames | Overwriting `ch01.mov` in place made the 9:16 render fail at 0% with "Error decoding full resolution media" (Bunny Girl ep2, 2026-10-18). |
| 9:16 zoom vs subtitles | With `Mitr-short-001` (cues at y ~990-1060) and the face column filling the top, a top-anchored Fusion punch-in pushes the chin into the subtitle line; use 1.1x (not 1.2x) and keep slam words at y >= 1160 and the info band at y >= 1520 | At 1.2x the chin dropped onto the cues, and slam words at y 1100 touched them (Bunny Girl ep2 9:16). |
| Thumbnail avatar cutout | `hyperframes remove-background` (human matting model) cannot cut out an anime VTuber: it dropped the torso and ears. Use the uncut frame (16:9: avatar right + left gradient mask; 9:16: sharp frame low with a top fade into a blurred plate) unless a real cutout PNG exists | Bunny Girl ep2 cover, 2026-10-18. |
| Red hook on a dark cover | Give a `#EC1C24` hook a white outer stroke outside the black stroke; red on dark purple vanished in the grayscale/squint previews | Bunny Girl ep2 cover QC, 2026-10-18. |
| Chapter wipe vs speech | Give every full-screen chapter wipe its own silent gap (1.6 s for the 1.55 s Pop Kinetic wipe): split V1/A1 at the chapter's first word, push later segments right, fill the V1 gap with the 1.6 s before the cut (hidden by the wipe) and leave A1 empty; shift zooms/subs/SFX by the chapter offset and re-render overlays with the wipe in the gap | User: speech started before the wipe finished (Bunny Girl ep2.5, 2026-10-23); `scripts/scratch/bunny_ep25/assemble_ep25_v2.py`. |
| Resolve launched by the agent | Never start Resolve as a child of the agent's shell (`subprocess.Popen(Resolve.exe)`); that instance never answered scripting. Launch through `explorer.exe` (now done in `load_subtitle_preset_auto.py`) | Two relaunches after the preset patch stayed unscriptable until Resolve was closed and started via Explorer (2026-10-23). |
| Resolve crashed or hung mid-edit | Run `python scripts/resolve_recover.py --project "<name>"` yourself (user-authorised 2026-10-28): it restarts Google Drive if the project's library path is gone, force-closes only a hung Resolve, relaunches via Explorer, restarts once if the library is missing from `GetDatabaseList`, and reopens the project. Then re-verify the item that was in flight and continue the batch | Sakuyako SRT batch: Google Drive for desktop stopped, `G:\My Drive\Projects\Resolve Project Library` vanished, `SaveProject` returned False on #80 and Resolve closed; the relaunched Resolve listed only `Local Database` until it was restarted after Drive was back. All 64 earlier saves survived; #80 lost its unsaved track. |
| Setters right after a relaunch | Confirm `SetCurrentTimeline` / `AddTrack` / `AppendToTimeline` by reading state back, not by the return value | After the 2026-10-28 relaunch `SetCurrentTimeline` returned None while it had switched the timeline; `GetCurrentPage`/`OpenPage` also returned None. |
| SaveProject returns False | Check that the project library's drive is mounted before retrying; stop the batch | Returned False just before the crash above. |
| `preserved_state` after many SetCurrentTimeline calls | Re-read the active timeline at the end of a batch and set it back explicitly if it differs | A 16-timeline replace batch ended on the last timeline it touched although `preserved_state` wrapped it (Sakuyako, 2026-10-28). |
| Replacing a subtitle track | `DeleteTrack('subtitle', 1)`, confirm the count is 0, then import the corrected SRT under a NEW path and append to an empty track | 27 timelines replaced this way with exact cue/frame readback and unchanged V1/A1 (Sakuyako, 2026-10-28). |
| Gains after a preset DB patch | Re-read clip `AudioVolume` (and any edit made shortly before) after `load_subtitle_preset_auto --apply`; reapply and save if they reverted | 7 of 8 A1 gains set to -1.5 dB came back as 0 dB after the patch; the render peaked at -0.0 dBFS again (ep2.5, 2026-10-23). |
| Subtitle burn-in by script | Set `ExportSubtitle: True, SubtitleFormat: 'BurnIn'` in `SetRenderSettings`; a plain render has no subtitles | ep2.5 v2 test came out without subtitles (2026-10-23). |
| User hand-trims speech after a gap | When the user ripples A1/V1/subs earlier inside a chapter (trimming a word head) but leaves V3, re-read every track, keep the overlay's wipe piece, re-place the speech piece at local 96+D at the cut, shift later chapters by -D, and end BGM/V3 with V1 so no black tail remains; check slams within 1-2 frames of their words | Happened twice on Bunny Girl ep2.5 (22 and 20 frames, 2026-10-23); the user approved this fix (`shift_v3_gfx.py`, `align_v3_ch09.py`). |
| Whisper VAD drops speech | After the full `asr_words_th.py` pass, re-run overlapping 8-10 s windows alone with beam 8 and `vad_filter=False` (`scripts/scratch/d26/window_words.py`) and compare text and coverage | The VAD pass silently skipped the whole 46-55 s outro of Katy404 day 26; the windowed pass recovered it and the channel name เคที่ (2026-10-18). |
| Cue edges on a gated mic | When the voice drops to digital silence between phrases (-180 dB floor), take cue starts/ends from 20 ms RMS speech edges, not Whisper token times | Whisper token times drifted 0.3-1.5 s at pauses (a "ไม่" smeared across a 1.8 s silence); energy edges were exact (Katy404 day 26). |
| Resolve ASR on short Thai clips | `transcribe_audio` with `transcriptionLanguage=th` is a cross-check only; set the setting back to `auto` afterwards | It got names and numbers right (เคที่, 2,120) but degraded into a repeated "กัน" after 30 s of a 57 s clip (day 26). |
| Split 25 fps GIF on a 60 fps timeline | A GIF piece of an odd record length (15 frames) cannot be re-appended: 6 source frames conform to 14, 7 to 16. Re-place a split GIF as one continuous source range matching the total record range, and check the duplicate's end frame | The 9:16 copy came out 1 frame longer than the original (day 26). |
| QC render size | `focus_qc_frames.py` renders 1280x720 by default; pass `--width 1080 --height 1920` on a 9:16 timeline | The first 9:16 QC render was squashed to 16:9. |
| Render length past the audio | With ExportAudio on, 21.1.0.17 stopped the render where V1/audio end (3031) although a GIF ran to 3108 and MarkOut was 3107; a video-only render gave all 3108 frames. Count output frames against the timeline and report a dropped tail | Katy404 day 26 9:16 delivery, 2026-10-18. |
| Drive manifests | Enumerate `G:` asset roots with `os.scandir` into a manifest | `ls` on Drive stalled over 2 minutes. |
| Still image on a long track | A PNG still appended with `AppendToTimeline` is capped at 300 frames and ignores `endFrame`; for a full-length plate use a short MOV (PNG codec, alpha) in back-to-back pieces with exclusive `endFrame` and read back every piece | The last still piece ran 273 frames past the timeline end (Armigon 9:16 plate, 2026-10-24). |
| Page after QC render | Read `GetCurrentPage()` after `focus_qc_frames.py` and reopen the user's page | Resolve was left on Deliver after three QC renders (2026-10-24). |
| Leftover QC render presets | `focus_qc_frames.py` saves a `focus-qc-<ts>` render preset and never deletes it; delete the ones created in the session with `DeleteRenderPreset` | 11 stale `focus-qc-*` presets had piled up by 2026-10-24. |
| Full 9:16 render hang | A full 10,827-frame 1080x1920 H.264_NVIDIA render (ProRes 4444 alpha overlays + PNG-codec plate MOV, burn-in subtitles) hung Resolve 21.1.0.17; Windows closed it at 12:34 and nothing was written. Before retrying, re-read every track (the relaunch showed A2 changes) and render a short range first | Armigon 9:16 preview, 2026-10-24. |
| Case-insensitive delete | On Windows never `rm -rf` a path that differs from an existing one only by letter case; fix a mis-cased folder with a two-step rename and delete only exact files you created | `rm -rf .herMES` deleted the whole `.hermes/` (plans, ASR, backups of several jobs) on 2026-10-24. |
| Repo Python and scripting | Run repo scripts with `py -3.13`; scripts that import `scripts.*` run as modules (`py -3.13 -m scripts.load_subtitle_preset_auto`); `connect_resolve()` returns the Resolve object (no `.GetResolve()`) | Default `py` 3.14 lacks PIL/numpy/faster-whisper/pythainlp; a direct run failed `cannot import name ... from 'scripts'`; `r.GetResolve()` returned None and was misread as "scripting unavailable" (Bunny Girl ep3). |
| Thai names in calls | Check project IDs instead of retyped Thai names; find episode folders with a glob (`bunny girl/3.*`) | A retyped name made `load`/`export_project` fail silently three times (ep3, 2026-10-24). |
| HyperFrames assets and background renders | Copy gsap 3.14.2 (jsdelivr) and Mitr Bold/SemiBold/Medium from the per-user font folder `%LOCALAPPDATA%\Microsoft\Windows\Fonts` into each job's `assets/`; in background terminal jobs call `node.exe`, not `node` | Mitr is installed per-user, not in `C:/Windows/Fonts`; the MSYS `node` wrapper exits "stdin is not a tty" without a terminal (ep3). |
| Source frame of a timeline item | Read source frames with `GetLeftOffset()`; `GetSourceStartFrame()` truncates seconds x fps | A segment appended at source 1960 read back 1959 (32.666... x 60) and stopped a correct base build (ep3, 21.1.0.17). |
| Fusion values after a reload | Compare Fusion Transform inputs with a tolerance after `load_subtitle_preset_auto --apply` | The reload returned Size 1.35135135135135 for 1.3513513513513513, so a strict `==` reported all 7 zooms changed when none had (ep3). |
| Phrase times on an open mic | Anchor phrase starts and chapter cuts on a -40 dB / 80 ms silence map even when the mic is not gated, and put a wipe cut inside a measured pause <= 0.15 s before speech | Whisper's Thai first-token times ran 0.2-0.5 s early after pauses (`เหตุผลแรก` at 15.80 s, signal silent to 16.35 s); extends row 78 (ep3). |
| Slams vs zooms and subtitles (16:9, 1.35x) | During a zoom the tray wrist sits near x 360 y 800 inside the slam zone, so keep 150 px slams out of zooms; keep a slam's right edge at x <= ~570 when a long centred cue can be on screen, and check burned-in frames at the widest overlapping cue (`scripts/scratch/bunny_ep3/qc_slam_subs.py`) | Latin `Bunny Girl!` at 104 px reached x ~688 and touched the cue `นี่แหละคือ Bunny Girl` (starts ~x 680); overlay-only composites cannot show it (ep3, fixed with size 84). |
| Restoring the playhead after a render | After `OpenPage('edit')`, `SetCurrentTimecode` can return True yet read back the render range's last frame; wait ~1 s, set it again and read it back | Restoring 00:00:15:08 after a `focus_qc_frames` render read back 00:00:15:29 until it was re-set (ep3, 21.1.0.17). |
| Render right after copying media to Google Drive | If a QC render fails at 0% ("Failed to render background job") just after a new asset was copied into `G:/My Drive`, retry once, then delete the failed job by ID | The CHAPTER 04 wipe test failed at 0% and passed unchanged on the retry; the failed job stayed in the queue (ep3, 2026-10-25). |
| Rendering/snapshotting one chapter file | `hyperframes snapshot` refuses `--at` together with `--composition` (0.8.191); copy `chNN.html` into a scratch project as `index.html` (with `assets/`) and snapshot/render there. Pass `export_verified` an absolute path | `ExportProject` failed on a relative backup path (ep3 cosplay card, 2026-10-25). |
| Preset apply: Resolve will not close | If `load_subtitle_preset_auto --apply` stops with "Resolve did not close gracefully", scripting hangs; ask the user to answer the dialog / quit, and if `Resolve.exe` then lingers with no window and no CPU, `Stop-Process` it, run `patch_subtitle_preset_offline --apply` with the same args, relaunch through `explorer.exe`, reopen the project and dry-run again (`already_matches=True`); never relaunch before the patch, and strip CRLF when reading saved command lines | ep3 9:16, 2026-10-25: the process stayed alive windowless after the user quit; the manual patch + relaunch worked. |
| Vertical copy of an episode | Check whether the V2 zooms are Fusion or Inspector-only before reusing a vertical script; ep3's user zooms were Inspector 2.145x, so the Fusion-only assertion stopped the build (delete the half-built copy and rerun) | ep3 9:16, 2026-10-25. |
| Before a FINAL of a copy | Compare the copy against its source timeline (every track except the re-laid one) right before rendering; the user keeps editing the source between steps, and `TimelineItem` has no SetEnd, so carry late trims/cue changes over by DRT | ep3: the user trimmed Timeline 1 and lengthened a cue after the 16:9 FINAL and the 9:16 test (2026-10-25). |
| Studio bridge mutation no-op | After a write/export returns no value, verify the active object by ID and the expected file on disk; if activation/readback fails or `ExportProject` leaves no `.drp`, stop before batch edits and have the user restart/reopen Resolve | On Studio MCP 21.1.1, the Sakuyako read-only probe worked while `SetCurrentTimeline` stayed on the same ID and `SaveProject`/`ExportProject` returned `None` without creating a file (2026-10-27). |

## Transform and offline-media traps

- Set transform floats (e.g. `0.25`), not strings. A setter immediately after append can return False while the value is already correct; wait/read back before another write.
- `ZoomGang=True` links ZoomX and ZoomY. Probing one can change the other.
- Fit overlays using their actual source raster and Media Pool FPS/Frames. Compare Resolve-rendered pixels, not only Inspector numbers.
- An offline overlay can replace the whole composite with Media Offline while V1 is online. Inspect overlay tracks first.
- If an offline item's GetMediaPoolItem() is None, there is no pool entry to relink. Re-import/re-place only after approval, preserving record frames, tracks, source ranges and transforms.

## Database boundaries

On observed Resolve 21.1.0.17, Subtitle track preset loading has no public scripting setter. Prefer the exact user-approved saved preset over guessed font/size/position values. `scripts/load_subtitle_preset.py` reads preset bytes with a Python/SQLite workaround, not a native preset API; it is currently dry-run only and its `--apply` flag stops before any database write because it cannot verify Resolve has fully exited. Do not bypass that block. Any future writer requires explicit database-write authorization, a verified `.drp`, confirmed Resolve shutdown, exact target-row mutation, and readback of cue text/frames, video/audio coverage, track states and style bytes. Do not guess Inspector size from QFont pointSize. Leave already-matching styles unchanged.

Preset names are exact: `Mitr-Font` and `Mitr Font` are not interchangeable without approval. An empty `--list` can mean the preset lives in another library's User.db; discover/read that source and use an approved `--user-db` rather than switching the project's active library. Do not use `--orientation` without `--timeline` for a single-timeline request: it implies all timelines. Full workflow: `.agents/skills/thai-subtitles-resolve/references/srt-insertion-and-presets.md`.

After any insertion-script failure, re-read the live subtitle track before retrying; append may already have succeeded. Use `Project.SetCurrentTimeline`, not `ProjectManager.SetCurrentTimeline`.

## Evidence and scope

For legacy subtitle migration, read the Thai subtitle skill's native-caption
migration reference. Preserve exact words and absolute frames; disable only a
verified captions-only legacy track after native cues pass. Preserve unrelated
titles/overlays and protected horizontal versions. Recheck live state before
repeating interrupted mutations. Caption insertion, publication legibility,
listening QC and DRP restore are separate verdicts.

`docs/skills-manifest.json` records original paths, source SHA-256s, copied files, local amendments, and bounded historical usage anchors. Only the current default Hermes history was examined. A load in a session mentioning Resolve is evidence of loading, not proof that the skill was used on every clip or completed an edit. No footage, render, SRT deliverable, project DB, secret, or entire conversation transcript was copied.

The current portable `.agents` source was chosen over older worktree versions. Distinct historical versions are retained under `docs/skill-variants/`; the old house-style variant lacks the newer Thai rules. A Codex-specific media-analysis wording variant was archived; the active local copy is agent-neutral.

The bundle validator checks file coverage under `.agents/`, `docs/`,
`resolve-advanced/`, `scripts/`, and `tests/`, plus the declared integration
documents. It excludes its manifest, generated validation report and Python
bytecode caches. `work/PLAN.md`, `work/WORKLOG.md`, `reference/` and `.mcp.json` are
separate editing-work context, not evidence that this collection completed any
live edit. Check those tasks independently; do not rewrite their progress from
bundle tests. Checksums detect drift against the local manifest, not malicious
changes to both a file and the manifest; they are not signed provenance.

Archive validation checks the discovered names/paths and upstream frontmatter.
Tests use `TMPDIR` when supplied, otherwise `HERMES_HOME/cache/scratch` or
the platform's default Hermes home; no system-temp fallback is needed.
The `superpowers-` directory prefix is an archive namespace, not part of the
upstream skill name. Archive scripts and all archive links are not execution-
tested by core validation; these files remain inactive historical references.

In the separate editing plan, keep the sample-approval gate authoritative.
`work/PLAN.md` Task 2's all-timeline font heading must not be used to bypass Task 3's
explicit sample approval. Review/reorder that plan with its owner before any
batch writes; this skill-package review does not approve the remaining clips.

## Offline review and enrichment tooling

The reusable scripts added by the enrichment work, all run from the repository root with `python -m`:

| Script | Purpose |
|---|---|
| `scripts/resolve_preflight.py` | MCP-first verdict (`USE_MCP`/`FALLBACK_SCRIPT`/`BLOCKED`) for a needed tool or API method. |
| `scripts/review_enrichment_readonly.py` | Read-only inventory of every timeline, track, item and asset library. |
| `scripts/build_offline_review.py` | Per-timeline ffprobe/ffmpeg packets: caption map, mixed-audio metrics, sampled frames, HTML contact sheet. |
| `scripts/build_offline_asset_draft.py` | Subtitle-keyed SFX/GIF/BGM shortlist plus a local human review page. |
| `scripts/apply_vdo_python.py` | Capture an approved `vdo` GIF's exposed values and apply them by exact project/timeline/clip IDs. |
| `scripts/enrich_timelines_python.py` | Native Python batch enrichment onto copies; dry-run default, BGM-only when no cue is defensible. |
| `scripts/promote_drafts_to_originals.py` | Idempotent promotion of verified drafts into originals by exact IDs. |
| `scripts/anomaly_sweep.py` | Read-only structural sweep over every timeline. |
| `scripts/cleanup_backups.py` | Export one fresh verified `.drp`, then delete the named archives. |

Media-analysis APIs stay out of this path: the offline route is ffprobe/ffmpeg plus the saved native
subtitle map, so no provider quota or key is involved. Local ASR (faster-whisper) is a hint only —
Thai speech over game audio transcribed unreliably and must not be treated as a caption or beat source.

The `.hermes/` directory holds this project's working artifacts (review packets, drafts, reports,
renders, `.drp` archives) and is gitignored; it is not part of the installable bundle.

## Imported references that are not prerequisites

Generic references to global `colorist`, `colorist-assistant`, `editor`, `assistant-editor`, `online-editor`, `post-supervisor`, `deliverables-knowledge`, `quality-control`, and `qc-domain` do not prove those skills are installed here. No copies were found in the inspected primary skill roots. Use the included craft guides and actual task requirements instead of pretending to load unavailable skills. Related workflow archives may also reference their parent plugin; they are preserved context, not a claim of a configured plugin.

Official Hermes reference: https://hermes-agent.nousresearch.com/docs/user-guide/features/skills#project-local-skills

## External standalone skills

| Topic | This project's rule | Why |
|---|---|---|
| HyperFrames core skill install | Preserve the upstream copies and run `scripts/refresh_skill_manifest.py`; report its local-reference verdict separately from Codex skill discovery. The current `npx skills add` core set is discoverable, while this repo's verifier reports 18 unresolved local reference paths in those copied skills. | A successful skills install does not imply this repo's bundle validator can resolve every upstream reference. |

## Armigon illustration pilot (2026-10-24)
- Resolve 21.1.0.17: for the 60 fps HyperFrames MP4 pilot, AppendToTimeline with endFrame=sourceStart+duration-1 produced one frame less; using the exclusive source end produced the exact requested range. Always read back the placed range before batching.
- Activate the timeline before comparing track enable/lock state: an inactive source inventory differed while another timeline was active, then matched its immutable baseline after activation.
- `focus_qc_frames.py` renders video only (no audio stream) and leaves Resolve on the Deliver page with the playhead moved; reopen the edit page and reset the timecode afterwards, and do listening QC separately.
- Mock side graphics before rendering: `hyperframes snapshot --at` returns transparent RGBA PNGs; composite them over the matching V1 source frame (ffmpeg) to catch wrapping text and avatar overlap in seconds instead of after a 3-minute ProRes render.
- HyperFrames generator: every element id must be unique across the whole reel. A text id `meaning-c` collided with the clip wrapper `<id>-c`, so `tl.from("#meaning-c",{scale:1.8})` scaled the whole panel off-frame for ~1 s (only "ยว" visible); a mid-clip mock frame missed it. Assert no duplicate ids in the generator and mock entry frames (start+0.1 s) as well as midpoints.
- 9:16 from an illustrated 16:9 timeline: full-frame cutaways that carry text cannot be centre-cropped to 1080 wide (a 72 px heading spans >1080 px after the full-height fill); re-author them as a native 1080x1920 HyperFrames reel and replace those V3 clips, keep side cards as alpha scaled into the top band.

- Track enabled readback: `Timeline.GetIsTrackEnabled` returns False for every track of a timeline that is not current (21.1.0.17); activate the timeline before reading or comparing it Evidence: DRT-import audit falsely failed on enabled flags only (Sakuyako, 2026-10-29).
- Fusion comp delete: `TimelineItem.DeleteFusionCompByName` returns False and removes nothing on 21.1.0.17; avoid stacking comps instead of trying to prune Evidence: Sakuyako zoom batch, 2026-10-29.
- Fusion value readback after reload: After Resolve restarts, Transform `Size`/`Center` read back rounded to ~15 significant digits; compare with a tolerance (1e-9), not `==` Evidence: All 80 audited clips "failed" exact compare after a crash, values were correct (2026-10-29).
- ExportProject path: `ProjectManager.ExportProject` fails with a relative path; pass an absolute path Evidence: Sakuyako backup, 2026-10-29.
- Google Drive dropped mid-batch: When Drive for desktop stops, G: vanishes: `ExportCurrentFrameAsStill` returns False, then Resolve hangs/crashes, and restarting before G: mounts closes it again. Check G: first; make still loops fail fast on False Evidence: Sakuyako QC, 2026-10-29.
