# Audio & Subtitles (Topics 7-9, 19)

## 7. Dynamic Thai Subtitles

**Core principle:** Subtitles must match speech rhythm and be readable within the video's pacing.

**Thai subtitle house style (Katy404):**
- **Max 3 short words / ~14 Thai characters per caption**
- **Max 1.5 seconds on screen**
- **NO spaces between Thai words** — spaces only around Latin names (e.g., "Armigon", "Mitr Font")
- **Short holds when speech is fast** — don't force slow pacing

**Subtitle timing principles:**
- Sync caption appearance to speech onset, not before
- Remove caption at speech end + natural pause, not fixed duration
- Allow slightly longer holds for emphasis or emotion
- Split long captions at natural phrase boundaries, not mid-word

**Technical implementation:**
- Native Resolve Subtitle tracks only — no Text+/TextPlus/Fusion titles
- Import SRT to empty subtitle track with bare `{"mediaPoolItem": item}` payload
- Verify every cue's text, timing, and style after insertion
- Corrected SRT requires removing stale pool cache before re-import

**Readability:**
- Position captions to avoid HUD/face overlap
- Maintain contrast with background (stroke/shadow as needed)
- Don't cover the VTuber's face or key game information

## 8. Sound Effects (SFX)

**Core principle:** SFX enhance moments without overwhelming the VTuber's voice or game audio.

**SFX categories:**
| Category | Purpose | Examples |
|---|---|---|
| Reaction | Enhance emotional beats | gasp, record scratch, rimshot |
| Transition | Smooth cuts | whoosh, hit, impact |
| Emphasis | Draw attention | bass drop, cymbal, glitch |
| Comedy | Timing jokes | trombone, buzzer, cartoon |
| Game context | Reinforce game events | explosion, level up, damage |

**SFX selection principles:**
- Match SFX to the moment's energy and emotion
- Don't use SFX for every reaction — save for peak moments
- Game audio already provides context — don't duplicate
- Thai internet culture SFX (if used) should feel natural, not forced

**Implementation:**
- Place SFX on dedicated audio tracks, not dialogue tracks
- Time SFX to visual impact, not just audio cue
- Adjust SFX volume relative to dialogue (typically -15 to -20 dB below speech)
- Use short SFX — long effects become distracting

## 9. Background Music (BGM)

**Core principle:** BGM supports the mood without competing with dialogue.

**BGM selection principles:**
- Match BGM mood to content emotion (hype, chill, emotional, funny)
- Choose BGM that fits the VTuber's personality
- Avoid BGM with lyrics that compete with speech
- Consider Thai music for cultural connection when appropriate

**BGM implementation:**
- Dialogue is priority — BGM at -18 to -25 dB relative to speech
- Duck BGM during important dialogue or reactions
- Fade BGM in/out at segment boundaries, not abrupt cuts
- Match BGM energy to content energy — build and release

**Per-timeline levels:**
- Measure speech loudness per timeline, not one shared dB value
- Source speech loudness can differ by ~20 LU between timelines
- Derive BGM/SFX gains from measured speech loudness

## 19. Audio Mixing & Voice Enhancement

**Core principle:** Clear, balanced audio is essential — viewers forgive bad video, not bad audio.

**Mixing hierarchy:**
1. **Dialogue/VTuber voice:** Priority — always intelligible
2. **Game audio:** Context — important for understanding gameplay
3. **SFX:** Enhancement — support moments without distraction
4. **BGM:** Atmosphere — mood support, lowest priority

**Voice enhancement:**
- Normalize dialogue to consistent loudness (I=-14 LUFS for YouTube)
- Remove background noise without affecting voice clarity
- De-ess harsh sibilance if present
- Compress dynamic range for consistent volume

**Technical notes:**
- AudioVolume in dB on Resolve scripting API
- Use actual property reads, not guesses — Volume/Gain/Level may return False
- Two-pass loudnorm for accurate normalization
- Preserve natural laughter and emotional variation — don't over-compress