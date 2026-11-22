# Laffy

## ตัวตนและคอนเทนต์
- VTuber ผมขาว สวมโค้ทดำทับเสื้อคอเต่าดำ ห้อยจี้สีฟ้า ฉากหลังเป็นห้องโทนอุ่น อวตาร์อยู่กลางเฟรม (หัวอยู่ราว y 0.10, หน้าอยู่ราว x 0.48 ของเฟรม 16:9)
- แทนตัวเองว่า "ครับ" ชื่อในซับไทยให้เขียน **ลาฟฟี่** (ผู้ใช้ยืนยัน 2026-11-13; Descript ถอดเป็น "ราฟฟี่" ต้องแก้ทุกครั้ง); ชื่อเต็มภาษาอังกฤษ **LaffeyNilvalen** (ผู้ใช้ยืนยัน 2026-11-15, YouTube https://www.youtube.com/@LaffeyNilvalen; Descript ถอดเป็น "RaffyNiveren")
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
  - render `render\laffy_intro_edit_v3.mov` (H.264 + AAC, -14.4 LUFS, peak -0.5 dBFS, 4407 เฟรม) ; v2 ยังเป็นชื่อสะกดผิด, v1 peak 0.0 dBFS (pop -9) ใช้ไม่ได้
  - 2026-11-15 แก้ชื่อ: cue 222-244 `LaffeyNilvalen` (DRT round trip) + การ์ดชื่อ `card01b.mov`; timeline ปัจจุบัน id e9ea6ca9..., เวอร์ชันก่อนแก้เก็บเป็น `เเนะนำตัว 3 นาที_edit_old`
  - ไฟล์งาน `edit\v2\` (backup `.drp`, DRT, cards/png + mov) สคริปต์ `scripts/scratch/laffy_intro/`
  - 2026-11-15 ตรวจซับกับเสียง: cue เดิม (แบ่งตามจำนวนตัวอักษรในช่วง Descript) ช้า/เร็วกว่าเสียงสูงสุด 1.7 วิ (54-58, 99-100, 105-108, 113-116, 130-132 วิ) → จัดเวลาใหม่ 151 cue (ข้อความ Descript เดิม, ใช้ Whisper เป็นตัวอ้างอิงเวลาเท่านั้น ผู้ใช้อนุญาต) timeline ปัจจุบัน id 8eef4c6d..., ก่อนแก้เก็บเป็น `เเนะนำตัว 3 นาที_edit_pre_sync`; render `render\laffy_intro_edit_v5.mov` (-14.4 LUFS, peak -0.5 dBFS, 4407 เฟรม); v4 จัดเวลาผิดช่วง 53-58 วิ ห้ามใช้; ไฟล์ตรวจ `edit\v2\sync\`
  - "ย่า" ต้นคลิป: Descript และ Whisper ได้ยินตรงกัน
  - 2026-11-20 ตรวจซ้ำด้วย CTC forced alignment (`airesearch/wav2vec2-large-xlsr-53-th`): timeline ที่ sync ด้วย Whisper ยังคลาด > 0.2 วิ 35 cue (สูงสุด 1.3 วิ ที่ "อะไรก็ตาม" 58.1 วิ, "มีผู้ชายคน" 25.5 วิ ช้า 1.07 วิ) → จัดเวลาใหม่เป็น timeline `เเนะนำตัว 3 นาที_edit_v2` (id 97525fa1...) 150 cue, V/A ทุกแทร็กเหมือนเดิม; แก้ข้อความตามเสียง: 85.5 วิ "อะไรประมาณเนี้ย", 96.6 วิ "เล่าเรื่องมั่ง", 107.9 วิ "เป็นคลิปมั่ง", รวม "สัมผัสมันเฉยๆน่ะ"; render `render\laffy_intro_edit_v6.mov` (4407 เฟรม, -14.4 LUFS); timeline `_edit` เดิมไม่แตะ, backup `edit\v2\sync\before_subs_v2.drp`, สคริปต์ `scripts/scratch/laffy_intro/retime.py` + `scripts/scratch/laffy_intro/apply_subs_v2.py`; visual QC สุ่มภาพนิ่ง burn-in 6 จุด: ซับถูกต้อง ไม่ทับซ้อน ตรงเฟรม
  - 2026-11-20 การ์ด V3 ทำใหม่ด้วย HyperFrames (ผู้ใช้เลือก: ทำในสำเนา, จังหวะ/ข้อความ/ตำแหน่งเดิม, แอนิเมชันพอดีๆ, SFX เดิม): timeline `เเนะนำตัว 3 นาที_edit_hf` (97563671...) reel เดียว `edit\hf\laffy_intro_cards_hf_v1.mov` + `placements.json`, render `render\laffy_intro_edit_v7_hf.mov` (4407 เฟรม, -14.4 LUFS, peak -0.5); `_edit` (97525fa1...) ยังเป็นการ์ดเก่า รอผู้ใช้สั่งเปลี่ยนเป็นตัวหลัก; ผู้ใช้อนุมัติแล้ว (2026-11-20): ตัวหลัก `เเนะนำตัว 3 นาที_edit` คือ id 97563671... (การ์ด HyperFrames) ส่วนตัวเดิมเปลี่ยนชื่อเป็น `เเนะนำตัว 3 นาที_edit_old` (97525fa1...) แล้วลบตามคำสั่งผู้ใช้ (2026-11-20, ย้อนกลับได้จาก `.hermes/projects/laffy-intro-hyperframes/before_delete_edit_old.drp`) ตอนนี้โปรเจกต์เหลือ `Timeline 1` (ต้นฉบับ) + `เเนะนำตัว 3 นาที_edit`, backup `.hermes/projects/laffy-intro-hyperframes/before_promote_hf.drp`, สคริปต์ `scripts/scratch/laffy_intro/promote_hf.py`; สคริปต์ `scripts/scratch/laffy_intro/build_hf_cards.py`, `scripts/scratch/laffy_intro/apply_hf_cards.py`, `scripts/scratch/laffy_intro/render_hf_v7.py`; งาน `.hermes/projects/laffy-intro-hyperframes/`
  - การ์ด HTML เดิมโหลดฟอนต์ Mitr ผ่าน `file:///` ไม่ติด หัวข้อจึงเป็นฟอนต์ระบบตัวบาง; ฉบับ HyperFrames ใช้ Mitr Bold จริง (หนากว่าเดิม)
  - ยังไม่แน่ใจ (คงข้อความเดิม): 108.5 วิ "ถ้าอยากทำอะนะ" (CTC ได้ยิน "ทำมานะ"), 112.3 วิ "เป็นซะ"/"ไปซะ" คะแนนเท่ากัน; "อ่า" ก่อน Body Horror (80.1 วิ) มีจริงแต่ไม่ใส่เพราะ cue จะเกิน 14 ตัว

## งานเหตุผลที่มาเป็นวี (2026-11-20)
- โฟลเดอร์ `G:\My Drive\laffy_projects\เหตุผลที่มาเป็นวี\` ต้นฉบับ `Timeline 1.mov` 240.4 วิ 7212 เฟรม 1920x1080@30 (-14.3 LUFS, peak -1.2 dBFS)
- Resolve project `เหตุผลที่มาเป็นวี-laffy` (id 7517c948...) : `Timeline 1` (d07360df...) ไม่แตะ, งานตัดคือ `เหตุผลที่มาเป็นวี_edit` (2316193a...)
  - ผู้ใช้สั่ง: ไม่มี hook, ไม่ตัดคำซ้ำ/ติดอ่าง (ทั้งเทคเต็ม), ชื่อ `ทีมมู` (Descript ได้ ทินมู/ทีน), `dreamlight projects` (Descript ได้ Dream Like); ประโยคสุดท้ายที่พูดไม่จบ `เป็นเหตุที่ทำให้ผม` เก็บเสียงไว้แล้วเติมการ์ด `มาเป็น VTuber ทุกวันนี้`; ป้ายบทแบบมุมจอ ไม่ใช่การ์ดเต็มจอ
  - Subtitle `Mitr Font` 251 cue, V2 `VTuber Zoom` 7 ช่วง (window เดิม), V3 การ์ด 18 ใบ, V4 `CHAPTER` ป้ายบท 3 บท, A2 pop -13 (ใบ 1-2 ลด -16) + Record Scratch -15 / Fire Whoosh -19 / Discord Notification -14 / HUH cat -17 / fairy sparkle -16, A3 BGM -22 dB 4 ท่อน fade in 15 / out 90
  - render `render\laffy_reason_edit_v2.mov` (H.264 + AAC, 7212 เฟรม, -14.3 LUFS, true peak -0.5 dBFS: BGM ทำให้พีคเสียงพูดเพิ่มราว 0.4 dB แม้ไม่มี SFX) ; v1 peak -0.4
  - Descript ช่วง 03:03.2-03:07.2 เป็นช่อง 4.000 วิหลอก เสียงพูดต่อเนื่องจริง; Whisper ถอดช่วง 136-144.6 วิเพี้ยน (token เดียวยาว 8 วิ) จึงกระจายเวลาตามช่วงที่มีเสียง
  - ไฟล์งาน `edit\` (backup `.drp`, `transcript\`, DRT, cards, chapters) สคริปต์ `scripts/scratch/laffy_reason/`; รอผู้ใช้รีวิว
  - ตรวจซับกับเสียง (2026-11-20 รอบสอง): ข้อความ Descript ตรงกับเสียงแทบทั้งหมด แต่เวลาคลาด 70 cue เกิน 0.2 วิ (สูงสุด 1.3 วิ ช่วง 1:21-1:31, 2:16-2:20, 3:13-3:15) → จัดเวลาใหม่ด้วย CTC forced alignment ได้ `เหตุผลที่มาเป็นวี_edit_v2` (1c67865c...) 247 cue (รวม cue ที่ยาว 4-6 เฟรม, แยก `กันหน่อยสิครับ | แค่นั้นครับ | ตอนนั้นคือ`, `dreamlight projects` อยู่ใน cue เดียว) แทร็กอื่นเหมือน `_edit` ทุกชิ้น; render `render\laffy_reason_edit_v3.mov` (7212 เฟรม, -14.3 LUFS, peak -0.5)

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
- งานเหตุผลที่มาเป็นวี (2026-11-21), timeline id `ccf99faf-35fc-4045-9f05-839d7460336e`: ผู้ใช้สั่งขยายภาพประกอบที่เล็กจาก `short` (confirmed: ข้อความพร้อมภาพ card02). ปรับ V3 ทั้ง 18 ใบด้วย MCP เป็น Zoom 2.087, Pan สลับ -798.1/+798.1, Tilt -2200; render กลางทุกใบอยู่ใต้ซับ ไม่บังหน้า (agent-verified; รอผู้ใช้รีวิวขนาด/ตำแหน่งสุดท้าย). จังหวะและทุกแทร็กนอก V3 เหมือนเดิม รวมซับ 247 cue; ไม่แก้ V4 ป้ายบท. หลักฐาน local `.hermes/projects/laffy-reason-vertical/qc_enlarged_final/sheet.jpg`, `enlarge_final_verified.json`; backup `before_enlarge_cards.drp`. ใช้เฉพาะงานนี้ ไม่แทน layout ด้านบนที่อนุมัติในงานแนะนำตัว.
- งานแนะนำตัว 3 นาที (2026-11-20): `เเนะนำตัว 3 นาที_edit_9x16` (248bdf61...) ผู้ใช้เลือก 1a 2a 3a + การ์ด 1.0 เท่า
  - ซับ preset `Mitr-short-001` (จาก User.db library หลัก ผ่าน `drt_set_subtitle_preset.py` + import DRT) อยู่ y ~940–1056 ใต้คาง
  - V1 Zoom 3.1605 Pan +66.56 (ผมขาวกว้าง source x 0.403–0.558, หัว y 0.226)
  - V2 Fusion Transform: Size 1.3158 เท่าเดิม (เพดานไม่ตัดผม 1.55) Center (0.4813, 0.5395) = เล็ง source y 0.53 ให้คาง (~0.505) อยู่เหนือซับ; ถ้าใช้ Center y เดิม 0.3947 ซับทับตา/ปาก
  - V3 การ์ดเป็น reel HyperFrames แนวตั้งโดยตรง **ผู้ใช้อนุมัติใช้แทน `short`** สำหรับการ์ด HyperFrames ของ Laffy; ตำแหน่งที่ผู้ใช้ต้องการคือ**ด้านบนจอ** (สั่งย้ายรอบ 2, 2026-11-20): `edit\hf\laffy_intro_cards_hf_916_v2.mov` การ์ด 460x360 cx 540 cy 215 = y 35–395 เหนือผม (~434; ไม่มีการ์ดใบไหนอยู่ในช่วงซูม V2) render `render\laffy_intro_edit_9x16_v2.mov` (4407 เฟรม, -14.4 LUFS, peak -0.5); v1 เดิมวางใต้ซับ (cy 1255) ใช้ไม่ได้แล้ว
  - render `render\laffy_intro_edit_9x16_v1.mov` (การ์ดใต้ซับ แทนที่ด้วย v2); 2 cue กว้างเกิน 1080: `Body Horror น่ะพวกแบบ` (~2429), `กด Subscribe ให้หน่อยนะ` (~4305) รอผู้ใช้ตัดสินใจแยก
  - สคริปต์ `scripts/scratch/laffy_intro/build_9x16.py` (subs|frame|cards|verify), `scripts/scratch/laffy_intro/build_hf_cards.py --vertical`, `scripts/scratch/laffy_intro/render_review.py`
- `Timeline 1_9x16` (1080x1920) สร้าง 2026-11-14 จาก `Timeline 1` เฉพาะการจัดเฟรม ไม่ตัด ซับและเสียงเหมือนต้นฉบับ ตอนสร้างไม่ได้ตรวจว่ามีอยู่ใน Resolve จริงหรือไม่ ต้องตรวจก่อนใช้
- V1 Zoom 3.1605 (เต็มความสูง) หัวครบ ไม่มีขอบดำ
- การ์ด V3 วางกลางช่วงอก (y ~1180) แทน preset `short`: แผงขวา Zoom 1.234 Pan -446 Tilt -261, แผงซ้าย Pan +446, Kaiju Zoom 0.982 Pan 0 Tilt -277 **ผู้ใช้ยังไม่อนุมัติให้ใช้แทน `short`** ให้ถามก่อนใช้ซ้ำ (skill `talking-avatar-vertical-copy`)
- render ตรวจภาพ (ไม่มีเสียง) ซับ Mitr Font อยู่ y ~0.85–0.95 ไม่ล้นขอบ การ์ดไม่บังหน้า

## งาน "รู้จัก Yu-Gi-Oh ได้ยังไง" (2026-11-15)
- library `laffy_project` โปรเจกต์ `รู้จัก Yu-Gi-Oh ได้ยังไง` ขนาด 1920x1080 30 fps ฟุตเทจ OBS 720p อยู่ที่ `Z:\laffy\รู้จัก Yu-Gi-Oh ได้ยังไง\` (เป็นไฟล์ media ไม่ใช่ library Drive Z ให้อ่านอย่างเดียว)
- timeline ต้นฉบับ `รู้จัก Yu-Gi-Oh ได้ยังไง-vdo` (id 0dd3efe9..., 1323 เฟรม) layout ต่างจากงาน 004:
  - V1 ฟุตเทจตัดเป็น 23 ชิ้น
  - V2 Adjustment Clip 10 ตัว ซูมด้วย Inspector 1.28/1.54/2.03x
  - V3 รูปเต็มจอ 8 รูป
  - V4 ซับ Text+ 61 ตัว ฟอนต์ Mitr Size 0.07 ที่ y 0.12
  - ST1 ปิดอยู่
  - A1 เสียงพูด, A2 BGM, A3/A4 SFX
- `รู้จัก Yu-Gi-Oh ได้ยังไง-vdo_9x16` (id fdee0121...) สร้าง 2026-11-15 ตั้ง V1 Zoom 3.1605 Pan +83.6 (ให้ผมอยู่กลางเฟรม) และย่อซูม V2 ตามสัดส่วนเป็น 1.06/1.12/1.23x ผู้ใช้เลือกวิธีนี้
- V3 ตอนแรกใช้ preset `short` แล้วรูปบังหน้าทุกรูป ผู้ใช้สั่งให้รูปเต็มจอ (2026-11-15) จึงตั้งทั้ง 8 รูปเป็น cover zoom 1.25–3.56 Pan/Tilt 0 แล้ว รูปกว้างจะโดนตัดข้างกลางภาพ (`hq720.jpg` ตัวอักษรมีมเหลือ "WAS T…")
- ซับ Text+ บน 9:16 จะเล็กลงเหลือ 56% ของขนาดเดิม ผู้ใช้สั่งให้ขยาย (2026-11-15) จึงตั้ง Size 0.12 ทั้ง 61 ตัวในสำเนา 9:16 ส่วนต้นฉบับยังเป็น 0.07 ประโยคยาวสุดกว้างราว 2/3 ของเฟรม ไม่ล้นขอบ
- backup: `.hermes/projects/laffy-yugioh/backup/pre_9x16_*.drp`
- ซับย้ายไป Subtitle track แล้ว (2026-11-15):
  - ทั้งสอง timeline เปิด ST1 และปิด V4 Text+ (เก็บคลิปไว้ ไม่ได้ลบ)
  - preset มาจาก library หลัก `G:\My Drive\Projects\Resolve Project Library` ผู้ใช้เลือกเอง: แนวนอนใช้ `Mitr Font` แนวตั้งใช้ `Mitr-short-001` (library `laffy_project` ไม่มี preset)
  - timeline ใหม่ใช้ชื่อเดิม id `0a2caab9...` (16:9) และ `e68deda7...` (9:16) ส่วนของเก่าเก็บไว้เป็น `_old`
  - ซับ 9:16 อยู่ที่ y ~0.49–0.55 ใต้คาง เดิมมี 2 cue ที่กว้างเกิน 1080 ผู้ใช้สั่งแยก (2026-11-15) ตอนนี้ 9:16 มี 63 cue: `ทุกวันเสาร์ | อาทิตย์เลยครับ` แยกที่เฟรม 726 และ `เรื่องนั้นคือเรื่อง | Yuki-o` แยกที่เฟรม 768 ส่วน 16:9 ยังเป็น 61 cue เหมือนเดิม

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
