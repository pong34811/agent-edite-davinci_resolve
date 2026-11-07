---
name: subtitle-analyzer
description: "วิเคราะห์ subtitle/transcript สำหรับ editing decisions — หาจังหวะ, แบ่งช่วง, จับอารมณ์, แนะนำจุดตัด/insert ใช้เมื่อต้องการวิเคราะห์ subtitle track, หาว่าวินาทีไหนพูดอะไร, ต้องการแบ่งช่วงเรื่อง, ต้องการหาจังหวะสำหรับ SFX/transition/cut, หรือต้องการเข้าใจเนื้อหาจาก transcript"
---

# Subtitle Analyzer

วิเคราะห์ subtitle/transcript เพื่อตัดสินใจ editing — ไม่ใช่แค่อ่าน แต่เข้าใจ context

## หลักการ

**เข้าใจ context ไม่ใช่ keyword:** อ่านทั้งเรื่องแล้วค่อยตัดสินใจ ไม่ใช่ search คำสำคัญ

**แบ่งช่วงก่อน:** ไม่ใช่ดูทีละบรรทัด — แบ่งเป็นช่วงๆ แล้วค่อยวิเคราะห์

**จับอารมณ์จากบริบท:** น้ำเสียง, คำพูดซ้ำ, emoji, pause ล้วนบอกอารมณ์

## Workflow

### Step 1: ดึง Subtitle

จาก DaVinci Resolve:
```python
timeline.get_transcript(with_timecodes=True)
```

จาก SRT file:
```
อ่าน SRT file ตรงๆ
```

### Step 2: แบ่งช่วงเรื่อง (Story Segmentation)

แบ่ง subtitle ออกเป็นช่วงตามเรื่องราว:

| ช่วง | ลักษณะ | ตัวอย่าง |
|---|---|---|
| **Setup** | แนะนำตัว, แนะนำหัวข้อ | "วันนี้เราจะมา...", "สวัสดีครับ" |
| **Build-up** | เล่าเรื่อง, สร้างความคาดหวัง | "แล้วก็...", "ปรากฎว่า..." |
| **Turning Point** | จุดเปลี่ยน | "แต่...", "ปรากฎว่า...", "แต่..." |
| **Climax** | จุดพีค | "สุดยอด!", "ไม่น่าเชื่อ!" |
| **Resolution** | จบเรื่อง | "ก็จบลง...", "ขอบคุณ..." |

### Step 3: จับ Emotion

จาก context จับอารมณ์ของแต่ละช่วง:

| สัญญาณ | อารมณ์ |
|---|---|
| ตัวเลขสูง, "สุดยอด", "เย้!" | ดีใจ, สำเร็จ |
| "แต่...", "ปรากฎว่า...", pause | ลุ้น, suspense |
| "ไม่ผ่าน", "(ร้องไห้)", "พัง" | เสียใจ, ล้มเหลว |
| "ห๊ะ?!", "อ้าว!", "啥" | ตกใจ, งง |
| "555", "ตลก", "ขำ" | ตลก |
| "ขอบคุณ", "รัก", "ซึ้ง" | ซาบซึ้ง |

### Step 4: หา Key Moments

จากช่วงและอารมณ์ หาจังหวะสำคัญ:

| จังหวะ | ลักษณะ | ใช้ทำอะไร |
|---|---|---|
| **Emphasis** | ตัวเลข, ชื่อ, คำสำคัญ | Insert SFX, zoom, highlight |
| **Turn** | "แต่...", "ปรากฎว่า..." | Transition, dramatic pause |
| **Peak** | จุดพีคของเรื่อง | Slow motion, effect, SFX |
| **End of section** | จบช่วง | Cut, transition, breathe |

### Step 5: สร้าง Editing Guide

สรุปเป็น guide สำหรับ editor:

```json
{
  "timeline_name": "ชื่อ timeline",
  "segments": [
    {
      "start": "วินาทีเริ่ม",
      "end": "วินาทีจบ",
      "type": "setup|build|turn|climax|resolution",
      "emotion": "อารมณ์หลัก",
      "key_moments": [
        {
          "timestamp": "วินาที",
          "text": "คำพูด",
          "type": "emphasis|turn|peak|end",
          "suggestion": "แนะนำ editing action"
        }
      ]
    }
  ]
}
```

## Tips

1. **อ่านทั้งเรื่องก่อน** — อย่าดูทีละบรรทัด
2. **จับ context ไม่ใช่ keyword** — "แต่" ไม่ใช่ turning point เสมอไป
3. **ดูน้ำเสียง** — pause, repetition, emoji บอกอารมณ์
4. **แบ่งช่วงชัดเจน** — แต่ละช่วงมีจุดประสงค์ต่างกัน
5. **สรุปสั้นๆ** — editor ไม่อ่านยาว

## Common Mistakes

| ผิดพลาด | วิธีแก้ |
|---|---|
| จับ keyword แทน context | อ่านทั้งเรื่องก่อน |
| แบ่งช่วงผิด | ดูจากเรื่องราว ไม่ใช่ความยาว |
| ไม่จับอารมณ์ | ดูจากบริบท + น้ำเสียง |
| สรุปยาวเกินไป | เฉพาะ key moments เท่านั้น |
