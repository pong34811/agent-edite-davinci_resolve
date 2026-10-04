# Skills สำหรับ Agent ตัดต่อ DaVinci Resolve

รวบรวม skills จากงานเดิมมาไว้ในโปรเจกต์นี้ โดยไม่ย้ายหรือลบต้นฉบับ ไม่แก้คลิป ไทม์ไลน์ หรือฐานข้อมูล Resolve และไม่เปลี่ยน config ของ Hermes

รุ่นของชุด skills: **v0.6.0** — ดู [CHANGELOG.md](CHANGELOG.md) และ [GitHub Releases](https://github.com/pong34811/agent-edite-davinci_resolve/releases) เลขรุ่นนี้ไม่ใช่เวอร์ชัน Resolve หรือ MCP server

## ชุดหลัก — 17 skills

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
| `thai-subtitles-resolve` | ถอดเสียงไทย ใส่ SRT ลง Subtitle track และจัดฟอนต์ด้วย saved preset พร้อมตรวจ readback |
| `thai-proofread` | ตรวจคำผิดภาษาไทย การสะกด และน้ำเสียงก่อนนำเข้าซับ |
| `resolve-video-enrichment` | ตัดคลิป VTuber ไทย วางจังหวะมุก/ซับ/เสียง เติม SFX/BGM/GIF จัดเฟรม และวัดผล YouTube |
| `resolve-fusion` | Fusion composition / Transform / title / VFX |
| `resolve-color` | ปรับสีและ matching แบบ frame-first |
| `resolve-conform` | Conform/interchange ตรวจ source range และการ relink |
| `resolve-delivery` | Render และตรวจไฟล์ส่งมอบตามสเปก |

ประวัติที่เข้าถึงได้พบการโหลด **14 จาก 17 skills หลัก** ใน sessions ที่เกี่ยวข้องกับ Resolve ส่วน `resolve-color`, `resolve-conform` และ `thai-proofread` รวมไว้ให้ชุดงานครบ แต่ไม่อ้างว่าเคยโหลดจริงจากประวัติที่ตรวจครั้งนี้ การโหลด skill ไม่ได้แปลว่าใช้งานกับทุกคลิปหรือทำงานเสร็จแล้ว

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

## ฐานความรู้คลิป VTuber ไทยและ YouTube

`resolve-video-enrichment` มีแกนงานสั้น พร้อม references 15 ไฟล์และ template 1 ไฟล์ใน `.agents/skills/resolve-video-enrichment/` เรียกอ่านเฉพาะหัวข้อผ่าน `skill_view` ได้:

- `resolve-editing-workflow.md` — เลือกช่วง ตัด/trim และลำดับการเก็บงาน
- `vtuber-story-and-pacing.md` — hook จังหวะมุก reaction และบุคลิกของผู้พูด
- `thai-captions-audio-framing.md` — ซับไทย native เสียงพูดชัด และพื้นที่อวาตาร์/เกม
- `youtube-packaging-and-feedback.md` — ชื่อ/ปก retention และการทดลองปรับคลิปจากข้อมูลจริง
- `youtube-delivery-and-rights.md` — สเปกส่งออก สิทธิ์ตัดคลิป เพลง และขอบเขต monetization
- `automation-safety.md` — รวมข้อควรระวังการสั่งงาน Resolve โดยรักษาต้นฉบับและสถานะ UI
- References เดิม: `asset-coverage.md`, `asset-library-and-cues.md`, `adjustment-focus.md`, `offline-media-repair.md`, `render-qc.md`
- Template: `templates/vtuber-edit-brief.md`

เนื้อหาแยกข้อเท็จจริงจากคู่มือ Blackmagic Design/YouTube Help ออกจากแนวทางสร้างสรรค์ที่ต้องทดลองกับผู้ชม ไม่รับประกันยอดวิว และคำขอเรียนรู้ไม่ใช่การอนุญาตให้แก้โปรเจกต์หรือเผยแพร่คลิป

ผลรีวิว ข้อบกพร่องที่แก้ และประเด็นค้างของงานตัดต่อแยกอยู่ที่ `docs/REVIEW.md`

## Python script สำหรับ Video/GIF style

`scripts/apply_video_style.py` จับค่าคลิปต้นแบบเป็น JSON แล้วใช้กับ video items ที่ระบุ ID
โดยเริ่มจาก dry-run และต้องตรวจ DRP backup ก่อน `--apply` สคริปต์ตรวจ property readback,
เปรียบเทียบ timeline ส่วนที่ต้องคงเดิม, rollback เมื่อผิดพลาด และคืน UI state
คู่มือ: [video-style-script.md](docs/guides/video-style-script.md)

นี่เป็น reference-style fallback **ไม่ใช่การโหลด native Video Preset `vdo`** และไม่เขียน SQL
ตัวอย่างใน `presets/video/approved-gif-style.json` เก็บเฉพาะ property values
โดยตัด ID/ชื่อคลิปจริงออก ต้อง capture จากคลิปที่อนุมัติสำหรับงานจริง

## ใส่ Subtitle และโหลด font preset

อ่าน workflow ที่ `.agents/skills/thai-subtitles-resolve/references/srt-insertion-and-presets.md`:
ใช้ SRT item ที่มีอยู่ใน Media Pool, empty Subtitle track และ bare append payload
ตรวจทุกข้อความ/เฟรม และอ่าน track กลับก่อน retry หาก script ล้มหลัง append

เริ่มค้นชื่อ preset จริงด้วย `scripts/load_subtitle_preset.py --list` และใช้ dry run;
ถ้า preset อยู่คนละ library ให้ตรวจ `--user-db` ที่ค้นพบจริง อย่าแทน `Mitr-Font`
ด้วย `Mitr Font` เอง

บน Resolve 21.1.0.17 helper โหลด subtitle preset เป็น Python/SQLite workaround
**ไม่ใช่ native preset API** จึงต้องอนุมัติ database write แยกต่างหาก สำรองและปิด project
ก่อนเขียน แล้วเปิดกลับตรวจ style bytes, ข้อความ/เฟรม และ coverage

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

Tests ของ contact sheet ต้องมี Pillow ด้วย ใช้ environment ที่ตรวจว่ามีแล้ว; ไม่ติดตั้งแพ็กเกจอัตโนมัติ ตัวตรวจสอบตรวจทั้งไฟล์ที่ตกหล่นจาก manifest และการจับคู่รายการ skills กับไฟล์จริง ไม่ใช่ตรวจเพียงจำนวนเท่ากัน

การตรวจนี้ครอบคลุม **ชุด skills** ไม่ใช่การตัดต่อคลิปให้เสร็จ `PLAN.md`, `WORKLOG.md`, `reference/` และ `.mcp.json` เป็นบริบทงานแยก ไม่ได้รวมใน provenance หรือการรับรองนี้ สถานะการแก้คลิปต้องตรวจจากหลักฐานของงานนั้นและ Resolve จริง ไม่ใช่จากผล tests ชุดนี้

`docs/skills-manifest.json` บันทึกแหล่งที่มา SHA-256 ของต้นฉบับ/สำเนา รายการปรับเฉพาะโปรเจกต์ และ history anchors โดยไม่คัดลอกข้อความสนทนาหรือ secrets

Checksum ตรวจไบต์จริงก่อน และยอมรับเฉพาะความต่าง LF/CRLF สำหรับไฟล์ข้อความ UTF-8 ที่ Git แปลงตอน checkout/archive เท่านั้น ไม่ข้ามการเปลี่ยนเนื้อหา ช่องว่าง หรือไบต์ของไฟล์ binary

## ขอบเขต

นี่คือ **ชุด skills และคู่มือ ไม่ใช่ MCP server ตัวใหม่** ต้องใช้ backend `davinci-resolve-mcp` ที่มีอยู่หรือ scripting bridge ที่ตรวจการเชื่อมต่อจริงก่อนลงมือ คำสั่งเกี่ยวกับ `src/server.py` ในคู่มือต้นทางให้รันจาก installation ของ backend ไม่ใช่จากโปรเจกต์นี้

ไม่ได้รวม `release-check` ซึ่งใช้ปล่อยเวอร์ชัน server, งาน Canva thumbnail/YouTube downloader ที่เป็นคนละ workflow, source footage, ไฟล์ SRT ของคลิป, render, หรือ Project.db รุ่นนี้เผยแพร่ชุดเอกสาร/skills ไม่ใช่การปล่อย MCP server หรือหลักฐานว่าตัดต่อคลิปเสร็จแล้ว
