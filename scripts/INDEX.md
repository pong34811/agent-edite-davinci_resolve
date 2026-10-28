# scripts/INDEX.md — งาน → script (ค้นที่นี่ก่อนเขียนเครื่องมือใหม่)

ลำดับ: MCP ก่อน → `python scripts/resolve_preflight.py --need <tool.action>` → หา script ในตารางนี้ → ถ้าไม่มีจริงๆ ค่อยเขียนใหม่ใน `scripts/scratch/` (ดู `AGENTS.md`) แล้วโปรโมตเข้า `scripts/` พร้อมเพิ่มแถวที่นี่ (tests/test_agent_entrypoints.py ตรวจว่าทุกไฟล์ใน `scripts/*.py` มีแถวในไฟล์นี้)

คอลัมน์ **ขอบเขต**: `ใช้ซ้ำ` = ใช้กับโปรเจคใดก็ได้ · `p2` / `armigon` / `sakuyako` = เขียนสำหรับโปรเจคนั้น อ่านโค้ดและแก้ค่าคงที่ก่อนใช้กับโปรเจคอื่น · `ครั้งเดียว` = pilot หรือแก้เฉพาะกิจ ใช้เป็นตัวอย่างเท่านั้น

ทุก script ที่เขียนค่า: เชื่อมผ่าน `resolve_common.connect_resolve`, ครอบด้วย `preserved_state(resolve)`, อ่านกลับทุกการเขียน, ทำบนสำเนา/variant

## 1. พื้นฐานและการตรวจก่อนเริ่ม

| Script | ทำอะไร | ขอบเขต |
|---|---|---|
| `resolve_common.py` | `connect_resolve`, `require_resolve`, `preserved_state`, `api_has_method` — import เท่านั้น | ใช้ซ้ำ |
| `resolve_preflight.py` | ตัดสิน `USE_MCP` / `FALLBACK_SCRIPT` / `BLOCKED` (`--need`, `--list-tools`, `--probe-api`) | ใช้ซ้ำ |
| `check_mcp_update.py` | เทียบเวอร์ชัน MCP ชุมชนที่ติดตั้งกับ tag ล่าสุดของ samuelgursky/davinci-resolve-mcp (`--apply` อัปเดตให้) — รันก่อนเริ่มทุกงาน | ใช้ซ้ำ |
| `backup_drp.py` | export + verify `.drp` ก่อนแก้เป็นชุด | ใช้ซ้ำ |
| `resolve_recover.py` | Resolve ปิดเอง/ค้าง: เปิด Google Drive ถ้า library หาย → kill ถ้าค้าง → เปิดผ่าน explorer → เปิดโปรเจกต์เดิม (`--project`, `--dry-run`) | ใช้ซ้ำ |
| `delete_archived_timelines.py` | ลบ timeline `<ชื่อ>_archived_vNN` ที่ MCP สร้าง (dry-run ก่อน, เทียบ V/A กับ timeline หลัก, สำรอง `.drp` แล้วลบด้วย `--confirm`) | ใช้ซ้ำ |
| `cleanup_backups.py` | export `.drp` ใหม่ที่ตรวจแล้ว แล้วลบ archive ที่ระบุ (ต้องได้รับอนุญาต) | ใช้ซ้ำ |
| `review_enrichment_readonly.py` | inventory read-only ของทุก timeline/track/item | ใช้ซ้ำ |
| `anomaly_sweep.py` | ตรวจโครงสร้างผิดปกติทุก timeline (รายงานอย่างเดียว) | ใช้ซ้ำ |
| `prepare_edit.py` | เตรียม intake offline พร้อม probe cache, แบบร่าง edit decisions, lint ซับ/contact sheet เดิม; ไม่ต่อ Resolve | ใช้ซ้ำ |
| `edit_workflow.py` | ตรวจแผนเฟรม/เหตุผลการตัด และ reconcile เกณฑ์ตรวจรับกับ evidence hash (`validate`, `accept`, `hash`) | ใช้ซ้ำ |
| `verify_skill_bundle.py` | ตรวจชุด skills ไม่ต้องต่อ Resolve | ใช้ซ้ำ |
| `refresh_skill_manifest.py` | อัปเดต `docs/skills-manifest.json` และตรวจซ้ำหลังแก้ repo | ใช้ซ้ำ |
| `release.py` | สร้าง patch release ค่าเริ่มต้น พร้อม changelog ภาษาไทยแบบ bullet; `--publish` อัปเดต VERSION/CHANGELOG, commit, tag, push และสร้าง GitHub Release | ใช้ซ้ำ |

## 2. ซับไตเติลภาษาไทย

| Script | ทำอะไร | ขอบเขต |
|---|---|---|
| `asr_words_th.py` | ASR ไทยระดับตัวอักษร (faster-whisper) offline | ใช้ซ้ำ |
| `build_dynamic_srt.py` | สร้าง SRT สั้นจากจุดเริ่ม cue ที่คัดแล้ว | ใช้ซ้ำ |
| `caption_lint.py` | ตรวจ SRT ตามกฎ house style (≤14 ตัวอักษร ≤1.5 วิ) | ใช้ซ้ำ |
| `verify_srt_on_timeline.py` | เทียบ cue บน Subtitle track กับ SRT (ข้อความ + เฟรม) | ใช้ซ้ำ |
| `load_subtitle_preset.py` | อ่าน/โหลด Subtitle preset (dry-run เท่านั้น ห้ามข้ามบล็อก `--apply`) | ใช้ซ้ำ |
| `drt_add_native_subtitle.py` | เติม native subtitle 1 cue ลง DRT | ใช้ซ้ำ |
| `drt_shift_subtitles.py` | แก้ offset ท้าย timeline ของซับที่สร้างจาก SRT ใน DRT | ใช้ซ้ำ |
| `p2_fix_captions.py` | สร้างซับแนวตั้ง p2 ใหม่ตามกฎสั้น | p2 |
| `p2_fix_captions_horizontal.py` | แผน offline ซับแนวนอน p2 (44 timeline) | p2 |
| `p2_apply_fixed_captions.py` | ใส่ SRT ที่แก้แล้วลง Subtitle track (`--horizontal` ได้) | p2 |
| `p2_verify_captions_after.py` | ตรวจหลังแก้ซับ read-only | p2 |
| `armigon_fix_captions.py` | แผน offline สร้างซับ armigon-2026-09 | armigon |
| `load_subtitle_preset_auto.py` | คำสั่งเดียวโหลด Subtitle preset ลง timeline ตามชื่อ (Resolve 21.1 ไม่มี API) | ใช้ซ้ำ |
| `patch_subtitle_preset_offline.py` | แพตช์ Project.db ตอน Resolve ปิด เพื่อโหลด preset 1 timeline (ต้องมี `.drp` สำรอง + ได้รับอนุญาต) | ใช้ซ้ำ |

## 3. VTuber Zoom / Adjustment Clip / Focus

| Script | ทำอะไร | ขอบเขต |
|---|---|---|
| `drt_focus_track.py` | ฉีด Adjustment Clip track ลง DRT (วิธีที่ปลอดภัยกว่า InsertGenerator) | ใช้ซ้ำ |
| `drt_focus_multi.py` | DRT offline: track ใหม่ 1 track ที่มี Adjustment Clip หลายช่วง (`--ranges`) ต่อยอด `drt_focus_track` | ใช้ซ้ำ |
| `import_focus_drt.py` | import DRT ที่ patch แล้วเป็น `_focus_variant` + ใส่ Fusion Transform ให้ทุก Adjustment Clip (dry run เป็นค่าเริ่ม, `--apply`) | ใช้ซ้ำ |
| `render_subtitle_stills.py` | render เฟรมเดี่ยวเป็น PNG พร้อม burn-in ซับ (แทน still export ที่ไม่ติดซับ) | ใช้ซ้ำ |
| `drt_rebuild_focus_track.py` | แทนที่ทุก clip บน Adjustment Clip track ที่ระบุชื่อใน DRT ด้วย clip ใหม่ตามช่วงที่กำหนด (`--create` สร้าง track ก่อน); ใช้ใส่หลายช่วงในครั้งเดียว หรือซ่อม clip ที่ถูกยืดหัวแล้ว render ไม่ได้ | ใช้ซ้ำ |
| `rebuild_trimmed_zoom_clip.py` | สร้าง Adjustment Clip track ใหม่บน timeline ที่เปิดอยู่ด้วย InsertGenerator (ลบทั้ง track แล้วใส่ตามลำดับเวลา, คง Transform) หลังตัดหัว timeline; บน 21.1.0.17 ให้ใช้ `drt_rebuild_focus_track.py` แทน (ดู OPERATING-NOTES) | ใช้ซ้ำ |
| `apply_vtuber_zoom.py` | เพิ่ม Zoom-Focus track บนสำเนา timeline (`--in-place` เมื่อผู้ใช้สั่งเท่านั้น) | ใช้ซ้ำ |
| `retune_vtuber_zoom.py` | ปรับ Fusion Transform ของ Adjustment Clip ทุกตัวบน focus track | ใช้ซ้ำ |
| `zoom_variant_stills.py` | export still จริงต้น/กลาง/ท้ายช่วงซูมสำหรับ QC | ใช้ซ้ำ |
| `focus_frame_qc.py` | contact sheet + รายงาน framing (headroom, ตัดหัว/มือ) | ใช้ซ้ำ |
| `focus_tune.py` | ตั้ง Transform ของ focus clip 1 ตัว + render 1 เฟรม | ใช้ซ้ำ |
| `focus_qc_frames.py` | render ช่วงสั้นของ timeline ที่เปิดอยู่ (burn-in ซับ) แล้วดึงเฟรม QC (`--width/--height` สำหรับ 9:16) | ใช้ซ้ำ |
| `focus_qc_all.py` | render ทุก focus cue ต่อ timeline + contact sheet | p2 |
| `focus_apply_batch.py` | apply/verify focus บน aomimama-2026-09-p1 | p2 |
| `focus_apply_p2.py` | apply focus บน aomimama-2026-09-p2 | p2 |
| `plan_p2_focus.py` | วางแผน beat ที่เห็น VTuber + ค่า Transform (read-only) | p2 |
| `deploy_climbing_focus.py` | ย้าย focus timeline เข้าโปรเจคหลักผ่าน DRT | ครั้งเดียว |
| `armigon_focus_pilot.py` | pilot Adjustment Clip บนสำเนาชั่วคราว | armigon |
| `fix_focus_black_band.py` | แก้แถบดำใต้เฟรม focus ใน `_9x16` Mobile-Legends | ครั้งเดียว |
| `scan_p2_vtuber_presence.py` | ดึงเฟรมกลางของแต่ละ timeline ดูว่ามี VTuber ไหม | p2 |

## 4. แปลง 16:9 → 9:16

| Script | ทำอะไร | ขอบเขต |
|---|---|---|
| `p2_9x16_common.py` | helper ร่วม (import เท่านั้น) | p2 |
| `p2_9x16_inventory.py` | inventory timeline p2 ก่อนแปลง (read-only) | p2 |
| `p2_9x16_sources.py` | still ต้นฉบับสำหรับ calibrate facecam | p2 |
| `p2_9x16_cutscan.py` | สแกน scene cut ของ V1 ทั้งช่วง | p2 |
| `p2_9x16_build.py` | สร้างโครง `<name>_9x16` (pilot) | p2 |
| `p2_9x16_layout.py` | ใส่ transform/layout ของ 9:16 | p2 |
| `p2_9x16_convert.py` | ตัวแปลงหลัก 1 original → `<name>_9x16` (`--slow-raster`) | p2 |
| `katy_9x16.py` | สร้าง/จัด layout `<original>_9x16` ของ Katy404 day-23 (`build`/`layout`/`stills`) | ครั้งเดียว |
| `p2_9x16_charscene.py` | 9:16 เต็มจอสำหรับฉากตัวละคร (ไม่มี game panel) | p2 |
| `p2_9x16_sections.py` | 9:16 ต่อ section เมื่อ V1 เปลี่ยนฉาก OBS | p2 |
| `p2_9x16_gif_relayout.py` | จัด GIF V2 ให้อยู่ใน game panel เหนือรอยต่ออวาตาร์ | p2 |
| `p2_9x16_verify.py` | ตรวจ 9:16 เทียบ original + baseline (read-only) | p2 |
| `p2_9x16_verify_t3.py` | ตรวจเฉพาะ #3 | ครั้งเดียว |
| `p2_delete_stray_copy.py` | ลบสำเนา `_9x16` ที่สร้างค้าง (ชื่อ+id ตรง) | p2 |
| `build_9x16_batch.py` | สร้าง `<name>_9x16` จาก 16:9 (Mobile-Legends/Roblox) | sakuyako |
| `run_batch_9x16.py` | รัน build ทีละ timeline + verify still | sakuyako |
| `create_and_fix.py` | สร้าง 9:16 แล้ว apply crop fix | sakuyako |
| `apply_group_fix.py` | แก้ crop ขวาของ track ตามชื่อ | sakuyako |
| `inventory_remaining_9x16.py` | หา original ที่ยังไม่มี `_9x16` | sakuyako |
| `inventory_sources_9x16.py` | source/ความละเอียดของ original ที่ยังไม่มี `_9x16` | sakuyako |
| `qc_vertical_all.py` | QC `_9x16` ทุกตัวเทียบ original | sakuyako |
| `qc_vertical_stills.py` | สุ่ม still `_9x16` สำหรับ QC | sakuyako |
| `vertical_layout_repair_pilot.py` | geometry ซ่อม vertical (pilot) | ครั้งเดียว |
| `fix_t3_9x16.py` | แก้ #3 `_9x16` | ครั้งเดียว |
| `fix_vtuber2d_9x16.py` | แก้ 9:16 VTuber 2D | ครั้งเดียว |
| `rebuild_t3_9x16.py` | สร้าง #3 ใหม่ทั้งตัว | ครั้งเดียว |
| `inspect_t3.py` | ดู #3 ละเอียด | ครั้งเดียว |
| `armigon_9x16_pilot.py` | pilot 9:16 Armigon บน duplicate | armigon |
| `armigon_9x16_batch_one.py` | สร้างและตรวจ Armigon 9:16 ทีละ 1 | armigon |
| `armigon_9x16_focus_retarget.py` | ย้ายเป้า Adjustment Clip ของ pilot ไปที่ chibi | armigon |
| `armigon_9x16_reframe_target.py` | reframe 9:16 ตัวแรกโดยไม่แตะ protected tracks | armigon |
| `armigon_9x16_fractional_probe.py` | probe readback ช่วง focus เฟรมเรตผสม (ทิ้งได้) | ครั้งเดียว |
| `armigon_9x16_snapshot.py` | baseline read-only ของ 48 timeline แนวนอน | armigon |
| `build_9x16_day22.py` | สร้าง `<name>_9x16` โปรเจค Katy404 Minecraft day 22 (60 fps, อวาตาร์ขวาล่าง) | ครั้งเดียว |
| `build_9x16_day24.py` | เหมือนกันสำหรับ day 24 | ครั้งเดียว |
| `sakuyako_update_vertical_masters.py` | โปรโมตตัวแปรแนวตั้งที่ใส่ cover แล้วเป็น master | sakuyako |

## 5. Enrichment: BGM / SFX / GIF

| Script | ทำอะไร | ขอบเขต |
|---|---|---|
| `enrichment_engine.py` | วิเคราะห์ cue ซับและกฎวางตำแหน่ง (import) | ใช้ซ้ำ |
| `enrichment_assets.py` | ingest asset + สำรองความปลอดภัย (import) | ใช้ซ้ำ |
| `enrich_timelines_python.py` | enrich เป็นชุดบนสำเนา (dry-run เป็นค่าเริ่มต้น) | ใช้ซ้ำ |
| `apply_enrichment_d22.py` | ใส่ BGM+SFX+GIF ที่อนุมัติลงสำเนา `[ENHANCED]` | ใช้ซ้ำ |
| `apply_vdo_preset.py` | ใช้ Video preset (`vdo`) กับ GIF บน REACTIONS | ใช้ซ้ำ |
| `apply_vdo_python.py` | จับค่า vdo จาก clip ที่โหลดด้วย GUI แล้ว apply ตาม ID | ใช้ซ้ำ |
| `apply_video_style.py` | จับ/apply คุณสมบัติวิดีโอ native | ใช้ซ้ำ |
| `promote_drafts_to_originals.py` | ยก draft ที่ตรวจแล้วเข้า original (idempotent) | ใช้ซ้ำ |
| `build_offline_asset_draft.py` | shortlist asset + หน้า review | ใช้ซ้ำ |
| `build_offline_review.py` | packet review offline ต่อ timeline | ใช้ซ้ำ |
| `apply_offline_enrichment_pilot.py` | pilot บนสำเนาที่กู้คืนได้ | ครั้งเดียว |
| `render_enrichment_pilot.py` | render pilot สำหรับ QC | ครั้งเดียว |
| `run_pilot.py` | pilot บน Timeline 1 | ครั้งเดียว |
| `p2_dump_cue_inputs.py` | dump ซับ + asset candidate สำหรับร่าง cue | p2 |
| `p2_build_sample_cues.py` | cue sheet ตัวอย่าง 3 ชุด | p2 |
| `p2_build_all_cues.py` | cue spec → cue sheet ที่วัดแล้ว | p2 |
| `p2_apply_cues.py` | apply cue sheet ที่อนุมัติลง original | p2 |
| `p2_verify_all.py` | ตรวจ enrichment เทียบ baseline + cue sheet | p2 |
| `p2_trim_bad_gif_tail.py` | ตัดเฟรมท้าย GIF ที่ render ไม่ได้ | p2 |
| `p2_inventory_readonly.py` | inventory p2 ผ่าน review_enrichment_readonly | p2 |

## 6. QC / Review / Contact sheet

| Script | ทำอะไร | ขอบเขต |
|---|---|---|
| `contact_sheet.py` | contact sheet จากโฟลเดอร์เฟรม media_analysis | ใช้ซ้ำ |
| `render_review_previews.py` | preview เพื่อ review (ไม่แก้ timeline) | ใช้ซ้ำ |
| `analyze_review_previews.py` | วิเคราะห์ preview ที่ได้รับอนุญาต | ใช้ซ้ำ |
| `verify_review_resume.py` | ตรวจ preview ที่บันทึกกับ Resolve สด | ใช้ซ้ำ |
| `p2_publish_qc.py` | QC ก่อนเผยแพร่ ทั้งแนวนอน/แนวตั้ง (read-only) | p2 |
| `p2_publish_audio_qc.py` | QC loudness/silence ของเสียงต้นทาง | p2 |
| `p2_publish_stills.py` | export still 3 เฟรมต่อ timeline | p2 |
| `armigon_publish_qc.py` | QC ข้อมูลทุก timeline ของ armigon-2026-09 | armigon |
| `armigon_audio_qc.py` | loudness + hook-frame ของ V1 | armigon |
| `armigon_source_ranges.py` | dump source/range ของ V1 | armigon |

## 7. Render / Export

| Script | ทำอะไร | ขอบเขต |
|---|---|---|
| `p2_render_vertical.py` | render `_9x16` ทุกตัว (burn-in ซับ) | p2 |
| `p2_render_horizontal.py` | render แนวนอนทุกตัว (burn-in ซับ) | p2 |
| `p2_loudnorm_worker.py` | loudnorm 2 pass I=-14 สำหรับไฟล์แนวตั้ง | p2 |
| `p2_loudnorm_worker_h.py` | loudnorm 2 pass I=-14 สำหรับไฟล์แนวนอน | p2 |
| `p2_trim_tail_150s.py` | สร้าง variant `<name>_150s` | p2 |
| `p2_export_final.py` | export สุดท้ายด้วย `H.264 Master` (dry-run ถ้าไม่ใส่ `--apply`) | p2 |
| `drt_prepend_cover.py` | เลื่อนเนื้อหาใน DRT ชั่วคราว N เฟรมเพื่อเติม cover (ใช้กับ `p2_export_final.py --prepend-cover-frames`) | ใช้ซ้ำ |
| `sakuyako_export_preflight.py` | จับ baseline ก่อน export (Resolve Python + JSON) | sakuyako |
| `sakuyako_export_final_audit.py` | เทียบไฟล์ที่ export กับ baseline | sakuyako |
| `sakuyako_export_qc.py` | QC ไฟล์ export ด้วย ffmpeg/ffprobe + contact sheet (read-only) | sakuyako |
| `sakuyako_export_resume.py` | ทำต่อเฉพาะ job ที่ manifest เป็นเจ้าของและสถานะ Ready หลังถูกขัดจังหวะ | sakuyako |

## 8. จัดการโปรเจค / timeline

| Script | ทำอะไร | ขอบเขต |
|---|---|---|
| `cleanup_and_rename_timelines.py` | ลบ timeline สำรอง + ตั้งชื่อไทยมาตรฐาน | ใช้ซ้ำ |

---

## เมื่อต้องเพิ่ม script ใหม่

1. ค้นตารางนี้และ `grep -r "<คำสำคัญ>" scripts/` ก่อน
2. เขียนใน `scripts/scratch/<ชื่อ>.py` (gitignored, ไม่ต้องขออนุญาต)
3. ถ้าจะใช้ซ้ำ ย้ายเข้า `scripts/`, ใช้ `resolve_common`, เพิ่ม test ถ้าแก้ state, เพิ่มแถวในตารางนี้
4. รายงาน `MCP-GAP:` line ในคำตอบทุกครั้งที่เขียน script
