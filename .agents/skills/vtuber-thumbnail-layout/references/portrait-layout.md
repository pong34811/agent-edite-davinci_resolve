# Portrait 9:16 Shorts (1080×1920) — Layout Rules

Source: `src/engine/layout.py::ShortsLayout`, `compositor.py::composite_shorts`, engagement guide §4.2, style guide Shorts section.

## Zones

| Zone | Bounds | Purpose |
|---|---|---|
| Text Safe Zone (Top) | `x: centered`, `y: 280–650` | Hook + ข้อความรอง |
| Avatar Zone (Bottom) | `y: 700–1100` (head), ฐานยึดขอบล่าง | VTuber model |
| Feed UI Bottom (DANGER) | `y: 1350–1920` | ชื่อคลิป, แอคเคาท์, เพลง |
| Feed Action Stack | `x: 880–1080`, `y: 800–1750` | Like/Comment/Share |
| Channel Grid 4:5 Crop | `y: 285–1635` | ตัดบน-ล่างด้านละ 285 px |
| Search 3:4 Crop | `y: 240–1680` | ตัดบน-ล่างด้านละ 240 px |

## Layer Order (bottom → top)

1. Background (brightness 0.90)
2. Avatar (centered horizontally, ฐานล่าง)
3. Emotion Marker (ถ้ามี)
4. Text Layer (hook สีแดง `y_cursor=320`, ข้อความรองขาว)

## Text Rendering

- Hook: Mitr Bold, 150–100 px (fit_text auto-shrink), stroke 8%
- Secondary: Mitr Bold, 90–60 px, stroke 8%
- `x` เริ่ม 70, `y_cursor` เริ่ม 320
- Max width 940 px, กึ่งกลางแนวนอน `x=540` tolerance 15 px

## Shorts-Specific Rules

- จัดข้อความ + โมเดลให้อยู่กึ่งกลางแนวนอน — อย่าชิดขอบ
- หลีกเลี่ยงขอบล่าง 25% และขวา 20%
- ตรวจ 4:5 Channel Grid Crop: องค์ประกอบสำคัญอยู่ใน `y 285–1635`
- Shorts ต่างจากแนวนอน: จัดใหม่ตาม 9:16 ไม่ครอปแนวนอนแล้วอ้างว่าเป็น Shorts
- Hook Zone อยู่บน, Avatar Zone อยู่ล่าง — เล่าเรื่อง top→bottom

## Channel Profile Note

- KATY404 Shorts: ใบหน้าขนาดใหญ่เด่น (หน้า 86, 171), hook เหนือศีรษะ, อวาตาร์ล่าง
- อย่าตัดขอบปกแนวนอนมาทำ Shorts — เลือกหน้าคู่กันจากคอลเลกชัน Shorts แล้วจัดจุดเด่นใหม่
