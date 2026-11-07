---
name: sfx-library-manager
description: "จัดการ SFX library — ค้นหา, จัดหมวดหมู่, เปรียบเทียบ, เลือกเสียงที่เหมาะ ใช้เมื่อต้องการหา SFX ที่เข้ากับจังหวะ, ต้องการ知道 library มีไฟล์อะไรบ้าง, ต้องการ compare เสียง 2 ตัว, หรือต้องการแนะนำเสียงสำหรับ context ที่กำหนด"
---

# SFX Library Manager

ค้นหาและจัดการ SFX library — หาเสียงที่ใช่สำหรับจังหวะที่ต้องการ

## หลักการ

**เลือกจาก context ไม่ใช่ชื่อ:** เสียงที่ดีที่สุดคือเสียงที่เข้ากับจังหวะจริง ไม่ใช่เสียงที่ชื่อเพราะ

**รู้จัก library:** scan ก่อนเสมอ อย่า guess ชื่อไฟล์

**เปรียบเทียบก่อนเลือก:** บางครั้งเสียง 2 ตัวคล้ายกัน — ต้องรู้ว่าต่างกันยังไง

## Library Structure

```
Z:\SFX\              — ไฟล์ต้นฉบับ (mp3/wav, 71 ไฟล์)
Z:\SFX_processed\    — ไฟล์ wav ที่ normalize แล้ว (34 ไฟล์)
                      — ชื่อไฟล์: <shortname>-<dB>.wav
                      — เช่น pop-14.wav = Pop ที่ −14 dB
```

## Workflow

### Step 1: Scan Library

```python
sfx(action="scan")
```

ดู:
- `total_files` — ไฟล์ทั้งหมด
- `families` — ตระกูลเสียงที่มี
- `processed_count` / `raw_count` — แยกจำนวน

### Step 2: Search by Category

```python
sfx(action="search", params={"category": "success"})
```

Categories ที่มี:
- `success` — สำเร็จ, ได้, ผ่าน
- `fail` — ล้มเหลว, ผิด, พัง
- `impact` — ตกใจ, ชน, กระแทก
- `transition` — เปลี่ยนฉาก, ย้าย
- `emphasis` — เน้นตัวเลข, คำสำคัญ
- `emotion` — ดีใจ, เสียใจ, ตลก

### Step 3: Compare Sounds

เมื่อเจอเสียงที่เข้ากับ context ได้ 2-3 ตัว:

1. **ฟังทั้งหมด** — ใช้ ffprobe ดูความยาว
2. **เปรียบเทียบ:**
   - ความยาว (สั้น vs ยาว)
   - น้ำหนัก (เบา vs หนัก)
   - อารมณ์ (ตลก vs จริงจัง)
3. **เลือกตัวที่เหมาะที่สุด** — ไม่ใช่ตัวที่เพราะที่สุด

### Step 4: Match to Context

จาก context ที่กำหนด จับคู่กับ family:

| Context | Family ที่เหมาะ | ตัวอย่าง |
|---|---|---|
| สำเร็จ | collect, ding, sparkle | "ผ่านแล้ว!", "ได้แล้ว!" |
| ล้มเหลว | wrong, gong | "ไม่ผ่าน", "พัง" |
| ตกใจ | impact | "ห๊ะ?!", "อ้าว!" |
| เน้นตัวเลข | pop | "1 ล้าน!", "500 บาท" |
| เสียดาย | awkward, gong | "(ร้องไห้)", "หมดแล้ว" |
| ดีใจมาก | sparkle, collect | "เย้!", "สุดยอด!" |
| transition | whoosh | เปลี่ยนฉาก/หัวข้อ |

### Step 5: Verify Availability

ก่อนเขียน plan ต้องแน่ใจว่าไฟล์มีจริง:

```python
sfx(action="search", params={"query": "impact"})
```

ถ้าไม่มีใน list = ห้ามใช้

## Taxonomy

| Family | ชื่อไฟล์ (processed) | ความยาว | อารมณ์ |
|---|---|---|---|
| pop | pop-14.wav | ~0.45s | สั้น, crisp, เน้น |
| collect | collect-10.wav | ~0.87s | สำเร็จ, ได้รางวัล |
| ding | ding-12.wav | ~0.5s | ดัง, clear, สำเร็จ |
| impact | impact-10.wav | ~0.67s | หนัก, ตกใจ |
| wrong | wrong-10.wav | ~1.15s | ผิด, ล้มเหลว |
| gong | gong-10.wav | ~2.31s | หนักมาก, ดราม่า |
| awkward | awkward-16.wav | ~1.5s | เขิน, เสียดาย |
| sparkle | sparkle-10.wav | ~0.8s | วิบวับ, ดีใจ |
| whoosh | whoosh-10.wav | ~0.7s | เร็ว, transition |
| bleep | bleep-10.wav | ~0.5s | censor, ตลก |

## Tips

1. **ใช้ processed เป็นหลัก** — normalize แล้ว, ไม่ต้องปรับ level
2. **สั้นดีกว่ายาว** — sting สั้นๆ ใช้ได้บ่อยกว่า
3. **อย่าใช้ซ้ำบ่อย** — สลับ families
4. **check duration** — บางไฟล์ยาวเกินไป ต้อง trim
5. **level สำคัญ** — SFX ต้องเบากว่า speech/music bed

## Common Mistakes

| ผิดพลาด | วิธีแก้ |
|---|---|
| ใช้ไฟล์ที่ไม่มีจริง | scan + search ก่อนเสมอ |
| ใช้ processed ทั้งๆ ที่ต้องการ raw | รู้ความต่าง: processed = สั้น, raw = เต็ม |
| ใช้ pop 3 ครั้งติด | สลับ families |
| ไม่ check duration | ffprobe ก่อน |
| วางเสียงดังเกินไป | ใช้ processed (normalize แล้ว) |
