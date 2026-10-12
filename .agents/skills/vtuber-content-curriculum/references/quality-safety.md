# Quality & Safety (Topics 20-21)

## 20. Video Quality Control

**Core principle:** QC catches errors before viewers do.

**QC checklist:**
| Area | Check | Method |
|---|---|---|
| Video | Black frames, blur, corruption | Frame inspection |
| Audio | Silence, clipping, sync | Waveform + listening |
| Subtitles | Text accuracy, timing, style | Screenshot + read |
| Transitions | Smoothness, appropriate type | Playback review |
| Pacing | Dead air, rhythm consistency | Timing analysis |
| Aspect ratio | Correct for platform | Project settings |
| Resolution | Matches source/spec | ffprobe |
| Loudness | I=-14 LUFS | EBU R128 measurement |

**QC workflow:**
1. **Structural check:** Gaps, overlaps, track integrity
2. **Visual check:** Frame inspection at key moments
3. **Audio check:** Waveform analysis + spot listening
4. **Subtitle check:** Text, timing, readability
5. **Playback check:** Full review at normal speed
6. **Render check:** ffprobe + visual QC of output

**Common issues:**
- Caption timing off by frames
- Audio sync drift in long timelines
- GIF duration shorter than expected (conform drift)
- Black frames from incorrect transitions
- Loudness inconsistency between timelines

**For agents:**
- Use `ffprobe` for read-only media analysis
- Use `caption_lint.py` for offline Thai caption rule check
- Use `focus_frame_qc.py` for multi-frame visual QC
- Document QC results with evidence

## 21. Copyright & Content Safety

**Core principle:** Respect rights holders and platform policies.

**Music licensing:**
- YouTube Audio Library: Safe for monetization
- Creative Commons: Check specific license terms
- Commercial music: Requires license or Content ID claim
- Game music: Varies by publisher — check policy

**Meme and GIF usage:**n- Fair use is a defense, not a right
- Credit sources when required
- Transformative use (commentary, criticism) is stronger
- Don't use memes/GIFs that contain copyrighted content

**Game content:**
- Most gameplay is fair use for commentary
- Cutscenes may have restrictions
- Check publisher's content creation policy
- Mute/replace restricted audio

**VTuber content:**
- Clip only with permission or fair use basis
- Respect VTuber agency guidelines
- Don't misrepresent or take out of context
- Credit the VTuber/channel

**Platform policies:**
- YouTube monetization policies vary by content type
- Reused content may affect monetization
- Age-restricted content limits distribution
- Community guidelines apply to thumbnails and titles

**For agents:**
- Flag potential copyright issues, don't resolve them
- Suggest licensed alternatives when possible
- Document rights checks in edit brief
- Never assume fair use without human review