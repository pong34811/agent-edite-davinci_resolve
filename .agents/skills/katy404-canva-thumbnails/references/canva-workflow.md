# Canva workflow: preserve native editable structure

Tool capability snapshot: 2026-09-26. Discover the available Canva tools and read their current schemas at runtime; names below describe verified operations, not an API client to paste blindly. Use the Canva connector first for Canva work. Read applicable editing instructions when performing an actual edit.

## 1. Resolve and inspect the selected reference

- Use `get_design` and `get_design_pages` with the full user-supplied Canva URL from the source manifest. Do not discard its collaboration token on read operations; some shared designs need it.
- The manifest stores sampled page IDs and page numbers. Resolve the current page, compare its preview, then use its current 1-based page number. If the ID moved, locate it using paginated page listings. If removed, choose a comparable visible page and say so.
- Do not fetch all hundreds of pages by default. Start with the relevant sample and expand only if it does not meet the brief.
- Ordinary design references are not necessarily brand templates. Do not use autofill unless a real non-empty autofill schema is available from tools currently exposed.

## 2. Copy only the useful page

`copy_design` accepts `design_id` and optional `page_numbers` (1-based). Use the resolved design ID and `[selectedPage]`. Omitting `page_numbers` copies the whole collection; avoid that for a single thumbnail.

Record the returned new design ID and returned edit URL. Use only the new ID for editing, unless the user explicitly requested editing the original. Do not describe the copied, unchanged page as the completed new cover.

If copying fails, check access and the current tool schema. Do not remove source pages or rewrite a reference as a workaround. Avoid creating duplicate copies repeatedly after an uncertain response; inspect results first.

## 3. Inspect native elements and assets

Start an editing transaction on the copy using `start_editing_transaction`. Retain its exact transaction ID and the returned element/page IDs.

- Map headline, secondary hook, avatar, game background, LIVE/episode labels and decoration to observed elements. Element IDs belong to this transaction; do not reuse IDs from the original design or old transactions.
- If replacing one image on a page with multiple assets, inspect all assets on that page with `get_assets` before choosing which element/fill to replace.
- Identify repeated text: outlines/shadows may involve layered text copies. Change every matching layer of the intended headline without touching unrelated occurrences.
- If a visually visible headline is absent from the text elements, it may be embedded in a bitmap. Do not pretend a text replacement can edit it. Prefer another source page with native text, or use actual editor capabilities to rebuild that part. Tell the user if only some parts remain editable.
- Inspection does not authorize changing the source design. Cancel any inspection-only transaction if one was needed; normal work should inspect and edit the new copy in the same transaction.

## 4. Bring in the new media

- Keep source avatar art when appropriate; use the user's supplied art for identity or pose changes.
- For a local file, use a supported private upload route. `create_upload_url` provides an upload URL; follow its returned transport exactly (in the inspected version: HTTP POST of raw bytes with `Content-Type: application/octet-stream`). Do not base64-wrap bytes or publish the file on an unrelated host.
- `upload_asset_from_url` can use public HTTPS media URLs or an `asset_file` supported by its host environment. Do not assume every local Windows path is supported: inspect the current schema; use the upload-URL route when appropriate.
- Use the returned asset ID and actual version in edit operations; do not invent IDs or reuse an expired signed thumbnail URL as a source asset.
- `remove_background` operates on an image already in Canva and returns a new transparent image. It does not add a white outline, recrop a subject, or preserve surrounding game context. Use only when a cutout is needed.
- If a white subject outline is essential, choose an existing compatible cutout or use verified editor/image capabilities; do not promise the replace-image API will recreate an effect automatically. Inspect the resulting crop and outline.

## 5. Edit within exposed capabilities

Use `perform_editing_operations` and its current schema. The inspected version supports text find/replace, font size/weight/italic/color/alignment/line height, element position/resize, image fill updates and media insert/delete, and title changes.

The inspected edit API does **not** expose font family, new text boxes, text stroke/shadow creation, background color/gradients, shape restyling, grouping, existing opacity, or z-order. Do not invent unsupported operation names or claim that all artwork can be rebuilt through this API.

Choose a compatible source to preserve these properties. If the brief genuinely requires an unsupported change:

1. First look for a source page with the needed native structure.
2. Otherwise use available Canva UI or another actual Canva capability within the user's scope.
3. If still blocked, show the specific limitation and the usable work already prepared. Do not silently flatten the cover when editable text was requested.

`create_design` is an alternative for a new generated layout when fidelity is flexible. Use it instead of legacy `generate_design`/`prepare_design_generation` when available. `image_to_design` reconstructs editable layers from a bitmap; it is not equivalent to copying native layers and must be visually verified. Neither fallback guarantees exact KATY404 likeness, typography or editability.

Keep a compact edit recipe (new text, assets and intended positions) so a lost transaction can be recovered without copying the source again unnecessarily.

## 6. Preview and save correctly

- Inspect and show the latest preview of every modified page. The editing operation may only return the first page preview; call `get_design_thumbnail` with the transaction and the page index required by its current schema for other pages.
- Use the quality checklist in SKILL.md. Fix stale source text, Thai marks, overflow, image cropping, unintended hidden elements and layer collisions before calling the result ready.
- Edits are drafts until `commit_editing_transaction` succeeds. The inspected commit tool requires showing changes and obtaining explicit approval before commit. Apply its current requirement; keep already applicable approval and do not invent extra checkpoints. When approval is required, finish the draft first, show the preview, summarize changes and explain that the Canva commit tool requires approval to save.
- Await the required answer. Do not cancel a desired draft simply because the user has not replied yet. State clearly that it is awaiting save approval, not a saved finished design.
- On approval, commit once and provide the returned or verified edit URL. A committed transaction ID is invalid for further editing.
- If commit fails, do not report success: the inspected tool says the changes are lost. Reopen the same copy and reapply the edit recipe in a new transaction if appropriate. Avoid endless retries; after a repeated failure report the error and current saved state.
- Cancel rejected/discarded transactions. Do not create a new revision or additional variants beyond the user's request.

## 7. Deliver the editable result

Use the actual edit link returned by Canva/get_design. Mention the page if the result has multiple pages. Provide the preview and concise Thai wording; disclose any bitmap-bound content affecting the requested editability.

No Canva export tool was exposed in the inspected tool inventory. If PNG/JPG is requested later, check for an export capability then, or use the actual Canva editor download UI when available. Verify file size/dimensions and the saved artifact before claiming export succeeded. A 596-pixel page thumbnail is a preview, not a full-resolution 1920×1080 deliverable.
