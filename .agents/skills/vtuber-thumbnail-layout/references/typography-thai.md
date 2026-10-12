# Thai Typography & Text Rendering

Source: `src/engine/text_thai.py`, engagement guide §3.3, style guide, QC skill.

## Font & Size

- **ฟอนต์:** Mitr Bold (ค้นหาจาก env, Windows Fonts, `outputs/timeline-covers/fonts/`)
- Hook หลัก: 130–165 px, สีแดง `#EC1C24`, stroke ดำ 12–14 px
- ข้อความรอง: 75–100 px, สีขาว `#FFFFFF`, stroke ดำ 8–10 px
- Stroke ratio: ~8% ของขนาดตัวอักษร

## Thai Layout Engine (libraqm)

- รองรับ complex Thai OpenType: ซ้อนสระ/วรรณยุกต์, ตัวห้อย ป ฝ ฟ, หัว ไ ใ โ
- Ink bbox line stacking — คำนวณบรรทัดจาก ink ไม่ใช่ canvas
- Upper mark collision avoidance — วรรณยุกต์ไม่ทับหัวข้อความ

## ข้อความบนปก

- Hook สั้น 1–4 คำ, อ่านจบเร็ว, 1 วินาที
- Title-Thumbnail Synergy: ปกเน้นอารมณ์/ปมสงสัย, ชื่อคลิปให้บริบท — ห้ามก๊อปชื่อมาวางบนปก
- อย่าสั่งย่อข้อความโดยพลการ — เปลี่ยนการจัดวางแทน
- วางข้อความซ้อนกันไม่ให้มัว/อ่านผิด — แยกตำแหน่ง+น้ำหนัก

## สระ/วรรณยุกต์ Pitfalls

- ขอบดำหนาอุดช่องตัวอักษร → ใช้ RAQM engine, แยกสระออกจากหาง
- ตรวจทุกคำ: consonant, vowel, tone mark, spacing, transliteration, ชื่อเกม/ตัวละคร
- ภาษาไทยไม่เว้นวรรคทุกคำ — อย่าอ่านจากจำนวนตัวอักษร

## QC

- ทดสอบอ่านง่ายที่ 320×180 (mobile) — สระที่อ่านได้บน 1920px อาจกลืนบนมือถือ
- ซูมดูคำที่มี ป ฝ ฟ หรือวรรณยุกต์หน้า ไ ใ โ ว่าขอบดำคั่นจริง
- โหลด `skill_view(name="thai-proofread")` ถ้าไม่แน่ใจข้อความ
