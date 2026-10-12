# ขั้นตอนออกรีลีสชุดสกิล

รีโปนี้บรรจุสกิล คู่มือ และสคริปต์ช่วยงานตัดต่อ DaVinci Resolve ไม่ใช่ซอร์สของ MCP server หรือแพ็กเกจ npm เลขรุ่นของชุดสกิลใน `VERSION` แยกจากเลขรุ่น Resolve และ MCP การเตรียมรีลีสไม่ได้อนุญาตให้เชื่อมต่อหรือแก้โปรเจกต์ Resolve โดยอัตโนมัติ

## เตรียมรุ่น

1. ตรวจ `git status` และ `git log <tag ก่อนหน้า>..HEAD` เพื่อรวบรวมสิ่งที่ส่งมอบจริง เว้นไฟล์ส่วนตัวหรือ artifact ที่ไม่เกี่ยวข้อง
2. ตั้งเลขรุ่นใน `VERSION` และบรรทัดรุ่นปัจจุบันใน `README.md` ให้ตรงกัน ใช้ `v<เลขรุ่น>` เป็นหัวข้อใหม่ใน `CHANGELOG.md`
3. เขียน changelog จากหลักฐานใน commit และรายงาน QC ที่มีจริง แยกผลตรวจแบบ static, ผลตรวจใน Resolve และข้อจำกัด ห้ามกล่าวว่าตรวจ render หรือพฤติกรรมจริงแล้วถ้าไม่มีหลักฐาน
4. อัปเดตไฟล์สกิลหรือคู่มือที่เกี่ยวข้องตามขอบเขตงาน และบันทึกเหตุผลการแก้ใน manifest ด้วย `--edit` ซ้ำได้หลายรายการ:

   ```text
   python scripts/refresh_skill_manifest.py --edit "docs/process/release-process.md" "อธิบายขั้นตอนรีลีสของชุดสกิล"
   ```

   สคริปต์อ่าน `VERSION` เพื่อเติม `bundle_version`, เก็บ checksum ของไฟล์ในชุด, ตัดรายการ `edits` ที่ซ้ำ และเรียกตัวตรวจ bundle ต่อ สามารถรันซ้ำโดยส่งคู่ path/reason เดิมได้

## ตรวจชุดก่อนเผยแพร่

1. รัน `python scripts/verify_skill_bundle.py` แล้วอ่าน `docs/validation-report.json`; ต้องไม่มี `errors` ตรวจความครบของไฟล์ checksum สกิล และลิงก์ภายในตามขอบเขตของ validator
2. รัน `git diff --check` และตรวจ diff ด้วยตนเอง ให้แน่ใจว่า `VERSION`, `README.md`, `CHANGELOG.md`, `docs/skills-manifest.json` และรายงาน validation สอดคล้องกัน
3. ถ้ารีลีสอ้างผลการทำงานกับ Resolve ให้แนบหลักฐานการตรวจ live ของฟีเจอร์นั้นตามกฎใน `AGENTS.md` และสกิลที่เกี่ยวข้อง การผ่าน bundle validator ไม่พิสูจน์ว่า script ทำงานกับ Resolve หรือภาพ/เสียงที่ render ถูกต้อง

## Commit, tag และ GitHub Release

ทำขั้นตอนเผยแพร่เมื่อผู้ดูแลอนุมัติรีลีสและผลตรวจครบแล้ว:

```text
git add VERSION README.md CHANGELOG.md docs/skills-manifest.json docs/validation-report.json docs/process/release-process.md
git commit -m "chore(release): prepare skill bundle vX.Y.Z"
git push origin main
git tag -a vX.Y.Z -m "Skill bundle vX.Y.Z"
git push origin vX.Y.Z
gh release create vX.Y.Z --title "Skill bundle vX.Y.Z" --notes-file release-notes.md
```

เพิ่มไฟล์สกิล/สคริปต์ที่เปลี่ยนจริงลงใน commit ด้วย และตรวจชื่อ remote/repository ก่อน push สร้าง `release-notes.md` จาก changelog รุ่นเดียวกัน พร้อมข้อจำกัดการตรวจที่สำคัญ จากนั้นตรวจ tag และ GitHub Release ที่สร้างแล้ว การเตรียมเอกสารหรือ bump `VERSION` เพียงอย่างเดียวไม่ถือว่าออกรีลีสแล้ว
