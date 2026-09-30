# YouTube delivery, clipping rights, and publication gates

## Scope and freshness
- This is a production checklist, not a legal opinion or permission to upload someone else's work.
- Platform facts below were retrieved from official YouTube Help; refresh the linked pages before a real delivery/publication decision.
- No specific Thai talent or agency was named, so no agency-wide clipping permission has been established.
- A similarly named company or unrelated VTuber project is not the relevant rights holder.
- Keep official platform requirements, creator-specific terms, and editorial recommendations distinct.

## Establish clipping permission before publishing
1. Identify the exact creator/channel, original stream URL, source date, and relevant source time ranges.
2. Locate the creator/agency's current clipping or derivative-work policy from an official channel/site.
3. Record whether editing, translation, monetization, music reuse, branding, and required credits are covered.
4. Check stream-specific exclusions and any waiting period, restricted topics, collaboration rights, or takedown request.
5. If permission is unclear, hold publication and ask the owner/user to resolve it; do not treat public availability as a license.
6. Avoid members-only, paid, private, deleted, or explicitly no-clip material without specific permission for the intended reuse.
7. Preserve context and avoid exposing private information, impersonating official accounts, or manufacturing conflict.
8. Keep the evidence URL/text and asset license record with the deliverable, not a vague "copyright checked" label.
- Credit alone, non-profit labels, disclaimers, a few seconds of use, and "other clippers do it" do not automatically establish rights.[13]
- Editing or translating content does not by itself remove the need for permission or another valid legal basis.[13]
- Do not promise a fair-use outcome; uncertain legal questions need qualified advice for the relevant jurisdiction.

## Permission is not monetization approval
- YouTube's reused-content policy is separate from copyright and can apply even when the original creator permitted the reuse.[10]
- Review can consider the channel as a whole, including videos, titles, descriptions, and channel information.[10]
- The policy looks for meaningful original contribution, substantive modification, commentary, or educational/entertainment value rather than minimal reuploads.[10]
- Subtitles, a border, speed changes, and a few meme sounds do not guarantee eligibility.
- Do not promise that a particular number of edits or a clip length makes reused footage monetizable.
- The editorial goal is a coherent, distinctive viewer experience with honest context, not a template disguised as original reporting.
- Keep attribution and original-value descriptions accurate; never claim ownership of source performance or music.

## Music and effects licenses
- YouTube Studio's Audio Library supplies music and SFX with documented usage/attribution information.[11]
- Tracks marked Creative Commons require the supplied artist attribution in the video description; a generated music-credit panel does not replace it.[11]
- Preserve the exact license and attribution text from the selected track's listing.
- A library filename or a third-party "no copyright"/NCS label is not proof of permission; verify the actual track and intended use.
- Separate the Studio Audio Library from the Shorts Audio Library's in-product music choices and duration restrictions.[9][11]
- Do not assume an in-app music permission covers an externally edited Resolve export, a full track, or cross-platform distribution.
- Include game music, karaoke/cover songs, collaborations, GIFs, fonts, and artwork in the rights inventory, not just the added BGM.
- If a license cannot be established, omit/replace the asset only within authorized scope and report the tradeoff.

## Choose a format deliberately
- The retrieved Shorts help page supports square/vertical Shorts up to three minutes, with classification depending on upload date and channel type.[9]
- This is a platform limit, not an editorial target; stop when the selected story is complete.
- Read the current page for Official Artist Channel exceptions, music length limits, and Content ID treatment.[9]
- Do not cache an absolute rule such as "all claimed Shorts over one minute are always blocked"; policy and claim treatment can change.
- A claim not blocking playback does not grant copyright permission or guarantee revenue.
- Keep a horizontal highlight when game geography matters; produce a vertical variant only if approved.
- Do not crop an approved 16:9 master or alter its timeline/playback FPS merely to classify the export as a Short.
- YouTube's player adapts to different aspect ratios; avoid adding arbitrary baked-in bars just to imitate a player frame.[12]

## Resolve export plan
1. Read the current target raster, FPS, duration, audio requirements, and subtitle delivery mode.
2. Probe the installed Resolve render format/codec/preset availability; choose a verified route rather than a guessed codec ID.
3. Set output directory and basename separately from sources; never overwrite footage or an approved master without explicit approval.
4. Load the intended preset and pin format/codec, raster, FPS, render range, video/audio export, and caption mode.
5. Inspect rejected settings before queuing; preset inheritance is not a substitute for explicit configuration.
6. Render only the authorized jobs and retain the exact job/output mapping for batch verification.
- [render-qc.md](render-qc.md) contains the existing recipe; all example values must be replaced by the approved live target.
- Rendering is not uploading; publication and public metadata changes are separate authorized actions.

## Upload encoding reference, not a forced project preset
- YouTube recommends MP4, H.264 progressive video, and supported audio such as AAC-LC at 48 kHz.[12]
- Its SDR upload guidance recommends BT.709; preserve a correct approved color-managed pipeline rather than blindly retagging HDR or misinterpreting levels.[12]
- Encode at the recorded frame rate where consistent with the approved edit; do not invent extra motion by simply changing an FPS label.[12]
- If a finished approved timeline intentionally differs from its source, resolve the delivery choice with the user instead of rewriting the project.

| SDR raster class | 24 / 25 / 30 fps recommendation | 48 / 50 / 60 fps recommendation |
|---|---|---|
| 1080p | 8 Mbps | 12 Mbps |
| 1440p | 16 Mbps | 24 Mbps |
| 2160p | 35–45 Mbps | 53–68 Mbps |

These are YouTube's published upload recommendations, not acceptance guarantees, mandatory bitrate ceilings, or Resolve API enum values.[12]
- Test fast game motion, particles, dark gradients, and fine Thai text in the encoded result.
- Do not upscale low-resolution material merely to imply detail that does not exist.
- Keep burn-in captions versus optional subtitle sidecars explicit; they serve different accessibility/playback needs.

## Technical and perceptual checks
- Require Resolve job status Complete and a nonempty output at the expected path.
- Invoke through `terminal`: `ffprobe -v error -print_format json -show_format -show_streams "<rendered-file>.mp4"`.
- Substitute the actual output path and compare video/audio streams, raster, frame rate, duration, and color/audio metadata with the approved specification.
- Watch/listen to the output rather than treating metadata as quality proof.
- Inspect the first/last frames, edit joins, payoff, each changed focus/overlay cue, and representative bright/dark caption backgrounds.
- Check every batch output; a good pilot does not prove later outputs are correct.
- Restore and read back project/timeline/playhead/page/folder/track states after rendering and saving.
- If upload is explicitly authorized, inspect the exact published/draft target after processing for format, captions, audio, visibility, metadata, and any restrictions.
- Do not publish publicly, dispute claims, remove a published video, or accept rights declarations without the appropriate authorization.

## Release record
- Output file(s), target format, and verified technical/perceptual checks.
- Original creator/channel and source stream/time references.
- Required artist/asset/license attributions, copied accurately.
- Rights status and unresolved exclusions/claims.
- Accurate title/thumbnail/description drafts, plus actual published URL only if publication happened.
- Analytics hypothesis and what remains to be measured after release.
- A complete release record must distinguish "rendered", "upload checked", "published", and "performance measured".

## Sources

[9] https://support.google.com/youtube/answer/15424877?hl=en-GB
[10] https://support.google.com/youtube/answer/1311392?hl=en
[11] https://support.google.com/youtube/answer/3376882?hl=en
[12] https://support.google.com/youtube/answer/1722171?hl=en
[13] https://support.google.com/youtube/answer/2797449?hl=en
