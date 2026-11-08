# Changelog

## v0.17.38 — จัด Timeline น้ำท่วม Aomi-mama วันละโฟลเดอร์

### รายละเอียด
- ลบ Timeline เดิมทั้ง 21 อันในโปรเจกต์ `น้ำถ่วม-2026` (สำรอง .drp ก่อนลบ) แล้วทำใหม่ 6 วัน วันละ 1 โฟลเดอร์ใน Media Pool เหลือเฉพาะ Timeline สุดท้าย; ตรวจย้อนกลับซูม ภาพประกอบ และแทร็กเดิมผ่านทุกวัน
- บันทึกกฎใน OPERATING-NOTES: ตั้งโฟลเดอร์ปัจจุบันก่อนสร้าง/นำเข้า/duplicate timeline และตั้งชื่อไฟล์ DRT ใหม่ทุกครั้งที่ทำซ้ำ

## v0.17.37 — Timeline อัปเดตน้ำท่วม Aomi-mama ครบ 6 วัน

### รายละเอียด
- สร้าง Timeline อัปเดตน้ำท่วม Aomi-mama ครบ 6 วัน (29-09 ถึง 22-10) ในโปรเจกต์ `น้ำถ่วม-2026`: คลิปเต็มไม่ตัดช่วงเงียบ มี hook, การ์ดวันที่, VTuber Zoom และภาพประกอบ HyperFrames; render preview และ QC ภาพผ่านทุกวัน
- แก้ `scripts/asr_words_th.py` ให้ใช้กับ PyAV 19 ได้ (ถอดรหัส WAV เอง) และหา DLL CUDA จาก pip wheel ได้ พร้อมเทสต์ใหม่
- house-style: ไม่ตัดช่วงเงียบ เว้นแต่ผู้ใช้สั่ง
- บันทึกเลย์เอาต์และกรอบซูมของช่อง Aomi-mama และกับดักใหม่ 4 ข้อใน OPERATING-NOTES

## v0.17.36 — Bunny Girl ep6 ปกคลิป

### รายละเอียด
- Bunny Girl ep6: ทำปก 16:9 และ 9:16 (hook "แต่งชุดยังไง?" + Bunny Girl, ภาพอวาตาร์ 13.0 วิ) แบบเดียวกับ ep4/ep5 บันทึกในโฟลเดอร์ Thumbnail

## v0.17.35 — Bunny Girl ep6 แก้ตาม QC และแนวตั้ง

### รายละเอียด
- Bunny Girl ep6: แก้ตามที่ผู้ใช้สั่งทีละจุดจนผู้ใช้ยืนยันว่าโอเคทั้งหมด (ลบคำกระแทก 6 จุดพร้อมเสียง pop, เพิ่ม/ย้ายการ์ดรูปประกอบไปมุมขวาบน, การ์ดรวม 7 ชิ้น, ลดขนาดรายการท้ายคลิป, เปลี่ยนหัวข้อการ์ด INTRO, เพิ่มซูม VTuber 2 ช่วง)
- ทำแนวตั้ง 9:16 `Timeline 1_9x16_mitr`: ครอปที่หน้า ซูม 1.1x 13 ช่วง กราฟิกแนวตั้ง 10 ไฟล์ ซับ `Mitr-short-001` ทุก track ตรงกับต้นฉบับ (ยังไม่ render รอผู้ใช้ QC)
- บันทึกวิธีทำงานแบบแก้ทีละจุดเร็วๆ ไม่ render ทดสอบ

## v0.17.34 — Bunny Girl ep6 สติกเกอร์กระต่ายง่วง

### รายละเอียด
- Bunny Girl ep6: เปลี่ยนภาพสติกเกอร์ "กระต่ายง่วง" เป็นภาพกระต่ายหูตกหลับตา (Zzz) และเอาคำกระแทก "พับลง = ง่วงนอน" ออกพร้อมเสียง pop ตามที่ผู้ใช้สั่ง; สลับ `ch02.mov` เป็น `ch02b.mov` ที่ตำแหน่งเดิม track อื่นไม่เปลี่ยน
- พบว่า render เต็มล้มที่ 00:00:17:10 จาก zoom clip ที่ถูกยืดหัว (กับดัก row 77) รอผู้ใช้อนุมัติให้สร้าง track ซูมใหม่

## v0.17.33 — Bunny Girl ep6 การ์ด INTRO ขึ้น Timeline หลัก

### รายละเอียด
- Bunny Girl ep6: ย้าย `Timeline 1_intro_wipe` (มีการ์ด INTRO "ครบเซต 7 ชิ้น") ขึ้นเป็น `Timeline 1` ตามที่ผู้ใช้อนุมัติ; เหลือ timeline เดียว ทุก track ตรงกับก่อนเปลี่ยนชื่อ; จุดย้อนกลับ `pre_promote_intro.drp`

## v0.17.32 — Bunny Girl ep6 การ์ดเปลี่ยนฉาก INTRO

### รายละเอียด
- เพิ่มการ์ดเปลี่ยนฉาก INTRO "ครบเซต 7 ชิ้น" ใน Katy404 Bunny Girl ep6 พร้อมช่องเงียบ 1.6 วินาทีที่ 00:00:16:27 และเสียง whoosh
- สร้างเป็น Timeline ใหม่ `Timeline 1_intro_wipe` โดย `Timeline 1` ไม่ถูกแตะ และตรวจเทียบแล้วมีความต่าง 0 รายการ (ส่วนเพิ่มคือฟิลเลอร์ การ์ด และ whoosh เท่านั้น)
- บันทึกกับดัก DRT: คลิปที่เริ่มที่ source frame 0 จะมีแท็ก `<In>` ว่าง (ไม่ใช่ "0") ต้องตีความว่าเป็น 0
- render ทดสอบ `Bunny Girl ep6_POP_intro_test_2026-11-08.mp4`: 8180 เฟรม, -15.9 LUFS, peak -0.8 dBFS, ไม่มีเฟรมดำ, ช่องว่างใต้การ์ดเงียบ (-29.4 dB), ซับ Mitr ยังอยู่ครบ

## v0.17.31 — Bunny Girl ep6 ขึ้น Timeline หลัก

### รายละเอียด
- Bunny Girl ep6: ย้ายงานตัดต่อขึ้นเป็น `Timeline 1` (timeline เดียวในโปรเจกต์ ทุก track ตรงกับก่อนเปลี่ยนชื่อ) และลบ timeline สำรอง 3 อันตามที่ผู้ใช้สั่ง; จุดย้อนกลับ `pre_promote.drp`

## v0.17.30 — ตัดต่อ Bunny Girl ep6 (16:9 test)

### รายละเอียด
- Katy404 Bunny Girl ep6 "แต่งชุดบันนี่เกอร์ได้ยังไง": ทำ `Timeline 1_pop_mitr` แบบ Pop Kinetic 16:9 (การ์ด CHAPTER 01–07 ตามชิ้นชุด 7 ชิ้น, slam 47, การ์ดภาพ 10, ซูม 8 ช่วง, ซับไทย 125 cue `Mitr Font`, SFX/BGM) โดยไม่แตะ `Timeline 1`
- ซับไทยใช้ข้อความจาก Descript ตามที่ผู้ใช้สั่ง (หยุด Whisper ในเครื่อง) แล้วจับเวลาจากแผนที่ช่วงเงียบ
- render ทดสอบ `Bunny Girl ep6_POP_test_v2_2026-11-08.mp4`: 8084 เฟรม, -15.9 LUFS, peak -1.1 dBFS, ไม่มีเฟรมดำ, ช่องว่างก่อนการ์ด CHAPTER เงียบทุกช่อง
- house-style 0.3.2 / thai-subtitles-resolve 0.5.1: ใช้ Descript เป็นค่าเริ่มต้นแม้คลิปสั้น และลดเฉพาะ SFX ตัวที่ทำ peak เกิน

## v0.17.29 — Render ไฮไลต์ Hoshi_1489 ครบ 30 Timeline

### รายละเอียด
- Render และส่งออกคลิปไฮไลต์ Hoshi_1489 (2026-10-1) ครบทั้ง 30 Timeline ลงโฟลเดอร์ `G:\My Drive\Projects\Hoshi_1489\2026-10-1\footer`
- ใช้ DaVinci Resolve Python Scripting API ควบคุมการ Render ต่อเนื่องด้วย Preset `H.264 Master` (1920x1080@60fps)
- ตรวจสอบคุณภาพไฟล์ผ่าน QC ด้วย `ffprobe` ครบถ้วนทั้ง 30 ไฟล์ (ขนาดรวม 8.85 GB, ความยาวรวม 32 นาที 22 วินาที) ยืนยัน Video Stream (H.264), Audio Stream (AAC) และความยาวตรงกับ Timeline
- บันทึกบทเรียนการรอ Background Indexing สำหรับโปรเจกต์ขนาดใหญ่ (17.3 ชั่วโมง) และขั้นตอน Batch Render ตรงสู่ Google Drive ลงใน `docs/OPERATING-NOTES.md`

## v0.17.28 — ไฮไลต์ 30 Timelines สำหรับ Hoshi_1489 2026-10-1

### รายละเอียด
- วิเคราะห์ฟุตเทจดิบ 5 ไฟล์ของช่อง Hoshi_1489 รวม 17 ชม. 29 นาที จาก `G:\My Drive\Projects\Hoshi_1489\2026-10-1`
- คัดเลือกไฮไลต์ที่น่าสนใจ 30 คลิป (คลิปละประมาณ 36-96 วินาที) ครอบคลุม 3 หมวด: ช่วงเล่นเกม (gameplay), ช่วงสนุกสนาน (fun), และช่วง meme
- สร้าง 30 Timelines ใน DaVinci Resolve Studio โปรเจกต์ `hoshi-2026-10-1` (ใน Project Library `Google_drive`, โฟลเดอร์ `hoshi_1489`) ตามรูปแบบชื่อ `{ชื่อคลิป}-{ชื่อเกม}-vdo`
- ตรวจสอบความถูกต้องระดับเฟรม (Frame-accurate): 28 Timelines ตรงเป๊ะ 100%, 2 Timelines มีการปัดเศษของ Resolve 21.1 API ที่ source start 1 เฟรมแต่ความยาวคลิปตรงเป๊ะตาม Rule 55
- เพิ่มโปรไฟล์ช่อง `docs/channels/hoshi-1489.md` พร้อมบันทึกข้อค้นพบและข้อจำกัดของ Google Drive latency
- แก้ไข `scripts/highlight/briefs.py` ให้ใช้ `sys.base_prefix` เพื่อป้องกันการอ้างอิง `.venv` ใน subagent briefs
- ผ่านการทดสอบชุดใหญ่ 424 tests (รวม 74 highlight pipeline tests) 100%

## v0.17.27 — ปก Bunny Girl ep5 ได้รับอนุมัติ

### รายละเอียด
- Bunny Girl ep5: ผู้ใช้อนุมัติข้อความปก "วันแรกที่ใส่ชุด / Bunny Girl" ตามเดิม บันทึกในโปรไฟล์ Katy404 ว่าปกเป็นฉบับสุดท้ายแล้ว

## v0.17.26 — ปก Bunny Girl ep5

### รายละเอียด
- Bunny Girl ep5: ทำปก 16:9 และ 9:16 (ข้อความ "วันแรกที่ใส่ชุด" แดง + "Bunny Girl", เฟรม 0.4 วิ) เก็บไว้ที่โฟลเดอร์ Thumbnail ของตอน
- บันทึกในโปรไฟล์ Katy404: hook ที่ยาวกว่า ep4 ต้องลดขนาดตัวอักษร (128/142 px) ไม่งั้นชนหูกระต่ายและขอบจอ และ hyperframes 0.8.197 บันทึก snapshot ไว้ใน .hyperframes/artifacts/snapshots

## v0.17.25 — Bunny Girl ep5 แนวตั้ง

### รายละเอียด
- Bunny Girl ep5 แนวตั้ง: สร้าง Timeline 1_9x16_mitr (1080x1920) ซับ Mitr-short-001 ด้วย drt_clone_subtitle_style, render ทดสอบ 2440 เฟรม -15.6 LUFS ไม่มีเฟรมดำ
- แก้ drt_clone_subtitle_style ให้แปลง --workdir เป็น path เต็ม (Timeline.Export ล้มเหลวเมื่อได้ path แบบ relative)
- skill resolve-mitr-subtitle-presets: ระบุไฟล์ DRT อ้างอิงของ Mitr Font (16:9) และ Mitr-short-001 (9:16)

## v0.17.24 — ใส่ฟอนต์ซับ Mitr โดยไม่ปิด Resolve

### รายละเอียด
- เพิ่มสคริปต์ scripts/drt_clone_subtitle_style.py (พร้อม test): ใส่สไตล์ซับแบบ track เช่น Mitr Font โดย clone track จาก DRT อ้างอิงแล้ว import เป็น timeline ใหม่ Resolve เปิดค้าง ไม่เขียน Project.db
- บันทึกว่า MCP timeline_ai set_subtitle_preset ใช้ได้เฉพาะ preset แบบ animation จึงปฏิเสธ Mitr Font ("No animation preset") ใน house-style และ skill resolve-mitr-subtitle-presets
- Bunny Girl ep5: สร้าง Timeline 1_pop_mitr ซับเป็น Mitr Font ทุก track/gain/fade ตรงกับ Timeline 1_pop, render ทดสอบ 2440 เฟรม -15.6 LUFS ไม่มีเฟรมดำ

## v0.17.23 — Bunny Girl ep5 และกฎ ASR บน GPU ที่ไม่ว่าง

### รายละเอียด
- บันทึกงาน Bunny Girl ep5 "วันแรกที่ตัดสินใจว่าจะใส่ชุดบันนี่เกอร์" ในโปรไฟล์ Katy404: Timeline 1_pop (ซูม 6 ช่วง, Pop Kinetic 3 ส่วน, ซับ 48 cue, SFX/BGM) และผล render ทดสอบ 2440 เฟรม -15.6 LUFS peak -1.0 dBFS ไม่มีเฟรมดำ
- เพิ่มกฎใน OPERATING-NOTES: เมื่อเกม/OBS ใช้ GPU เกือบเต็ม ให้รัน faster-whisper บน CPU int8 พร้อม HF_HUB_OFFLINE=1
- เพิ่มกฎใน OPERATING-NOTES: heredoc ของ Bash tool เปลี่ยน backslash-n เป็นขึ้นบรรทัดจริง ให้ใช้ chr(92) หรือ Edit tool

## v0.17.22 — แก้อ้างอิงสคริปต์ Sakuyako ที่หายไป

### รายละเอียด
- `docs/channels/sakuyako-cheris.md`: ระบุว่าสคริปต์ `sk06_bands.py`, `sk06_9x16_layoutA.py`, `sk06_layoutA_qc.py` เป็น scratch ครั้งเดียวที่ไม่ได้เก็บไว้ (ไม่มีในเครื่องและไม่เคย commit)
- `test_channel_profiles` ผ่านครบ 3 ตัว; `test_skill_bundle` ผ่าน

## v0.17.21 — นำ skill เข้าโปรเจกต์ + กฎอัปเดต skill เดิม

### รายละเอียด
- นำ skill ที่เขียนเองเข้าโปรเจกต์ 5 ตัวจาก `~/.agents/skills`: `katy404-canva-thumbnails`, `kt404-youtube-upload`, `sfx-library-manager`, `sfx-story-analyzer`, `subtitle-analyzer`
- รวมกฎที่ไม่ซ้ำของ `davinci-resolve-workflow` เข้า `resolve-mcp/references/target-resolution.md` (resolve-mcp 0.4.0) แทนการสร้าง skill ซ้ำ
- `project-learning` 0.2.0: skill ต้องอยู่ใน `.agents/skills` ของ repo เท่านั้น; ถ้ามี skill เดิมครอบคลุมให้อัปเดตตัวเดิมและเพิ่ม `version` ก่อนคิดสร้างใหม่; ก่อนลบโฟลเดอร์ที่ gitignore ให้ค้นการอ้างอิงก่อน (AGENTS.md เพิ่มกฎเดียวกัน)
- `verify_skill_bundle` รู้จักลิงก์ `references/` ข้าม skill ของ HyperFrames และลิงก์โฟลเดอร์ ทำให้ test validation 3 ตัวที่เคยพังผ่านแล้ว
- test QC เสียง/ซับของ Armigon ข้ามอัตโนมัติเมื่อไฟล์หลักฐานใน `.agents/teamwork` (gitignore) ไม่มีอยู่
- ยังเหลือ test ที่พังมาก่อนงานนี้ 1 ตัว: `docs/channels/sakuyako-cheris.md` อ้าง `sk06_bands.py` ที่ไม่มีใน `scripts/`

## v0.17.20 — ติดตั้ง AutoHarness

### รายละเอียด
- ติดตั้ง AutoHarness v0.1.0 (aiming-lab/AutoHarness) ใน `.venv` ของ repo ทดสอบ `autoharness check` แล้วบล็อก `rm -rf /` เป็น critical ได้จริง ยังไม่ติดตั้ง hook ของ Claude Code
- `.gitignore` เพิ่ม `audit.jsonl` เพราะ `autoharness check` เขียน audit log ลงโฟลเดอร์ที่รันทุกครั้ง

## v0.17.19 — Aomi-mama ปกขึ้น Drive

### รายละเอียด
- Aomi-mama 2026-10: คัดลอกปก 12 ใบและ manifest ขึ้น Google Drive `Projects/Aomi-mama/2026-10/covers/` (ตรวจ hash ตรงทุกไฟล์)

## v0.17.18 — Aomi-mama ปกคลิป 12 ใบ

### รายละเอียด
- Aomi-mama 2026-10: ทำปกครบ 12 ใบ (แนวนอน 6, แนวตั้ง 6) ข้อความจาก subtitle จริงของแต่ละคลิป
- โปรไฟล์ช่อง: บันทึกที่อยู่ไฟล์ปก โมเดลที่ใช้ และท่าที่ถือเครื่องเกม (ใช้กับคลิปเกมเท่านั้น)
- OPERATING-NOTES: เครื่องนี้ Pillow ไม่มี RAQM วางสระ/วรรณยุกต์ไทยผิด ให้ใช้ Chrome headless วาดข้อความปก

## v0.17.17 — Aomi-mama คลิปแนวตั้ง 6 อัน

### รายละเอียด
- Aomi-mama 2026-10: สร้างคลิปแนวตั้ง `<ชื่อ>_9x16` ครบ 6 timeline (1080x1920) ต้นฉบับไม่เปลี่ยน ตรวจ render ครบทุกเฟรม
- `load_subtitle_preset_auto.py` ใส่ `--timeline` ซ้ำได้หลายอัน โหลด Subtitle preset หลาย timeline โดยปิดเปิด Resolve รอบเดียว พร้อม test ใหม่
- โปรไฟล์ช่อง Aomi-mama: บันทึกเลย์เอาต์แนวตั้ง (คอมเมนต์บน/อวาตาร์ล่าง, ฉากห้องนอนใช้ track Reframe ตัดช่วงตามตำแหน่งหัว) และ GIF/ภาพประกอบใช้ preset `short`
- house-style: แนวตั้งให้ GIF และภาพประกอบใช้ video preset `short` แม้ทับหน้า (ผู้ใช้ยืนยัน)
- OPERATING-NOTES: SmartReframe ผ่านสคริปต์ไม่มีผล, ตำแหน่งซับแบบ track style แก้ผ่าน MCP ไม่ได้, Resolve ที่เปิดใหม่อัตโนมัติอาจไม่ตอบ scripting จนกว่าจะปิดจริง

## v0.17.16 — KT404 Highlights อัปเดต timeline หลัก 48 อัน

### รายละเอียด
- KT404 Highlights 2026-10: ตัดต่อครบ 48 timeline (ซับ Mitr Font, VTuber Zoom, GIF/SFX/BGM) และอัปเดตเป็น timeline หลักแล้ว ลบ timeline ต้นฉบับดิบกับสำรอง (`_bak`, `_edit_subs`) ตามที่ผู้ใช้สั่ง ตรวจแล้วทั้ง 48 มีครบ V1–V3, A1–A3 และซับ
- บันทึกวิธีแก้ peak: peak ที่ยังเกิน 0 dBTP หลังลด gain ทั้ง timeline มาจาก SFX ที่วางทับเสียงพูด จึงลดเฉพาะ SFX ที่ตรงจุด peak ไว้ใน skill `resolve-audio`
- บันทึกว่า SaveProject บนโปรเจกต์ใหญ่ใน Google Drive ใช้เวลาราว 30–60 วินาทีต่อครั้ง และ Windows ขึ้นว่า "ไม่ตอบสนอง" แม้งานยังเดินอยู่
- บันทึกเรื่องแถบดำด้านล่างของแต่ละสตรีมกับกรอบซูม, การโคลนสไตล์ซับผ่าน DRT, การหยุด render อย่างปลอดภัย และวิธีแก้ helper ล่ม
- `apply_enrichment_d22.py` ใช้คลิปใน media pool ซ้ำและ import ไฟล์ละครั้งเดียว พร้อมเทสต์ใหม่ 3 เคส

## v0.17.15 — Aomi-mama อัปเดตไฟล์หลัก

### รายละเอียด
- อัปเดตไฟล์หลักของโปรเจค aomimama-2026-10: ลบ timeline ต้นฉบับ 6 อันและ `_archived_v02` แล้วเปลี่ยนชื่อสำเนาที่ตัดต่อแล้วเป็นชื่อเดิม ตรวจแล้วทุก track ไม่เปลี่ยน
- ย้ายไฟล์สำรอง .drp/.db และไฟล์ render QC ของงานนี้ 76 ไฟล์ไป Recycle Bin (ยังกู้คืนได้)
- OPERATING-NOTES: เพิ่มกฎลบ timeline ด้วย `MediaPool.DeleteTimelines` เพราะ MCP `delete_timeline` สร้าง `_archived` ใหม่ทุกครั้ง

## v0.17.14 — Aomi-mama ภาพประกอบครบ 5 คลิป

### รายละเอียด
- ใส่ภาพประกอบ Noto Emoji 3D 14 ภาพใน 5 คลิปของโปรเจค aomimama-2026-10 (กิน 3, เสื้อผ้า 3, ยุง 2, บอส 3, ซิม 3) แล้ว render QC ผ่านครบ ไม่มีเฟรมดำ ความยาวตรง timeline
- โปรไฟล์ช่อง Aomi-mama: บันทึกตำแหน่งภาพประกอบตามเลย์เอาต์ (ซ้ายบนปกติ, ขวาบนเมื่ออยู่ในช่วงซูมที่อวาตาร์อยู่ซ้าย)

## v0.17.13 — Aomi-mama 2026-10 ครบ 6 คลิป

### รายละเอียด
- ตัดต่อครบชุด 5 timeline ที่เหลือของโปรเจค aomimama-2026-10 (สำเนา `_edit`): ซับไทย Mitr Font, VTuber Zoom, GIF, SFX, BGM; render QC ครบ 5 คลิป ไม่มีเฟรมดำ, ความยาวตรง timeline
- บันทึกกฎใหม่ใน OPERATING-NOTES: กู้งาน preset ซับเมื่อ Resolve เปิดกลับไม่ขึ้น, ต้องเช็คเลย์เอาต์ทุกคลิปก่อนตั้งกรอบซูมและตำแหน่ง GIF, เสียงที่ยาวเกิน timeline ทำให้มีเฟรมดำท้าย render
- โปรไฟล์ช่อง Aomi-mama: บันทึก 2 เลย์เอาต์ (หน้าคอมเมนต์ / ฉากห้องนอน) พร้อมค่ากรอบซูมและ Pan ของ GIF
- `apply_enrichment_d22.py`: รับ `fps` จากแผน และปฏิเสธ SFX ที่จะยาวเกินท้าย timeline ตั้งแต่ dry run พร้อม test ใหม่

## v0.17.12 — KT404 Highlights ซับ Mitr Font

### รายละเอียด
- โหลด Subtitle preset `Mitr Font` ลง timeline นำร่อง KT404 Highlights (`_vdo_edit`, 55 cue) ตามที่ผู้ใช้อนุมัติ; dry run ยืนยัน `already_matches=True`, gain/ซับ/track อ่านกลับไม่เปลี่ยน
- render ทดสอบ v2 ซับ burn-in 7052 เฟรม true peak -1.0 dBFS ไม่มีเฟรมดำ ซับอ่านได้บนฉากหิมะ
- บันทึกวิธีแก้เมื่อ Resolve กลับมาค้างที่ Project Manager หลังแพตช์ preset: ใช้ `resolve_recover.py` แล้ว dry run ซ้ำ ไม่แพตช์ซ้ำ

## v0.17.11 — KT404 Highlights งานนำร่อง

### รายละเอียด
- บันทึกงานนำร่อง KT404 Highlights 2026-10 (บอสกับหมากับกระสุน-Soul Walker): ซับไทย 55 cue, VTuber Zoom 5 ช่วง, GIF 5, SFX 9, BGM 1 บนสำเนา `_vdo_edit`; ต้นฉบับไม่แตะ
- บันทึก layout อวาตาร์มุมขวาล่างของโปรเจคนี้ (window top 0.545 / bottom 1.0 / cx 0.77) และระดับเสียงต้นทาง -25.7 LUFS
- เพิ่มกฎคัด GIF: ใช้เวลาเล่นจริง ≥1.5 วิ (ไม่ใช่จำนวนเฟรม/25) และห้ามใช้ GIF ภาพคนจริง `Reaction - Laughing Pointing.gif`

## v0.17.10 — บันทึกบทเรียนงานไฮไลต์ Katy404 2026-10

### รายละเอียด
- บันทึกการเรียนรู้และอัปเดตโปรไฟล์ช่อง Katy404 2026-10 (48 timeline หลัก + 3 timeline สำรอง _bak และข้อเสนอ 342 ช่วง)
- เพิ่มกฎการทำงานใหม่ใน docs/OPERATING-NOTES.md: ห้าม subagent เขียนไฟล์สคริปต์ช่วยลง %TEMP% เพื่อป้องกันการเขียนทับกัน, การปรับเกณฑ์ธงกระโดด !! แบบสัมพัทธ์, และการตรวจขยายขอบเขตท้ายคลิป +40 วิ
- บันทึกประวัติงานลงใน docs/highlight/wiki/wiki/log.md แบบ append-only
- รีเฟรช checksums ใน docs/skills-manifest.json และผ่านชุดทดสอบ highlight 74 รายการ

## v0.17.9 — รายงานงาน Katy404 2026-10 ฉบับเต็ม

### รายละเอียด
- เพิ่มรายงานภาษาไทยฉบับเต็มของงาน Katy404 2026-10 ที่ `work/highlight/Katy404/2026-10/REPORT.md`: ภาพรวม ขั้นตอน งานแต่ละ release รายการ 48 timeline พร้อมแนวคลิป ผลอ่านทั้งไลฟ์ ปัญหาและวิธีแก้ และสิ่งที่ยังไม่ได้ตรวจ

## v0.17.8 — อ่านทั้งไลฟ์ Katy404 ครบ 12 ไฟล์

### รายละเอียด
- Katy404 2026-10: ถอดเสียงทั้งไลฟ์ครบ 12 ไฟล์ (11 ไฟล์ใหม่ ใช้ GPU 42 นาที) และให้ reader 61 ตัวอ่านทั้งไลฟ์
- ได้ข้อเสนอ 342 ช่วง (ช่วงเงียบที่การคัดจากความดังไม่เจอ 248 ช่วง) ครอบคลุมคลิปที่อนุมัติไว้เดิม 37 จาก 48 คลิป สรุปช่วงเงียบที่ความมั่นใจ ≥ 0.5 จำนวน 27 ช่วงไว้ใน `work/highlight/Katy404/2026-10/whole_stream_proposals.md` ให้ฟังก่อน
- ข้อความถอดเสียงไทยยังเพี้ยนมาก (ความมั่นใจส่วนใหญ่ 0.3–0.5) ยังไม่มีคนดูช่วงใหม่ และไม่ได้แก้ timeline หรือ `review/<id>.json` ที่อนุมัติแล้ว
- แก้ brief ของ reader: ห้ามเขียนสคริปต์ช่วยลง `%TEMP%` หลังเจอ reader ที่ทำงานพร้อมกันใช้ชื่อไฟล์ซ้ำกัน; บันทึกตัวเลขและบทเรียนในสกิล `long-video-highlight-clipping`

## v0.17.7 — สกิลทางเข้าเดียว /highlight และคำสั่ง status

### รายละเอียด
- เพิ่มสกิลทางเข้าเดียว `highlight` (`/highlight`) หน้าเดียว มีผังขั้นตอน คำสั่งทีละขั้น ตัวอย่าง `job.json` และกฎรสนิยม ใช้ได้ทั้ง Claude Code, Codex และ Hermes; `AGENTS.md` ชี้มาที่สกิลนี้ก่อน
- เพิ่ม `pipeline.py status [ids]` (`scripts/highlight/status.py`) อ่านไฟล์อย่างเดียว แสดงตารางขั้นที่เสร็จต่อวิดีโอ และพิมพ์คำสั่งถัดไปคำสั่งเดียว รวมรายชื่อแพ็กที่ reader ยังไม่ส่ง และเตือนเมื่อวิดีโอมี `review/<id>.json` ที่อนุมัติแล้ว
- `fulltext`, `proposals`, `packets` รับ id วิดีโอได้ ทำทีละวิดีโอได้; เพิ่มตัวเลือก `READ_WHOLE_STREAM` ใน `job.json` (false = ใช้แค่การคัดจากความดัง)
- ทดสอบแบบ cold-start ด้วย agent ใหม่ที่ไม่มีบริบท: หาวิธีทำงานเจอเองจาก `AGENTS.md` และวางลำดับคำสั่งถูก; แก้ 3 จุดที่มันเจอ (ไม่มีกฎตอนทำวิดีโอที่อนุมัติแล้วซ้ำ, status เลือกวิดีโอไม่ได้, ไม่ได้บอก `WORK_DIR` และวิธีรันเบื้องหลัง)
- เพิ่มเทสต์ 7 ข้อใน `tests/highlight/test_status.py` (เทสต์ไฮไลต์ผ่านทั้งหมด 74 ข้อ)

## v0.17.6 — ให้ agent อ่านทั้งไลฟ์เพื่อหาช่วงน่าสนใจ

### รายละเอียด
- เพิ่มขั้น `pipeline.py readpacks` (`scripts/highlight/readpack.py`) แบ่งข้อความทั้งไลฟ์เป็นแพ็กละ 30 นาที (ซ้อนกัน 2 นาที) พร้อมบรรทัดสัญญาณเสียงรายนาที `loud` / `jump` / `talk` / `!!` / `shortlist`
- เพิ่ม `pipeline.py readbriefs` และ `templates/reader_brief.md` ให้ subagent อ่านทีละแพ็กแล้วเสนอช่วงแบบ ปูเรื่อง → จุดพีค → ปฏิกิริยา พร้อมประโยคที่ยกมาตรงตัว
- เพิ่ม `pipeline.py proposals` (`proposals.py`) ตรวจข้อเสนอ (ลำดับเวลา ความยาว หมวด และประโยคที่ยกมาต้องมีอยู่ในแพ็กจริง) รวมตัวซ้ำ ติดป้าย `quiet` ให้ช่วงที่การคัดจากความดังไม่เจอ แล้วให้ reviewer อ่าน `<id>.proposals.md` ก่อน
- ทดลองกับ Katy404 v05: reader 3 ตัวเสนอ 23 ช่วง ผ่านการตรวจทั้งหมด เป็นช่วงเงียบ 18 ช่วง และครอบคลุมคลิปที่อนุมัติไว้เดิม 3 จาก 4 คลิป (พลาดฉากลาวาที่มีแต่เสียงเกม) ยังไม่ได้ให้คนดูช่วงใหม่ และไม่ได้แก้ timeline ใน Resolve
- แก้ชื่อไฟล์แพ็กให้ตรงกับที่ brief เขียน (`<id>-read-NN.md`) และเปลี่ยนเกณฑ์ `!!` ให้เทียบกับทั้งไลฟ์ (เกณฑ์ dB ตายตัวขึ้นแทบทุกนาที) เพิ่มเทสต์ 6 ข้อ

## v0.17.5 — ถอดเสียงทั้งไลฟ์และตัดตรงขอบประโยค

### รายละเอียด
- เพิ่มขั้น `pipeline.py fulltext` (`scripts/highlight/fulltext.py`) ถอดเสียงทั้งไลฟ์พร้อมเวลาระดับคำด้วย faster-whisper `large-v3-turbo` ก้อนละ 10 นาที ทำต่อจากจุดค้างได้ ได้ `transcripts/<id>.fulltext.txt` แบบ `[H:MM:SS] ข้อความ [ends วินาที]` ให้ agent อ่านทั้งไลฟ์
- `snap.py` รับ `in:<วินาที>` / `out:<วินาที>` เลื่อนจุดตัดที่อยู่กลางประโยคไปต้น/ท้ายประโยค ถ้าไม่มีประโยคจะใช้ช่วงเงียบเหมือนเดิม
- packet ของ reviewer ใช้ประโยคทั้งไลฟ์พร้อม `[ends]` เมื่อมีไฟล์ fulltext และ brief บอกให้อ่านก่อน/หลังหน้าต่างเพื่อหาจุดปูเรื่องและมุกจบ
- ทดลองกับ Katy404 v05 (84 นาที): ใช้เวลา 2.5 นาที ได้ 626 ประโยค; snap คลิปเดิม 4 คลิป เลื่อนต้นคลิป 2 คลิปเร็วขึ้น 3–9 วิ และท้ายคลิป 2 คลิปช้าลง 0.4–4 วิ เพื่อไม่ตัดกลางประโยค (ยังไม่ได้แก้ timeline ใน Resolve)
- เพิ่มเทสต์ 9 ข้อใน `tests/highlight/test_fulltext.py` และบันทึกวิธีใช้ในสกิล `long-video-highlight-clipping` และ `scripts/INDEX.md`

## v0.17.4 — ไฮไลต์ Katy404 2026-10 และถอดเสียงไทยคุณภาพสูง

### รายละเอียด
- งานไฮไลต์ Katy404 2026-10: inventory ฟุตเทจ 12 ไลฟ์ (~27.4 ชม.), เลือก 48 คลิป (gameplay 26, fun 13, meme 9) และสร้าง 48 Timeline ในโปรเจกต์ `KT404 Highlights 2026-10` (อ่านกลับแล้ว 46 ตรงทุกค่า, 2 เลื่อนต้นทาง 1 เฟรมแต่ความยาวตรง)
- `features.py` เขียนไฟล์เสียงเป็น `.part.wav` แล้วเก็บเฉพาะเมื่อความยาวตรงกับต้นฉบับ พร้อม retry (การอ่านพร้อมกันจาก Google Drive ตัดไฟล์สั้นโดยไม่แจ้ง error)
- เพิ่ม `DEMUX_WORKERS` ใน `job.json` และให้ `pipeline.py` แสดงชื่อไฟล์ไทย/อีโมจิได้บนคอนโซล Windows, ส่งข้อความ hint ให้ขั้น `briefs`
- `gpu_env.py` ใช้ CUDA DLL จาก `torch/lib` ได้เมื่อไม่มีแพ็กเกจ `nvidia-*`
- บรีฟผู้ตรวจคลิปใช้ Python ตัวจริงและใส่ `HIGHLIGHT_JOB` ในคำสั่ง snap; schema test อ่านจำนวนคลิปจาก `CLIPS_PER_VIDEO`
- เพิ่ม `scripts/highlight/verify_timelines.py` อ่านกลับทุก Timeline แบบ read-only พร้อมเทสต์ (เทสต์ highlight ผ่าน 52 ข้อ)
- ยืนยันจากภาพในเกมว่า v11 และ v12 เป็นเกม Soul Walker (SoulWorker) และบันทึกในโปรไฟล์ช่อง Katy404
- ถอดเสียงภาษาไทยทั้ง 48 คลิปใหม่ด้วย demucs (แยกเสียงพูด) + Typhoon ASR (Whisper เป็นตัวเทียบ) แก้ปัญหาข้อความวนซ้ำใน 7 คลิป และถอดเลยจุดจบ 40 วินาทีเพื่อเช็กว่าไฮไลต์หลุดหลังจุดจบไหม
- ขยาย 3 Timeline ที่จบก่อนถึงไฮไลต์: v09-03 (100→135 วินาที), v08-03 (98→115), v12-01 (102→118) อ่านกลับแล้วตรงตามแผน ของเดิมเก็บเป็น `_bak`
- บันทึกใน `OPERATING-NOTES` และสกิล `long-video-highlight-clipping`: วิธีถอดเสียงคุณภาพสูงสุด, การเช็กประโยคไฮไลต์เทียบจุดจบ, และกรณี Resolve วางต้นทางคลาด 1 เฟรมเพราะปัดเวลา (สร้างใหม่ไม่หาย)

## v0.17.3 — แก้ path MCP และเก็บกวาด environment ทดสอบ

### รายละเอียด
- แก้ `.mcp.json` ให้ชี้ไปยัง checkout `davinci-resolve-mcp` ที่ตรวจ remote, entrypoint และ Python environment แล้ว; อัปเดตและยืนยันเวอร์ชัน v4.18.4
- เพิ่มวิธีตรวจและแก้ path MCP โดยรักษา `env` และยืนยันการเชื่อมต่อหลังเริ่ม session ใหม่
- เพิ่มวิธีตรวจ root `.venv` และลบเฉพาะ environment ชั่วคราวที่งานปัจจุบันสร้าง พร้อมตรวจ path ก่อนลบ

## v0.17.2 — ทดสอบออก release ใหม่บนคอนโซล Windows

### รายละเอียด
- แก้ `scripts/release.py` ให้พิมพ์ตัวอย่าง changelog ภาษาไทยได้บนคอนโซล Windows โดยไม่ต้องตั้ง `PYTHONIOENCODING=utf-8` (ก่อนหน้านี้ dry run ล้มทันที) พร้อมเทสจำลองคอนโซล cp1252
- release นี้ออกด้วย `scripts/release.py --publish` ตรงๆ โดยไม่ตั้งตัวแปร encoding เพื่อทดสอบทั้งขั้นตอน commit, tag, push และ `gh release create`

## v0.17.1 — แก้สคริปต์ออก release กับข้อความภาษาไทย

### รายละเอียด
- แก้ `scripts/release.py` ให้อ่านผลลัพธ์คำสั่งเป็น UTF-8: ตอนออก v0.17.0 ข้อความ commit ภาษาไทยทำให้สคริปต์ล้มหลังสร้าง commit (ต้องทำ tag/push/release ต่อเอง) พร้อมเทสใหม่ใน `tests/test_release.py`

## v0.17.0 — รวมเครื่องมือคัดไฮไลต์ไลฟ์สตรีมเข้าโปรเจกต์

### รายละเอียด
- ย้ายเครื่องมือคัดไฮไลต์ไลฟ์สตรีม (mp4 เสียงไทย) จาก repo `agent-seacrh-virus-cut` มาไว้ที่ `scripts/highlight/` พร้อมเทส `tests/highlight/` (ผ่าน 44 เทส)
- เพิ่ม 10 สกิล: long-video-highlight-clipping, livestream-highlight-clipping, new-channel-job-setup, timeline-naming-convention, user-feedback-capture, resolve-project-folder-targeting, resolve-still-qc-capture, llm-wiki, resolve-smart-edit, vertical-video-reframing
- ย้ายวิกิความรู้คัดคลิปไปที่ `docs/highlight/wiki/`, เทมเพลตงานภาษาไทยไปที่ `docs/highlight/prompt-template.md` และข้อมูลงานเก่า 4 งาน (เฉพาะไฟล์เล็ก) ไปที่ `work/highlight/`
- เพิ่มหัวข้อขั้นตอนงานไฮไลต์ใน `AGENTS.md`, หมวด 9 ใน `scripts/INDEX.md` และกฎตั้งชื่อ Timeline ไฮไลต์ใน house-style
- repo เดิมไม่ถูกแก้; ไฟล์เสียง/เฟรม/ถอดเสียงขนาดใหญ่ไม่ได้ย้ายและถูก gitignore

## v0.16.23 — ปกคลิป Bunny Girl ep4

### รายละเอียด
- ทำปก Bunny Girl ep4: `Thumbnail/ep4_thumb_16x9.jpg` (1920x1080) และ `ep4_thumb_9x16.jpg` (1080x1920) ข้อความตามผู้ใช้ "ทำไมถึงใส่ชุด Bunny Girl?" (บรรทัดแรกแดง, Bunny ขาว / Girl? เหลือง, Mitr Bold ขอบดำ+ขาว), ภาพอวาตาร์เฟรม 0.8 วิ
- ตรวจสระ/วรรณยุกต์ไทยและภาพย่อ 320x180 / 180x320 แล้ว; บันทึกกับดักระยะบรรทัด (สระ ุ ใต้ "ชุด" ชนบรรทัดล่าง)

## v0.16.22 — ส่งมอบ Bunny Girl ep4 9:16

### รายละเอียด
- ส่งมอบ Bunny Girl ep4 9:16: `Bunny Girl ep4_9x16_FINAL_2026-11-01.mp4` จาก `Timeline 1_9x16` 1080x1920@60 ซับ burn-in, 9655 เฟรม, -15.7 LUFS, peak -1.5 dBFS, ไม่มีเฟรมดำ
- บันทึกการส่งมอบในโปรไฟล์ Katy404 (ไฟล์ส่งมอบปัจจุบัน: 16:9 FINAL_v2 + 9:16 FINAL; งานที่เหลือ: ปก)

## v0.16.21 — Bunny Girl ep4 FINAL_v2 และ 9:16 ทดสอบ

### รายละเอียด
- เรนเดอร์ 16:9 ใหม่เป็น `Bunny Girl ep4_FINAL_v2_2026-11-01.mp4` จาก `Timeline 1_pop` ที่ผู้ใช้แก้เอง: 9655 เฟรม, -15.7 LUFS, peak -1.5 dBFS, ไม่มีเฟรมดำ
- สร้าง 9:16 `Timeline 1_9x16` (กราฟิกแนวตั้ง 7 บท, ซูม 1.1x, ซับ `Mitr-short-001`) และเรนเดอร์ทดสอบ `Bunny Girl ep4_9x16_test_2026-11-01.mp4`: 1080x1920@60, 9655 เฟรม, -15.7 LUFS, ไม่มีเฟรมดำ
- บันทึกกับดัก: เรนเดอร์ Resolve พร้อม HyperFrames ทำให้ Fusion ล้ม, Resolve ค้างตอนโหลด preset ต้องให้ผู้ใช้ปิดเอง, gain ของ timeline อื่นเด้งกลับหลัง reload
- house-style: ผู้ใช้อยากได้วิธีโหลด preset ซับที่ไม่ต้องปิด Resolve ให้ลอง MCP `timeline_ai set_subtitle_preset` ก่อน

## v0.16.20 — ส่งมอบ Bunny Girl ep4 16:9

### รายละเอียด
- ส่งมอบ Bunny Girl ep4 16:9: `Bunny Girl ep4_FINAL_2026-11-01.mp4` เรนเดอร์จาก `Timeline 1_pop` 1920x1080@60 ซับ burn-in, 10210 เฟรม, -15.7 LUFS, peak -0.9 dBFS, ไม่มีเฟรมดำ
- บันทึกการส่งมอบในโปรไฟล์ Katy404 (ไม่ได้เปลี่ยนชื่อหรือ promote timeline; งานที่เหลือ: 9:16 และปก)

## v0.16.19 — ตัดต่อ Bunny Girl ep4 (ทดสอบ)

### รายละเอียด
- ตัดต่อ Bunny Girl ep4 "ทำไมถึงอยากใส่ชุดบันนี่เกอร์" บน `Timeline 1_pop` (ต้นฉบับ `Timeline 1` ไม่แตะ): ช่วงเงียบ 1.6 วิ + การ์ด CHAPTER 01–05, ซูม 7 ช่วง 1.35x, กราฟิก Pop Kinetic 7 บท, ซับไทย 188 cue preset `Mitr Font`, SFX 41 จุด, BGM ต่อสองท่อน
- เรนเดอร์ทดสอบ `Bunny Girl ep4_POP_test_2026-11-01.mp4` 10210 เฟรม 1080p60 ซับ burn-in, -15.7 LUFS, peak -0.9 dBFS, ไม่มีเฟรมดำ, ช่วงการ์ดเงียบทุกช่วง
- บันทึกโปรไฟล์ Katy404: ซับช่องนี้ใส่คำหยาบตามที่พูดจริง, ไอคอน `leotard` อ่านไม่ออกที่ขนาดการ์ดให้ใช้ `earband`, คำที่ต้องฟังยืนยัน 6 จุด
- skill `resolve-delivery`: เรนเดอร์ล้มที่ 0% แล้ว helper ยังล็อกไฟล์ปลายทาง ("Existing file can not be removed") ต้องเรนเดอร์ด้วยชื่อใหม่

## v0.16.18 — ปกคลิป เกมที่ชอบในปี 2026

### รายละเอียด
- ทำปกคลิป "เกมที่ชอบในปี 2026" ของ Armigon สองสัดส่วน คือแนวนอน 1920×1080 และแนวตั้ง 1080×1920 วางไว้ข้างคลิปใน `Z:/armigon/เกมโปรด 2026/`
- ใช้เฟรมจริงจากคลิป (วินาทีที่ 65) และข้อความ "เกมที่ชอบปี 2026 / MINECRAFT / ครบ 3 อันดับ?!" ตรวจด้วยตาที่ขนาดมือถือ ภาพขาวดำ และภาพเบลอแล้ว ไม่มีการแก้ Resolve
- บันทึกกับดัก: `hyperframes snapshot` ไม่ใช้ `--out` และเขียนภาพไว้ใน `.hyperframes/artifacts/snapshots/`

## v0.16.17 — ลบ timeline สำรองแนวตั้ง เกมที่ชอบในปี 2026

### รายละเอียด
- ลบ timeline สำรอง `FirstPass v2_illustrated_9x16_bak` ตามที่ผู้ใช้สั่ง หลังตรวจว่า 16:9 ต้นฉบับไม่เปลี่ยนและ timeline แนวตั้งหลักเป็นเวอร์ชันล่าสุด (ซับ 79 cue)
- บันทึกการลบและไฟล์ .drp ที่ใช้กู้คืนได้ลงโปรไฟล์ Armigon

## v0.16.16 — คลิปแนวตั้ง เกมที่ชอบในปี 2026

### รายละเอียด
- ทำคลิปแนวตั้ง 1080×1920 "เกมที่ชอบในปี 2026" (Armigon) ด้วย layout B: อวาตาร์ครึ่งล่าง แถบบนเบลอ กราฟิกข้าง 12 ชิ้นย้ายเข้าแถบบน ภาพเต็มจอ 2 ช่วงทำใหม่เป็นแนวตั้ง
- ซับยาว 10 บรรทัดที่ล้นขอบจอแนวตั้ง แบ่งเป็นบรรทัดสั้นเฉพาะเวอร์ชันแนวตั้ง (68 → 79 cue สไตล์เดิม) ผ่าน DRT ตรวจแล้วภาพ เสียง และ transform ไม่เปลี่ยน
- render แล้วมีซับฝังในภาพ 4,151 เฟรม 60 fps −15.8 LUFS ตรวจเฟรมแล้วว่าซับทุกบรรทัดที่แบ่งอยู่ในจอ
- แก้ `full_original_signature` ให้รองรับ Adjustment Clip ที่ซูมผ่าน Inspector (ไม่มี Fusion)
- บันทึกกฎตรวจความกว้างซับเมื่อทำ 9:16 จาก 16:9 ลง OPERATING-NOTES

## v0.16.15 — Adjustment Clip บน Video 3 เกมที่ชอบในปี 2026

### รายละเอียด
- เกมที่ชอบในปี 2026 (Armigon): สร้าง timeline `FirstPass v2_illustrated_focus_v3` ที่มี Adjustment Clip แบบ Inspector (Zoom 1.377) บน Video 3 ครบ 5 ช่วงตามคลิปที่ผู้ใช้วางเอง; ต้นฉบับไม่ถูกแก้ ตรวจ readback และ render 1 เฟรมต่อช่วงแล้ว
- บันทึกกับดัก: Adjustment Clip จาก Effects library ใน DRT เป็น `Sm2TiVideoClip` ไม่ใช่ `Sm2TiGenerator` จึงใช้ `drt_rebuild_focus_track` ไม่ได้ ต้องโคลน Element เอง
- house-style: เมื่อผู้ใช้วาง Adjustment Clip เองบน track ใด ให้โคลนคลิปนั้นบน track เดิม ไม่ใช้ Fusion Transform แทน

## v0.16.14 — ภาพประกอบ เกมที่ชอบในปี 2026

### รายละเอียด
- เพิ่มภาพประกอบ HyperFrames 14 ช่วงให้คลิป "เกมที่ชอบในปี 2026" (Armigon) บนสำเนา `FirstPass v2_illustrated` แทร็ก V2 `REACTIONS`: กราฟิกข้าง 12 + ภาพแฟนตาซีเต็มจอ 2 ตรงตามซับ
- ตรวจแล้ว: `illustration_reel.py` baseline/pilot/apply/verify ผ่าน, แทร็กต้นฉบับ (วิดีโอ 15 / เสียง 41 / ซับ 68) ตรง baseline, render QC 1920×1080 60 fps 4,151 เฟรม decode ไม่มี error มีซับครบทุกช่วง
- บันทึกกฎใหม่: เก็บ reel และ placements.json ไว้ข้างฟุตเทจ (`Z:/…/illustrations/`) แทน `.hermes/projects/` เพื่อกัน Media Offline

## v0.16.13 — Render แนวตั้ง ทำไมถึงมาเป็นวีทูปเบอร์

### รายละเอียด
- Render วิดีโอแนวตั้ง "ทำไมถึงมาเป็นวีทูปเบอร์" เต็มความยาว ซับ burn-in ที่ `Z:/armigon/Why Vtuber/FirstPass v2_illustrated_9x16.mp4`
- QC ผ่าน: 1080×1920 60 fps 9,195 เฟรมตรง Timeline, เสียง AAC stereo −16.1 LUFS / peak −1.1 dBFS, ตรวจ 12 เฟรมมีซับและ layout ถูกต้อง
- บันทึกผล render และคำสั่งไว้ในโปรไฟล์ Armigon

## v0.16.12 — แนวตั้ง ทำไมถึงมาเป็นวีทูปเบอร์

### รายละเอียด
- สร้าง Timeline แนวตั้ง `FirstPass v2_illustrated_9x16` (1080×1920, 60 fps) ของโปรเจกต์ "ทำไมถึงมาเป็นวีทูปเบอร์" ด้วย layout B; build ผ่าน readback ต้นฉบับไม่เปลี่ยน เสียงและซับ 146 ตรงเดิม
- เพิ่ม reel ภาพเต็มจอ 9:16 (novel/party) และ top plate ไว้ใน `Z:/armigon/Why Vtuber/illustrations/v916/`
- บันทึกสูตร Tilt/Zoom ของภาพนิ่งสี่เหลี่ยมจัตุรัสใน Timeline 9:16 ที่ยืนยันจากเฟรม render จริง และวิธีแปลงจาก Timeline สดที่ผู้ใช้แก้แล้ว
- แก้ path สคริปต์ scratch ในโปรไฟล์ Armigon ให้ผ่านการตรวจโปรไฟล์

## v0.16.11 — ย้ายสื่อโปรเจกต์ทำไมถึงมาเป็นวีทูปเบอร์

### รายละเอียด
- เพิ่ม `scripts/consolidate_project_media.py`: คัดลอกไฟล์ทุกตัวที่โปรเจกต์ใช้ไปไว้โฟลเดอร์เดียว แยกเป็น gif/sfx/bgm/subtitles/illustrations แล้ว relink และอ่าน File Path กลับทุกคลิป (สำรอง `.drp` ก่อน, ไม่ลบต้นฉบับ)
- โปรเจกต์ ทำไมถึงมาเป็นวีทูปเบอร์: คัดลอก 51 ไฟล์ไปที่ `Z:\armigon\Why Vtuber` และ relink สำเร็จ 49 ไฟล์; Timeline `FirstPass v2_illustrated` ใช้ 14 ไฟล์ ทั้งหมดอยู่ในโฟลเดอร์ใหม่และ online
- บันทึกใน OPERATING-NOTES: ย้ายสื่อให้ใช้วิธีคัดลอก (คลัง GIF/SFX/BGM ใช้ร่วมกับโปรเจกต์อื่น) และ `RelinkClips` คืนค่า False กับคลิป `.srt` ใน Media Pool บน 21.1.0.17

## v0.16.10 — Render ส่งมอบครบ 76 ไฟล์ พร้อมปกแนวตั้ง (Sakuyako 2026-06)

### รายละเอียด
- Render ส่งมอบโปรเจกต์ `2026-06-Sakuyako` ครบ 76 ไฟล์ `.mov` (H.264/AAC 30 fps, preset `H.264 Master`, ซับฝังในภาพ) ไปที่ `G:\My Drive\Projects\Sakuyako-Cheris\2026-06\vdo`: แนวนอน 38 ไฟล์ 1920×1080 และแนวตั้ง 38 ไฟล์ 1080×1920
- แนวตั้งทุกไฟล์เปิดด้วยปกแนวตั้งของคลิปนั้น 1 วินาที (30 เฟรม ไม่มีเสียง) แล้วจึงเริ่มเนื้อหา; แนวนอนไม่มีปก; Timeline ต้นฉบับไม่ถูกแก้ (ใช้สำเนาชั่วคราวแล้วลบทิ้ง)
- `scripts/p2_export_final.py`: เพิ่ม `--vertical-suffix`, `--cover-pattern` (`{name}`/`{stem}`) และ `--cover-bin` ให้ใช้กับชื่อ timeline/ปกแบบอื่นได้ ค่าเดิมไม่เปลี่ยน พร้อมเทสต์ใหม่
- ตรวจแล้ว: Resolve รายงาน Complete ครบ 76 job, `--verify` ผ่าน 76/76 (สตรีมภาพ+เสียง ขนาด ความยาวตรง timeline และเฟรมแรกแนวตั้งตรงกับปก SSIM ≥ 0.9); pilot ตรวจภาพแล้วว่าซับฝังในภาพทั้งสองแนว และวินาทีแรกของแนวตั้งเงียบ (-78 dB)
- บันทึกคำสั่งและผลในโปรไฟล์ช่อง Sakuyako และกฎรับมือเมื่อ `SaveProject` ล้มเหลวชั่วคราวใน `docs/OPERATING-NOTES.md`
- ข้อจำกัด: ตรวจซับด้วยภาพเฉพาะคู่ pilot (ไฟล์อื่นใช้การตั้งค่าเดียวกัน); pytest ยังมี 5 failed / 12 errors เดิมที่มีก่อนงานนี้ ไม่มีรายการใหม่

## v0.16.9 — ระบบหลักฐานเกม/ช่อง และรีวิวหลังตัดต่อ

### รายละเอียด
- เพิ่ม `scripts/channel_intelligence.py` สำหรับตรวจรายงานหลักฐานเกม/ช่องแบบ offline พร้อมเทสต์ และแถวใน `scripts/INDEX.md`
- เพิ่มขั้นตอนระบุเกม (`video-footage-review/references/game-identification.md`) และรีวิวหลังตัดต่อ (`resolve-video-enrichment/references/post-edit-review.md`) พร้อมอัปเดต skill `project-learning`, `resolve-video-enrichment`, `video-footage-review`
- `AGENTS.md`: เพิ่มวิธีแก้เมื่อพาธ MCP หาย และให้งานตัดต่อทำตาม `project-learning` + post-edit review ตั้งแต่ต้นงาน
- แก้พาธ `davinci-resolve` MCP ใน `.mcp.json` ให้ตรงตำแหน่งจริง และเพิ่ม `.codex/config.toml` สำหรับ Codex
- `.gitignore`: คง `.hermes/` ไว้ไม่ให้ไฟล์งาน/ภาพเข้า repo และเพิ่ม `.worktrees/`
- ตรวจแล้ว: pytest 325 passed (เพิ่มจาก 243), รายการที่ล้มเหลว 5 failed / 12 errors เป็นของเดิมทั้งหมด ไม่มีความล้มเหลวใหม่; commit ไม่มีไฟล์ภาพ/วิดีโอ/.drp/.hermes และไม่มี key
- ไม่ได้ commit: `.hermes/` (~5.7 GB ภาพ/รายงาน/backup) และสคริปต์ทดลอง `test_insert*.py` ที่รากโปรเจกต์ซึ่งลบ/สร้าง Timeline บน Resolve จริง

## v0.16.8 — ปกคลิปครบ 38 คลิป (Sakuyako 2026-06)

### รายละเอียด
- ทำปกคลิปโปรเจกต์ `2026-06-Sakuyako` ครบ 38 คลิป คลิปละแนวนอน 1920×1080 และแนวตั้ง 1080×1920 รวม 76 ไฟล์ JPG ใน `G:\My Drive\Projects\Sakuyako-Cheris\2026-06\vdo`
- ใช้ Template มินิมอลแบบเดียวที่ผู้ใช้อนุมัติ: ฉากเกมจริงจาก Timeline + มาสคอต `sk_04` + ข้อความไทย 2 บรรทัด (ชมพู/ขาว) ไม่มีของตกแต่งเพิ่ม
- ตรวจแล้ว: ขนาดภาพถูกต้องทุกไฟล์ ไม่เกิน 2 MB, ไฟล์บน Drive ตรงต้นฉบับ (sha256), ตรวจภาพครบไม่พบข้อความล้น/ชนมาสคอต/อวาตาร์ซ้ำ; ดึงเฟรมจาก Resolve แบบอ่านอย่างเดียวและคืน Timeline/playhead เดิมแล้ว
- บันทึกความชอบปกแบบมินิมอลใน `house-style`, รายละเอียด Template ในโปรไฟล์ช่อง Sakuyako และกฎ retry playhead ก่อน export ภาพนิ่งใน `docs/OPERATING-NOTES.md`
- รวม commit งาน Sakuyako ที่ค้างในเครื่อง (layout A, BGM, render, `backup_drp` absolute path) เข้ากับ `main`
- ข้อจำกัด: pytest ยังมี 5 failed / 12 errors ที่มีอยู่แล้วก่อนงานนี้ (ตรวจเทียบ baseline แล้ว ไม่มีความล้มเหลวใหม่); ไฟล์ปกเป็นงานส่งมอบบน Drive จึงไม่ได้ commit เข้า repo

## v0.16.7 — ภาพประกอบคลิปทำไมถึงมาเป็นวีทูปเบอร์

### รายละเอียด
- เพิ่มภาพประกอบ 21 ช่วงให้คลิป "ทำไมถึงมาเป็นวีทูปเบอร์" บนสำเนา `FirstPass v2_illustrated` (V2 `REACTIONS`): ภาพแฟนตาซีเต็มจอ 4 ช่วง + กราฟิกเคลื่อนไหวมุมซ้ายบน 17 ช่วง จาก reel HyperFrames ProRes 4444 alpha เดียว
- ตรวจแล้ว: ช่วงเฟรมทั้ง 21 ชิ้นอ่านกลับตรงแผน, track วิดีโอ/เสียง/ซับของต้นฉบับตรง baseline, เฟรม Resolve พร้อมซับทุกช่วงไม่ทับหน้า/เขาตัวละครและไม่ชนซับ
- บันทึกโปรไฟล์ช่อง Armigon และกับดักเวลา/ขนาดไฟล์ของ reel alpha ยาวใน OPERATING-NOTES

## v0.16.6 — 9:16 ครบ 85 Timeline และ render ทั้งหมด (Sakuyako)

### รายละเอียด
- สร้าง `_9x16` ครบ 85 Timeline ของ 2026-06-Sakuyako: เกมด้านบน chibi ด้านล่าง (ย่อ chibi ให้ซับอยู่ใต้ตัว) ตรวจภาพ/เสียง/ช่วงเวลา/ซับเทียบต้นฉบับผ่านทุก Timeline
- render 16:9 และ 9:16 ครบอย่างละ 85 ไฟล์ (มีเสียง + burn-in ซับ) ตรวจจำนวนเฟรมและเสียงด้วย ffprobe ผ่านทุกไฟล์ และย้ายไปไว้ใน Google Drive `2026-06/vdo` และ `vdo/9x16`
- บันทึกวิธีทำ 9:16 ที่ไม่ทำให้ Resolve 21.1.0.17 ค้าง (ตั้งขนาดบน Timeline ว่างก่อน, ใส่ซับก่อนภาพ) และกับดักเรื่อง render preset ค้างคิว

## v0.16.5 — VTuber Zoom ครบ 85 Timeline (Sakuyako)

### รายละเอียด
- แก้ VTuber Zoom ที่ใหญ่ผิดปกติใน `ช็อตฮา  โอ้ย-vdo` (Sakuyako) และสร้างคลิปใหม่ให้เหลือ Fusion comp เดียวต่อคลิป
- เพิ่ม VTuber Zoom ให้ครบ 85 Timeline ของ 2026-06-Sakuyako: เลือกจุดซูมจากซับ (Timeline ที่ไม่มีซับใช้ความดังของเสียงแทน) วัดตำแหน่ง chibi แยกตามแต่ละ source และจัด chibi ไว้ทางซ้ายเพื่อไม่ให้ซับตกบนตัว ผลตรวจ: ช่วง/comp/Transform/track เดิมผ่านทุก Timeline และดูภาพ still จาก Resolve ครบทุกคลิป
- `scripts/focus_qc_frames.py` เพิ่มตัวเลือก `--fps` (เดิมใช้ได้เฉพาะ 60 fps)
- บันทึกกับดัก API ของ 21.1.0.17 ใน skill และ OPERATING-NOTES: track enabled อ่านค่าได้เฉพาะ Timeline ปัจจุบัน, ลบ Fusion comp ไม่ได้, ค่า Fusion ถูกปัดเศษหลังเปิดใหม่, ExportProject ต้องใช้ path แบบเต็ม, Google Drive หลุดทำให้ Resolve ค้าง
- รวม commit ที่ push ไว้ก่อนหน้า: ปก Armigon, helper ทำ inventory จุด focus จากซับ และแผน pilot ของ VTuber zoom

## v0.16.4 — ลบ Timeline สำรองและเพิ่มเครื่องมือลบ archive

### รายละเอียด
- เพิ่ม `scripts/delete_archived_timelines.py` สำหรับลบ timeline `<ชื่อ>_archived_vNN` ที่ MCP สร้างอัตโนมัติ: dry-run ก่อน, เทียบคลิปภาพ/เสียงกับ timeline หลัก, สำรอง `.drp` แล้วลบด้วย `--confirm` และอ่านกลับ พร้อม test
- ลบ timeline สำรอง `_archived_v01` 20 อันในโปรเจกต์ `2026-06-Sakuyako` (ภาพ/เสียงตรงกับ timeline หลักทุกอัน) เหลือ timeline หลัก 85 อัน ซับยังตรง SRT 81/85 ตามเดิม

## v0.16.3 — ซับ Typhoon และแก้ชื่อเชอรี่ทั้งโปรเจกต์ Sakuyako

### รายละเอียด
- นำข้อความ Typhoon ที่ตรวจคำแล้วเข้า native Subtitle track 11 Timeline ของ `2026-06-Sakuyako` แทนซับร่างเดิม และอ่านกลับตรงทุก cue
- แก้ชื่อสตรีมเมอร์เป็น "เชอรี่" ใน 16 Timeline ที่ใช้ SRT เดิม (ASR เคยได้ยินเป็น ชนิด/เฉศนิท/ฉลิด/ชะลีด/ชิคกี้พาย) โดยไม่เปลี่ยนเวลา
- ผลรวม: ซับตรงกับ SRT 81/85 Timeline ต้นฉบับ; อีก 4 Timeline ไม่มีเสียงพูดของสตรีมเมอร์ (ไม่มีเสียง, เสียงพากย์เกม, เพลง)
- บันทึกวิธีถอดเสียงคลิปที่เสียงเกมกลบเสียงพูด (demucs + VAD + Whisper/Typhoon) ใน skill `thai-subtitles-resolve` และกฎการแทน subtitle track ใน `docs/OPERATING-NOTES.md`

## v0.16.2 — กู้ Resolve อัตโนมัติเมื่อปิดเองหรือค้าง

### รายละเอียด
- เพิ่ม `scripts/resolve_recover.py` ให้ agent กู้ DaVinci Resolve ที่ปิดเองหรือค้างได้เอง: เปิด Google Drive ใหม่เมื่อไดรฟ์ของ project library หาย, kill เฉพาะเมื่อ Resolve ค้าง, เปิด Resolve ผ่าน Explorer และเปิดโปรเจกต์เดิมให้ (ทดสอบจริงกับ `2026-06-Sakuyako` ได้ `RECOVER_OK`)
- เพิ่ม test `tests/test_resolve_recover.py` (5 ข้อผ่าน) และแถวใน `scripts/INDEX.md`
- บันทึกกฎใน `AGENTS.md`, `docs/OPERATING-NOTES.md` และ skill `resolve-session`: ผู้ใช้อนุญาตให้กู้ Resolve เองแล้ว, ถ้า SaveProject คืนค่า False ให้ตรวจไดรฟ์ library ก่อน, หลังเปิดใหม่ให้ตรวจผลโดยอ่านค่ากลับแทนการเชื่อค่าที่ setter คืนมา
- อัปเดตสถานะช่อง Sakuyako-Cheris: นำ SRT เข้า native Subtitle track แล้ว 78/85 timeline และอ่านกลับตรวจครบทุก cue

## v0.16.1 — วางระบบเรียนรู้และเผยแพร่ให้ทุก agent

### รายละเอียด
- ปรับ `AGENTS.md` และ `.agents/skills/project-learning/SKILL.md` ให้ทุก agent บันทึกบทเรียนลง skill/เอกสารที่ตรงงาน และทำ release หลังตรวจสอบงาน
- เพิ่ม `scripts/release.py` สำหรับ SemVer patch bump โดยปริยาย, ตรวจความสะอาดและซิงก์ของ branch/tag, ตรวจหัว changelog, preview ก่อนเผยแพร่ และเผยแพร่ GitHub Release เมื่อระบุ `--publish`
- ปรับ `refresh_skill_manifest.py` ให้คง checksum ที่ยังถูกต้องเมื่อ checkout แปลง LF/CRLF; บันทึกกฎใน `docs/OPERATING-NOTES.md` เพื่อไม่ให้ refresh เปลี่ยน hash ที่ไม่จำเป็น
- ลงทะเบียนเครื่องมือ release ใน `scripts/INDEX.md` และเพิ่ม unit tests สำหรับ release/preflight และ manifest checksum
- ผลทดสอบเฉพาะทาง: ผ่าน 11 tests; full suite: 236 passed, 23 skipped, 4 failed และ 12 errors จาก references/ไฟล์ QC ที่ขาดใน workspace
- ไม่ได้ทดสอบกับ DaVinci Resolve จริง; งาน Armigon/export ที่ค้าง staged ก่อนเริ่มและ config เฉพาะเครื่องไม่รวมใน release นี้

## v0.16.0

### Added
- เพิ่ม `scripts/drt_rebuild_focus_track.py` แทนที่ทุก clip บน Adjustment Clip track ที่ระบุชื่อใน DRT ด้วย clip ใหม่จาก template ตามช่วงที่กำหนด (`--create` สร้าง track ก่อน) ตรวจช่วงซ้อน, DbId ซ้ำ และเทียบ track อื่นแบบ byte ต่อ byte (ยกมาจากขั้น `rezoom` ของงาน Bunny Girl)
- เพิ่ม `scripts/rebuild_trimmed_zoom_clip.py` สร้าง zoom track ใหม่บน timeline ที่เปิดอยู่หลังตัดหัว timeline (คง Fusion Transform)
- เพิ่มชุดทดสอบ 12 รายการใน `tests/test_drt_rebuild_focus_track.py`

### Fixed
- `scripts/refresh_skill_manifest.py` และ `scripts/verify_skill_bundle.py` ไม่นับไฟล์ที่ gitignore (เช่น `scripts/scratch/*`) เป็นไฟล์ใน bundle อีกต่อไป และลบ skill declaration ที่ไม่มีโฟลเดอร์แล้ว (ก่อนหน้านี้ manifest พังทุกครั้งที่ไฟล์ scratch เปลี่ยน และ checkout ใหม่จะ verify ไม่ผ่าน); เพิ่ม `tests/test_bundle_git_ignored.py`

### Updated
- บทเรียนจากงาน "Bunny Girl คืออะไร" (Katy404, 2026-10-17) ใน `docs/OPERATING-NOTES.md`: ชื่อ timeline หลัง import DRT, endFrame ของ `AppendToTimeline` เป็น exclusive, วิธีต่อ BGM ให้วนที่ช่วงเงียบ, Adjustment Clip ที่ถูกยืดหัวแล้ว render ไม่ได้, InsertGenerator บน 21.1.0.17 และ SFX ทับกันบน track เดียว
- `house-style`: กราฟิก keyword ใน explainer ต้องใหญ่และเปลี่ยนตามคำพูด (ผู้ใช้เลือก Pop Kinetic)
- โปรไฟล์ `docs/channels/katy404.md`: สถานะ day 25 และ Bunny Girl (timeline, ค่า SFX/BGM ที่ผู้ใช้ยืนยัน, backup)
- `resolve-edit` และ `adjustment-focus.md` ชี้ไปที่เครื่องมือใหม่; ลงทะเบียนใน `scripts/INDEX.md`
- `scripts/check_mcp_update.py` รายงาน `BLOCKED` เมื่อ path ใน `.mcp.json` ไม่มี MCP อยู่จริง; `.mcp.json` ชี้ไปที่ `D:\davinci-resolve-mcp`

### Verified
- `python -m pytest -q` ผ่าน 227 passed, 22 skipped, 10 subtests; `python scripts/verify_skill_bundle.py` ผ่าน (errors ว่าง)
- เครื่องมือใหม่ทดสอบแบบ offline กับ DRT จำลองเท่านั้น ยังไม่ได้รันกับ Resolve จริง (logic เดียวกับขั้น `rezoom` ที่ render ผ่านในงาน Bunny Girl)

### Scope
- skill HyperFrames ที่ติดตั้งจาก upstream (`general-video`, `hyperframes*`, `media-use`, `skills-lock.json`) ไม่รวมใน release นี้ เพราะมี local reference ที่ verifier ยังหาไม่เจอ 18 รายการ

## v0.15.0

### Added
- เพิ่ม `scripts/prepare_edit.py` เตรียม offline intake แคชผล ffprobe สร้าง draft edit decisions นำผล caption lint เดิมมาใช้ซ้ำ และสร้าง contact sheet โดยไม่ต่อ Resolve และไม่แก้ footage ต้นฉบับ
- เพิ่ม `scripts/edit_workflow.py` ตรวจ rational frame rates (คำนวณแยกตาม source/record rate), ตรวจ gapless cut และ evaluate acceptance gate เทียบกับ SHA-256 evidence hashes แบบ deterministic
- เพิ่ม schema และสัญญาตรวจรับงานใน `docs/contracts/`: `acceptance-gate.json`, `edit-decisions.schema.json` และ `edit-decisions.example.json`
- เพิ่มเอกสารคู่มือ `docs/EDIT-WORKFLOW.md` อธิบายกระบวนการเตรียมงาน offline การร่างสัญญาตัดต่อ และเกณฑ์ตรวจรับงานตาม house style
- เพิ่มชุดทดสอบ 37 รายการใน `tests/test_edit_workflow.py` ครอบคลุม frame rate parsing, duplicate IDs, cache invalidation, caption linting, SRT validation, contact sheet hashing และการป้องกัน Windows junction

### Updated
- เพิ่มหัวข้อ "เตรียมงานและเกณฑ์ตรวจรับกลาง" ใน `README.md` ชี้ไปที่ `docs/EDIT-WORKFLOW.md`
- บันทึกกฎ offline intake, cache validation และ coverage ใน `docs/OPERATING-NOTES.md`
- ลงทะเบียนเครื่องมือใหม่ทั้งสองรายการใน `scripts/INDEX.md`
- เชื่อมโยงแนวทางการตรวจรับงานและสัญญาเฟรมใน `.agents/skills/resolve-delivery/`, `resolve-edit/`, `resolve-media-analysis/` และ `video-footage-review/`

### Verified
- ทดสอบ unit tests: `python -m pytest tests/test_edit_workflow.py` ผ่านครบ 37 รายการ
- ทดสอบทั้ง repo: `python -m pytest -q` ผ่าน 212 passed, 22 skipped, 10 subtests
- ตรวจสอบความถูกต้องของ skill bundle: `python scripts/verify_skill_bundle.py` ผ่าน 100%

### Scope
- ทุกเครื่องมือทำงานแบบ offline 100% โดยอ่านไฟล์และ JSON เท่านั้น ไม่ต่อ Resolve และไม่มีการดัดแปลง footage ต้นฉบับ

## v0.14.0

### Added
- เพิ่ม `docs/guides/resolve211-agent-guide.md` ให้ agent เลือก API และ MCP สำหรับ Resolve 21.1 โดยอ้างอิง build, schema และหลักฐานการตรวจที่ตรงกัน
- รวมเส้นทาง native สำหรับ speed/fades, transitions, multicam, audio normalization/alignment และ DCTL พร้อมลิงก์ไปยังคู่มือเฉพาะงาน

### Updated
- แก้ข้อความใน skills และคู่มือที่ระบุว่าไม่มี clip-speed API หรือ native multicam API ในทุกเวอร์ชัน ให้แยกข้อจำกัดของรุ่นเก่าจากความสามารถ 21.1
- แยกการสร้าง transition ออกจากการ clone และแยก native multicam creation/flattening ออกจาก stacked-timeline helper
- เพิ่มคำอธิบาย DCTL validation/encryption, Python ในตัว, settings แบบ TypedDict, ผลข้างเคียงของการเขียนหลายคีย์ และขอบเขตการตรวจ subtitle/render
- ตรวจ catalog ของ community MCP 4.13.1 ซึ่งมี 37 compound tools และกำหนดให้ตรวจ action schema ที่แนบในแต่ละ session
- ชี้แจง SHA-256 ของ vendor stub แบบ CRLF และ LF: เนื้อหาตรงกัน ความต่างของ hash ไม่ได้หมายความว่า API เปลี่ยน

### Verified
- ชุดไฟล์ release แยกจาก working tree: `python -m pytest -q` ผ่าน 175 tests, ข้าม 22 รายการ และผ่าน 10 subtests
- Community MCP รายงาน DaVinci Resolve Studio `21.1.0.17` และ MCP `4.13.1`; Studio MCP ยืนยันว่า Resolve `21.1` กำลังรันและเข้าถึงได้
- เปรียบเทียบ vendor stub ใน repo กับไฟล์ที่ Studio MCP ส่งมาได้ตรงกันแบบ byte-for-byte; เมื่อแปลง CRLF เป็น LF ค่า hash ตรงกับ provenance เดิม
- ตรวจลิงก์ภายใน คู่มือ และ manifest/checksums ก่อนเผยแพร่

### Scope
- ปรับ checksum เดิมที่ค้างใน manifest 3 รายการให้ตรงกับไฟล์ที่ติดตามอยู่ใน HEAD ได้แก่ helper subtitle preset และเอกสาร Armigon 2 ไฟล์ โดยไม่แก้เนื้อหาไฟล์เหล่านั้น
- รุ่นนี้ปรับ skills และเอกสาร ไม่ได้ทดลอง setters, แก้ timeline, render หรือเขียนฐานข้อมูล Resolve; หลักฐาน contributor บน macOS Build 14 ยังคงมีขอบเขตตามที่บันทึกไว้
- ไม่รวมงาน offline intake/edit workflow ที่ค้างอยู่ใน working tree ก่อนงานนี้
- เลขเวอร์ชันของ skill bundle แยกจากเวอร์ชัน DaVinci Resolve และ MCP server

## v0.13.0

เน้นให้ agent (Claude Code, Codex, Hermes) เริ่มงานเร็วขึ้นและไม่สร้างเครื่องมือซ้ำนอกโปรเจค

### เพิ่ม
- `CLAUDE.md` เป็นไฟล์ตัวชี้สั้นๆ ไป `AGENTS.md` (`@AGENTS.md`) เพราะ Claude Code อ่าน `CLAUDE.md` ไม่ใช่ `AGENTS.md`; กฎอยู่ที่เดียว Codex และ Hermes อ่าน `AGENTS.md` เหมือนเดิม
- `AGENTS.md` เพิ่มหัวข้อ "Start of task checklist" (ขั้น 0-4) และ "Finish of task: record what you learned" ใช้ได้กับทั้ง 3 agent
  - ขั้น 0: รัน `scripts/check_mcp_update.py` ก่อนเริ่มงาน
  - ขั้น 1: อ่านโปรไฟล์ช่องใน `docs/channels/` เมื่อผู้ใช้พูดถึงช่อง
  - ขั้น 3-4: ค้น `scripts/INDEX.md` ก่อน ห้ามสร้างเครื่องมือนอก repo; ถ้าไม่มีจริงให้เขียนใน `scripts/scratch/` พร้อมบรรทัด `MCP-GAP:`
- `scripts/INDEX.md` ตาราง "งาน -> script -> ขอบเขต" ครบ 115 script จัด 8 หมวด (พื้นฐาน, ซับไทย, VTuber Zoom/Focus, แปลง 9:16, Enrichment, QC/Review, Render/Export, จัดการโปรเจค) ติดป้ายขอบเขต `ใช้ซ้ำ` / `p2` / `armigon` / `sakuyako` / `ครั้งเดียว`
- `scripts/scratch/` (ติดตามเฉพาะ `.gitkeep`) ที่ทิ้ง script ชั่วคราวภายในโปรเจค แก้ `.gitignore` ให้ไม่ถูกกฎ `scratch/` เดิมบัง
- `scripts/check_mcp_update.py` ตรวจเวอร์ชัน MCP ชุมชน ([samuelgursky/davinci-resolve-mcp](https://github.com/samuelgursky/davinci-resolve-mcp)) เทียบ tag ล่าสุดผ่าน `git ls-remote`
  - อ่านโฟลเดอร์ที่ติดตั้งจาก `.mcp.json` ไม่ฝัง path
  - `--apply` ทำ `git fetch --tags`, `git checkout <tag>`, `pip install -r requirements.txt` และปฏิเสธเมื่อมีการแก้ค้างในโฟลเดอร์ MCP
  - สถานะผลลัพธ์: `UP-TO-DATE`, `UPDATE`, `BLOCKED`, `UNKNOWN` (ออฟไลน์)
- skill `project-learning` (`.agents/skills/project-learning/SKILL.md`) ขั้นตอนค้นเครื่องมือเดิมก่อนเขียนใหม่ และตารางว่าจบงานแล้วบันทึกอะไรลงไฟล์ไหน (OPERATING-NOTES, INDEX, house-style, โปรไฟล์ช่อง, AGENTS.md)
- `docs/channels/` โปรไฟล์ช่อง 7 ช่อง + สารบัญ: Katy404, Aomi-mama, Armigon, Tygarina, Sakuyako-Cheris, Laffy, Kael แต่ละไฟล์มี 8 หัวข้อ (ตัวตน, ที่เก็บไฟล์, โปรเจค/timeline, layout, ซับ/เสียง/enrichment, script/skill, กับดัก/งานค้าง, "ยังไม่ทราบ")
  - Laffy และ Kael ยังมีข้อมูลน้อย (ยังไม่พบ timeline หรือ script) ส่วนที่ไม่มีหลักฐานเขียนว่า "ยังไม่ทราบ" ไม่เดา
  - `aomimama.md` มีบทเรียนจากงานเดบิวต์ 30 ก.ย. 2026: เลย์เอาต์แนวตั้ง "Story", ค่า GIF แนวตั้งที่ผู้ใช้ยอมรับ, กฎซับ, ขั้นตอน sample gate
- กฎใหม่ใน `docs/OPERATING-NOTES.md`: audit ฟอนต์ต้องสแกนแบบ UTF-16 และห้ามอ่านค่า Text+ (Fusion) สดผ่านสคริปต์ (เคยทำให้ Resolve ค้าง) ให้อ่านจาก `.drp` ที่ export
- `patches/README.md` ระบุว่า patch เอกสาร MCP เดิมใช้กับ v4.13.x ไม่ได้
- `work/README.md` อธิบายโฟลเดอร์งานจริง
- test ใหม่ 3 ไฟล์: `tests/test_agent_entrypoints.py` (ทุก script ต้องอยู่ใน INDEX, ตรวจจุดเข้าของ agent), `tests/test_channel_profiles.py` (ครบ 7 ช่อง 8 หัวข้อ), `tests/test_check_mcp_update.py` (เรียงเวอร์ชันแบบตัวเลข, อ่านเวอร์ชันที่ติดตั้ง, ตัดสินใจ update/blocked, apply ใน repo ทดลอง)

### เปลี่ยน
- `.mcp.json` ชี้ MCP ที่ติดตั้งจริงที่ `Desktop/davinci-resolve-mcp` (เดิมชี้ `D:\` ที่ไม่มีอยู่) และตัด `PYTHONHOME` ที่ชี้ Python 3.13 ซึ่งไม่ได้ติดตั้งออก
- `AGENTS.md` ตัดรายการ script ยาวออก ชี้ไป `scripts/INDEX.md` และเลิกฝังเลขรุ่น MCP
- ย้าย `PLAN.md`, `PLAN-9x16.md`, `PROJECT.md`, `WORKLOG.md` ไป `work/` พร้อมอัปเดตลิงก์ใน README, OPERATING-NOTES, REVIEW
- `scripts/README.md` ชี้ไป INDEX และ `scratch/`
- รวม v0.12.0 จาก remote (script `sakuyako_*`, `drt_prepend_cover`, `build_9x16_day22/24` ฯลฯ) เข้า INDEX และโปรไฟล์ช่อง

### ลบ / เลิกติดตาม
- ลบโฟลเดอร์ `reference/` และที่เก็บถาวรภาพหนักของงาน Aomi-mama 30 ก.ย. (881MB) หลังสกัดบทเรียนลงโปรไฟล์ช่องแล้ว รายงานรีวิวกับ readback json ไม่มีสำเนา
- เลิกติดตามสำเนาฐานข้อมูลโปรเจค `backups/**/*.sqlite` (14 ไฟล์ ประมาณ 100MB) ใน git ไฟล์ยังอยู่บนดิสก์ และเพิ่มกฎใน `.gitignore`

### ผลการตรวจ
- `pytest`: 175 ผ่าน, 22 ข้าม (test `test_m1_*` ที่ต้องใช้ Resolve จริง ข้ามเมื่อไม่ใส่ `--live`), 197 collected
- `scripts/verify_skill_bundle.py`: `ok: true`, ไม่มี errors; manifest และ checksum อัปเดตด้วย `refresh_skill_manifest.py`
- อัปเดต MCP ชุมชน v4.10.3 -> v4.13.1 บนเครื่อง (ติดตั้ง dependency ผ่าน, import `server` ได้); `check_mcp_update.py` รายงาน `UP-TO-DATE`

### ข้อจำกัด
- ไม่ได้เชื่อมต่อหรือแก้ Resolve ในรุ่นนี้: ยังไม่ได้ทดสอบว่า MCP v4.13.1 คุยกับ Resolve ได้ (`resolve_preflight.py` ตอบ `BLOCKED` เพราะ Resolve ไม่ได้เปิด) ต้อง restart session แล้วลอง `resolve_control get_version`
- ข้อมูลในโปรไฟล์ช่องมาจากหลักฐานใน repo, memory และการดูโฟลเดอร์ต้นทางแบบอ่านอย่างเดียว ไม่ใช่การตรวจ Resolve สด ต้องยืนยันชื่อโปรเจค/timeline จาก Resolve ก่อนเขียนทุกครั้ง
- ป้ายขอบเขตใน INDEX จัดจากชื่อไฟล์และ docstring ไม่ได้อ่านโค้ดทุก script
- หัวข้อรายการ tool ใน skill `resolve-mcp` ยังอ้าง v4.10.4 (ยังไม่ได้ตรวจกับ v4.13.1)
- ไม่ได้ลดขนาด `.git` (ประมาณ 400MB เป็นประวัติเก่า) เพราะต้องเขียนประวัติใหม่และ force-push
- ไม่ได้แยก `scripts/` เป็นโฟลเดอร์ย่อย เพราะ import `scripts.xxx` 150+ จุดและยังไม่มีทางตรวจกับ Resolve จริง

## v0.12.0

### เพิ่ม
- เพิ่ม `scripts/build_9x16_day22.py` และ `scripts/build_9x16_day24.py` สำหรับสร้าง `<ชื่อเดิม>_9x16` (1080x1920) จาก timeline 16:9 ที่มี V1 / V2 Adjustment Clip / V3 GIF: เกมครึ่งบน, VTuber ขยายครึ่งล่าง, ช่วง focus เดิมเป็นหน้า VTuber เต็มจอ, GIF คงเวลาเดิม; dry run เป็นค่าเริ่มต้น และเทียบ subtitle/เสียง/ช่วง V1 กับต้นฉบับก่อนและหลังบันทึก
- บันทึกผลรันจริงวันที่ 24 ลงสกิล `resolve-video-enrichment` (focus zoom, enrichment BGM/SFX/GIF, แปลง 9:16) และ `docs/OPERATING-NOTES.md`: ค่า window ของ avatar มุมขวาล่าง, การคัด GIF ด้วย PIL ก่อนรัน, ผลข้างเคียงเมื่อรัน `apply_enrichment_d22` แล้วหยุดกลางคัน, การ list ไดรฟ์ Drive ด้วย `os.scandir`

### ผลการตรวจ
- ตรวจใน Resolve Studio 21.1.0.17 กับโปรเจกต์วันที่ 24 (1 timeline): แทรก Adjustment Clip 7 ช่วงและอ่านค่ากลับตรงแผน; เพิ่ม SFX 8, BGM 1, GIF 5 พร้อมอ่านค่ากลับ; สร้าง `_9x16` และเทียบ subtitle 105 cue, เสียง และ V1 กับต้นฉบับได้ตรงกัน; ต้นฉบับยังเป็น 1920x1080
- ตรวจภาพ still ที่ Resolve render: 8 จาก 21 เฟรม (focus), 4 เฟรม (GIF), 5 เฟรม (9:16) ไม่พบแถบดำ ใบหน้าและผมส่วนโด่งอยู่ในเฟรม
- ข้อจำกัด: ไม่ได้ฟังเสียงหรือ render ช่วงเต็ม, ภาพ still ไม่มี subtitle จึงยังไม่ยืนยันการทับของ subtitle บนจอแนวตั้ง, ไม่ได้เทียบเปิด/ปิด Adjustment Clip, ไม่ยืนยัน license ของไฟล์ SFX/BGM/GIF
- รวมสคริปต์จากงานอื่นที่ค้างใน working tree ด้วย (`sakuyako_*`, `drt_prepend_cover`, helper subtitle preset, การแก้ `scripts/README.md` และ `p2_export_final.py`) เพื่อให้ manifest ตรงกับไฟล์จริง; มีเฉพาะ `tests/test_drt_prepend_cover.py` (3 เทสต์ผ่าน) ที่ได้รัน ส่วนสคริปต์เหล่านี้ยังไม่ได้ QC ใน Resolve ในรีลีสนี้

## v0.11.0

### เพิ่ม
- เพิ่มกฎใน `house-style` ให้ยึด subject ที่ผู้ใช้ระบุหรือชี้ในภาพอ้างอิงเป็น focus target แทนการสมมติว่าเป็น VTuber เสมอ
- เพิ่มชุด helper สำหรับ pilot/ปรับ layout 9:16 ของ Armigon, retarget/reframe focus, ตรวจ source range/audio/publish แบบอ่านอย่างเดียว และเตรียมแผนแก้ caption แบบ offline พร้อม geometry test
- ปรับ bundle validator ให้ normalize line ending ของไฟล์ Graphviz `.dot` เพื่อให้ checksum ผ่านเหมือนกันข้ามระบบปฏิบัติการ

### ขอบเขต
- สคริปต์ชุดนี้ผูกกับ project/timeline IDs เฉพาะและยังไม่ได้รันหรือ QC ใน Resolve ในการเตรียมรีลีสนี้; ไม่ได้เชื่อมต่อหรือแก้ project, render หรือฐานข้อมูล Resolve

## v0.10.0

### เพิ่ม
- เพิ่มสกิลเสริม 29 ชุดใน `.agents/skills/` (workflow จากโปรไฟล์ 14 ชุด และ Superpowers v7.0.0 จำนวน 15 ชุด) โดยแยก `supporting` ออกจากสกิลตัดต่อหลัก 17 ชุดใน manifest
- เพิ่มคำอธิบายจำนวนสกิลและขอบเขตการเปิดใช้งานใน README/operating notes และปรับคู่มือการเผยแพร่ให้ใช้ tag สูงสุดเป็นฐาน พร้อม release title ภาษาไทย

### ปรับปรุง
- ปรับกฎ Resolve ให้ตรงกับ `AGENTS.md`: ไม่ใช้ FFmpeg แปลงสื่อหรือ API ที่ยังไม่ยืนยัน, ระบุ dependency ภายนอก, ขออนุญาตก่อนส่งภาพ/วิดีโอไปผู้ให้บริการภายนอก และจำกัดการเขียน preset ลงฐานข้อมูลจนกว่าจะรับประกันได้ว่า Resolve ปิดสนิท
- ให้ helper preset ใต้สกิลส่งต่อไปยัง helper กลางของโปรเจกต์ และบล็อกการเขียน Project.db ที่ยังไม่มี shutdown guard
- ทำให้การ resume export เชื่อถือเฉพาะงาน Resolve สถานะ `Complete` ที่ไฟล์ผ่านการตรวจ stream/ขนาด/ระยะเวลา และการเทียบ cover สำหรับแนวตั้ง พร้อมหยุดเมื่อพบไฟล์ output หลายชนิดที่ใช้ชื่อฐานเดียวกัน
- แก้ลิงก์ข้ามสกิล Superpowers ให้สัมพันธ์กับโฟลเดอร์จริง และปรับแนวทางล้าง worktree ให้เก็บหลักฐาน review/ledger ไว้
- อัปเดตแผนผัง community MCP จาก v4.10.3 เป็น v4.10.4 ตามข้อมูลในโปรเจกต์

### ผลการตรวจ
- `scripts/verify_skill_bundle.py` ผ่านโดยไม่มี errors: manifest 559 ไฟล์, ลิงก์ภายใน 90 จุด, สกิล active 17 core + 29 supporting = 46 และ archive 13 ชุด; รายงาน 14 ลิงก์ตัวอย่างจากคู่มือภายนอกเป็น exception ที่บันทึกเหตุผลไว้
- ตัวสแกน Hermes ใช้งานไม่ได้ใน environment นี้ จึงตรวจเฉพาะโครงสร้าง/frontmatter, references และ checksums; ไม่มีการรัน unit tests, เชื่อมต่อ Resolve, แก้ project database หรือทดสอบ render ในการเตรียมรีลีสนี้
- ผล validator ไม่ใช่หลักฐานว่า Resolve scripts หรือภาพที่ render ทำงานถูกต้อง

## v0.9.0

ชุดสกิลและสคริปต์ช่วยงานตัดต่อรุ่นนี้แยกเลขรุ่นจาก DaVinci Resolve และ MCP server

### P2 และการจัดภาพ 9:16
- เพิ่มชุด `p2_9x16_*` สำหรับสำรวจ source, สร้างและแปลง timeline, จัดส่วนเกม/ตัวละคร, ตรวจ cut และตรวจโครงสร้างหลังแปลง รวมถึงการรับสำเนา 1080×1920 ที่ตั้งค่าด้วยมือหรือ MCP และโหมด raster ช้า
- เพิ่มตัวลบ stray copy ตามขอบเขตที่ระบุ และการตรวจทุก timeline หลังเปลี่ยนเพื่อช่วยจับการคลาดเคลื่อนของแทร็กและช่วงภาพ

### ซับไทยและ QC ก่อนเผยแพร่
- เพิ่มเครื่องมือสร้าง cue จากข้อมูลต้นทางและ sample, ใช้ cue กับ native subtitle track, แก้กฎข้อความ/ช่วงเวลา และใช้ซับที่แก้แล้วได้ทั้งแนวตั้งและแนวนอน
- เพิ่ม `p2_publish_qc.py`, การตรวจซับหลังแก้, still และ audio QC เพื่อจัดหลักฐานก่อนเผยแพร่; `caption_lint.py` ตรวจข้อกำหนดซับไทยแบบอ่านอย่างเดียว

### VTuber focus และ QC
- เพิ่มตัววางแผน/ใช้ zoom focus ของ P2 พร้อม rollback, เครื่องมือสร้างและย้ายแทร็ก `Adjustment Clip` ผ่าน DRT, ตัวตรวจเฟรม/โครงสร้าง focus และ pilot Armigon บนสำเนา
- รายงาน QC Armigon ใน Resolve Studio 21.1.0.17 ที่ 1920×1080/60 fps ตรวจ `Adjustment Clip` 48 รายการ พบ `MotionBlur=0` ทั้งหมด; อ่าน `Center`/`Size` รวม 192 input โดยไม่พบ keyframe ใน input ที่ตรวจ
- T74–T77 เป็น VTuber ผมชมพูอีกคน จึงคืนค่าเฉพาะ V2 focus ให้เป็นกลางและอ่านค่ากลับแล้ว; T1 เฟรม 2261 และ T70 เฟรม 1839 มีภาพ still A/B เปิด/ปิด V2 ในเวลาเดียวกัน เขาด้านขวาถูกตัดใน source อยู่แล้ว และสติกเกอร์ผมขาวใน source ของ T70 บังมือ/ลำตัวบางส่วน การลอง `X=-0.06` ไม่แก้เขา จึงคืน T70 เป็น `X=-0.03`
- ภาพ still ที่ตรวจไม่พบขอบดำหรือ blur ที่ zoom เพิ่มขึ้น แต่ไม่ใช่หลักฐานว่า motion ทุกเฟรมไม่มีอาการสั่น และไม่ได้ตรวจวิดีโอ render เต็มช่วง รายละเอียดและขอบเขตหลักฐานอยู่ที่ `docs/superpowers/reports/2026-10-12-armigon-focus-qc-th.md`

### GIF, การตัดท้าย และการส่งออก
- เพิ่มการย้าย GIF บน V2 ให้อยู่ในแผงเกมเหนือรอยต่อ avatar ของ 9:16 โดยคำนึงถึง V3 ที่วาดทับ V2; เพิ่มเครื่องมือตัด GIF ท้ายที่ผิดและสร้าง timeline รุ่น `_150s` โดยลบ cue ที่เลยหรือคร่อมจุดตัดตามนโยบายสคริปต์
- เพิ่มชุด render แนวตั้ง/แนวนอน, ตัวช่วย loudness ของแต่ละสัดส่วน และ `p2_export_final.py` สำหรับเตรียม export หลาย timeline ด้วย `H.264 Master` พร้อม readback/การตรวจผลที่สคริปต์กำหนด; การมีสคริปต์ไม่ใช่หลักฐานว่าไฟล์ส่งออกทุกชิ้นผ่าน QC แล้ว

### ขอบเขตเครื่องมือและสกิล
- ปรับ `AGENTS.md` และสกิล Resolve ให้บังคับใช้ Resolve MCP ก่อน แล้วจึงใช้ Python Scripting API เมื่อมีหลักฐานช่องว่าง; เพิ่มแผนผังเครื่องมือ MCP v4.10.4 และคำแนะนำ subtitle/conform/focus QC ล่าสุด
- เพิ่มกฎ house style และ `adjustment-focus.md` ให้ยืนยันตัว Armigon, อ่าน transform/`MotionBlur`, เทียบเฟรมเดียวกันเมื่อเปิด/ปิด focus และแยกปัญหา source ออกจากผล zoom

### เพิ่มเติม
- `scripts/caption_lint.py`: ตรวจ SRT ภาษาไทยแบบ read-only ตามกฎซับสั้น (ไม่เกิน 14 อักษรไทยและ 1.5 วินาทีต่อ cue, ไม่เว้นวรรคระหว่างอักษรไทย, ไม่เกิน 2 บรรทัด) คืน exit code 1 เมื่อมีข้อผิดกฎ; ชี้จาก `thai-subtitles-resolve`
- `scripts/backup_drp.py`: `export_verified` / `verify_drp` สำหรับ export `.drp` แล้วตรวจว่าไฟล์ไม่ว่างและเป็น zip ที่สมบูรณ์
- `tests/conftest.py`: ข้ามเทสต์ `test_m1_*` ที่ต้องมี Resolve จริง เว้นแต่ใส่ `--live`
- `tests/test_caption_lint.py`, `tests/test_backup_cleanup.py`

### แก้ไข
- `scripts/cleanup_backups.py`: เดิมลบ `.drp` ทุกไฟล์ในโฟลเดอร์ รวมถึงไฟล์ rollback (`pre-enrichment`, `before_promotion_`) เพราะ `KEEP_MARKERS` / `DELETE_PREFIXES` ไม่ถูกใช้และ `--keep-rollback` ไม่ทำอะไร; ตอนนี้ลบเฉพาะชื่อที่ขึ้นต้นด้วย `before_python_batch_` / `before_python_vdo_` เท่านั้น ไฟล์อื่นรายงานเป็น kept / skipped_unmatched (ยังเป็น dry-run ถ้าไม่ใส่ `--confirm`)
- `scripts/promote_drafts_to_originals.py`: เดิมเขียน report ทับก่อนอ่านสถานะรอบก่อน ทำให้ตรวจ "promoted_verified" ไม่เคยได้ผล; ตอนนี้อ่านก่อน, คงรายการ `added` เดิม และ dry-run ไม่ลบบันทึกการ promote ที่ยืนยันแล้ว
- `scripts/focus_apply_batch.py`, `scripts/focus_tune.py`: เพิ่ม bootstrap path ให้รันตรงด้วย `python scripts/<ชื่อ>.py` ได้ (เดิมได้ `ModuleNotFoundError`; `python -m scripts.<ชื่อ>` ใช้ได้อยู่แล้ว)
- `scripts/resolve_common.py`: `preserved_state` คืน Media Pool folder ด้วย และรายงานบน stderr เมื่อคืนค่าขั้นใดไม่สำเร็จ แทนการกลืน exception เงียบๆ
- ลบ import / ตัวแปรที่ไม่ใช้ (pyflakes สะอาด)

### ย้ายออก
- ย้ายออกไป `Desktop/_archive-davinci-cleanup-2026-10-09/scripts-review-2026-10-09/` (ไม่ได้ลบ): สคริปต์งานครั้งเดียว `render_t02_candidate`, `render_lowerleft_16_42`, `render_bottomleft_batch`, `render_headroom_tune`, `apply_focus_candidate`, `apply_bottomleft_candidates`, `tune_focus_headroom`, `focus_set_transform`; ชุดย้าย 9:16 รอบ M2/M3 `m2_convert_pilot`, `m3_convert`, `calibrate_crop`, `calibrate_zoom`, `compare_invariants`, `survey_sources`, `export_source_stills`, `layout9x16`, `split_projects`, `challenger_m2_1_results.json`; และเทสต์ live `test_m2_*`, `test_m3_*`
### การตรวจ
- ในการเตรียมรีลีสครั้งนี้ รัน `python scripts/verify_skill_bundle.py` ได้ `ok: true`, `errors: []`, 449 ไฟล์ใน manifest และ 73 ลิงก์ภายใน; ผลอยู่ใน `docs/validation-report.json` (ตัวสแกน Hermes ไม่พร้อม จึงเป็นการตรวจโครงสร้าง/checksum) รัน `git diff --check` ผ่านด้วย
- รายงาน Armigon ข้างต้นเป็นหลักฐาน QC ที่บันทึกไว้ก่อนหน้านี้ ไม่ใช่การทดสอบสดของสคริปต์ทั้งหมดในรีลีสนี้ ไม่มีการเชื่อมต่อ Resolve หรือตรวจวิดีโอ render เต็มช่วงในการเตรียมรีลีสครั้งนี้

## v0.8.0

### Added
- `scripts/resolve_common.py`: เพิ่ม `require_resolve()` ที่จบโปรแกรมพร้อมข้อความชัดเจนเมื่อเชื่อมต่อ Resolve ไม่ได้ และ `preserved_state(resolve)` ที่คืนโปรเจกต์ ไทม์ไลน์ playhead และเพจให้เหมือนเดิมเมื่อจบงาน (คืนค่าได้แม้เนื้อหาข้างในล้มเหลว)
- `scripts/resolve_preflight.py`: เพิ่มตัวเลือก `--list-tools` สำหรับดูรายชื่อ tool ใน catalog ของ MCP; ไม่ต้องใส่ `--need` เมื่อใช้ตัวนี้
- `scripts/README.md`: จัดกลุ่มเครื่องมือทั้งหมด พร้อมลำดับการใช้งาน (MCP ก่อน แล้ว preflight แล้วค่อยสคริปต์)
- `tests/test_resolve_common.py`: ทดสอบ `preserved_state` และ `require_resolve` ด้วย Resolve จำลอง
- `.agents/skills/resolve-mcp/SKILL.md`: เพิ่มตาราง "Live tool map" ที่บอกว่างานแต่ละอย่างใช้ tool ของ `davinci-resolve` MCP ตัวไหน และขั้นตอนตรวจ MCP ทางการของ Resolve (`get_whats_new`, `search_scripting_api`, `run_script`) ก่อนเขียนสคริปต์เอง

### Updated
- `scripts/resolve_common.py`: ค้นหาโมดูล Resolve จาก `C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules` ด้วย
- `scripts/apply_vdo_preset.py`, `scripts/load_subtitle_preset.py`, `scripts/split_projects.py`: เลิกเขียนตัวเชื่อมต่อเอง ใช้ตัวกลางใน `resolve_common` แทน (คงชื่อ `connect_resolve` ใน `load_subtitle_preset.py` เพราะ `apply_video_style.py` เรียกใช้)
- `scripts/apply_bottomleft_candidates.py`, `render_bottomleft_batch.py`, `render_headroom_tune.py`, `render_lowerleft_16_42.py`, `render_t02_candidate.py`, `tune_focus_headroom.py`: แตกคำสั่งบรรทัดเดียวที่ต่อกันด้วย `;` ให้เป็นบรรทัดแยก ตรรกะเหมือนเดิม (ตรวจโครงสร้างโค้ดตรงกันทุกไฟล์) ยังไม่ได้ทดสอบกับ Resolve จริง
- `scripts/refresh_skill_manifest.py`: `bundle_version` เป็น 0.8.0
- `docs/skills-manifest.json` และ `docs/validation-report.json`: สร้างใหม่หลังจัดระเบียบไฟล์

### Removed
- ย้ายสคริปต์ทดลอง/ใช้ครั้งเดียวที่ไม่มีเอกสาร สกิล หรือเทสต์อ้างถึง 73 ไฟล์ออกจาก repo ไปไว้ที่ `Desktop/_archive-davinci-cleanup-2026-10-09/scripts/` (ไม่ได้ลบทิ้ง) รวมถึงชุด VTuber focus เก่า ไฟล์ `dbg_*`, `diagnose_*`, `probe_*`, `test_v*`, `test_challenger_*` และ `aomimama_*`
- ย้ายสกิลทั่วไปสำหรับงานเขียนโค้ด 38 ตัว (จาก `mattpocock/skills` เช่น `tdd`, `wizard`, `teach`) ออกจาก `.agents/skills/` ไปไว้นอกโปรเจกต์ ทำให้เหลือสกิลของ Resolve, house-style และสกิลภาษาไทย 17 ตัว
- ลบโฟลเดอร์ `scratch/` (ไฟล์ทดลองและภาพนิ่ง ไม่เคยอยู่ใน git)
- ลบ `skills-lock.json` ที่ว่างเปล่า

### Validation
- `python scripts/verify_skill_bundle.py` — `ok: true`
- เทสต์ที่ไม่ต้องใช้ Resolve จริง — ผ่าน 105 รายการ ล้มเหลว 1 รายการ (`test_review_analysis_budget.py` ต้องใช้โมดูล `agent` ของ Hermes ที่ไม่มีในเครื่อง)
- `tests/test_m1_*`, `test_m2_*`, `test_m3_*` ไม่ได้รัน; `test_m1_backup_empirical` และ `test_m1_baseline_validation` ล้มเหลวเพราะไฟล์เก่ากว่า 24 ชั่วโมงและผูกกับโปรเจกต์ KT404
- ยังไม่ได้ทดสอบสคริปต์ที่แก้กับ Resolve จริง

## v0.7.0

### Added
- ชุดเครื่องมือออฟไลน์สำหรับตรวจและเพิ่ม SFX/BGM/GIF ให้ทุก Timeline โดยไม่ใช้ API วิเคราะห์วิดีโอ: `scripts/review_enrichment_readonly.py`, `scripts/build_offline_review.py`, `scripts/build_offline_asset_draft.py`, `scripts/resolve_preflight.py`, `scripts/resolve_common.py`
- `scripts/apply_vdo_python.py`: จับค่าที่เปิดเผยของ GIF ที่โหลด preset `vdo` แล้วด้วย UI แล้วใช้กับ GIF ตาม project/timeline/clip ID; dry-run เป็นค่าเริ่มต้น ต้องมี DRP backup ก่อนเขียน และคืน UI state
- `scripts/enrich_timelines_python.py`: เพิ่ม SFX/BGM/GIF บนสำเนา Timeline ด้วย Resolve Python; dry-run เป็นค่าเริ่มต้น, ไม่มีจุดจากซับที่พอจะเสนอ BGM อย่างเดียวโดยไม่แต่งจังหวะมุกขึ้นเอง, คง GIF เดิมที่ทับช่วงไว้
- `scripts/promote_drafts_to_originals.py`: ย้ายงานที่ตรวจแล้วเข้าต้นฉบับตาม ID จริง ทำซ้ำได้ (นับ (ชื่อ asset, record frame) ที่มีอยู่แล้วเป็นรายการเดิม) และปฏิเสธเมื่อต้นฉบับไม่ตรง baseline
- `scripts/anomaly_sweep.py`: ตรวจความผิดปกติทั้งโปรเจกต์แบบอ่านเท่านั้น (ช่วงเวลา คลิปหลุดขอบ คลิปซ้อน คลิปซ้ำ ไฟล์ต้นทางหาย GIF นานเกิน ค่า `vdo` ความยาว BGM จำนวนซับ)
- `scripts/cleanup_backups.py`: export `.drp` ใหม่ที่ตรวจแล้วหนึ่งไฟล์ก่อนลบ archive
- `scripts/refresh_skill_manifest.py`: สร้าง `docs/skills-manifest.json` ใหม่จากไฟล์จริง (เพิ่ม/ลบ/อัปเดต checksum และเรียก validator ต่อ)
- `scripts/apply_offline_enrichment_pilot.py`, `scripts/render_enrichment_pilot.py`, `scripts/render_review_previews.py`, `scripts/verify_review_resume.py`, `scripts/delete_draft_copies.py`, `scripts/audit_promotion.py`, `scripts/audit_draft_copies.py`, `scripts/export_enrichment_backup.py`, `scripts/finish_timeline1.py`, `scripts/reapply_pilot_original.py`, `scripts/smoke_offline_review.py`, `scripts/smoke_alternative_video.py`, `scripts/run_draft_batches.sh`, `scripts/run_promotion_batches.sh`
- tests ออฟไลน์ 10 ไฟล์ (`tests/test_offline_*.py`, `tests/test_apply_vdo_python.py`, `tests/test_enrich_timelines_python.py`, `tests/test_render_enrichment_pilot.py`, `tests/test_resolve_preflight.py`, `tests/test_review_analysis_*.py`, `tests/test_review_resume_cache.py`)

### Updated
- `.agents/skills/resolve-video-enrichment/references/automation-safety.md`: เพิ่มหัวข้อ draft-then-promote ที่บันทึกจากของจริง 4 ข้อ — ลำดับสำเนาก่อนต้นฉบับ, การย้ายแบบ idempotent, Resolve conform GIF สั้นกว่าที่ขอ 2 เฟรม จึงต้องตรวจช่วงจริงไม่ใช่ค่าที่ขอ, และ native subtitle item ไม่มี Media Pool entry (เคยทำให้ sweep รายงานผิด 960 ครั้ง)
- `resolve-video-enrichment` (SKILL.md + house-style): กฎ native Subtitle-only, ขอบเขต style ที่ผู้ใช้ถือเอง, และ Thai cue cap 1.5 วินาที ตรงกับไฟล์ที่ลงทะเบียนใน manifest
- `docs/OPERATING-NOTES.md`: เพิ่ม 6 กฎที่วัดได้ + ตารางเครื่องมือ + ย้ำว่าเส้นทางออฟไลน์ไม่พึ่ง provider ใด
- `README.md`: เพิ่มขั้นตอน 9 ขั้นพร้อมคำสั่งจริง และข้อจำกัดที่ต้องรายงานเสมอ
- `docs/skills-manifest.json` (237 ไฟล์, bundle_version 0.7.0) และ `docs/validation-report.json` — สร้างใหม่หลังจัดระเบียบไฟล์
- `.gitignore`: เพิ่ม `.hermes/` สำหรับไฟล์งานเฉพาะเครื่อง

### Removed
- ลบ artifact งานภายใน 1,379 ไฟล์ที่เลิกใช้แล้วออกจาก index: `.agents/teamwork/**` (บันทึกประสานงาน/audit), `reference/**` และ `scratch/**` ซึ่ง `.gitignore` กันไว้อยู่แล้ว (`*.drp`, `*.mp4`, `*.mov` ยังคงถูก ignore)

### Validation
- `python scripts/verify_skill_bundle.py` — `ok: true`, `errors: []`, 237 manifest files, 17 core skills, ลิงก์ในโปรเจกต์ 65 จุด
- `python -m unittest tests.test_skill_bundle` — ผ่าน 9 tests
- tests ออฟไลน์ของ helper ใหม่/ที่แก้ — ผ่าน 33 tests
- ตรวจ path ที่อ้างใน `README.md` และ `docs/OPERATING-NOTES.md` ด้วยสคริปต์ — 12/12 มีอยู่จริง
- `git diff --check` — สะอาด

### Scope
- งานนี้คือชุด skills, คู่มือ, เครื่องมือออฟไลน์ และการจัดระเบียบไฟล์ในรีโป ไม่ได้เปลี่ยนซอร์สฟุตเทจหรือโปรเจกต์ Resolve ระหว่างจัดทำ release
- 8 test modules ที่ต้องใช้ `pytest` (`test_enrichment_assets`, `test_enrichment_engine`, ชุด `m1`–`m3`, `test_pilot_readback`) ยัง import ไม่ได้ใน interpreter นี้เพราะไม่มีแพ็กเกจ — เป็นสภาพเดิมก่อนงานนี้ ไม่ได้แก้และไม่ปิดบัง
- `.hermes/` (ผลตรวจ, รายงาน, render, `.drp`) ถูก ignore จึงไม่เข้า bundle
- ยังไม่ผ่านการตรวจภาพ/ฟังเสียงจริงของทั้ง 49 Timeline และยังไม่ได้ยืนยันสิทธิ์ของ asset ที่ใช้

## v0.6.0

### Added
- `scripts/apply_video_style.py`: capture and apply exposed video properties from an approved reference clip to explicit timeline item IDs. Dry-run is the default; writes require a verified DRP backup and include property readback, rollback, protected timeline comparisons, and UI-state restoration. It is not a native named Video Preset loader and makes no Resolve database writes.
- Offline orchestration coverage for project/timeline ID refusal, invalid backup refusal, and successful save/readback/restoration. `docs/guides/video-style-script.md` and a sanitized example at `presets/video/approved-gif-style.json` contain no live project clip ID or filename.
- `.agents/skills/thai-subtitles-resolve/references/srt-insertion-and-presets.md` with SRT insertion, exact saved-preset discovery, database-write boundaries, and post-load verification.

### Updated
- `thai-subtitles-resolve` v0.4.0 now documents reuse of Media Pool SRT items, exact cue/frame readback, failure-safe append recovery, and approved saved font presets.
- House style, `resolve-edit`, `resolve-video-enrichment`, operating notes, and README clarify approved preset use and distinguish native APIs from database workarounds.

### Validation
- `python -m unittest discover -s tests -p test_apply_video_style.py -v` — 10 tests passed.
- The helper was live-verified against explicitly approved GIF items during development; this release preparation did not connect to or modify a Resolve project.

### Scope
- Editing-skill bundle and helper documentation only. No source media, Resolve project, or database was changed for this release. Caption/GIF visual review and listening QC remain separate checks.

## v0.5.0

### Added
- `scripts/apply_vdo_preset.py` + `scripts/video_presets.json`: applies the Inspector Video preset "vdo" to GIF items on the V2 REACTIONS track. Resolve 21.1 has no API for Inspector > Video Presets > Load Preset and `User.db` does not expose the preset body, so the script writes captured property values (Zoom 0.42 gang, Pan 0, Tilt 32.28, others default) with `SetProperty`. Dry run by default; `--apply`, `--timeline`, `--only-originals`, `--track-name`, `--capture NAME` (captures from the clip under the playhead).
- `resolve-video-enrichment/references/horizontal-gif-placement.md`: 16:9 GIF placement, the measured Pan/Tilt-to-pixel model (X shift = Pan*fitted_w/1920, Y shift = Tilt*fitted_h/1080), GIF import timing (Resolve 25 fps normalization, 1.5s minimum), per-timeline loudness-based BGM/SFX levels.

### Updated
- Synced `resolve-video-enrichment` with the live Hermes copy (also brings the previously unsynced `katy404-channel-study.md`, `vertical-9x16-conversion.md`, `assets/` and edits to `asset-library-and-cues.md`, `automation-safety.md`, `illustration-assets.md`).

### Verified
- Live on Resolve Studio 21.1.0.17, project `tygarina_2026-09-30_FreeTalk_1`: preset applied to 63 of 64 GIF items (10 originals + 10 `[ENHANCED]` copies; 1 already matching), 0 failures, repeat dry run reports 0 changes, active timeline/playhead/page restored.
- Enrichment of the same 10 timelines (SFX/BGM/GIF added to originals and copies, protected V1/A1/subtitle ranges unchanged) was read back; a 3-timeline pixel check confirmed GIF bounding boxes before the preset was applied.

### Scope
- Not a real Load Preset: the preset values are a captured clone; re-capture if "vdo" changes. No listening QC, no render, and no per-file license check of the BGM/SFX/GIF assets was done.
- `tests/test_skill_bundle.py::test_bundle_structure_references_and_checksums` was already failing before this release (core skill count 16 vs 18 and an out-of-date file manifest); `docs/skills-manifest.json` was not refreshed here.

## v0.4.0

### Added
- `scripts/load_subtitle_preset.py`: loads a saved Subtitle track preset (Inspector > Load Preset) by script. Resolve 21.1 has no preset API, so it copies the preset bytes (`User.db` `SubtitlePresetsBA`) into each target track's `EffectFiltersBA` in `Project.db`. Dry run by default; `--apply` saves, exports a `.drp`, closes the project, snapshots `Project.db`, writes one transaction, reopens, restores timeline/playhead/page and verifies blobs and cue counts.
- `--orientation horizontal|vertical` selects timelines by resolution (Mitr Font for 16:9, Mitr-short-001 for 9:16 in the user's library).
- `tests/test_load_subtitle_preset.py`: offline tests for blob parsing/round-trip and exact-row database writes.

### Verified
- Applied `Mitr Font` to 10/10 subtitle tracks of project `tygarina_2026-09-30_FreeTalk_1` (8 changed, 2 already matching); cue counts unchanged; repeat dry run reports 0 changes. The vertical path is dry-run tested only.

## v0.2.0

### Added
- `resolve-video-enrichment/references/adjustment-focus.md`: using the user's selected Adjustment Clip as a protected template (selection readback, copy rather than move, per-timeline templates) and a 9-point per-cue VTuber framing checklist (subtitle association, new-track placement, prominence, centering, head-to-chest/hands, headroom, no crop, caption/HUD overlap, scope audit).
- `resolve-video-enrichment/references/illustration-assets.md`: planning, rights, organization, import, placement, and QC of still-image overlays.
- KT404 enrichment tooling: `scripts/enrichment_assets.py`, `scripts/enrichment_engine.py`, `scripts/run_pilot.py`, with tests, plus the design spec and implementation plans under `docs/superpowers/`.
- Working references and QC evidence under `reference/` and `scratch/`.

### Updated
- Synced `resolve-video-enrichment` with the live Hermes copy: per-timeline `timelineFrameRate` for record/source conversions, full-length BGM and 1.5–2.5s GIF holds, and new Thai trigger phrases.
- Bundle manifest checksums and counts refreshed for the release contents.

### Scope
- No claim of live Resolve verification for the new guidance; the pilot tooling's own results are recorded in `WORKLOG.md`.

## v0.1.0

First versioned release of the DaVinci Resolve editing skill bundle. The bundle version is independent of Resolve, the upstream MCP server, and individual archived skill versions.

### Added
- Thai VTuber editorial guidance: selecting self-contained highlights, truthful hooks, comic timing, and preserving the creator's personality.
- On-demand chapters for Resolve editing, Thai captions/audio/framing, YouTube packaging/feedback, and delivery/rights, with primary-source references.
- A reusable edit brief, cutlist, experiment plan, and acceptance-record template.

### Updated
- Expanded `resolve-video-enrichment` into a lean core with 11 reference chapters and one template, retaining the existing enrichment/recovery workflows.
- Clarified native subtitles versus burned-in pixels, evidence-led cue placement, measured audio versus scripting capability, source-frame timebases, and approval-gated repair/cleanup.
- Preserved the project's native Subtitle-track workflow and Thai short-form limits: three short words/about 14 Thai characters, at most 1.5 seconds, and no spaces between Thai words except appropriate Latin boundaries.
- Refreshed bundle provenance/checksums and validation evidence for the release contents.

### Fixed
- Bundle validation now accepts Git's LF/CRLF conversion for UTF-8 text while still rejecting content changes and preserving exact binary checksums; regression tests cover both newline directions and binary changes.

### Scope
- Skills, documentation, and bundle-validation release only: no MCP implementation, Resolve project, source media, or live editing behavior was changed.
- No claim of proven audience growth, channel-specific analytics, or live Resolve verification.
- Unrelated local editing plans, worklogs, scratch reports, media, and project backups are not part of this release change.
