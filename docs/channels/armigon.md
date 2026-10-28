# Armigon

## ตัวตนและคอนเทนต์
- VTuber ไทย ตัวละครชื่อ Armigon เนื้อหาเกมและ free talk (ในโฟลเดอร์มี "เกมโปรด 2026", "แนะนำตัว", "ทำไมถึงชื่อ Armigon")

## ปกที่มาของชื่อ (2026-10-28)
- ผู้ใช้ยืนยันหัวข้อ “ทำไมถึงชื่อ Armigon” ตาม Timeline แทนข้อความเริ่มต้น “ทำไมมาเป็นวีทูปเบอร์”; อ่านสดผ่าน Studio MCP: โปรเจกต์ `ทำไมถึงชื่อ Armigon`, `FirstPass v2_illustrated` (1920×1052, 60 fps) และ `FirstPass v2_illustrated_9x16` (1080×1920).
- สร้างเฉพาะไฟล์ปกแยกแนวนอน 1920×1080 และแนวตั้ง 1080×1920 ใน `.hermes/projects/armigon-covers-20261028/`; ไม่แก้ Timeline. ไฟล์ส่ง: `FirstPass v2_illustrated_cover.jpg` และ `FirstPass v2_illustrated_9x16_cover_final.jpg`.
- ใช้ built-in imagegen อ้างอิงตัวละครจริงจาก source frame; ข้อความ “ทำไมถึงชื่อ ARMIGON?” สีขาว/ทองบนพื้นหลังแฟนตาซีเขียวเข้ม. เป็นภาพประกอบที่สร้างจาก reference ไม่ใช่ cutout ที่คงพิกเซลต้นฉบับ. ตรวจมือถือ/เทา/squint/badge; แนวตั้งแก้ให้วรรณยุกต์ทั้งหมดอยู่ในพื้นที่ครอป 4:5 และคำถามหลบขอบขวา.

- ปก v2 (2026-10-28, ผู้ใช้ขอเวอร์ชันใหม่หลังเห็นชุด imagegen): `.hermes/projects/armigon-covers-v2/armigon_name_cover_v2_16x9.jpg` และ `_9x16.jpg` (+ `Armigon_Name_Covers_v2.zip`, `QC.md`); ตัวละครเป็นเฟรมจริงไม่ตัด cutout: timeline 2640 = source 3245 (ยิ้ม ตาเปิด เห็นแขนไม้); ข้อความ `ที่มาของชื่อ / ARM 1 GON (เลข 1 แดง) / แขนหาย?!` อิงซับ 1234/1740/1889; HTML + `hyperframes snapshot --at 0.5 --no-end --describe false`; builder `scripts/scratch/armigon_covers_v2.py`, ดึงเฟรม `scripts/scratch/armigon_covers_v2_frames.py` (map timeline→source จาก V1 left offset)
- ผู้ใช้ขอให้เก็บปกไว้ข้างคลิปต้นฉบับ: คัดลอก v2 ทั้งสองไฟล์ไปที่ `Z:/armigon/ทำไม Name Armigon/` (โฟลเดอร์เดียวกับ `ทำไม Name Armigon.mp4`)
- กับดัก: เฟรม source มีตัวจิบิชมพูมุมซ้ายล่าง (x~270,y~900) — ปกแนวนอนต้องทำ radial มืดทับ หรือเลือก scale/offset ให้หลุดเฟรม

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

## คลิปแนะนำตัว — ภาพประกอบแฟนตาซี (2026-10-24)
- โปรเจกต์ `เเนะนำตัว-armigon`; ต้นฉบับ `FirstPass v2` และสำเนา `FirstPass v2_illustrated` (ID `ab0559f8-ae8c-4f99-98c7-ff79eb79f003`)
- ผู้ใช้เลือกแฟนตาซีจริงจัง ภาพเต็มจอสลับกราฟิกข้างตัว; คง 1920×1052, 60 fps, 11,045 เฟรม ไม่แปลงเป็น 1920×1080 อัตโนมัติ
- ภาพประกอบ 23 ช่วงบน `REACTIONS`: full-frame 7 ช่วง และกราฟิกโปร่งใส 16 ช่วง; สร้างด้วย HyperFrames และนำเข้า Resolve ผ่าน Python API
- ไฟล์งาน/backup/baseline/readback/QC อยู่ `.hermes/projects/armigon-illustrated/`; ต้นฉบับวิดีโอ/เสียง/ซับอ่านกลับตรง baseline หลังนำเข้า ตรวจพรีวิวกำเนิดโกเลมพร้อมซับแล้ว ส่วน QC พรีวิวเต็มดู `ACCEPTANCE.md` ในโฟลเดอร์งาน
- ผู้ใช้แก้ `FirstPass v2_illustrated` เองหลังส่งงาน (ยาว 10,827 เฟรม, SFX 22, ไม่มี BGM, ซับ 177) และ `FirstPass v2` ถูกลบออกจากโปรเจกต์ก่อน backup 9:16 (ยังกู้ได้จาก `Armigon_illustrated_project_v2.drp`)
- 9:16 (2026-10-24): `FirstPass v2_illustrated_9x16` ID `967342ca-ba76-45ea-8b88-650c77cffdd7`; ผู้ใช้อนุมัติ layout B = อวาตาร์ครึ่งล่าง (window x 470–1350, Zoom 2.1818, Pan 61.36, Tilt -1020.28) + แถบบน plate เบลอ (V2 `Top Plate`) + การ์ด side กลางแถบบน + art เต็มความสูงครอปตาม `v916/art_centre.json`; ซับสไตล์เดิมอยู่ราว y 1530 บนอก สคริปต์ build อยู่ใน `scripts/scratch/` (armigon_illustrated_9x16, ยังไม่ promote)
- ปกคลิปแนะนำตัว (2026-10-24): `.hermes/projects/armigon-illustrated/thumb/armigon_intro_thumb_16x9.jpg` (1920x1080) และ `_9x16.jpg` (1080x1920); พื้นหลัง art `tree` (ต้นไม้แห่งชีวิตลุกไฟ) + อวาตาร์เฟรม source 1413 (ตาเปิด มองกล้อง ตาเรืองแสง) ไม่ตัด cutout; ข้อความ "แนะนำตัว ARMIGON" / "โกเลม" ขาว / "2,000 ปี" ทองเรืองส้ม, Mitr Bold ขอบดำ; HTML `thumb/t169|t916/index.html` render ด้วย `hyperframes snapshot`; QC มือถือ/เทา/squint `thumb/qc_t*.jpg`
- ปกชุดใหม่ (2026-10-25, ชุดเดิมใน `thumb/` หายไปพร้อมโฟลเดอร์): `.hermes/projects/armigon-illustrated/thumbnail/armigon_intro_thumb_16x9.jpg` และ `_9x16.jpg`; ผู้ใช้ขอให้ใช้ตัวละครจากคลิปแทน chibi: ใช้เฟรม source 10800 ของ `Z:rmigon\แนะนำตัว6-04-18 20-20-19 (1 take).mp4` (ยิ้ม ตาเปิด มองกล้อง ตาขวาเรืองแสง) เต็มเฟรมไม่ตัด cutout เป็นทั้งตัวละครและฉากหลัง; 16:9 scale 1.30 ตัวละครขวา gradient มืดซ้าย; 9:16 scale 1.25 ตัวละครล่าง (ty 650) + ฉากบนเป็นเฟรมเดียวกันเบลอ 30px brightness .8, fade 70px; เวอร์ชัน chibi เก็บใน `thumbnail/chibi_v1/`; ข้อความ `แนะนำตัว ARMIGON` / `โกเลมอายุ` / `2,000 ปี` ทอง อิงซับ 11.2–14.9 วิ ("อามิกอนเป็นโกเลมชายอายุ...ประมาณ 2,000 ปี"); builder (build_html) ในโฟลเดอร์ `thumbnail/` -> `t169|t916/index.html` -> `npx -y hyperframes@0.8.197 snapshot`; QC `thumbnail/qc/`
- กับดัก: ร่างปกจาก Pillow compositor ของ `D:\agent-thumbnail` ตัด glyph ท้ายบรรทัดใน 9:16 ("2,000 ป", "Armigon" หาย) — ใช้ HTML snapshot สำหรับข้อความไทยบนปก

## กู้คืนภาพประกอบคลิปแนะนำตัว (2026-10-25)
- `.hermes/projects/armigon-illustrated/` หายไป แต่ภาพต้นฉบับ 5 ภาพยังอยู่ใน `.codex/generated_images/01a16c15-a3ca-7752-b489-031c4aa20f70/`; คัดลอกกลับแบบ byte-identical ไป `assets/ice|forge|tree|ruins|forest.png` และสร้างฉากสงคราม `battle.png` ใหม่จาก prompt ที่เก็บไว้ในโฟลเดอร์โปรเจกต์
- สร้าง HyperFrames source และวิดีโอที่ Resolve อ้างถึงกลับ ณ path เดิม: `art.mp4` (1,935 เฟรม), `side.mov` (3,014 เฟรม, alpha), `battle.mp4` (298 เฟรม); ทั้งหมด 1920×1052, 60 fps
- Resolve ตรวจ `FirstPass v2_illustrated` แล้วพบสื่อ `REACTIONS` 23/23 ชิ้นเป็น Online และตำแหน่งกับ source offsets ตรงกับ `placements.json`; รักษาการขยับตำแหน่งของผู้ใช้บน `art-06` (5524–5756) กับ `side-15` (10357–10613)
- Backup ก่อนกู้: `.hermes/projects/armigon-illustrated/Armigon_illustrated_before_rebuild.drp`; หลังตรวจยังอยู่โปรเจกต์/ไทม์ไลน์/หน้า Edit/folder/playhead เดิม ไม่มีการย้ายหรือแทนที่คลิปใน Resolve
- กู้ timeline แนวตั้ง `FirstPass v2_illustrated_9x16` (ID `967342ca-ba76-45ea-8b88-650c77cffdd7`, 1080×1920/60 fps, 10,827 เฟรม): `v916/top_plate_B.mov` ที่หายถูกสร้างใหม่ตามสูตรต้นแบบของ mockup ใน scratch จาก still source frame 150; ขยาย/เบลอแถบ x470–1350, y0–36, ลดความสว่าง 75%, fade ที่ y630–694
- ไฟล์ใหม่ `v916/top_plate_B.mov` เป็น ProRes 4444 alpha, 300 เฟรม/5 วิ และ Resolve อ่านกลับเป็น Online ทั้ง 37 ชิ้นบน V2 `Top Plate`; V1 21, V3 `REACTIONS` 23, audio 21/20/0 และ Subtitle 177 คงเดิม ไม่มีการแก้ตำแหน่ง timeline; still QC `v916/vertical_restored_frame.png`, source/HTML `v916/`
- `GetClipProperty("Video Codec")` หลัง restore ยังรายงาน `PNG` แม้ `ffprobe` อ่านไฟล์จริงเป็น ProRes; Resolve ส่ง still จาก timeline ได้ถูกต้อง จึงบันทึกเป็น metadata cache ที่อาจเก่า ไม่ใช่หลักฐานว่าไฟล์ออฟไลน์

## ปกคลิป "ทำไมถึงชื่อ Armigon" (2026-10-24)
- ผู้ใช้ยืนยันขอบเขตเป็นปกสองสัดส่วน ไม่ใช่แปลงวิดีโอ; ไม่แก้ Resolve timeline
- ไฟล์ `.hermes/projects/armigon-name/thumb/armigon_name_thumb_16x9.jpg` (1920×1080) และ `armigon_name_thumb_9x16.jpg` (1080×1920), JPEG sRGB <2 MB
- ข้อความ `ที่มาของชื่อ / ARMIGON / แขนหาย?!`; แนวนอนเพิ่ม `ชื่อที่เข้าใจผิดมาตลอด` อิงซับเรื่อง Arm 1 gon และแขนซ้ายหาย ไม่แต่งเหตุการณ์ใหม่
- เฟรม source 659 จาก `ทำไม Name Armigon.mp4`; ฉากป่า forest เดิมจากภาพประกอบ; Mitr Bold สีทอง/ขาวบนเขียวเข้ม จัดสองเลย์เอาต์แยก ไม่ครอปปกนอน
- HTML `thumb/t169/index.html`, `thumb/t916/index.html`; builder `scripts/scratch/armigon_name_covers.py`; QC `thumb/qc/`, รายงาน `thumb/QC.md`

## คลิป "ทำไมถึงชื่อ Armigon" — ภาพประกอบ HyperFrames (2026-10-24)
- โปรเจกต์ `ทำไมถึงชื่อ Armigon`; ต้นฉบับ `FirstPass v2` (51 วิ, 1920×1052, 60 fps, ซับ 52) สำเนา `FirstPass v2_illustrated` ID `83e7cd5c-172f-4ce6-9f46-c90e6749263b`
- 10 ภาพบน V2 `REACTIONS` จาก reel alpha เดียว `name_v3.mov` (แก้ 2 รอบหลังผู้ใช้แจ้ง panel ล้นจอ): full-frame 2 (forest, forge/โอดิน) + กราฟิกมุมซ้ายบน 8 (x 20–560, y 30–520 ซ้ายของเขา) ซับอยู่ราว y 840 ไม่ชน
- งาน/QC: `.hermes/projects/armigon-name/` (`ACCEPTANCE.md`); สคริปต์ `scripts/scratch/build_armigon_name.py`, `scripts/scratch/armigon_name_apply.py`, `scripts/scratch/armigon_name_mock.py`
- 9:16 (2026-10-24): `FirstPass v2_illustrated_9x16` ID `10b4ec54-6dbc-424b-8997-25978fd851d1` ใช้ layout B เดียวกับคลิปแนะนำตัว; ภาพเต็มจอ 2 ช่วงทำใหม่เป็น reel 1080x1920 (`v916/art916.mp4`) แทนการครอป 16:9 เพราะข้อความบนภาพจะถูกตัด; สคริปต์ `scripts/scratch/armigon_name_9x16*.py`, `scripts/scratch/build_armigon_name_art916.py`; `FirstPass v2` ถูกลบออกจากโปรเจกต์ก่อน build (กู้ได้จาก `Armigon_name_illustrated_project.drp`)

## กู้คืน reel ภาพประกอบ `name_v3.mov` และตรวจสอบ timeline (2026-10-26)
- ไฟล์ภาพประกอบ `name_v3.mov` หายไปและ Track V2 แสดง Media Offline ทั้ง 10 คลิป
- กู้คืนโดยสร้าง reel ใหม่ผ่าน HyperFrames ด้วยสคริปต์ใน scratch (build_armigon_name) ที่ `D:\agent-edite-davinci_resolve\.hermes\projects\armigon-name\name_v3.mov` (ProRes 4444 + alpha, 1920x1052, 60 fps, 1,794 เฟรม, 1.69 GB)
- Resolve อ่านคลิปทั้ง 10 ตัวบน V2 กลับมาเป็น Online อัตโนมัติ (0 missing media); แทร็กดั้งเดิม V1, A1, A2, Subtitle 1 มี zero drift
- สำรอง DRP ก่อนและหลัง: `Armigon_name_before_restoration.drp` และ `Armigon_name_illustrated_project.drp`
- ดำเนินการและตรวจรับผ่านระบบ Teamwork Multi-Agent (5 concurrent subagents) พร้อมผ่าน Victory Audit ครบทุกข้อกำหนด
- กู้คืน timeline แนวตั้ง `FirstPass v2_illustrated_9x16`: พบ `top_plate.mov` และ `art916.mp4` ออฟไลน์เนื่องจากโฟลเดอร์ `v916` หายไป; กู้คืน `top_plate.mov` จากต้นฉบับ layout B และเรนเดอร์ `art916.mp4` (1080x1920 @ 60fps) ด้วย HyperFrames ผ่านสคริปต์ใน scratch (build_armigon_name_art916); Resolve อ่านกลับเป็น Online ครบทุกแทร็ก (V1: 10, V2: 11, V3: 10, ST1: 52) รายงาน 0 missing media

## ทำไมถึงชื่อ Armigon — ตรวจปก (2026-10-28)
- โปรเจกต์ Resolve มี FirstPass v2_illustrated และ FirstPass v2_illustrated_9x16; ชื่อซ้ำกับโปรเจกต์แนะนำตัวแต่เป็นคนละโปรเจกต์ ตรวจ project และ source ก่อนจับคู่ปก
- ตรวจ tracks และโฟลเดอร์งาน armigon-name กับ outputs/reports ใน agent-thumbnail แล้ว ยังไม่พบปกที่ยืนยันได้สำหรับคลิปนี้; ปก Armigon_Intro เป็นของคลิปแนะนำตัว
