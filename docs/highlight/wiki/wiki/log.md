# บันทึกการทำงาน

เพิ่มรายการใหม่ที่ท้ายไฟล์ ใช้วันที่ ISO ตามเวลา Asia/Bangkok ไม่แก้ประวัติย้อนหลัง

## [2026-10-04] setup | สร้าง LLM Wiki เริ่มต้น

- บริบท: ผู้ใช้ส่งแนวคิด LLM Wiki และอนุมัติโครงสร้างเริ่มต้นในแชท
- สร้าง: กฎเอเจนต์ คู่มือ แม่แบบ โฟลเดอร์ต้นฉบับ และโฟลเดอร์หน้าความรู้
- หน้า: [สารบัญ](index.md), [ภาพรวม](overview.md), [คู่มือ](../README.md)
- ขอบเขต: ใช้งานทั่วไปจนกว่าผู้ใช้จะระบุหัวข้อเฉพาะ
- สถานะ: ยังไม่มีการนำเข้าแหล่งข้อมูล แนวคิดในแชทใช้กำหนดโครงสร้าง ไม่ได้บันทึกเป็นต้นฉบับหรือแหล่งอ้างอิงเชิงเนื้อหา

## [2026-10-04] lint | ตรวจโครงสร้างเริ่มต้น

- ขอบเขต: Markdown ทั้ง 9 ไฟล์ใน vault และโฟลเดอร์ที่จำเป็น
- ตรวจผ่าน: ตำแหน่งที่ต้องมี 14 รายการ ลิงก์ภายใน 25 จุด frontmatter ของหน้าความรู้ และการลงหน้าความรู้ในสารบัญ
- ผล: ไม่พบลิงก์เสียหรือหน้าความรู้ตกสารบัญ ไม่มีต้นฉบับที่ถูกเพิ่มหรือแก้ไข และไม่ได้แก้การตั้งค่า Obsidian
- ข้อจำกัด: ตรวจเชิงโครงสร้างเท่านั้น ยังไม่มีแหล่งข้อมูลให้ตรวจข้อเท็จจริง ความขัดแย้ง หรือความล้าสมัย
- ขั้นต่อไป: ผู้ใช้เลือกหัวข้อหรือเพิ่มต้นฉบับแรกแล้วสั่งนำเข้า

## [2026-10-04] ingest | เป้าหมายโปรเจกต์ Vtuber ไทย

- Source: [ข้อความผู้ใช้](../raw/2026-10-04-user-project-brief.md), บันทึกตามต้นฉบับจากแชท
- Pages: [สรุป brief](sources/user-project-brief.md), [ภาพรวม](overview.md)
- Outcome: completed; ผู้ใช้กำหนดขอบเขต Vtuber ไทย ไลฟ์ gameplay funny และ meme สำหรับคลิป YouTube แทนค่าเริ่มต้นใช้งานทั่วไป ยังไม่ยืนยันนิยามไวรัลหรือ Shorts โดยเฉพาะ

## [2026-10-04] ingest | Prompt โปรเจกต์ปัจจุบัน

- Source: [สำเนา prompt](../raw/2026-10-04-project-prompt.md), คัดลอกตรงต้นฉบับและตรวจ hash ตรงกัน
- Pages: [สรุป prompt](sources/project-prompt.md), [การคัดคลิป](concepts/clip-selection.md), [การเชื่อม skill](analyses/skill-integration.md)
- Outcome: completed; อ่าน prompt ครบ ไม่ได้อ่านแผนที่ prompt อ้างถึง พบข้อความ auto/ask ต่างกันภายในสำเนา ต้องตรวจ live prompt ของงานจริง

## [2026-10-04] ingest | House style ของโปรเจกต์

- Source: [สำเนา house-style](../raw/2026-10-04-house-style.md), คัดลอกตรงต้นฉบับและตรวจ hash ตรงกัน
- Pages: [สรุป skill](sources/house-style.md), [รสนิยม](concepts/editorial-preferences.md), [วงจร feedback](analyses/feedback-loop.md)
- Outcome: completed; กฎ rough-cut และซับมีขอบเขตต่างกัน ยังไม่มี preference เรื่อง hook/shot/cut ที่ยืนยัน ไม่ได้แก้ actual skill

## [2026-10-04] query | วิกิช่วย skill คัดคลิปได้อย่างไร

- Pages: [การเชื่อม skill](analyses/skill-integration.md), [เกณฑ์ทดลอง](concepts/clip-selection.md), [feedback](analyses/feedback-loop.md)
- Outcome: บันทึกคำตอบที่ใช้ซ้ำได้ เพิ่ม entry point ใน AGENTS.md ของโปรเจกต์ และแม่แบบ clip review คะแนนเป็นข้อเสนอทดลอง ไม่ใช่ผลทำนาย ยังไม่ได้รันฟุตเทจ Resolve หรืออัปโหลด

## [2026-10-04] lint | ตรวจวิกิสำหรับโปรเจกต์คัดคลิป

- ขอบเขต: Markdown ที่สร้าง/ดูแลและคู่มือ 17 ไฟล์ ตรวจลิงก์ภายใน 122 จุด หน้าความรู้ 8 หน้าลงสารบัญครบและ sources ชี้ไฟล์จริง
- ผล: ไม่พบลิงก์เสีย ตรวจ hash สำเนา prompt และ house-style ตรงกับต้นฉบับทั้งสองไฟล์ log ก่อนเพิ่มรายการนี้มี 6 รายการในรูปแบบที่กำหนด
- ปรับแก้: overview/schema/คู่มือเปลี่ยนจากขอบเขตทั่วไปเป็นขอบเขตผู้ใช้ระบุ ประวัติเก่าคงอยู่
- ประเด็นเปิด: ความต่าง auto/ask ใน prompt, นิยามไวรัล/Shorts, feedback คลิปที่ชอบ/ไม่ชอบ และ analytics จริง ยังไม่ครบ จึงไม่ยืนยันผลของเกณฑ์ทดลอง
- ข้อจำกัด: ตรวจเอกสารและ provenance ไม่ได้ตรวจความพร้อมของ runtime หรือสื่อ ไม่ได้เปลี่ยน skill เดิมหรือดำเนินงานวิดีโอ

## [2026-10-04] ingest | คำตอบและการอนุมัติ 31 คลิป (Hoshi 2026-10-03)

- Source: [ข้อความผู้ใช้](../raw/2026-10-04-user-approval-31-clips.md), บันทึกตามต้นฉบับจากแชท
- Pages: [สรุปคำตอบ](sources/user-approval-31-clips.md), [บันทึกรอบงาน](analyses/hoshi-2026-10-03-run.md), [วงจร feedback](analyses/feedback-loop.md), [การคัดคลิป](concepts/clip-selection.md), [การเชื่อม skill](analyses/skill-integration.md), [ภาพรวม](overview.md)
- Outcome: completed; บันทึกค่าที่ผู้ใช้เลือก (16:9, 4-8 คลิปต่อ VOD, ไม่หยุดอนุมัติ) และการอนุมัติ 31 คลิปโดยไม่ระบุเหตุผลรายคลิป ไม่เพิ่มกฎ house-style เพราะไม่มี preference ที่ใช้ซ้ำได้ ตัวเลขของงานเป็นข้อสังเกตเอเจนต์ ข้อความ ASR ยังไม่ยืนยัน และยังไม่มี analytics

## [2026-10-04] maintenance | ซิงก์วิกิ skill และ AGENTS.md หลังรัน pipeline จริง

- Pages: [การเชื่อม skill](analyses/skill-integration.md), [AGENTS.md ของโปรเจกต์](../../AGENTS.md)
- Outcome: completed; เพิ่มหมายเหตุสถานะว่า pipeline ถูกรันจริงและมี skill คัดคลิปใน skill ของ Hermes (นอก repo) เพิ่ม entry point โค้ด pipeline ใน AGENTS.md ไม่ได้คัดลอก skill เข้า repo
- ข้อสังเกต: สำเนา prompt ใน raw เป็น snapshot ก่อน prompt.md ถูกปรับให้ใช้ซ้ำได้และตั้ง APPROVAL=auto ต้องอ่าน prompt.md ปัจจุบันทุกงาน ไม่ได้นำเข้าเวอร์ชันใหม่เป็นแหล่งใหม่เพราะผู้ใช้ไม่ได้สั่ง

## [2026-10-04] lint | ตรวจหลังซิงก์งาน Hoshi 2026-10-03

- ขอบเขต: หน้าความรู้ 10 หน้า (รวมภาพรวม) และลิงก์ Markdown ทั้ง vault
- ตรวจผ่าน: frontmatter ครบ, sources ชี้ไฟล์จริง, ทุกหน้าอยู่ในสารบัญ, ไม่มีลิงก์ .md เสีย
- ประเด็นเปิด: ไม่มีเหตุผลรายคลิปจากผู้ใช้, ยังไม่มี analytics, ASR ยังไม่ยืนยัน, ไม่ได้ตรวจความถูกต้องของข้อเท็จจริงเนื้อหาคลิป
- ข้อจำกัด: การตรวจลิงก์ไม่พิสูจน์ความถูกต้องของข้อเท็จจริง ไม่ได้ commit การเปลี่ยนแปลง

## [2026-10-04] lint | ตรวจตามสกิล llm-wiki (orphan, ขนาดหน้า, tag, drift)

- ขอบเขต: หน้าความรู้ 10 หน้า และ raw 4 ไฟล์ ตามกฎ AGENTS.md ของ vault นี้ (ลิงก์ Markdown ไม่ใช่ wikilink; ไม่มี SCHEMA.md)
- ตรวจผ่าน: ไม่มี orphan (ทุกหน้ามีลิงก์เข้าจากหน้าอื่นอย่างน้อย 2 หน้า), ไม่มีหน้าเกิน 200 บรรทัด (ยาวสุด 65), ลิงก์ไม่เสีย
- ประเด็นเปิด: vault ไม่มีรายการ tag taxonomy กลาง tag ใหม่ hoshi, approval, pipeline-run ยังเป็น tag อิสระ; raw ไม่มี sha256 frontmatter จึงเช็ก drift ด้วย hash เทียบต้นฉบับแทน; prompt.md ปัจจุบันต่างจากสำเนาใน raw โดยตั้งใจ (แก้ให้ใช้ซ้ำได้) ไม่ใช่ความผิดพลาด
- ข้อจำกัด: ไม่ได้แก้ raw ตามกฎ immutability

## [2026-10-04] maintenance | แก้ข้อความผิดใน log ก่อนหน้า (prompt drift)

- ตรวจ sha256 วันนี้: สำเนา [prompt ใน raw](../raw/2026-10-04-project-prompt.md) ตรงกับ prompt.md ปัจจุบัน และสำเนา house-style ตรงกับ `.agents/skills/house-style/SKILL.md`
- แก้: รายการ maintenance และ lint ก่อนหน้านี้ที่ว่า prompt.md ปัจจุบันต่างจากสำเนาใน raw เป็นข้อมูลผิด ไม่มี drift ณ เวลาตรวจ (ความต่าง auto/ask ยังอยู่ภายในตัวเอกสารเดียวกัน ดู [สรุป prompt](sources/project-prompt.md))
- ข้อจำกัด: ไม่แก้รายการเก่าตามกฎ append-only

## [2026-11-02] maintenance | ย้าย vault เข้า repo agent-edite-davinci_resolve

- คัดลอก vault ทั้งหมดจาก `agent-seacrh-virus-cut/llm_wiki/` มาไว้ที่ `docs/highlight/wiki/` ตามคำสั่งผู้ใช้ให้รวมเครื่องมือและสกิลไว้ใน repo เดียว; repo เดิมไม่ถูกแก้
- path ใหม่: โค้ด pipeline `scripts/highlight/`, ข้อมูลงาน `work/highlight/<channel>/<job>/`, prompt `docs/highlight/prompt-template.md`, skill highlight อยู่ใน `.agents/skills/` ของ repo นี้
- ไม่แก้ `raw/` และรายการ log เก่า ข้อความเก่าที่อ้าง `llm_wiki/`, `work/` หรือ Hermes skills นอก repo ให้อ่านตาม path ใหม่ข้างบน
- ลิงก์ `../../AGENTS.md` ในรายการ log เก่าชี้ AGENTS.md ของ repo เดิม และเสียหลังย้าย; ไม่แก้ตามกฎ append-only (AGENTS.md ของ repo นี้อยู่ที่ `../../../../AGENTS.md`)
