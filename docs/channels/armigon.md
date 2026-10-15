# Armigon

## ตัวตนและคอนเทนต์
- VTuber ไทย ตัวละครชื่อ Armigon เนื้อหาเกมและ free talk (ในโฟลเดอร์มี "เกมโปรด 2026", "แนะนำตัว", "ทำไมถึงชื่อ Armigon")

## ที่เก็บไฟล์
- ฟุตเทจ: `C:/Users/warit/SynologyDrive/armigon/` มี `2026-09-20`, `_firstpass`
- Google Drive: `Projects/Armigon/`

## โปรเจคและ timeline ใน Resolve
- `armigon-2026-09`: 48 timeline แนวนอน (vdo) พร้อม baseline ใน `armigon_9x16_snapshot.py`
- pilot แนวตั้งสร้างบน timeline duplicate เท่านั้น

## รูปแบบและ layout
- ต้นทาง 16:9; 9:16 ต้อง pilot ทีละ 1 timeline แล้วให้ผู้ใช้อนุมัติก่อนทำต่อ ห้ามสร้างทั้งชุดเอง
- เป้าโฟกัสอาจเป็นตัวละครในเกม (chibi) ไม่ใช่แค่อวาตาร์ — ยึด subject ที่ผู้ใช้ระบุหรือชี้ในภาพ (กฎใน `house-style`)

## ซับ เสียง และ enrichment
- ซับสั้นตามกฎกลาง; แผนแก้ซับแบบ offline: `armigon_fix_captions.py` (ไม่แตะ Resolve)
- QC เสียง: `armigon_audio_qc.py` (loudness + เฟรม hook ของ V1)
- QC Zoom Focus: ยืนยันว่าตัวละครในทุกช่วงเป็น Armigon ก่อนซูม ตรวจภาพเต็มเฟรม/ขอบดำ/blur เทียบเฟรมเดิมเมื่อเปิด-ปิด Adjustment Clip (รายละเอียดใน `AGENTS.md` และ `adjustment-focus.md`)

## Script และ skill ที่เกี่ยวข้อง
- `armigon_9x16_pilot.py`, `armigon_9x16_batch_one.py`, `armigon_9x16_focus_retarget.py`, `armigon_9x16_reframe_target.py`, `armigon_focus_pilot.py`
- QC แบบอ่านอย่างเดียว: `armigon_publish_qc.py`, `armigon_source_ranges.py`, `armigon_audio_qc.py`
- skill: `resolve-video-enrichment` (`references/adjustment-focus.md`), `house-style`

## กับดักและงานค้าง
- แทรก Adjustment Clip อาจเลื่อน track อื่น ทำผ่าน DRT (`drt_focus_track.py`) หรือ pilot ที่ล็อก track เดิม
- ผลที่ตรวจแล้วและขอบเขตหลักฐานอยู่ใน `adjustment-focus.md` ภาพ still ไม่พิสูจน์ว่าไม่มีอาการสั่นของภาพเคลื่อนไหว

## ยังไม่ทราบ (ถามผู้ใช้ก่อนเดา)
- จำนวนคลิปที่ทำ 9:16 เสร็จและอนุมัติแล้ว
- preset ซับ/ฟอนต์ที่ผู้ใช้ยืนยันเฉพาะช่องนี้
