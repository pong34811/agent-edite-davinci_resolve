---
name: vtuber-cover-source-video
description: Build YouTube covers from video, character-free background.
version: 0.1.0
author: Hermes
license: MIT
metadata:
  hermes:
    tags: [VTuber, Thumbnail, Cover, ffmpeg, Background]
---

# VTuber Cover from Source Video

Builds 16:9 + 9:16 YouTube covers straight from a source video file: ffmpeg extracts frames read-only, Pillow composites the channel's model PNG over a background region that contains no character, and headless Chrome renders the Thai hook because Pillow has no RAQM. It does not drive Resolve and does not need the agent-thumbnail repo. The hard part is the background — the in-stream model is often baked into every frame — so the skill centres on measuring where the model actually is and cutting the room beside it.

## When to Use

- "ทำปกคลิป", "ทำ thumbnail จากไฟล์วิดีโอ", "ปกปี 2026 จากโปรเจค"
- "พื้นหลังปกมีตัวละคร", "เลือกพื้นหลังที่ไม่มีตัวละคร", "พื้นหลังรบกวน"
- ผู้ใช้ขอให้ใส่รูปตัวละครทับ และเอาตัวละครออกจากพื้นหลัง
- ต้องการปกโดยไม่ต้องแตะ Resolve timeline

## Prerequisites

- `ffmpeg` อยู่บน PATH (อ่านต้นทางเท่านั้น ห้ามเขียนทับ)
- Python ที่มี `numpy` + `Pillow`
- Chrome (Windows ค่า default `C:\Program Files\Google\Chrome\Application\chrome.exe`) — ข้อความไทยต้องผ่าน Chrome เพราะ Pillow ไม่มี RAQM สระ/วรรณยุกต์จะเพี้ยน
- ฟอนต์ `C:\Windows\Fonts\Mitr-Bold.ttf` หรือฟอนต์ที่ช่องยืนยัน
- โมเดล PNG มี alpha จากโฟลเดอร์ `1.picture` ของช่อง

## How to Run

เรียกสคริปต์ผ่าน `terminal` tool:

```
python .agents/skills/vtuber-cover-source-video/scripts/character_free_bg.py --source "<source.mp4>" crop --frame <N> --side LR --out bg.png
python .agents/skills/vtuber-cover-source-video/scripts/character_free_bg.py --source "<source.mp4>" scan --around-frame <N> --out scan.json
```

## Quick Reference

- `scan` → JSON ต่อ sample: `frame`, `bbox`, `left`, `right`, `both` (=left+right) เลือก `both` มากสุด
- `crop --side L|R|LR` → PNG ของช่องที่ไม่มีตัวละคร; `LR` = ซ้าย+ขวาจากเฟรมเดียวกันต่อกัน
- hair mask: `B > R+70 and B > G+70`; นับเป็นโมเดลได้ก็ต่อเมื่อ bbox สูง > 400 px และ y0 < 200
- `--pad` (default 10 px) ระยะเว้นรอบ bbox; `--fps` (default 30)
- ฉากหลัง: ห้องนอน L|R ใช้ blur 2; หน้าคอมเมนต์ใช้ blur 8 ตามที่ช่องอนุมัติไว้

## Procedure

1. **ตรวจต้นทาง** — อ่านขนาด/ความยาว/fps แล้วแยก layout ด้วยความสว่างเฉลี่ย (ห้องสว่าง vs หน้า UI มืด) อย่าเดาจากชื่อไฟล์
2. **สแกนหยาบ** ทุก 10 วิ หาเฟรมที่ไม่มีตัวละครทั้งเฟรม ถ้าตัวละครอยู่กลางจอตลอดคลิป เฟรมว่างจะมีแต่ช่วงเปิด/ปิดสตรีม — และช่วงเหล่านั้นมักเป็นภาพประกอบของตัวละคร ต้องดูก่อนใช้
3. **สแกน fine** ด้วย `scan` รอบ evidence frame (±120 วิ ทีละ 3 วิ) เรียงตาม `both`
4. **ตัดฉาก** ด้วย `crop` จากเฟรมที่ชนะ สคริปต์วัด bbox บนเฟรมนั้นจริง ๆ อีกครั้งเสมอ
5. **ประกอบปก** — ฉากหลัง (blur ตามที่อนุมัติ) + โมเดล crop ตาม alpha bbox + hook แดง `#EC1C24` และบรรทัดรองขาว ผ่าน Chrome ด้วย Mitr Bold; ข้อความจาก subtitle cue จริงเท่านั้น
6. **QC สองชั้น** — ตัวเลข (ขนาด, hook แดง, ข้อความขาว, จำนวน hair/skin px ในฉาก) แล้ว `vision_analyze` ยืนยันไม่มีตัวละครในฉากหลัง
7. **ส่งมอบ** — `<timeline>.jpg` + `manifest.json` ไปโฟลเดอร์ที่ผู้ใช้ระบุ ฝากชุดก่อนไว้ `vN/` แทนการเขียนทับ แล้วสร้าง contact sheet
8. **บันทึกบทเรียน** — ช่องที่ `docs/channels/<slug>.md` และ skill นี้ พร้อมรัน `pytest` + `refresh_skill_manifest.py`

## Pitfalls

- `fps=1/10` กับ `ffmpeg -ss` ไปเจอเฟรมคนละอันกัน (bbox ผมต่างกันถึง 600 px) — ห้ามตัด crop จาก bbox ที่วัดบนเฟรมอื่น
- hair mask ได้ false positive จากสีน้ำเงินในเกมและสีน้ำเงินในห้อง ต้องกรองให้ bbox ดูเป็นตัวละคร (สูง เริ่มใกล้ๆ ด้านบน) ก่อนเชื่อ
- อวาตาร์จอเล็กมุมขวาล่างใน layout หน้าคอมเมนต์มักหลุดเข้า crop ที่ "กว้าง" — วัดขอบซ้ายจริงด้วย column profile บนเฟรมนั้น แล้วเว้นให้พอ
- เฟรมเปิด/ปิดสตรีมไม่ได้ปลอดภัยโดยอัตโนมัติ มักมีภาพประกอบตัวละคร
- ซูมช่องห้อง ~300 px ให้เต็ม 1920 px จะนุ่ม — รายงานตรง ๆ ว่าดูใกล้จะนุ่ม อย่าอ้างว่าฉากคม
- ผล `vision_analyze` อาจผิด ใช้ pixel mask ยืนยันก่อนแก้อะไร
- ห้ามเขียนทับฟุตเทจต้นทาง; เขียนเฉพาะไฟล์ปกและสคราช

## Verification

```
python .agents/skills/vtuber-cover-source-video/scripts/character_free_bg.py --source "<source.mp4>" crop --frame <N> --side LR --out bg.png
```

ยืนยันด้วย `vision_analyze` ว่าฉากหลังไม่มีตัวละคร และปกที่ประกอบเสร็จต้องผ่านทั้ง check ตัวเลข (hair mask px, hook แดง, ข้อความขาว) และ `vision_analyze` ทุกใบ
