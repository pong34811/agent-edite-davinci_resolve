# Thai captions, intelligible sound, and VTuber framing

## Provenance and scope
- Caption constraints here are this user's short-form house style, not a Thai language standard or a YouTube requirement.
- Sources: `.agents/skills/house-style/SKILL.md`, `docs/OPERATING-NOTES.md`, and the existing `thai-subtitles-resolve` workflow.
- Audio principles draw on the Editor's Guide, lesson 8: picture lock (p. 477), balancing clips (p. 512), EQ (p. 524), effects (p. 534), and music (p. 539).[6]
- Native subtitle creation/import and export review are covered in lesson 9, pp. 586 and 608 onward.[6]
- Exact build, edition, installed fonts, API support, and deliverable requirements must be discovered, not inferred from this chapter.

## Subtitle creation contract
- Create dialogue captions only on native Resolve Subtitle tracks; do not substitute Text+, Fusion titles, or video-track text.
- Separate verbatim dialogue from editorial annotations; never make commentary look like words the talent said.
- New Thai short-form cues: at most three short words, about 14 Thai characters, and no more than 1.5 seconds onscreen.
- Use shorter holds for faster speech, but split or flag unreadable cues rather than silently deleting words.
- Join Thai words naturally with no inter-word spaces; spaces belong around Latin names/terms only under this house style.
- Do not split a Thai combining vowel/tone mark away from its base character to satisfy a count.
- Count real word groups for pacing; `line.split()` cannot measure Thai words reliably.
- Character counts are a guide, not proof of fit: inspect rendered Thai marks and phone-size readability.
- Keep proper names, pronouns, particles, dialect, and deliberate comic phrasing faithful to the audio.
- Confirm uncertain name spellings from the creator's public naming/credits or the user, not ASR confidence alone.
- A preserve-text-and-timing migration must preserve legacy words and absolute frames; flag style exceptions instead of automatically splitting/retiming them.
- If the user owns font/style decisions, report readability problems without applying old style templates.

## Transcript-to-cue workflow
1. Establish the source/WAV/timeline timebase and any retimed segments before transcribing.
2. Review speech with surrounding context; game announcers and multilingual names are not automatically hallucinations.
3. Correct the transcript before grouping cues; guessed text should not become a confident caption.
4. Build word groups from complete Thai text, not isolated ASR word-timestamp fragments.
5. Align corrected text to audio and actual frames; review tone marks, punctuation, names, overlap, and out-of-range cues.
6. On uncertain spans, compare context-rich raw/filtered/model passes when available; record unresolved intervals explicitly.
7. Split at semantic units and speaker/intonation changes without leaking the punchline before it is spoken.
8. Reparse the exported UTF-8 sidecar and check every cue, not a sample.
9. Import only when project changes are authorized and the native subtitle target is known.
10. Review the final rendered/viewer captions with the actual mix at playback speed.
- Keep ASR API variants separate: parameters for faster-whisper are not automatically valid for openai-whisper.
- Do not mechanically delete genuine multilingual text just because it uses another script; verify suspicious glyphs against the audio.
- If speech remains uncertain, flag it for review; neither a silent omission nor invented full coverage is acceptable.

## Native subtitle placement traps
- Use an empty subtitle track and the bare placement payload `{"mediaPoolItem": item}` for the established SRT route.
- Extra placement fields such as `trackIndex`/`mediaType` have shifted SRT offsets to the timeline end on the observed build.
- A nonempty append return does not prove captions were placed; read back every item.
- Same-path SRT imports can reuse stale Media Pool text; approved replacement must remove the stale cached pool item before re-import.
- Replacing a track can reset its style; verify content/timing and approved style separately.
- Start structural mutations at roughly 1.2-second spacing, not the older short append-only delay.
- Never delete unrelated subtitle tracks or cached items by broad wildcard.
- Verify cue count, exact text, and absolute frames against the intended sidecar/timebase.
- Native still export can omit subtitle overlays; use a Resolve viewer capture or an authorized burn-in preview.
- Database style-copy is not implied by permission to add captions; keep it a separately approved, closed-project last resort.

## Readable design without overpowering the performance
- Use the existing approved typeface/style first; check it actually contains Thai glyphs and marks.
- Maintain clear contrast against both bright and dark game frames; use outline/shadow only within approved style scope.
- Keep dialogue cues away from avatar eyes/mouth, important hands, subtitles already baked into footage, and game HUD evidence.
- Test against the actual YouTube player/device UI; no single pixel margin is safe on every layout or screen.
- A style that passes a full-size still can still fail at phone size or during fast motion.
- Use stable placement and a small consistent speaker distinction only if the approved native-track workflow supports it.
- Do not flash full sentences so quickly that they technically meet the duration cap but cannot be read.
- Example grouping for new fictional speech: `อย่ากด` / `ปุ่มนั้น` / `บอกแล้วไง`; actual cue timing must come from the recording.

## Dialogue-first mix
1. Inventory existing source dialogue, game sound, music, effects, and routing before adding anything.
2. Make speech clips perceptually consistent before balancing music and effects; intelligible dialogue carries the story.[6]
3. Correct specific problems gently: rumble, noise, harshness, excessive dynamic jumps, or clicks.
4. Compare processed and bypassed audio at similar perceived level; louder alone is not better.
5. Add game/SFX components against the dialogue, then music, checking the complete combination.[6]
6. Preserve the original reaction/laugh and meaningful game sound; do not replace every emotion with a stock sting.
7. Wait until the picture is substantially settled before detailed mixing so later cuts do not discard the work.[6]
8. Listen through the whole short, including caption transitions, music tail, and the loudest reaction.
- EQ is frequency-specific shaping, not a universal preset for every VTuber microphone.[6]
- Noise reduction should not erase soft syllables or produce watery artifacts; dial it back if intelligibility worsens.
- Do not normalize every component to the same loudness; their narrative roles differ.
- Clip gain in dB, measured sample/true peaks in dBFS/dBTP, and integrated loudness in LUFS are different quantities.
- An old BGM gain such as -26 dB is not a final program loudness target or evidence of an acceptable mix.
- Keep numerical loudness goals project-specific and measured; do not invent a universal YouTube upload pass/fail LUFS rule.

## Ducking: software feature versus scripting access
- Resolve 20's guide describes audio-level keyframes and mentions Ducker/sidechain approaches for letting speech take priority.[6]
- That does not establish an automation API. The established bridge workflow verifies flat per-item `AudioVolume`, not fade/ducking keyframes.
- If using an approved verified UI workflow, automate music around speech and listen for pumping or unnatural recovery.
- If only the verified scripting surface is available, use a low flat bed or no music; report the limitation honestly.
- A single source file with baked-in voice/game/music cannot be independently mixed merely by creating extra timeline tracks.
- Do not promise stem separation, restoration of clipped peaks, or AI repair without actual capability and perceptual verification.

## Framing decision table
| What carries the beat? | Preferred emphasis | Must remain visible |
|---|---|---|
| Facial/upper-body reaction | Motivated avatar focus | Head, face, headroom, relevant hands, caption space |
| Gameplay outcome | Gameplay-first composition | Target/action/HUD needed to understand the result |
| Banter among speakers | Stable context with clear focus shifts | Speaker identity and authentic response order |
| Both action and reaction | Test split/composite or timed focus in an approved variant | Readable action plus recognizable avatar |

- Preserve the approved aspect ratio; 9:16 is a separate requested version, not an automatic upgrade.
- Do not stretch the image to fill a new raster; evaluate a crop, layout, or approved background treatment.
- Calibrate framing per recorded layout and source raster; the same Pan/Tilt values are not portable across all clips.
- Prefer scripted approved adjustment clips, protecting and auditing all original video/audio/subtitle ranges.
- Inspect beginning, middle, end, and motion-sensitive moments of each focus cue, not just a neutral pose.
- Check for duplicate-edge avatars, empty borders, zoom softness, HUD obstruction, and cropped hands.

## Listening and visual gate
- Listen on headphones and a small speaker when available; if a device test was not done, mark it unverified.
- Check speech at modest playback volume and ensure sudden effects do not force the listener to turn it down.
- Review the actual export/viewer at phone-scale size with captions, avatar motion, and intended music all present.
- Verify source audio ranges separately from rendered AAC hashes; transcoding can change samples without changing the approved timeline.
- Require clean starts/ends, no black/offline composites, no clipped syllables, and no caption overlap that hides the payoff.
- Report insertion, typography, listening, and publication readiness as separate checks.

## Sources

[6] https://documents.blackmagicdesign.com/UserManuals/DaVinci-Resolve-20-Editors-Guide.pdf?_v=1757574011000
