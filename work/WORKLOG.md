# WORKLOG — Aomi-mama Clip Polish

แผน: [PLAN.md](PLAN.md) | เริ่ม: 30 กันยายน 2026

| วันที่ | Timeline | สิ่งที่แก้ + เวลา | อ้างอิงอนุมัติ | ผลเทียบ baseline | ภาพ/พรีวิว | สถานะ/งานค้าง |
|---|---|---|---|---|---|---|

## บันทึกงาน 1 — ยืนยันโปรเจกต์หลังย้าย

**เริ่ม:** 2026-09-30T11:26 | **จบ:** 2026-09-30T11:30

### ผล
- ✅ โปรเจกต์ที่เปิด: `【DEBUT STREAM】AOMI-MAMA｜ 31⧸07⧸2026 เวลา 20.00` (ID: 4c703836) — ตรงกับ manifest
- ✅ 16 Timeline ครบ — 8 แนวนอน + 8 แนวตั้ง ทุก ID ตรง manifest ไม่มี Timeline สำรองพิเศษ
- ✅ Lint: 0 error, 0 warning (เฉพาะ info: color science DaVinci YRGB — ปกติ)
- ✅ Media: 0 missing, 42 clips online — source .mp4, GIF, audio, subtitle ครบ
- ✅ Backup .drp สร้างสำเร็จ: Resolve_Backups/Aomi-mama_pre_plan_20260930_112700.drp (2.76 MB)
- ✅ Timeline ตัวอย่าง ทำไมน้ำหน้กน่ายกจังครับ_9x16: 0-976 frames, V4 มี 6 GIF items, subtitle track 1 มี 21 cues

### Baseline ตัวอย่าง (ทำไมน้ำหน้กน่ายกจังครับ_9x16)
- Duration: 976 frames @ 60fps = 16.267s
- V1: 13 clips (main.mp4), V2: 2 overlay clips, V3: empty, V4: 6 GIF items
- Subtitle track 1: 21 cues (ทำมั้ยน้ำหนัก, มัน, น่ายกจัง, เลยครับ, อือ, น่ายกอ่อ, ไม่รุ้สิ, ก็ตัวเบา, ถ้าพูดกัน, ตามจริง, ตัวเบาแล้วก็ตัวเล็ก, นะ, เพราะบ้างที, ความตัวเล็ก, มันทำให้, รอดชีวิตได้, แล้วก็มันจวงแทง, คนจากข้างหลัง, ง่ายด้วย, ตัวเล็กมีประโยชน์นะ, 555+)

## บันทึกยืนยันใหม่และรอบตัวอย่าง — 2026-09-30 12:59–13:44 +07

บันทึก 11:26–11:30 ด้านบนเป็นประวัติ ไม่ใช่สถานะ live ล่าสุด รอบนี้ตรวจผ่าน Resolve scripting จริงและเก็บหลักฐานใหม่ที่ `reference/Aomi_plan_sample_20260930_125916/`

| วันที่ | Timeline | สิ่งที่แก้ + เวลา | อ้างอิงอนุมัติ | ผลเทียบ baseline | ภาพ/พรีวิว | สถานะ/งานค้าง |
|---|---|---|---|---|---|---|
| 2026-09-30 | โปรเจกต์ / ทั้ง 17 Timeline ที่เปิดจริง | ตรวจ manifest 16 เป้าหมาย + archive เดิมหนึ่งรายการ; ไม่ลบ/สร้าง Timeline | ทำต่อตาม PLAN; Global Constraints | 16 targets ตรง ID/ชื่อ/raster/60 fps/frame count; source A/V ที่มี path ไม่ขาด; SRT เก่า 11 pool entries ขาด | `baseline.json`, `preflight-summary.json` | warning ต่างจากบันทึกเดิม; ไม่ relink/reimport |
| 2026-09-30 | โปรเจกต์ | Save + export DRP ก่อนแก้ | PLAN งาน 1 | ZIP integrity และ SHA-256 ผ่าน; ยังไม่ทดลอง restore | `Aomi-mama_pre_sample_20260930_130245.drp`, `backup-verification.json` | สำรองก่อนแก้แล้ว |
| 2026-09-30 | ทำไมน้ำหน้กน่ายกจังครับ_9x16 | V4: opening GIF f0–132, Cat f205–247 และ Angry Chibi สี่ items f443–506; แก้เฉพาะ ZoomX/ZoomY/Pan/Tilt ให้ขอบครบและกึ่งกลางบน | PLAN 98–100, 153–162; ทำตัวอย่างก่อน | ทุก item save/readback ผ่าน; main picture/audio/captions/cuts/retime ไม่เปลี่ยน; ใบหน้าเห็นชัด หู/ผมยังถูก GIF ทับบางส่วน | `sample-transform-changelog.json`, `after_9x16.mp4`, `sample-before-after.jpg` | ผ่าน QC เฉพาะ transforms/เฟรมที่ตรวจ; รอผู้ใช้ดูเลย์เอาต์ |
| 2026-09-30 | คู่ตัวอย่างทั้งสองสัดส่วน | ตรวจ stored font แบบ read-only จาก DRP; ไม่มี font/style/database mutation | PLAN งาน 2 เริ่มคู่ตัวอย่าง; ห้ามเดา binary | Track descriptor Mitr Bold; พบ Open Sans UTF-16 metadata ใน 6 cues ต่อ Timeline; ยังไม่พิสูจน์ effective font | `sample-font-audit-v02.json` (แทนฉบับ ASCII-only แรก), burn-in frames | **รอ UI**: Resolve main window visible=false; ไม่ฝืนเปิด/kill/restart |
| 2026-09-30 | คู่ตัวอย่างทั้งสองสัดส่วน | Render before/after แบบ H.264/AAC, 60 fps, subtitles BurnIn; render queue ลบเฉพาะ job ที่สร้างเอง | PLAN งาน 3/ข้อควรทราบเครื่องมือ | native previews Complete; ffprobe 976 video frames / 16.266667 s / audio 48kHz; decode ผ่าน; ตรวจภาพก่อน125+หลัง125 contact frames | `before-render-report-20260930_131906.json`, `after-render-report-20260930_133302.json`, โฟลเดอร์ `before-qc_20260930_132131` และ `after-qc_20260930_133350` | เป็นพรีวิวตรวจงาน ไม่ใช่ไฟล์ส่งมอบ |
| 2026-09-30 | โปรเจกต์ / ทั้ง 17 Timeline | final readback + Save + DRP หลังแก้ | PLAN การตรวจ baseline/บันทึก | live properties/เวลา/text/audio/track/settings ตรง baseline นอก whitelist 6 GIF; exported subtitle blocks ทุก sequence ไม่เปลี่ยน; effect blobs เปลี่ยนเฉพาะ 6 GIF; คืน timeline/playhead/page/folder และ queue เดิม | `final-verification.json`, `Aomi-mama_post_sample_20260930_134413.drp` | ZIP/hash ผ่าน; ไม่ทดสอบ restore; อีก 7 คู่ยังไม่แก้ |
| 2026-09-30 | คู่ตัวอย่าง | เทียบ decoded output ก่อน/หลัง | PLAN รักษาแนวนอนและเสียง | แนวนอน 976 frames เหมือนกันทั้งหมด; PCM SHA-256 เหมือนกันทั้งสองสัดส่วน | `comparison-verification.json`, `sample-before-after.mp4` (ซ้ายก่อน/ขวาหลัง) | **ยังไม่ฟังครบจริง** ให้ผู้ใช้ตรวจเสียง |

### Gate / ข้อจำกัด

- ยังไม่ปิดงาน sample-font และยังไม่อนุมัติตัวอย่าง จึงไม่เริ่มอีก 7 คู่ แม้ Task 2 เดิมใช้หัวข้อ “ครบ 16”
- งาน UI ต้องให้หน้าต่าง Resolve มองเห็นก่อน: stored Open Sans อาจเป็น effective override หรือข้อมูลค้าง ห้ามอ้างว่า Mitr Bold ครบจาก metadata/รูปเพียงอย่างเดียว
- แนวนอนมี GIF บังหน้าตาม baseline; รายงานไว้และไม่แก้เพราะไม่มีสิทธิ์เปลี่ยน layout ของต้นฉบับ
- ไม่พบซับล้นเฟรม sample ที่ตรวจ แต่บาง cue ยาวตามต้นฉบับ; ไม่แก้ข้อความ เวลา ขนาด สี ขอบ ตำแหน่งหรือ line break
- วิเคราะห์/เปรียบเทียบเฉพาะ rendered previews; ไม่มี source media write/transcode/proxy/relink และไม่มี direct SQLite write
- ค่าที่ native build ปฏิเสธ (`SelectAllFrames=False`, `ReplaceExistingFilesInPlace=False`, `VideoQuality='High'` และ `VideoQuality=0`) ถูกทดสอบแยกโดยคืน preset เดิมก่อน ใช้ SelectAllFrames=True และ quality ของ preset H.264 Master ที่โหลดชัดเจน ไม่ queue งานหลัง setter false
- พบ Resolve DRP tag `ListMgt::LmVersionTable` ซึ่งไม่ใช่ XML ชื่อมาตรฐาน: normalize เฉพาะ tag ใน memory เพื่ออ่านตรวจ ไม่แก้ DRP/DB/ID; effect blob ของ GIF เก็บ transforms จึง whitelist เฉพาะ 6 approved IDs แทนการกล่าวว่า effects ทุก blob ต้องไม่เปลี่ยน

## ปิดงานย้ายซับที่ค้าง — 2026-09-30 16:35 +07

คำสั่งปัจจุบัน: ทำต่อจากแชตเดิม โดยคำตอบล่าสุดเรื่องฟอนต์คือ “ไม่ต้องปรับฟอนครับ ใส่เเค่ subtitle เท่านั้น ได้เลยครับ เดี่ยวทางผมค่อยไปปรับฟอนเอง” จึงไม่แก้ฟอนต์/สไตล์และไม่เริ่มงานภาพชุดใหม่ในรอบปิด handoff นี้

| Timeline / งาน | ผลที่ตรวจจริง | หลักฐาน / ข้อจำกัด |
|---|---|---|
| `เคยเล่น Rov ไหม_9x16` | S1 enabled, 17 cues ข้อความและทุก in/out frame ตรง extraction เดิม; V5 captions-only Text+ disabled เก็บคลิปครบ ไม่ import ซ้ำ | `reference/Aomi_remaining7_20260930_154312/resume-verification-20260930_163508.json` |
| ทั้ง 17 Timeline | live invariants ตรง baseline รอบ 15:43 นอก native-caption migration; serialized sequences ทั้ง 17 ตรง DRP หลังย้ายก่อนหน้า โดยละเฉพาะ export thumbnail IDs | แนวนอน RoV ยังใช้ Text+ เดิม; ต้นฉบับภาพ/เสียงและซับของ Timeline อื่นไม่เปลี่ยน |
| Save / state / backup | SaveProject ผ่าน คืน active timeline/playhead/page/folder ณเริ่มรอบใหม่; queue/presets/format/mode ไม่เปลี่ยน; export `Aomi-mama_verified_native_20260930_163508.drp` ZIP/hash ผ่าน | DRP 2,795,479 bytes; SHA-256 `f32f9b6b19593079d7a6266c405361c1df9b27c76bca7390ced034288a0701a0`; ไม่ทดสอบ restore |
| พรีวิวเดิม `after_rov_9x16.mp4` | ffprobe ใหม่ + full decode: 1080×1920, H.264, 60 fps, 1285 frames, 21.416667 s, AAC 48kHz | ไม่มีการเรนเดอร์ใหม่; content audit ยืนยัน serialized state เท่ากับหลังย้ายที่ใช้สร้างพรีวิว |
| Visual QC | ตรวจ f72/f263/f1254 เห็น native captions; ไม่เห็นกล่องอักษร/ซับ native ซ้ำ; ยังมีข้อความชิดขอบ ทับแชต และสีขาวกลืนเสื้อ | **การย้ายซับผ่าน แต่ความอ่านง่ายยังไม่ผ่าน** ให้ผู้ใช้ปรับฟอนต์/สไตล์เอง; ไม่ฟังเสียงครบและไม่อ้าง audio PCM เหมือนกัน |
| ขอบเขตอื่น | ไม่ทำ source write/relink/transcode, SQL write, timeline creation/deletion, recut หรือ audio mutation | legacy cues >1.5s จำนวน 2 รายการเก็บตามเดิม; PLAN ทั้งฉบับยังไม่เสร็จ |

## Re-baseline หลังลบสำรอง — 2026-09-30 17:34 +07

คำสั่ง: ลบ archived 7 ตัวที่ค้าง (เก็บ `.drp` 2 ไฟล์) แล้ว readback ยืนยันค่า fix ในต้นฉบับ

| Timeline / งาน | ผลที่ตรวจจริง | หลักฐาน / ข้อจำกัด |
|---|---|---|
| ลบสำรอง 7 archived | 23 → 16 Timeline; ไม่เหลือ `_FIX`/`_archived_`; SaveProject ผ่าน; active timeline คือ `เคยเล่น Rov ไหม_9x16` | confirm token `56dea6c7...`; `.drp` 2 ไฟล์ใน Temp/backup ไม่ถูกแตะ |
| `เคยเล่น Rov ไหม_9x16` | V1 13 Tilt ตรง array เดิมครบ; V4 3 ชิ้นตรง (0.4/-150/1250), (0.45/-350/1250)x2 | `reference/Aomi_fix_readback_20260930_173418/fix-readback-baseline.json` |
| `เกมเเรกที่เริ่มไลฟ์คือ_9x16` | V1 35 Tilt pattern ตรง baseline แต่ shift -60.0 ทุกตัว (เช่น -364.392→-424.392) | ไฟล์เดียวกันข้างต้น |
| `สาเหตุไม่ชอบหนอนเเมลง_9x16` | V1 52 ตัวเป็น -424.392 หมด จากเดิม -364.392 หมด (shift -60.0) | ไฟล์เดียวกันข้างต้น |
| `เคยเล่น Rov ไหม` (แนวนอน) | V3 i0/i1 = 0.5/0.45 ตรงที่เคยแก้; i2 ไม่ถูกแตะ (0.587) | ไฟล์เดียวกันข้างต้น |
| วิธีตรวจ | read-only `get_transform` ราย item; ไม่มี setter/save; คืน active timeline แล้ว | ไม่ได้ตรวจ captions/audio/cuts/effects รอบนี้ |
| ข้อขัดแย้ง | live ไม่ตรง `Aomi_remaining7_20260930_154312/baseline.json` (ไฟล์นั้นยังเก็บค่า pre-fix) ทั้งที่บันทึก 16:35 อ้างว่าตรง — ไฟล์ baseline เก่าสำหรับ Timeline เหล่านี้ ให้ถือไฟล์ re-baseline นี้เป็นหลัก | ต้อง re-baseline ก่อนอ้างอิงครั้งต่อไป (ทำแล้วในรอบนี้) |

