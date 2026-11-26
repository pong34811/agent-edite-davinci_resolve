# Skills และคู่มือสำหรับทีม Agent ตัดต่อ DaVinci Resolve

ชุด skills, roles, สคริปต์ และบทเรียนจากงานจริงของทีมตัดต่อคลิป VTuber ไทยใน DaVinci Resolve
ไม่ใช่ MCP server ตัวใหม่ และไม่เก็บ source footage, SRT ของคลิป, render หรือ Project.db

รุ่นของชุด: **v0.17.126** (ไฟล์ `VERSION`) — ดู [CHANGELOG.md](CHANGELOG.md) และ
[GitHub Releases](https://github.com/pong34811/agent-edite-davinci_resolve/releases)
เลขรุ่นนี้ไม่ใช่เวอร์ชัน Resolve หรือ MCP server

## เริ่มต้นตรงไหน

| ต้องการ | อ่าน |
|---|---|
| กฎทำงานทุกงาน (MCP ก่อน, backup ก่อนแก้, ไม่ render ถ้าไม่สั่ง) | [AGENTS.md](AGENTS.md) |
| ข้อผิดพลาดที่เคยเจอและกฎกันซ้ำ | [docs/OPERATING-NOTES.md](docs/OPERATING-NOTES.md) |
| ค่าเฉพาะของแต่ละช่อง (ฟอนต์ซับ, เรขาคณิตอวตาร์, ชื่อ timeline) | [docs/channels/README.md](docs/channels/README.md) |
| แบ่งงานในทีมหลาย agent | [.agents/roles/README.md](.agents/roles/README.md) |
| หาว่า skill ไหนรับงานไหน | `.agents/skills/agent-edite-skills-catalog/SKILL.md` |
| งานไฮไลต์หลายคลิปจากไลฟ์ยาว (16:9 + 9:16) | `.agents/skills/resolve-highlight-batch-production/SKILL.md` |
| เปิดงาน/ช่องใหม่ | `.agents/skills/new-channel-job-setup/SKILL.md` |
| บันทึกบทเรียนหลังจบงาน (/learn) | `.agents/skills/project-learning/SKILL.md` |

## ทีมและหน้าที่ (Davinci Team, 2026-11-26)

| หน้าที่ | Agent | ไฟล์ role |
|---|---|---|
| Producer / Lead + /learn (แบ่งงาน, ให้สิทธิ์เขียน Resolve, ตรวจรอบสุดท้าย, commit/push) | Hermes-claude | `producer-lead.md` |
| Resolve editor (16:9 + 9:16) | antigravity | `resolve-editor.md` |
| Render & QC + editor สำรอง | opencode | `render-qc.md` |
| Thai content + floating helper | Hermes chatgpt | `thai-content.md`, `floating-helper.md` |

กฎหลัก: แก้ Resolve ได้ทีละคน (lead ให้สิทธิ์ตามชื่อ), "เสร็จ" ต้องมี path + จำนวน + ผลตรวจ 1 อย่าง,
ไม่ upload / render / ลบ timeline ถ้าผู้ใช้ไม่ได้สั่ง รายละเอียดอยู่ใน `.agents/roles/`

## ชุด Skills — 90 ชุดที่เปิดใช้ + 13 ชุดอ้างอิง

อยู่ที่ `.agents/skills/` แหล่งที่มาและ SHA-256 ทุกไฟล์อยู่ใน `docs/skills-manifest.json`

### ชุดหลักงานตัดต่อ — 17 ชุด

| Skill | หน้าที่ |
|---|---|
| `house-style` | กฎการตัดต่อและสไตล์ซับไทย |
| `resolve-session` | ตรวจการเชื่อมต่อ เวอร์ชัน โปรเจกต์ และไทม์ไลน์ก่อนเริ่มงาน |
| `resolve-mcp` | แผนที่เครื่องมือ Resolve แบบ live และ offline |
| `resolve-media-pool` | นำเข้าและจัดระเบียบสื่อ ตรวจและวางแผน relink |
| `resolve-media-analysis` | วิเคราะห์ภาพ เสียง และเนื้อหาฟุตเทจก่อนตัด |
| `video-footage-review` | ตรวจฟุตเทจ ทำ cutlist และเลือกไฮไลต์ |
| `resolve-rough-cut` | ประกอบ first pass / rough cut |
| `resolve-tighten-recording` | ตัด dead air จากคลิปยาว และสร้าง variant |
| `resolve-edit` | ตัด ย้าย คัดลอกช่วง ปรับ pacing และโครงสร้างไทม์ไลน์ |
| `resolve-audio` | Fairlight การมิกซ์ การถอดเสียง และขอบเขต API |
| `thai-subtitles-resolve` | ถอดเสียงไทย ใส่ SRT ลง Subtitle track จัดฟอนต์ด้วย preset และตรวจ readback |
| `thai-proofread` | ตรวจคำผิดและการสะกดภาษาไทยก่อนนำเข้าซับ |
| `resolve-video-enrichment` | จังหวะมุก/ซับ/เสียง เติม SFX/BGM/GIF จัดเฟรม และวัดผล YouTube |
| `resolve-fusion` | Fusion composition / Transform / title / VFX |
| `resolve-color` | ปรับสีและ matching แบบ frame-first |
| `resolve-conform` | Conform/interchange ตรวจ source range และ relink |
| `resolve-delivery` | Render และตรวจไฟล์ส่งมอบตามสเปก |

### ชุดเสริม — 73 ชุด

- **งานไฮไลต์และแนวตั้ง:** `resolve-highlight-batch-production`, `long-video-highlight-clipping`, `livestream-highlight-clipping`, `highlight`, `vertical-video-reframing`, `talking-avatar-vertical-copy`, `resolve-clip-editing`, `resolve-smart-edit`, `resolve-trim-to-length`
- **Resolve workflow:** `davinci-resolve-api`, `resolve-batch-export`, `resolve-folder-cover-batch`, `resolve-mitr-subtitle-presets`, `resolve-offline-media-repair`, `resolve-project-folder-targeting`, `resolve-project-media-storage`, `resolve-still-qc-capture`, `timeline-naming-convention`, `video-provider-smoke-qc`
- **ช่อง/ปก/YouTube:** `katy404-minecraft-editing`, `katy404-canva-thumbnails`, `kt404-youtube-upload`, `vtuber-content-curriculum`, `vtuber-cover-batch-pipeline`, `vtuber-cover-source-video`, `vtuber-thumbnail-layout`, `vtuber-thumbnail-qc`, `youtube-content`, `youtube-downloader`
- **ซับ / SFX / GIF:** `subtitle-analyzer`, `sfx-library-manager`, `sfx-story-analyzer`, `gif-search`
- **HyperFrames (กราฟิก/โมชัน):** `hyperframes`, `hyperframes-animation`, `hyperframes-cli`, `hyperframes-core`, `hyperframes-creative`, `hyperframes-keyframes`, `hyperframes-registry`, `general-video`, `media-use`, `pop-kinetic-chapter-gap`
- **ทีม/ความรู้/รีลีส:** `agent-edite-skills-catalog`, `project-learning`, `new-channel-job-setup`, `user-feedback-capture`, `agent-skill-repo-release`, `llm-wiki`, `last30days`, `grill-me`, `grilling`
- **Ponytail (ทำแบบน้อยที่สุดที่ใช้ได้):** `ponytail`, `ponytail-audit`, `ponytail-debt`, `ponytail-gain`, `ponytail-help`, `ponytail-review`
- **Superpowers 7.0.0** (โฟลเดอร์ `superpowers-*`, ชื่อใน frontmatter ไม่มี prefix): `brainstorming`, `diagnosing-superpowers`, `dispatching-parallel-agents`, `executing-plans`, `finishing-a-development-branch`, `receiving-code-review`, `requesting-code-review`, `subagent-driven-development`, `systematic-debugging`, `test-driven-development`, `using-git-worktrees`, `using-superpowers`, `verification-before-completion`, `writing-plans`, `writing-skills`

### ชุดอ้างอิง — 13 ชุด

อยู่ที่ `docs/related-skills/` เป็นเอกสารอ้างอิง ไม่เปิดเป็น skill อัตโนมัติ:
`computer-use`, `songsee`, `codex`, `systematic-debugging`, `grounded-citations`, `blocked-page-recovery`
และ Superpowers 7 ชุด (`brainstorming`, `test-driven-development`, `dispatching-parallel-agents`,
`systematic-debugging`, `executing-plans`, `verification-before-completion`, `using-superpowers`)

## โปรไฟล์ช่อง

`docs/channels/` เก็บค่าที่ยืนยันแล้วของแต่ละช่อง: `katy404`, `aomimama`, `armigon`, `hoshi-1489`,
`kael`, `laffy`, `sakuyako-cheris`, `tygarina` — ค่าที่เปลี่ยนรายวัน (ศูนย์กลางอวตาร์, ซูม, crop)
ต้องวัดจากฟุตเทจของวันนั้นใหม่ทุกครั้ง ไม่คัดลอกจากวันก่อน

## เตรียมงานและเกณฑ์ตรวจรับกลาง

ดู [docs/EDIT-WORKFLOW.md](docs/EDIT-WORKFLOW.md): ใช้ `python scripts/prepare_edit.py <source-folder> --out-dir scratch/edit-review`
เพื่อสร้าง intake พร้อม probe cache และแบบร่างแผนตัดต่อ จากนั้นใช้ `scripts/edit_workflow.py`
ตรวจ source/record frames และหลักฐานส่งงานตาม house style ทั้งหมดทำงาน offline โดยไม่แก้ Resolve

## Python script สำหรับ Video/GIF style

`scripts/apply_video_style.py` จับค่าคลิปต้นแบบเป็น JSON แล้วใช้กับ video items ที่ระบุ ID
เริ่มจาก dry-run และต้องตรวจ DRP backup ก่อน `--apply` สคริปต์ตรวจ property readback,
เปรียบเทียบ timeline ส่วนที่ต้องคงเดิม, rollback เมื่อผิดพลาด และคืน UI state
คู่มือ: [video-style-script.md](docs/guides/video-style-script.md)

นี่เป็น reference-style fallback **ไม่ใช่การโหลด native Video Preset `vdo`** และไม่เขียน SQL
ตัวอย่างใน `presets/video/approved-gif-style.json` เก็บเฉพาะ property values

## เพิ่ม SFX / BGM / GIF ให้ทุก Timeline (offline + Resolve Python)

**ทำสำเนาก่อน แล้วค่อยย้ายเข้าต้นฉบับ**:

| ขั้น | คำสั่ง |
|---|---|
| ตรวจว่าควรใช้ MCP หรือ script | `python -m scripts.resolve_preflight --need <tool>` |
| สำรวจ timeline/asset แบบอ่านเท่านั้น | `python -m scripts.review_enrichment_readonly` |
| สร้างหลักฐานต่อ timeline (ซับ/เสียง/ภาพตัวอย่าง) | `python -m scripts.build_offline_review --first 1 --last 49` |
| ร่างจุด SFX/GIF + หน้าให้คนตรวจ | `python -m scripts.build_offline_asset_draft` |
| จับค่า preset `vdo` แล้วใช้กับ GIF | `python -m scripts.apply_vdo_python --capture-from-clip-id ...` |
| เพิ่มเอฟเฟกต์บนสำเนา (dry-run ก่อน) | `python -m scripts.enrich_timelines_python --all --project-id ...` |
| ย้ายเข้าต้นฉบับแบบทำซ้ำได้ | `python -m scripts.promote_drafts_to_originals --all --project-id ... --apply` |
| ตรวจความผิดปกติทั้งโปรเจกต์ | `python -m scripts.anomaly_sweep` |
| สำรองใหม่แล้วลบ archive เก่า | `python -m scripts.cleanup_backups --confirm` |

ข้อจำกัดที่ต้องรายงานเสมอ: จุดจากซับไม่ใช่จังหวะมุกที่ตรวจรับแล้ว, ระดับเสียงต้องวัดจากไฟล์จริง
(`ffmpeg -af ebur128=peak=true`), และ `vdo` คือการคัดลอกค่าที่จับได้ ไม่ใช่ native named-preset loader

## ใส่ Subtitle และโหลด font preset

อ่าน workflow ที่ `.agents/skills/thai-subtitles-resolve/references/srt-insertion-and-presets.md`:
ใช้ SRT item ที่มีอยู่ใน Media Pool, empty Subtitle track และ bare append payload
ตรวจทุกข้อความ/เฟรม และอ่าน track กลับก่อน retry หาก script ล้มหลัง append
ก่อนนำเข้า ตรวจเวลา SRT เทียบเสียงของคลิปเองทุกครั้ง (ทั้ง 16:9 และ 9:16)

ค้นชื่อ preset จริงด้วย `scripts/load_subtitle_preset.py --list` และใช้ dry run;
อย่าแทน `Mitr-Font` ด้วย `Mitr Font` เอง บน Resolve 21.1.0.17 helper อ่าน preset ผ่าน
Python/SQLite workaround (ไม่ใช่ native preset API) และ `--apply` ยังถูกบล็อกก่อนเขียนฐานข้อมูล

ภาพนิ่งจาก `ExportCurrentFrameAsStill` ไม่รวมแทร็กซับ — ตำแหน่งซับต้องตรวจจากไฟล์ render เท่านั้น

## ซิงก์หลายเครื่อง (Multi-PC)

ทุกเครื่องทำงานบน `main` เท่านั้น ก่อนเริ่มงาน: `git fetch origin --prune` แล้ว `git pull --ff-only origin main`
ถ้ามีไฟล์ที่ track ค้างหรือ local นำหน้า ให้ commit/stash ก่อน ห้าม `reset --hard`, `clean` หรือ force
โฟลเดอร์งานในเครื่อง (`backups/`, `work/`, `scripts/scratch/`, `.venv/`) ไม่อยู่ใน git

## ใช้กับ Hermes

Hermes รองรับ project-local skills ใน `.agents/skills/` แต่ต้อง trust โปรเจกต์ก่อน จากไดเรกทอรีนี้:

```bash
hermes skills trust
```

แล้วเริ่ม session ใหม่ หากยังไม่ trust สั่ง agent อ่าน SKILL.md ในโปรเจกต์โดยตรงได้
คู่มือ: https://hermes-agent.nousresearch.com/docs/user-guide/features/skills#project-local-skills

## ตรวจความครบของชุด

```bash
python -m pytest -q
python scripts/refresh_skill_manifest.py   # หลังแก้ไฟล์ใน .agents/ หรือ docs/
python scripts/verify_skill_bundle.py
```

Validator ต้องมี PyYAML, tests ของ contact sheet ต้องมี Pillow (บน Windows ใช้ `py -3.13`)
ผลตรวจล่าสุดอยู่ที่ `docs/validation-report.json` Checksum ตรวจไบต์จริง ยอมรับเฉพาะความต่าง LF/CRLF ของไฟล์ข้อความ

การตรวจนี้ครอบคลุม **ชุด skills และเอกสาร** ไม่ใช่การตัดต่อคลิปให้เสร็จ สถานะงานตัดต่อต้องตรวจจากหลักฐานของงานนั้นและ Resolve จริง

## ขอบเขต

ต้องใช้ backend `davinci-resolve-mcp` ที่มีอยู่ หรือ scripting bridge ที่ตรวจการเชื่อมต่อจริงก่อนลงมือ
ไม่ได้รวม `release-check` ของ MCP server, implementation ของ YouTube downloader/Canva (มีเฉพาะคู่มือสกิล),
source footage, SRT ของคลิป, render หรือ Project.db
