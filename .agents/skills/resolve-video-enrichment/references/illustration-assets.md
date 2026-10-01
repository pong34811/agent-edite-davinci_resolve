# New illustrative stills: source, organize, place, verify

Use this workflow when adding new static images as visual illustrations or overlays in a Resolve clip. It covers still images, not generated art production or a blanket asset-library cleanup. Research and planning do not authorize a live Resolve edit; import, track creation, placement, relinking, or publishing require explicit scope.

## 1. Define the visual job

- Describe the image's editorial purpose in one phrase: clarify an object, punctuate a joke, show a reference, or reinforce a reaction. If it has no clear job, leave it out.
- Identify the exact clip/timeline, cue or frame range, expected hold, audience, approved aspect ratio, and whether the image is an overlay or a full-frame insert.
- Check an approved same-project exemplar and current house style before inventing placement, scale, track names, borders, or animation.
- Protect gameplay evidence, avatar head/face/hands, headroom, subtitles, and important HUD. Keep the original approved aspect ratio; do not convert a horizontal project to vertical by assumption.

## 2. Source and validate the image

- Prefer an authorized, user-provided or appropriately licensed image. Record exact source URL/path, creator, license, attribution requirement, acquisition date if relevant, and intended use. A search result, filename, or "free" label is not proof of reuse rights.
- If the user requests a newly generated image, use `image_generate` only when available and within the requested art direction; save it as a new derivative asset, never over a source image.
- Inspect the actual image with `vision_analyze` or a viewer. Check subject identity, legibility at intended display size, edge/crop quality, palette, and unwanted text/watermarks. Do not rely on filename or metadata as visual QC.
- Record actual pixel width and height, color mode, and alpha/transparency. Do not assume a PNG has transparency or a JPEG does not contain a critical background.
- Preserve the received source file. If an approved crop, resize, or background removal is needed, create a separate derivative with a traceable name and retain source-to-derivative provenance. Do not overwrite originals.
- Check file existence and supported format before import. Flag missing, corrupt, unsupported, low-resolution, or license-unclear files rather than silently substituting another image.

## 3. Organize a small, traceable selection

- Inventory only the candidate folder through `search_files` and `read_file` or inspect it with the authorized file tools available; do not import the whole library to use one still.
- Use a dedicated, clearly named asset bin/folder when supported by the verified Resolve workflow. `ImportMedia` has no destination parameter in the documented project workflow: set the current folder first, then import, and read back the resulting folder.
- Keep a task manifest with: asset ID, source path, derivative path if any, source/creator/license/attribution, dimensions/alpha, intended cue, approved timeline, and import status.
- Avoid ambiguous names such as `new.png` or duplicate basenames. Preserve the original basename when it carries provenance; otherwise use a descriptive stable name without claiming an unverified origin.

## 4. Place only after approval

- For an existing finished timeline, first inventory video/audio/subtitle coverage and existing overlays. If a relevant image is already present, do not duplicate it. Use a recoverable `[ENHANCED]` variant unless the user explicitly approves edits to original timeline IDs behind a fresh verified `.drp`.
- Present a cue-level plan before importing or appending: image/path, purpose, exact record-frame range, target track, scale/position, overlap risks, and any license note. A caption or keyword may suggest a beat but does not prove the right frame; review speech, action, and reaction.
- Import only approved selections. Add a dedicated overlay track only if needed and consistent with the project's exemplar. Keep picture/audio/subtitle source ranges untouched.
- For a still, set the approved duration explicitly; do not assume its default hold. Match the source raster to the approved timeline raster and derive fitting from actual image dimensions. Numeric transform properties must be numeric, and read back accepted values instead of guessing API names.
- Keep image placement on-screen long enough to read but short enough not to obscure the underlying action. No universal duration, corner, or scale applies; use the clip's pace, approved exemplar, and user direction.
- Start structural mutations with about 1.2 seconds of spacing, serialize live bridge calls, save and read back each batch, and pilot one representative placement before any batch.

## 5. Verify the result

- After import, read back exact file path and Media Pool location; after placement, verify timeline ID, target track, item name/path, start/end/duration, transform, enable state, and that no duplicate path+record-frame pair exists.
- Confirm all inserted ends are within the intended timeline. Inspect the actual composite at cue start, midpoint, and end for transparency, scaling, crop, safe areas, legibility, offline-media indicators, and occlusion. A source still or Media Pool thumbnail does not prove its timeline composite is correct.
- Render-check at least one frame where the image is visible, using the actual approved output/render route. Native still export can omit subtitles; use a viewer capture or appropriate authorized preview when subtitle overlap matters.
- Recheck protected picture/audio/subtitle ranges and track states, save with `ProjectManager.SaveProject()`, restore and read back the original active project/timeline/playhead/page/folder/track states, and report exact verification performed.
- Before publication, recheck the selected license terms and provide required attribution. Editing permission and attribution alone do not establish copyright clearance or platform monetization eligibility.

## Pitfalls

- A visually relevant image can still be wrong, illegible, low resolution, misleading, or unauthorized.
- Transparent-looking checkerboard pixels may be baked into the image; confirm the alpha channel and rendered composite.
- A static image may default to an unexpectedly long hold or alter timeline duration; verify its exact inserted range.
- Overlay media can show the composite as Media Offline while the base video remains online; inspect the overlay before diagnosing the original footage.
- Reimporting, relinking, replacing, deleting, database patching, or publishing are distinct operations; do not infer their authorization from a request to learn or plan.
- Windows paths and historical track labels in examples are not live project state. Discover current paths, build, raster, tracks, and capabilities first.

## Verification

A placement passes only when the manifest and Resolve readback agree on source/path, target timeline/track, and frame range, and a rendered/viewer composite confirms correct appearance and no protected-range change. For advice-only tasks, verify the plan identifies authorization, provenance/rights, exact cue, import location, and visual QC without claiming a live edit.
