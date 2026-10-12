# Avatar Placement & Model Separation

Source: `src/engine/graphics.py::apply_avatar_separation`, engagement guide §2, style guide §สิ่งที่เห็นซ้ำ.

## 5-Layer Separation

1. **White/Neon Contour Stroke** — หนา 8–18 px, รอบตัวโมเดล, ป้องกันผมกลืนฉาก
2. **Directional Drop Shadow** — `dx=8–12, dy=12–18, blur 14–20 px` สีดำใต้ stroke
3. **Rim Light** — แสงเรืองขอบผม+ไหล่ เน้นมิติ 3D
4. **Local Darkening / Backdrop Gradient Mask** — เงามืดบริเวณที่โมเดลพาด
5. **Avatar Alpha** — แม่พิมพ์โปร่งใส, วางจากพื้นที่มองเห็นไม่ใช่ผืน PNG ทั้งใบ

## Engine Defaults (compositor.py)

- `stroke_width=12`, `stroke_color=(255,255,255)`, `shadow_offset=(10,14)`, `shadow_blur=16`, `shadow_opacity=0.7`
- Landscape: avatar วางขวา `av_x = 1920 - width + 60`, `av_y = ฐานล่าง`
- Shorts: avatar กึ่งกลาง `av_x = (1080 - width) // 2`, `av_y = ฐานล่าง`

## Gaze Direction

- **Direct Eye Contact** — กระตุ้น amygdala, สร้าง parasocial intimacy → VOD คุย, เดบิวต์, challenge
- **Gaze Cuing** — สายตามองตามอวาตาร์ไปยัง focal point → เกมไฮไลท์, ชี้ hook ข้อความ

## Expression Matrix (จับคู่กับคลิป)

| อารมณ์ | Visual | ไคลแมกซ์ | Hook ตัวอย่าง |
|---|---|---|---|
| Shock/Panic | ตาเบิก, ปากอ้า, `!` | โดนลอบยิง | "ช่วยด้วย!" |
| Horror | หน้าถอดสี, เงามืด | เกมผี | "อย่าหันไป" |
| Hysterical Laugh | ตาหยี, น้ำตา | บั๊กฮา | "ทำไปได้ไง" |
| Smug/Sadistic | สบประมาท, ยิ้มมุม | ชนะล้วง | "ไม่เห็นจริงดิ" |
| Despair | คิ้วตก, น้ำตา | เกมเซฟพัง | "หายหมดแล้ว" |
| Adore | ตาหัวใจ, แก้มแดง | ฉลอง | "รักที่สุด" |

## Pitfalls

- อย่าใช้สีหน้านิ่ง/ยิ้มบาง — เกิด Deadpan Doll Effect
- อย่าเรียก pose เกินกว่าที่ภาพจริงสื่อ (ตกใจ/เศร้า/โมโห)
- ถ้าไม่มี pose ตรง ใช้ pose กลาง + แจ้งข้อจำกัด
- ตรวจ alpha bounding box ก็วาง — อย่าจากผืน PNG ทั้งใบ
