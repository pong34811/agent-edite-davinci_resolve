---
name: sfx-story-analyzer
description: "วิเคราะห์คลิปวิดีโอจาก subtitle track แล้ววาง SFX ให้ตรงจังหวะ story arc — ใช้เมื่อต้องการใส่ SFX ให้คลิปที่มี subtitle/subtitle track อยู่แล้ว, ต้องการวิเคราะห์ว่าจังหวะไหนควรใส่ SFX, ต้องการให้ AI คิดเหมือน Video Editor ที่เข้าใจเนื้อหา, หรือต้องการ workflow ที่อ่าน subtitle ก่อนค่อยตัดสินใจวาง SFX — ใช้กับทุกรูปแบบ: talking-head, gaming, vlog, podcast, meme, livestream"
---

# SFX Story Analyzer

วิเคราะห์ story arc จาก subtitle track แล้ววาง SFX ให้ตรงจังหวะจริง ไม่ใช่ keyword matching

## หลักการ

**คิดเหมือน Video Editor** ไม่ใช่ keyword matcher:
- อ่าน subtitle ทั้งหมดตามลำดับเวลา → เข้าใจเรื่องราว
- หา "จุดเปลี่ยน" ของเรื่อง (turning points) ไม่ใช่ทุกคำสำคัญ
- วาง SFX เฉพาะจังหวะที่ impact สูงสุดจริงๆ
- ห้ามใส่ SFX ทุกประโยค หรือสุ่มตาม keyword

## Workflow

### Step 1: ดึง Subtitle

ใช้ MCP tools ดึง subtitle จาก timeline:

```
timeline(action="get_transcript")
```

ถ้าไม่มี subtitle track ให้ใช้ SRT file ที่用户提供

### Step 2: วิเคราะห์ Story Arc

อ่าน subtitle ทั้งหมดแล้วแบ่งเป็นช่วง:

| ช่วง | ถามตัวเอง |
|---|---|
| Setup | กำลังเล่าอะไร? ใครพูด? |
| Build-up | สร้างความคาดหวังยังไง? |
| Turning point | จุดเปลี่ยนคือตรงไหน? |
| Climax/Punchline | จุดพีคคือตรงไหน? |
| Resolution | จบยังไง? |

**จุดเปลี่ยน (Turning points) คือจังหวะหลักสำหรับ SFX** — ไม่ใช่ keyword สำคัญ

### Step 3: หา Emotional Beats

จาก story arc หาจังหวะที่ SFX ช่วยจริงๆ:

| อารมณ์ | SFX ที่เหมาะ | ตัวอย่าง |
|---|---|---|
| สำเร็จ | collect, ding | "ผ่านแล้ว!", "ได้แล้ว!" |
| ล้มเหลว | wrong, gong | "ไม่ผ่าน", "พัง" |
| ตกใจ | impact | "ห๊ะ?!", "อ้าว!" |
| เน้นตัวเลข | pop | "1 ล้าน!", "500 บาท" |
| เสียดาย | awkward, gong | "(ร้องไห้)", "หมดแล้ว" |
| ดีใจมาก | sparkle, collect | "เย้!", "สุดยอด!" |
| transition | whoosh | เปลี่ยนฉาก/หัวข้อ |

**กฎเหล็ก:** ถ้าบอกไม่ได้ว่า SFX ช่วยจังหวะไหน → ตัดทิ้ง

### Step 4: ตรวจ Library

เรียก `sfx` MCP tool เพื่อดูไฟล์ที่มีจริง:

```
sfx(action="scan")
```

มี 2 โฟลเดอร์:
- `Z:\SFX` — ไฟล์ต้นฉบับ (mp3/wav)
- `Z:\SFX_processed` — **ใช้เป็นหลัก** ไฟล์ wav ที่ normalize แล้ว

**ห้ามเดาชื่อไฟล์** ถ้าไม่อยู่ใน list = ห้ามใช้

### Step 5: เขียน Plan JSON

เขียน plan ด้วย format นี้:

```json
{
  "timeline_name": "ชื่อ timeline",
  "sfx": [
    {
      "sfx_file": "ชื่อไฟล์.wav",
      "timestamp_seconds": วินาที,
      "duration": ความยาว(วินาที),
      "reason": "เหตุผลสั้นๆ ว่าทำไมตรงนี้ต้องมี SFX"
    }
  ]
}
```

**ทุกตัวต้องมี `reason`** — ถ้าเขียน reason ไม่ได้ = ไม่ต้องใส่

### Step 6: Dry-run แล้ว Place

```bash
# Dry-run ก่อนเสมอ
python scripts/sfx_place.py --plan plan.json --dry-run

# วางจริง
python scripts/sfx_place.py --plan plan.json --verify
```

### Step 7: Hindsight Pass

หลังวางเสร็จ ถามตัวเอง:
1. มี SFX ตัวไหนที่ไม่จำเป็นไหม?
2. มีจังหวะที่พลาดไปไหม?
3. ระดับเสียง/ตำแหน่งดีไหม?

## Density Guide

| รูปแบบ | SFX/นาที | หมายเหตุ |
|---|---|---|
| Talking-head | 3-5 | เน้นคำ, มุก, เปลี่ยนหัวข้อ |
| Podcast | 1-2 | น้อยมาก, ห้ามทับบทสนทนา |
| Game | 5-8 | kill/death/UI/power-up |
| Meme | สูง | เสียงคือมุก |
| Livestream | ต่อ event | alert-driven |

**ถ้า user บอก "น้อย" หรือ "มาก" → ปรับตามนั้น ไม่ต้องตามตาราง**

## Common Mistakes

| ผิดพลาด | วิธีแก้ |
|---|---|
| ใส่ SFX ทุกประโยค | เฉพาะ turning points เท่านั้น |
| ใช้ keyword matching | อ่าน story arc ไม่ใช่ search words |
| ใช้ไฟล์ที่ไม่มีจริง | scan library ก่อนเสมอ |
| ไม่ dry-run | dry-run เสมอก่อนวางจริง |
| ไม่มี reason ใน plan | ทุกตัวต้องมีเหตุผล |
