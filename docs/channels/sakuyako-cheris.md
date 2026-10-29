# Sakuyako-Cheris

## ตัวตนและคอนเทนต์
- โฟลเดอร์ใน Google Drive ชื่อ `Sakuyako-Cheris` โปรเจคตัดต่อที่พบคือ `sakuyako-2026-09` เนื้อหาเกมมือถือ/สตรีม (Mobile Legends, Roblox ตามคำอธิบายใน script)
- ความสัมพันธ์ระหว่าง Sakuyako กับ Cheris ยังไม่ยืนยัน (ดูหัวข้อสุดท้าย)

## ที่เก็บไฟล์
- Google Drive: `Projects/Sakuyako-Cheris/` มี `00_Channel_Kit`, `sakuyako-2026-09/vdo` (ไฟล์ส่งมอบ), `Thumbnails`, `1.picture`, `อัปโหลดเเล้ว`, `rename_map_original_to_new.json`
- ปก (cover) ส่งออกใน `sakuyako-2026-09/vdo`

## โปรเจคและ timeline ใน Resolve
- โปรเจค `sakuyako-2026-09` (ชื่อใช้ตรวจใน script ก่อนเขียนทุกครั้ง)

## รูปแบบและ layout
- facecam อยู่มุมซ้ายล่างของภาพเกม (ค่าที่ผู้ใช้อนุมัติ ตามคอมเมนต์ใน script)
- แปลง 9:16 ด้วย `build_9x16_batch.py` / `run_batch_9x16.py` / `create_and_fix.py` (แก้ crop ขวา) และตรวจด้วย `qc_vertical_all.py`

## ซับ เสียง และ enrichment
- ส่งออกแนวตั้ง 30 fps ใช้ `p2_export_final.py --prepend-cover-frames 30` เพิ่ม cover เงียบ 1 วินาที; ถ้าไม่ใส่ตัวเลือก จะใช้ cover overlay 1 เฟรมแบบเดิม
- preset ซับตามกฎกลาง ยังไม่ยืนยันเฉพาะช่อง

## Script และ skill ที่เกี่ยวข้อง
- ส่งออก: `sakuyako_export_preflight.py`, `sakuyako_export_final_audit.py`, `sakuyako_export_qc.py`, `sakuyako_export_resume.py`, `drt_prepend_cover.py`, `sakuyako_update_vertical_masters.py`
- แปลง/QC แนวตั้ง: `build_9x16_batch.py`, `run_batch_9x16.py`, `inventory_remaining_9x16.py`, `inventory_sources_9x16.py`, `qc_vertical_all.py`, `qc_vertical_stills.py`
- skill: `resolve-delivery`, `resolve-batch-export`, `resolve-folder-cover-batch`, `vtuber-cover-batch-pipeline`

## กับดักและงานค้าง
- `drt_prepend_cover.py` ต้องมี `zstandard` (`pip install zstandard`) สำหรับบีบอัด DRT
- script ส่งออกสำรอง `.drp` ก่อนทุกครั้ง (`backups/sakuyako-2026-09_before-export-*.drp`); ทำต่อเฉพาะ job ที่ manifest เป็นเจ้าของ (`sakuyako_export_resume.py`)

## งาน `2026-06-Sakuyako` — 85 timelines (2026-10)
- โปรเจกต์ Resolve `2026-06-Sakuyako` มี timeline ต้นฉบับ 85 รายการ; pilot ที่อนุมัติแล้วมีสำเนา `_9x16` เพิ่มหนึ่งรายการ รวม 86 รายการ ณ 2026-10-27
- ผู้ใช้อนุมัติการตัดแบบอนุรักษ์นิยม เก็บไฮไลต์เดิมและตัดเฉพาะช่วงรอ/dead air ที่ชัดเจน, 16:9 บนต้นฉบับ, สร้าง `_9x16` โดยวางเกมด้านบนและอวาตาร์ด้านล่าง, ซับไทย native พร้อม SRT แยก และ H.264 Master 30 fps ที่ `G:\My Drive\Projects\Sakuyako-Cheris\2026-06\vdo\16x9` / `9x16`
- Pilot timeline #84 ผ่านการอนุมัติ: ตัด source frames `[101323, 101492]`, 1,649 frames (~54.97 วินาที) และทำแนวตั้งจากตำแหน่งสื่อของโปรเจกต์นี้
- ไฟล์ pilot MP4 ที่ตรวจแล้วมีอย่างละหนึ่งไฟล์: 16:9 1920×1080 H.264/AAC, 9:16 1080×1920 H.264/AAC, 30 fps, 54.976 วินาที
- เตรียม SRT 85 คู่ รวม 1,711 cues; ชื่อคู่ตรงกันเมื่อถอด suffix `_9x16`, bytes ตรงกัน และ caption lint ผ่านทั้งหมด; มี 15 timeline ที่ไม่มี cue ส่งเข้าคิวตรวจเสียง/ASR ที่ `.hermes/projects/sakuyako-2026-06/asr/caption-review-queue.tsv`; lint ไม่ยืนยันความถูกต้องของคำพูด
- SRT เหล่านี้ยังเป็น sidecar; ยังไม่ได้ใส่ native subtitle track หรือ render ให้ 84 timelines ที่เหลือ
- อัปเดต 2026-10-28 (confirmed, อ่านกลับจาก Resolve): นำ SRT เข้า native Subtitle track ครบ **78/85** timeline ต้นฉบับ — 70 จาก SRT ใน `vdo\16x9` และ 8 จาก ASR draft ที่ตัด cue ให้ ≤1.5 วิ (`scripts/scratch/empty-caption-audio/<n>.capped.srt`: #7, 9, 13, 23, 32, 46, 48, 77; คำยังไม่ได้ตรวจเทียบเสียง); 7 timeline ไม่มีข้อความ (#33, 36, 49, 56, 60, 63, 76) ไม่ใส่ track. ทุก cue ตรง SRT ทั้งข้อความและเฟรม, V1/A1 ไม่ขยับ; `_archived_v01` 20 รายการที่ MCP สร้างเองยังเก็บไว้; สำรอง `backups/2026-10-28-sakuyako-after-caption-import.drp`; ยังไม่ได้ render และยังไม่ได้ใส่ preset ฟอนต์
- กับดัก: project library ของช่องนี้อยู่บน Google Drive (`G:\My Drive\Projects\Resolve Project Library`, library ชื่อ `google drive`, โปรเจกต์อยู่ในโฟลเดอร์ `Sakuyako-Cheris/2026-06`; หลังเปิด Resolve ใหม่อาจค้างที่ Untitled Project ให้เปิดโฟลเดอร์นี้แล้ว LoadProject, อย่าเชื่อ `runtime_mode` ที่รายงาน `Drive Z`) — ถ้า Drive for desktop หยุด Resolve จะ Save ไม่ได้และปิดเอง ใช้ `scripts/resolve_recover.py`
- ซับเฉพาะเสียงพูดของ Sakuyako/คนในสตรีม **ไม่ใส่ซับเสียงพากย์ในเกม** เช่น "ป้องกันฐานของเรากำลังถูกโจมตี" (confirmed โดยผู้ใช้ 2026-10-28)
- ชื่อที่สตรีมเมอร์ใช้เรียกตัวเองสะกดว่า **เชอรี่** (confirmed โดยผู้ใช้ 2026-10-28) — ASR มักได้ยินเป็น "ชนิด", "เฉศนิท", "ชะลีด", "ชาลิก", "ชิคกี้พาย"; ผู้ใช้สั่งให้แก้ให้ตรงกันทั้ง 85 timeline
- ถอดเสียงคลิปที่ยาก: แยกเสียงพูดด้วย demucs → VAD ตัดช่วงสั้น → Whisper large-v3 + Typhoon ASR ถอดช่วงเดียวกันแล้วเทียบ (`scripts/scratch/sakuyako_asr_v3_whisper.py`, `scripts/scratch/sakuyako_asr_v2_typhoon.py`, `scripts/scratch/sakuyako_asr_v2_build.py` ด้วย `ASR_V=v3`). แม้สองโมเดลตรงกัน ≥0.75 ยังมีคำผิด (เช่น "เมฆ" แทน "มีด")
- อัปเดตล่าสุด 2026-10-28 (confirmed, อ่านกลับจาก Resolve): ซับ native ตรงกับ SRT ครบ **81/85** timeline ต้นฉบับ; 11 timeline (#7, 9, 13, 23, 32, 46, 48, 49, 60, 63, 77) ใช้ข้อความ Typhoon ที่ agent ตรวจคำแล้ว (`scripts/scratch/empty-caption-audio/typhoon-corrected.json`) แทนซับร่าง; 16 timeline แก้ชื่อเป็น "เชอรี่" (`scripts/scratch/name-fix-cherry.json`); ไม่มีซับ 4 timeline: #33 ไม่มีเสียงพูด, #36 เสียงพากย์เกม, #56 เพลงมีเนื้อร้อง, #76 เสียงพากย์เกม/ฟังไม่ออก. #74 c6 "คอชนิดบ่อย" คงไว้เพราะไม่แน่ว่าเป็นชื่อ. SRT แยกใน G: ทั้ง `16x9`/`9x16` อัปเดต 62 ไฟล์ (สำรองเดิมที่ `scripts/scratch/sidecar-backup-20261028`); สำรอง `backups/2026-10-28-sakuyako-after-typhoon-namefix.drp`. ข้อความ Typhoon ตรวจโดย agent จาก ASR สองตัว ไม่ได้ฟังเสียงจริง
- 2026-10-28 ลบ `_archived_v01` 20 timeline ตามคำสั่งผู้ใช้ (V/A ตรงกับ timeline หลักทุกตัว ต่างแค่ไม่มีซับ) ด้วย `scripts/delete_archived_timelines.py`; เหลือ 85 timeline หลัก; สำรองก่อนลบใน `backups/2026-06-Sakuyako-before-delete-archives-*.drp`
- ก่อน batch ต้องสร้างและตรวจ `.drp` หลัง pilot ใหม่: ไฟล์ที่มีอยู่ `backups/2026-10-26-sakuyako-2026-06-pre-pilot.drp` เก่ากว่า pilot และใช้เป็น rollback ของสถานะปัจจุบันไม่ได้; Studio MCP 21.1.1 read-only ยังตอบ แต่ `SetCurrentTimeline`/`SaveProject`/`ExportProject` ไม่ยืนยันการทำงานและไม่เกิดไฟล์สำรอง ต้อง restart Resolve และเปิดโปรเจกต์ใหม่ก่อนทำ batch

## ยังไม่ทราบ (ถามผู้ใช้ก่อนเดา)
- Sakuyako และ Cheris เป็นคนเดียวกัน คนละช่อง หรือคอลแล็บ
- ถ้ามี Cheris แยก: โปรเจคและฟุตเทจของ Cheris อยู่ที่ไหน (พบแค่ `contact-cheris.gsheet` และคำว่า cheris ใน 3 script)
- งานค้างหลังส่งออกวันที่ 2026-10-13

- VTuber Zoom (2026-10-29, timeline `ช็อตฮา  โอ้ย-vdo`): chibi sits bottom-left in a pillarboxed 1280x720 Roblox capture. Verified window is `top 0.55 / bottom 0.955 / cx 0.255` (Size 2.469). Anything larger (e.g. Size 4.2) crops the chibi and shows the black pillarbox. Details in `adjustment-focus.md`.

- 9:16 ของ 2026-06 (2026-10-29, ผู้ใช้อนุมัติ layout): ทำครบ 85 `_9x16` ด้วย `scripts/scratch/sk06_9x16.py` + `v916_batch.sh`: เกม 16:9 เต็มเฟรมด้านบน (แถว 60..667), chibi สูง ~740 px กึ่งกลาง (540,1060) ให้ซับกลางล่างอยู่ใต้ตัว, แถบดำล่างสุดยอมรับได้. render 1080x1920 มีเสียง+burn-in ซับ อยู่ที่ `vdo/9x16/<name>_9x16.mp4` (pilot เก่าเปลี่ยนชื่อเป็น `..._9x16_pilot-old.mp4`). ไฟล์ `จังหวะเกม  มาดีดๆ-vdo_9x16.srt` บน Drive เร็วกว่าซับ native 100 เฟรม (ยังไม่ได้แก้ไฟล์บน Drive).

- Layout A (อนุมัติ 2026-10-29; ดูบรรทัดถัดไปสำหรับชุดเต็ม; pilot timeline `ช็อตฮา  มันก็ได้แบบใส่ข-vdo_9x16_layoutA`, builder `scripts/scratch/sk06_9x16_layoutA.py`): ใน source 1280x720 ส่วนเกมจริงอยู่แถว 64..655 เท่านั้น (บน/ล่างเป็นแถบดำ + PRISM Live) minimap อยู่ราว x 42..230 / y 64..252 และ chibi อยู่ราว x 124..279 / y 395..603. V1 ครอปจัตุรัสกลาง x 344..936 ขยาย 1.824 เต็มแถว 0..1080 (ตัด chibi ในเกมและรายชื่อทีมออกเอง); ผู้ใช้ขอให้แบ่งเป็น 2 ส่วนคือเกมกับตัวละคร (ไม่เอาการ์ด minimap): `scripts/scratch/sk06_layoutA_twopart.py` ลบ V4 แล้วตั้ง V3 ให้เต็มแถว 1080..1920 (window source x 1.6..401.6 / y 345..656, k 2.7) chibi กึ่งกลางสูง ~560 px แถว ~1215..1777 ไม่มีแถบดำ; ขอบซ้ายยังเห็นรายชื่อทีม และมุมขวาล่างเห็น HUD ฮีโร่. ซับ (~1500-1580) จะทับลำตัว chibi ถ้า timeline มีซับ. ภาพเกมนุ่มกว่า `_9x16` เดิมเพราะต้องขยาย 1.8x.

- Layout A ชุดเต็ม (2026-10-29): สร้าง `<name>_9x16_layoutA` ครบ 38 timeline ที่มีอยู่ในโปรเจกต์ (builder `scripts/scratch/sk06_9x16_layoutA.py` + `v916A_batch.sh`, geometry ต่อ timeline จาก `sk06_bands.py`). source มี 2 แบบ: แถวเกม 64..656 เต็มกว้าง (ขยายเกม 1.824) หรือเต็มสูงมีขอบดำซ้ายขวา 64 px (ขยาย 1.5); chibi สูง ~562 px กึ่งกลางแถว 1496 เต็มช่อง 1080..1920 และเลื่อนซ้ายแทนการโชว์ขอบดำ. QC (`sk06_layoutA_qc.py`): raster/tracks/V1-V3/audio/subtitle count/range ตรง original ครบ 38, ภาพนิ่ง 3 เฟรมทุกตัว. ภาพนิ่งไม่แสดงซับ จึงยังไม่ได้ยืนยันว่าซับทับ chibi แค่ไหน (34 timeline มีซับ). ระหว่าง batch, AppendToTimeline คืน False ครั้งเดียวและ Resolve หลุดครั้งเดียว: timeline ที่ค้างว่างเปล่า ลบแล้วรันซ้ำผ่าน.
- Layout A render (2026-10-30): render ครบ 38 ไฟล์ 1080x1920 มีเสียง+burn-in ซับ (`scripts/scratch/render_all.py _9x16_layoutA` -> `scripts/scratch/oyvdo/render_9x16_layoutA/NN.mp4`), ffprobe: จำนวนเฟรมตรงความยาว timeline และมีเสียงทุกไฟล์. ภาพจากไฟล์ render ยืนยันว่าซับ (แถว ~1500-1580) ทับมือ/ลำตัว chibi ใน layout 2 ส่วน; ยังไม่คัดลอกขึ้น Drive.
