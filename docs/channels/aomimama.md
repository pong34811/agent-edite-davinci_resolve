# Aomi-mama

## ตัวตนและคอนเทนต์
- VTuber ไทย เดบิวต์ 31/07/2026 คอนเทนต์ผสม: เกม, free talk, เรื่องเล่า ตัดเป็นไฮไลต์แนวนอนและแนวตั้ง

## ที่เก็บไฟล์
- ฟุตเทจ: `C:/Users/warit/SynologyDrive/Aommi-mama/` (สะกดสองตัว m: `Aommi-mama`) มี `2026-09-aomimama`, `อัปโหลดเเล้ว`
- Google Drive: `Projects/Aomi-mama/` (โฟลเดอร์ส่งออก `vdo`)

## โปรเจคและ timeline ใน Resolve
- `aomimama-2026-09-p1` และ `aomimama-2026-09-p2` (p2 = 88 timeline: 44 แนวนอน + 44 `_9x16`)
- โปรเจคเดบิวต์: `【DEBUT STREAM】AOMI-MAMA｜ 31⧸07⧸2026 เวลา 20.00` (16 timeline: 8 แนวนอน + 8 แนวตั้ง) ดู `work/PLAN.md`
- หลัง restart Resolve จะเปิดที่ "Untitled Project": เปิดโฟลเดอร์ `Aommi-mama` → `2026-09` แล้วโหลดโปรเจค

## รูปแบบและ layout
- 16:9 1920x1080 และ 9:16 1080x1920 ที่ 60 fps ตั้งชื่อแนวตั้ง `<ชื่อเดิม>_9x16` ห้ามสร้างซ้ำก่อนตรวจรายการ
- แนวตั้ง: GIF V2 ต้องอยู่ใน game panel เหนือรอยต่ออวาตาร์ (V3 วาดทับ V2) ใช้ `p2_9x16_gif_relayout.py`

## ซับ เสียง และ enrichment
- preset ซับ: แนวตั้ง `Mitr-short-001`, แนวนอน `Mitr Font` (ผู้ใช้ยืนยันแล้ว); ฟอนต์ Mitr Bold ในแผนเดบิวต์
- ซับ p2 ทั้ง 88 timeline ถูกเขียนใหม่ตามกฎสั้นเมื่อ 2026-10-10
- GIF ใช้ video preset `vdo` (แนวนอน) / `short` (แนวตั้ง) ผ่าน `apply_vdo_preset.py`
- เสียง: loudnorm สองรอบ I=-14, TP=-1.5, LRA=11 (`p2_loudnorm_worker.py`)
- ส่งออกด้วย preset `H.264 Master` ไปโฟลเดอร์ `vdo` ใน Drive ผ่าน `p2_export_final.py` (dry-run ถ้าไม่ใส่ `--apply`)

## Script และ skill ที่เกี่ยวข้อง
- แปลง 9:16: `p2_9x16_convert.py`, `p2_9x16_build.py`, `p2_9x16_layout.py`, `p2_9x16_verify.py`
- ซับ: `p2_fix_captions.py`, `p2_apply_fixed_captions.py`, `p2_verify_captions_after.py`
- enrichment: `p2_apply_cues.py`, `p2_verify_all.py`; focus: `focus_apply_p2.py`, `plan_p2_focus.py`
- QC/ส่งออก: `p2_publish_qc.py`, `p2_render_vertical.py`, `p2_export_final.py`, `p2_trim_tail_150s.py`
- ดูตารางเต็มใน `scripts/INDEX.md` (ป้าย `p2`)

## กับดักและงานค้าง
- timeline #27 และ #33 ทำให้ Resolve ค้างเมื่อสคริปต์เปลี่ยน raster บนสำเนา ต้องตั้ง raster ผ่าน MCP `timeline set_setting` บน timeline ปัจจุบัน (ทำสำเร็จแล้ว ครบ 44 ตัว)
- timeline ที่ไม่ active อ่านค่า transform ได้เพี้ยนตาม 1920/1080; ffmpeg seek เฟรมเดียวในไฟล์ยาวอาจผิด
- หลัง restart ต้องตั้ง Preferences › General › External scripting = Local
- งานค้างจากการ QC 2026-10-10: ดู memory `p2-publish-qc-and-captions` (ข้อมูลอาจเก่า ตรวจสถานะสดก่อน)

## ยังไม่ทราบ (ถามผู้ใช้ก่อนเดา)
- งานล่าสุดหลัง 2026-10-13 และคลิปไหนส่งมอบหรืออัปโหลดแล้ว
