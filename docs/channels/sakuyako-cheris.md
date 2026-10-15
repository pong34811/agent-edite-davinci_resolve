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

## ยังไม่ทราบ (ถามผู้ใช้ก่อนเดา)
- Sakuyako และ Cheris เป็นคนเดียวกัน คนละช่อง หรือคอลแล็บ
- ถ้ามี Cheris แยก: โปรเจคและฟุตเทจของ Cheris อยู่ที่ไหน (พบแค่ `contact-cheris.gsheet` และคำว่า cheris ใน 3 script)
- งานค้างหลังส่งออกวันที่ 2026-10-13
