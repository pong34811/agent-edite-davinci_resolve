# Skills สำหรับ Agent ตัดต่อ DaVinci Resolve

รวบรวม skills จากงานเดิมมาไว้ในโปรเจกต์นี้ โดยไม่ย้ายหรือลบต้นฉบับ ไม่แก้คลิป ไทม์ไลน์ หรือฐานข้อมูล Resolve และไม่เปลี่ยน config ของ Hermes

## ชุดหลัก — 16 skills

อยู่ที่ `.agents/skills/` พร้อม references และคู่มือ Resolve ที่อ้างถึง

| Skill | หน้าที่ |
|---|---|
| `house-style` | กฎการตัดต่อและสไตล์ซับที่เคยกำหนด |
| `resolve-session` | ตรวจการเชื่อมต่อ เวอร์ชัน โปรเจกต์ และไทม์ไลน์ก่อนเริ่มงาน |
| `resolve-mcp` | แผนที่เครื่องมือ Resolve แบบ live และ offline |
| `resolve-media-pool` | นำเข้าและจัดระเบียบสื่อ ตรวจและวางแผน relink |
| `resolve-media-analysis` | วิเคราะห์ภาพ เสียง และเนื้อหาฟุตเทจก่อนตัด |
| `video-footage-review` | ตรวจฟุตเทจ ทำ cutlist และเลือกไฮไลต์เป็นคลิปสั้น |
| `resolve-rough-cut` | ประกอบ first pass / rough cut โดยไม่เติมสิ่งที่ไม่ได้ขอ |
| `resolve-tighten-recording` | วางแผนตัด dead air จากคลิปยาว และสร้าง variant |
| `resolve-edit` | ตัด ย้าย คัดลอกช่วง ปรับ pacing และโครงสร้างไทม์ไลน์ |
| `resolve-audio` | เสียง Fairlight การมิกซ์ การถอดเสียง และขอบเขต API |
| `thai-subtitles-resolve` | ถอดเสียงไทย จัดคำและเวลา SRT นำเข้าและตรวจ subtitle |
| `resolve-video-enrichment` | เติม SFX/BGM/GIF ซูม VTuber ด้วย Adjustment Clip และ QC |
| `resolve-fusion` | Fusion composition / Transform / title / VFX |
| `resolve-color` | ปรับสีและ matching แบบ frame-first |
| `resolve-conform` | Conform/interchange ตรวจ source range และการ relink |
| `resolve-delivery` | Render และตรวจไฟล์ส่งมอบตามสเปก |

ประวัติที่เข้าถึงได้พบการโหลด **14 จาก 16 skills หลัก** ใน sessions ที่เกี่ยวข้องกับ Resolve ส่วน `resolve-color` และ `resolve-conform` รวมไว้ให้ชุดงานครบ แต่ไม่อ้างว่าเคยโหลดจริงจากประวัติที่ตรวจครั้งนี้ การโหลด skill ไม่ได้แปลว่าใช้งานกับทุกคลิปหรือทำงานเสร็จแล้ว

## Skills เสริมที่เก็บแยก — 13 ชุด

อยู่ที่ `docs/related-skills/` เป็นเอกสารอ้างอิง ไม่เปิดเป็น skills ตัดต่ออัตโนมัติ:

- `computer-use`, `songsee`, `codex`, `systematic-debugging`
- `grounded-citations`, `blocked-page-recovery`
- Superpowers: `brainstorming`, `test-driven-development`, `dispatching-parallel-agents`, `systematic-debugging`, `executing-plans`, `verification-before-completion`, `using-superpowers`

ชุด `using-superpowers` เก็บเพื่อรักษา bootstrap/reference dependencies; ชุดอื่นมีหลักฐานการโหลดใน sessions ที่กล่าวถึง Resolve ไม่ใช่หลักฐานว่าเป็นขั้นตอนที่จำเป็นสำหรับทุกงาน

## จุดที่ตรวจและปรับให้เข้ากัน

- ใช้ house style ซับไทย **ไม่เกิน 3 คำสั้น / ประมาณ 14 ตัวอักษร / 1.5 วินาที** และไม่เว้นวรรคระหว่างคำไทย แทนค่าทั่วไป 2.2 วินาที
- เพิ่มข้อระวังการนำเข้า SRT ด้วย bare payload และ cache ของ ImportMedia
- ปรับคำแนะนำเว้นช่วง structural mutations เป็นประมาณ 1.2 วินาทีเป็นจุดเริ่มต้น พร้อม save/readback
- ไม่ให้ลบไทม์ไลน์สำรองอัตโนมัติเมื่อทำ rough cut
- แก้คำสั่ง contact sheet ให้ใช้ `python` บน Windows และคำแนะนำ inventory ให้ใช้ `search_files`
- เติม reference `whisper-transcription.md` ที่เดิมถูกอ้างถึงแต่ไม่มีไฟล์
- เก็บ historical variants ที่ต่างจริงไว้ใน `docs/skill-variants/` ไม่เอากฎเก่าทับ house style ปัจจุบัน

อ่านกฎใช้งานที่ `AGENTS.md` และรายละเอียดข้อขัดแย้ง/ข้อจำกัดที่ `docs/OPERATING-NOTES.md`

## ใช้กับ Hermes

Hermes รองรับ project-local skills ใน `.agents/skills/` แต่ต้อง trust โปรเจกต์ก่อน จากไดเรกทอรีนี้ใช้:

```bash
hermes skills trust
```

จากนั้นเริ่ม session ใหม่เพื่อให้ค้นพบชุดของโปรเจกต์ งานรวบรวมครั้งนี้ **ไม่ได้เปลี่ยน trust/config ให้เอง** หากยังไม่ trust สามารถสั่ง agent อ่านไฟล์ SKILL.md ในโปรเจกต์โดยตรงได้

คำสั่งนี้ตรวจจาก CLI ที่ติดตั้งอยู่แล้ว คู่มือทางการ: https://hermes-agent.nousresearch.com/docs/user-guide/features/skills#project-local-skills

## ตรวจความครบของชุด

```bash
python -m unittest discover -s tests -v
python scripts/verify_skill_bundle.py
```

Validator ต้องมี PyYAML; ใช้ Python environment ที่ตรวจแล้วว่ามีแพ็กเกจนี้ หากมี Hermes ใน interpreter เดียวกัน จะสแกน core skills ด้วย security scanner จริงของ Hermes ด้วย ผลตรวจชุดปัจจุบันอยู่ที่ `docs/validation-report.json`

`docs/skills-manifest.json` บันทึกแหล่งที่มา SHA-256 ของต้นฉบับ/สำเนา รายการปรับเฉพาะโปรเจกต์ และ history anchors โดยไม่คัดลอกข้อความสนทนาหรือ secrets

## ขอบเขต

นี่คือ **ชุด skills และคู่มือ ไม่ใช่ MCP server ตัวใหม่** ต้องใช้ backend `davinci-resolve-mcp` ที่มีอยู่หรือ scripting bridge ที่ตรวจการเชื่อมต่อจริงก่อนลงมือ คำสั่งเกี่ยวกับ `src/server.py` ในคู่มือต้นทางให้รันจาก installation ของ backend ไม่ใช่จากโปรเจกต์นี้

ไม่ได้รวม `release-check` ซึ่งใช้ปล่อยเวอร์ชัน server, งาน Canva thumbnail/YouTube downloader ที่เป็นคนละ workflow, source footage, ไฟล์ SRT ของคลิป, render, หรือ Project.db ไม่มีการ commit/push หรือติดตั้งแพ็กเกจเพิ่มในงานนี้
