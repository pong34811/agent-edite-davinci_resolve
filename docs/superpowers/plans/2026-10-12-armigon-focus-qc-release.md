# แผนบันทึก QC Zoom Focus Armigon และปล่อย skill bundle v0.9.0

## เป้าหมาย

เก็บแนวทาง QC ที่ใช้กับ Armigon ให้เป็นกฎถาวรใน skill และ house style พร้อมรายงานหลักฐานและข้อจำกัดที่ตรวจสอบได้ จากนั้นตรวจไฟล์ manifest และปล่อย GitHub Release `v0.9.0` ซึ่งยังไม่มี tag หรือ release บน GitHub

## ขอบเขตและข้อกำหนดร่วม

- เขียนเนื้อหาใหม่และรายละเอียด release เป็นภาษาไทย โดยคงชื่อ API, tool, path และศัพท์ Resolve ที่จำเป็นตามต้นฉบับ
- งาน release นี้แก้เฉพาะเอกสาร skill bundle และสคริปต์ในรีโป ไม่เชื่อมต่อหรือแก้โปรเจกต์ Resolve เพิ่ม
- คงข้อกำหนดแก้เฉพาะ Adjustment Clip; ห้ามแก้ footage, audio, subtitles หรือ overlay ที่ไม่เกี่ยวข้อง
- ระบุว่า QC ใช้การอ่านค่าและภาพ still/A-B ไม่ใช่การดูวิดีโอ render เต็มเรื่อง
- รายงานแยกความผิดปกติที่อยู่ใน source ตั้งแต่เดิมออกจากสิ่งที่ Adjustment Clip ทำให้เกิด
- เก็บไฟล์ `.drp` และ patch ที่ยัง untracked ไว้ในเครื่อง ห้ามใส่ใน commit หรือ manifest
- ใช้ branch `main` ตามคำขอของผู้ใช้ที่อนุมัติให้ `git push` และ release; รวมการเปลี่ยนแปลง local ที่เกี่ยวกับงานนี้โดยตรวจ diff ก่อน stage
- เป้าหมายเวอร์ชันคือ `0.9.0`: `VERSION`, `CHANGELOG.md` และ manifest ระบุเลขนี้อยู่แล้ว; tag/release ล่าสุดบน GitHub คือ `v0.8.0`

## งาน

### Task 1 — ทำ QC ให้เป็นแนวทางใช้ซ้ำและบันทึกผล Armigon

- ปรับ `.agents/skills/resolve-video-enrichment/references/adjustment-focus.md` ให้กำหนดการตรวจ subject identity, full-frame/no black edges, no added blur, transform keyframe/shake, และการเทียบภาพเวลาเดียวกันตอนเปิด/ปิด Adjustment Clip เพื่อแยก source crop/overlay ออกจาก crop ที่เกิดจาก zoom
- ปรับ `.agents/skills/house-style/SKILL.md` ให้เก็บข้อกำหนดของผู้ใช้: โฟกัส Armigon, ภาพเต็มจอ, ไม่เพิ่ม blur/ขอบดำ/อาการสั่น, จัดหัวถึงอก/มือพร้อม headroom และห้ามตัดส่วนสำคัญ
- เพิ่มกติกาเข้า `.agents/skills/resolve-video-enrichment/SKILL.md` ให้ค้น chapter QC นี้เมื่อทำ zoom focus
- ปรับ `AGENTS.md` และ `docs/OPERATING-NOTES.md` ให้ใช้ QC gate เดียวกันกับกฎของโปรเจกต์และขั้นตอนปฏิบัติ
- เพิ่มรายงานภาษาไทย `docs/superpowers/reports/2026-10-12-armigon-focus-qc-th.md` ระบุหลักฐาน 48 Adjustment Clips, ค่าที่อ่านกลับ, T74–T77, A/B ของ T1/T70, สิ่งที่ยังแก้ไม่ได้ใน source, และขอบเขตการตรวจ
- รวมการเปลี่ยนแปลงที่มีอยู่ใน `scripts/armigon_focus_pilot.py` เฉพาะเมื่อ review แล้วเห็นว่าเป็นการปรับ diagnostic/การรอของ pilot ที่เกี่ยวข้อง; ห้ามแตะไฟล์สำรองหรือ patch

### Task 2 — ทำเอกสาร release ให้ตรงกับ skill bundle

- ปรับ `docs/process/release-process.md` ให้กล่าวถึง release ของ skill bundle นี้ โดยใช้ `VERSION`, `CHANGELOG.md`, `docs/skills-manifest.json`, การตรวจ bundle, git tag และ GitHub Release; ตัดคำสั่ง npm/MCP ที่ไม่เกี่ยวข้องออก
- ปรับเลข bundle ใน `README.md` ให้ตรงกับ `VERSION` และหัว changelog
- ตรวจความเปลี่ยนแปลงทั้งหมดตั้งแต่ tag `v0.8.0` แล้วบันทึกความสามารถที่ส่งมอบในหัวข้อ `v0.9.0` ของ `CHANGELOG.md` เป็นภาษาไทย รวม pipeline 9:16/P2, subtitle/QC, focus, การจัด GIF, การ trim และการ export; เพิ่มผล QC Armigon พร้อมข้อจำกัดที่ตรวจยืนยันได้
- ทำให้ `scripts/refresh_skill_manifest.py` อ่านเวอร์ชันจาก `VERSION`, deduplicate ประวัติ edits ที่ซ้ำ และรับรายการไฟล์/เหตุผลของ release เพื่อบันทึก metadata
- สร้าง manifest checksum และ validation report ใหม่ แล้วตรวจว่า bundle validator ผ่าน

### Task 3 — ทบทวนและปล่อย

- ตรวจ diff ทั้งหมด, ตรวจไม่ให้ `.drp`, media, screenshot ชั่วคราว, หรือ `patches/` เข้า commit
- ตรวจ `git diff --check`, bundle validator, version consistency และสถานะ working tree
- รวม local `main` กับ `origin/main` แบบไม่ทิ้ง commits ที่ยังไม่ push แล้ว commit ไฟล์ที่เกี่ยวข้อง
- push `main`, สร้างและ push annotated tag `v0.9.0`, สร้าง GitHub Release ด้วย release notes ภาษาไทย และอ่านกลับเพื่อตรวจว่ามีอยู่จริงและเป็น latest

## เงื่อนไขสำเร็จ

- สกิลบอกขั้นตอน QC ที่ทำซ้ำได้และไม่อ้างเกินหลักฐาน
- รายงานแยกสิ่งที่เกิดจาก source กับ Adjustment Clip และบอกข้อจำกัดภาพ still ชัดเจน
- manifest/checksum/version ผ่านการอ่านกลับและ validator
- `main` และ tag `v0.9.0` อยู่บน origin และ GitHub Release `v0.9.0` ถูกสร้าง/อ่านกลับสำเร็จ
