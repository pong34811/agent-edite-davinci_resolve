# Changelog

## v0.9.0

ชุดสกิลและสคริปต์ช่วยงานตัดต่อรุ่นนี้แยกเลขรุ่นจาก DaVinci Resolve และ MCP server

### P2 และการจัดภาพ 9:16
- เพิ่มชุด `p2_9x16_*` สำหรับสำรวจ source, สร้างและแปลง timeline, จัดส่วนเกม/ตัวละคร, ตรวจ cut และตรวจโครงสร้างหลังแปลง รวมถึงการรับสำเนา 1080×1920 ที่ตั้งค่าด้วยมือหรือ MCP และโหมด raster ช้า
- เพิ่มตัวลบ stray copy ตามขอบเขตที่ระบุ และการตรวจทุก timeline หลังเปลี่ยนเพื่อช่วยจับการคลาดเคลื่อนของแทร็กและช่วงภาพ

### ซับไทยและ QC ก่อนเผยแพร่
- เพิ่มเครื่องมือสร้าง cue จากข้อมูลต้นทางและ sample, ใช้ cue กับ native subtitle track, แก้กฎข้อความ/ช่วงเวลา และใช้ซับที่แก้แล้วได้ทั้งแนวตั้งและแนวนอน
- เพิ่ม `p2_publish_qc.py`, การตรวจซับหลังแก้, still และ audio QC เพื่อจัดหลักฐานก่อนเผยแพร่; `caption_lint.py` ตรวจข้อกำหนดซับไทยแบบอ่านอย่างเดียว

### VTuber focus และ QC
- เพิ่มตัววางแผน/ใช้ zoom focus ของ P2 พร้อม rollback, เครื่องมือสร้างและย้ายแทร็ก `Adjustment Clip` ผ่าน DRT, ตัวตรวจเฟรม/โครงสร้าง focus และ pilot Armigon บนสำเนา
- รายงาน QC Armigon ใน Resolve Studio 21.1.0.17 ที่ 1920×1080/60 fps ตรวจ `Adjustment Clip` 48 รายการ พบ `MotionBlur=0` ทั้งหมด; อ่าน `Center`/`Size` รวม 192 input โดยไม่พบ keyframe ใน input ที่ตรวจ
- T74–T77 เป็น VTuber ผมชมพูอีกคน จึงคืนค่าเฉพาะ V2 focus ให้เป็นกลางและอ่านค่ากลับแล้ว; T1 เฟรม 2261 และ T70 เฟรม 1839 มีภาพ still A/B เปิด/ปิด V2 ในเวลาเดียวกัน เขาด้านขวาถูกตัดใน source อยู่แล้ว และสติกเกอร์ผมขาวใน source ของ T70 บังมือ/ลำตัวบางส่วน การลอง `X=-0.06` ไม่แก้เขา จึงคืน T70 เป็น `X=-0.03`
- ภาพ still ที่ตรวจไม่พบขอบดำหรือ blur ที่ zoom เพิ่มขึ้น แต่ไม่ใช่หลักฐานว่า motion ทุกเฟรมไม่มีอาการสั่น และไม่ได้ตรวจวิดีโอ render เต็มช่วง รายละเอียดและขอบเขตหลักฐานอยู่ที่ `docs/superpowers/reports/2026-10-12-armigon-focus-qc-th.md`

### GIF, การตัดท้าย และการส่งออก
- เพิ่มการย้าย GIF บน V2 ให้อยู่ในแผงเกมเหนือรอยต่อ avatar ของ 9:16 โดยคำนึงถึง V3 ที่วาดทับ V2; เพิ่มเครื่องมือตัด GIF ท้ายที่ผิดและสร้าง timeline รุ่น `_150s` โดยลบ cue ที่เลยหรือคร่อมจุดตัดตามนโยบายสคริปต์
- เพิ่มชุด render แนวตั้ง/แนวนอน, ตัวช่วย loudness ของแต่ละสัดส่วน และ `p2_export_final.py` สำหรับเตรียม export หลาย timeline ด้วย `H.264 Master` พร้อม readback/การตรวจผลที่สคริปต์กำหนด; การมีสคริปต์ไม่ใช่หลักฐานว่าไฟล์ส่งออกทุกชิ้นผ่าน QC แล้ว

### ขอบเขตเครื่องมือและสกิล
- ปรับ `AGENTS.md` และสกิล Resolve ให้บังคับใช้ Resolve MCP ก่อน แล้วจึงใช้ Python Scripting API เมื่อมีหลักฐานช่องว่าง; เพิ่มแผนผังเครื่องมือ MCP v4.10.3 และคำแนะนำ subtitle/conform/focus QC ล่าสุด
- เพิ่มกฎ house style และ `adjustment-focus.md` ให้ยืนยันตัว Armigon, อ่าน transform/`MotionBlur`, เทียบเฟรมเดียวกันเมื่อเปิด/ปิด focus และแยกปัญหา source ออกจากผล zoom

### เพิ่มเติม
- `scripts/caption_lint.py`: ตรวจ SRT ภาษาไทยแบบ read-only ตามกฎซับสั้น (ไม่เกิน 14 อักษรไทยและ 1.5 วินาทีต่อ cue, ไม่เว้นวรรคระหว่างอักษรไทย, ไม่เกิน 2 บรรทัด) คืน exit code 1 เมื่อมีข้อผิดกฎ; ชี้จาก `thai-subtitles-resolve`
- `scripts/backup_drp.py`: `export_verified` / `verify_drp` สำหรับ export `.drp` แล้วตรวจว่าไฟล์ไม่ว่างและเป็น zip ที่สมบูรณ์
- `tests/conftest.py`: ข้ามเทสต์ `test_m1_*` ที่ต้องมี Resolve จริง เว้นแต่ใส่ `--live`
- `tests/test_caption_lint.py`, `tests/test_backup_cleanup.py`

### แก้ไข
- `scripts/cleanup_backups.py`: เดิมลบ `.drp` ทุกไฟล์ในโฟลเดอร์ รวมถึงไฟล์ rollback (`pre-enrichment`, `before_promotion_`) เพราะ `KEEP_MARKERS` / `DELETE_PREFIXES` ไม่ถูกใช้และ `--keep-rollback` ไม่ทำอะไร; ตอนนี้ลบเฉพาะชื่อที่ขึ้นต้นด้วย `before_python_batch_` / `before_python_vdo_` เท่านั้น ไฟล์อื่นรายงานเป็น kept / skipped_unmatched (ยังเป็น dry-run ถ้าไม่ใส่ `--confirm`)
- `scripts/promote_drafts_to_originals.py`: เดิมเขียน report ทับก่อนอ่านสถานะรอบก่อน ทำให้ตรวจ "promoted_verified" ไม่เคยได้ผล; ตอนนี้อ่านก่อน, คงรายการ `added` เดิม และ dry-run ไม่ลบบันทึกการ promote ที่ยืนยันแล้ว
- `scripts/focus_apply_batch.py`, `scripts/focus_tune.py`: เพิ่ม bootstrap path ให้รันตรงด้วย `python scripts/<ชื่อ>.py` ได้ (เดิมได้ `ModuleNotFoundError`; `python -m scripts.<ชื่อ>` ใช้ได้อยู่แล้ว)
- `scripts/resolve_common.py`: `preserved_state` คืน Media Pool folder ด้วย และรายงานบน stderr เมื่อคืนค่าขั้นใดไม่สำเร็จ แทนการกลืน exception เงียบๆ
- ลบ import / ตัวแปรที่ไม่ใช้ (pyflakes สะอาด)

### ย้ายออก
- ย้ายออกไป `Desktop/_archive-davinci-cleanup-2026-10-09/scripts-review-2026-10-09/` (ไม่ได้ลบ): สคริปต์งานครั้งเดียว `render_t02_candidate`, `render_lowerleft_16_42`, `render_bottomleft_batch`, `render_headroom_tune`, `apply_focus_candidate`, `apply_bottomleft_candidates`, `tune_focus_headroom`, `focus_set_transform`; ชุดย้าย 9:16 รอบ M2/M3 `m2_convert_pilot`, `m3_convert`, `calibrate_crop`, `calibrate_zoom`, `compare_invariants`, `survey_sources`, `export_source_stills`, `layout9x16`, `split_projects`, `challenger_m2_1_results.json`; และเทสต์ live `test_m2_*`, `test_m3_*`
### การตรวจ
- ในการเตรียมรีลีสครั้งนี้ รัน `python scripts/verify_skill_bundle.py` ได้ `ok: true`, `errors: []`, 449 ไฟล์ใน manifest และ 73 ลิงก์ภายใน; ผลอยู่ใน `docs/validation-report.json` (ตัวสแกน Hermes ไม่พร้อม จึงเป็นการตรวจโครงสร้าง/checksum) รัน `git diff --check` ผ่านด้วย
- รายงาน Armigon ข้างต้นเป็นหลักฐาน QC ที่บันทึกไว้ก่อนหน้านี้ ไม่ใช่การทดสอบสดของสคริปต์ทั้งหมดในรีลีสนี้ ไม่มีการเชื่อมต่อ Resolve หรือตรวจวิดีโอ render เต็มช่วงในการเตรียมรีลีสครั้งนี้

## v0.8.0

### Added
- `scripts/resolve_common.py`: เพิ่ม `require_resolve()` ที่จบโปรแกรมพร้อมข้อความชัดเจนเมื่อเชื่อมต่อ Resolve ไม่ได้ และ `preserved_state(resolve)` ที่คืนโปรเจกต์ ไทม์ไลน์ playhead และเพจให้เหมือนเดิมเมื่อจบงาน (คืนค่าได้แม้เนื้อหาข้างในล้มเหลว)
- `scripts/resolve_preflight.py`: เพิ่มตัวเลือก `--list-tools` สำหรับดูรายชื่อ tool ใน catalog ของ MCP; ไม่ต้องใส่ `--need` เมื่อใช้ตัวนี้
- `scripts/README.md`: จัดกลุ่มเครื่องมือทั้งหมด พร้อมลำดับการใช้งาน (MCP ก่อน แล้ว preflight แล้วค่อยสคริปต์)
- `tests/test_resolve_common.py`: ทดสอบ `preserved_state` และ `require_resolve` ด้วย Resolve จำลอง
- `.agents/skills/resolve-mcp/SKILL.md`: เพิ่มตาราง "Live tool map" ที่บอกว่างานแต่ละอย่างใช้ tool ของ `davinci-resolve` MCP ตัวไหน และขั้นตอนตรวจ MCP ทางการของ Resolve (`get_whats_new`, `search_scripting_api`, `run_script`) ก่อนเขียนสคริปต์เอง

### Updated
- `scripts/resolve_common.py`: ค้นหาโมดูล Resolve จาก `C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules` ด้วย
- `scripts/apply_vdo_preset.py`, `scripts/load_subtitle_preset.py`, `scripts/split_projects.py`: เลิกเขียนตัวเชื่อมต่อเอง ใช้ตัวกลางใน `resolve_common` แทน (คงชื่อ `connect_resolve` ใน `load_subtitle_preset.py` เพราะ `apply_video_style.py` เรียกใช้)
- `scripts/apply_bottomleft_candidates.py`, `render_bottomleft_batch.py`, `render_headroom_tune.py`, `render_lowerleft_16_42.py`, `render_t02_candidate.py`, `tune_focus_headroom.py`: แตกคำสั่งบรรทัดเดียวที่ต่อกันด้วย `;` ให้เป็นบรรทัดแยก ตรรกะเหมือนเดิม (ตรวจโครงสร้างโค้ดตรงกันทุกไฟล์) ยังไม่ได้ทดสอบกับ Resolve จริง
- `scripts/refresh_skill_manifest.py`: `bundle_version` เป็น 0.8.0
- `docs/skills-manifest.json` และ `docs/validation-report.json`: สร้างใหม่หลังจัดระเบียบไฟล์

### Removed
- ย้ายสคริปต์ทดลอง/ใช้ครั้งเดียวที่ไม่มีเอกสาร สกิล หรือเทสต์อ้างถึง 73 ไฟล์ออกจาก repo ไปไว้ที่ `Desktop/_archive-davinci-cleanup-2026-10-09/scripts/` (ไม่ได้ลบทิ้ง) รวมถึงชุด VTuber focus เก่า ไฟล์ `dbg_*`, `diagnose_*`, `probe_*`, `test_v*`, `test_challenger_*` และ `aomimama_*`
- ย้ายสกิลทั่วไปสำหรับงานเขียนโค้ด 38 ตัว (จาก `mattpocock/skills` เช่น `tdd`, `wizard`, `teach`) ออกจาก `.agents/skills/` ไปไว้นอกโปรเจกต์ ทำให้เหลือสกิลของ Resolve, house-style และสกิลภาษาไทย 17 ตัว
- ลบโฟลเดอร์ `scratch/` (ไฟล์ทดลองและภาพนิ่ง ไม่เคยอยู่ใน git)
- ลบ `skills-lock.json` ที่ว่างเปล่า

### Validation
- `python scripts/verify_skill_bundle.py` — `ok: true`
- เทสต์ที่ไม่ต้องใช้ Resolve จริง — ผ่าน 105 รายการ ล้มเหลว 1 รายการ (`test_review_analysis_budget.py` ต้องใช้โมดูล `agent` ของ Hermes ที่ไม่มีในเครื่อง)
- `tests/test_m1_*`, `test_m2_*`, `test_m3_*` ไม่ได้รัน; `test_m1_backup_empirical` และ `test_m1_baseline_validation` ล้มเหลวเพราะไฟล์เก่ากว่า 24 ชั่วโมงและผูกกับโปรเจกต์ KT404
- ยังไม่ได้ทดสอบสคริปต์ที่แก้กับ Resolve จริง

## v0.7.0

### Added
- ชุดเครื่องมือออฟไลน์สำหรับตรวจและเพิ่ม SFX/BGM/GIF ให้ทุก Timeline โดยไม่ใช้ API วิเคราะห์วิดีโอ: `scripts/review_enrichment_readonly.py`, `scripts/build_offline_review.py`, `scripts/build_offline_asset_draft.py`, `scripts/resolve_preflight.py`, `scripts/resolve_common.py`
- `scripts/apply_vdo_python.py`: จับค่าที่เปิดเผยของ GIF ที่โหลด preset `vdo` แล้วด้วย UI แล้วใช้กับ GIF ตาม project/timeline/clip ID; dry-run เป็นค่าเริ่มต้น ต้องมี DRP backup ก่อนเขียน และคืน UI state
- `scripts/enrich_timelines_python.py`: เพิ่ม SFX/BGM/GIF บนสำเนา Timeline ด้วย Resolve Python; dry-run เป็นค่าเริ่มต้น, ไม่มีจุดจากซับที่พอจะเสนอ BGM อย่างเดียวโดยไม่แต่งจังหวะมุกขึ้นเอง, คง GIF เดิมที่ทับช่วงไว้
- `scripts/promote_drafts_to_originals.py`: ย้ายงานที่ตรวจแล้วเข้าต้นฉบับตาม ID จริง ทำซ้ำได้ (นับ (ชื่อ asset, record frame) ที่มีอยู่แล้วเป็นรายการเดิม) และปฏิเสธเมื่อต้นฉบับไม่ตรง baseline
- `scripts/anomaly_sweep.py`: ตรวจความผิดปกติทั้งโปรเจกต์แบบอ่านเท่านั้น (ช่วงเวลา คลิปหลุดขอบ คลิปซ้อน คลิปซ้ำ ไฟล์ต้นทางหาย GIF นานเกิน ค่า `vdo` ความยาว BGM จำนวนซับ)
- `scripts/cleanup_backups.py`: export `.drp` ใหม่ที่ตรวจแล้วหนึ่งไฟล์ก่อนลบ archive
- `scripts/refresh_skill_manifest.py`: สร้าง `docs/skills-manifest.json` ใหม่จากไฟล์จริง (เพิ่ม/ลบ/อัปเดต checksum และเรียก validator ต่อ)
- `scripts/apply_offline_enrichment_pilot.py`, `scripts/render_enrichment_pilot.py`, `scripts/render_review_previews.py`, `scripts/verify_review_resume.py`, `scripts/delete_draft_copies.py`, `scripts/audit_promotion.py`, `scripts/audit_draft_copies.py`, `scripts/export_enrichment_backup.py`, `scripts/finish_timeline1.py`, `scripts/reapply_pilot_original.py`, `scripts/smoke_offline_review.py`, `scripts/smoke_alternative_video.py`, `scripts/run_draft_batches.sh`, `scripts/run_promotion_batches.sh`
- tests ออฟไลน์ 10 ไฟล์ (`tests/test_offline_*.py`, `tests/test_apply_vdo_python.py`, `tests/test_enrich_timelines_python.py`, `tests/test_render_enrichment_pilot.py`, `tests/test_resolve_preflight.py`, `tests/test_review_analysis_*.py`, `tests/test_review_resume_cache.py`)

### Updated
- `.agents/skills/resolve-video-enrichment/references/automation-safety.md`: เพิ่มหัวข้อ draft-then-promote ที่บันทึกจากของจริง 4 ข้อ — ลำดับสำเนาก่อนต้นฉบับ, การย้ายแบบ idempotent, Resolve conform GIF สั้นกว่าที่ขอ 2 เฟรม จึงต้องตรวจช่วงจริงไม่ใช่ค่าที่ขอ, และ native subtitle item ไม่มี Media Pool entry (เคยทำให้ sweep รายงานผิด 960 ครั้ง)
- `resolve-video-enrichment` (SKILL.md + house-style): กฎ native Subtitle-only, ขอบเขต style ที่ผู้ใช้ถือเอง, และ Thai cue cap 1.5 วินาที ตรงกับไฟล์ที่ลงทะเบียนใน manifest
- `docs/OPERATING-NOTES.md`: เพิ่ม 6 กฎที่วัดได้ + ตารางเครื่องมือ + ย้ำว่าเส้นทางออฟไลน์ไม่พึ่ง provider ใด
- `README.md`: เพิ่มขั้นตอน 9 ขั้นพร้อมคำสั่งจริง และข้อจำกัดที่ต้องรายงานเสมอ
- `docs/skills-manifest.json` (237 ไฟล์, bundle_version 0.7.0) และ `docs/validation-report.json` — สร้างใหม่หลังจัดระเบียบไฟล์
- `.gitignore`: เพิ่ม `.hermes/` สำหรับไฟล์งานเฉพาะเครื่อง

### Removed
- ลบ artifact งานภายใน 1,379 ไฟล์ที่เลิกใช้แล้วออกจาก index: `.agents/teamwork/**` (บันทึกประสานงาน/audit), `reference/**` และ `scratch/**` ซึ่ง `.gitignore` กันไว้อยู่แล้ว (`*.drp`, `*.mp4`, `*.mov` ยังคงถูก ignore)

### Validation
- `python scripts/verify_skill_bundle.py` — `ok: true`, `errors: []`, 237 manifest files, 17 core skills, ลิงก์ในโปรเจกต์ 65 จุด
- `python -m unittest tests.test_skill_bundle` — ผ่าน 9 tests
- tests ออฟไลน์ของ helper ใหม่/ที่แก้ — ผ่าน 33 tests
- ตรวจ path ที่อ้างใน `README.md` และ `docs/OPERATING-NOTES.md` ด้วยสคริปต์ — 12/12 มีอยู่จริง
- `git diff --check` — สะอาด

### Scope
- งานนี้คือชุด skills, คู่มือ, เครื่องมือออฟไลน์ และการจัดระเบียบไฟล์ในรีโป ไม่ได้เปลี่ยนซอร์สฟุตเทจหรือโปรเจกต์ Resolve ระหว่างจัดทำ release
- 8 test modules ที่ต้องใช้ `pytest` (`test_enrichment_assets`, `test_enrichment_engine`, ชุด `m1`–`m3`, `test_pilot_readback`) ยัง import ไม่ได้ใน interpreter นี้เพราะไม่มีแพ็กเกจ — เป็นสภาพเดิมก่อนงานนี้ ไม่ได้แก้และไม่ปิดบัง
- `.hermes/` (ผลตรวจ, รายงาน, render, `.drp`) ถูก ignore จึงไม่เข้า bundle
- ยังไม่ผ่านการตรวจภาพ/ฟังเสียงจริงของทั้ง 49 Timeline และยังไม่ได้ยืนยันสิทธิ์ของ asset ที่ใช้

## v0.6.0

### Added
- `scripts/apply_video_style.py`: capture and apply exposed video properties from an approved reference clip to explicit timeline item IDs. Dry-run is the default; writes require a verified DRP backup and include property readback, rollback, protected timeline comparisons, and UI-state restoration. It is not a native named Video Preset loader and makes no Resolve database writes.
- Offline orchestration coverage for project/timeline ID refusal, invalid backup refusal, and successful save/readback/restoration. `docs/guides/video-style-script.md` and a sanitized example at `presets/video/approved-gif-style.json` contain no live project clip ID or filename.
- `.agents/skills/thai-subtitles-resolve/references/srt-insertion-and-presets.md` with SRT insertion, exact saved-preset discovery, database-write boundaries, and post-load verification.

### Updated
- `thai-subtitles-resolve` v0.4.0 now documents reuse of Media Pool SRT items, exact cue/frame readback, failure-safe append recovery, and approved saved font presets.
- House style, `resolve-edit`, `resolve-video-enrichment`, operating notes, and README clarify approved preset use and distinguish native APIs from database workarounds.

### Validation
- `python -m unittest discover -s tests -p test_apply_video_style.py -v` — 10 tests passed.
- The helper was live-verified against explicitly approved GIF items during development; this release preparation did not connect to or modify a Resolve project.

### Scope
- Editing-skill bundle and helper documentation only. No source media, Resolve project, or database was changed for this release. Caption/GIF visual review and listening QC remain separate checks.

## v0.5.0

### Added
- `scripts/apply_vdo_preset.py` + `scripts/video_presets.json`: applies the Inspector Video preset "vdo" to GIF items on the V2 REACTIONS track. Resolve 21.1 has no API for Inspector > Video Presets > Load Preset and `User.db` does not expose the preset body, so the script writes captured property values (Zoom 0.42 gang, Pan 0, Tilt 32.28, others default) with `SetProperty`. Dry run by default; `--apply`, `--timeline`, `--only-originals`, `--track-name`, `--capture NAME` (captures from the clip under the playhead).
- `resolve-video-enrichment/references/horizontal-gif-placement.md`: 16:9 GIF placement, the measured Pan/Tilt-to-pixel model (X shift = Pan*fitted_w/1920, Y shift = Tilt*fitted_h/1080), GIF import timing (Resolve 25 fps normalization, 1.5s minimum), per-timeline loudness-based BGM/SFX levels.

### Updated
- Synced `resolve-video-enrichment` with the live Hermes copy (also brings the previously unsynced `katy404-channel-study.md`, `vertical-9x16-conversion.md`, `assets/` and edits to `asset-library-and-cues.md`, `automation-safety.md`, `illustration-assets.md`).

### Verified
- Live on Resolve Studio 21.1.0.17, project `tygarina_2026-09-30_FreeTalk_1`: preset applied to 63 of 64 GIF items (10 originals + 10 `[ENHANCED]` copies; 1 already matching), 0 failures, repeat dry run reports 0 changes, active timeline/playhead/page restored.
- Enrichment of the same 10 timelines (SFX/BGM/GIF added to originals and copies, protected V1/A1/subtitle ranges unchanged) was read back; a 3-timeline pixel check confirmed GIF bounding boxes before the preset was applied.

### Scope
- Not a real Load Preset: the preset values are a captured clone; re-capture if "vdo" changes. No listening QC, no render, and no per-file license check of the BGM/SFX/GIF assets was done.
- `tests/test_skill_bundle.py::test_bundle_structure_references_and_checksums` was already failing before this release (core skill count 16 vs 18 and an out-of-date file manifest); `docs/skills-manifest.json` was not refreshed here.

## v0.4.0

### Added
- `scripts/load_subtitle_preset.py`: loads a saved Subtitle track preset (Inspector > Load Preset) by script. Resolve 21.1 has no preset API, so it copies the preset bytes (`User.db` `SubtitlePresetsBA`) into each target track's `EffectFiltersBA` in `Project.db`. Dry run by default; `--apply` saves, exports a `.drp`, closes the project, snapshots `Project.db`, writes one transaction, reopens, restores timeline/playhead/page and verifies blobs and cue counts.
- `--orientation horizontal|vertical` selects timelines by resolution (Mitr Font for 16:9, Mitr-short-001 for 9:16 in the user's library).
- `tests/test_load_subtitle_preset.py`: offline tests for blob parsing/round-trip and exact-row database writes.

### Verified
- Applied `Mitr Font` to 10/10 subtitle tracks of project `tygarina_2026-09-30_FreeTalk_1` (8 changed, 2 already matching); cue counts unchanged; repeat dry run reports 0 changes. The vertical path is dry-run tested only.

## v0.2.0

### Added
- `resolve-video-enrichment/references/adjustment-focus.md`: using the user's selected Adjustment Clip as a protected template (selection readback, copy rather than move, per-timeline templates) and a 9-point per-cue VTuber framing checklist (subtitle association, new-track placement, prominence, centering, head-to-chest/hands, headroom, no crop, caption/HUD overlap, scope audit).
- `resolve-video-enrichment/references/illustration-assets.md`: planning, rights, organization, import, placement, and QC of still-image overlays.
- KT404 enrichment tooling: `scripts/enrichment_assets.py`, `scripts/enrichment_engine.py`, `scripts/run_pilot.py`, with tests, plus the design spec and implementation plans under `docs/superpowers/`.
- Working references and QC evidence under `reference/` and `scratch/`.

### Updated
- Synced `resolve-video-enrichment` with the live Hermes copy: per-timeline `timelineFrameRate` for record/source conversions, full-length BGM and 1.5–2.5s GIF holds, and new Thai trigger phrases.
- Bundle manifest checksums and counts refreshed for the release contents.

### Scope
- No claim of live Resolve verification for the new guidance; the pilot tooling's own results are recorded in `WORKLOG.md`.

## v0.1.0

First versioned release of the DaVinci Resolve editing skill bundle. The bundle version is independent of Resolve, the upstream MCP server, and individual archived skill versions.

### Added
- Thai VTuber editorial guidance: selecting self-contained highlights, truthful hooks, comic timing, and preserving the creator's personality.
- On-demand chapters for Resolve editing, Thai captions/audio/framing, YouTube packaging/feedback, and delivery/rights, with primary-source references.
- A reusable edit brief, cutlist, experiment plan, and acceptance-record template.

### Updated
- Expanded `resolve-video-enrichment` into a lean core with 11 reference chapters and one template, retaining the existing enrichment/recovery workflows.
- Clarified native subtitles versus burned-in pixels, evidence-led cue placement, measured audio versus scripting capability, source-frame timebases, and approval-gated repair/cleanup.
- Preserved the project's native Subtitle-track workflow and Thai short-form limits: three short words/about 14 Thai characters, at most 1.5 seconds, and no spaces between Thai words except appropriate Latin boundaries.
- Refreshed bundle provenance/checksums and validation evidence for the release contents.

### Fixed
- Bundle validation now accepts Git's LF/CRLF conversion for UTF-8 text while still rejecting content changes and preserving exact binary checksums; regression tests cover both newline directions and binary changes.

### Scope
- Skills, documentation, and bundle-validation release only: no MCP implementation, Resolve project, source media, or live editing behavior was changed.
- No claim of proven audience growth, channel-specific analytics, or live Resolve verification.
- Unrelated local editing plans, worklogs, scratch reports, media, and project backups are not part of this release change.
