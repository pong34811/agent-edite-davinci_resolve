---
name: katy404-minecraft-editing
description: ใช้เมื่อตัดต่อคลิปเกม Minecraft ช่อง KATY404 (ซีรีส์ "ปลูกข้าวจนกว่าจะ 10K ผู้ติดตาม") ทั้ง 16:9 Clean Master และ 9:16 Shorts/TikTok ใน DaVinci Resolve — ครอบคลุมการจัดโครงสร้างแทร็ก, ค่า Geometry/Scale, Preset ซับไตเติล Mitr, การวาง Focus Zoom, กลยุทธ์การตัดต่อเพิ่มยอดวิว/Retention, และการแก้ Bug/Trap ทางเทคนิค (DRT XML In-offset, Live DRT Preset patch, Loudness -13.2 LUFS)
version: 0.3.0
author: Warit (pong34811), Hermes Agent
license: MIT
platforms: [windows]
metadata:
  hermes:
    tags: [Katy404, Minecraft, DaVinci-Resolve, Editing, VTuber, Shorts, Retention]
user-invocable: true
---

# Katy404 Minecraft Editing Workflow & Guidelines

คู่มือและขั้นตอนมาตรฐานสำหรับการตัดต่อคลิปซีรีส์ Minecraft **"ปลูกข้าวจนกว่าจะ 10K ผู้ติดตาม"** ของ VTuber ช่อง **Katy404** (`@KATY_404`) ทั้งเวอร์ชันแนวนอน 16:9 Clean Master และแนวตั้ง 9:16 Shorts/TikTok บน DaVinci Resolve Studio

---

## 1. ปรัชญาการตัดต่อและกลยุทธ์เพิ่มยอดคนดู (Retention Strategy)

1. **"ตัวละครคือเนื้อหาหลัก"**:
   - ปฏิกิริยา อารมณ์ น้ำเสียง และความโก๊ะ/ตกใจของ Katy404 สำคัญกว่าความเชี่ยวชาญในการเล่นเกม
   - ตัดต่อเพื่อขับเน้น "จังหวะปฏิกิริยา" (Reaction) มากกว่าการโชว์เกมเพลย์ยาวๆ

2. **ระบบ 2 ขา (Shorts + Mid-form)**:
   - **9:16 Shorts (30–60 วินาที)**: ทำหน้าที่เป็น "Hook ตัวดึงคนดูใหม่" สับจังหวะไว โฟกัสช็อตตกใจ มุกฮา หรือประเด็นที่คนดูสงสัย เพื่อดึงยอดวิวจาก Shorts Feed และเปลี่ยนคนดูจรเป็น Follower (ดันเป้าหมาย 10K)
   - **16:9 Clean Master (1–3 นาที)**: เล่าเรื่องกระชับแบบ Story-driven มีจุดเริ่มต้น ปัญหา และบทสรุปของแต่ละวัน เพื่อเก็บ Watch Time และสร้างแฟนคลับประจำ

3. **The Cold Open Hook (ตัดช่วงเงียบ/เมนูทิ้ง 100%)**:
   - ห้ามเปิดคลิปด้วยหน้าเมนูเกม การโหลดแมพ หรือการนับ 1–2–3
   - ตัดหัวคลิป 0–2.8 วินาที (168 เฟรมแรก) ออกทันที เพื่อเปิดคลิปด้วยประโยคพูดที่มีประเด็นหรือแอ็กชันทันที ลดอัตรา Drop-off ของคนดู

4. **Visual Simplicity (สไตล์เรียบง่ายแบบวันที่ 29 และ 30)**:
   - **ห้ามใส่ Title Card** บังต้นคลิป
   - **ห้ามใส่สติกเกอร์ Chibi** ป๊อปอัปหากผู้ใช้ไม่ได้สั่งชัดเจน
   - ให้เกมเพลย์และโมเดลตัวละครเป็นตัวเดินเรื่องหลัก เพื่อไม่ให้ภาพดูรกตา

---

## 2. โครงสร้างแทร็กเวอร์ชันแนวนอน 16:9 Clean Master (1920x1080 @ 60fps)

### Track Layout
- **Video 1 (Base Footage)**: ฟุตเทจหลักเกมเพลย์พร้อมอวาตาร์ฝังขวาล่าง ตัดหัว In=168 (Duration 5,846 เฟรม / 97.433 วิ)
- **Video 2 (VTuber Zoom)**: 6 Adjustment Clips วางเฉพาะช่วงสำคัญ (สเกล 1.35x, Center X: 0.325, Center Y: 0.675 ล็อกขวาล่าง ไร้ขอบดำ 100%, Headroom 5–8% เหนือจงอยผม)
  - ซูมช่วงที่พูดถึงยอดซับ, ม้าหาย/เจอม้า, และ Call to Action ท้ายคลิป
- **Subtitle 1**: 45 cues ซับไทย Native Subtitle Track โหลด Preset ฟอนต์ `Mitr Font` (สีขาว ขอบดำ ตำแหน่งกลางจอด้านล่าง ไม่บังอวาตาร์)
- **Audio 1 (Dialogue)**: เสียงพูดและเสียงเกมต้นฉบับ ตัดหัว In=168
- **Audio 2 (SFX)**: จุดไฮไลต์และจังหวะกระแทกคำ (Whoosh -10 dB, Pop -9 dB) รวม 15 จุด
- **Audio 3 (BGM)**: `Melody Island` (-19.0 dB, Fade In 12 เฟรม, Fade Out 120 เฟรม)

### สเปกเสียงส่งมอบ 16:9
- Integrated Loudness: **-13.2 LUFS** (มาตรฐาน -13 ถึง -14 LUFS)
- True Peak ไม่แตะ 0 dBFS

---

## 3. โครงสร้างแทร็กและเลย์เอาต์แนวตั้ง 9:16 (1080x1920 @ 60fps)

สร้างด้วยสคริปต์อัตโนมัติ `scripts/build_9x16_day30.py` บน Resolution 1080x1920:

```
+-----------------------------------+  y = 0
|                                   |
|      Video 1: Game Top (2.03x)    |
|      เน้นเกมเพลย์กึ่งกลางจอ       |
|                                   |
+-----------------------------------+  y = 960 (รอยต่อกึ่งกลางจอ)
|      Subtitle 1: Mitr-short-001   |  y ~ 1000 px (ระดับอก/รอยต่อ)
+-----------------------------------+
|                                   |
|      Video 3: VTuber Bottom       |
|      (3.56x, Headroom ~6-7%)      |
|      (และ Video 4: VTuber Full)   |
|                                   |
+-----------------------------------+  y = 1920
```

### รายละเอียดแทร็กแนวตั้ง
- **Video 1 (Game Top)**: สเกล 2.03x อยู่แถว 0..960 px โฟกัสเกมเพลย์ตรงกลางจอ ไร้ขอบดำ
- **Video 2 (REACTIONS)**: แทร็กว่างสำรองสำหรับ overlay พิเศษ
- **Video 3 (VTuber Bottom)**: สเกล 3.56x อยู่แถว 960..1920 px โฟกัสตัวละคร Katy404 เด่นชัด เว้น Headroom ~6-7% เหนือจงอยผม มือและไมค์ครบถ้วน
- **Video 4 (VTuber Full Zoom)**: สเกล 4.27x ซูมโคลสอัปเต็มจอสำหรับช่วง Focus Zoom 6 จุด:
  1. `[545..803]` (9.08s – 13.38s)
  2. `[1217..1601]` (20.28s – 26.68s)
  3. `[2081..2441]` (34.68s – 40.68s)
  4. `[3671..4032]` (61.18s – 67.20s)
  5. `[4962..5102]` (82.70s – 85.03s)
  6. `[5422..5755]` (90.37s – 95.92s)
- **Subtitle 1**: 45 cues ใช้ Preset แนวตั้ง `Mitr-short-001` (วางตำแหน่ง y ~1000 px ลอยระดับอก/รอยต่อจอ อ่านง่าย ไม่ทับหน้าตัวละคร)
- **Audio 1–3**: Dialogue, SFX 15 จุด, BGM -19 dB ตรงตาม master 16:9 ทุกประการ

---

## 4. กับดักทางเทคนิคและวิธีแก้ (Technical Traps & Fixes)

### Trap 1: การตัดหัวคลิปในไฟล์ DRT XML
- **ปัญหา**: เมื่อระบุเฉพาะ `Duration=5846` ใน DRT XML โดยไม่ระบุ `<In>168</In>` Resolve จะตัดที่หางคลิปแทนหัว (LeftOffset: 0, RightOffset: 168)
- **วิธีแก้**: ต้องระบุ `<In>168</In>` บนทั้ง Video 1 และ Audio 1 ในไฟล์ DRT XML เสมอ เพื่อให้ได้ `LeftOffset: 168, RightOffset: 0`

### Trap 2: การโหลด Subtitle Preset โดยไม่ต้องปิด Resolve (Live DRT Patching)
- **ปัญหา**: Resolve Scripting API ไม่มีเมธอดในการเปลี่ยน Subtitle Track Preset บนไทม์ไลน์ที่เปิดอยู่โดยตรง และการแก้ SQLite Database ออฟไลน์เสี่ยงต่อการค้างของ `Resolve.exe`
- **วิธีแก้ที่เสถียรที่สุด**:
  1. ส่งออกไทม์ไลน์เป็น DRT ด้วย `timeline.Export(drt_path, r.EXPORT_DRT, r.EXPORT_NONE)`
  2. รัน `scripts/drt_set_subtitle_preset.py` เพื่อแพตช์ไบต์ Preset ลงใน `EffectFiltersBA` ของ `Sm2TiTrack.FieldsBlob` (Type 2)
  3. ลบไทม์ไลน์ชั่วคราวออก
  4. นำเข้ากลับเข้ามาใหม่ด้วย `media_pool.ImportTimelineFromFile(patched_drt)`
  5. ไทม์ไลน์จะได้สไตล์ Preset ทันทีโดยไม่ต้องแก้ Project.db และไม่ต้องรีสตาร์ท Resolve

### Trap 3: ค่าคงที่ Export Constants ใน Resolve Python API
- **ปัญหา**: การเรียก `timeline.Export()` ด้วยค่าตัวเลขดิบ เช่น `(path, 2, 0)` ทำให้คำสั่งล้มเหลวหรือส่งออกเป็น EDL
- **วิธีแก้**: ใช้ค่าคงที่ทางการเสมอ:
  - `r.EXPORT_DRT` (ค่า `1.0`)
  - `r.EXPORT_NONE` (ค่า `-1.0`)

### Trap 4: การค้นหา Library Root สำหรับ `find_user_db`
- **ปัญหา**: `find_user_db(root, user)` ต้องการ path ของ Library Root Directory ไม่ใช่ชื่อโปรเจกต์
- **วิธีแก้**:
  ```python
  pm = resolve.GetProjectManager()
  db = pm.GetCurrentDatabase()
  root = library_roots()[db["DbName"]]
  user_db = find_user_db(root, "guest")
  ```

### Trap 5: มาตรฐาน Loudness สำหรับ YouTube Shorts / Social Clips
- ตั้งเป้าหมาย Integrated Loudness ไว้ที่ **-13 ถึง -14 LUFS** (ผลลัพธ์ของ Day 30 ได้ **-13.2 LUFS**, LRA 2.2 LU)
- ระดับนี้ช่วยให้เสียงดังฟังชัดบนโทรศัพท์มือถือ โดยไม่โดนระบบ Auto-Gain / Loudness Normalization ของ YouTube ปรับลดความดังลง

### Trap 6: นโยบายความปลอดภัยของไฟล์ (Safety & Recoverability)
- **ต้องสำรอง `.drp` ที่ตรวจสอบแล้วเสมอก่อนลบไทม์ไลน์หรือแปลงโปรเจกต์** ผ่าน `scripts/backup_drp.py`:
  - ตัวอย่าง Day 30: `katy404_day30_pre_promote_clean_*.drp` และ `katy404_day30_before_9x16_*.drp`
- ทำงานบน Timeline สำรอง (`_clean`, `_9x16`, `_variant`) เสมอ และตรวจสอบเฟรมผ่าน readback ก่อนโปรโมตเป็นไทม์ไลน์หลัก

---

## 5. สคริปต์และชุดคำสั่งสำคัญใน Repository

- `scripts/build_9x16_day30.py`: สคริปต์ประกอบ 9:16 อัตโนมัติ (V1/V3/V4 layout, focus zoom 6 จุด, patch Mitr-short-001 ผ่าน DRT, verify ภาพนิ่ง)
- `tests/test_build_9x16_day30.py`: เทสต์สำหรับสคริปต์ 9:16 (merge ranges, layout math, timeline naming)
- `scripts/drt_set_subtitle_preset.py`: ตัวแพตช์ Subtitle Preset เข้าไฟล์ DRT XML
- `scripts/backup_drp.py`: ตัวสำรองโปรเจกต์ DRP ที่ตรวจสอบความถูกต้องแล้ว

### Trap 7: ไมค์เบามากในไฟล์ OBS ดิบ (day 31)
- **ปัญหา**: ไฟล์ day 31 วัดได้ -34.7 LUFS (true peak -15.8 dBFS) ขณะที่ day 30 ได้ -30.8 LUFS; ถ้าใช้แค่ AudioVolume จะต้องเพิ่ม ~20 dB ซึ่งทำให้ peak ชน
- **วิธีแก้**: ใช้ `scripts/set_dialogue_leveler.py --apply` เปิด AI Dialogue Leveler บน A1 (ReduceLoud + LiftSoft, BackgroundReduction ปิด, OutputGain 0) แล้วค่อยปรับ AudioVolume; day 31 ได้ -12.3 LUFS / true peak -1.1 dBFS (A1 +9.6 dB จากเดิม +11.6 dB ที่ผู้ใช้ตั้งไว้)
- **หมายเหตุ**: หน้าต่างซูมต้องวัดใหม่ทุกสตรีม — day 31 อวาตาร์อยู่คอลัมน์ ~0.78 ของเฟรม โทนผมเริ่ม ~0.556 ทำให้ window top 0.520 / bottom 0.985 / cx 0.760 (Size 2.15) ได้ headroom ~7% และไม่มีขอบดำขวา ไม่ใช้ค่าของ day 30 ได้โดยตรง

---

## 6. Day 31 Learned Rules & SOPs (เพิ่มเติมจาก Session Summary)

### 6.1 Timeline Promotion Workflow (โปรโมตไทม์ไลน์หลักและลบตัวดิบ)
- **คำสั่งทริกเกอร์**: "อัปเดต Timeline หลัก และลบ Timeline สำรอง"
- **ขั้นตอน**:
  1. สำรองไฟล์ `.drp` ก่อน (เช่น `pre_promote.drp`) ผ่าน `scripts/backup_drp.py`
  2. ลบ Timeline ตัวดิบด้วย unique ID ผ่าน Python `MediaPool.DeleteTimelines` (ห้ามใช้ MCP `timeline.delete_timeline` เพราะจะสร้าง `_archived` ค้างในโปรเจกต์)
  3. เปลี่ยนชื่อ `Timeline 1_edit` → `Timeline 1`
  4. ตรวจสอบ: 3,140 เฟรม, A1 OutputGain = 2.0
- **เหตุผล**: MCP `delete_timeline` ทำให้เกิด timeline `_archived` ค้าง ใช้ Python API ตรงๆ สะดวกกว่าและสะอาดกว่า

### 6.2 การคำนวณ Geometry 9:16 สำหรับ Katy404 (Day 31)
- **หลักการ**: **ห้ามคัดลอกค่าพิกัดและสเกลจากตอนก่อนหน้า** ต้องวัดค่าจาก source ใหม่ทุกครั้ง เนื่องจากขนาดและตำแหน่งอวาตาร์เปลี่ยนไปในแต่ละวัน
- **ค่าที่วัดได้ Day 31**:
  - `AV_CENTRE`: (1022, 532)
  - `K_STACK`: 2.8235
  - `K_FULL`: 3.3 (ปรับลดจาก 4.0 เพื่อหลบซับ)
  - `GAME_WIN`: (230, 90, 860, 650)
- **QC**: ผ่าน 6/6 เฟรม และเรนเดอร์ส่งมอบ `วันที่ 31_9x16_test_2026-11-18.mp4` (-12.3 LUFS)
- **สคริปต์**: เก็บไว้ที่ `scripts/scratch/d31/`

### 6.3 ระยะปลอดภัยของซับไตเติล (Mitr-short-001)
- **ความละเอียด**: 1080x1920
- **แถบซับ**: อยู่ที่ y ≈ 985-1090
- **กฎ**: ตั้งค่าสเกลและตำแหน่งของอวาตาร์โหมด Full (K_FULL) ให้ **ดวงตาอยู่ต่ำกว่า y = 1090 เสมอ**
- **ตัวอย่าง**: K_FULL 3.3 → ดวงตาอยู่ที่ y ≈ 1129 (ปลอดภัย)
- **หมายเหตุ**: K_FULL 4.0 เดิมทำให้ดวงตาสูงเกินไป ทับซับ → ปรับเป็น 3.3

### 6.4 การตรวจสอบ QC ตำแหน่งซับ (Subtitle Position QC)
- **ปัญหา**: การ `ExportCurrentFrameAsStill` จาก DaVinci Resolve **จะไม่ติดซับไตเติล** (native still export omits subtitles)
- **วิธีที่ถูกต้อง**: ใช้วิธี **diff ภาพเฟรมจากไฟล์วิดีโอที่เรนเดอร์จริง** เทียบกับ `expected canvas` เพื่อตรวจสอบตำแหน่งซับ
- **เครื่องมือ**: `scripts/focus_frame_qc.py` หรือ `ffprobe` + pixel comparison
- **หลักฐาน**: ต้องดูภาพเคลื่อนไหวจากไฟล์ render จริง ไม่ใช่ still image

### 6.5 การอัปเดตเอกสารและทดสอบ Repo (Day 31)
- เพิ่มบันทึกใน `docs/channels/katy404.md` และ `docs/OPERATING-NOTES.md`
- รีเฟรช `docs/skills-manifest.json`
- `pytest` ผ่าน 27 รายการ
- **ยังไม่ได้ commit** และ **ไม่แตะไฟล์** `katy404-minecraft-editing/SKILL.md` ที่ถูกแก้ไขค้างไว้ (จะทำในครั้งนี้)

---

## 7. สคริปต์และชุดคำสั่งสำคัญใน Repository (อัปเดต Day 31)

- `scripts/build_9x16_day30.py`: สคริปต์ประกอบ 9:16 อัตโนมัติ (V1/V3/V4 layout, focus zoom 6 จุด, patch Mitr-short-001 ผ่าน DRT, verify ภาพนิ่ง)
- `scripts/scratch/d31/`: สคริปต์ Day 31 geometry measurement และ 9:16 build
- `scripts/scratch/d35/`: สคริปต์ Day 35 16:9 master, DRT subtitle patch, avatar centering calibration และ 9:16 build
- `tests/test_build_9x16_day30.py`: เทสต์สำหรับสคริปต์ 9:16 (merge ranges, layout math, timeline naming)
- `scripts/drt_set_subtitle_preset.py`: ตัวแพตช์ Subtitle Preset เข้าไฟล์ DRT XML
- `scripts/backup_drp.py`: ตัวสำรองโปรเจกต์ DRP ที่ตรวจสอบความถูกต้องแล้ว
- `scripts/focus_frame_qc.py`: QC ตำแหน่งซับด้วย pixel diff จากไฟล์ render จริง
- `scripts/set_dialogue_leveler.py`: AI Dialogue Leveler สำหรับไฟล์มิกเบา

---

## 8. Day 35 Learned Rules & SOPs (Minecraft Day 35)

### 8.1 การตัดต่อ 16:9 Clean Master (Cold Open Pacing)
- **แหล่งฟุตเทจ**: `2026-11-22 22-28-34.mp4` (2560x1440 @ 60fps บนไทม์ไลน์ 1920x1080 @ 60fps)
- **การตัดหัวและท้าย**:
  - ตัดหัว 0–318 เฟรม (5.3 วินาที) ลบหน้าเมนูเกมและช่วงนับเลข 1–2–3 เพื่อเปิดด้วยประโยคพูดทักทายทันที
  - ตัดท้าย 3,660–3,760 เฟรม ลบช่วงเงียบหลังพูด "บ๊ายบาย" ได้ความยาวสุทธิ 55.7 วินาที (3,342 เฟรม)
- **VTuber Zoom (Video 2)**: 5 Adjustment Clips ด้วย Fusion Transform (สเกล 2.15x, จัดกึ่งกลางอวาตาร์ Katy404, คุม Headroom ~7% ไม่ตัดจงอยผม ahoge และไร้ขอบดำ):
  1. เปิดคลิป & ทักทาย
  2. ประกาศเป้าหมายปลูกข้าวจนกว่าจะ 10,000 ซับ
  3. เผยยอดผู้ติดตามปัจจุบัน
  4. จังหวะขอบคุณคนดู
  5. Call to action ฝากแชร์ & โบกมือลาจบคลิป
- **ซับไตเติล (Subtitle 1)**: 33 cues ด้วย Preset `Mitr Font` ผ่าน `caption_lint.py` 100%
- **ระดับเสียง (Audio 1)**: ยกเกน +11.5 dB จากต้นทาง -29.4 LUFS (เป้า -13 ถึง -14 LUFS; ยังไม่ได้วัดความดังหลังปรับจากไฟล์ render — ต้องวัดก่อนส่งมอบ)

### 8.2 Clean Timeline Promotion Workflow
- **กติกาสำคัญ**: ห้ามใช้ MCP `timeline.delete_timeline` เพราะจะทิ้งไทม์ไลน์ `_archived` ตกค้างในโปรเจกต์
- **ขั้นตอนที่ถูกต้อง**:
  1. สำรองไฟล์ DRP: `day35_pre_promote_cleanup.drp` (ตรวจความสมบูรณ์ไฟล์)
  2. ลบไทม์ไลน์ดิบเดิมออกด้วย Python API ตรง: `media_pool.DeleteTimelines([raw_timeline])`
  3. เปลี่ยนชื่อไทม์ไลน์ตัดต่อ `Timeline 1_edit` เป็น `Timeline 1` ให้เป็นไทม์ไลน์หลักหนึ่งเดียว

### 8.3 กับดักพิกัดอวาตาร์ 9:16 (Day 35 Geometry & Centering Trap)
- **ปัญหาที่พบ**: เมื่อใช้ค่า `AV_CENTRE = (1065.0, 540.0)` ที่คัดลอกมาจาก Day 30 ตัวละครเยื้องไปทางขวา ~118–133 พิกเซล (วัดด้วยสคริปต์ สคริปต์วัดของ opencode ใน `scripts/scratch/d35/`: V3 +117.6 px, V4 +127..+133 px; หลังแก้เหลือไม่เกิน 27 px) ทำให้ผู้ใช้ต้องทักว่า *"ตัวละคร ให้อยู่ตรงกลางให้หน่อย"* และซับไตเติลทับหน้าผาก/ดวงตา
- **การวัดพิกัดจริงของ Day 35**:
  - Bounding Box เส้นผม: x = 999..1214, จุดกึ่งกลางแท้จริง `cx = 1103.0`
  - ปลายจงอยผม (ahoge): y = 405
- **สูตรพิกัดที่ถูกต้องสำหรับ Day 35**:
  - `GAME_WIN = (300.0, 90.0, 930.0, 650.0)`
  - `AV_CENTRE = (1103.0, 540.0)`
  - `K_STACK = 3.06`: หน้าต่าง 353x314 px (`x = [926.5, 1279.5]`), Headroom เหนือ ahoge ~7%, `CropRight = 0.45 >= 0` (ไม่เกิด Crop ติดลบ)
  - `K_FULL = 3.3`: สเกล 3.91x, จัดกึ่งกลางหน้าจอพอดีที่ x = 540, ตาอยู่ที่ y ≈ 1194 (อยู่ใต้แถบซับไตเติล y ≈ 985-1090 พอดี ไม่โดนซับบังตา)
  - `SRC_BOTTOM = 720.0`: ยึดขอบล่างของอวาตาร์ชิดขอบล่างจอ canvas y = 1920 ไร้ขอบดำ 100%

### 8.4 การลง Subtitle Preset โดยไม่รีสตาร์ท Resolve ผ่าน DRT Round-trip
- ส่งออกไทม์ไลน์เป็น DRT ด้วย `timeline.Export(tmp_export, resolve.EXPORT_DRT, resolve.EXPORT_NONE)`
- แพตช์ไบต์ Preset `Mitr-short-001` ลงใน DRT ด้วย `patch_drt`
- สลับหน้าไปไทม์ไลน์เดิม ลบไทม์ไลน์ชั่วคราว แล้ว `media_pool.ImportTimelineFromFile(tmp_patched)`
- ไทม์ไลน์ 9:16 จะได้สไตล์ฟอนต์ Mitr สำหรับแนวตั้งทันทีโดยไม่ต้องแก้ SQLite Database ออฟไลน์

### 8.5 Automated Visual QC ด้วยภาพนิ่ง
- สคริปต์สุ่มส่งออกภาพนิ่ง 6 เฟรม (100, 500, 1000, 1800, 2300, 3100) ไปยัง `exports/9x16-day35/verify/`
- รันสคริปต์ตรวจสอบความสมดุลขอบซ้าย-ขวา (Margin Diff ≤ 30-70px), ตรวจสอบขอบดำทั้ง 6 ด้าน, และยืนยันว่าซับไตเติลไม่ทับบังตา

---

## 9. Day 36 Learned Rules & SOPs (Minecraft Day 36, 2026-11-25)

### 9.1 การจัดกึ่งกลางอวาตาร์ 9:16 โดยห้ามยืดภาพ (`ZoomGang = True`)
- **ปัญหาที่พบ:** เมื่ออวาตาร์อยู่ชิดขอบขวาของเฟรม (`AV_CX = 1109.2` จาก `1280` ในพิกัด 720p) การใช้สเกลเล็กเกินไป (`K_STACK = 2.50`) แล้วเลื่อนมากลางจอจะเกิดแถบดำด้านขวา และการแก้ด้วยการปลดล็อกสัดส่วน (`ZoomGang = False`, `ZoomX = 3.64`, `ZoomY = 2.963`) เพื่อยืดปิดแถบดำทำให้ตัวละคร VTuber ยืดออกด้านข้างผิดสัดส่วน
- **กฎบังคับ:**
  - **ต้องตั้ง `ZoomGang = True` (`ZoomX == ZoomY`) เสมอ** บนทั้ง `V3 VTuber Bottom` และ `V4 VTuber Full` ห้ามยืดแกนใดแกนหนึ่งเพื่อปิดขอบดำเด็ดขาด
  - คำนวณสเกลขั้นต่ำแบบคงสัดส่วนจากสูตร `K_UNIFORM >= 540.0 / (1280.0 - AV_CX)` (เมื่ออวาตาร์อยู่ฝั่งขวาในพิกัด 720p):
    - ค่า Day 36 (`AV_CX = 1109.2`): `540.0 / (1280.0 - 1109.2) = 3.162` → ใช้ **`K_UNIFORM = 3.18`**, `CY_STACK = 524.0` (ครอบคลุมหัว–จงอยผม–ไมค์–มือบน)
    - ค่าอ่านกลับจริงใน Resolve: `ZoomX = ZoomY = 3.769`, `Pan = -1492.056` → ตัวละครอยู่กึ่งกลางเฟรม (`x = 540 px`) ไร้แถบดำ และสัดส่วน `1:1` ครบถ้วน
  - อ้างอิงชุดสคริปต์งานของ Day 36 ใน `scripts/scratch/d36/` (ขั้นตอนปลดอาการภาพยืดและจัดกึ่งกลาง V3/V4)

### 9.2 การคาลิเบรตเสียงจากต้นทาง OBS ที่เบามาก (-33.5 LUFS)
- ต้นทาง Day 36 (`2026-11-24 22-34-34.mp4`, `2560x1440 @ 60fps`) วัดเสียงพูดดิบได้ `-33.5 LUFS` (True Peak `-13.5 dBFS`)
- ชุดค่าที่ผ่านเกณฑ์บนทั้ง 16:9 และ 9:16: เปิด `Dialogue Leveler` บน `A1` (`ReduceLoud + LiftSoft`, ปิด `BackgroundReduction`) + `AudioVolume +4.5 dB`, วาง `SFX` บน `A2`, `BGM` (`bgm_cute_adventure_melody_island.wav`) `-20.0 dB` (`FadeIn 12 / FadeOut 96`) บน `A3`
- ผลวัดบนไฟล์ `_FINAL` ทั้งสองรูปแบบ: **`-14.2 LUFS`**, `LRA 2.1 LU`, True Peak **`-1.1 dBFS`**

### 9.3 การตัดหัวคลิป vs การคงท้ายคลิป และสำเนาเรนเดอร์ชั่วคราว
- **เริ่มงานตามคำสั่งล่าสุด:** หากผู้ใช้สั่งคงฟุตเทจเต็มไว้ใช้ footer ก่อน ให้ประกอบบนความยาวเต็ม (`4048` เฟรม) และเมื่อผู้ใช้สั่งตัดหัวภายหลัง (`385` เฟรม → เหลือ `3663` เฟรม / `61.05 วิ`) ให้ซิงก์ V2/V3/V4/ซับ/เสียงทั้งหมดเข้าช่วงใหม่
- **เช็กแทร็กและคิวเรนเดอร์:** อย่าตีความว่า `GetIsTrackEnabled == False` บนไทม์ไลน์ที่ไม่ได้แอ็กทีฟแปลว่าแทร็กถูกปิด (ต้อง activate ไทม์ไลน์ก่อนอ่านค่า) และหากต้องเรนเดอร์ผ่านสำเนาชั่วคราว (`_delivery_tmp`) เพื่อคงไทม์ไลน์หลักไม่ให้ถูกแตะ ต้องเก็บกวาดลบไทม์ไลน์ชั่วคราวออกหลังส่งมอบเสร็จทุกครั้ง


