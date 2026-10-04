# ใส่ SRT ใน Subtitle Track และโหลด font preset

## ขอบเขตและ prerequisites

ใช้เมื่อผู้ใช้ขอใส่ซับจาก SRT ที่มีอยู่ หรือใช้ preset จัดฟอนต์บน native
Subtitle track เท่านั้น ไม่สร้าง Text+ ไม่ถอดเสียงใหม่ ไม่เปลี่ยนคำ/เวลา
และไม่แก้ source media โดยไม่ได้รับอนุญาต

ต้องมี Resolve เปิดอยู่, Python scripting bridge ที่เชื่อมต่อได้ และเข้าถึง
SRT/Media Pool item จริง สำหรับ helper โหลด preset ต้องเป็น disk database
และมี preset อยู่ใน User.db ที่ระบุ ใช้ `terminal` รันคำสั่งจาก root ของ repo
ตรวจ interpreter/dependencies จริงก่อน ไม่สมมติว่า pip และ python เป็นตัวเดียวกัน

## 1. สำรวจและเก็บสถานะก่อนแก้

- อ่านกฎ `AGENTS.md` และ `docs/OPERATING-NOTES.md` ตรวจ project/timeline IDs,
  Resolve build, timelineFrameRate และ timelinePlaybackFrameRate แยกกัน,
  resolution/aspect ratio, timeline start/end และสถานะ render
- ตรวจ Media Pool ทุก bin ที่เกี่ยวข้องด้วย path, unique ID และ Type == Subtitle
  อย่าเลือกด้วยชื่อแสดงผลอย่างเดียว และอย่า import ซ้ำถ้ามี item ที่ถูกต้องอยู่แล้ว
- เก็บทุก video/audio/subtitle item: ID, ข้อความ/ชื่อ, record start/end,
  source trim, track index; เก็บ enabled/locked, track names, format,
  active timeline, playhead ที่อ่านสดจาก active timeline, page และ Media Pool folder
- ใช้ recoverable variant ตามขอบเขต หรือ export/ตรวจ DRP ก่อนแก้ original
  ตรวจว่าไฟล์ไม่ว่างและ archive อ่านได้ ไม่ลบ backups โดยอัตโนมัติ

## 2. ใส่ SRT ที่มีอยู่ด้วย Python API

ใช้ `Project.GetCurrentTimeline()` และ `Project.GetMediaPool()`
อ่าน SRT UTF-8/UTF-8-SIG จาก path ที่ตรวจแล้วและนับ cues ด้วยโปรแกรม

- ถ้าไม่มี subtitle track: `Timeline.AddTrack("subtitle")` แล้วรออย่างน้อย
  ~1.2s และอ่านกลับว่า track ใหม่ว่างจริง
- ถ้ามี cues อยู่แล้ว: ตรวจว่าเป็นรายการเดียวกันหรือไม่ก่อน ถ้าครบแล้วให้เป็น
  no-op; ห้าม append ซ้ำหรือ delete/replace track โดยไม่ได้รับอนุญาต
- เมื่อมีหลาย subtitle tracks อย่าเดาว่า bare payload จะเลือก track ที่ต้องการ
  ต้องมี empty target และตรวจ readback ว่าซับไปลง track ไหนจริง
- ใช้ `MediaPool.AppendToTimeline([{"mediaPoolItem": item}])` เท่านั้น
  ห้ามใส่ trackIndex/mediaType/recordFrame/startFrame/endFrame ใน payload SRT:
  อาจทำให้ cues เลื่อนไป timeline-end บวกเวลาจากไฟล์
- เว้นอย่างน้อย ~1.2s ระหว่าง structural mutations และอ่าน live state
  อย่าเชื่อ nonempty return list เพียงอย่างเดียว
- เปรียบเทียบทุก cue ตามลำดับ: text และ absolute `GetStart()/GetEnd()`
  แปลง SRT milliseconds ด้วย FPS ของ timeline และ start-frame origin ที่ตรวจแล้ว
  สำหรับ nonnegative timestamps ที่วัดบน 21.1.0.17 ใช้ nearest frame
  (half-up: `int(milliseconds * fps / 1000 + 0.5)`); อย่าใช้ integer rounding
  นี้กับ fractional/drop-frame build โดยไม่ตรวจ timebase จริง
- ตรวจ end ของทุก cue อยู่ในช่วงอนุมัติ ภาพ/เสียงเดิมไม่เลื่อน และ save/readback

**ข้อผิดพลาดหลัง append:** ถ้า script ล้มระหว่าง restore/save ซับอาจใส่ไปแล้ว
เริ่มด้วยการอ่าน track ไม่ rerun append ทั้งก้อน ใช้ `Project.SetCurrentTimeline`
ไม่ใช่ `ProjectManager.SetCurrentTimeline`

**แก้ SRT path เดิม:** ImportMedia อาจคืน cached text เก่า ต้องได้รับอนุญาต
replace ก่อน เอาเฉพาะ stale pool item/target captions ออก แล้ว reimport/readback
อย่าลบทุก subtitle track ด้วย loop เป็นค่าเริ่มต้น และตรวจ preset หลังสร้าง track ใหม่

## 3. ค้นหา preset โดยรักษาชื่อจริง

โหลดด้วย helper ที่มีอยู่ผ่าน `terminal`:

```bash
python scripts/load_subtitle_preset.py --list
python scripts/load_subtitle_preset.py --preset "Mitr Font"
```

คำสั่งที่สองเป็น **dry run** บน current timeline เท่านั้น
ตัวอย่างชื่อไม่ได้อนุญาตให้แทนชื่อที่ผู้ใช้ระบุ ต้องตรวจ `--list` ก่อนเสมอ
`Mitr-Font`, `Mitr Font` และ `Mitr-short-001` เป็นคนละ identifier
ถามผู้ใช้เมื่อชื่อไม่ตรง อย่า normalize hyphen เป็น space เอง

Preset ผูกกับ library/User.db ไม่ใช่ global list เสมอไป ถ้า list ว่าง:

1. ตรวจ current database name/type และ source User.db ที่ helper ใช้
2. ตรวจ disk-library roots จาก `library_roots()` และเฉพาะ User.db ของ
   libraries ที่ผู้ใช้เข้าถึงได้แบบ read-only ไม่อ่าน credential/config secrets
3. list ด้วย `--user-db` ของ source ที่ค้นพบ ตรวจ exact name/font descriptor
4. ขออนุมัติชื่อ/source library ก่อนใช้ preset ข้าม library

```bash
python scripts/load_subtitle_preset.py --list --user-db "<discovered-source-User.db>"
python scripts/load_subtitle_preset.py --preset "<exact-approved-name>" --user-db "<discovered-source-User.db>" --timeline "<exact-target-timeline-name>"
```

แทน placeholders ด้วย path/name ที่ค้นพบจริง ไม่ hardcode machine-local paths
อย่าสลับ active database เพื่ออ่าน preset ไม่แก้ User.db ต้นทาง
และอย่าใช้ `--all-timelines` หรือ `--orientation` สำหรับคำขอ current timeline
เพราะ orientation ที่ไม่ระบุ timeline ขยาย scope ไปทุก timeline ในโปรเจกต์

## 4. โหลด preset: native API กับ database workaround

บน Resolve Studio **21.1.0.17** ที่ตรวจจริง ไม่มี public Python method
โหลด Subtitle track preset; `LoadBurnInPreset`, `LoadUserPreferencesPreset`
และ `LoadRenderPreset` ไม่ใช่ตัวแทน ตรวจ build/API ใหม่ก่อนสรุปกับเวอร์ชันอื่น
probe method ด้วย `name in dir(obj)` ไม่ใช้ `hasattr` ซึ่งให้ผลบวกปลอม

`scripts/load_subtitle_preset.py` ใช้ Python scripting API สำหรับ save/close/reopen
แต่ **ใช้ SQLite สำหรับเปลี่ยน style**: คัดลอก bytes ของ named preset จาก
`SM_User.FieldsBlob / SubtitlePresetsBA` ไปเฉพาะ keyed value `EffectFiltersBA`
ใน `Sm2TiTrack.FieldsBlob` (`Type=2`) ห้ามบอกว่าเป็น native preset API

Permission ให้ใส่ซับ/จัดฟอนต์/รัน Python ไม่ใช่ permission แก้ฐานข้อมูล
ขอ **explicit database-write approval** หลังอธิบายสำรอง/ปิด/เปิดโปรเจกต์
ตรวจ dry-run target IDs และจำนวน tracks; helper เปลี่ยนทุก subtitle track ของ
selected timeline ถ้ามีหลาย tracks แต่อนุมัติเพียง track เดียวให้หยุด ไม่ใช้ helper ทั้งก้อน

เมื่ออนุมัติ exact targets และ source preset แล้ว:

```bash
python scripts/load_subtitle_preset.py --preset "<exact-approved-name>" --user-db "<discovered-source-User.db>" --timeline "<exact-target-timeline-name>" --backup-dir "<approved-scratch-backup-directory>" --apply
```

ตรวจ no-op ถ้า style bytes ตรงแล้ว มิฉะนั้น:

1. บันทึก exact before snapshot ตามข้อ 1; SaveProject และตรวจ verified DRP
   ที่ไม่ว่างและอ่าน archive ได้ก่อน SQL (helper ตรวจแค่ existence/size ของ DRP)
2. ปิด project สำเร็จและตรวจว่า target project ไม่เปิดอยู่ ห้าม patch open database
3. ทำ SQLite backup ของ database ที่ปิดแล้ว ตรวจ integrity และ exact target rows
4. helper เขียน transaction เดียว เฉพาะ style key ของ target subtitle rows;
   ห้ามเปลี่ยน non-style keys/source clips/video/audio หรือเปิด database อื่นแทน
5. เปิด project เดิมกลับ คืน active timeline/playhead/page, SaveProject และ readback
   หาก reopen/verify ล้มให้รายงาน blocker กับ backup paths อย่าประกาศว่าจบ

## 5. Verification และ handoff

helper ยืนยัน exact style bytes, จำนวน subtitle tracks และ **cue counts**
แต่ยังไม่ตรวจ text/start/end ทุก cue, video/audio coverage, Media Pool folder
หรือภาพ Viewer ให้ agent ตรวจเพิ่มทุกครั้ง:

- ทุก cue text และ absolute start/end เท่ากับ before snapshot
- video/audio IDs/ranges/source trims และ subtitle count ไม่เปลี่ยน
- resolution, timeline FPS, playback FPS, track enabled/locked/names ไม่เปลี่ยน
- ทุก approved target track มี EffectFiltersBA ตรงกับ **source preset bytes**
  ไม่เทียบ FieldsBlob ทั้งก้อน และไม่แปลง QFont pointSize เป็น Inspector Size
- คืน original project/timeline, playhead/page และ Media Pool folder
  `ProjectManager.GetCurrentFolder()` เป็น Project Manager folder ไม่ใช่
  `MediaPool.GetCurrentFolder()`; ต้องคืน Media Pool folder แยกต่างหาก
- ตรวจ Viewer screenshot ด้วย `computer_use` + `vision_analyze` หรือ burn-in
  render ที่อนุมัติแล้ว: caption visibility, readability, HUD/avatar overlap
  native still export อาจไม่แสดง subtitle overlay จึงใช้พิสูจน์ซับไม่ได้
- บันทึกผล/backup paths และบอกสิ่งที่ยังไม่ได้ตรวจ แยก “inserted”, “style bytes
  match”, “visual QC” และ “listening/transcription QC” ไม่รวมเป็น verdict เดียว

ก่อน apply ทดสอบ helper offline ผ่าน `terminal`:

```bash
python -m unittest discover -s tests -p test_load_subtitle_preset.py -v
```

Tests นี้ทดสอบ parser/exact database rows บน fixtures ไม่ได้เชื่อม Resolve
และไม่เป็นหลักฐาน live verification ของโปรเจกต์ที่จะทำครั้งถัดไป
