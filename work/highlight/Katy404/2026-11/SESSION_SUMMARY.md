# สรุปการทำงาน Davinci Team (2026-11-22 ถึง 2026-11-23)

ผู้สรุป: claude (หัวหน้าทีม) — ใช้เป็นอินพุตให้ `project-learning`

## 1. ตั้งทีมและบทบาท
- แบ่งหน้าที่: claude = producer-lead, antigravity = resolve-editor (16:9+9:16), opencode = render-qc + editor สำรอง, chatgpt = thai-content, hermes = floating-helper
- เขียนไฟล์ role ลง `.agents/roles/` (README, producer-lead, resolve-editor, render-qc, thai-content, floating-helper) ชี้จาก `AGENTS.md`; commit `3822be0`, release `v0.17.122`
- กติกากลาง: ใช้ Resolve ทีละคน ต้องประกาศว่าถือคิว, backup `.drp` ก่อนแก้, ห้ามอัปโหลด/ลบโดยไม่สั่ง

## 2. Katy404 วันที่ 35 (16:9 + 9:16)
- ตัดหัวเมนู/ท้ายเงียบ เหลือ 3,342 เฟรม, ซูม VTuber, ซับ 33 cues, promote เป็น `Timeline 1`, ทำ `Timeline 1_9x16`
- ปัญหา: ตัวละคร 9:16 เยื้องขวา ~118–133 px เพราะลอกค่า day 30 → วัดใหม่จากเฟรม day 35 แล้วเหลือ ≤27 px; ซูมเต็มจอ 4.27 ทำให้ซับทับตา → 3.3
- ปัญหา: 3 agent ลงมือแก้งานเดียวกันพร้อมกัน → เกิดกติกาประกาศถือคิว
- เสียง: ต้นทาง −29.4 LUFS; render แรก −17.8 LUFS / true peak +0.1; ใส่ Dialogue Leveler + A1 16 dB ได้ −13.8 LUFS แต่ true peak +0.3 (API ไม่มี limiter) → ผู้ใช้รับงานแล้ว ไม่ระบุวิธีแก้พีค

## 3. โหลดเพลย์ลิสต์ 2026-11 (14 คลิป)
- claude โหลดด้วย yt-dlp ≤1080p H.264 MP4 ลง `G:\My Drive\Projects\Katy404\2026-11` ครบ 14 ไฟล์ ความยาวตรง YouTube ±3 วิ
- ปัญหา: รอบแรกใช้ path แบบ git-bash (`/g/...`) กับ yt-dlp ของ Windows ไฟล์ไปลง `D:\g\...` → ใช้ path `G:/...` หรือ `-P` เสมอ
- ปัญหา: hermes รันตัวโหลดซ้ำ 7 ชุดพร้อมกันลงโฟลเดอร์เดียวกัน + D: (ไฟล์ซ้ำ ~110 GB, .part 16 GB) แม้มีไฟล์ `_DOWNLOADING_by_claude.txt` → ลบไฟล์ซ้ำตามที่ผู้ใช้สั่งหลังโหลดครบ
- บทเรียน: งานที่สั่ง @everyone ต้องให้คนเดียวรับ คนอื่นตรวจ claim file/process ก่อนลงมือ

## 4. คัดไฮไลต์ 2026-11 และสร้าง timeline
- job `work/highlight/Katy404/2026-11/job.json` (30–180 วิ, gameplay/fun/meme, 3–4 คลิป/วิดีโอ, APPROVAL auto); inventory 14 ไฟล์ รวม 29 ชม. 33 นาที (ffprobe ของ hermes ตรง inventory)
- features/shortlist ครบ; full ASR ต้องใช้ Python ระบบ (`Python313`) เพราะ `.venv` ของ repo ไม่มี `faster_whisper`; ASR อ่านจาก G: ช้าลง (~45 นาทีรวม)
- อ่านแพ็ก: claude v02 ทั้งสอง, chatgpt v01-01..03, opencode v01-04..06, antigravity v01-07 + v03-01, hermes v03-02..03 (มาช้า); วิดีโอที่เหลือ claude คัดเองจาก top 10–12 shortlist windows + transcript (อาจพลาดช่วงเงียบ)
- ผลลัพธ์: 56 คลิปใน `review/v01..v14.json` (schema gate ผ่าน), สรุป `selected_clips.md`
- สร้าง timeline ด้วย Python API (MCP ไม่ได้ต่อใน session ของ claude): `CreateTimelineFromClips` ใช้ `endFrame` แบบ exclusive (ส่ง end-1 ได้สั้นไป 1 เฟรม) → `verify_timelines.py` ผ่าน 56/56

## 5. ความผิดพลาดตอนสร้างโปรเจกต์ (ผู้ใช้ทักด้วยภาพ Save Current Project)
- สาเหตุ: สคริปต์เรียก `pm.SaveProject()` ขณะโปรเจกต์ปัจจุบันเป็น "Untitled Project" หลังเปิด Resolve → dialog Save Current Project → Resolve Not Responding, API ค้าง
- สร้างครั้งแรกด้วย `CreateProject(name)` ไม่มี media location (ขัดกับ commit `61b5e0d` / สกิล `resolve-mcp` 0.5.0)
- ระหว่างค้าง probe `CreateProject` ถูกส่งค้างไว้ แล้วไปสร้าง `zz_probe_tmp_claude` หลัง dialog ปิด (ภายหลังหาไม่พบในโฟลเดอร์ใด)
- หลายคนต่อ MCP เข้า Resolve พร้อมกันหลังผู้ใช้ทัก @everyone
- แก้: backup `backups/kt404_highlights_2026-11_wrong_create.drp` → ลบโปรเจกต์ผิด → `CreateProject("KT404 Highlights 2026-11", "G:/My Drive/Projects/Katy404/2026-11")` ในโฟลเดอร์ `Katy404/2026-11` → import 14 ไฟล์ → สร้าง 56 timeline ใหม่ → verify 56/56
- บันทึกแล้วใน `docs/OPERATING-NOTES.md` (ห้าม SaveProject บน Untitled, สร้างด้วย name + media location)
- ค้าง: `timelinePlaybackFrameRate` ตั้งผ่าน API ไม่ติด (อ่านได้ 24) ให้ผู้ใช้ตั้งเอง

## 6. ข้อมูลที่ยังไม่ได้ยืนยัน / งานค้าง
- ชื่อคลิปทั้ง 56 มาจาก ASR ยังไม่มีใครฟัง
- Day 35 true peak +0.3 dBFS ยังไม่มีวิธีแก้ที่เลือก
- ยังไม่ commit: `docs/OPERATING-NOTES.md`, `docs/channels/katy404.md`, `docs/skills-manifest.json`, `work/highlight/Katy404/2026-11/`
- สคริปต์ชั่วคราวใน `scripts/scratch/hl2611/` (condense, topn, write_review, setup_project, recreate_project, create_timelines) — antigravity แก้ `setup_project.py` ด้วย; สคริปต์สร้างโปรเจกต์/timeline ด้วย Python ยังไม่มีใน `scripts/`
