# Laffy

## ตัวตนและคอนเทนต์
- VTuber ผมขาว สวมโค้ทดำทับเสื้อคอเต่าดำ ห้อยจี้สีฟ้า ฉากหลังเป็นห้องโทนอุ่น อวตาร์อยู่กลางเฟรม (หัวอยู่ราว y 0.10, หน้าอยู่ราว x 0.48 ของเฟรม 16:9)
- แทนตัวเองว่า "ครับ" ในคลิป Descript ถอดชื่อที่พูดตอนทักทายว่า "ราฟฟี่" (ยังไม่ได้ยืนยันกับผู้ใช้ว่าสะกดแบบไหน)
- คอนเทนต์: แนะนำการ์ด Yu-Gi-Oh! (Master Duel) และหัวข้อแนะนำตัว เช่น เกมที่เล่น, เหตุผลที่เป็น VTuber, รู้จัก Yu-Gi-Oh ได้ยังไง

## ที่เก็บไฟล์
- งานตัดต่อ: `G:\My Drive\laffy_projects\<เลขงาน>\` เช่น `004` แนะนำการ์ด Underworld Goddess
  - ในโฟลเดอร์มี `Timeline 1.mov` (1080p30 ที่ export มาแล้ว), ไฟล์ OBS ดิบ 720p และโฟลเดอร์รูปการ์ดแยกตามการ์ด
  - ไฟล์ที่ agent สร้าง (backup, ซับ, overlay, zoom DRT, QC) อยู่ใน `<งาน>\edit\`
- ฟุตเทจเก่า: `C:/Users/warit/SynologyDrive/laffy/` (มีแต่โฟลเดอร์หัวข้อ)

## โปรเจคและ timeline ใน Resolve
- Library `laffy_project` มีโปรเจกต์ `ตัวการ์ด Underworld Goddess-Yu-Gi-Oh! Master Duel` ที่ 1920x1080, 30 fps
  - `Timeline 1` คือต้นฉบับ ห้ามแก้
  - `Underworld Goddess_edit` คืองานที่ตัดเสร็จ
  - `Underworld Goddess_edit_pre_zoom` คือสำเนาสำรองก่อนใส่ซูม

## รูปแบบและ layout (16:9)
| แทร็ก | ใช้สำหรับ |
|---|---|
| V1 | `Timeline 1.mov` ทั้งไฟล์ ไม่ตัด |
| V2 | `VTuber Zoom` เป็น Fusion Transform 1.32x (window บน 0.04 ล่าง 0.80, cx 0.485) |
| V3 | `REACTIONS` รูปการ์ด |
| A2 | `SFX` |
| A3 | `BGM` |
| ST1 | `Thai` |

- รูปการ์ดใบเดียว: สูง 860 px อยู่ด้านขวา (cx 1560) หรือซ้าย (cx 360) ของอวตาร์
- การ์ดหลายใบ (เช่น Kaiju 6 ใบ): สูง 520 px แบ่งเป็นพัดซ้าย 3 ใบ ขวา 3 ใบ ไม่บังหน้า
- ใบแรกที่พูดถึงการ์ดใช้แบบ overframe ส่วนตอนอธิบายเอฟเฟกต์ใช้การ์ดแบบธรรมดา

## ซับ เสียง และ enrichment
- ซับ: ใช้ Descript (`language: auto`) แล้วแบ่ง cue ด้วยมือ ตามกฎ house-style ไม่เกิน 14 ตัวอักษร ไม่เกิน 1.5 วิ
  - ใช้ชื่อการ์ดภาษาอังกฤษ (Underworld Goddess, I:P Masquerena, Kaiju) และเขียนตัวเลขเป็นตัวเลข
- เสียงพูดดัง (-14.2 LUFS, peak -1.1 dBFS) BGM ใช้ระดับประมาณ -22 dB และ SFX ไม่เกิน -3 dB
- ยังไม่มี preset สไตล์ซับของช่องนี้ (ตอนนี้ใช้ default ไม่มีขอบตัวหนังสือ)

## Script และ skill ที่เกี่ยวข้อง
- `scripts/card_pop_overlay.py` (รูปการ์ดเด้ง), สคริปต์ขั้นตอนของงาน 004 อยู่ในโฟลเดอร์ scratch ชื่อ laffy004 (gitignored: backup, build_subs, subs_insert, zoom, audio, levels, verify)
- skill: `resolve-video-enrichment` (illustration-assets), `thai-subtitles-resolve`, `vtuber-content-curriculum`

## กับดักและงานค้าง
- ซับสีขาวไม่มีขอบทับเสื้อดำ จี้สีฟ้าโผล่ผ่านตัวอักษรบางคำ ควรใช้สไตล์ที่มีขอบ
- รอผู้ใช้ตัดสินใจเรื่องสไตล์ซับ และยืนยันการสะกดชื่อ ราฟฟี่/ลาฟฟี่

## ยังไม่ทราบ (ถามผู้ใช้ก่อนเดา)
- preset ซับที่ช่องต้องการ และการสะกดชื่อช่องเป็นภาษาไทย
