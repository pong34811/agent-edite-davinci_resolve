# เตรียมงานและตรวจรับด้วยเครื่องมือกลาง

ใช้จาก repo root บน Windows ด้วย `python` ไม่ต้องติดตั้ง dependencies เพิ่ม
สำหรับ intake ต้องมี FFprobe บน PATH; contact sheet ต้องมี Pillow ที่เครื่องมือเดิมใช้
คำสั่งทั้งหมดในหน้านี้ทำงาน offline ไม่เปิด Resolve ไม่ import สื่อ ไม่แก้ timeline
และไม่ render หรือตัดต่อด้วย FFmpeg

## 1. เตรียมงานหนึ่งคำสั่ง

```powershell
python scripts/prepare_edit.py 'G:/My Drive/Projects/YourChannel/Source' --out-dir 'scratch/edit-review'
```

เติม `--srt 'path/to/captions.srt'` เพื่อเรียก `caption_lint` เดิม
และ `--frames-dir 'path/to/clip-analysis'` เพื่อทำ contact sheet จากเฟรมที่มีอยู่
ผ่าน `contact_sheet` เดิม ไม่ดึงภาพหรือถอดเสียงใหม่

ผลลัพธ์:

| ไฟล์ | หน้าที่ |
|---|---|
| `intake.json` | รายการสื่อ, FFprobe streams, duration, ข้อผิดพลาด, cache hits และผล lint/contact sheet ถ้าขอ |
| `edit_decisions.json` | แบบร่าง source IDs/path/FPS/frame count; timeline เป็น null และ edits ว่างจนกว่าจะเลือกจริง |
| `acceptance_checks.json` | รายการตรวจรับที่เริ่มด้วย unverified ทุกข้อ |
| `sheets-*/` | contact sheets ของ sampled frames พร้อม receipt/hash เมื่อส่ง frames-dir |

`prepared` หมายถึงเตรียมข้อมูลสำเร็จ ไม่ได้หมายถึงเสียงดี เรื่องเข้าใจได้ หรือตัดต่อเสร็จ
ไฟล์ probe เสียหรือไม่มีสื่อทำให้สถานะเป็น `incomplete` และ exit 1
ข้อผิดพลาดในการเรียกคำสั่งเป็น exit 2

ใช้ output ใหม่ที่แยกจาก source root หรือใช้ output ที่คำสั่งนี้เป็นเจ้าของอยู่แล้ว
คำสั่งจะข้ามโฟลเดอร์ output ระหว่างสแกน ปฏิเสธโฟลเดอร์ที่มีไฟล์อื่นอยู่ก่อน
และไม่เขียนทับแบบร่างแผน/ผลตรวจที่คนแก้แล้ว

รันซ้ำด้วยคำสั่งเดิมเพื่อใช้ cache ของไฟล์ที่ path, size, mtime_ns และรุ่น probe/tool ตรงกัน
probe ที่ล้มเหลวจะลองใหม่ ไฟล์ที่ถูกลบจะหายจาก intake รอบใหม่
ถ้าแทนเนื้อหาไฟล์โดยเก็บ size/mtime เดิม ให้ใช้ `--refresh` เพื่อ probe ใหม่
cache ไม่ใช่ content hash ของฟุตเทจ จึงไม่ต้องอ่านไฟล์วิดีโอทั้งไฟล์ซ้ำ
contact sheet ตรวจ hash ของผลที่ cache ไว้ก่อนใช้ซ้ำ

เมื่อ source เปลี่ยน ให้ reconcile `edit_decisions.json` กับ intake ใหม่เอง
แบบร่างไม่ถูกสร้างทับอัตโนมัติ เพื่อรักษางาน editorial ที่ทำไปแล้ว

## 2. แผนตัดต่อรูปแบบเดียวกัน

ข้อกำหนดอยู่ใน [edit-decisions.schema.json](contracts/edit-decisions.schema.json)
ตัวอย่างที่กรอกครบอยู่ใน [edit-decisions.example.json](contracts/edit-decisions.example.json)
ตัวอย่างเป็นข้อมูลสมมติ ไม่ใช่ค่า default หรือคำสั่งให้เปลี่ยนสัดส่วนโปรเจกต์

```powershell
python scripts/edit_workflow.py validate 'scratch/edit-review/edit_decisions.json'
```

- กรอก timeline จากสัดส่วน/ความละเอียด/FPS ที่อนุมัติจริง ไม่มีค่า 9:16 หรือ 24 fps อัตโนมัติ
- `fps` เป็น string จำนวนเต็มหรือเศษส่วน เช่น `60`, `30000/1001` ห้ามปัดเป็น `30`
- `in_frame`/`out_frame` เป็นเฟรมสัมพันธ์กับ source แบบ `[IN, OUT)` โดย OUT ไม่รวมเฟรมนั้น
- `record_frame` เป็น absolute frame บน timeline เริ่มที่หรือหลัง `start_frame`
- `frame_count` ต้องยืนยันจริง ห้ามคำนวณเดาจาก duration × FPS; intake คง null เมื่อ FFprobe ไม่รายงาน
- source ที่ avg/r frame rates ไม่ตรงกันจะคง FPS เป็น null ต้องตรวจ VFR/conform ก่อน
- audio-only source ไม่มี FPS ที่เชื่อถือได้จาก FFprobe ให้ยืนยัน media frame basis ใน Resolve
- source ID ในแผนเป็น ID ภายใน manifest ไม่ใช่ Media Pool ID; ก่อน apply ต้องจับคู่ File Path และอ่าน Media Pool ID จริง
- ทุก edit ต้องมี story beat, เหตุผล, หลักฐานอ้างอิง และ confidence
- ใช้แยก video/audio edits ตามจริง ไม่สร้างซับแทนด้วย video track

รุ่นแรกตรวจ normal speed/hard cuts เท่านั้น ปฏิเสธ field ที่ไม่รองรับ เช่น speed
และช่วงซ้อนบนแทร็กเดียวกัน โดยไม่เดาพฤติกรรม retime/transition
ตัว validator ใช้เฉพาะ JSON Schema keywords ใน schema ที่ส่งมาพร้อม repo ไม่ใช่ validator ของ schema ใด ๆ จากภายนอก
จะตรวจ duplicate ID/path, source bounds, timeline start, FPS และ overlap
การปัดความยาว record ใช้ rational arithmetic แล้ว round half up หนึ่งครั้ง
อย่าส่ง OUT จากแผนเข้า API ที่ใช้ endFrame แบบ inclusive โดยตรง: ต้องแปลง convention
และอ่านกลับบน build ปัจจุบัน รวมถึงตรวจ audio sync ก่อน apply เป็นชุด

ผล `passed` ยืนยันความถูกต้องของแผนเท่านั้น ไม่ตรวจว่า evidence ในแผนมีจริง
หรือภาพ/เสียงมีความหมายตามเหตุผลที่เขียน และไม่ยืนยัน live timeline

## 3. เกณฑ์ตรวจรับและหลักฐาน

เกณฑ์กลางอยู่ใน [acceptance-gate.json](contracts/acceptance-gate.json)
แบ่งด้าน direction, craft, visual, audio และ handoff โดยทุกข้อจำเป็นต้องมีผล
ถ้าซับหรือ render อยู่นอกขอบเขต ให้ผู้ตรวจบันทึกเหตุผลและหลักฐาน scope แทนการปล่อยข้ามเงียบ ๆ

กรอก `target` ให้ระบุ project/timeline ID และ revision หรือ render ที่กำลังตรวจ
แต่ละ check มี status `passed`, `failed` หรือ `unverified`
check ที่ passed ต้องมี `reviewer`, `note` และ `evidence` ซึ่งเป็นรายการ path/hash:

```json
{
  "id": "story",
  "status": "passed",
  "reviewer": "editor-name",
  "note": "Reviewed the setup and payoff against picture and sound for the named target",
  "evidence": [{"path": "story-review.json", "sha256": "REPLACE_WITH_ACTUAL_HASH"}]
}
```

```powershell
python scripts/edit_workflow.py hash 'scratch/edit-review/story-review.json'
python scripts/edit_workflow.py accept 'scratch/edit-review/acceptance_checks.json' --out 'scratch/edit-review/acceptance-report-v1.json'
```

evidence paths สัมพันธ์กับโฟลเดอร์ของ acceptance_checks.json หรือเป็น absolute path
ตัวตรวจปฏิเสธ evidence ว่าง/หาย/hash เปลี่ยน, ID ซ้ำ/ไม่รู้จัก และ claim ที่ข้อมูลไม่ครบ
check ที่ไม่ส่งมาคง unverified; failed มีลำดับเหนือ unverified; exit 0 เฉพาะผ่านทุกข้อ
ไฟล์ report จาก `--out` ต้องเป็นไฟล์ใหม่ ป้องกันการเขียนทับหลักฐานเดิม

ตัวตรวจนี้ reconcile คำยืนยันของผู้ตรวจและ hash เท่านั้น ไม่ตัดสินเนื้อหาของหลักฐาน
และไม่ยืนยันว่าหลักฐานยังตรงกับ Resolve ปัจจุบัน หากแก้ timeline ต้องตรวจใหม่
ใช้ `verify_review_resume.py`/MCP readback ตามขอบเขตจริงเพื่อยืนยัน freshness
ห้ามคัด status ผ่านจาก report เก่าเพียงเพราะไฟล์ยังอยู่

ซับที่ขอสร้างใช้ native Subtitle track เท่านั้น: ประมาณ 14 ตัวอักษรไทย,
ไม่เกิน 3 คำสั้น/1.5 วินาที และไม่เว้นวรรคระหว่างคำไทย
lint เดิมตรวจจำนวนตัวอักษร/เวลา/ช่องว่าง แต่ไม่ตัดคำไทยหรือพิสูจน์การฟัง
ต้องตรวจคำ เสียงจริง native cue frames และภาพ burn-in ที่ Resolve render
ฟอนต์ใช้ชื่อ saved preset ที่อนุมัติตรงตัว; ไม่บังคับ Netflix-style/ASS/Text+

ค่า loudness และ safe area ใช้ spec ที่ผู้ใช้อนุมัติ ไม่สร้างค่าเป้าหมายใหม่จากแพลตฟอร์มโดยอัตโนมัติ
การตรวจภาพ still ไม่พิสูจน์ motion ทุกเฟรม และ LUFS ไม่พิสูจน์ความชัดของคำพูด

## ที่มาและขอบเขตการปรับใช้

นำแนวคิด edit rationale, acceptance checklist และ intake brief จาก
[ChaiWithJai/davinci-resolve-claude-skills](https://github.com/ChaiWithJai/davinci-resolve-claude-skills/tree/cf7e4275f10d6d7b709a5c50155769715c8d14f0)
มาสร้าง implementation ของ repo นี้เอง ไม่ได้นำ toolkit หรือโค้ด GUI มาเปิดใช้งาน
คงการวิเคราะห์/จัดแผนแยกจากการ apply ผ่าน MCP/Resolve Python ที่ต้องมี preflight,
backup, variant, save และ readback ตาม AGENTS.md
