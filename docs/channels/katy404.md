# Katy404 (KT404)

## ตัวตนและคอนเทนต์
- VTuber ไทย ช่อง YouTube `@KATY_404` คอนเทนต์หลักตอนนี้คือซีรีส์ Minecraft "ปลูกข้าวจนกว่าจะ 10K ผู้ติดตาม" แยกเป็นวัน (day 13–17 มีโฟลเดอร์ใน SynologyDrive, day 22 และ day 24 มีโปรเจค Resolve)
- ตัวละครคือเนื้อหา: ปฏิกิริยาและเสียงสำคัญกว่าฝีมือเล่นเกม

## ที่เก็บไฟล์
- ฟุตเทจ: `C:/Users/warit/SynologyDrive/วันที่ NN ปลูกข้าวจนกว่าจะ 10K ผู้ติดตาม - Katy404/` และ `SynologyDrive/KT404/{pic,video}`
- Google Drive: `Projects/Katy404/`

## โปรเจคและ timeline ใน Resolve
- โปรเจค "day 22" และ "day 24" (ชื่อเต็มให้อ่านจาก Resolve) ต้นทาง 1920x1080 @ 60 fps
- ผล QC จริงของ day 24 (1 timeline, Resolve Studio 21.1.0.17) อยู่ใน `.agents/skills/resolve-video-enrichment/references/` (ดูส่วน v0.12.0 ใน `CHANGELOG.md`)

## รูปแบบและ layout
- 16:9 ต้นทางมีอวาตาร์ฝังอยู่มุมขวาล่างของภาพเกม
- 9:16 สร้างด้วย `build_9x16_day22.py` / `build_9x16_day24.py`; ภาพตัวอย่าง layout ปฏิกิริยาแนวตั้ง: `.agents/skills/resolve-video-enrichment/assets/katy404-vertical-reaction-layout.png`
- โครงสร้าง track ตาม `AGENTS.md` (16:9: V1 base, V2 VTuber Zoom, V3 REACTIONS; 9:16: Game Top / REACTIONS / VTuber Bottom / VTuber Zoom)

## ซับ เสียง และ enrichment
- ซับตามกฎกลาง (≤14 ตัวอักษร ≤1.5 วิ ไม่เว้นวรรคระหว่างคำไทย) preset: แนวตั้ง `Mitr-short-001` แนวนอน `Mitr Font` (กฎของโปรเจคโดยรวม ยังไม่มีการยืนยันเฉพาะช่องนี้)
- enrichment (BGM/SFX/GIF) ที่ตรวจแล้วบน day 24: focus zoom 7 ช่วง, GIF, 9:16 ดูผลใน CHANGELOG v0.12.0; ข้อจำกัด: ยังไม่ได้ฟังเสียงเต็มช่วง

## Script และ skill ที่เกี่ยวข้อง
- `build_9x16_day22.py`, `build_9x16_day24.py`, `apply_vtuber_zoom.py`, `apply_enrichment_d22.py`, `zoom_variant_stills.py`
- skill: `resolve-video-enrichment` (มี `katy404-channel-study.md`), `vtuber-content-curriculum`, `vtuber-thumbnail-layout`

## กับดักและงานค้าง
- script day22/day24 ผูกกับ ID/ชื่อของโปรเจคนั้น ก่อนใช้กับ day อื่นต้องแก้ค่าคงที่และ pilot 1 timeline ก่อน
- ยังไม่มีรายการ day อื่นที่ตัดแล้วในโปรไฟล์นี้

## ยังไม่ทราบ (ถามผู้ใช้ก่อนเดา)
- ซีรีส์ถึง day ไหนแล้ว และ day ไหนส่งมอบแล้ว
- มีกฎซับ/สีตัวอักษร/BGM เฉพาะช่องหรือไม่
- เป้าซูมคืออวาตาร์เสมอหรือมีตัวละครในเกมด้วย
