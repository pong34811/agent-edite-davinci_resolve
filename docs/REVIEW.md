# รีวิวชุด skills สำหรับ DaVinci Resolve

## ขอบเขตและคำตอบเรื่องสถานะ

ชุด skills ถูกนำมาไว้ในโปรเจกต์และปรับหลังรีวิวแล้ว แต่ผลตรวจชุดนี้ไม่ใช่หลักฐานว่าตัดต่อคลิปใน Resolve เสร็จ ไม่ได้เชื่อมต่อ Resolve, แก้ฟุตเทจ, commit/push, ติดตั้ง dependency หรือเปลี่ยน trust/config ของ Hermes ในงานรีวิวนี้

`PLAN.md`, `WORKLOG.md`, `reference/` และ `.mcp.json` เป็นงาน/บริบทแยก ไม่ได้แก้หรือรวมใน provenance ของชุด skills

## ข้อบกพร่องที่แก้แล้ว

| ระดับ | ข้อบกพร่อง | การแก้และหลักฐานทดสอบ |
|---|---|---|
| สูง | Contact sheet เขียนทับไฟล์เดิมหรือ input frame ได้เมื่อเลือก output ผิด | ตรวจปลายทางทั้ง batch และสร้างไฟล์ด้วย exclusive mode; regression test ยืนยัน input ไม่เปลี่ยน |
| กลาง | เฟรมที่หายจาก pending vision ถูกกรองออกแล้วทำให้ index/metadata เลื่อน | หยุดด้วย FileNotFoundError ก่อนสร้าง output; ห้าม renumber เฟรมที่เหลือ |
| กลาง | Manifest ลบ record แล้ว checksum ของไฟล์นั้นถูกข้าม | ตรวจ inventory ของ `.agents/`, `docs/`, `resolve-advanced/`, `scripts/`, `tests/` และเอกสาร integration; tests ครอบคลุม record ที่หายและ inventory ว่าง |
| กลาง | Core skills ตรวจเพียงจำนวน ไม่ตรวจชื่อ/เส้นทาง | เทียบชุดเส้นทางกับไฟล์จริงและตรวจชื่อจาก frontmatter |
| กลาง | Archive paths/ชื่ออาจไม่มีจริงแต่ยังตรวจผ่าน | เทียบรายการกับ archive ที่อยู่จริงและตรวจชื่อ upstream; รองรับ namespace `superpowers-` โดยไม่เปลี่ยนต้นฉบับ |
| กลาง | Manifest มีรายการไฟล์ซ้ำหรือยอดนับไม่ตรงได้ | ปฏิเสธ duplicate paths และตรวจ counts เทียบข้อมูลจริง |
| กลาง | ค่า grid ติดลบอาจรายงานสำเร็จแต่ไม่ได้สร้าง sheet | ตรวจ tile width/columns/rows ให้เป็นบวกก่อนสร้าง output; CLI คืน usage error พร้อมข้อความชัดเจน |
| ต่ำ | Tests พังเมื่อไม่มี TMPDIR | ใช้ Hermes scratch เป็น fallback ไม่ใช้ system temp; ทดลองรันโดยลบ TMPDIR จาก environment |

Tests สร้างสำเนา/ภาพเล็กใน scratch เท่านั้น ไม่ใช้หรือแก้ source footage ของผู้ใช้ CLI ของ contact sheet ถูกทดลองสร้างไฟล์จริงและเปิดตรวจ JPEG ทุกแผ่น พร้อมเทียบว่า input ไม่เปลี่ยน

## ประเด็นค้างในงานตัดต่อแยก

**กลาง — `PLAN.md:140–162`:** งาน 2 ระบุปรับฟอนต์ครบ 16 Timeline ก่อนงาน 3 ซึ่งมี sample-approval gate อาจอ่านลำดับเป็นการแก้ทั้งชุดก่อนผู้ใช้อนุมัติตัวอย่าง ควรจำกัดงานก่อน gate ไว้ที่คู่ตัวอย่างและย้ายงานที่เหลือไปหลังอนุมัติ ประเด็นนี้ยังไม่ได้แก้ใน PLAN; บันทึกข้อห้ามข้าม gate เพิ่มใน OPERATING-NOTES แล้ว

WORKLOG ของงานแยกไม่ใช่หลักฐานว่าปรับและ QC คลิปครบแล้ว ต้องยืนยันจากหลักฐานงานนั้นและ Resolve จริงก่อนบอกว่าเสร็จ

## วิธีตรวจซ้ำและข้อจำกัด

```bash
python -m unittest discover -s tests -v
python scripts/verify_skill_bundle.py
```

ใช้ Python environment ที่มี PyYAML และ Pillow อยู่แล้ว ผลตรวจชุดล่าสุดอยู่ที่ `docs/validation-report.json` รายการต้นทาง/checksums/amendments อยู่ที่ `docs/skills-manifest.json`

- Security scanner ตรวจ core skills เมื่อ import Hermes ได้; `safe` ไม่ได้แปลว่าไม่มี informational findings หรือรับรองความปลอดภัยของ API ภายนอก
- Medium finding ใน subtitle skill เป็น regex Unicode ของสระ/วรรณยุกต์ไทย ไม่ใช่โค้ดซ่อนคำสั่ง
- ตรวจ frontmatter/ไฟล์/checksum ของ archive แต่ไม่ได้รัน archive scripts หรือรับรองลิงก์ทั้งหมดในคู่มือเก่า
- Checksum manifest ไม่ได้ลงลายเซ็น จึงตรวจ drift ได้ แต่ไม่รับรองความแท้เมื่อทั้งไฟล์และ manifest ถูกแก้พร้อมกัน
- ยังไม่รับรอง live MCP/Resolve connection, project trust, ฟุตเทจ online หรือความพร้อมเผยแพร่ของคลิป
