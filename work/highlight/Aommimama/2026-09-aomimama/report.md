# รายงานงานไฮไลต์ — Aommimama / 2026-09-aomimama

สถานะ: สร้าง assembly timelines ใน DaVinci Resolve ครบ 93 รายการแล้ว ตรวจ readback ครบทั้งสองโปรเจกต์

## ฟุตเทจและการวิเคราะห์

- อินพุต: `Z:\Aommi-mama\2026-09-aomimama` (อ่านอย่างเดียว)
- พบวิดีโอ 13 ไฟล์; `downloaded.txt` ไม่ถูกนับเป็นวิดีโอ
- วิดีโอ H.264, 1920x1080; 12 ไฟล์ 60 fps และ Becastled 002 (v12) 30 fps
- ผู้ใช้กำหนด timeline/project fps เป็น 60 และยืนยัน Playback frame rate 60 ทั้งสองโปรเจกต์แล้ว
- `features`, `shortlist`, `transcribe`, `sheets`, `packets`, `briefs` เสร็จ
- ตรวจ review JSON ครบ 13 ไฟล์: 93 คลิป (6-8 ต่อวิดีโอ), ไม่ซ้อนกัน, ความยาว 30-180 วินาที, อยู่ในขอบเขตต้นฉบับ, ผ่าน schema pytest
- ผลถอดเสียงภาษาไทยมีความผิดพลาด/วนซ้ำหลายช่วง ผู้รีวิวหลายไฟล์เลือกจาก contact sheet เป็นหลัก บทพูด มุก และจุดตัดจึงยังไม่ยืนยัน ต้องดูคลิปก่อนเผยแพร่

## Resolve projects และ timelines

Project Library: `Google drive` / Project Manager path: `Aommi-mama / 2026-09`

- `aomimama-2026-09-p1`: source v01-v07; 49 timelines; fps 60
- `aomimama-2026-09-p2`: source v08-v13; 44 timelines; fps 60
- นำเข้าฟุตเทจของแต่ละชุดใน bin `2026-09-aomimama` ภายในโปรเจกต์ที่ตรงกัน
- รูปแบบชื่อ: `{ชื่อคลิป}-{ชื่อเกม}-vdo`; ไม่ใส่ id/category
- v12 เป็น 30 fps source แต่คำนวณ source frames ด้วย 30 fps และอยู่ใน timeline 60 fps ตามคำสั่งผู้ใช้
- Readback ตรวจครบ: ไม่มีชื่อที่หายหรือเกินจากแผน, ไม่มี archived timeline, ทุก Timeline มีหนึ่ง video item และหนึ่ง audio item เริ่มที่เฟรม 0, source start ตรงแผน, duration ตรงกับอัตรา source/timeline ที่แปลงแล้ว
- รายละเอียดตรวจสอบอยู่ใน `verification.json`; แผนชื่อ/เฟรมอยู่ใน `timeline_plan.json`

## คลิปที่ควรตรวจเป็นพิเศษ

ผู้รีวิวระบุความไม่มั่นใจหรือ ASR ไม่ชัดเจนในหลายคลิป โดยเฉพาะ:

- v01-01, v01-02, v01-05, v01-06, v01-07, v01-08
- v02-01, v02-02, v02-03, v02-04, v02-05, v02-06
- v03-01 ถึง v03-07; review packet ของ v03 ครอบคลุมเพียงช่วงต้นประมาณ 2 ชั่วโมง 24 นาทีจากวิดีโอ 3 ชั่วโมง 13 นาที
- v04-01 ถึง v04-07
- v05-01, v05-02, v05-04, v05-05, v05-07
- v06-01 ถึง v06-07; packet ครอบคลุมช่วงต้นประมาณ 2 ชั่วโมง 19 นาทีจากวิดีโอ 3 ชั่วโมง 49 นาที
- v07-01 ถึง v07-07
- v08-01 ถึง v08-08; packet ครอบคลุมถึงประมาณ 3 ชั่วโมง 27 นาทีจากวิดีโอ 3 ชั่วโมง 37 นาที
- v09-01 ถึง v09-08
- v10-01 ถึง v10-07
- v11-01 ถึง v11-07
- v12-01 ถึง v12-06
- v13-01 ถึง v13-08

รายการทั้งหมดเป็น Assembly เท่านั้น: ไม่ใส่ title, caption, transition, effect, เพลง หรือ grading ไม่มีการ render/export หรือ upload YouTube

## ไฟล์ส่งมอบ

- `inventory.json`, `inventory.md`
- `candidates.json`, `timeline_plan.json`
- `review/v01.json` ถึง `review/v13.json`; briefs และ packets อยู่ใน `review/`
- `verification.json`
