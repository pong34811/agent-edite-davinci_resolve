# Laffy

## ตัวตนและคอนเทนต์
- VTuber ผมขาว สวมโค้ทดำทับเสื้อคอเต่าดำ ห้อยจี้สีฟ้า ฉากหลังเป็นห้องโทนอุ่น อวตาร์อยู่กลางเฟรม (หัวอยู่ราว y 0.10, หน้าอยู่ราว x 0.48 ของเฟรม 16:9)
- แทนตัวเองว่า "ครับ" ชื่อในซับไทยให้เขียน **ลาฟฟี่** (ผู้ใช้ยืนยัน 2026-11-13; Descript ถอดเป็น "ราฟฟี่" ต้องแก้ทุกครั้ง)
- คอนเทนต์: แนะนำการ์ด Yu-Gi-Oh! (Master Duel) และหัวข้อแนะนำตัว เช่น เกมที่เล่น, เหตุผลที่เป็น VTuber, รู้จัก Yu-Gi-Oh ได้ยังไง

## ที่เก็บไฟล์
- งานตัดต่อ: `G:\My Drive\laffy_projects\<เลขงาน>\` เช่น `004` แนะนำการ์ด Underworld Goddess
  - ในโฟลเดอร์มี `Timeline 1.mov` (1080p30 ที่ export มาแล้ว), ไฟล์ OBS ดิบ 720p และโฟลเดอร์รูปการ์ดแยกตามการ์ด
  - ไฟล์ที่ agent สร้าง (backup, ซับ, overlay, zoom DRT, QC) อยู่ใน `<งาน>\edit\`
- ฟุตเทจเก่า: `C:/Users/warit/SynologyDrive/laffy/` (มีแต่โฟลเดอร์หัวข้อ)

## โปรเจคและ timeline ใน Resolve
- Library `laffy_project` มีโปรเจกต์ `ตัวการ์ด Underworld Goddess-Yu-Gi-Oh! Master Duel` ที่ 1920x1080, 30 fps
  - หลังผู้ใช้อนุมัติ (2026-11-13) เหลือ timeline เดียวคือ `Timeline 1` (id b138d521... หลังย้ายฟุตเทจกลับ V1/A1 2026-11-13) ที่เป็นงานตัดเสร็จ ซับ `Mitr Font`
  - timeline สำรอง/archive ทั้งหมดและโฟลเดอร์ `Archive` ลบแล้ว ถ้าต้องย้อนกลับใช้ `edit/backup/laffy004_pre_cleanup_*.drp`

## งานแนะนำตัว 3 นาที (2026-11-15)
- โฟลเดอร์ `G:\My Drive\laffy_projects\เเนะนำตัว 3 นาที\` ต้นฉบับ `Timeline 1.mov` 146.9 วิ 4407 เฟรม 1920x1080@30 (เสียง -14.4 LUFS peak -1.2 dBFS)
- Resolve project `เเนะนำตัว laffy` (id f4bfbbe1...) : `Timeline 1` (d621d940...) ไม่แตะ, งานตัดคือ `เเนะนำตัว 3 นาที_edit` (2726b753...)
  - ผู้ใช้เลือก **ไม่ตัดอะไรเลย** แม้ช่วงพูดเนื้อหาช่องซ้ำ 4 เทค ("อันนี้ขอใหม่นะ" ~99 วิ) → ทำเป็นมุก การ์ด `เทค 2/3/4`
  - V2 `VTuber Zoom` 8 ช่วง Fusion 1.32x (window 0.04/0.80/0.485), V3 `REACTIONS` การ์ดคีย์เวิร์ด 21 ใบ (ซ้าย cx 280 / ขวา cx 1640, y 400), A2 `SFX` pop -13 dB x21 + Record Scratch -15 dB ที่ 2963, A3 `BGM` `bgm_lofi_chill_loop_04.wav` -22 dB 2 ท่อนต่อกันที่ 2304 fade in 15 / out 90, Subtitle 1 `Mitr Font` 165 cue (Descript)
  - render `render\laffy_intro_edit_v2.mov` (H.264 + AAC, -14.4 LUFS, peak -0.5 dBFS, 4407 เฟรม ไม่มีเฟรมดำ) ; v1 peak 0.0 dBFS (pop -9) ใช้ไม่ได้
  - ไฟล์งาน `edit2\` (backup `.drp`, DRT, cards/png + mov) สคริปต์ `scripts/scratch/laffy_intro/`
  - ยังไม่ยืนยัน: ชื่อเต็มละติน `RaffyNiveren` (cue 222-244), คำอุทาน "ย่า" ใน cue แรก, ยังไม่ได้ฟังทั้งคลิป; รอผู้ใช้รีวิว

## รูปแบบและ layout (16:9)
| แทร็ก | ใช้สำหรับ |
|---|---|
| V1 | `Timeline 1.mov` ทั้งไฟล์ ไม่ตัด (ผู้ใช้ลบซูมและ SFX ออกเอง 2026-11-13; V2 `VTuber Zoom` และ A2 `SFX` ว่างไว้ตามโครงบ้าน) |
| V2 | `VTuber Zoom` เป็น Fusion Transform 1.32x (window บน 0.04 ล่าง 0.80, cx 0.485) |
| V3 | `REACTIONS` รูปการ์ด |
| A2 | `SFX` |
| A3 | `BGM` |
| ST1 | `Thai` |

- รูปการ์ดใบเดียว: สูง 820 px อยู่ด้านขวา (cx 1600) หรือซ้าย (cx 320) ของอวตาร์ เว้นช่องจากซับ Mitr Font อย่างน้อย 65 px (ขนาด 860 ที่ cx 1560 เกือบชนซับ)
- การ์ดหลายใบ (เช่น Kaiju 6 ใบ): สูง 520 px แบ่งเป็นพัดซ้าย 3 ใบ ขวา 3 ใบ ไม่บังหน้า
- ใบแรกที่พูดถึงการ์ดใช้แบบ overframe ส่วนตอนอธิบายเอฟเฟกต์ใช้การ์ดแบบธรรมดา

## รูปแบบ 9:16
- `Timeline 1_9x16` (1080x1920) สร้าง 2026-11-14 จาก `Timeline 1` เฉพาะการจัดเฟรม ไม่ตัด ซับและเสียงเหมือนต้นฉบับ ตอนสร้างไม่ได้ตรวจว่ามีอยู่ใน Resolve จริงหรือไม่ ต้องตรวจก่อนใช้
- V1 Zoom 3.1605 (เต็มความสูง) หัวครบ ไม่มีขอบดำ
- การ์ด V3 วางกลางช่วงอก (y ~1180) แทน preset `short`: แผงขวา Zoom 1.234 Pan -446 Tilt -261, แผงซ้าย Pan +446, Kaiju Zoom 0.982 Pan 0 Tilt -277 **ผู้ใช้ยังไม่อนุมัติให้ใช้แทน `short`** ให้ถามก่อนใช้ซ้ำ (skill `talking-avatar-vertical-copy`)
- render ตรวจภาพ (ไม่มีเสียง) ซับ Mitr Font อยู่ y ~0.85–0.95 ไม่ล้นขอบ การ์ดไม่บังหน้า

## ซับ เสียง และ enrichment
- ซับ: ใช้ Descript (`language: auto`) แล้วแบ่ง cue ด้วยมือ ตามกฎ house-style ไม่เกิน 14 ตัวอักษร ไม่เกิน 1.5 วิ
  - ใช้ชื่อการ์ดภาษาอังกฤษ (Underworld Goddess, I:P Masquerena, Kaiju) และเขียนตัวเลขเป็นตัวเลข
- เสียงพูดดัง (-14.2 LUFS, peak -1.1 dBFS) BGM -22 dB, SFX -3 ถึง -6 dB, เสียง boom ยาวต้อง -24 dB (ที่ -12 render peak -0.01 dBFS)
- ไฟล์ส่งงาน: `004/render/laffy004_Underworld_Goddess_v5.mp4` (2026-11-13, ซับปรับเวลาตามเสียงแล้ว; H.264 1920x1080 30 fps, ซับ burn-in, -14.2 LUFS, peak -0.7 dBFS) ส่วน v4 คือเวอร์ชันซับเวลาเก่า
- สไตล์ซับ: `Mitr Font` (ผู้ใช้อนุมัติ 2026-11-13) clone จาก DRT ของ Katy404 Bunny Girl ep6 แนวนอน (`.hermes/projects/bunny-girl-ep6/substyle/styled_subs.drt`) ด้วย `drt_clone_subtitle_style.py`; ตัวหนาสีขาวขอบดำ อ่านชัดบนเสื้อดำ

## Script และ skill ที่เกี่ยวข้อง
- `scripts/card_pop_overlay.py` (รูปการ์ดเด้ง), สคริปต์ขั้นตอนของงาน 004 อยู่ในโฟลเดอร์ scratch ชื่อ laffy004 (gitignored: backup, build_subs, subs_insert, zoom, audio, levels, verify)
- skill: `resolve-video-enrichment` (illustration-assets), `thai-subtitles-resolve`, `vtuber-content-curriculum`

## กับดักและงานค้าง
- เวลาซับต้องตรงกับช่วงที่พูดจริง: การแบ่งเวลาตามจำนวนตัวอักษรทำให้ cue ขึ้นก่อนเสียงช่วงที่มีจังหวะหยุด (ผู้ใช้แจ้ง `มาเป็น` 2026-11-13) ใช้ speech map + ตรวจเฟรมในช่วงเงียบ
- สไตล์ default ไม่มีขอบตัวหนังสือ บนเสื้อดำจี้สีฟ้าจะโผล่ผ่านตัวอักษร ให้ใช้ `Mitr Font`

## ยังไม่ทราบ (ถามผู้ใช้ก่อนเดา)
- ยังไม่มี
