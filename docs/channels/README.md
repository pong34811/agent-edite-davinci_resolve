# docs/channels/ — โปรไฟล์ช่อง

เมื่อผู้ใช้พูดถึงช่องหรือชื่อโปรเจคด้านล่าง ให้อ่านโปรไฟล์ของช่องนั้นก่อนเริ่มงาน (ต่อจาก `house-style` และ `docs/OPERATING-NOTES.md`) โปรไฟล์บอกว่าไฟล์อยู่ที่ไหน ใช้ preset อะไร เคยพังตรงไหน และ script ไหนใช้กับช่องนี้ได้

| ช่อง | โปรไฟล์ | โปรเจค Resolve ที่รู้จัก | สถานะ |
|---|---|---|---|
| Katy404 (KT404) | [katy404.md](katy404.md) | ซีรีส์ Minecraft "ปลูกข้าวจนกว่าจะ 10K" (day 22, day 24) | ทำงานแล้ว |
| Aomi-mama | [aomimama.md](aomimama.md) | `aomimama-2026-09-p1`, `aomimama-2026-09-p2` | ทำงานมากที่สุด |
| Armigon | [armigon.md](armigon.md) | `armigon-2026-09` | ทำงานแล้ว |
| Tygarina | [tygarina.md](tygarina.md) | `tygarina_2026-09-30` | ทำงานแล้ว |
| Sakuyako-Cheris | [sakuyako-cheris.md](sakuyako-cheris.md) | `sakuyako-2026-09` | ทำงานแล้ว |
| Laffy | [laffy.md](laffy.md) | ยังไม่พบ | ข้อมูลน้อย |
| Kael | [kael.md](kael.md) | ยังไม่พบ | ข้อมูลน้อย |

## กติกาการใช้และการอัปเดต

- ข้อมูลในโปรไฟล์มาจากหลักฐานใน repo, memory ของ agent และการดูโฟลเดอร์ต้นทางแบบอ่านอย่างเดียว ไม่ใช่การตรวจ Resolve สด ต้องยืนยันชื่อโปรเจค/timeline/IDs จาก Resolve ทุกครั้งก่อนเขียน
- หัวข้อ "ยังไม่ทราบ" คือสิ่งที่ต้องถามผู้ใช้ อย่าเดา และเมื่อได้คำตอบให้ย้ายขึ้นไปหัวข้ออื่น
- จบงานของช่องไหน ให้อัปเดตโปรไฟล์นั้นตาม `.agents/skills/project-learning/SKILL.md`: โปรเจค/timeline ใหม่, preset ที่ผู้ใช้ยืนยัน, กับดักใหม่, งานค้าง
- กฎที่ใช้กับทุกช่อง (ซับ ≤14 ตัวอักษร ≤1.5 วิ, โครงสร้าง track ฯลฯ) อยู่ใน `AGENTS.md` และ `house-style` ไม่ต้องคัดลอกมาที่นี่

## ที่เก็บไฟล์ต้นทางร่วม

- `C:/Users/warit/SynologyDrive/<ช่อง>/` — ฟุตเทจและสื่อดิบในเครื่อง (อ่านอย่างเดียว ห้ามเขียนทับ)
- `G:/.shortcut-targets-by-id/1EfyfEGeG4UTUmNzTR2IDLUPjm386Fqlu/Projects/<ช่อง>/` — Google Drive ของโปรเจค (ไฟล์ส่งมอบ `vdo`, thumbnail, `_SHARED_ASSETS` ที่มี bgm / SFX / GIF ร่วม)
- BGM / SFX / GIF ส่วนกลาง: `SynologyDrive/1.bgm`, `2.1_sfx`, `3.gif` และ `Projects/_SHARED_ASSETS`

## แม่แบบสำหรับช่องใหม่

คัดลอกหัวข้อจากไฟล์ใดก็ได้ในโฟลเดอร์นี้ ต้องมีครบทั้ง 8 หัวข้อ (`tests/test_channel_profiles.py` ตรวจ) แล้วเพิ่มแถวในตารางด้านบน
