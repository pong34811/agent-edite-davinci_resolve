# Landscape 16:9 (1920×1080) — Layout Rules

Source: `src/engine/layout.py::LandscapeLayout`, `compositor.py::composite_landscape`, engagement guide §4.1, style guide.

## Zones

| Zone | Bounds | Purpose |
|---|---|---|
| Text Safe Zone (Center-Left) | `x: 80–930`, `y: 380–520` | Hook หลัก + ข้อความรอง |
| Avatar Zone (Right) | `x: 950–1850` | VTuber model, 35–50% ความกว้างเฟรม |
| Timestamp Badge (DANGER) | `x: 1580–1900`, `y: 980–1060` | ห้ามวางใบหน้า/ข้อความ |
| Bottom Scrubber | `y: 1062–1080` | หลบแถบเลื่อน |
| Hover Actions | `x: 1780–1900`, `y: 20–160` | ปุ่ม Like/Share |
| Min Outer Margin | `≥40 px` ทุกขอบ | ป้องกัน crop แพลตฟอร์ม |

## Layer Order (bottom → top)

1. Background ( gameplay: 0 px blur + brightness 0.90 + contrast 1.08 ; คุย: blur 50 px + dim 128 alpha)
2. Backdrop Gradient Mask (ซ้ายสุด `x: 0–980`, fade cosine, alpha ≤0.65) — ให้อ่านข้อความบนเกมโดยไม่เบลอ footage
3. Avatar (with 5-layer separation: white stroke 12 px + shadow dx=10 dy=14 blur 16)
4. Focus Circle (`#EC1C24` hand-drawn loop, ล้อมจุดเกิดเหตุ)
5. Emotion Marker (`!` แดงส้ม เอียง -12° / `?` ฟ้าคราม เอียง +12°)
6. Text Layer (hook สีแดง ข้อความรองสีขาว)

## Text Rendering

- Hook: Mitr Bold, 130–165 px, สีแดง `#EC1C24`, stroke ดำ 12–14 px
- Secondary: Mitr Bold, 75–100 px, สีขาว `#FFFFFF`, stroke ดำ 8–10 px
- `y_cursor` เริ่มที่ 380, เว้นบรรทัด `size * 1.15 + 20`
- Max width 850 px, center-left alignment

## Expression → Hook Mapping (excerpt)

- Shock/Panic → `!` marker, ตาเบิก, ปากอ้า
- Horror/Dread → หน้าถอดสี, เงาม่วง
- Hysterical Laugh → ตาหยี, น้ำตา
- Despair/Crying → คิ้วตก, น้ำตา
- Adore/Heartfelt → ตาหัวใจ, แก้มแดง

## Gameplay vs Talk Background Rule

- เกม: 0 px blur (จำเกมได้ 1 วินาที) + Gradient Mask ซ้าย
- คุย/เดบิวต์: blur 46–60 px + brightness 0.50
