# Subtitle-track continuation — PLAN.md

## Scope and rulings

- Current user instruction: continue, using native Subtitle tracks only; no new Text+/Fusion dialogue captions.
- Ruling: begin with vertical RoV (`de94c609-9127-40bf-8a28-bbde6ffb3076`), preserving the horizontal original under the existing plan constraint. Cost if broader conversion was intended: horizontal legacy Text+ remains for a separately confirmed pass.
- Preserve existing words, in/out frames, all underlying video, audio, GIF and SFX ranges. Do not re-transcribe or shorten legacy captions to fit house-style limits; report exceptions.
- Keep legacy Text+ clips recoverable by disabling their caption-only track after native subtitles verify, not deleting clips or source media.
- Read-only exported DRP inspection replaces live Fusion reads: the previous TextPlus read probe hung Resolve. No direct database writes are authorized.
- This is a Resolve editing task, not a repository implementation/commit task: retain current dirty worktree and all prior artifacts. No commits, branch switches, deletions, or new backup timelines.

## Preflight

- Resolve Studio 21.1.0.17; expected project UUID confirmed through live scripting.
- Captured all 17 live timelines and media paths in baseline.json; existing picture/audio sources present. Eleven historical missing SRT pool paths remain untouched.
- Both RoV timelines are 1285 frames at 60 fps; vertical 1080×1920 and horizontal 1920×1080. Project playback frame rate separately verified as 60.
- Vertical RoV V5 contains 17 enabled Text+ clips and nothing else; no native subtitle track. Horizontal V4 contains the original 17 Text+ clips.
- Fresh pre-edit DRP exported; ZIP integrity and SHA-256 verified in backup-verification.json. Restore/import has not been tested.

## Progress

- Baseline and backup complete.
- Native subtitle migration, styling, burn-in QC and final invariant checks pending.

## Verified continuation / supersedes pending status

- User explicitly waived font/style work: “ไม่ต้องปรับฟอนครับ ใส่เเค่ subtitle เท่านั้น ได้เลยครับ เดี่ยวทางผมค่อยไปปรับฟอนเอง”. No style or font mutation performed.
- Live recheck at 2026-09-30 16:35 +07 verified all 17 native cues' exact text and absolute start/end frames, S1 enabled and legacy caption-only V5 disabled. Legacy Text+ clips remain recoverable. Horizontal RoV is unchanged and still uses legacy Text+.
- All 17 live timelines' non-migration content matches the pre-migration baseline. All 17 exported sequences match the prior post-migration DRP after excluding only regenerated BtThumnail.DbId attributes.
- SaveProject succeeded and the state captured at this continuation's start was restored; queue/presets/format/mode unchanged.
- Fresh report: `resume-verification-20260930_163508.json`. Fresh backup: `Aomi-mama_verified_native_20260930_163508.drp`, ZIP/hash verified, restore untested.
- Existing preview `after_rov_9x16.mp4` freshly probed and fully decoded: H.264/AAC, 1080×1920, 60 fps, 1285 frames, 21.416667 s, 48kHz audio. No new render or duplicate subtitle import.
- Visual recheck f72/f263/f1254 confirms captions appear. Long cue near edges, chat overlap, and white-on-white contrast remain; migration passes but publication-legibility QC does not. User handles font/style finishing. No claim of complete listening.
- Two legacy cues exceed 1.5s (3.233333s and 1.616667s). Kept unchanged to preserve words and timing; no silent deletion or retiming.
- Handoff complete for the native-subtitle migration, not for the entire seven-pair image-polish plan.
