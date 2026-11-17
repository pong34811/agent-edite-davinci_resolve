---
name: katy404-minecraft-editing
description: ใช้เมื่อตัดต่อคลิปเกม Minecraft ช่อง KATY404 (ซีรีส์ "ปลูกข้าวจนกว่าจะ 10K ผู้ติดตาม") ทั้ง 16:9 Clean Master และ 9:16 Shorts/TikTok ใน DaVinci Resolve — ครอบคลุมการจัดโครงสร้างแทร็ก, ค่า Geometry/Scale, Preset ซับไตเติล Mitr, การวาง Focus Zoom, กลยุทธ์การตัดต่อเพิ่มยอดวิว/Retention, และการแก้ Bug/Trap ทางเทคนิค (DRT XML In-offset, Live DRT Preset patch, Loudness -13.2 LUFS)
version: 0.1.0
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
