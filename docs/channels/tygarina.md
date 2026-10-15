# Tygarina

## ตัวตนและคอนเทนต์
- VTuber ไทย เนื้อหาเกมหลากหลายและ free talk: R.E.P.O, Climbing, IB, DnD, Gartic Phone, LoL, Overcooked, Fallout 4 ฯลฯ (ดูชื่อ timeline ใน `backups/`)

## ที่เก็บไฟล์
- ฟุตเทจ: `C:/Users/warit/SynologyDrive/Tygarina/2026-09-30/` (32 ไฟล์ 69.5 GiB, 60 fps, เสียงสเตอริโอ Opus 48 kHz) ห้ามแก้ต้นฉบับ
- มีโฟลเดอร์ `2026-08`, `2026-08-01`, `DEBUT & HBD TYGARINA`

## โปรเจคและ timeline ใน Resolve
- โปรเจค `tygarina_2026-09-30`: 28 timeline (7 เดิม + 21 ไฮไลต์ที่สร้างใหม่) ชื่อรูปแบบ `tygarina_2026-09-30_<เกม>`
- สรุปไฮไลต์และเหตุผลต่อคลิป: `work/PROJECT.md`

## รูปแบบและ layout
- ต้นทาง 16:9 60 fps; ไฮไลต์ยาว 30–180 วินาที
- Zoom Focus ถูกย้ายเข้า timeline Climbing ผ่าน DRT (`deploy_climbing_focus.py`)

## ซับ เสียง และ enrichment
- ซับและ preset ตามกฎกลาง (ยังไม่มีการยืนยันเฉพาะช่อง)
- มีการสำรอง `.drp` ก่อน export ทุก timeline (`backups/2026-10-10-before-final-export-tygarina_*.drp`)

## Script และ skill ที่เกี่ยวข้อง
- `deploy_climbing_focus.py`, `drt_focus_track.py`, `focus_apply_batch.py`, `backup_drp.py`
- skill: `video-footage-review`, `resolve-rough-cut`, `resolve-video-enrichment`

## กับดักและงานค้าง
- ตัดจากไฟล์ยาวหลายชั่วโมง ใช้เฟรมที่ 60 fps (วินาที × 60) และตรวจ duration จริงหลังสร้าง
- สถานะการอัปโหลดและเวอร์ชันแนวตั้งยังไม่บันทึกในโปรไฟล์

## ยังไม่ทราบ (ถามผู้ใช้ก่อนเดา)
- คลิปไหนส่งมอบ/อัปโหลดแล้ว และมีแนวตั้งหรือไม่
- ตัวละครที่ต้องโฟกัสและกรอบซูมที่ผู้ใช้อนุมัติ
