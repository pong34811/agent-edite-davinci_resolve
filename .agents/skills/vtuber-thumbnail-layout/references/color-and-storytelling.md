# Color, Storytelling Elements & Background Logic

Source: engagement guide §5, style guide §สิ่งที่เห็นซ้ำ, src/engine/graphics.py.

## Color Tokens

- Red accent: `#EC1C24` (236, 28, 36) — สงวนไว้เฉพาะ hook หลักจุดเดียว
- White: `#FFFFFF` — ข้อความรอง
- Black: `#000000` — stroke, shadow
- Red marker: `(255, 46, 46)` — `!`
- Cyan marker: `(0, 229, 255)` — `?`
- Gradient mask base: `(4, 8, 20)`

## Storytelling Elements

- **Hand-drawn Red Circle** — วงรีเบี้ยวเล็กน้อย, เส้นเหลื่อม, ล้อมจุดเกิดเหตุ (เกม: เพื่อนล้ม, บอส, ไอเทม)
- **Manpu `!`** — เอียง -10° ถึง -15°, ส้มแดง, ลอยข้างศีรษะ (ตกใจ)
- **Manpu `?`** — เอียง +10° ถึง +15°, ฟ้าขาว (สงสัย)
- **Sweat drop** — ตกที่นั่งลำบาก; **Anger mark** — เส้นเลือดปูด

## Background Logic

| คลิป | Blur | Brightness | Mask |
|---|---|---|---|
| เกม/ไฮไลท์ | 0 px | 0.90 | Gradient ซ้าย `x:0–980` |
| คุย/เดบิวต์/สไลด์ | 46–60 px | 0.50 | Dim overlay |

## 5 Archetypes

1. Gaming/Horror — 0 blur + อวาตาร์ช็อก + วงกลมแดง + hook ตัวโต
2. Zatsudan — เบลอ 50 px + อวาตาร์ใหญ่ 50% + hook ปริศนา
3. Karaoke — Mood tone ตามเพลง + Rim Light ละมุน
4. Collaboration — โฮสต์ขวา + หัวเพื่อนซ้าย + สแลคกลาง
5. Milestone/Debut — Silhouette 100% + Rim Light เรือง + สีทอง-ม่วง

## ห้าม

- ลูกศร/วงกลม/emoji เฉย ๆ — ต้องมี job ชี้ไปยังเหตุการณ์จริง
- ใส่ชื่อ/ยอดติดตาม/เลขตอน/โลโก้เกมที่ไม่มีหลักฐาน
- คัดลอก asset ศิลปินโดยไม่ได้รับอนุญาต
- ทำทุกปกให้มีวงกลม/กราฟิก — ใช้เฉพาะเมื่อชี้เหตุการณ์ได้
