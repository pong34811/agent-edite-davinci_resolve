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
- day 25 9:16 (2026-10-15): `Timeline 1_9x16` สร้างด้วยสำเนา `scripts/scratch/d25/build_9x16_day25.py` (geometry day 24 ใช้ซ้ำได้, GIF src end ต้อง +1); stills 8 เฟรมผ่าน; ซับ overlap/เสียงยังไม่ตรวจ; backup `.hermes/katy404-d25/pre_9x16.drp`
- day 25 enrichment (2026-10-15): `Timeline 1 [ENHANCED]` = A2 SFX x6, A3 BGM `Melody Island` (-39.3 dB), V3 GIF x4 (vdo preset, นอกช่วง zoom); รอผู้ใช้รีวิวก่อน promote; ยังไม่ได้ฟังเสียง/ตรวจ licence; แผน/สคริปต์ที่ `.hermes/katy404-d25/`, `scripts/scratch/d25/`
- day 25 (2026-10-15): Timeline เดียว, 2560x1440 บน 1920x1080@60, อวาตาร์มุมขวาล่างเหมือน day 24 ใช้ window top 0.515 / bottom 0.962 / cx 0.775 (ahoge ที่ ~0.547) ได้ 8 ช่วงบน `Timeline 1_focus_variant` (ต้นฉบับไม่แตะ); สคริปต์ชั่วคราวอยู่ `scripts/scratch/d25/`, แผน/ภาพ QC อยู่ `.hermes/katy404-d25/`
- Bunny Girl คืออะไร (2026-10-17): ผู้ใช้เลือก template Pop Kinetic (คำกระแทกล่างซ้าย, การ์ด/รายการคอลัมน์ขวา, wipe ชมพูเปลี่ยนบท) overlay ProRes 4444 9 ไฟล์อยู่ `Graphics/v3_pop/` ตัวสร้าง `scripts/scratch/bunny_pop/build_pop_overlays.py`, โปรเจค HyperFrames `.hermes/projects/bunny-girl-pop-kinetic/`; ประกอบแล้วบน `Timeline 1_pop` (V2 `VTuber Zoom` 8 Adjustment Clip 1.35x window top 0 / bottom 0.74 / cx 0.57, V3 `REACTIONS` ch01–ch09) ต้นฉบับ `Timeline 1` ไม่แตะ; backup `.hermes/projects/bunny-girl-pop-kinetic/assemble/pre_pop.drp`; render ทดสอบ `Bunny Girl คืออะไร_POP_test_2026-10-17.mp4` ผ่าน ffprobe+ภาพ 21 เฟรม, เพิ่ม A2 `SFX` 24 จุด (whoosh `TRANSITIONSWOOSH.mp3` -10 dB ที่ wipe 6 จุด, `Pop Sound Effect.mp3` ตัด 0.5 วิ -9 dB ที่คำกระแทก 17 จุด + VS) จาก `G:/My Drive/Projects/2.1_sfx/`; render `..._POP_SFX_test_2026-10-17.mp4` -14.4 LUFS ไม่ clip, SFX ต่ำกว่าเสียงพูด ~15-20 dB (ผู้ใช้ฟังแล้วยืนยันว่าระดับนี้พอดี 2026-10-17: whoosh -10 dB / pop -9 dB ใช้เป็นค่าเริ่มต้นของช่องได้); backup `pre_sfx.drp`; BGM (ผู้ใช้เลือก 2026-10-17): `bgm_chill_lounge_mocktale.wav` บน A3 `BGM` -19 dB (ใต้เสียงพูด ~17.5 dB) วน 2 ท่อน ต่อที่ช่วงเงียบ 98.88 วิ (ท่อนนี้ซ้ำทุก 4702 เฟรม, ไม่มีเสียงคลิก) fade in 12 / fade out 120 เฟรม; render `..._POP_BGM_test_2026-10-17.mp4` -14.4 LUFS, peak 0.9993 ที่ 26.22 วิ (whoosh+เสียงพูด, ไม่ clip); backup `pre_bgm.drp`; ยังไม่มีซับ; ผู้ใช้ปรับช่วงซูมเองเป็น 10 ช่วง แล้วยืดหัว clip 85.07 วิ ทำให้ render ไม่ผ่าน → สร้าง `Timeline 1_pop_v2` (V2 สร้างใหม่ 10 clip ตามช่วงของผู้ใช้, track อื่น/gain/fade เหมือนเดิม) render ผ่าน `..._POP_v2_test_2026-10-17.mp4`; `Timeline 1_pop` เดิมยังอยู่ (ช่วงหัว 85.07–86.77 วิ render ไม่ได้); backup `pre_zoomfix.drp`; สคริปต์ `scripts/scratch/bunny_pop/assemble.py` (ขั้น rezoom ยกเป็น `scripts/drt_rebuild_focus_track.py` แล้ว)
- Bunny Girl คืออะไร ส่งมอบ (2026-10-17): `Timeline 1` = งานจบ (สร้างจาก `Timeline 1_pop_v2` ที่ผู้ใช้แก้ซูมเองเป็น 13 ช่วง รวม close-up ท้ายด้วย Inspector zoom 2.03 ที่ 138.72 วิ และตัด ch09 จบที่ 138.72 วิ; Fusion zoom 12 clip สร้างใหม่) ไฟล์ `Bunny Girl คืออะไร_FINAL_2026-10-17.mp4` 1080p60 H.264 -14.4 LUFS ไม่มีเฟรมดำ; timeline เก่า: `Timeline 1_original` (ฟุตเทจล้วน), `Timeline 1_pop`, `Timeline 1_pop_v2` (มี clip ซูมที่ render ไม่ได้ อย่าใช้); backup `pre_final.drp`
- script day22/day24 ผูกกับ ID/ชื่อของโปรเจคนั้น ก่อนใช้กับ day อื่นต้องแก้ค่าคงที่และ pilot 1 timeline ก่อน
- ยังไม่มีรายการ day อื่นที่ตัดแล้วในโปรไฟล์นี้

## ยังไม่ทราบ (ถามผู้ใช้ก่อนเดา)
- ซีรีส์ถึง day ไหนแล้ว และ day ไหนส่งมอบแล้ว
- มีกฎซับ/สีตัวอักษร/BGM เฉพาะช่องหรือไม่
- เป้าซูมคืออวาตาร์เสมอหรือมีตัวละครในเกมด้วย
