# แผนแปลง Timeline 16:9 → 9:16 (KT404_2026-09-29) — บันทึกส่งต่องาน

> เขียนเมื่อ 2026-10-01 หลังหยุดงานกลางคัน (โควตา Antigravity/Gemini หมด และผู้ใช้สั่งหยุด)
> แหล่งข้อมูล: transcript Antigravity `2009ba19-…`, ไฟล์ใน `.agents/teamwork/`, `scripts/`, `test_qc_stills/`
> **ไม่ได้ตรวจ Resolve สด** ตอนเขียนแผนนี้ — สถานะ timeline ใน Resolve ต้องอ่านใหม่ก่อนทำอะไรต่อ
> `PLAN.md` ที่ root เป็นแผนของงาน Aomi-mama คนละงาน อย่าสับสน

## 1. เป้าหมาย (จากคำสั่งผู้ใช้)
- โปรเจกต์ `KT404_2026-09-29` (ID `7c38045b-c9ae-426c-8b4c-2e2d726d88ff`), โฟลเดอร์งาน `G:\My Drive\Projects\Katy404\2026-09-29`
- สร้าง Timeline ใหม่ `<ชื่อเดิม>_9x16` 1080x1920 จาก 16:9 ที่ตัดเสร็จแล้ว **30 ตัว** (29 @60fps, 1 @30fps — ให้ FPS ตรงต้นฉบับ) เพื่อ TikTok/Shorts/Reels
- เลย์เอาต์: เกมอยู่บน + หน้า VTuber ขยายอยู่ล่าง (Split Screen)
- ช่วง V3 "Adjustment Clip" (VTuber Focus) → ภาพ VTuber เต็มจอ 9:16
- V2 GIF รีแอคชัน: คงเวลาเดิม วางใหม่ไม่บังหน้า/ซับ
- **ห้ามแตะ:** Subtitle track (ข้อความ/เวลา/สไตล์), ความยาวคลิปและจุดตัด, SFX/BGM/ระดับเสียง, timeline 16:9 เดิม
- ผลลัพธ์: แค่ Timeline ใน Resolve (ไม่เรนเดอร์)
- วิธีทำ: สำรอง .drp ก่อน → ทำ 1 ตัวอย่างให้ดู → ค่อยทำที่เหลือ → ทำทีละตัวและเช็ก Resolve ทุกครั้ง

## 2. สถานะที่ทำเสร็จแล้ว
| ขั้น | สถานะ | หลักฐาน |
|---|---|---|
| สำรวจ (30 timeline, track, FPS) | เสร็จ | `.agents/teamwork/explorer_{1,2,3}/report.md`, `orchestrator/PROJECT.md` |
| M1 สำรอง `.drp` + baseline 30 timeline (ซับรวม 2,066 คิว) | ผ่าน gate (reviewer/challenger/auditor ผ่านหมด) | `G:\My Drive\Projects\Katy404\2026-09-29\KT404_2026-09-29_pre_9x16_conversion_2026-10-01.drp` (1.45 MB), `worker_m1/baseline_30_timelines.json`, `scripts/m1_backup_and_baseline.py` |
| M2 Pilot `หนีฝ่าความหนาว_Minecraft-vdo_9x16` (5,880 เฟรม, ซับ 45/45, เสียง A1–A3) | สร้างแล้ว **แต่ภาพ framing ไม่ผ่าน gate** | `orchestrator/GATE_STATUS.md` |

M2 รอบแรก FAIL (reviewer_m2_2 + challenger_m2_1): `V1 CropBottom=486` ทำให้เกิดช่องดำ ~964px กลางจอ, `V2 CropTop=480` ตัดหัว/หน้า avatar, `V3 Fusion Center=(0.50,0.25)` ดัน VTuber ออกนอกจอ (ดำ ~83%). ส่วน invariant (ซับ/เสียง/ความยาว/ไม่มี offline) **ผ่านทุกคน** — ข้อบกพร่องอยู่ที่ geometry เท่านั้น. นอกจากนี้ `worker_m2/verify_pilot.py` เป็นตัวตรวจที่ตรวจตัวเอง (เทียบเลขที่ตัวเองตั้ง + ไฟล์ >1MB) — ห้ามใช้เป็นหลักฐาน

## 3. จุดที่ค้างกลางทาง (worker_m2_retry — ไม่มี handoff)
- `scripts/m2_convert_pilot.py` **ไม่สอดคล้องในตัวเอง**: docstring (บรรทัด ~10–13) เป็นค่าใหม่ (V1 CropBottom 0, V2 Tilt -80/CropTop 0, V3 Pivot (0.5,0.25)/Center (0.5,0.5)/Size 2.0) แต่โค้ดบรรทัด ~329–366 ยังเป็นค่าเก่า (CropBottom 486, Tilt -200, CropTop 480, Center 0.25) → **แก้โค้ดให้ตรงค่าใหม่ก่อนรันซ้ำ**
- ค่าใหม่ยังเป็น *สมมติฐาน* ยังไม่ผ่านการยืนยันจากภาพ — ผลทดลองอยู่ใน `test_qc_stills/` (`v1_tilt_*`, `diag_v1_tilt_*`, `v2_tilt_*`, `v2_pan_936/960`, `split_screen_normal_216500.png`, `vtuber_focus_zoom_219300.png`, `reaction_gif_safe_218650.png`) และสคริปต์ `experiment_framing.py`, `test_v1_tilt.py`, `diagnose_v1.py`, `test_v3_fusion.py`, `test_v4_gif.py`, `inspect_avatar_features.py`
- `scripts/verify_pilot_pixels.py` เขียนแล้ว (ตรวจ 1080x1920, สัดส่วนแถวดำ <15%, ไม่มีช่องดำกลางจอ rows 500–1400, มี avatar ล่าง, V3 ไม่มีแถวดำ) แต่ **ยังไม่มีบันทึกว่ารันผ่าน**; ค่าเริ่มต้นชี้ไปโฟลเดอร์ `worker_m2/qc_stills/` ซึ่งยังเป็นภาพเก่าจากรอบ FAIL (17:34) ต้อง re-export ใหม่
- ไม่รู้ว่า retry เขียนค่าใหม่ลง Resolve แล้วหรือยัง → อ่านค่าจริงจาก timeline ก่อน

## 4. ขั้นต่อไป (ลำดับ)
1. **Preflight (อ่านอย่างเดียว):** ต่อ Resolve, ยืนยัน build/โปรเจกต์/timeline ที่เปิดอยู่, บันทึก playhead/page/timeline ปัจจุบันเพื่อคืนค่าตอนจบ, เช็กว่า timeline 16:9 เดิมยังตรง `baseline_30_timelines.json` (ความยาว, track, ซับ)
2. **ซ่อม Pilot:** แก้ `m2_convert_pilot.py` ให้ตรงค่าใหม่ → ปรับจูนทีละ param (หนึ่งตัวแปรต่อรอบ, mutation ห่างอย่างน้อย ~1.2s, ค่าเป็น float, อ่านกลับหลัง setter คืน False) → ตรวจด้วยภาพจริง (frame 216500 ปกติ / 218650 GIF / 219300 VTuber Focus) ดูหัว หน้า มือ headroom และไม่ชนซับ
3. **Gate Pilot:** re-export 3 stills → `verify_pilot_pixels.py` ผ่านจริง + ดูภาพด้วยตา + ซับ 45/45 (ข้อความ+เฟรมตรง baseline), เสียง A1–A3 ไม่เปลี่ยน, 5,880 เฟรม, offline = 0, `SaveProject()` → **ให้ผู้ใช้ดูและอนุมัติตัวอย่าง** (กฎ "ตัวอย่างก่อน" ของผู้ใช้ — ห้ามข้ามไปทำ batch)
4. **M3 Batch 29 ตัว** (หลังอนุมัติเท่านั้น): ทีละตัว, ตรวจ invariant และเสถียรภาพ Resolve ทุกตัว, หยุดทันทีถ้ามีตัวใดล้ม. หมายเหตุ: ค่า framing ที่จูนจากตัวอย่างอาจไม่พอดีทุกคลิป (ตำแหน่ง avatar/ขนาด GIF/จำนวน V3 ต่างกัน) → ตรวจภาพอย่างน้อยสุ่มต่อตัว, 1 ตัวเป็น 30fps
5. **M4 ตรวจรวม:** 30 ต้นฉบับไม่เปลี่ยน, 30 `_9x16` ครบ (1080x1920, FPS ตรง, ซับ/เสียง/ความยาวเท่ากัน, ไม่มี offline), `SaveProject()`, คืน project/timeline/playhead/page เดิม

## 5. กฎที่ต้องไม่ลืม (AGENTS.md / OPERATING-NOTES)
- ห้ามแตะ/แก้ footage ต้นฉบับ; timeline เดิม 16:9 อ่านอย่างเดียว; ไม่ลบ backup/timeline เก่า
- ห้ามใส่ซับ/ข้อความผ่าน Text+; ซับคงเดิม 100% (อย่าตัดคำ/แก้เวลา/แก้สไตล์)
- `ZoomGang=True` ทำให้ ZoomX/ZoomY ผูกกัน; setter หลัง append อาจคืน False ทั้งที่ค่าถูก → อ่านกลับก่อนเขียนซ้ำ
- Resolve เคยแครชเมื่อ loop แน่นเกินไป → เว้น ~0.45–1.2s ระหว่าง mutation
- `ExportCurrentFrameAsStill` อาจไม่มีซับ — ใช้เพื่อดู framing ได้ แต่ QC ซับต้องจับภาพ viewer
- รายงานเฉพาะสิ่งที่ตรวจจริง; ตัวตรวจต้องอิสระจากค่าที่ตัวเองตั้ง

## 6. ความเสี่ยง/คำถามเปิด
- ใน transcript ผู้ใช้ยังไม่ได้ตอบ A1/A2 ในคำถามเลือกเลย์เอาต์ครบถ้วนใน log ที่ย่อไว้ — prompt ที่ปล่อยทีมสรุปไว้ว่า *Split Screen + VTuber Focus เต็มจอ + GIF ย้ายตำแหน่ง ไม่เพิ่มแถบหัวข้อ/SFX*; ถ้าผู้ใช้ต้องการเปลี่ยน ให้ยืนยันก่อนทำ batch
- ไฟล์ untracked ใน repo (`.agents/teamwork/` ~12MB รวมภาพ, `scratch/`, `test_qc_stills/` ~230MB, สคริปต์ทดลอง) ยังไม่ commit — ตัดสินใจเรื่อง commit/ลบทีหลัง (ไม่ได้ลบอะไร)
- `.agents/teamwork/orchestrator/PROJECT.md` ยังระบุค่า framing เก่า (CropBottom 486 ฯลฯ) — ถือว่าล้าสมัย


## 7. อัปเดต 2026-10-01 (หลังกลับมาทำต่อ)
- Preflight สด (Resolve Studio 21.1.0.17): 30 ต้นฉบับตรง baseline ทั้งหมด (raster, start/end, ซับ), มี `_9x16` แค่ตัวเดียว (pilot)
- สอบเทียบ Resolve จริงด้วยสคริปต์ `scripts/calibrate_crop.py`, `calibrate_zoom.py`: Pan 1px/หน่วย, Tilt 0.3164px/หน่วย (บวก = ภาพขึ้น), Crop เป็นหน่วยก่อนซูม (px จริง = crop x Zoom) → สูตรอยู่ใน `scripts/layout9x16.py`
- ใช้ `scripts/apply_pilot_layout.py` ตั้งค่า V1/V2/V3 บน pilot `_9x16` เท่านั้น (id 2b0779e3-...). V1 เกมครึ่งบน, V2 ครอปเฉพาะ facecam ครึ่งล่าง, V3 Fusion Size 2.05
- ผลตรวจ: `verify_pilot_pixels.py` ผ่าน (stills ใน `scratch/pilot_iter3/`), ตรวจภาพด้วยตา: ไม่มีช่องดำ, หัว/ผม/หน้า/มือ avatar ครบ, GIF ไม่บังหน้า, focus เต็มจอเห็นหน้าชัด
- `scripts/compare_invariants.py` เทียบกับต้นฉบับสด: ซับ 45/45 ตรงข้อความ+เฟรม, เสียง 3 item ตรง, V1 range ตรง, 5,880 เฟรม, 60fps, ไม่มี offline; `SaveProject()` = True; คืน timecode 01:00:55:00 / page edit แล้ว
- **ยังไม่ได้ตรวจ:** ซับซ้อนทับ avatar บน viewer จริง (stills ไม่มีซับ), การฟังเสียง, ความเหมาะของค่า framing กับอีก 29 คลิป
- **รออนุมัติ pilot จากผู้ใช้ ก่อนเริ่ม M3**

## 8. ผลสุดท้าย (M3 + M4)
- สร้าง `_9x16` ครบ 30 ตัว (รวม pilot) รวมโปรเจกต์ 60 timeline; `scripts/m4_audit.py` ผ่าน 30/30: ต้นฉบับตรง baseline, 1080x1920, FPS ตรง (29@60, 1@30), 4 video track, ซับ/เสียง/V1/V3/GIF ตรงต้นฉบับ, ไม่มี offline, transform ตรงสูตรของแต่ละสตรีม, ไม่มี timeline กำพร้า
- ดูภาพ still (normal/gif/focus) ของทั้ง 30 ตัวด้วยตาแล้ว; ยังไม่ได้ตรวจ: ซับบน viewer จริง, การฟังเสียง, การเรนเดอร์
- Resolve ค้าง 2 ครั้งช่วงรันต่อเนื่อง ~10 timeline → ลบ timeline ที่ค้างครึ่งทาง (ตัวที่ 10 และ 20) แล้วสร้างใหม่ ผ่านทั้งคู่
- สคริปต์: `layout9x16.py` (สูตร+ค่าต่อสตรีม), `m3_convert.py`, `m4_audit.py`, `recover_check.py`
