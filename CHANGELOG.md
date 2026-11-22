# Changelog

## v0.17.117 — Bunny Girl ep12 แนวตั้ง 9:16

### รายละเอียด
- Bunny Girl ep12: สร้าง `Timeline 1_9x16` (1080x1920) จาก `Timeline 1` โดยไม่แก้ต้นฉบับ ซับ preset `Mitr-short-001` ผ่าน DRT (ไม่เขียน DB), ภาพเต็มจอที่หน้า, ซูม 1.1x 5 ช่วง และกราฟิก Pop Kinetic แนวตั้งจัดกึ่งกลาง 4 บท
- render ทดสอบ `Bunny Girl ep12_9x16_test_2026-11-22.mp4`: 4077 เฟรม, -16.0 LUFS, peak -0.8 dBFS, ไม่มีเฟรมดำ, ซับอยู่ระดับคอ/อก ไม่ชนคำกระแทก

### Skill ที่อัปเดต
- ไม่มี

### ไฟล์ที่เปลี่ยน
- แก้ไข `docs/channels/katy404.md`
- แก้ไข `docs/skills-manifest.json`

## v0.17.116 — Bunny Girl ep12 อัปเดต Timeline หลักและลบ timeline สำรอง

### รายละเอียด
- Bunny Girl ep12: เปลี่ยนชื่อ `Timeline 1_pop_mitr` เป็น `Timeline 1` และลบ timeline สำรอง 3 อัน (ต้นฉบับ, `_base`, `_pop`) ด้วย ID ในคำสั่งเดียว ตามที่ผู้ใช้สั่ง
- อ่านกลับทุก track และ gain เท่าเดิม (V1 5, V2 5, V3 4, A1 3, A2 20, A3 1, ซับ 68 cue, 4077 เฟรม); สำรอง `pre_promote.drp` ก่อนลบ

### Skill ที่อัปเดต
- ไม่มี

### ไฟล์ที่เปลี่ยน
- แก้ไข `docs/channels/katy404.md`
- แก้ไข `docs/skills-manifest.json`

## v0.17.115 — ตัดต่อ Bunny Girl ep12 และกฎ timeline ที่ตัดหัว

### รายละเอียด
- ตัดต่อ Bunny Girl ep12 "รู้สึกยังไงตอนใส่ชุดบันนี่เกอร์ครั้งแรก" (Katy404) เป็น `Timeline 1_pop_mitr`: การ์ด CHAPTER 2 ใบพร้อมช่วงเงียบ 1.6 วิ, ซูม VTuber 5 ช่วง, กราฟิก Pop Kinetic 4 บท, ซับไทย 68 cue จาก Descript (Mitr Font), SFX 20 จุด และ BGM; `Timeline 1` ต้นฉบับไม่ถูกแก้
- render ทดสอบ `Bunny Girl ep12_POP_test_v2_2026-11-22.mp4` ผ่าน: 4077 เฟรม 1920x1080@60, -16.0 LUFS, true peak -0.8 dBFS, ไม่มีเฟรมดำ, ช่วงการ์ดเงียบ -29/-30 dB และไม่มีซับบนการ์ด
- เพิ่มกฎใน OPERATING-NOTES: ถ้า `Timeline 1` ไม่ได้เริ่มที่ source frame 0 (ผู้ใช้ตัดหัว) ต้องบวก offset ให้ทุกช่วง V1/A1 และตัดไฟล์เสียงวิเคราะห์จากจุดนั้น
- รอบนี้ push commit ค้างอีก 2 รายการที่มีอยู่ก่อนงานนี้ (skill pop-kinetic-chapter-gap, wipe_gap_plan, เอกสารช่อง, `.mcp.json` และบันทึก Aomi-mama) จึงอาจเห็นไฟล์เหล่านั้นในรายการไฟล์ที่เปลี่ยน

### Skill ที่อัปเดต
- `house-style` (แก้ไข): `SKILL.md`
- `pop-kinetic-chapter-gap` (ใหม่): `SKILL.md`
- `resolve-delivery` (แก้ไข): `SKILL.md`
- `resolve-fusion` (แก้ไข): `SKILL.md`
- `resolve-mitr-subtitle-presets` (แก้ไข): `SKILL.md`
- `resolve-project-media-storage` (ใหม่): `SKILL.md`
- `talking-avatar-vertical-copy` (แก้ไข): `SKILL.md`
- `thai-subtitles-resolve` (แก้ไข): `SKILL.md`

### ไฟล์ที่เปลี่ยน
- แก้ไข `.agents/skills/house-style/SKILL.md`
- เพิ่ม `.agents/skills/pop-kinetic-chapter-gap/SKILL.md`
- แก้ไข `.agents/skills/resolve-delivery/SKILL.md`
- แก้ไข `.agents/skills/resolve-fusion/SKILL.md`
- แก้ไข `.agents/skills/resolve-mitr-subtitle-presets/SKILL.md`
- เพิ่ม `.agents/skills/resolve-project-media-storage/SKILL.md`
- แก้ไข `.agents/skills/talking-avatar-vertical-copy/SKILL.md`
- แก้ไข `.agents/skills/thai-subtitles-resolve/SKILL.md`
- แก้ไข `.gitignore`
- แก้ไข `.mcp.json`
- เพิ่ม `IDEA.md`
- แก้ไข `docs/OPERATING-NOTES.md`
- แก้ไข `docs/channels/aomimama.md`
- แก้ไข `docs/channels/armigon.md`
- แก้ไข `docs/channels/katy404.md`
- แก้ไข `docs/channels/laffy.md`
- แก้ไข `docs/skills-manifest.json`
- แก้ไข `docs/validation-report.json`
- แก้ไข `scripts/INDEX.md`
- แก้ไข `scripts/focus_qc_frames.py`
- เพิ่ม `scripts/wipe_gap_plan.py`
- เพิ่ม `tests/test_wipe_gap_plan.py`

## v0.17.114 — บทเรียนส่งงานซับ CTC: สำเนา timeline + QC ครบวงจร

### รายละเอียด
- เพิ่ม `references/ctc-retime-delivery.md` ใน thai-subtitles-resolve: ขั้นตอนครบวงจรจากงาน Laffy แนะนำตัว 3 นาที — ตรวจซับที่จัดเวลาด้วย Whisper ด้วย CTC forced alignment (พบคลาด > 0.2 วิ 35/151 cue, สูงสุด 1.3 วิ), ให้คะแนนคำที่สงสัยด้วย local_ctc (นี้→เนี้ย, บ้าง→มั่ง; คะแนนใกล้เคียงกันให้คงข้อความ Descript), จัดเวลาใหม่ (รวม cue สั้น "น่ะ" 7 เฟรมเป็น "สัมผัสมันเฉยๆน่ะ", 151→150 cue), สร้าง timeline `_v2` สำเนาโดยไม่แตะของเดิม (DRP snapshot ก่อนแก้, DRT clone สไตล์ซับของ timeline เอง, readback ทุกแทร็ก V/A + Fusion zoom และ cue ตรงแผนทุกตัว), ปิดท้ายด้วย render/QC (4407 เฟรม, -14.4 LUFS, ภาพนิ่ง burn-in 6 จุดตรวจซับไม่ทับซ้อนตรงเฟรม)
- อัปเดต SKILL.md เป็น v0.5.12: เพิ่ม delivery gates ในหัวข้อ CTC และปรับ description เป็น "Insert, style, and CTC-sync Thai subtitles in Resolve." (54 ตัวอักษร)
- เพิ่มรายละเอียด visual QC ภาพนิ่ง 6 จุดใน docs/channels/laffy.md และแก้การอ้างสคริปต์ scratch เป็น path เต็ม (ให้ผ่านการทดสอบ channel profile)
- เพิ่มกฎใน docs/OPERATING-NOTES.md: แก้ skill ใน repo ด้วย `patch`/`write_file` เพราะ `skill_manage` อาจชนสำเนาเก่าชื่อเดียวกันใน profile dir
- ตรวจแล้ว: refresh manifest + test_skill_bundle 9 passed, full suite 459 passed / 35 skipped (แก้ 1 failure เดิมเรื่องชื่อสคริปต์ใน laffy.md), test_channel_profiles 12 passed

### Skill ที่อัปเดต
- `thai-subtitles-resolve` (แก้ไข): `SKILL.md`, `references/ctc-retime-delivery.md`

### ไฟล์ที่เปลี่ยน
- แก้ไข `.agents/skills/thai-subtitles-resolve/SKILL.md`
- เพิ่ม `.agents/skills/thai-subtitles-resolve/references/ctc-retime-delivery.md`
- แก้ไข `docs/OPERATING-NOTES.md`
- แก้ไข `docs/channels/laffy.md`
- แก้ไข `docs/skills-manifest.json`
- แก้ไข `docs/validation-report.json`

## v0.17.113 — ตรวจและจัดเวลาซับ Laffy แนะนำตัวด้วย CTC

### รายละเอียด
- ตรวจซับคลิป Laffy แนะนำตัว 3 นาทีกับเสียงด้วย CTC forced alignment: timeline ที่เคยจัดเวลาด้วย Whisper ยังคลาดเกิน 0.2 วิ 35 cue (สูงสุด 1.3 วิ)
- สร้าง timeline ใหม่ `เเนะนำตัว 3 นาที_edit_v2` (150 cue) แก้ข้อความตามที่พูดจริง 3 จุด (ประมาณเนี้ย, มั่ง x2) และรวม cue สั้น "น่ะ"; อ่านกลับแล้ววิดีโอ/เสียงทุกแทร็กเหมือนเดิม และ cue ตรงกับแผนทุกตัว
- render `laffy_intro_edit_v6.mov` เสร็จ 4407 เฟรม 1080p30 + AAC, -14.4 LUFS, ตรวจภาพนิ่ง 6 จุดเห็นซับถูกต้อง
- เพิ่มบทเรียนใน thai-subtitles-resolve: ซับที่จัดเวลาด้วย Whisper ยังไม่ถือว่าตรวจแล้ว และวิธีให้คะแนนคำที่สงสัยด้วย local_ctc

### Skill ที่อัปเดต
- `thai-subtitles-resolve` (แก้ไข): `SKILL.md`

### ไฟล์ที่เปลี่ยน
- แก้ไข `.agents/skills/thai-subtitles-resolve/SKILL.md`
- แก้ไข `docs/channels/laffy.md`
- แก้ไข `docs/skills-manifest.json`

## v0.17.112 — ตรวจและจัดเวลาซับ Laffy เหตุผลที่มาเป็นวีใหม่

### รายละเอียด
- ตรวจซับคลิป Laffy "เหตุผลที่มาเป็นวี" เทียบกับเสียงทีละ cue: ข้อความ Descript ตรงกับเสียงแทบทั้งหมด แต่เวลาคลาดเกิน 0.2 วิ 70 จาก 251 cue (สูงสุด 1.3 วิ) เพราะเวลาคำของ Whisper ภาษาไทยมาก่อนเสียงจริงราว 0.36 วิ และมีช่วงที่ถอดไม่ออก
- จัดเวลาซับใหม่ด้วย CTC forced alignment (โมเดล wav2vec2 ไทย) ซึ่งวัดแล้วคลาดจากจุดเริ่มเสียงพูดเพียงราว 0.05 วิ ได้ timeline ใหม่ `เหตุผลที่มาเป็นวี_edit_v2` 247 cue แทร็กภาพ/เสียงอื่นตรงกับ `_edit` ทุกชิ้น และ render v3 ผ่านการตรวจ (7212 เฟรม, -14.3 LUFS)
- บันทึกวิธีจัดเวลาด้วย forced alignment ลง skill `thai-subtitles-resolve` (v0.5.10) และบันทึกผลลงโปรไฟล์ช่อง Laffy

### Skill ที่อัปเดต
- `thai-subtitles-resolve` (แก้ไข): `SKILL.md`

### ไฟล์ที่เปลี่ยน
- แก้ไข `.agents/skills/thai-subtitles-resolve/SKILL.md`
- แก้ไข `docs/channels/laffy.md`
- แก้ไข `docs/skills-manifest.json`

## v0.17.111 — งานตัดคลิป Laffy เหตุผลที่มาเป็นวี และบทเรียนการ์ด

### รายละเอียด
- ตัดต่อคลิป Laffy "เหตุผลที่มาเป็นวี" ใน Resolve เป็น timeline ใหม่ `เหตุผลที่มาเป็นวี_edit` (ไม่แตะ Timeline 1): ซับไทย Mitr Font 251 cue, VTuber Zoom 7 ช่วง, การ์ดคีย์เวิร์ด 18 ใบ, ป้ายบทมุมจอ 3 บท, SFX และ BGM; render `laffy_reason_edit_v2.mov` ตรวจแล้ว 7212 เฟรม, -14.3 LUFS, true peak -0.5 dBFS และตรวจภาพ 9 เฟรม
- บันทึกข้อมูลงานนี้ในโปรไฟล์ช่อง Laffy (คำสั่งผู้ใช้: ไม่มี hook, ไม่ตัดคำซ้ำ, ชื่อทีมมู/dreamlight projects, ระดับเสียง SFX ที่ใช้จริง)
- แก้วิธีทำการ์ดภาษาไทย: ฝังฟอนต์ Mitr แบบ data URI จาก `C:\Windows\Fonts` และวัดขนาดหลัง `document.fonts.ready` เพราะ path เดิมไม่มีอยู่และ Chrome ใช้ฟอนต์ serif แทนโดยไม่แจ้ง
- เพิ่มวิธีทำป้ายบทมุมจอเป็น MOV qtrle บน V4 `CHAPTER` และกับดัก ffmpeg ที่ต้องใส่ `-f image2` ไม่เช่นนั้นค้าง
- รวมการเปลี่ยนแปลงจาก commit ก่อนหน้า 430523d (กฎและ SOP ของ Katy404 Day 31: `katy404-minecraft-editing` และ `docs/channels/katy404.md`) ที่ยังไม่ได้ออก release ไว้ด้วย ไม่ใช่งานของรอบนี้

### Skill ที่อัปเดต
- `katy404-minecraft-editing` (แก้ไข): `SKILL.md`
- `resolve-video-enrichment` (แก้ไข): `SKILL.md`, `references/illustration-assets.md`

### ไฟล์ที่เปลี่ยน
- แก้ไข `.agents/skills/katy404-minecraft-editing/SKILL.md`
- แก้ไข `.agents/skills/resolve-video-enrichment/SKILL.md`
- แก้ไข `.agents/skills/resolve-video-enrichment/references/illustration-assets.md`
- แก้ไข `docs/OPERATING-NOTES.md`
- แก้ไข `docs/channels/katy404.md`
- แก้ไข `docs/channels/laffy.md`
- แก้ไข `docs/skills-manifest.json`

## v0.17.110 — export ทีละคลิป + เปิด Resolve/Drive กลับอัตโนมัติ — Armigon Shorts 2026-10 96 คลิป

### รายละเอียด
- `scripts/p2_export_final.py`: เพิ่ม `--chunk N` (ค่าเริ่มต้น 1) — render + verify ทีล่ะคลิป เขียน `jobs.json`/`done.jsonl` หลังแต่ละชุด แล้วรันใหม่เพื่อทำต่อได้; เพิ่ม `ensure_alive()` และ `_out_dir_ready()` เช็ค Resolve กับโฟลเดอร์ปลายทางก่อนทุกชุด ถ้าปิดให้เปิดกลับ (Resolve ผ่าน `resolve_recover.py` ซึ่งเปิด Google Drive เมื่อ library path หาย) แล้วทำต่อ ไม่หยุด batch; `LoadRenderPreset`/`SetRenderSettings`/`AddRenderJob` รีทได้; การ trim หาง GIF เฉพาะ p2 เปลี่ยนเป็นคำเตือน ไม่ abort
- `scripts/resolve_recover.py`: แก้ `GetName()` ที่ตอบ `None` หลัง relaunch ให้ re-fetch ด้วย `_name_of()`
- export Armigon Shorts 2026-10 ครบ 96 คลิปที่ `G:\My Drive\Projects\Armigon\2026-10\vdo` (48 แนวนอน 1920×1080 + 48 แนวตั้ง 1080×1920, 24 fps, H.264 + AAC, รวม 11.13 GB) คลิปแนวตั้งแนบปก 1 เฟรมแรก; `--verify` ผ่าน 96/96 และ ffprobe ยืนยันขนาด/เฟรมเรต/เสียงครบทุกไฟล์
- `docs/OPERATING-NOTES.md` บันทึกกฎใหม่ 5 ข้อ (export ทีละคลิป, เปิด app กลับเมื่อปิด, `Project.SaveProject` บน 21.1, `GetName()` หลัง relaunch, restart Resolve ทุก ~20 คลิป) และ `resolve-delivery` skill อัปเดตส่วน batch export
- หมายเหตุ: release นี้ยังรวมงานที่ยังไม่เคย release ของ session อื่น (skill `ponytail`, `ponytail-audit/debt/gain/help/review` และ `last30days`) ที่เข้ามาหลัง tag v0.17.109

### Skill ที่อัปเดต
- `last30days` (ใหม่): `.skillignore`, `SKILL.md`, `agents/openai.yaml`, `assets/aging-portrait.jpeg`, `assets/claude-code-rap.mp3`, `assets/dog-as-human.png`, `assets/dog-original.jpeg`, `assets/swimmom-mockup.jpeg`, `references/agent-mode.md`, `references/category-peers.md`, `references/comparison.md`, `references/competitors.md`, `references/discovery.md`, `references/followups.md`, `references/grok-bot-x.md`, `references/hiring-signals.md`, `references/library-queue.md`, `references/patent-signals.md`, `references/recommendations.md`, `references/reddit-session.md`, `references/research-runbook.md`, `references/runtime.md`, `references/save-html-brief.md`, `references/setup-wizard.md`, `references/synthesis.md`, `scripts/box_chrome_login.py`, `scripts/briefing.py`, `scripts/build-skill.sh`, `scripts/compare.sh`, `scripts/evaluate_search_quality.py`, `scripts/last30days.py`, `scripts/lib/__init__.py`, `scripts/lib/agentcookie.py`, `scripts/lib/amazon.py`, `scripts/lib/arxiv.py`, `scripts/lib/backends.py`, `scripts/lib/bird_x.py`, `scripts/lib/bluesky.py`, `scripts/lib/bounded_get.py`, `scripts/lib/brightdata.py`, `scripts/lib/categories.py`, `scripts/lib/chrome_cdp.py`, `scripts/lib/chrome_cookies.py`, `scripts/lib/cjk.py`, `scripts/lib/cluster.py`, `scripts/lib/cluster_diversity.py`, `scripts/lib/company_names.py`, `scripts/lib/company_resolve.py`, `scripts/lib/competitors.py`, `scripts/lib/cookie_extract.py`, `scripts/lib/cookie_paths.py`, `scripts/lib/corpus.py`, `scripts/lib/dates.py`, `scripts/lib/dedupe.py`, `scripts/lib/devto.py`, `scripts/lib/digg.py`, `scripts/lib/discovery_handoff.py`, `scripts/lib/doctor.py`, `scripts/lib/dripstack.py`, `scripts/lib/entity_extract.py`, `scripts/lib/env.py`, `scripts/lib/fanout.py`, `scripts/lib/feed.py`, `scripts/lib/fetch_memo.py`, `scripts/lib/freshness.py`, `scripts/lib/fusion.py`, `scripts/lib/github.py`, `scripts/lib/grok_audit.py`, `scripts/lib/grok_x.py`, `scripts/lib/grounding.py`, `scripts/lib/hackernews.py`, `scripts/lib/health.py`, `scripts/lib/hiring_signals.py`, `scripts/lib/hosted.py`, `scripts/lib/html_publish.py`, `scripts/lib/html_render.py`, `scripts/lib/http.py`, `scripts/lib/instagram.py`, `scripts/lib/job_boards/__init__.py`, `scripts/lib/job_boards/detect.py`, `scripts/lib/job_boards/google.py`, `scripts/lib/job_boards/ibm.py`, `scripts/lib/job_boards/jibe.py`, `scripts/lib/job_boards/kula.py`, `scripts/lib/job_boards/oracle.py`, `scripts/lib/job_boards/phenom.py`, `scripts/lib/job_boards/robots.py`, `scripts/lib/job_boards/sitemap.py`, `scripts/lib/job_boards/talentbrew.py`, `scripts/lib/job_boilerplate.py`, `scripts/lib/jobs.py`, `scripts/lib/jobs_digest.py`, `scripts/lib/jobs_story.py`, `scripts/lib/jobs_teams.py`, `scripts/lib/library.py`, `scripts/lib/library_index.py`, `scripts/lib/linkedin.py`, `scripts/lib/log.py`, `scripts/lib/meta_ads.py`, `scripts/lib/normalize.py`, `scripts/lib/parallel_mcp.py`, `scripts/lib/patent_digest.py`, `scripts/lib/patents.py`, `scripts/lib/permission_preflight.py`, `scripts/lib/perplexity.py`, `scripts/lib/pinterest.py`, `scripts/lib/pipeline.py`, `scripts/lib/planner.py`, `scripts/lib/polymarket.py`, `scripts/lib/preflight.py`, `scripts/lib/prescriptions.py`, `scripts/lib/private_files.py`, `scripts/lib/providers.py`, `scripts/lib/quality_nudge.py`, `scripts/lib/query.py`, `scripts/lib/reddit.py`, `scripts/lib/reddit_arctic.py`, `scripts/lib/reddit_discover.py`, `scripts/lib/reddit_enrich.py`, `scripts/lib/reddit_envelope.py`, `scripts/lib/reddit_health.py`, `scripts/lib/reddit_hydrate.py`, `scripts/lib/reddit_keyless.py`, `scripts/lib/reddit_listing.py`, `scripts/lib/reddit_public.py`, `scripts/lib/reddit_refs.py`, `scripts/lib/reddit_search.py`, `scripts/lib/reddit_session.py`, `scripts/lib/reddit_shreddit.py`, `scripts/lib/registers.py`, `scripts/lib/relevance.py`, `scripts/lib/render.py`, `scripts/lib/report_checklist.py`, `scripts/lib/rerank.py`, `scripts/lib/resolve.py`, `scripts/lib/safari_cookies.py`, `scripts/lib/schema.py`, `scripts/lib/setup_wizard.py`, `scripts/lib/signals.py`, `scripts/lib/skill_meta.py`, `scripts/lib/snippet.py`, `scripts/lib/sqlite_snapshot.py`, `scripts/lib/stocktwits.py`, `scripts/lib/subproc.py`, `scripts/lib/techmeme.py`, `scripts/lib/telegram.py`, `scripts/lib/threads.py`, `scripts/lib/tiktok.py`, `scripts/lib/topic_shape.py`, `scripts/lib/transcribe.py`, `scripts/lib/trustpilot.py`, `scripts/lib/truthsocial.py`, `scripts/lib/ui.py`, `scripts/lib/usage.py`, `scripts/lib/vendor/bird-search/LICENSE`, `scripts/lib/vendor/bird-search/bird-search.mjs`, `scripts/lib/vendor/bird-search/lib/cookies.js`, `scripts/lib/vendor/bird-search/lib/features.json`, `scripts/lib/vendor/bird-search/lib/paginate-cursor.js`, `scripts/lib/vendor/bird-search/lib/query-ids.json`, `scripts/lib/vendor/bird-search/lib/runtime-features.js`, `scripts/lib/vendor/bird-search/lib/runtime-query-ids.js`, `scripts/lib/vendor/bird-search/lib/twitter-client-base.js`, `scripts/lib/vendor/bird-search/lib/twitter-client-constants.js`, `scripts/lib/vendor/bird-search/lib/twitter-client-features.js`, `scripts/lib/vendor/bird-search/lib/twitter-client-search.js`, `scripts/lib/vendor/bird-search/lib/twitter-client-types.js`, `scripts/lib/vendor/bird-search/lib/twitter-client-utils.js`, `scripts/lib/vendor/bird-search/package.json`, `scripts/lib/web_fetch_keyless.py`, `scripts/lib/web_search_keyless.py`, `scripts/lib/windows_job.py`, `scripts/lib/x_api.py`, `scripts/lib/x_envelope.py`, `scripts/lib/x_judge.py`, `scripts/lib/xai_x.py`, `scripts/lib/xiaohongshu_api.py`, `scripts/lib/xquik.py`, `scripts/lib/xurl_x.py`, `scripts/lib/yahoo_finance.py`, `scripts/lib/youtube_yt.py`, `scripts/reddit_canary.py`, `scripts/setup-keychain.sh`, `scripts/setup-pass.sh`, `scripts/store.py`, `scripts/test-v1-vs-v2.sh`, `scripts/test_device_auth.py`, `scripts/verify_v3.py`, `scripts/watchlist.py`, `scripts/x_lane_parity.py`
- `ponytail` (ใหม่): `SKILL.md`
- `ponytail-audit` (ใหม่): `SKILL.md`
- `ponytail-debt` (ใหม่): `SKILL.md`
- `ponytail-gain` (ใหม่): `SKILL.md`
- `ponytail-help` (ใหม่): `SKILL.md`
- `ponytail-review` (ใหม่): `SKILL.md`
- `resolve-delivery` (แก้ไข): `SKILL.md`

### ไฟล์ที่เปลี่ยน
- เพิ่ม `.agents/skills/last30days/.skillignore`
- เพิ่ม `.agents/skills/last30days/SKILL.md`
- เพิ่ม `.agents/skills/last30days/agents/openai.yaml`
- เพิ่ม `.agents/skills/last30days/assets/aging-portrait.jpeg`
- เพิ่ม `.agents/skills/last30days/assets/claude-code-rap.mp3`
- เพิ่ม `.agents/skills/last30days/assets/dog-as-human.png`
- เพิ่ม `.agents/skills/last30days/assets/dog-original.jpeg`
- เพิ่ม `.agents/skills/last30days/assets/swimmom-mockup.jpeg`
- เพิ่ม `.agents/skills/last30days/references/agent-mode.md`
- เพิ่ม `.agents/skills/last30days/references/category-peers.md`
- เพิ่ม `.agents/skills/last30days/references/comparison.md`
- เพิ่ม `.agents/skills/last30days/references/competitors.md`
- เพิ่ม `.agents/skills/last30days/references/discovery.md`
- เพิ่ม `.agents/skills/last30days/references/followups.md`
- เพิ่ม `.agents/skills/last30days/references/grok-bot-x.md`
- เพิ่ม `.agents/skills/last30days/references/hiring-signals.md`
- เพิ่ม `.agents/skills/last30days/references/library-queue.md`
- เพิ่ม `.agents/skills/last30days/references/patent-signals.md`
- เพิ่ม `.agents/skills/last30days/references/recommendations.md`
- เพิ่ม `.agents/skills/last30days/references/reddit-session.md`
- เพิ่ม `.agents/skills/last30days/references/research-runbook.md`
- เพิ่ม `.agents/skills/last30days/references/runtime.md`
- เพิ่ม `.agents/skills/last30days/references/save-html-brief.md`
- เพิ่ม `.agents/skills/last30days/references/setup-wizard.md`
- เพิ่ม `.agents/skills/last30days/references/synthesis.md`
- เพิ่ม `.agents/skills/last30days/scripts/box_chrome_login.py`
- เพิ่ม `.agents/skills/last30days/scripts/briefing.py`
- เพิ่ม `.agents/skills/last30days/scripts/build-skill.sh`
- เพิ่ม `.agents/skills/last30days/scripts/compare.sh`
- เพิ่ม `.agents/skills/last30days/scripts/evaluate_search_quality.py`
- เพิ่ม `.agents/skills/last30days/scripts/last30days.py`
- เพิ่ม `.agents/skills/last30days/scripts/lib/__init__.py`
- เพิ่ม `.agents/skills/last30days/scripts/lib/agentcookie.py`
- เพิ่ม `.agents/skills/last30days/scripts/lib/amazon.py`
- เพิ่ม `.agents/skills/last30days/scripts/lib/arxiv.py`
- เพิ่ม `.agents/skills/last30days/scripts/lib/backends.py`
- เพิ่ม `.agents/skills/last30days/scripts/lib/bird_x.py`
- เพิ่ม `.agents/skills/last30days/scripts/lib/bluesky.py`
- เพิ่ม `.agents/skills/last30days/scripts/lib/bounded_get.py`
- เพิ่ม `.agents/skills/last30days/scripts/lib/brightdata.py`
- ... และอีก 163 ไฟล์ (ดู `git diff --name-status` ของ tag นี้)

## v0.17.109 — เพิ่ม skill davinci-resolve-api และสร้างโปรเจกต์ Resolve ผ่าน MCP ได้โดยไม่มี dialog

### รายละเอียด
- เพิ่ม skill ใหม่ `davinci-resolve-api` (`.agents/skills/davinci-resolve-api/SKILL.md`) — รวบรวมเอกสาร DaVinci Resolve scripting API ไว้ใน repo เพื่อให้อ้างอิง method ได้โดยไม่ต้องเดินไปอ่าน gist ภายนอก
- `project-learning` 0.3.0: เพิ่มหัวข้อ "Fast Resolve iteration" (ไม่รัน pytest ในลูป run-inspect-fix บนไทม์ไลน์จริง แต่ยังคง .drp backup/preserved_state และห้ามเขียน master timeline) และเปลี่ยนขั้นตอนจบงานเป็น refresh manifest ก่อน แล้วรัน bundle check + test ที่กระทบ พร้อมรัน full suite ก่อนออก release
- `resolve-smart-edit` 0.1.0: เขียนใหม่สำหรับ Resolve 21 เป็น MCP-first (prerequisites, quick reference, procedure, execution recipes) แทนเอกสาร pipeline เดิม
- `AGENTS.md`: ผ่อนกฎ "บังคับ release หลังทุก task" และปรับคำแนะนำ pytest ให้สอดคล้องกับ skill (ไม่ต้องรันใน live loop แต่รันก่อน release)
- `resolve-mcp` 0.5.0: บันทึกเส้นทาง project lifecycle ว่า `project_manager create` รับ `name` + `media_location_path` (Resolve 20.2.2+) สร้างโปรเจกต์ได้จริงโดยไม่มี modal ขณะที่ `project_settings set_name` คืน `False` บน 21.1.0.17 และห้ามใช้ dialog Save Current Project เพราะเป็น GUI step ที่ read-back ไม่ได้
- `.mcp.json`: ชี้ `davinci-resolve-mcp` ไปที่ `C:\Users\warit\Desktop\davinci-resolve-mcp` (แก้ `command` และ `args[0]` เท่านั้น คง `env` เดิม)
- บันทึก job artifact ของ Laffy introduction 2 ไฟล์ log ไว้ใน `work/laffy-introduction/intake/`
- ตรวจสอบจริงบนเครื่องนี้: `project_manager create` สร้างโปรเจกต์ `Agent Editing` (media location `C:\Users\warit\DaVinci Resolve Media`) โดยไม่มี dialog และ read-back `get_name` ได้ `Agent Editing`; `project_settings set_name` ล้มเหลงตามที่ระบุ; `py -m pytest -q` ผ่านทั้งชุด 460 passed, 35 skipped
- ยังไม่ได้ commit stills 3 ไฟล์ใน `work/laffy-introduction/intake/` (`pilot-1s.jpg`, `source-8s.jpg`, `source-sheet.jpg`) ตามกฎ repo ที่ห้าม staging stills/footage

### Skill ที่อัปเดต
- `davinci-resolve-api` (ใหม่): `SKILL.md`
- `project-learning` (แก้ไข): `SKILL.md`
- `resolve-mcp` (แก้ไข): `SKILL.md`
- `resolve-smart-edit` (แก้ไข): `SKILL.md`

### ไฟล์ที่เปลี่ยน
- เพิ่ม `.agents/skills/davinci-resolve-api/SKILL.md`
- แก้ไข `.agents/skills/project-learning/SKILL.md`
- แก้ไข `.agents/skills/resolve-mcp/SKILL.md`
- แก้ไข `.agents/skills/resolve-smart-edit/SKILL.md`
- แก้ไข `.mcp.json`
- แก้ไข `AGENTS.md`
- แก้ไข `docs/skills-manifest.json`
- แก้ไข `docs/validation-report.json`
- เพิ่ม `work/laffy-introduction/intake/caption-prep.log`
- เพิ่ม `work/laffy-introduction/intake/source-audio-analysis.log`

## v0.17.108 — เพิ่มสกิล katy404-minecraft-editing และบันทึก Operating Notes จาก Day 30

### รายละเอียด
- เพิ่มสกิลใหม่ `katy404-minecraft-editing` บันทึกเวิร์กโฟลว์การตัดต่อคลิปซีรีส์ Minecraft ของ Katy404 ("ปลูกข้าวจนกว่าจะ 10K") ครอบคลุมทั้ง 16:9 Clean Master และ 9:16 Shorts/TikTok
- บันทึกการแก้กับดักทางเทคนิค 6 ข้อใน `docs/OPERATING-NOTES.md`: การตัดหัวใน DRT XML ด้วย `<In>offset</In>`, การแพตช์ Subtitle Preset ผ่าน DRT โดยไม่ต้องปิด Resolve, ค่าคงที่ `r.EXPORT_DRT`/`r.EXPORT_NONE`, การหา `find_user_db` จาก Library root, มาตรฐาน Loudness -13 ถึง -14 LUFS, และการสำรอง .drp อย่างปลอดภัย
- อัปเดต `.agents/skills/house-style/SKILL.md` (v0.3.9) เพิ่มเกณฑ์สไตล์ Katy404 Minecraft: ตัดหัวเมนู 168 เฟรม, งด Title Card และสติกเกอร์ Chibi รกๆ เพื่อโฟกัสปฏิกิริยาตัวละคร, และสเปกเลย์เอาต์แนวตั้ง 9:16
- ตรวจสอบความถูกต้องผ่าน `scripts/refresh_skill_manifest.py` และชุดทดสอบ `pytest` ทั้งหมด 460 ข้อผ่าน 100%

### Skill ที่อัปเดต
- `house-style` (แก้ไข): `SKILL.md`
- `katy404-minecraft-editing` (ใหม่): `SKILL.md`

### ไฟล์ที่เปลี่ยน
- แก้ไข `.agents/skills/house-style/SKILL.md`
- เพิ่ม `.agents/skills/katy404-minecraft-editing/SKILL.md`
- แก้ไข `docs/OPERATING-NOTES.md`
- แก้ไข `docs/skills-manifest.json`
- แก้ไข `docs/validation-report.json`

## v0.17.107 — Katy404 Day 30 เวอร์ชันแนวตั้ง 9:16 (Shorts/TikTok)

### รายละเอียด
- สร้างไทม์ไลน์แนวตั้ง `Timeline 1_9x16` (1080x1920 @ 60fps, 5,846 เฟรม / 97.433 วิ) สำหรับ Katy404 Minecraft Day 30 ใน DaVinci Resolve Studio ผ่านสคริปต์ `scripts/build_9x16_day30.py`
- จัดวาง Track Architecture สไตล์ 9:16:
- Video 1 (`Game Top`): สเกล 2.03x แถว 0..960 px โฟกัสเกมเพลย์ตรงกลางจอ ไร้ขอบดำ
- Video 2 (`REACTIONS`): แทร็กเปล่าสำรองสำหรับ overlay ปฏิกิริยา
- Video 3 (`VTuber Bottom`): สเกล 3.56x แถว 960..1920 px โฟกัสตัวละคร Katy404 เว้น Headroom ~6-7% เหนือจงอยผม
- Video 4 (`VTuber Full`): สเกล 4.27x ซูมโคลสอัปเต็มจอสำหรับช่วง Focus Zoom ทั้ง 6 จุด ([545..803], [1217..1601], [2081..2441], [3671..4032], [4962..5102], [5422..5755])
- Subtitle 1: 45 cues นำเข้า Preset `Mitr-short-001` (144 bytes จาก User.db ผ่าน `patch_drt`) ลอยตำแหน่งอก/คอ ไม่ทับหน้าตัวละคร
- Audio 1-3: เสียงพูด Dialogue, SFX 15 จุด และ BGM `Melody Island` (-19 dB) คงที่เท่า Master 16:9 100%
- ตรวจสอบภาพ Still Frame จาก Resolve 7 ช่วง (`still_100.png` ถึง `still_5600.png`) ผ่านเกณฑ์ไม่มีขอบดำ และสัดส่วนตัวละครถูกต้อง
- เรนเดอร์ไฟล์ส่งมอบ `วันที่ 30_9x16_test_2026-11-17.mp4` (668,132,511 ไบต์) ไว้ใน Google Drive
- ผลการตรวจเช็คคุณภาพ (QC):
- ffprobe: 1080x1920 @ 60fps H.264, ความยาว 97.433s, AAC 48kHz Stereo
- EBU R128: Integrated Loudness -13.2 LUFS, LRA 2.2 LU (ได้มาตรฐานวิดีโอโซเชียล -13 ถึง -14 LUFS)
- Subtitle Burn-In: ฟอนต์ Mitr-short-001 ติดลงในวิดีโอชัดเจน สีขาวขอบดำ ตำแหน่งกลางจอระดับอก/รอยต่อเกม
- สร้างชุดทดสอบยูนิต `tests/test_build_9x16_day30.py` ผ่าน 3/3 ข้อ และผ่าน test suite รวม 12/12 ข้อ

### Skill ที่อัปเดต
- ไม่มี

### ไฟล์ที่เปลี่ยน
- แก้ไข `docs/channels/katy404.md`
- แก้ไข `docs/skills-manifest.json`
- แก้ไข `docs/validation-report.json`
- แก้ไข `scripts/INDEX.md`
- เพิ่ม `scripts/build_9x16_day30.py`
- เพิ่ม `tests/test_build_9x16_day30.py`

## v0.17.106 — Katy404 Day 30 โหลด Subtitle Preset แนวนอน และ Promote Timeline 1

### รายละเอียด
- นำเข้า Subtitle preset `Mitr Font` แนวนอน (134 ไบต์จาก User.db) ลงบน Subtitle track ของคลิปแนวนอน Katy404 Day 30 ตรวจสอบ already_matches=True 100%
- Promote งานตัดต่อ Clean เข้าสู่ Timeline หลัก `Timeline 1` (1920x1080 @ 60 fps, 5846 เฟรม, 97.43 วินาที)
- ลบ Timeline สำรองทั้งหมด (`Timeline 1_enriched`, `Timeline 1_clean`, `__old_t1_to_delete`) ออกจากโปรเจกต์ คงเหลือ `Timeline 1` เป็นไทม์ไลน์หลักเพียงหนึ่งเดียวตามคำสั่งผู้ใช้
- บันทึกสำรอง Project Archive (.drp) ก่อนลบไว้ที่ `exports/_backups/katy404_day30_pre_promote_clean_20261117_212607.drp` (158,391 ไบต์) ปลอดภัย 100%

### Skill ที่อัปเดต
- ไม่มี

### ไฟล์ที่เปลี่ยน
- แก้ไข `docs/channels/katy404.md`
- แก้ไข `docs/skills-manifest.json`

## v0.17.105 — ตัดต่อ Katy404 Minecraft Day 30 สไตล์ Clean แนวนอน 16:9

### รายละเอียด
- สร้าง `Timeline 1_clean` (1920x1080 @ 60 fps, 5846 เฟรม, 97.43 วินาที) สำหรับโปรเจกต์ "วันที่ 30 ปลูกข้าวจนกว่าจะ 10K ผู้ติดตาม - Katy404" ตามสไตล์ Clean แบบเดียวกับวันที่ 29
- ตัดช่วงหัว 0–2.8 วินาทีแรก (หน้าจอเมนูเกมและช่วงนับ 1 2 3 รวม 168 เฟรม) ออกจาก Video 1 และ Audio 1 ด้วย In=168 เปิดคลิปมาทักทาย "สวัสดีทุกคน..." ทันที
- ตัดป้าย Title Card และสติกเกอร์การ์ตูน Chibi ออกทั้งหมดเพื่อความสะอาดตา ให้เห็นเกมและตัวละครเต็มอิ่ม
- วางแทร็ก Subtitle 1 ภาษาไทย 45 คิว สไตล์ฟอนต์ `Mitr Bold` สีขาวขอบดำ กึ่งกลางล่าง กระชับ ≤14 ตัวอักษร ไม่บังตัวละคร
- ปรับแต่งแทร็ก Video 2 `VTuber Zoom` 6 จุดสำคัญด้วย Adjustment Clip ซูม 1.35x ตรึงมุมขวาล่าง ไร้ขอบดำ 100%
- เพิ่มแทร็ก Audio 2 `SFX` 15 จุด (เสียง Whoosh -10 dB ซูมเข้า/ออก 12 จุด + เสียง Pop -9 dB เน้นคำ 3 จุด) และ Audio 3 `BGM` (เพลง Melody Island -19 dB ตลอดคลิป)
- เรนเดอร์ไฟล์ส่งมอบ `วันที่ 30_CLEAN_2026-11-17.mp4` ขนาด 634,228,643 ไบต์ ไปยัง Google Drive ตรวจสอบผ่าน ffprobe (1080p60 H.264/AAC), ความดัง -13.2 LUFS (มาตรฐาน YouTube) และภาพนิ่ง burn-in ซับไตเติลชัดเจนทุกจุด

### Skill ที่อัปเดต
- ไม่มี

### ไฟล์ที่เปลี่ยน
- แก้ไข `docs/channels/katy404.md`
- แก้ไข `docs/skills-manifest.json`
- แก้ไข `docs/validation-report.json`

## v0.17.104 — เพิ่ม skill vtuber-cover-source-video (ทำปกจากไฟล์วิดีโอ พื้นหลังไม่มีตัวละคร)

### รายละเอียด
- เพิ่ม skill ใหม่ `vtuber-cover-source-video` (`.agents/skills/vtuber-cover-source-video/`) รวม workflow การทำปกจากไฟล์วิดีโอที่ผ่านมาในรอบนี้: แยก layout ต้นทางด้วยความสว่าง, สแกนหยาบ 10 วิ + สแกน fine 3 วิ, วัด bbox ของตัวละครบนเฟรมจริงที่ extract, ตัดช่องห้อง L|R, ประกอบปก, QC สองชั้น และส่งมอบพร้อม manifest
- มีสคริปต์จริง `scripts/character_free_bg.py` (คำสั่ง `scan` หาเฟรมที่ห่างกันกว้างสุด และ `crop --side L|R|LR` ตัดช่องที่ไม่มีตัวละคร) ทดสอบกับสตรีม Aomi-mama 2026-10 จริง: `crop --frame 33162 --side LR` ได้ 481x720 px และ hair=0 px; `scan --around-frame 31272` ได้เฟรม 33162 เป็นอันดับแรก (both=581) ตรงกับที่ส่งมอบ
- บันทึกกับดักที่เจอจริงไว้ใน skill: `fps=1/10` กับ `ffmpeg -ss` เจอเฟรมคนละอัน (bbox ต่างกันถึง 600 px), hair mask false positive จากสีน้ำเงินในเกม/ในห้อง, อวาตาร์จอเล็กมุมขวาล่างหลุดเข้า crop, เฟรมเปิด/ปิดสตรีมมักมีภาพประกอบตัวละคร, และฉากที่ซูมจะนุ่ม
- คัดลอก skill ไปยัง skill directory ของ profile เพื่อให้ `skill_view`/`skills_list` เห็น (skill_manage เขียนไปที่ profile และ repo rule คือ skill ต้องอยู่ใน `.agents/skills/`)
- รัน `python -m pytest -q` ผ่านทั้งชุด: 457 passed, 35 skipped และ `refresh_skill_manifest.py` แล้ว

### Skill ที่อัปเดต
- `vtuber-cover-source-video` (ใหม่): `SKILL.md`, `scripts/character_free_bg.py`

### ไฟล์ที่เปลี่ยน
- เพิ่ม `.agents/skills/vtuber-cover-source-video/SKILL.md`
- เพิ่ม `.agents/skills/vtuber-cover-source-video/scripts/character_free_bg.py`
- แก้ไข `docs/skills-manifest.json`

## v0.17.103 — รีแชม skill manifest หลัง release + บันทึกกับดัก checksum ล้าสมัย

### รายละเอียด
- เพิ่มบทเรียนใน `docs/OPERATING-NOTES.md` (หัวข้อ Release manifest drift): `scripts/release.py --publish` แก้และ commit `VERSION` + `CHANGELOG.md` หลังที่ manifest ถูก refresh ไปแล้ว ทำให้ `tests/test_skill_bundle.py` แดงเพราะ checksum ของไฟล์สองตัวนั้นล้าสมัย — ต้องรัน `python scripts/refresh_skill_manifest.py` แล้ว commit `docs/skills-manifest.json` ก่อนรันทดสอบครั้งต่อไป
- รีแชม `docs/skills-manifest.json` ให้ตรงไฟล์จริง (`CHANGELOG.md`, `VERSION`, `docs/OPERATING-NOTES.md`) หลังปิด release v0.17.102
- รัน `python -m pytest -q` ผ่านทั้งชุด: 457 passed, 35 skipped

### Skill ที่อัปเดต
- ไม่มี

### ไฟล์ที่เปลี่ยน
- แก้ไข `docs/OPERATING-NOTES.md`
- แก้ไข `docs/skills-manifest.json`

## v0.17.102 — ปก Aomi-mama 2026-10 v3 — มีโมเดลทับทุกใบ + พื้นหลังไม่มีตัวละคร

### รายละเอียด
- ปก Aomi-mama 2026-10 ชุด v3 ครบ 12 ใบ (แนวนอน 1920x1080 + แนวตั้ง 1080x1920) ตามฟีดแบ็กผู้ใช้ "แก้ไขปกคลิปทั้งหมดใหม่ เนื่องจากมีบางปกคลิปไม่มีรูปตัวละคร และมีการเลือกพื้นหลังแล้วมีรูปตัวละคร พื้นหลังรบกวนเลือกแบบไม่มีตัวละครเท่านั้น เพราะเรานำรูปตัวละครมาใส่แทนแล้ว" — ทุกปกอวาตาร์ใน stream ถูกแทนด้วยโมเดล `1.picture` ทับ และพื้นหลังทุกใบไม่มีตัวละคร; ส่งครบ 12 ไฟล์ชื่อ `<timeline>.jpg` + `manifest.json` ไป Drive `Projects/Aomi-mama/2026-10/covers/` (v2 เก็บไว้ `covers/v2/` ก่อนแทน) แล้ว verify ปลายทาง 12/12 ผ่าน
- คลิปห้องนอน (กิน, เสื้อผ้า, ยุง, ซิม): อวาตาร์ใน stream อยู่กลางจอตลอดไม่มีเฟรมว่าง จึงตัดช่องห้องซ้าย+ขวาของอวาตาร์จากเฟรมเดียวกันแล้วต่อกัน (L|R) เลือกเฟรมที่ห่างกันกว้างที่สุดด้วย `scripts/scratch/aomimama_2026_10/find_strip.py` (สแกน 3 วิ รอบ evidence frame ครั้งละ 120 วิ) ได้ฉาก 481-517 px จากเฟรม 1280 px blur 2 ทั้งสองสัดส่วน; ตรวจฉากหลัง hair=0 px, skin 34-52 px (มาจากเฟรมห้อง ไม่ใช่ตัวละคร)
- คลิปหน้าคอมเมนต์ (เกมฟรี, บอส): crop แนวนอนเดิม x<1060 ยังโผล่ครึ่งซ้ายของอวาตาร์จอเล็ก (ขอบซ้ายจริง ~x=960 ใน `เกมฟรี` และ ~x=1000 ใน `บอส`) จึงแคบลงเป็น x<910; แนวตั้ง (60,0,465) ไม่มีอวาตาร์ เก็บเดิม
- บันทึกบั๊กเชิงกริด: การสแกนด้วย `fps=1/10` ไปเจอเฟรมคนละอันกับ `ffmpeg -ss` (bbox ผมต่างกันถึง 600 px) ทำให้ขอบห้องที่คำนวณไว้ผิด; ต้องวัด bbox บนเฟรมจริงที่ extract ก่อนตัด crop
- QC สองชั้น: ตัวเลข 12/12 (ขนาด, hook แดง `#EC1C24`, ข้อความขาว) และ `vision_analyze` 12/12 ยืนยันไม่มีตัวละครในฉากหลัง ฉากห้องอ่านออก (ทีวี/เตียง/หน้าต่าง); contact sheet `.hermes/projects/aomimama-2026-10/covers/v3/sheet_v3.html`
- อัปเดต `docs/channels/aomimama.md` (ประวัติ v3 + วิธีหาเฟรม/เหตุผลที่ต้องวัด bbox ใหม่) และ skill `vtuber-cover-batch-pipeline` (เพิ่มกับดัก: วัดขอบอวาตาร์บนเฟรมจริง และเมื่อไม่มีเฟรมว่างให้ใช้ช่องห้อง L|R)
- ยังไม่ได้ตรวจ: ฉากหลังห้องนอน v3 ยังซูมประมาณ 3.7-4 เท่าแนวนอน ดูใกล้จึงนุ่ม รอผู้ใช้ตัดสินว่าใช้ดีหรือต้องการฉากคมกว่านี้

### Skill ที่อัปเดต
- `vtuber-cover-batch-pipeline` (แก้ไข): `SKILL.md`

### ไฟล์ที่เปลี่ยน
- แก้ไข `.agents/skills/vtuber-cover-batch-pipeline/SKILL.md`
- แก้ไข `docs/channels/aomimama.md`
- แก้ไข `docs/skills-manifest.json`

## v0.17.101 — ปก Aomi-mama 2026-10 v2 ครบ 12 ใบ + แก้ปก กินง่าย ตามฟีดแบ็ก + บทเรียน CSS/QC

### รายละเอียด
- ทำปกคลิป Aomi-mama 2026-10 ใหม่ทั้งชุด 12 ใบ (แนวนอน 1920x1080 + แนวตั้ง 1080x1920) ด้วยดีไซน์ `scene` ที่ผู้ใช้เลือกจากตัวอย่าง 8 ใบ — ส่งครบทั้ง 12 ไฟล์ชื่อ `<timeline>.jpg` + `manifest.json` ใหม่ไปที่ Drive `Projects/Aomi-mama/2026-10/covers/` แล้วตรวจไฟล์ปลายทางครบ (ปก v1 เก็บไว้ `covers/v1/`)
- ผู้ใช้ตรวจปกที่ส่งแล้ว 2 ใบ (คลิป `กินง่าย`, ทั้ง 1920x1080 และ 1080x1920) แล้วสั่งแก้ "ไม่มีรูปตัวละคร, พื้นหลัง blur เกินไป" — เพิ่มโมเดลอวาตาร์ `vts_avatar_06` ทับ (ตามที่ผู้ใช้เลือก) และลด blur 14/10 → 6/5 ด้วยกลไก `force_avatar`/`blur` รายคลิปใน `covers_v2.py`; ส่งแทนที่ 2 ไฟล์ใน Drive + manifest 2 บรรทัดแล้ว verify ผ่านครบ (hair 290,190/446,477 px, bg-edge sharper ทั้งคู่, red/white px ครบ) ด้วย `scripts/scratch/aomimama_2026_10/fix_kin.py`
- แก้บั๊กจริงในสคริปต์ทำปก: CSS ที่สร้าง rule `av{...}` ขาดจุด`.` ทำให้อวาตาร์ไม่ถูกจัดตำแหน่งและถูกฉากหลังทับ (position static ที่ 0,0) และ glow มี `}}` เกิน + ไม่มี `<div class="glow">` ใน body — แก้แล้ว re-render อ่านค่า bbox โมเดล (826,70 1214x1010) และจำนวน像素ผม 4091 -> 53331 ยืนยันว่า overlay แสดงจริง
- QC ทั้งชุด 12 ใบผ่านด้วยตัวเลข: ขนาดถูกต้อง, hook แดง `#EC1C24` และข้อความขาวมี像素ครบ, bbox ข้อความอยู่ในขอบ, timestamp ไฟล์ต่างกัน (mtime ใหม่ทุกใบ)
- บันทึกบทเรียน 2 แถวใน `docs/OPERATING-NOTES.md`: (1) CSS ที่สร้างจาก string ต้อง assert จุด `.` นำหน้า (2) ห้ามใช้ผลคืนของ image-read/screenshot เป็นหลักฐานเดียวเมื่อค่าที่คืนไม่ตรงไฟล์ ให้ QC ด้วย pixel mask/DOM/diff/timestamp แทน
- อัปเดต `docs/channels/aomimama.md`: ประวัติปก v2 ปี 2026-11-17 (ดีไซน์ที่ผู้ใช้เลือก, blur 8-26 + brightness 0.70-0.88 แทน v1 ที่ดำสนิท, สคริปต์และปลายทางส่งมอบ)
- skill `vtuber-thumbnail-qc` (0.1.1): เพิ่มกับดัก QC สำรองเชิงตัวเลขเมื่อ image-viewing ใช้ไม่ได้หรือผลไม่น่าเชื่อถือ
- รัน `python -m pytest -q` ผ่านทั้งชุด (456 passed รอบล่าสุด รวม `test_channel_profiles` ที่แก้ชื่อสคริปต์ใน profile แล้ว) และ `python scripts/refresh_skill_manifest.py` แล้ว
- ยังไม่ได้ตรวจสอบในรอบนี้: การ restart session ให้ MCP reload เป็น 5.3.1 (ยังไม่ได้ทำ)

### Skill ที่อัปเดต
- `house-style` (แก้ไข): `SKILL.md`
- `resolve-audio` (แก้ไข): `SKILL.md`
- `talking-avatar-vertical-copy` (แก้ไข): `SKILL.md`
- `vtuber-thumbnail-qc` (แก้ไข): `SKILL.md`

### ไฟล์ที่เปลี่ยน
- แก้ไข `.agents/skills/house-style/SKILL.md`
- แก้ไข `.agents/skills/resolve-audio/SKILL.md`
- แก้ไข `.agents/skills/talking-avatar-vertical-copy/SKILL.md`
- แก้ไข `.agents/skills/vtuber-thumbnail-qc/SKILL.md`
- แก้ไข `docs/OPERATING-NOTES.md`
- แก้ไข `docs/channels/aomimama.md`
- แก้ไข `docs/channels/katy404.md`
- แก้ไข `docs/channels/laffy.md`
- แก้ไข `docs/skills-manifest.json`
- แก้ไข `docs/validation-report.json`
- แก้ไข `scripts/INDEX.md`
- แก้ไข `scripts/backup_drp.py`
- เพิ่ม `scripts/build_9x16_day29.py`
- แก้ไข `scripts/p2_export_final.py`
- แก้ไข `scripts/rebuild_trimmed_zoom_clip.py`
- เพิ่ม `scripts/set_dialogue_leveler.py`
- เพิ่ม `tests/test_build_9x16_day29.py`
- เพิ่ม `tests/test_set_dialogue_leveler.py`

## v0.17.100 — แปลง 9:16 วันที่ 29 Katy404

### รายละเอียด
- สร้าง `Timeline 1_9x16` (1080x1920 @ 60 fps) จาก Timeline 1 แนวนอนของโปรเจกต์ "วันที่ 29 ปลูกข้าวจนกว่าจะ 10K ผู้ติดตาม - Katy404"
- จัด layout แนวตั้งแบบซ้อน (Stacked Layout): V1 "Game Top" (ครึ่งบน 0..960 px), V2 "REACTIONS" (ว่างไว้สำหรับใส่ GIF/overlay ภายหลัง), V3 "VTuber Bottom" (ครึ่งล่าง 960..1920 px ขยายอวาตาร์ Katy404 ชัดเจนเว้น headroom พอดี)
- ปรับช่วง VTuber Zoom เดิม 2 ช่วง ([240, 630) และ [1488, 1998)) ไปไว้ที่ V4 "VTuber Full" ขยายโคลสอัปเต็มจอในจังหวะโฟกัสตามสไตล์ของช่อง
- ตรวจสอบ protected tracks: เสียง A1 (Dialogue), A2 (SFX 4 จุด), A3 (BGM) และช่วง V1 ต้นฉบับตรงกับต้นฉบับ 100%
- ตรวจสอบภาพนิ่ง Export Still จาก DaVinci Resolve ทั้งหมด 5 เฟรม (เฟรม 100, 400, 1000, 1700, 2500) ยืนยันขนาด 1080x1920 ไม่มีขอบดำ ภาพเกมและอวาตาร์ชัดเจน

### Skill ที่อัปเดต
- ไม่มี

### ไฟล์ที่เปลี่ยน
- แก้ไข `docs/channels/katy404.md`
- แก้ไข `docs/skills-manifest.json`
- แก้ไข `docs/validation-report.json`
- แก้ไข `scripts/INDEX.md`
- เพิ่ม `scripts/build_9x16_day29.py`
- เพิ่ม `tests/test_build_9x16_day29.py`

## v0.17.99 — Export Katy404 2026-10-1 ครบ 134 คลิป (แนวนอน 67 + แนวตั้งพร้อมปก 67)

### รายละเอียด
- Render ส่งมอบคลิปไฮไลต์โปรเจกต์ `KT404 Highlights 2026-10-1` ครบ 134 ไฟล์ `.mov` (H.264/AAC 24 fps, preset `H.264 Master`, ซับไทยฝังในภาพ burn-in) ไปที่ `G:\My Drive\Projects\Katy404\2026-10-1\vdo`: แนวนอน 67 ไฟล์ (1920x1080) ไม่ใส่ปก และแนวตั้ง 67 ไฟล์ (1080x1920) พร้อมแทรกปกคลิป (`.jpg`) ที่เฟรมแรก (frame 0) 1 เฟรม
- ตรวจสอบคุณภาพผ่านครบ 134/134 PASS: ffprobe ยืนยันขนาดภาพ, framerate 24 fps, audio stream, ซับไตเติล burn-in ทุกไฟล์ และตรวจ SSIM เฟรม 0 ของแนวตั้งเทียบภาพปก ≥ 0.90 ครบถ้วน
- ไม่แตะต้อง Timeline ต้นฉบับ: ใช้โครงสร้างสำเนาชั่วคราว `__cover_tmp` ในการแทรกปกและเรนเดอร์ พร้อมลบออกอัตโนมัติ Media Pool สะอาดคงเหลือ 134 timeline หลัก
- ปรับปรุง `scripts/p2_export_final.py`: เพิ่ม directory caching ป้องกันการสแกน I/O ซ้ำบน Google Drive, ปรับ auto-resume render queue ให้ทำงานต่อเนื่องเมื่อคิวหยุดชั่วคราว, และเพิ่ม defensive error handling เมื่อ reference โปรเจกต์หลุด
- ปรับปรุง `scripts/backup_drp.py`: รองรับพฤติกรรม Resolve 21 ที่ `pm.SaveProject()` คืนค่า `None` เมื่อโปรเจกต์ไม่มีการเปลี่ยนแปลงที่ยังไม่ได้บันทึก
- บันทึกผลการส่งมอบและสถานะใน `docs/channels/katy404.md`

### Skill ที่อัปเดต
- ไม่มี

### ไฟล์ที่เปลี่ยน
- แก้ไข `docs/OPERATING-NOTES.md`
- แก้ไข `docs/channels/katy404.md`
- แก้ไข `docs/skills-manifest.json`
- แก้ไข `scripts/backup_drp.py`
- แก้ไข `scripts/p2_export_final.py`

## v0.17.98 — Katy404 วันที่ 28 ลบ Timeline สำรอง

### รายละเอียด
- Katy404 วันที่ 28: ตามคำสั่ง "อัปเดต Timeline หลัก และลบ Timeline สำรอง" — `Timeline 1` เป็นงานล่าสุดอยู่แล้ว (อ่านกลับตรงกับที่ผู้ใช้ตัด) จึงคงไว้เป็น Timeline หลัก; ลบ `Timeline 1_original` และ `Timeline 1_pre_zoomfix` ด้วย unique ID หลังสำรอง `pre_delete_timelines.drp` (152,374 bytes); `Timeline 1` และ `Timeline 1_9x16` อ่านกลับไม่เปลี่ยน โปรเจกต์เหลือ 2 timeline

### Skill ที่อัปเดต
- ไม่มี

### ไฟล์ที่เปลี่ยน
- แก้ไข `docs/channels/katy404.md`
- แก้ไข `docs/skills-manifest.json`

## v0.17.97 — Katy404 วันที่ 28 FINAL + 9:16

### รายละเอียด
- Katy404 วันที่ 28 FINAL 16:9: ระหว่าง render ผู้ใช้ตัดหัว 6.3 วิ (เมนูหยุดเกม + นับ 1-2-3) ออกจาก `Timeline 1` เหลือ 5785 เฟรม; คลิปซูมแรกที่ถูกตัดหัวทำ render ล้ม ("Fusion composition at 00:00:06:12") จึงสร้าง track `VTuber Zoom` ใหม่ผ่าน DRT ตามช่วงของผู้ใช้ทุกช่วง แล้ว import เป็น `Timeline 1` ใหม่ (track อื่นตรงกับที่ผู้ใช้ตัดทุกชิ้น, Dialogue Leveler ยังอยู่, คืน BGM fade-in 12 เฟรมที่หายไปกับการตัด); ไฟล์ `วันที่ 28_FINAL_2026-11-15.mp4` 1920x1080@60, 5785 เฟรม, -13.0 LUFS, peak -1.1 dBFS, ไม่มีเฟรมดำ
- Katy404 วันที่ 28 9:16: `Timeline 1_9x16` 1080x1920 (Game Top / REACTIONS GIF preset `short` / VTuber Bottom 2.8x / VTuber Full 3.2x ตามช่วงซูม) ซับ `Mitr-short-001` ผ่าน DRT ไม่เขียนฐานข้อมูล; ซับ/เสียง/V1 ตรงกับ 16:9; ไฟล์รีวิว `วันที่ 28_9x16_test_2026-11-15.mp4` 5785 เฟรม -13.0 LUFS ไม่มีเฟรมดำ ซับอยู่เหนือผมไม่บังหน้า
- `rebuild_trimmed_zoom_clip.py`: เพิ่มคำเตือนว่าถ้า InsertGenerator ล้มหลังลบ clip track จะว่าง ให้ใช้เส้นทาง DRT (`drt_rebuild_focus_track.py`) แทน; OPERATING-NOTES เพิ่มกฎอ่าน timeline ซ้ำก่อน render ทุกครั้ง และย้ายแถว "Quiet raw mic recording" ที่ v0.17.95 วางผิดที่ (หลุดออกนอกตาราง) กลับเข้าตาราง
- timeline ที่เก็บไว้: `Timeline 1_original` (ดิบ) และ `Timeline 1_pre_zoomfix` (ก่อนแก้ซูม, V2 ว่าง) ยังไม่ลบ

### Skill ที่อัปเดต
- ไม่มี

### ไฟล์ที่เปลี่ยน
- แก้ไข `docs/OPERATING-NOTES.md`
- แก้ไข `docs/channels/katy404.md`
- แก้ไข `docs/skills-manifest.json`
- แก้ไข `scripts/rebuild_trimmed_zoom_clip.py`

## v0.17.96 — Katy404 วันที่ 28 promote Timeline หลัก

### รายละเอียด
- Katy404 วันที่ 28: promote `Timeline 1_edit` เป็น `Timeline 1` ตามที่ผู้ใช้สั่ง; timeline ดิบเก็บไว้เป็น `Timeline 1_original` (ไม่ลบ เพราะสั่งแค่ promote) อ่านกลับตรง baseline; timeline หลักอ่านกลับตรงแผนทุก track (ซูม 6, GIF 6, SFX 15, BGM 1, ซับ 86) และ Dialogue Leveler บน A1 ยังเปิด OutputGain 0.0; สำรอง `pre_promote.drp`
- บันทึกกับดักใน skill `resolve-audio`: ค่า Dialogue Leveler เป็น "Active Timeline Only" อ่านจาก timeline ที่ไม่ได้เปิดอยู่จะได้ `False` ทั้งหมด ต้องเปิด timeline ก่อนอ่าน

### Skill ที่อัปเดต
- `resolve-audio` (แก้ไข): `SKILL.md`

### ไฟล์ที่เปลี่ยน
- แก้ไข `.agents/skills/resolve-audio/SKILL.md`
- แก้ไข `docs/channels/katy404.md`
- แก้ไข `docs/skills-manifest.json`

## v0.17.95 — Katy404 วันที่ 28 + Dialogue Leveler

### รายละเอียด
- Katy404 วันที่ 28: สร้าง `Timeline 1_edit` สูตรเดียวกับวันที่ 27 ไม่ตัดเนื้อหา — VTuber Zoom 6 ช่วง (2.19x ไม่มีขอบดำ), GIF 6 ตัว (preset `vdo`), SFX 15 จุด (คลิก Minecraft นับ 1-2-3, Rare Achievement ตอนป๊อปอัป Voluntary Exile, Level Up ที่ 2,221 คน ฯลฯ), BGM `cheerful_blossom_day` -19 dB fade 12/120, ซับไทย 86 cue (ข้อความจาก Descript, Whisper ใช้จับเวลาเท่านั้น); `Timeline 1` ต้นฉบับไม่ถูกแตะ อ่านกลับครบทุก track
- ไฟล์ดิบวันที่ 28 เสียงเบามาก (-29 LUFS) จึงเปิด Dialogue Leveler บน A1: render QC ได้ -14.0 LUFS, LRA 3.3 LU, peak -1.1 dBFS, 6163 เฟรม ไม่มีเฟรมดำ (ไฟล์ `วันที่ 28_EDIT_test_2026-11-15.mp4` ในโฟลเดอร์ตอน)
- เพิ่มสคริปต์ใช้ซ้ำ `scripts/set_dialogue_leveler.py` (+ test) เปิด/ปิด Dialogue Leveler พร้อมตั้ง BackgroundReduction/OutputGain ชัดเจนและอ่านกลับ; บันทึกกับดัก OutputGain เด้งเป็น 2.0 ไว้ใน OPERATING-NOTES และ skill `resolve-audio`
- ยังต้องให้ผู้ใช้ฟังยืนยันคำ: ขอเคลียร์พิลเลเจอร์ (27.9 วิ), อันนี้บังเอิญมากเลย (31.7 วิ), ไอ้วันของวันที่ 27 (57.2 วิ), 2,222 / เลข 2 สี่ตัว (77-81 วิ)

### Skill ที่อัปเดต
- `resolve-audio` (แก้ไข): `SKILL.md`

### ไฟล์ที่เปลี่ยน
- แก้ไข `.agents/skills/resolve-audio/SKILL.md`
- แก้ไข `docs/OPERATING-NOTES.md`
- แก้ไข `docs/channels/katy404.md`
- แก้ไข `docs/skills-manifest.json`
- แก้ไข `docs/validation-report.json`
- แก้ไข `scripts/INDEX.md`
- เพิ่ม `scripts/set_dialogue_leveler.py`
- เพิ่ม `tests/test_set_dialogue_leveler.py`

## v0.17.94 — บันทึกการลบ Timeline สำรอง Bunny Girl ep10 (แก้ v0.17.93)

### รายละเอียด
- แก้ข้อผิดพลาดของ v0.17.93: บันทึกการลบ Timeline สำรองของ Bunny Girl ep10 ยังไม่ได้ลงโปรไฟล์ช่อง Katy404 เพราะการแก้ไฟล์ไม่สำเร็จ (ข้อความอ้างอิงไม่ตรง) ทั้งที่ release นั้นเขียนว่าบันทึกแล้ว รุ่นนี้เพิ่มบันทึกนั้นจริงแล้ว
- เนื้อหาที่บันทึก: ลบ `Timeline 1_original`, `Timeline 1_base`, `Timeline 1_pop` ด้วย ID เหลือ `Timeline 1` อันเดียว ซึ่งอ่านกลับตรงกับก่อนลบทุก track, ไฟล์ย้อนกลับ `pre_delete_timelines.drp` และกับดักเรื่องสคริปต์ scratch ที่ไม่มี `__main__` guard จะทำงานซ้ำเมื่อถูก import
- ทดสอบ: `pytest` ผ่าน 450 ข้าม 35

### Skill ที่อัปเดต
- ไม่มี

### ไฟล์ที่เปลี่ยน
- แก้ไข `docs/channels/katy404.md`
- แก้ไข `docs/skills-manifest.json`

## v0.17.93 — ลบ Timeline สำรอง Bunny Girl ep10

### รายละเอียด
- ลบ Timeline สำรองของ Bunny Girl ep10 (Katy404) ตามคำสั่งผู้ใช้: `Timeline 1_original`, `Timeline 1_base`, `Timeline 1_pop` ลบด้วย ID แล้ว เหลือ `Timeline 1` (งานตัดต่อที่อัปเดตเป็น Timeline หลักไว้แล้ว) เพียงอันเดียว
- ผลที่อ่านกลับแล้ว: `Timeline 1` ทุก track ตรงกับก่อนลบ (V1 7, V2 7, V3 5, A1 4, A2 46, A3 2, ซับ 165, 9762 เฟรม) บันทึกโปรเจคแล้ว และมีไฟล์ย้อนกลับ `pre_delete_timelines.drp`
- บันทึกขั้นตอนและกับดักลงโปรไฟล์ช่อง Katy404: สคริปต์ scratch ที่ไม่มี `__main__` guard จะทำงานซ้ำเมื่อถูก import

### Skill ที่อัปเดต
- ไม่มี

### ไฟล์ที่เปลี่ยน
- แก้ไข `docs/skills-manifest.json`

## v0.17.92 — อัปเดต Timeline หลัก Bunny Girl ep10

### รายละเอียด
- อัปเดต Timeline หลักของ Bunny Girl ep10 (Katy404) ตามคำสั่งผู้ใช้: `Timeline 1_pop_mitr` เปลี่ยนชื่อเป็น `Timeline 1` แล้ว ส่วน `Timeline 1` ดิบเดิมเปลี่ยนชื่อเป็น `Timeline 1_original` (ผู้ใช้ไม่ได้สั่งลบ จึงไม่ลบ timeline ใด)
- ผลที่อ่านกลับแล้ว: ทั้งสอง timeline ทุก track ตรงกับก่อนเปลี่ยนชื่อ (V1 7, V2 7, V3 5, A1 4, A2 46, A3 2, ซับ 165, 9762 เฟรม) บันทึกโปรเจคแล้ว และมีไฟล์ย้อนกลับ `pre_promote.drp`
- บันทึกขั้นตอนนี้ลงโปรไฟล์ช่อง Katy404

### Skill ที่อัปเดต
- ไม่มี

### ไฟล์ที่เปลี่ยน
- แก้ไข `docs/channels/katy404.md`
- แก้ไข `docs/skills-manifest.json`

## v0.17.91 — ตัดต่อ Bunny Girl ep10 ของ Katy404 แบบ Pop Kinetic

### รายละเอียด
- ตัดต่อ Bunny Girl ep10 "ถ้าคาแรกเตอร์ของผมกลายเป็น Bunny Girl จะเป็นยังไง" ของช่อง Katy404 ตามสูตร Pop Kinetic ของซีรีส์ เพื่อให้คนดูอยู่ต่อ: การ์ด CHAPTER 3 บท (ชุดสายชิล / นิสัย / เสียงผู้ชาย) พร้อมช่วงเงียบ 1.6 วิ, ซูม VTuber 7 ช่วงที่มุกเด็ด, คำกระแทก 43 จุด, การ์ดรูป 13 ใบ, ซับไทย 165 cue สไตล์ `Mitr Font`, SFX 46 จุด และ BGM
- ผลที่อ่านกลับแล้ว: `Timeline 1_pop_mitr` ยาว 9762 เฟรม ทุก track ตรงกับ `Timeline 1_pop` (V1 7, V2 7 ซูม Size 1.35, V3 5, A1 4, A2 46, A3 2, ซับ 165) และ `Timeline 1` ต้นฉบับไม่ถูกแก้ ยังไม่ได้ render (ผู้ใช้ตรวจใน Resolve เอง)
- บันทึกตอน ep10 ลงโปรไฟล์ช่อง Katy404 พร้อมคำที่ต้องฟังยืนยัน 5 จุด
- เพิ่มบันทึกปฏิบัติงาน 2 ข้อ: อัปโหลดเฉพาะเสียงไป Descript (1.5 MB แทน 473 MB) และห้ามส่งโค้ดที่มีภาษาไทยผ่าน bash heredoc บนเครื่องนี้ เพราะตัวอักษรเพี้ยนจนการแทนที่ข้อความไม่ทำงาน
- ทดสอบ: `pytest` ผ่าน 450 ข้าม 35

### Skill ที่อัปเดต
- ไม่มี

### ไฟล์ที่เปลี่ยน
- แก้ไข `docs/OPERATING-NOTES.md`
- แก้ไข `docs/channels/katy404.md`
- แก้ไข `docs/skills-manifest.json`

## v0.17.90 — รูปประกอบเต็มจอในคลิปแนวตั้ง Yu-Gi-Oh ของ Laffy

### รายละเอียด
- ตั้งรูปประกอบบน V3 ของ `รู้จัก Yu-Gi-Oh ได้ยังไง-vdo_9x16` ทั้ง 8 รูปให้เต็มจอตามที่ผู้ใช้สั่ง ใช้ cover zoom 1.25–3.56 และ Pan/Tilt 0 แทน preset `short` ที่ทำให้รูปเล็กบังหน้า
- ค่าทุกรูปอ่านกลับมาตรง และ backup .drp ไว้ก่อนแก้ ภาพนิ่ง QC ทั้ง 8 จุดเต็มเฟรม ไม่มีขอบดำ
- รูปกว้างถูกตัดข้างกลางภาพ เช่น ตัวอักษรมีมใน `hq720.jpg`
- house-style เพิ่มข้อยกเว้น: รูปที่เป็นภาพเต็มจอใน 16:9 ต้องเต็มจอใน 9:16 ด้วย ส่วน `short` ใช้กับ GIF และ overlay อื่น
- อัปเดต skill talking-avatar-vertical-copy และโปรไฟล์ Laffy ให้ตรงกับกฎใหม่

### Skill ที่อัปเดต
- `house-style` (แก้ไข): `SKILL.md`
- `talking-avatar-vertical-copy` (แก้ไข): `SKILL.md`

### ไฟล์ที่เปลี่ยน
- แก้ไข `.agents/skills/house-style/SKILL.md`
- แก้ไข `.agents/skills/talking-avatar-vertical-copy/SKILL.md`
- แก้ไข `docs/channels/laffy.md`
- แก้ไข `docs/skills-manifest.json`

## v0.17.89 — ตรวจและจัดเวลาซับคลิปแนะนำตัว Laffy ให้ตรงเสียง

### รายละเอียด
- ตรวจซับคลิปแนะนำตัว Laffy เทียบกับเสียง: cue เดิมที่แบ่งตามจำนวนตัวอักษรช้าหรือเร็วกว่าเสียงสูงสุด 1.7 วิ (39 cue เกิน 0.5 วิ) จึงจัดเวลาใหม่เป็น 151 cue โดยข้อความยังเป็นของ Descript ทุกตัว ใช้จุดเริ่มประโยคของ Descript + แผนที่เสียง 10 ms + Whisper (ในเครื่อง, ผู้ใช้อนุญาต, ใช้แค่เวลา) ผลตรวจ: ไม่มี cue ขึ้นก่อนเสียง ไม่มีช่วงพูดที่ไม่มีซับ caption_lint ผ่าน และ track อื่น/การ์ด/ซูม/เสียงไม่เปลี่ยน
- render `laffy_intro_edit_v5.mov` 4407 เฟรม -14.4 LUFS peak -0.5 dBFS ตรวจภาพเฟรมที่แก้แล้ว
- บันทึกวิธีตรวจ sync และกับดัก (Resolve auto-caption ภาษาไทยได้ 0 cue, Descript project เข้าไม่ได้เมื่อเปลี่ยนบัญชี, ช่วงเสียงคร่อมประโยคต้องตัดไม่ใช่ทิ้ง) ใน OPERATING-NOTES และ skill thai-subtitles-resolve
- house-style: ใช้ Whisper ในเครื่องเป็นตัวอ้างอิงเวลาได้ (ไม่ใช้เป็นข้อความซับ)
- ทดสอบทั้งชุดผ่าน 450 ตัว (ข้าม 35)

### Skill ที่อัปเดต
- `house-style` (แก้ไข): `SKILL.md`
- `thai-subtitles-resolve` (แก้ไข): `SKILL.md`

### ไฟล์ที่เปลี่ยน
- แก้ไข `.agents/skills/house-style/SKILL.md`
- แก้ไข `.agents/skills/thai-subtitles-resolve/SKILL.md`
- แก้ไข `docs/OPERATING-NOTES.md`
- แก้ไข `docs/channels/laffy.md`
- แก้ไข `docs/skills-manifest.json`

## v0.17.88 — แยกซับยาวในคลิปแนวตั้ง Yu-Gi-Oh ของ Laffy

### รายละเอียด
- แยก 2 cue ที่กว้างเกินเฟรมใน `รู้จัก Yu-Gi-Oh ได้ยังไง-vdo_9x16` ตามที่ผู้ใช้สั่ง: `ทุกวันเสาร์ | อาทิตย์เลยครับ` แยกที่เฟรม 726 และ `เรื่องนั้นคือเรื่อง | Yuki-o` แยกที่เฟรม 768 จุดแยกวางตรงช่วงเสียงเบาของเสียงพูด
- ซับ 9:16 จาก 61 เพิ่มเป็น 63 cue ข้อความและเฟรมตรงตามแผนทุกตัว วิดีโอ/เสียงไม่เปลี่ยน และ backup .drp ไว้ก่อนแก้ ส่วน 16:9 ไม่ได้แตะ
- render burn-in ยืนยันว่าสไตล์ `Mitr-short-001` ยังอยู่ และทั้ง 4 cue ใหม่อยู่ในเฟรม 1080
- skill thai-subtitles-resolve (0.5.8) บันทึกวิธีแยก cue โดยไม่เสียสไตล์ของแทร็ก: ลบเฉพาะคลิปซับ แล้ว append SRT ลงแทร็กเดิม

### Skill ที่อัปเดต
- `thai-subtitles-resolve` (แก้ไข): `SKILL.md`, `references/native-caption-migration.md`

### ไฟล์ที่เปลี่ยน
- แก้ไข `.agents/skills/thai-subtitles-resolve/SKILL.md`
- แก้ไข `.agents/skills/thai-subtitles-resolve/references/native-caption-migration.md`
- แก้ไข `docs/channels/laffy.md`
- แก้ไข `docs/skills-manifest.json`

## v0.17.87 — ย้ายซับ Yu-Gi-Oh ของ Laffy ไป Subtitle track พร้อม preset

### รายละเอียด
- ย้ายซับของ Laffy "รู้จัก Yu-Gi-Oh ได้ยังไง" ไปใช้ Subtitle track ทั้ง timeline แนวนอนและแนวตั้ง โดยเปิด ST1 (ข้อความและเวลาตรงกับ Text+ ทั้ง 61 cue) และปิด V4 Text+ ไว้ ไม่ได้ลบ
- โหลด preset จาก library หลักตามที่ผู้ใช้เลือก แนวนอนใช้ `Mitr Font` แนวตั้งใช้ `Mitr-short-001` ผ่าน DRT ไม่ต้องปิด Resolve และ backup .drp ไว้ก่อนแก้
- ทุกแทร็กอ่านค่ากลับมาตรงกับ timeline เดิม และเก็บ timeline เดิมไว้เป็น `_old`
- render burn-in ช่วงสั้นยืนยันว่า preset ทำงานทั้งสองแบบ แต่แนวตั้งมี 2 cue ที่กว้างเกินเฟรม 1080 รายงานไว้แต่ยังไม่ได้แยก cue
- skill thai-subtitles-resolve (0.5.7) บันทึกขั้นตอนย้าย "Subtitle as Text+" บน 21.1 ไว้ 4 เรื่อง:
- ห้ามอ่าน `StyledText` ของ Text+ แบบสด เพราะทำให้ Resolve ค้างจนต้องกู้
- ช่อง Name ของ cue ใน DRT อาจเป็นข้อความเก่า
- ขั้นตอนใส่ preset ผ่าน DRT
- วิธีวัดความกว้างซับบน 9:16

### Skill ที่อัปเดต
- `thai-subtitles-resolve` (แก้ไข): `SKILL.md`, `references/native-caption-migration.md`

### ไฟล์ที่เปลี่ยน
- แก้ไข `.agents/skills/thai-subtitles-resolve/SKILL.md`
- แก้ไข `.agents/skills/thai-subtitles-resolve/references/native-caption-migration.md`
- แก้ไข `docs/channels/laffy.md`
- แก้ไข `docs/skills-manifest.json`

## v0.17.86 — ขยายซับ Text+ ในคลิปแนวตั้ง Yu-Gi-Oh ของ Laffy

### รายละเอียด
- ขยายซับ Text+ บน V4 ของ `รู้จัก Yu-Gi-Oh ได้ยังไง-vdo_9x16` ทั้ง 61 ตัว จาก Size 0.07 เป็น 0.12 ตามที่ผู้ใช้สั่ง เพราะในเฟรมกว้าง 1080 ซับเดิมเล็กลงเหลือ 56%
- แก้เฉพาะสำเนา 9:16 ต้นฉบับ 16:9 อ่านค่ากลับมายังเป็น 0.07 ครบ 61 ตัว และ backup .drp ไว้ก่อนแก้
- ภาพนิ่ง QC ประโยคยาว 5 ประโยคยืนยันว่าประโยคยาวที่สุดกว้างราว 2/3 ของเฟรม ไม่ล้นขอบ
- skill talking-avatar-vertical-copy (0.1.3) บันทึกวิธีขยาย Text+ ในสำเนา และค่าที่ใช้ได้

### Skill ที่อัปเดต
- `talking-avatar-vertical-copy` (แก้ไข): `SKILL.md`

### ไฟล์ที่เปลี่ยน
- แก้ไข `.agents/skills/talking-avatar-vertical-copy/SKILL.md`
- แก้ไข `docs/channels/laffy.md`
- แก้ไข `docs/skills-manifest.json`

## v0.17.85 — ทำคลิปแนวตั้ง รู้จัก Yu-Gi-Oh ได้ยังไง ของ Laffy

### รายละเอียด
- สร้าง timeline แนวตั้ง `รู้จัก Yu-Gi-Oh ได้ยังไง-vdo_9x16` (1080x1920, 30 fps, 1323 เฟรมเท่าต้นฉบับ) ของ Laffy ปรับแค่การจัดเฟรม ไม่ได้ตัดอะไรออก ต้นฉบับไม่ถูกแตะ และ backup .drp ไว้ก่อนแก้
- V1 ซูมให้เต็มความสูง 3.1605x และ Pan +83.6 ให้ผมอยู่กลางเฟรม
- ซูม Adjustment Clip ของ V2 ย่อตามสัดส่วนจาก 1.28/1.54/2.03x เป็น 1.06/1.12/1.23x ตามแบบที่ผู้ใช้เลือก
- ภาพนิ่ง QC 7 จุดยืนยันว่าเห็นผมครบทุกช่วง และไม่มีขอบดำ
- ทุกแทร็กที่ห้ามแตะ (ซับ Text+, ST1, เสียงทั้งหมด) อ่านค่ากลับมาแล้วตรงกับต้นฉบับ
- V3 ใช้ preset `short` ตามกฎ 9:16 ของบ้าน QC พบว่ารูปบังหน้า รายงานไว้แต่ไม่ได้ย้ายรูป
- skill talking-avatar-vertical-copy เพิ่มสูตรเพดานซูมกันผมหลุดขอบ สำหรับ Adjustment Clip ที่ซูมด้วย Inspector
- skill เดียวกันบันทึกว่าซับ Text+ ในสำเนาที่กว้าง 1080 จะเล็กลงเหลือ 56% และใช้ภาพนิ่งพอสำหรับ QC การจัดเฟรม
- อัปเดตโปรไฟล์ Laffy ด้วยโครงโปรเจกต์ Yu-Gi-Oh และ timeline 9:16 ใหม่
- refresh skills manifest ตาม CHANGELOG/VERSION ของ v0.17.84

### Skill ที่อัปเดต
- `talking-avatar-vertical-copy` (แก้ไข): `SKILL.md`

### ไฟล์ที่เปลี่ยน
- แก้ไข `.agents/skills/talking-avatar-vertical-copy/SKILL.md`
- แก้ไข `docs/channels/laffy.md`
- แก้ไข `docs/skills-manifest.json`

## v0.17.84 — แก้ชื่อ LaffeyNilvalen ในคลิปแนะนำตัว Laffy

### รายละเอียด
- แก้ชื่อในคลิปแนะนำตัว Laffy ตามที่ผู้ใช้ยืนยัน: ซับ cue 222-244 จาก `RaffyNiveren` เป็น `LaffeyNilvalen` (แก้ผ่าน DRT เพราะ MCP set_name ใช้กับซับไม่ได้) และการ์ดชื่อใหม่ `card01b.mov`; ทุก item/ระดับเสียง/fade/ค่าซูมอื่นตรงกับเวอร์ชันก่อนแก้ทุกตัว, เก็บเวอร์ชันเก่าไว้เป็น `เเนะนำตัว 3 นาที_edit_old`
- render ใหม่ `laffy_intro_edit_v3.mov` 4407 เฟรม -14.4 LUFS peak -0.5 dBFS ตรวจภาพเฟรมชื่อแล้วถูกต้อง
- บันทึกชื่อเต็ม LaffeyNilvalen และช่อง YouTube ในโปรไฟล์ช่อง Laffy
- ทดสอบทั้งชุดผ่าน 450 ตัว (ข้าม 35)

### Skill ที่อัปเดต
- ไม่มี

### ไฟล์ที่เปลี่ยน
- แก้ไข `docs/channels/laffy.md`
- แก้ไข `docs/skills-manifest.json`

## v0.17.83 — ตัดต่อคลิปแนะนำตัว 3 นาที ของ Laffy

### รายละเอียด
- ตัดต่อคลิป "แนะนำตัว 3 นาที" ของช่อง Laffy เป็น timeline ใหม่ `เเนะนำตัว 3 นาที_edit` (`Timeline 1` ต้นฉบับไม่แตะ) ไม่ตัดเนื้อหาออกตามที่ผู้ใช้เลือก: ซับไทย `Mitr Font` 165 cue, VTuber Zoom 1.32x 8 ช่วง, การ์ดคีย์เวิร์ด 21 ใบ (รวมมุก เทค 2/3/4), pop/record scratch, BGM lo-fi -22 dB; render ตรวจแล้ว 4407 เฟรม -14.4 LUFS peak -0.5 dBFS ไม่มีเฟรมดำ
- `drt_clone_subtitle_style.py` ใส่สไตล์ซับให้ timeline ที่ยังไม่มี Subtitle track ได้ (ไม่ต้องสร้าง track ชั่วคราว) พร้อม test ใหม่
- บันทึกบทเรียน: preset `H.264 Master` ได้ไฟล์ `.mov`, ลดเสียง pop เป็น -13 dB เมื่อเสียงพูดดัง, ทำการ์ดตัวหนังสือไทยด้วย headless Chrome + `card_pop_overlay.py`
- house-style: เก็บช่วงพูดซ้ำ/ขอใหม่ไว้ถ้าผู้ใช้ไม่อนุมัติให้ตัด และทำเป็นมุกแทน
- ทดสอบทั้งชุดผ่าน 450 ตัว (ข้าม 35)

### Skill ที่อัปเดต
- `house-style` (แก้ไข): `SKILL.md`
- `resolve-video-enrichment` (แก้ไข): `SKILL.md`, `references/illustration-assets.md`

### ไฟล์ที่เปลี่ยน
- แก้ไข `.agents/skills/house-style/SKILL.md`
- แก้ไข `.agents/skills/resolve-video-enrichment/SKILL.md`
- แก้ไข `.agents/skills/resolve-video-enrichment/references/illustration-assets.md`
- แก้ไข `docs/OPERATING-NOTES.md`
- แก้ไข `docs/channels/laffy.md`
- แก้ไข `docs/skills-manifest.json`
- แก้ไข `docs/validation-report.json`
- แก้ไข `scripts/INDEX.md`
- แก้ไข `scripts/drt_clone_subtitle_style.py`
- แก้ไข `tests/test_drt_clone_subtitle_style.py`

## v0.17.82 — ย้ายปก KT404 HL 2026-10-1 มารวมใน Thumbnails

### รายละเอียด
- ย้ายปก KT404 Highlights 2026-10-1 ทั้ง 134 ไฟล์ออกจากโฟลเดอร์ย่อย `Horizontal_16x9` / `Vertical_9x16` มาไว้ใน `2026-10-1/Thumbnails/` โดยตรงตามที่ผู้ใช้ขอ แล้วลบโฟลเดอร์ย่อยที่ว่างออก (แนวนอน 67 + แนวตั้ง `_9x16` 67, ไม่มีชื่อซ้ำ, md5 ตรงกับไฟล์ต้นทางครบ 134 ไฟล์)
- บันทึกในโปรไฟล์ช่อง Katy404 และ skill vtuber-cover-batch-pipeline ว่าช่องนี้ต้องการปกรวมใน `Thumbnails/` ไม่แยกโฟลเดอร์ตามสัดส่วน

### Skill ที่อัปเดต
- `vtuber-cover-batch-pipeline` (แก้ไข): `SKILL.md`

### ไฟล์ที่เปลี่ยน
- แก้ไข `.agents/skills/vtuber-cover-batch-pipeline/SKILL.md`
- แก้ไข `docs/channels/katy404.md`
- แก้ไข `docs/skills-manifest.json`

## v0.17.81 — ปกคลิปครบทุก Timeline ของ KT404 Highlights 2026-10-1

### รายละเอียด
- ทำปกคลิปครบทุก Timeline ของ KT404 Highlights 2026-10-1: 67 Timeline x 2 สัดส่วน = 134 ไฟล์ (แนวนอน 1920x1080 และแนวตั้ง 1080x1920) ตั้งชื่อตาม Timeline และวางไว้ที่ `2026-10-1/Thumbnails/Horizontal_16x9` กับ `Vertical_9x16` ใน Google Drive (md5 ตรงกับไฟล์ต้นทางครบ 134 ไฟล์)
- ใช้สไตล์เดียวกับปก KT404 2026-09-29 ที่อัปโหลดแล้ว: ข้อความจากชื่อคลิปใน Timeline แบ่งบรรทัดแดง/ขาว (Mitr Bold ขอบดำ) และเลือกโมเดลเคที่ตามอารมณ์ของชื่อคลิป ภาพพื้นหลังคัดจากเฟรมจริงของคลิปละ 6–14 เฟรม และครอปเฉพาะส่วนเกมเพื่อไม่ให้อวาตาร์ในสตรีมซ้อนกับโมเดล
- ตรวจแล้ว: agent-thumbnail `cli.verify` ผ่าน 134/134 ไม่มีปัญหา, ขนาด/ฟอร์แมต/ไฟล์ไม่เกิน 2MB ครบ, ข้อความไม่ทับโมเดลในแนวนอน (นับพิกเซล = 0 ทุกใบ) และไม่ทับกรอบภาพเกมในแนวตั้ง, ตรวจ contact sheet ทุกใบ
- ข้อสังเกต: #40 ชื่อ Timeline ถูกตัดที่ "ล้" จึงใช้คำจากซับ "โดนทีเดียวตาย"; #16 ไม่พบเฟรมที่เห็นป้ายโรงเรียน; ไม่ได้แก้อะไรใน Resolve (อ่านอย่างเดียว)
- บันทึกบทเรียนการทำปกลง skill vtuber-cover-batch-pipeline และโปรไฟล์ช่อง Katy404 แก้การอ้างไฟล์ scratch ใน skill/โปรไฟล์ที่ทำให้เทสต์ล้ม (pytest ผ่าน 449)

### Skill ที่อัปเดต
- `thai-subtitles-resolve` (แก้ไข): `SKILL.md`
- `vtuber-cover-batch-pipeline` (แก้ไข): `SKILL.md`

### ไฟล์ที่เปลี่ยน
- แก้ไข `.agents/skills/thai-subtitles-resolve/SKILL.md`
- แก้ไข `.agents/skills/vtuber-cover-batch-pipeline/SKILL.md`
- แก้ไข `docs/channels/armigon.md`
- แก้ไข `docs/channels/katy404.md`
- แก้ไข `docs/skills-manifest.json`

## v0.17.80 — ทำ 9:16 ครบทุก timeline ของ KT404 Highlights 2026-10-1

### รายละเอียด
- สร้าง 9:16 ครบทุก timeline ของ `KT404 Highlights 2026-10-1` (67 อัน รวมตัวต้นแบบ) โครงเดียวกับตัวต้นแบบ: เกมบน / GIF preset `short` ใหม่ / อวาตาร์กลางกรอบล่าง / ซูมอวาตาร์เต็มจอตามช่วงซูม 16:9 / ซับสไตล์ใหม่ที่ผู้ใช้โหลด
- ตรวจครบ 67 อัน: เสียง ซับ V1 ช่วงซูม ช่วง GIF สไตล์ซับ และ 1080x1920 ตรงกับต้นฉบับทุกอัน
- ปรับกรอบเกมด้านบนให้อยู่ในพื้นที่เกมจริงของแต่ละไลฟ์ (RoV/Minecraft มีขอบดำในต้นฉบับ) อ่านค่ากลับครบ 67 อัน และดูภาพนิ่ง 1 อันต่อไลฟ์ (18 ไลฟ์)
- บันทึกบทเรียน: วางคลิปเฟรมเรตต่างกันต้องลองเฟรมท้ายใกล้เคียง, รีสตาร์ต Resolve ทุก ~10 GB, ตรวจ `GetCurrentPage()` หลังเปิดใหม่, ไดรฟ์ G: ค้างทำให้ Resolve ปิดไม่ได้

### Skill ที่อัปเดต
- `vertical-video-reframing` (แก้ไข): `SKILL.md`
- `vtuber-cover-batch-pipeline` (แก้ไข): `SKILL.md`

### ไฟล์ที่เปลี่ยน
- แก้ไข `.agents/skills/vertical-video-reframing/SKILL.md`
- แก้ไข `.agents/skills/vtuber-cover-batch-pipeline/SKILL.md`
- แก้ไข `docs/OPERATING-NOTES.md`
- แก้ไข `docs/channels/hoshi-1489.md`
- แก้ไข `docs/channels/katy404.md`
- แก้ไข `docs/skills-manifest.json`

## v0.17.79 — สร้างคลิปแนวตั้ง Katy404 วันที่ 27

### รายละเอียด
- สร้าง Timeline 1_9x16 สำหรับ Katy404 วันที่ 27 ขนาด 1080x1920@60 แบบเกมบน–อวาตาร์ล่าง และคงช่วงโฟกัสเดิม 5 ช่วง
- รักษาเสียงและซับ 67 cue ตรงกับแนวนอน โหลด Mitr-short-001 ผ่าน DRT โดยไม่ปิด Resolve และไม่แก้ Timeline แนวนอน
- ตรวจ render สำเร็จ 3725 เฟรม เสียง -15.8 LUFS / -1.6 dBTP ไม่มีช่วงภาพดำ แก้ซับแตะผมในช่วงโฟกัสแล้ว ตรวจภาพตัวอย่าง ไม่ได้ฟังหรือดู motion ครบทั้งคลิป
- ชุดทดสอบ repo: 446 ผ่าน 5 ไม่ผ่านจาก reference scratch ที่ขาดและ manifest checksum เดิม; refresh manifest หลังบันทึกเอกสาร

### Skill ที่อัปเดต
- ไม่มี

### ไฟล์ที่เปลี่ยน
- แก้ไข `docs/channels/katy404.md`
- แก้ไข `docs/skills-manifest.json`

## v0.17.78 — อัปเดต preset short และซับของ 9:16 KT404

### รายละเอียด
- อัปเดต video preset `short` ตามที่ผู้ใช้บันทึกใหม่: Zoom 0.42 / Pan 0 / Position Y 655.26 (เดิม 403.2) เก็บใน `scripts/video_presets.json` และใช้กับ GIF ทั้ง 2 ตัวบน `ไฟต์ท้ายเกมปิดชัยชนะ-League of Legends-vdo_9x16` แล้ว (อ่านค่ากลับตรงกัน)
- แก้ `apply_vdo_preset.py --capture` ให้เก็บค่าจากคลิปบน track ของ preset (REACTIONS) ใต้ playhead แทน `GetCurrentVideoItem()` ที่ไปหยิบคลิปอวาตาร์ V3 ผิดตัว
- เก็บสไตล์ซับใหม่ที่ผู้ใช้โหลดบน timeline นี้เป็น DRT อ้างอิงสำหรับทำ 9:16 ที่เหลือ; อัปเดต house-style, talking-avatar-vertical-copy และโปรไฟล์ Katy404

### Skill ที่อัปเดต
- `house-style` (แก้ไข): `SKILL.md`
- `talking-avatar-vertical-copy` (แก้ไข): `SKILL.md`

### ไฟล์ที่เปลี่ยน
- แก้ไข `.agents/skills/house-style/SKILL.md`
- แก้ไข `.agents/skills/talking-avatar-vertical-copy/SKILL.md`
- แก้ไข `docs/channels/katy404.md`
- แก้ไข `docs/skills-manifest.json`
- แก้ไข `scripts/apply_vdo_preset.py`
- แก้ไข `scripts/video_presets.json`

## v0.17.77 — โปรโมต Timeline หลัก Katy404 วันที่ 27

### รายละเอียด
- โปรโมต `Timeline 1_edit` ของ Katy404 วันที่ 27 เป็น `Timeline 1` ตามที่ผู้ใช้สั่ง และลบ Timeline ดิบเดิมด้วย unique ID; อ่านกลับทุก track แล้วเท่าเดิม (V2 5, V3 6, A2 13, S1 67)
- สำรอง `pre_promote.drp` ไว้เป็นจุดย้อนกลับ และบันทึกในโปรไฟล์ช่อง Katy404

### Skill ที่อัปเดต
- ไม่มี

### ไฟล์ที่เปลี่ยน
- แก้ไข `docs/channels/katy404.md`
- แก้ไข `docs/skills-manifest.json`

## v0.17.76 — โหลดซับ Mitr-short-001 ให้ 9:16 ของ KT404

### รายละเอียด
- โหลด preset ซับ `Mitr-short-001` ให้ `ไฟต์ท้ายเกมปิดชัยชนะ-League of Legends-vdo_9x16` ผ่าน DRT (ไม่เขียน DB, Resolve ไม่ต้องปิด) timeline ใหม่ id `fec53400…` ทุก track/ค่า transform/เสียงอ่านกลับเท่าเดิม แล้วลบตัวเก่าตาม ID
- ตรวจด้วยภาพ render 3 เฟรม (ซับ burn-in): ซับขึ้นตัว Mitr หนา ขอบดำ; ช่วงจอแบ่งอยู่ตรงรอยต่อเกม/อวาตาร์ แต่ช่วงซูมเต็มจอทับตา/จมูก
- บันทึกขั้นตอนและข้อสังเกตไว้ในโปรไฟล์ช่อง Katy404; backup `pre_sub_short.drp`

### Skill ที่อัปเดต
- ไม่มี

### ไฟล์ที่เปลี่ยน
- แก้ไข `docs/OPERATING-NOTES.md`
- แก้ไข `docs/channels/katy404.md`
- แก้ไข `docs/skills-manifest.json`

## v0.17.75 — ตัดต่อ Katy404 วันที่ 27 ให้น่าดูขึ้น

### รายละเอียด
- ตัดต่อ Katy404 วันที่ 27 บนสำเนา `Timeline 1_edit` (ต้นฉบับ `Timeline 1` ไม่แตะ ตรวจอ่านกลับแล้วเท่าเดิม): ซูม VTuber 5 ช่วง, GIF 6 ตัว (ค่า vdo), SFX 13 จุด, BGM, ซับไทย 67 cue สไตล์ `Mitr Font` ผ่าน DRT ไม่ต้องปิด Resolve
- ไฟล์ทดสอบ render สำเร็จ 3725 เฟรม 1920x1080@60, -15.8 LUFS, true peak -1.6 dBTP (ตรงกับค่าที่จำลอง mix ไว้ล่วงหน้า), ไม่มีเฟรมดำ, ตรวจภาพ 20 เฟรมแล้ว
- บันทึกในโปรไฟล์ช่อง Katy404: ตำแหน่งกรอบซูมของวันที่ 27 (ผมสูงกว่าวันที่ 26 จึงยกกรอบขึ้น) และคำที่ต้องให้ผู้ใช้ฟังยืนยัน ("วันที่ 26", "1,200 คน")
- แก้ OPERATING-NOTES แถว Python บนเครื่อง DESKTOP-C0B08FI: ใน terminal ของ Hermes คำสั่ง `python` เป็น venv ของ Hermes ที่ไม่มี CUDA DLL ต้องใช้ `py -3.12`
- เทส: 446 ผ่าน, 5 ไม่ผ่านซึ่งไม่ผ่านอยู่แล้วก่อนงานนี้ (อ้างถึงไฟล์ scratch ที่อยู่บนเครื่องอื่น)

### Skill ที่อัปเดต
- ไม่มี

### ไฟล์ที่เปลี่ยน
- แก้ไข `docs/OPERATING-NOTES.md`
- แก้ไข `docs/channels/katy404.md`
- แก้ไข `docs/skills-manifest.json`

## v0.17.74 — จัดอวาตาร์ KT404 ให้อยู่กลางกรอบล่างใน 9:16

### รายละเอียด
- จัดอวาตาร์ Katy404 ให้อยู่กลางกรอบล่าง (VTuber Bottom) ของ `ไฟต์ท้ายเกมปิดชัยชนะ-League of Legends-vdo_9x16` แล้ว: window ต้นทาง 1360-1920 x 582-1080 (Zoom 3.43, Pan -1311.4, Tilt 257.4) อวาตาร์ใหญ่ขึ้นราว 18% เพราะกรอบต้องชิดขอบขวาของต้นทางจึงจะไม่มีขอบดำ
- ตรวจ still จาก Resolve 6 เฟรม (ก่อน/หลัง): อวาตาร์อยู่กลาง ไม่มีขอบดำ ahoge ไม่ถูกตัด; track เสียง/ซับ/V1/V2/V4 อ่านกลับเท่าเดิม; backup `pre_center_bottom.drp`
- บันทึกค่ากรอบใหม่ไว้ในโปรไฟล์ช่อง Katy404 สำหรับทำ 9:16 อีก 66 timeline

### Skill ที่อัปเดต
- ไม่มี

### ไฟล์ที่เปลี่ยน
- แก้ไข `docs/channels/katy404.md`
- แก้ไข `docs/skills-manifest.json`

## v0.17.73 — release notes แสดง skill และไฟล์ที่เปลี่ยน

### รายละเอียด
- release ทุกเวอร์ชันมี 3 หัวข้อ: `รายละเอียด` (เขียนเอง), `Skill ที่อัปเดต` และ `ไฟล์ที่เปลี่ยน` (`release.py` สร้างให้จาก `git diff --name-status` ตั้งแต่ tag ก่อนหน้า)
- รายการ skill บอกสถานะ ใหม่/แก้ไข/ลบ และไฟล์ในแต่ละ skill; รายการไฟล์บอก เพิ่ม/แก้ไข/ลบ/เปลี่ยนชื่อ ไม่รวม `VERSION`/`CHANGELOG.md` แสดงสูงสุด 40 บรรทัด
- `AGENTS.md`, `project-learning` (0.2.1) และ `scripts/INDEX.md` อธิบายขั้นตอนใหม่: push commit เนื้อหาก่อน `--publish`, ห้ามพิมพ์รายการไฟล์เอง, stash `.mcp.json` ชั่วคราว
- เพิ่ม test 5 ข้อใน `tests/test_release.py` ผ่านครบ 16/16; ทั้ง repo ผ่าน 446 ข้าม 35 ส่วนที่ตก 5 ข้อมีอยู่เดิมบน origin (โปรไฟล์ Armigon และ skill 2 ตัวอ้างสคริปต์ scratch ที่ไม่มี)

### Skill ที่อัปเดต
- `project-learning` (แก้ไข): `SKILL.md`

### ไฟล์ที่เปลี่ยน
- แก้ไข `.agents/skills/project-learning/SKILL.md`
- แก้ไข `AGENTS.md`
- แก้ไข `docs/skills-manifest.json`
- แก้ไข `scripts/INDEX.md`
- แก้ไข `scripts/release.py`
- แก้ไข `tests/test_release.py`

## v0.17.72 — กับดักการ release เมื่อมีหลาย session

### รายละเอียด
- `agent-skill-repo-release` เพิ่มกับดัก 2 ข้อ: `release.py --publish` ต้องการ working tree สะอาดและ `HEAD == origin/main` (push commit เนื้อหาก่อน, stash `.mcp.json` ชั่วคราว) และวิธีกู้ไฟล์เมื่อ session อื่น reset `main` ไปที่ `origin/main` ระหว่างทำงาน

## v0.17.71 — skill ทำ 9:16 คลิป VTuber เดี่ยว

### รายละเอียด
- เพิ่ม skill `talking-avatar-vertical-copy` สำหรับทำสำเนา 9:16 ของคลิปที่มี VTuber คนเดียวในห้อง (ไม่มีภาพเกม): ซูม V1 เต็มความสูง (3.1605) ไม่มีขอบดำ ใช้ preset `short` กับ overlay ตาม house-style และเสนอตำแหน่งกลางช่วงอกเป็นทางเลือกที่ต้องให้ผู้ใช้อนุมัติ
- เพิ่มสคริปต์ `overlay_place.py` ใน skill: วัดขอบเขต alpha ของ overlay เต็มเฟรมแล้วคำนวณ Zoom/Pan/Tilt (ค่าที่ได้ห่างจากค่าที่ render ตรวจแล้วของ Laffy 004 ไม่เกิน ~1%)
- ทดสอบ skill แบบ RED/GREEN ด้วย subagent: ก่อนมี skill แผนใส่ขอบดำ 528 px และเรียก `DuplicateTimeline` ผิด object; หลังมี skill แก้ได้ทั้งสองข้อ
- `vertical-video-reframing` ชี้ไปที่ skill ใหม่ และอธิบายสูตรวาง overlay เต็มเฟรม
- โปรไฟล์ Laffy เพิ่มหัวข้อ 9:16 ของ `Timeline 1_9x16` (ค่าการ์ดยังไม่ได้รับอนุมัติให้ใช้แทน `short`)

## v0.17.70 — อัปเดต Timeline หลัก KT404 67 อันและลบ Timeline สำรอง

### รายละเอียด
- อัปเดต timeline หลักของ KT404 Highlights 2026-10-1 ครบ 67 อัน (66 คลิป + pilot): ใช้เวอร์ชันที่ตัดต่อแล้วแทนต้นฉบับ ชื่อเดิม `{ชื่อคลิป}-{เกม}-vdo`
- ลบ timeline สำรองทั้งหมด (ต้นฉบับดิบ 67 อัน + สำเนา `_archived_v01` 2 อัน) ในคำสั่งเดียว เหลือ 67 timeline
- ตรวจอ่านกลับแล้ว: ชื่อตรงกับรายการเดิมทั้งหมด, ทุก timeline มี V1–V3 / A1–A3 / Subtitle 1, เนื้อหาในแต่ละ track ไม่เปลี่ยน
- จุดย้อนกลับ: `.hermes/kt404-hl1/batch/pre_promote.drp`

## v0.17.69 — สร้างไฮไลต์ KT404 66 คลิปใหม่จากช่วงที่ถูกต้อง

### รายละเอียด
- สร้าง timeline `_edit` ของ KT404 Highlights 2026-10-1 ใหม่ทั้ง 66 อัน เพราะชุดแรกดึงเสียง/ซับ/ซูมจากช่วงผิดของไลฟ์ (หาร `GetLeftOffset()` ด้วย 60 แทน 24)
- ถอดเสียงใหม่ผ่าน Descript ครบ 66 คลิป รวม 4,048 cue, ซูม 255, GIF 211, SFX 373; ทุกคลิปมีซับภาษาไทยแล้ว
- ตั้งระดับเสียงด้วยการจำลอง mix offline แล้วลดคลิปละ 0.4–3 dB; render ตัวอย่าง 3 คลิปวัดได้ตรงกับที่จำลองภายใน 0.1 LU, true peak -1.2 ถึง -1.7 dBTP
- ตรวจอ่านกลับครบ 66 timeline เทียบต้นฉบับและแผน ผ่านทั้งหมด; render QC 3 คลิปจำนวนเฟรมตรงแผน ไม่มีเฟรมดำ
- บันทึกบทเรียนใน OPERATING-NOTES: เวลาต้นทางบนโปรเจคที่ frame rate ต่างกัน, จำลอง mix แทนการ render, ลบ timeline จำนวนมากในคำสั่งเดียว (10 วิ แทน ~5 นาทีต่ออัน), หน่วยความจำ Resolve ระหว่าง batch ยาว

## v0.17.68 — Bunny Girl ep9 ปกคลิป

### รายละเอียด
- Bunny Girl ep9: ทำปก 16:9 (1920x1080) และ 9:16 (1080x1920) ตามแบบ ep4-ep6 hook สีแดง `คาแรกเตอร์แรก` + Bunny Girl, ภาพอวาตาร์ยิ้มสบตาที่ 0.6 วิ; ตรวจสระ/วรรณยุกต์และขนาดย่อแล้ว

## v0.17.67 — Bunny Girl ep9 แนวตั้ง ซูมเพิ่ม

### รายละเอียด
- Bunny Girl ep9 แนวตั้ง: เพิ่ม VTuber Zoom จาก 6 เป็น 17 จุด (1.1x กึ่งกลาง ปากไม่โดนซับ) สร้างใหม่ผ่าน DRT; track อื่นและสไตล์ซับไม่เปลี่ยน; render ทดสอบ v3 5499 เฟรม -15.8 LUFS ไม่มีเฟรมดำ

## v0.17.66 — Bunny Girl ep9 แนวตั้ง 9:16

### รายละเอียด
- Bunny Girl ep9 แนวตั้ง: สร้าง `Timeline 1_9x16` (1080x1920) พร้อมกราฟิก Pop Kinetic แนวตั้ง 5 ไฟล์ และซับ `Mitr-short-001` ใส่ผ่าน DRT ไม่ต้องปิด Resolve; render ทดสอบ 5499 เฟรม -15.8 LUFS ไม่มีเฟรมดำ
- กฎใหม่: ถ้าหน้าอวาตาร์อยู่ต่ำ ให้ซูม 1.1x แบบกึ่งกลางแทนการยึดขอบบน (แบบยึดขอบบนทำให้ซับทับปากทั้ง 6 จุดใน ep9)

## v0.17.65 — Bunny Girl ep9 อัปเดต Timeline หลัก

### รายละเอียด
- Bunny Girl ep9: ย้ายงานตัดต่อขึ้นเป็น `Timeline 1` ตามที่ผู้ใช้สั่ง และลบ timeline สำรอง 2 อันด้วย ID (ตรวจทุก track ตรงกับก่อนเปลี่ยน, สำรอง `.drp` ไว้ก่อนลบ)

## v0.17.64 — Katy404 ep9 คง layout เดิม

### รายละเอียด
- โปรไฟล์ Katy404: บันทึกว่าผู้ใช้เลือกคง layout ของ Bunny Girl ep9 (คำกระแทกล่างซ้าย การ์ดรูปซ้ายบน) การแก้ของ ep6 ไม่ใช่กฎของทั้งซีรีส์

## v0.17.63 — Bunny Girl ep9 + โหลดซับ preset ผ่าน DRT

### รายละเอียด
- ตัดต่อ Bunny Girl ep9 "จากคาแรกเตอร์ปกติสู่ Bunny Girl" (Katy404) เป็น `Timeline 1_pop` แบบ Pop Kinetic: แบ่ง 4 บทพร้อมการ์ด CHAPTER และช่วงเงียบ 1.6 วิ, ซูม VTuber 6 จุด, กราฟิกคำกระแทก/การ์ดรูป/ป้าย/เช็กลิสต์ 5 ไฟล์, ซับไทย 75 cue, SFX 41 จุด, BGM; `Timeline 1` ต้นฉบับไม่ถูกแตะ
- render ทดสอบ 5499 เฟรม 1080p60 ซับ burn-in -15.8 LUFS peak -0.5 dBFS ไม่มีเฟรมดำ
- เพิ่ม `scripts/drt_set_subtitle_preset.py`: ใส่ Subtitle preset ที่บันทึกไว้ (เช่น `Mitr Font`) ผ่าน DRT โดยไม่เขียน database และไม่ต้องปิด/เปิด Resolve ทดสอบจริงบน ep9 ได้ style ตรงไบต์ พร้อม test 4 ข้อ
- บันทึกกฎใหม่ใน OPERATING-NOTES (path DRT ต้องเป็น absolute, จำนวนเฟรม MOV alpha จาก HyperFrames, Python 3.12 บนเครื่องนี้) และอัปเดต house-style / thai-subtitles-resolve / โปรไฟล์ Katy404

## v0.17.62 — Laffy 004 จัดแทร็กให้ถูกชื่อ

### รายละเอียด
- Laffy 004: ย้ายฟุตเทจกลับ V1 และเสียงพูดกลับ A1 ให้ตรงชื่อแทร็ก ตำแหน่งและค่าทุกอย่างเหมือนเดิม (render เฟรมเทียบแล้วเหมือนกันทุกพิกเซล) และลบ timeline สำรอง เหลือ Timeline 1 ตัวเดียว
- บันทึกวิธีย้ายคลิปข้ามแทร็กผ่าน DRT ใน OPERATING-NOTES

## v0.17.61 — Laffy 004 render v5

### รายละเอียด
- render คลิป Laffy 004 ใหม่เป็น `laffy004_Underworld_Goddess_v5.mp4` ด้วยซับที่ปรับเวลาตามเสียงแล้ว (1080p30, -14.2 LUFS, peak -0.7 dBFS, ตรวจเฟรมช่วงเงียบและช่วงพูดแล้ว)

## v0.17.60 — Laffy 004 ปรับเวลาซับให้ตรงเสียง

### รายละเอียด
- ปรับเวลาซับไทย Laffy 004 ทั้ง 117 cue ให้ขึ้นตรงช่วงที่พูดจริง (เช่น `มาเป็น` จาก 26.43 เป็น 27.00 วิ) ข้อความและสไตล์ Mitr Font เหมือนเดิม แทร็กอื่นไม่เปลี่ยน ตรวจเฟรมที่ render แล้ว
- บันทึกวิธีปรับเวลาซับด้วย speech map + จุดยึดจากผู้ใช้ และข้อจำกัดว่าช่วงหยุดระหว่างวลีที่จำนวนพยางค์เท่ากันตัดสินจากเสียงอย่างเดียวไม่ได้

## v0.17.59 — Laffy 004 render คลิป

### รายละเอียด
- render คลิป Laffy 004 แล้ว: `laffy004_Underworld_Goddess_v4.mp4` (1920x1080 30fps ซับ burn-in, -14.2 LUFS, peak -0.72 dBFS)
- ลดเสียง boom ของการ์ด Kaiju เหลือ -24 dB เพราะไฟล์ render จริง peak -0.01 dBFS ทั้งที่ mix offline คาดไว้ -0.71
- ย่อและขยับรูปการ์ดใบเดี่ยว (สูง 820 px, cx 1600/320) ให้ห่างซับอย่างน้อย 65 px
- บันทึกกฎ: ตรวจ peak จากไฟล์ render จริง และวัดระยะซับกับการ์ดจากเฟรมที่ render

## v0.17.58 — Laffy 004 เหลือ Timeline หลักตัวเดียว

### รายละเอียด
- คลิป Laffy 004: งานตัดเสร็จเป็น `Timeline 1` timeline เดียวในโปรเจกต์ ลบ timeline สำรอง 7 ตัวและโฟลเดอร์ Archive ที่ว่างแล้ว (มี .drp สำรองก่อนลบ)
- โปรไฟล์ Laffy บันทึกสถานะโปรเจกต์ล่าสุดและไฟล์สำรองสำหรับย้อนกลับ

## v0.17.57 — Laffy 004 แก้ชื่อเป็นลาฟฟี่

### รายละเอียด
- คลิป Laffy 004 แก้ซับชื่อช่องเป็น "ลาฟฟี่ครับ" แล้วใน timeline `Underworld Goddess_edit_mitr` (สไตล์ Mitr Font ซูม การ์ด และเสียงยังครบ ตรวจภาพที่ render แล้ว)
- บันทึกวิธีแก้ข้อความซับทีละ cue ผ่าน DRT เพราะ `set_name` ของ MCP ใช้กับซับไม่ได้
- โปรไฟล์ Laffy: ชื่อในซับไทยใช้ "ลาฟฟี่"

## v0.17.56 — Laffy 004 ซับ Mitr Font

### รายละเอียด
- คลิป Laffy 004 ใส่ซับสไตล์ `Mitr Font` แล้วใน timeline `Underworld Goddess_edit_mitr` (ซับ 117 cue, ซูม, การ์ด และเสียงตรงกับต้นทางทุกแทร็ก)
- `drt_clone_subtitle_style.py` คงชื่อ Subtitle track เดิมของ timeline ต้นทาง ไม่ใช้ชื่อจาก DRT อ้างอิง (ไม่ได้รัน test ตามที่ผู้ใช้สั่ง)
- อัปเดตโปรไฟล์ Laffy และ skill ซับไทย: ผู้ใช้อนุมัติให้ใช้ Mitr Font จาก DRT ของ Katy404 ep6

## v0.17.55 — Laffy 004 รูปการ์ดเด้งและซับ Descript

### รายละเอียด
- เพิ่ม `scripts/card_pop_overlay.py` ทำรูปการ์ดของผู้ใช้เป็น MOV โปร่งใสแบบเด้งเข้า/ค้าง/จางออก มีเงา และเรียงหลายใบเป็นพัดได้ ใช้วางรูปการ์ด 4 ชุดในคลิป Laffy 004 ตรงเฟรมทุกชุด
- เพิ่ม test ของ `card_pop_overlay.py` (รันผ่าน 4/4 ตอนสร้าง ส่วนรอบนี้ข้ามการรัน test ทั้งชุดตามที่ผู้ใช้สั่ง)
- อัปเดตโปรไฟล์ช่อง Laffy: ที่เก็บงาน, โปรเจกต์ Resolve, แผนผังแทร็ก 16:9, ตำแหน่งการ์ด, ระดับเสียง
- เพิ่มบันทึกใน OPERATING-NOTES: Media Pool ของไฟล์เสียงคืนค่า Frames ว่าง, เช็ก peak ด้วยการ mix offline ก่อนวาง SFX/BGM, กู้ Resolve ที่ค้างข้ามคืน
- thai-subtitles-resolve: Descript ไม่มีภาษา th ให้ใช้ auto และวิธีแบ่งซับด้วยมือตาม speech map
- illustration-assets: layout และจังหวะการวางรูปการ์ดสำหรับ VTuber ที่อยู่กลางเฟรม

## v0.17.54 — Armigon ปกลบตัวจิ๋วสีม่วง

### รายละเอียด
- Armigon Shorts 2026-10: ลบสัตว์เลี้ยงจิ๋วสีม่วงออกจากโมเดลบนปกทั้ง 96 ใบ (แนวนอน 48 + แนวตั้ง 48) หน้ายังใหญ่เท่าเดิม ตรวจครบ

## v0.17.53 — Armigon ปกโมเดล Live2D พื้นหลังไม่มีตัวละคร

### รายละเอียด
- Armigon Shorts 2026-10: ปกทั้ง 96 ใบ (แนวนอน 48 + แนวตั้ง 48) เปลี่ยนตัวละครเป็นโมเดล Live2D จาก VTube Studio เลือกสีหน้าตามอารมณ์ของแต่ละปก
- พื้นหลังปกไม่มีตัวละคร: ตัด mascot/chibi ของไลฟ์ออก และ Debut 21-24 ใช้ฉากถ้ำว่าง
- skill `vtuber-cover-batch-pipeline`: วิธีใช้ภาพ VTS เต็มเฟรมและตัดตัวละครจากพื้นหลัง

## v0.17.52 — Armigon ปกแนวตั้ง 48 ใบ

### รายละเอียด
- Armigon Shorts 2026-10: ทำปกแนวตั้ง 1080×1920 ครบ 48 ใบ (`<ชื่อ timeline>_9x16.jpg` ในโฟลเดอร์ vdo) ตรวจขนาด/จำนวนครบ
- skill `vtuber-cover-batch-pipeline`: กับดัก engine agent-thumbnail จัดข้อความกลางแล้วตัดท้ายคำบน Shorts พร้อมวิธีแก้โดยไม่แตะ repo นั้น

## v0.17.51 — Armigon แนวตั้ง ซับ Mitr-short-001

### รายละเอียด
- Armigon Shorts 2026-10: ใส่ preset ซับ `Mitr-short-001` ให้ timeline แนวตั้งครบ 48 อัน (2,405 cue ไม่เปลี่ยน, ตรวจซ้ำตรงทั้ง 48)
- `load_subtitle_preset_auto`: รอ Resolve ปิดได้นานขึ้นเป็น 240 วินาที (โปรเจกต์ 96 timeline ปิดเกิน 90 วินาที)

## v0.17.50 — Armigon Shorts 2026-10 แนวตั้ง 48 คลิป

### รายละเอียด
- Armigon Shorts 2026-10: สร้าง timeline แนวตั้ง `_9x16` ครบ 48 อัน (เกมบน/Armigon ล่าง; Debut 21/23/24 โมเดลเต็มจอ, 22 สไลด์บน+โมเดลล่าง) ตรวจโครงสร้างครบ 48 อัน (1080×1920, ความยาว, เสียง, ซับตรงต้นฉบับ) ยังไม่ render รอผู้ใช้ QC
- ปกคลิป 48 ใบ: แก้เวลาเฟรมพื้นหลังที่ผิด (`GetLeftOffset` เป็นเฟรม timeline 24 fps) แล้ว build ทับครบ
- skill `resolve-edit`: กับดัก MCP `duplicate_clips` คัดลอกผิดความยาวเมื่อ fps ไม่ตรง และ `_archived_v01` ที่ MCP สร้างเอง
- skill `vtuber-cover-batch-pipeline`: แก้สูตรแปลงเวลาเฟรมให้ถูกต้อง

## v0.17.49 — ซับ Mitr Font บน pilot KT404 2026-10-1

### รายละเอียด
- ใส่สไตล์ซับ `Mitr Font` ให้ pilot `มอนเมินจนคนเหนื่อยเอง-Monster Hunter World-vdo_edit` ด้วย `load_subtitle_preset_auto --apply` (ผู้ใช้อนุมัติ) หลังโหลดผ่าน UI สองครั้งแล้วไม่ติด; ตรวจ `already_matches=True`, ซับ 72 cue, track และระดับเสียงทั้งหมดอ่านกลับตรงเดิม
- render ไฟล์รีวิวใหม่ `มอนเมินจนคนเหนื่อยเอง_pilot_mitr_2026-11-11.mov`: ซับ Mitr มีขอบดำ, 3736 เฟรม, -16.7 LUFS, peak -0.7 dBFS, ไม่มีเฟรมดำ
- เพิ่มกฎใน OPERATING-NOTES: หลังผู้ใช้โหลด preset ซับใน UI ให้ตรวจด้วย dry run และ render สั้นก่อนเสมอ ถ้าไม่ติดให้ใช้ DB patch

## v0.17.48 — Pilot ไฮไลต์ KT404 2026-10-1

### รายละเอียด
- ตัดต่อ pilot ของโปรเจกต์ KT404 Highlights 2026-10-1: timeline ใหม่ `มอนเมินจนคนเหนื่อยเอง-Monster Hunter World-vdo_edit` มีซับไทย 72 cue (จาก Descript), VTuber Zoom 6 ช่วง (2.2x), GIF 5 ตัว (ค่า vdo), SFX 9 จุด, BGM และปรับระดับเสียง; timeline ต้นฉบับไม่ถูกแก้
- ไฟล์ทดสอบ render ผ่านการตรวจ: 3736 เฟรม, -16.7 LUFS, peak -0.7 dBFS, ไม่มีเฟรมดำ
- บันทึกกฎใหม่ใน OPERATING-NOTES: ห้ามเปิดโปรเจกต์อื่นเพื่อยืมสไตล์ซับ (ทำให้ Resolve ค้าง) ให้ใช้ cue จาก CreateSubtitlesFromAudio เป็นแม่แบบแทน, คำนวณความยาว GIF จาก FPS ใน Media Pool (25/50), MCP export_project ใช้กับโปรเจกต์ที่เปิดอยู่ไม่ได้, ใช้ `.venv` ของ repo บนเครื่อง pc-server
- อัปเดตโปรไฟล์ช่อง Katy404 ด้วยข้อมูลโปรเจกต์ 2026-10-1 (timeline 24 fps, 67 timeline) และคำที่ต้องฟังยืนยัน

## v0.17.47 — อัปเดต MCP เป็น 5.2.1

### รายละเอียด
- อัปเดต MCP ชุมชน `davinci-resolve` จาก 4.19.3 เป็น 5.2.1 (ตัวตรวจรายงาน UP-TO-DATE)
- `docs/SKILL.md`: ตั้งแต่ v5.0.0 `apply_spec` ไม่รัน spec hooks แล้ว (`run_hooks=true` ถูกปฏิเสธด้วย `SPEC_HOOKS_NOT_RUN`)

## v0.17.46 — Armigon Shorts 2026-10 ปกคลิป

### รายละเอียด
- Armigon Shorts 2026-10: ทำปกแนวนอน 16:9 ครบ 48 timeline เก็บใน `G:\My Drive\Projects\Armigon\2026-10\vdo` (ตรวจแล้ว 1920×1080, < 2 MB, ชื่อไฟล์ตรง timeline)
- โปรไฟล์ Armigon: บันทึกวิธีเลือกเฟรมและกับดักฉากโหลด/สไลด์ Debut
- skill `vtuber-cover-batch-pipeline`: เพิ่มกับดักคลิปที่เป็นสไลด์ทั้งคลิป และสูตรแปลงเฟรม timeline 24 fps → source 60 fps

## v0.17.45 — Export คลิปน้ำท่วม Aomi-mama 6 คลิป

### รายละเอียด
- Export คลิปอัปเดตน้ำท่วม Aomi-mama ทั้ง 6 ตัวไปที่ Drive `drive-download-20261106T181323Z-1-001/vdo` ชื่อ `วันที่ 01 __ อัปเดตน้ำท่วม 29-09-2026` ถึง `วันที่ 06 __ อัปเดตน้ำท่วม 22-10-2026` ด้วย preset `H.264 Master` (.mov 1920x1080 60p)
- ตรวจด้วย ffprobe แล้ว: จำนวนเฟรมวิดีโอตรงกับ timeline ทุกไฟล์ มีเสียง AAC 48 kHz stereo ความยาวเท่ากัน; ดูเฟรมตัวอย่างช่วงซูมและกลางคลิป 12 เฟรม ไม่มีขอบดำ
- บันทึกใน OPERATING-NOTES ว่าเมื่อมีหน้าต่าง dialog ค้างหลัง render (page เป็น None) Resolve จะลบงาน render ไม่ได้ ต้องให้ผู้ใช้ปิดก่อนแล้วตรวจคิวซ้ำ

## v0.17.44 — ย้ายปกน้ำท่วม Aomi-mama ไปโฟลเดอร์ vdo

### รายละเอียด
- ย้ายปกน้ำท่วม Aomi-mama ทั้ง 6 ใบพร้อม manifest.json ไปไว้ที่ Drive `drive-download-20261106T181323Z-1-001/vdo` ตามที่ผู้ใช้สั่ง ตรวจแล้วว่าไฟล์ครบและขนาดเท่าเดิม
- อัปเดตสคริปต์ทำปกและโปรไฟล์ช่อง Aomi-mama ให้ใช้โฟลเดอร์ใหม่

## v0.17.43 — ปกน้ำท่วม Aomi-mama ย่อป้ายวันที่

### รายละเอียด
- ปกน้ำท่วม Aomi-mama: ย่อป้าย "วันที่ N" มุมล่างซ้ายเหลือราว 70% ของขนาดเดิม ทับไฟล์ปกทั้ง 6 ใบใน Drive และ manifest แล้ว ตรวจ contact sheet แล้ว

## v0.17.42 — ปกน้ำท่วม Aomi-mama ป้ายวันที่ล่างซ้าย

### รายละเอียด
- ปกน้ำท่วม Aomi-mama: ย้ายป้าย "วันที่ 1-6" ไปมุมล่างซ้าย และตกแต่งเป็น badge ธีมน้ำ (กล่องมนสีฟ้า ขอบขาว คลื่นน้ำ เลขสีเหลืองใหญ่ เอียงเล็กน้อยพร้อมเงา)
- บรรทัดขาวกลับเป็น "อัปเดตน้ำท่วม <วันที่>"; ทับไฟล์ปกทั้ง 6 ใบใน Drive และ manifest แล้ว ตรวจขนาด 1920x1080 และ contact sheet แล้ว
- บันทึกรูปแบบป้ายวันที่ไว้ในโปรไฟล์ช่อง Aomi-mama

## v0.17.41 — ปกน้ำท่วม Aomi-mama ไม่เบลอ + เลขวันที่

### รายละเอียด
- ปกอัปเดตน้ำท่วม Aomi-mama ทั้ง 6 ใบ เปลี่ยนเป็นพื้นหลังไม่เบลอ (หรี่แสงเล็กน้อย + ไล่เฉดด้านซ้ายให้อ่านตัวหนังสือง่าย) ทับไฟล์เดิมใน Drive และ manifest แล้ว
- ปก 29-09, 13-10, 16-10, 22-10 ใช้ภาพห้องจากเฟรม 04-10 เพราะเมื่อไม่เบลอจะเห็นอวาตาร์ใน stream ซ้อนกับโมเดลเป็นสองตัว
- บันทึกวิธีทำปกพื้นหลังไม่เบลอและกับดักอวาตาร์ซ้อนไว้ใน skill vtuber-cover-batch-pipeline และโปรไฟล์ช่อง Aomi-mama
- เพิ่มคำว่า "วันที่ N" บนปกตามลำดับคลิป (29-09 = วันที่ 1 ถึง 22-10 = วันที่ 6) โดยมีวันที่ปฏิทินอยู่บรรทัดใต้

## v0.17.40 — ปกคลิปอัปเดตน้ำท่วม Aomi-mama 6 วัน

### รายละเอียด
- ปก Aomi-mama อัปเดตน้ำท่วม 6 วัน (1920x1080) hook แดงจากคำภาพประกอบ + บรรทัด "อัปเดตน้ำท่วม <วันที่>" สไตล์เดียวกับปก 2026-10 วางที่ Drive `น้ำถ่วม-2026/covers/` พร้อม manifest
- vtuber-cover-batch-pipeline: ต้อง import `text_thai` ของ agent-thumbnail ก่อน Pillow ไม่งั้น libraqm ไม่ทำงานและสระ/วรรณยุกต์ไทยเพี้ยน; วิธีวางโมเดลใหญ่ไม่มีขอบขาวสำหรับปกคุย Aomi-mama

## v0.17.39 — Timeline น้ำท่วม Aomi-mama ใช้ footage เต็ม + ซูม VTuber

### รายละเอียด
- Aomi-mama น้ำท่วม 6 วัน: ทำ timeline หลักใหม่ใช้ footage เต็มไฟล์ตั้งแต่เฟรม 0 ไม่ตัด ไม่มี hook; มี VTuber Zoom ตามช่วงที่วิเคราะห์ไว้ 3-5 ช่วงต่อวัน และการ์ดวันที่ + ภาพประกอบอธิบาย ตรวจย้อนกลับผ่านทุกวัน
- ลบ timeline สำรอง (`_old`, `_base`, `_zoom`) หลังสำรอง `pre_fullclip.drp` / `pre_fullclip_zoom.drp` เหลือ 1 timeline ต่อโฟลเดอร์
- house-style: คลิปอัปเดตแบบเต็มเทคใช้ไฟล์ทั้งหมด ไม่ใส่ hook ใส่ซูม/ภาพประกอบทับด้านบนเท่านั้น
- OPERATING-NOTES: ต้องตั้ง `PYTHONIOENCODING=utf-8` เมื่อส่งชื่อไทยผ่าน Git Bash ไม่งั้นได้โฟลเดอร์ชื่อเพี้ยน
- แก้ขอบขวาดำในช่วงซูม 04-10 และ 08-10: ลดจุดกึ่งกลางซูม cx 0.68 -> 0.65 (ขีดจำกัด 1 - h/2) ทำ timeline ใหม่ ตรวจ preview ไม่มีขอบดำ
- OPERATING-NOTES: กฎขีดจำกัด `window_cx` และตรวจขอบดำทุกช่วงซูมหลังเรนเดอร์

## v0.17.38 — จัด Timeline น้ำท่วม Aomi-mama วันละโฟลเดอร์

### รายละเอียด
- ลบ Timeline เดิมทั้ง 21 อันในโปรเจกต์ `น้ำถ่วม-2026` (สำรอง .drp ก่อนลบ) แล้วทำใหม่ 6 วัน วันละ 1 โฟลเดอร์ใน Media Pool เหลือเฉพาะ Timeline สุดท้าย; ตรวจย้อนกลับซูม ภาพประกอบ และแทร็กเดิมผ่านทุกวัน
- บันทึกกฎใน OPERATING-NOTES: ตั้งโฟลเดอร์ปัจจุบันก่อนสร้าง/นำเข้า/duplicate timeline และตั้งชื่อไฟล์ DRT ใหม่ทุกครั้งที่ทำซ้ำ

## v0.17.37 — Timeline อัปเดตน้ำท่วม Aomi-mama ครบ 6 วัน

### รายละเอียด
- สร้าง Timeline อัปเดตน้ำท่วม Aomi-mama ครบ 6 วัน (29-09 ถึง 22-10) ในโปรเจกต์ `น้ำถ่วม-2026`: คลิปเต็มไม่ตัดช่วงเงียบ มี hook, การ์ดวันที่, VTuber Zoom และภาพประกอบ HyperFrames; render preview และ QC ภาพผ่านทุกวัน
- แก้ `scripts/asr_words_th.py` ให้ใช้กับ PyAV 19 ได้ (ถอดรหัส WAV เอง) และหา DLL CUDA จาก pip wheel ได้ พร้อมเทสต์ใหม่
- house-style: ไม่ตัดช่วงเงียบ เว้นแต่ผู้ใช้สั่ง
- บันทึกเลย์เอาต์และกรอบซูมของช่อง Aomi-mama และกับดักใหม่ 4 ข้อใน OPERATING-NOTES

## v0.17.36 — Bunny Girl ep6 ปกคลิป

### รายละเอียด
- Bunny Girl ep6: ทำปก 16:9 และ 9:16 (hook "แต่งชุดยังไง?" + Bunny Girl, ภาพอวาตาร์ 13.0 วิ) แบบเดียวกับ ep4/ep5 บันทึกในโฟลเดอร์ Thumbnail

## v0.17.35 — Bunny Girl ep6 แก้ตาม QC และแนวตั้ง

### รายละเอียด
- Bunny Girl ep6: แก้ตามที่ผู้ใช้สั่งทีละจุดจนผู้ใช้ยืนยันว่าโอเคทั้งหมด (ลบคำกระแทก 6 จุดพร้อมเสียง pop, เพิ่ม/ย้ายการ์ดรูปประกอบไปมุมขวาบน, การ์ดรวม 7 ชิ้น, ลดขนาดรายการท้ายคลิป, เปลี่ยนหัวข้อการ์ด INTRO, เพิ่มซูม VTuber 2 ช่วง)
- ทำแนวตั้ง 9:16 `Timeline 1_9x16_mitr`: ครอปที่หน้า ซูม 1.1x 13 ช่วง กราฟิกแนวตั้ง 10 ไฟล์ ซับ `Mitr-short-001` ทุก track ตรงกับต้นฉบับ (ยังไม่ render รอผู้ใช้ QC)
- บันทึกวิธีทำงานแบบแก้ทีละจุดเร็วๆ ไม่ render ทดสอบ

## v0.17.34 — Bunny Girl ep6 สติกเกอร์กระต่ายง่วง

### รายละเอียด
- Bunny Girl ep6: เปลี่ยนภาพสติกเกอร์ "กระต่ายง่วง" เป็นภาพกระต่ายหูตกหลับตา (Zzz) และเอาคำกระแทก "พับลง = ง่วงนอน" ออกพร้อมเสียง pop ตามที่ผู้ใช้สั่ง; สลับ `ch02.mov` เป็น `ch02b.mov` ที่ตำแหน่งเดิม track อื่นไม่เปลี่ยน
- พบว่า render เต็มล้มที่ 00:00:17:10 จาก zoom clip ที่ถูกยืดหัว (กับดัก row 77) รอผู้ใช้อนุมัติให้สร้าง track ซูมใหม่

## v0.17.33 — Bunny Girl ep6 การ์ด INTRO ขึ้น Timeline หลัก

### รายละเอียด
- Bunny Girl ep6: ย้าย `Timeline 1_intro_wipe` (มีการ์ด INTRO "ครบเซต 7 ชิ้น") ขึ้นเป็น `Timeline 1` ตามที่ผู้ใช้อนุมัติ; เหลือ timeline เดียว ทุก track ตรงกับก่อนเปลี่ยนชื่อ; จุดย้อนกลับ `pre_promote_intro.drp`

## v0.17.32 — Bunny Girl ep6 การ์ดเปลี่ยนฉาก INTRO

### รายละเอียด
- เพิ่มการ์ดเปลี่ยนฉาก INTRO "ครบเซต 7 ชิ้น" ใน Katy404 Bunny Girl ep6 พร้อมช่องเงียบ 1.6 วินาทีที่ 00:00:16:27 และเสียง whoosh
- สร้างเป็น Timeline ใหม่ `Timeline 1_intro_wipe` โดย `Timeline 1` ไม่ถูกแตะ และตรวจเทียบแล้วมีความต่าง 0 รายการ (ส่วนเพิ่มคือฟิลเลอร์ การ์ด และ whoosh เท่านั้น)
- บันทึกกับดัก DRT: คลิปที่เริ่มที่ source frame 0 จะมีแท็ก `<In>` ว่าง (ไม่ใช่ "0") ต้องตีความว่าเป็น 0
- render ทดสอบ `Bunny Girl ep6_POP_intro_test_2026-11-08.mp4`: 8180 เฟรม, -15.9 LUFS, peak -0.8 dBFS, ไม่มีเฟรมดำ, ช่องว่างใต้การ์ดเงียบ (-29.4 dB), ซับ Mitr ยังอยู่ครบ

## v0.17.31 — Bunny Girl ep6 ขึ้น Timeline หลัก

### รายละเอียด
- Bunny Girl ep6: ย้ายงานตัดต่อขึ้นเป็น `Timeline 1` (timeline เดียวในโปรเจกต์ ทุก track ตรงกับก่อนเปลี่ยนชื่อ) และลบ timeline สำรอง 3 อันตามที่ผู้ใช้สั่ง; จุดย้อนกลับ `pre_promote.drp`

## v0.17.30 — ตัดต่อ Bunny Girl ep6 (16:9 test)

### รายละเอียด
- Katy404 Bunny Girl ep6 "แต่งชุดบันนี่เกอร์ได้ยังไง": ทำ `Timeline 1_pop_mitr` แบบ Pop Kinetic 16:9 (การ์ด CHAPTER 01–07 ตามชิ้นชุด 7 ชิ้น, slam 47, การ์ดภาพ 10, ซูม 8 ช่วง, ซับไทย 125 cue `Mitr Font`, SFX/BGM) โดยไม่แตะ `Timeline 1`
- ซับไทยใช้ข้อความจาก Descript ตามที่ผู้ใช้สั่ง (หยุด Whisper ในเครื่อง) แล้วจับเวลาจากแผนที่ช่วงเงียบ
- render ทดสอบ `Bunny Girl ep6_POP_test_v2_2026-11-08.mp4`: 8084 เฟรม, -15.9 LUFS, peak -1.1 dBFS, ไม่มีเฟรมดำ, ช่องว่างก่อนการ์ด CHAPTER เงียบทุกช่อง
- house-style 0.3.2 / thai-subtitles-resolve 0.5.1: ใช้ Descript เป็นค่าเริ่มต้นแม้คลิปสั้น และลดเฉพาะ SFX ตัวที่ทำ peak เกิน

## v0.17.29 — Render ไฮไลต์ Hoshi_1489 ครบ 30 Timeline

### รายละเอียด
- Render และส่งออกคลิปไฮไลต์ Hoshi_1489 (2026-10-1) ครบทั้ง 30 Timeline ลงโฟลเดอร์ `G:\My Drive\Projects\Hoshi_1489\2026-10-1\footer`
- ใช้ DaVinci Resolve Python Scripting API ควบคุมการ Render ต่อเนื่องด้วย Preset `H.264 Master` (1920x1080@60fps)
- ตรวจสอบคุณภาพไฟล์ผ่าน QC ด้วย `ffprobe` ครบถ้วนทั้ง 30 ไฟล์ (ขนาดรวม 8.85 GB, ความยาวรวม 32 นาที 22 วินาที) ยืนยัน Video Stream (H.264), Audio Stream (AAC) และความยาวตรงกับ Timeline
- บันทึกบทเรียนการรอ Background Indexing สำหรับโปรเจกต์ขนาดใหญ่ (17.3 ชั่วโมง) และขั้นตอน Batch Render ตรงสู่ Google Drive ลงใน `docs/OPERATING-NOTES.md`

## v0.17.28 — ไฮไลต์ 30 Timelines สำหรับ Hoshi_1489 2026-10-1

### รายละเอียด
- วิเคราะห์ฟุตเทจดิบ 5 ไฟล์ของช่อง Hoshi_1489 รวม 17 ชม. 29 นาที จาก `G:\My Drive\Projects\Hoshi_1489\2026-10-1`
- คัดเลือกไฮไลต์ที่น่าสนใจ 30 คลิป (คลิปละประมาณ 36-96 วินาที) ครอบคลุม 3 หมวด: ช่วงเล่นเกม (gameplay), ช่วงสนุกสนาน (fun), และช่วง meme
- สร้าง 30 Timelines ใน DaVinci Resolve Studio โปรเจกต์ `hoshi-2026-10-1` (ใน Project Library `Google_drive`, โฟลเดอร์ `hoshi_1489`) ตามรูปแบบชื่อ `{ชื่อคลิป}-{ชื่อเกม}-vdo`
- ตรวจสอบความถูกต้องระดับเฟรม (Frame-accurate): 28 Timelines ตรงเป๊ะ 100%, 2 Timelines มีการปัดเศษของ Resolve 21.1 API ที่ source start 1 เฟรมแต่ความยาวคลิปตรงเป๊ะตาม Rule 55
- เพิ่มโปรไฟล์ช่อง `docs/channels/hoshi-1489.md` พร้อมบันทึกข้อค้นพบและข้อจำกัดของ Google Drive latency
- แก้ไข `scripts/highlight/briefs.py` ให้ใช้ `sys.base_prefix` เพื่อป้องกันการอ้างอิง `.venv` ใน subagent briefs
- ผ่านการทดสอบชุดใหญ่ 424 tests (รวม 74 highlight pipeline tests) 100%

## v0.17.27 — ปก Bunny Girl ep5 ได้รับอนุมัติ

### รายละเอียด
- Bunny Girl ep5: ผู้ใช้อนุมัติข้อความปก "วันแรกที่ใส่ชุด / Bunny Girl" ตามเดิม บันทึกในโปรไฟล์ Katy404 ว่าปกเป็นฉบับสุดท้ายแล้ว

## v0.17.26 — ปก Bunny Girl ep5

### รายละเอียด
- Bunny Girl ep5: ทำปก 16:9 และ 9:16 (ข้อความ "วันแรกที่ใส่ชุด" แดง + "Bunny Girl", เฟรม 0.4 วิ) เก็บไว้ที่โฟลเดอร์ Thumbnail ของตอน
- บันทึกในโปรไฟล์ Katy404: hook ที่ยาวกว่า ep4 ต้องลดขนาดตัวอักษร (128/142 px) ไม่งั้นชนหูกระต่ายและขอบจอ และ hyperframes 0.8.197 บันทึก snapshot ไว้ใน .hyperframes/artifacts/snapshots

## v0.17.25 — Bunny Girl ep5 แนวตั้ง

### รายละเอียด
- Bunny Girl ep5 แนวตั้ง: สร้าง Timeline 1_9x16_mitr (1080x1920) ซับ Mitr-short-001 ด้วย drt_clone_subtitle_style, render ทดสอบ 2440 เฟรม -15.6 LUFS ไม่มีเฟรมดำ
- แก้ drt_clone_subtitle_style ให้แปลง --workdir เป็น path เต็ม (Timeline.Export ล้มเหลวเมื่อได้ path แบบ relative)
- skill resolve-mitr-subtitle-presets: ระบุไฟล์ DRT อ้างอิงของ Mitr Font (16:9) และ Mitr-short-001 (9:16)

## v0.17.24 — ใส่ฟอนต์ซับ Mitr โดยไม่ปิด Resolve

### รายละเอียด
- เพิ่มสคริปต์ scripts/drt_clone_subtitle_style.py (พร้อม test): ใส่สไตล์ซับแบบ track เช่น Mitr Font โดย clone track จาก DRT อ้างอิงแล้ว import เป็น timeline ใหม่ Resolve เปิดค้าง ไม่เขียน Project.db
- บันทึกว่า MCP timeline_ai set_subtitle_preset ใช้ได้เฉพาะ preset แบบ animation จึงปฏิเสธ Mitr Font ("No animation preset") ใน house-style และ skill resolve-mitr-subtitle-presets
- Bunny Girl ep5: สร้าง Timeline 1_pop_mitr ซับเป็น Mitr Font ทุก track/gain/fade ตรงกับ Timeline 1_pop, render ทดสอบ 2440 เฟรม -15.6 LUFS ไม่มีเฟรมดำ

## v0.17.23 — Bunny Girl ep5 และกฎ ASR บน GPU ที่ไม่ว่าง

### รายละเอียด
- บันทึกงาน Bunny Girl ep5 "วันแรกที่ตัดสินใจว่าจะใส่ชุดบันนี่เกอร์" ในโปรไฟล์ Katy404: Timeline 1_pop (ซูม 6 ช่วง, Pop Kinetic 3 ส่วน, ซับ 48 cue, SFX/BGM) และผล render ทดสอบ 2440 เฟรม -15.6 LUFS peak -1.0 dBFS ไม่มีเฟรมดำ
- เพิ่มกฎใน OPERATING-NOTES: เมื่อเกม/OBS ใช้ GPU เกือบเต็ม ให้รัน faster-whisper บน CPU int8 พร้อม HF_HUB_OFFLINE=1
- เพิ่มกฎใน OPERATING-NOTES: heredoc ของ Bash tool เปลี่ยน backslash-n เป็นขึ้นบรรทัดจริง ให้ใช้ chr(92) หรือ Edit tool

## v0.17.22 — แก้อ้างอิงสคริปต์ Sakuyako ที่หายไป

### รายละเอียด
- `docs/channels/sakuyako-cheris.md`: ระบุว่าสคริปต์ `sk06_bands.py`, `sk06_9x16_layoutA.py`, `sk06_layoutA_qc.py` เป็น scratch ครั้งเดียวที่ไม่ได้เก็บไว้ (ไม่มีในเครื่องและไม่เคย commit)
- `test_channel_profiles` ผ่านครบ 3 ตัว; `test_skill_bundle` ผ่าน

## v0.17.21 — นำ skill เข้าโปรเจกต์ + กฎอัปเดต skill เดิม

### รายละเอียด
- นำ skill ที่เขียนเองเข้าโปรเจกต์ 5 ตัวจาก `~/.agents/skills`: `katy404-canva-thumbnails`, `kt404-youtube-upload`, `sfx-library-manager`, `sfx-story-analyzer`, `subtitle-analyzer`
- รวมกฎที่ไม่ซ้ำของ `davinci-resolve-workflow` เข้า `resolve-mcp/references/target-resolution.md` (resolve-mcp 0.4.0) แทนการสร้าง skill ซ้ำ
- `project-learning` 0.2.0: skill ต้องอยู่ใน `.agents/skills` ของ repo เท่านั้น; ถ้ามี skill เดิมครอบคลุมให้อัปเดตตัวเดิมและเพิ่ม `version` ก่อนคิดสร้างใหม่; ก่อนลบโฟลเดอร์ที่ gitignore ให้ค้นการอ้างอิงก่อน (AGENTS.md เพิ่มกฎเดียวกัน)
- `verify_skill_bundle` รู้จักลิงก์ `references/` ข้าม skill ของ HyperFrames และลิงก์โฟลเดอร์ ทำให้ test validation 3 ตัวที่เคยพังผ่านแล้ว
- test QC เสียง/ซับของ Armigon ข้ามอัตโนมัติเมื่อไฟล์หลักฐานใน `.agents/teamwork` (gitignore) ไม่มีอยู่
- ยังเหลือ test ที่พังมาก่อนงานนี้ 1 ตัว: `docs/channels/sakuyako-cheris.md` อ้าง `sk06_bands.py` ที่ไม่มีใน `scripts/`

## v0.17.20 — ติดตั้ง AutoHarness

### รายละเอียด
- ติดตั้ง AutoHarness v0.1.0 (aiming-lab/AutoHarness) ใน `.venv` ของ repo ทดสอบ `autoharness check` แล้วบล็อก `rm -rf /` เป็น critical ได้จริง ยังไม่ติดตั้ง hook ของ Claude Code
- `.gitignore` เพิ่ม `audit.jsonl` เพราะ `autoharness check` เขียน audit log ลงโฟลเดอร์ที่รันทุกครั้ง

## v0.17.19 — Aomi-mama ปกขึ้น Drive

### รายละเอียด
- Aomi-mama 2026-10: คัดลอกปก 12 ใบและ manifest ขึ้น Google Drive `Projects/Aomi-mama/2026-10/covers/` (ตรวจ hash ตรงทุกไฟล์)

## v0.17.18 — Aomi-mama ปกคลิป 12 ใบ

### รายละเอียด
- Aomi-mama 2026-10: ทำปกครบ 12 ใบ (แนวนอน 6, แนวตั้ง 6) ข้อความจาก subtitle จริงของแต่ละคลิป
- โปรไฟล์ช่อง: บันทึกที่อยู่ไฟล์ปก โมเดลที่ใช้ และท่าที่ถือเครื่องเกม (ใช้กับคลิปเกมเท่านั้น)
- OPERATING-NOTES: เครื่องนี้ Pillow ไม่มี RAQM วางสระ/วรรณยุกต์ไทยผิด ให้ใช้ Chrome headless วาดข้อความปก

## v0.17.17 — Aomi-mama คลิปแนวตั้ง 6 อัน

### รายละเอียด
- Aomi-mama 2026-10: สร้างคลิปแนวตั้ง `<ชื่อ>_9x16` ครบ 6 timeline (1080x1920) ต้นฉบับไม่เปลี่ยน ตรวจ render ครบทุกเฟรม
- `load_subtitle_preset_auto.py` ใส่ `--timeline` ซ้ำได้หลายอัน โหลด Subtitle preset หลาย timeline โดยปิดเปิด Resolve รอบเดียว พร้อม test ใหม่
- โปรไฟล์ช่อง Aomi-mama: บันทึกเลย์เอาต์แนวตั้ง (คอมเมนต์บน/อวาตาร์ล่าง, ฉากห้องนอนใช้ track Reframe ตัดช่วงตามตำแหน่งหัว) และ GIF/ภาพประกอบใช้ preset `short`
- house-style: แนวตั้งให้ GIF และภาพประกอบใช้ video preset `short` แม้ทับหน้า (ผู้ใช้ยืนยัน)
- OPERATING-NOTES: SmartReframe ผ่านสคริปต์ไม่มีผล, ตำแหน่งซับแบบ track style แก้ผ่าน MCP ไม่ได้, Resolve ที่เปิดใหม่อัตโนมัติอาจไม่ตอบ scripting จนกว่าจะปิดจริง

## v0.17.16 — KT404 Highlights อัปเดต timeline หลัก 48 อัน

### รายละเอียด
- KT404 Highlights 2026-10: ตัดต่อครบ 48 timeline (ซับ Mitr Font, VTuber Zoom, GIF/SFX/BGM) และอัปเดตเป็น timeline หลักแล้ว ลบ timeline ต้นฉบับดิบกับสำรอง (`_bak`, `_edit_subs`) ตามที่ผู้ใช้สั่ง ตรวจแล้วทั้ง 48 มีครบ V1–V3, A1–A3 และซับ
- บันทึกวิธีแก้ peak: peak ที่ยังเกิน 0 dBTP หลังลด gain ทั้ง timeline มาจาก SFX ที่วางทับเสียงพูด จึงลดเฉพาะ SFX ที่ตรงจุด peak ไว้ใน skill `resolve-audio`
- บันทึกว่า SaveProject บนโปรเจกต์ใหญ่ใน Google Drive ใช้เวลาราว 30–60 วินาทีต่อครั้ง และ Windows ขึ้นว่า "ไม่ตอบสนอง" แม้งานยังเดินอยู่
- บันทึกเรื่องแถบดำด้านล่างของแต่ละสตรีมกับกรอบซูม, การโคลนสไตล์ซับผ่าน DRT, การหยุด render อย่างปลอดภัย และวิธีแก้ helper ล่ม
- `apply_enrichment_d22.py` ใช้คลิปใน media pool ซ้ำและ import ไฟล์ละครั้งเดียว พร้อมเทสต์ใหม่ 3 เคส

## v0.17.15 — Aomi-mama อัปเดตไฟล์หลัก

### รายละเอียด
- อัปเดตไฟล์หลักของโปรเจค aomimama-2026-10: ลบ timeline ต้นฉบับ 6 อันและ `_archived_v02` แล้วเปลี่ยนชื่อสำเนาที่ตัดต่อแล้วเป็นชื่อเดิม ตรวจแล้วทุก track ไม่เปลี่ยน
- ย้ายไฟล์สำรอง .drp/.db และไฟล์ render QC ของงานนี้ 76 ไฟล์ไป Recycle Bin (ยังกู้คืนได้)
- OPERATING-NOTES: เพิ่มกฎลบ timeline ด้วย `MediaPool.DeleteTimelines` เพราะ MCP `delete_timeline` สร้าง `_archived` ใหม่ทุกครั้ง

## v0.17.14 — Aomi-mama ภาพประกอบครบ 5 คลิป

### รายละเอียด
- ใส่ภาพประกอบ Noto Emoji 3D 14 ภาพใน 5 คลิปของโปรเจค aomimama-2026-10 (กิน 3, เสื้อผ้า 3, ยุง 2, บอส 3, ซิม 3) แล้ว render QC ผ่านครบ ไม่มีเฟรมดำ ความยาวตรง timeline
- โปรไฟล์ช่อง Aomi-mama: บันทึกตำแหน่งภาพประกอบตามเลย์เอาต์ (ซ้ายบนปกติ, ขวาบนเมื่ออยู่ในช่วงซูมที่อวาตาร์อยู่ซ้าย)

## v0.17.13 — Aomi-mama 2026-10 ครบ 6 คลิป

### รายละเอียด
- ตัดต่อครบชุด 5 timeline ที่เหลือของโปรเจค aomimama-2026-10 (สำเนา `_edit`): ซับไทย Mitr Font, VTuber Zoom, GIF, SFX, BGM; render QC ครบ 5 คลิป ไม่มีเฟรมดำ, ความยาวตรง timeline
- บันทึกกฎใหม่ใน OPERATING-NOTES: กู้งาน preset ซับเมื่อ Resolve เปิดกลับไม่ขึ้น, ต้องเช็คเลย์เอาต์ทุกคลิปก่อนตั้งกรอบซูมและตำแหน่ง GIF, เสียงที่ยาวเกิน timeline ทำให้มีเฟรมดำท้าย render
- โปรไฟล์ช่อง Aomi-mama: บันทึก 2 เลย์เอาต์ (หน้าคอมเมนต์ / ฉากห้องนอน) พร้อมค่ากรอบซูมและ Pan ของ GIF
- `apply_enrichment_d22.py`: รับ `fps` จากแผน และปฏิเสธ SFX ที่จะยาวเกินท้าย timeline ตั้งแต่ dry run พร้อม test ใหม่

## v0.17.12 — KT404 Highlights ซับ Mitr Font

### รายละเอียด
- โหลด Subtitle preset `Mitr Font` ลง timeline นำร่อง KT404 Highlights (`_vdo_edit`, 55 cue) ตามที่ผู้ใช้อนุมัติ; dry run ยืนยัน `already_matches=True`, gain/ซับ/track อ่านกลับไม่เปลี่ยน
- render ทดสอบ v2 ซับ burn-in 7052 เฟรม true peak -1.0 dBFS ไม่มีเฟรมดำ ซับอ่านได้บนฉากหิมะ
- บันทึกวิธีแก้เมื่อ Resolve กลับมาค้างที่ Project Manager หลังแพตช์ preset: ใช้ `resolve_recover.py` แล้ว dry run ซ้ำ ไม่แพตช์ซ้ำ

## v0.17.11 — KT404 Highlights งานนำร่อง

### รายละเอียด
- บันทึกงานนำร่อง KT404 Highlights 2026-10 (บอสกับหมากับกระสุน-Soul Walker): ซับไทย 55 cue, VTuber Zoom 5 ช่วง, GIF 5, SFX 9, BGM 1 บนสำเนา `_vdo_edit`; ต้นฉบับไม่แตะ
- บันทึก layout อวาตาร์มุมขวาล่างของโปรเจคนี้ (window top 0.545 / bottom 1.0 / cx 0.77) และระดับเสียงต้นทาง -25.7 LUFS
- เพิ่มกฎคัด GIF: ใช้เวลาเล่นจริง ≥1.5 วิ (ไม่ใช่จำนวนเฟรม/25) และห้ามใช้ GIF ภาพคนจริง `Reaction - Laughing Pointing.gif`

## v0.17.10 — บันทึกบทเรียนงานไฮไลต์ Katy404 2026-10

### รายละเอียด
- บันทึกการเรียนรู้และอัปเดตโปรไฟล์ช่อง Katy404 2026-10 (48 timeline หลัก + 3 timeline สำรอง _bak และข้อเสนอ 342 ช่วง)
- เพิ่มกฎการทำงานใหม่ใน docs/OPERATING-NOTES.md: ห้าม subagent เขียนไฟล์สคริปต์ช่วยลง %TEMP% เพื่อป้องกันการเขียนทับกัน, การปรับเกณฑ์ธงกระโดด !! แบบสัมพัทธ์, และการตรวจขยายขอบเขตท้ายคลิป +40 วิ
- บันทึกประวัติงานลงใน docs/highlight/wiki/wiki/log.md แบบ append-only
- รีเฟรช checksums ใน docs/skills-manifest.json และผ่านชุดทดสอบ highlight 74 รายการ

## v0.17.9 — รายงานงาน Katy404 2026-10 ฉบับเต็ม

### รายละเอียด
- เพิ่มรายงานภาษาไทยฉบับเต็มของงาน Katy404 2026-10 ที่ `work/highlight/Katy404/2026-10/REPORT.md`: ภาพรวม ขั้นตอน งานแต่ละ release รายการ 48 timeline พร้อมแนวคลิป ผลอ่านทั้งไลฟ์ ปัญหาและวิธีแก้ และสิ่งที่ยังไม่ได้ตรวจ

## v0.17.8 — อ่านทั้งไลฟ์ Katy404 ครบ 12 ไฟล์

### รายละเอียด
- Katy404 2026-10: ถอดเสียงทั้งไลฟ์ครบ 12 ไฟล์ (11 ไฟล์ใหม่ ใช้ GPU 42 นาที) และให้ reader 61 ตัวอ่านทั้งไลฟ์
- ได้ข้อเสนอ 342 ช่วง (ช่วงเงียบที่การคัดจากความดังไม่เจอ 248 ช่วง) ครอบคลุมคลิปที่อนุมัติไว้เดิม 37 จาก 48 คลิป สรุปช่วงเงียบที่ความมั่นใจ ≥ 0.5 จำนวน 27 ช่วงไว้ใน `work/highlight/Katy404/2026-10/whole_stream_proposals.md` ให้ฟังก่อน
- ข้อความถอดเสียงไทยยังเพี้ยนมาก (ความมั่นใจส่วนใหญ่ 0.3–0.5) ยังไม่มีคนดูช่วงใหม่ และไม่ได้แก้ timeline หรือ `review/<id>.json` ที่อนุมัติแล้ว
- แก้ brief ของ reader: ห้ามเขียนสคริปต์ช่วยลง `%TEMP%` หลังเจอ reader ที่ทำงานพร้อมกันใช้ชื่อไฟล์ซ้ำกัน; บันทึกตัวเลขและบทเรียนในสกิล `long-video-highlight-clipping`

## v0.17.7 — สกิลทางเข้าเดียว /highlight และคำสั่ง status

### รายละเอียด
- เพิ่มสกิลทางเข้าเดียว `highlight` (`/highlight`) หน้าเดียว มีผังขั้นตอน คำสั่งทีละขั้น ตัวอย่าง `job.json` และกฎรสนิยม ใช้ได้ทั้ง Claude Code, Codex และ Hermes; `AGENTS.md` ชี้มาที่สกิลนี้ก่อน
- เพิ่ม `pipeline.py status [ids]` (`scripts/highlight/status.py`) อ่านไฟล์อย่างเดียว แสดงตารางขั้นที่เสร็จต่อวิดีโอ และพิมพ์คำสั่งถัดไปคำสั่งเดียว รวมรายชื่อแพ็กที่ reader ยังไม่ส่ง และเตือนเมื่อวิดีโอมี `review/<id>.json` ที่อนุมัติแล้ว
- `fulltext`, `proposals`, `packets` รับ id วิดีโอได้ ทำทีละวิดีโอได้; เพิ่มตัวเลือก `READ_WHOLE_STREAM` ใน `job.json` (false = ใช้แค่การคัดจากความดัง)
- ทดสอบแบบ cold-start ด้วย agent ใหม่ที่ไม่มีบริบท: หาวิธีทำงานเจอเองจาก `AGENTS.md` และวางลำดับคำสั่งถูก; แก้ 3 จุดที่มันเจอ (ไม่มีกฎตอนทำวิดีโอที่อนุมัติแล้วซ้ำ, status เลือกวิดีโอไม่ได้, ไม่ได้บอก `WORK_DIR` และวิธีรันเบื้องหลัง)
- เพิ่มเทสต์ 7 ข้อใน `tests/highlight/test_status.py` (เทสต์ไฮไลต์ผ่านทั้งหมด 74 ข้อ)

## v0.17.6 — ให้ agent อ่านทั้งไลฟ์เพื่อหาช่วงน่าสนใจ

### รายละเอียด
- เพิ่มขั้น `pipeline.py readpacks` (`scripts/highlight/readpack.py`) แบ่งข้อความทั้งไลฟ์เป็นแพ็กละ 30 นาที (ซ้อนกัน 2 นาที) พร้อมบรรทัดสัญญาณเสียงรายนาที `loud` / `jump` / `talk` / `!!` / `shortlist`
- เพิ่ม `pipeline.py readbriefs` และ `templates/reader_brief.md` ให้ subagent อ่านทีละแพ็กแล้วเสนอช่วงแบบ ปูเรื่อง → จุดพีค → ปฏิกิริยา พร้อมประโยคที่ยกมาตรงตัว
- เพิ่ม `pipeline.py proposals` (`proposals.py`) ตรวจข้อเสนอ (ลำดับเวลา ความยาว หมวด และประโยคที่ยกมาต้องมีอยู่ในแพ็กจริง) รวมตัวซ้ำ ติดป้าย `quiet` ให้ช่วงที่การคัดจากความดังไม่เจอ แล้วให้ reviewer อ่าน `<id>.proposals.md` ก่อน
- ทดลองกับ Katy404 v05: reader 3 ตัวเสนอ 23 ช่วง ผ่านการตรวจทั้งหมด เป็นช่วงเงียบ 18 ช่วง และครอบคลุมคลิปที่อนุมัติไว้เดิม 3 จาก 4 คลิป (พลาดฉากลาวาที่มีแต่เสียงเกม) ยังไม่ได้ให้คนดูช่วงใหม่ และไม่ได้แก้ timeline ใน Resolve
- แก้ชื่อไฟล์แพ็กให้ตรงกับที่ brief เขียน (`<id>-read-NN.md`) และเปลี่ยนเกณฑ์ `!!` ให้เทียบกับทั้งไลฟ์ (เกณฑ์ dB ตายตัวขึ้นแทบทุกนาที) เพิ่มเทสต์ 6 ข้อ

## v0.17.5 — ถอดเสียงทั้งไลฟ์และตัดตรงขอบประโยค

### รายละเอียด
- เพิ่มขั้น `pipeline.py fulltext` (`scripts/highlight/fulltext.py`) ถอดเสียงทั้งไลฟ์พร้อมเวลาระดับคำด้วย faster-whisper `large-v3-turbo` ก้อนละ 10 นาที ทำต่อจากจุดค้างได้ ได้ `transcripts/<id>.fulltext.txt` แบบ `[H:MM:SS] ข้อความ [ends วินาที]` ให้ agent อ่านทั้งไลฟ์
- `snap.py` รับ `in:<วินาที>` / `out:<วินาที>` เลื่อนจุดตัดที่อยู่กลางประโยคไปต้น/ท้ายประโยค ถ้าไม่มีประโยคจะใช้ช่วงเงียบเหมือนเดิม
- packet ของ reviewer ใช้ประโยคทั้งไลฟ์พร้อม `[ends]` เมื่อมีไฟล์ fulltext และ brief บอกให้อ่านก่อน/หลังหน้าต่างเพื่อหาจุดปูเรื่องและมุกจบ
- ทดลองกับ Katy404 v05 (84 นาที): ใช้เวลา 2.5 นาที ได้ 626 ประโยค; snap คลิปเดิม 4 คลิป เลื่อนต้นคลิป 2 คลิปเร็วขึ้น 3–9 วิ และท้ายคลิป 2 คลิปช้าลง 0.4–4 วิ เพื่อไม่ตัดกลางประโยค (ยังไม่ได้แก้ timeline ใน Resolve)
- เพิ่มเทสต์ 9 ข้อใน `tests/highlight/test_fulltext.py` และบันทึกวิธีใช้ในสกิล `long-video-highlight-clipping` และ `scripts/INDEX.md`

## v0.17.4 — ไฮไลต์ Katy404 2026-10 และถอดเสียงไทยคุณภาพสูง

### รายละเอียด
- งานไฮไลต์ Katy404 2026-10: inventory ฟุตเทจ 12 ไลฟ์ (~27.4 ชม.), เลือก 48 คลิป (gameplay 26, fun 13, meme 9) และสร้าง 48 Timeline ในโปรเจกต์ `KT404 Highlights 2026-10` (อ่านกลับแล้ว 46 ตรงทุกค่า, 2 เลื่อนต้นทาง 1 เฟรมแต่ความยาวตรง)
- `features.py` เขียนไฟล์เสียงเป็น `.part.wav` แล้วเก็บเฉพาะเมื่อความยาวตรงกับต้นฉบับ พร้อม retry (การอ่านพร้อมกันจาก Google Drive ตัดไฟล์สั้นโดยไม่แจ้ง error)
- เพิ่ม `DEMUX_WORKERS` ใน `job.json` และให้ `pipeline.py` แสดงชื่อไฟล์ไทย/อีโมจิได้บนคอนโซล Windows, ส่งข้อความ hint ให้ขั้น `briefs`
- `gpu_env.py` ใช้ CUDA DLL จาก `torch/lib` ได้เมื่อไม่มีแพ็กเกจ `nvidia-*`
- บรีฟผู้ตรวจคลิปใช้ Python ตัวจริงและใส่ `HIGHLIGHT_JOB` ในคำสั่ง snap; schema test อ่านจำนวนคลิปจาก `CLIPS_PER_VIDEO`
- เพิ่ม `scripts/highlight/verify_timelines.py` อ่านกลับทุก Timeline แบบ read-only พร้อมเทสต์ (เทสต์ highlight ผ่าน 52 ข้อ)
- ยืนยันจากภาพในเกมว่า v11 และ v12 เป็นเกม Soul Walker (SoulWorker) และบันทึกในโปรไฟล์ช่อง Katy404
- ถอดเสียงภาษาไทยทั้ง 48 คลิปใหม่ด้วย demucs (แยกเสียงพูด) + Typhoon ASR (Whisper เป็นตัวเทียบ) แก้ปัญหาข้อความวนซ้ำใน 7 คลิป และถอดเลยจุดจบ 40 วินาทีเพื่อเช็กว่าไฮไลต์หลุดหลังจุดจบไหม
- ขยาย 3 Timeline ที่จบก่อนถึงไฮไลต์: v09-03 (100→135 วินาที), v08-03 (98→115), v12-01 (102→118) อ่านกลับแล้วตรงตามแผน ของเดิมเก็บเป็น `_bak`
- บันทึกใน `OPERATING-NOTES` และสกิล `long-video-highlight-clipping`: วิธีถอดเสียงคุณภาพสูงสุด, การเช็กประโยคไฮไลต์เทียบจุดจบ, และกรณี Resolve วางต้นทางคลาด 1 เฟรมเพราะปัดเวลา (สร้างใหม่ไม่หาย)

## v0.17.3 — แก้ path MCP และเก็บกวาด environment ทดสอบ

### รายละเอียด
- แก้ `.mcp.json` ให้ชี้ไปยัง checkout `davinci-resolve-mcp` ที่ตรวจ remote, entrypoint และ Python environment แล้ว; อัปเดตและยืนยันเวอร์ชัน v4.18.4
- เพิ่มวิธีตรวจและแก้ path MCP โดยรักษา `env` และยืนยันการเชื่อมต่อหลังเริ่ม session ใหม่
- เพิ่มวิธีตรวจ root `.venv` และลบเฉพาะ environment ชั่วคราวที่งานปัจจุบันสร้าง พร้อมตรวจ path ก่อนลบ

## v0.17.2 — ทดสอบออก release ใหม่บนคอนโซล Windows

### รายละเอียด
- แก้ `scripts/release.py` ให้พิมพ์ตัวอย่าง changelog ภาษาไทยได้บนคอนโซล Windows โดยไม่ต้องตั้ง `PYTHONIOENCODING=utf-8` (ก่อนหน้านี้ dry run ล้มทันที) พร้อมเทสจำลองคอนโซล cp1252
- release นี้ออกด้วย `scripts/release.py --publish` ตรงๆ โดยไม่ตั้งตัวแปร encoding เพื่อทดสอบทั้งขั้นตอน commit, tag, push และ `gh release create`

## v0.17.1 — แก้สคริปต์ออก release กับข้อความภาษาไทย

### รายละเอียด
- แก้ `scripts/release.py` ให้อ่านผลลัพธ์คำสั่งเป็น UTF-8: ตอนออก v0.17.0 ข้อความ commit ภาษาไทยทำให้สคริปต์ล้มหลังสร้าง commit (ต้องทำ tag/push/release ต่อเอง) พร้อมเทสใหม่ใน `tests/test_release.py`

## v0.17.0 — รวมเครื่องมือคัดไฮไลต์ไลฟ์สตรีมเข้าโปรเจกต์

### รายละเอียด
- ย้ายเครื่องมือคัดไฮไลต์ไลฟ์สตรีม (mp4 เสียงไทย) จาก repo `agent-seacrh-virus-cut` มาไว้ที่ `scripts/highlight/` พร้อมเทส `tests/highlight/` (ผ่าน 44 เทส)
- เพิ่ม 10 สกิล: long-video-highlight-clipping, livestream-highlight-clipping, new-channel-job-setup, timeline-naming-convention, user-feedback-capture, resolve-project-folder-targeting, resolve-still-qc-capture, llm-wiki, resolve-smart-edit, vertical-video-reframing
- ย้ายวิกิความรู้คัดคลิปไปที่ `docs/highlight/wiki/`, เทมเพลตงานภาษาไทยไปที่ `docs/highlight/prompt-template.md` และข้อมูลงานเก่า 4 งาน (เฉพาะไฟล์เล็ก) ไปที่ `work/highlight/`
- เพิ่มหัวข้อขั้นตอนงานไฮไลต์ใน `AGENTS.md`, หมวด 9 ใน `scripts/INDEX.md` และกฎตั้งชื่อ Timeline ไฮไลต์ใน house-style
- repo เดิมไม่ถูกแก้; ไฟล์เสียง/เฟรม/ถอดเสียงขนาดใหญ่ไม่ได้ย้ายและถูก gitignore

## v0.16.23 — ปกคลิป Bunny Girl ep4

### รายละเอียด
- ทำปก Bunny Girl ep4: `Thumbnail/ep4_thumb_16x9.jpg` (1920x1080) และ `ep4_thumb_9x16.jpg` (1080x1920) ข้อความตามผู้ใช้ "ทำไมถึงใส่ชุด Bunny Girl?" (บรรทัดแรกแดง, Bunny ขาว / Girl? เหลือง, Mitr Bold ขอบดำ+ขาว), ภาพอวาตาร์เฟรม 0.8 วิ
- ตรวจสระ/วรรณยุกต์ไทยและภาพย่อ 320x180 / 180x320 แล้ว; บันทึกกับดักระยะบรรทัด (สระ ุ ใต้ "ชุด" ชนบรรทัดล่าง)

## v0.16.22 — ส่งมอบ Bunny Girl ep4 9:16

### รายละเอียด
- ส่งมอบ Bunny Girl ep4 9:16: `Bunny Girl ep4_9x16_FINAL_2026-11-01.mp4` จาก `Timeline 1_9x16` 1080x1920@60 ซับ burn-in, 9655 เฟรม, -15.7 LUFS, peak -1.5 dBFS, ไม่มีเฟรมดำ
- บันทึกการส่งมอบในโปรไฟล์ Katy404 (ไฟล์ส่งมอบปัจจุบัน: 16:9 FINAL_v2 + 9:16 FINAL; งานที่เหลือ: ปก)

## v0.16.21 — Bunny Girl ep4 FINAL_v2 และ 9:16 ทดสอบ

### รายละเอียด
- เรนเดอร์ 16:9 ใหม่เป็น `Bunny Girl ep4_FINAL_v2_2026-11-01.mp4` จาก `Timeline 1_pop` ที่ผู้ใช้แก้เอง: 9655 เฟรม, -15.7 LUFS, peak -1.5 dBFS, ไม่มีเฟรมดำ
- สร้าง 9:16 `Timeline 1_9x16` (กราฟิกแนวตั้ง 7 บท, ซูม 1.1x, ซับ `Mitr-short-001`) และเรนเดอร์ทดสอบ `Bunny Girl ep4_9x16_test_2026-11-01.mp4`: 1080x1920@60, 9655 เฟรม, -15.7 LUFS, ไม่มีเฟรมดำ
- บันทึกกับดัก: เรนเดอร์ Resolve พร้อม HyperFrames ทำให้ Fusion ล้ม, Resolve ค้างตอนโหลด preset ต้องให้ผู้ใช้ปิดเอง, gain ของ timeline อื่นเด้งกลับหลัง reload
- house-style: ผู้ใช้อยากได้วิธีโหลด preset ซับที่ไม่ต้องปิด Resolve ให้ลอง MCP `timeline_ai set_subtitle_preset` ก่อน

## v0.16.20 — ส่งมอบ Bunny Girl ep4 16:9

### รายละเอียด
- ส่งมอบ Bunny Girl ep4 16:9: `Bunny Girl ep4_FINAL_2026-11-01.mp4` เรนเดอร์จาก `Timeline 1_pop` 1920x1080@60 ซับ burn-in, 10210 เฟรม, -15.7 LUFS, peak -0.9 dBFS, ไม่มีเฟรมดำ
- บันทึกการส่งมอบในโปรไฟล์ Katy404 (ไม่ได้เปลี่ยนชื่อหรือ promote timeline; งานที่เหลือ: 9:16 และปก)

## v0.16.19 — ตัดต่อ Bunny Girl ep4 (ทดสอบ)

### รายละเอียด
- ตัดต่อ Bunny Girl ep4 "ทำไมถึงอยากใส่ชุดบันนี่เกอร์" บน `Timeline 1_pop` (ต้นฉบับ `Timeline 1` ไม่แตะ): ช่วงเงียบ 1.6 วิ + การ์ด CHAPTER 01–05, ซูม 7 ช่วง 1.35x, กราฟิก Pop Kinetic 7 บท, ซับไทย 188 cue preset `Mitr Font`, SFX 41 จุด, BGM ต่อสองท่อน
- เรนเดอร์ทดสอบ `Bunny Girl ep4_POP_test_2026-11-01.mp4` 10210 เฟรม 1080p60 ซับ burn-in, -15.7 LUFS, peak -0.9 dBFS, ไม่มีเฟรมดำ, ช่วงการ์ดเงียบทุกช่วง
- บันทึกโปรไฟล์ Katy404: ซับช่องนี้ใส่คำหยาบตามที่พูดจริง, ไอคอน `leotard` อ่านไม่ออกที่ขนาดการ์ดให้ใช้ `earband`, คำที่ต้องฟังยืนยัน 6 จุด
- skill `resolve-delivery`: เรนเดอร์ล้มที่ 0% แล้ว helper ยังล็อกไฟล์ปลายทาง ("Existing file can not be removed") ต้องเรนเดอร์ด้วยชื่อใหม่

## v0.16.18 — ปกคลิป เกมที่ชอบในปี 2026

### รายละเอียด
- ทำปกคลิป "เกมที่ชอบในปี 2026" ของ Armigon สองสัดส่วน คือแนวนอน 1920×1080 และแนวตั้ง 1080×1920 วางไว้ข้างคลิปใน `Z:/armigon/เกมโปรด 2026/`
- ใช้เฟรมจริงจากคลิป (วินาทีที่ 65) และข้อความ "เกมที่ชอบปี 2026 / MINECRAFT / ครบ 3 อันดับ?!" ตรวจด้วยตาที่ขนาดมือถือ ภาพขาวดำ และภาพเบลอแล้ว ไม่มีการแก้ Resolve
- บันทึกกับดัก: `hyperframes snapshot` ไม่ใช้ `--out` และเขียนภาพไว้ใน `.hyperframes/artifacts/snapshots/`

## v0.16.17 — ลบ timeline สำรองแนวตั้ง เกมที่ชอบในปี 2026

### รายละเอียด
- ลบ timeline สำรอง `FirstPass v2_illustrated_9x16_bak` ตามที่ผู้ใช้สั่ง หลังตรวจว่า 16:9 ต้นฉบับไม่เปลี่ยนและ timeline แนวตั้งหลักเป็นเวอร์ชันล่าสุด (ซับ 79 cue)
- บันทึกการลบและไฟล์ .drp ที่ใช้กู้คืนได้ลงโปรไฟล์ Armigon

## v0.16.16 — คลิปแนวตั้ง เกมที่ชอบในปี 2026

### รายละเอียด
- ทำคลิปแนวตั้ง 1080×1920 "เกมที่ชอบในปี 2026" (Armigon) ด้วย layout B: อวาตาร์ครึ่งล่าง แถบบนเบลอ กราฟิกข้าง 12 ชิ้นย้ายเข้าแถบบน ภาพเต็มจอ 2 ช่วงทำใหม่เป็นแนวตั้ง
- ซับยาว 10 บรรทัดที่ล้นขอบจอแนวตั้ง แบ่งเป็นบรรทัดสั้นเฉพาะเวอร์ชันแนวตั้ง (68 → 79 cue สไตล์เดิม) ผ่าน DRT ตรวจแล้วภาพ เสียง และ transform ไม่เปลี่ยน
- render แล้วมีซับฝังในภาพ 4,151 เฟรม 60 fps −15.8 LUFS ตรวจเฟรมแล้วว่าซับทุกบรรทัดที่แบ่งอยู่ในจอ
- แก้ `full_original_signature` ให้รองรับ Adjustment Clip ที่ซูมผ่าน Inspector (ไม่มี Fusion)
- บันทึกกฎตรวจความกว้างซับเมื่อทำ 9:16 จาก 16:9 ลง OPERATING-NOTES

## v0.16.15 — Adjustment Clip บน Video 3 เกมที่ชอบในปี 2026

### รายละเอียด
- เกมที่ชอบในปี 2026 (Armigon): สร้าง timeline `FirstPass v2_illustrated_focus_v3` ที่มี Adjustment Clip แบบ Inspector (Zoom 1.377) บน Video 3 ครบ 5 ช่วงตามคลิปที่ผู้ใช้วางเอง; ต้นฉบับไม่ถูกแก้ ตรวจ readback และ render 1 เฟรมต่อช่วงแล้ว
- บันทึกกับดัก: Adjustment Clip จาก Effects library ใน DRT เป็น `Sm2TiVideoClip` ไม่ใช่ `Sm2TiGenerator` จึงใช้ `drt_rebuild_focus_track` ไม่ได้ ต้องโคลน Element เอง
- house-style: เมื่อผู้ใช้วาง Adjustment Clip เองบน track ใด ให้โคลนคลิปนั้นบน track เดิม ไม่ใช้ Fusion Transform แทน

## v0.16.14 — ภาพประกอบ เกมที่ชอบในปี 2026

### รายละเอียด
- เพิ่มภาพประกอบ HyperFrames 14 ช่วงให้คลิป "เกมที่ชอบในปี 2026" (Armigon) บนสำเนา `FirstPass v2_illustrated` แทร็ก V2 `REACTIONS`: กราฟิกข้าง 12 + ภาพแฟนตาซีเต็มจอ 2 ตรงตามซับ
- ตรวจแล้ว: `illustration_reel.py` baseline/pilot/apply/verify ผ่าน, แทร็กต้นฉบับ (วิดีโอ 15 / เสียง 41 / ซับ 68) ตรง baseline, render QC 1920×1080 60 fps 4,151 เฟรม decode ไม่มี error มีซับครบทุกช่วง
- บันทึกกฎใหม่: เก็บ reel และ placements.json ไว้ข้างฟุตเทจ (`Z:/…/illustrations/`) แทน `.hermes/projects/` เพื่อกัน Media Offline

## v0.16.13 — Render แนวตั้ง ทำไมถึงมาเป็นวีทูปเบอร์

### รายละเอียด
- Render วิดีโอแนวตั้ง "ทำไมถึงมาเป็นวีทูปเบอร์" เต็มความยาว ซับ burn-in ที่ `Z:/armigon/Why Vtuber/FirstPass v2_illustrated_9x16.mp4`
- QC ผ่าน: 1080×1920 60 fps 9,195 เฟรมตรง Timeline, เสียง AAC stereo −16.1 LUFS / peak −1.1 dBFS, ตรวจ 12 เฟรมมีซับและ layout ถูกต้อง
- บันทึกผล render และคำสั่งไว้ในโปรไฟล์ Armigon

## v0.16.12 — แนวตั้ง ทำไมถึงมาเป็นวีทูปเบอร์

### รายละเอียด
- สร้าง Timeline แนวตั้ง `FirstPass v2_illustrated_9x16` (1080×1920, 60 fps) ของโปรเจกต์ "ทำไมถึงมาเป็นวีทูปเบอร์" ด้วย layout B; build ผ่าน readback ต้นฉบับไม่เปลี่ยน เสียงและซับ 146 ตรงเดิม
- เพิ่ม reel ภาพเต็มจอ 9:16 (novel/party) และ top plate ไว้ใน `Z:/armigon/Why Vtuber/illustrations/v916/`
- บันทึกสูตร Tilt/Zoom ของภาพนิ่งสี่เหลี่ยมจัตุรัสใน Timeline 9:16 ที่ยืนยันจากเฟรม render จริง และวิธีแปลงจาก Timeline สดที่ผู้ใช้แก้แล้ว
- แก้ path สคริปต์ scratch ในโปรไฟล์ Armigon ให้ผ่านการตรวจโปรไฟล์

## v0.16.11 — ย้ายสื่อโปรเจกต์ทำไมถึงมาเป็นวีทูปเบอร์

### รายละเอียด
- เพิ่ม `scripts/consolidate_project_media.py`: คัดลอกไฟล์ทุกตัวที่โปรเจกต์ใช้ไปไว้โฟลเดอร์เดียว แยกเป็น gif/sfx/bgm/subtitles/illustrations แล้ว relink และอ่าน File Path กลับทุกคลิป (สำรอง `.drp` ก่อน, ไม่ลบต้นฉบับ)
- โปรเจกต์ ทำไมถึงมาเป็นวีทูปเบอร์: คัดลอก 51 ไฟล์ไปที่ `Z:\armigon\Why Vtuber` และ relink สำเร็จ 49 ไฟล์; Timeline `FirstPass v2_illustrated` ใช้ 14 ไฟล์ ทั้งหมดอยู่ในโฟลเดอร์ใหม่และ online
- บันทึกใน OPERATING-NOTES: ย้ายสื่อให้ใช้วิธีคัดลอก (คลัง GIF/SFX/BGM ใช้ร่วมกับโปรเจกต์อื่น) และ `RelinkClips` คืนค่า False กับคลิป `.srt` ใน Media Pool บน 21.1.0.17

## v0.16.10 — Render ส่งมอบครบ 76 ไฟล์ พร้อมปกแนวตั้ง (Sakuyako 2026-06)

### รายละเอียด
- Render ส่งมอบโปรเจกต์ `2026-06-Sakuyako` ครบ 76 ไฟล์ `.mov` (H.264/AAC 30 fps, preset `H.264 Master`, ซับฝังในภาพ) ไปที่ `G:\My Drive\Projects\Sakuyako-Cheris\2026-06\vdo`: แนวนอน 38 ไฟล์ 1920×1080 และแนวตั้ง 38 ไฟล์ 1080×1920
- แนวตั้งทุกไฟล์เปิดด้วยปกแนวตั้งของคลิปนั้น 1 วินาที (30 เฟรม ไม่มีเสียง) แล้วจึงเริ่มเนื้อหา; แนวนอนไม่มีปก; Timeline ต้นฉบับไม่ถูกแก้ (ใช้สำเนาชั่วคราวแล้วลบทิ้ง)
- `scripts/p2_export_final.py`: เพิ่ม `--vertical-suffix`, `--cover-pattern` (`{name}`/`{stem}`) และ `--cover-bin` ให้ใช้กับชื่อ timeline/ปกแบบอื่นได้ ค่าเดิมไม่เปลี่ยน พร้อมเทสต์ใหม่
- ตรวจแล้ว: Resolve รายงาน Complete ครบ 76 job, `--verify` ผ่าน 76/76 (สตรีมภาพ+เสียง ขนาด ความยาวตรง timeline และเฟรมแรกแนวตั้งตรงกับปก SSIM ≥ 0.9); pilot ตรวจภาพแล้วว่าซับฝังในภาพทั้งสองแนว และวินาทีแรกของแนวตั้งเงียบ (-78 dB)
- บันทึกคำสั่งและผลในโปรไฟล์ช่อง Sakuyako และกฎรับมือเมื่อ `SaveProject` ล้มเหลวชั่วคราวใน `docs/OPERATING-NOTES.md`
- ข้อจำกัด: ตรวจซับด้วยภาพเฉพาะคู่ pilot (ไฟล์อื่นใช้การตั้งค่าเดียวกัน); pytest ยังมี 5 failed / 12 errors เดิมที่มีก่อนงานนี้ ไม่มีรายการใหม่

## v0.16.9 — ระบบหลักฐานเกม/ช่อง และรีวิวหลังตัดต่อ

### รายละเอียด
- เพิ่ม `scripts/channel_intelligence.py` สำหรับตรวจรายงานหลักฐานเกม/ช่องแบบ offline พร้อมเทสต์ และแถวใน `scripts/INDEX.md`
- เพิ่มขั้นตอนระบุเกม (`video-footage-review/references/game-identification.md`) และรีวิวหลังตัดต่อ (`resolve-video-enrichment/references/post-edit-review.md`) พร้อมอัปเดต skill `project-learning`, `resolve-video-enrichment`, `video-footage-review`
- `AGENTS.md`: เพิ่มวิธีแก้เมื่อพาธ MCP หาย และให้งานตัดต่อทำตาม `project-learning` + post-edit review ตั้งแต่ต้นงาน
- แก้พาธ `davinci-resolve` MCP ใน `.mcp.json` ให้ตรงตำแหน่งจริง และเพิ่ม `.codex/config.toml` สำหรับ Codex
- `.gitignore`: คง `.hermes/` ไว้ไม่ให้ไฟล์งาน/ภาพเข้า repo และเพิ่ม `.worktrees/`
- ตรวจแล้ว: pytest 325 passed (เพิ่มจาก 243), รายการที่ล้มเหลว 5 failed / 12 errors เป็นของเดิมทั้งหมด ไม่มีความล้มเหลวใหม่; commit ไม่มีไฟล์ภาพ/วิดีโอ/.drp/.hermes และไม่มี key
- ไม่ได้ commit: `.hermes/` (~5.7 GB ภาพ/รายงาน/backup) และสคริปต์ทดลอง `test_insert*.py` ที่รากโปรเจกต์ซึ่งลบ/สร้าง Timeline บน Resolve จริง

## v0.16.8 — ปกคลิปครบ 38 คลิป (Sakuyako 2026-06)

### รายละเอียด
- ทำปกคลิปโปรเจกต์ `2026-06-Sakuyako` ครบ 38 คลิป คลิปละแนวนอน 1920×1080 และแนวตั้ง 1080×1920 รวม 76 ไฟล์ JPG ใน `G:\My Drive\Projects\Sakuyako-Cheris\2026-06\vdo`
- ใช้ Template มินิมอลแบบเดียวที่ผู้ใช้อนุมัติ: ฉากเกมจริงจาก Timeline + มาสคอต `sk_04` + ข้อความไทย 2 บรรทัด (ชมพู/ขาว) ไม่มีของตกแต่งเพิ่ม
- ตรวจแล้ว: ขนาดภาพถูกต้องทุกไฟล์ ไม่เกิน 2 MB, ไฟล์บน Drive ตรงต้นฉบับ (sha256), ตรวจภาพครบไม่พบข้อความล้น/ชนมาสคอต/อวาตาร์ซ้ำ; ดึงเฟรมจาก Resolve แบบอ่านอย่างเดียวและคืน Timeline/playhead เดิมแล้ว
- บันทึกความชอบปกแบบมินิมอลใน `house-style`, รายละเอียด Template ในโปรไฟล์ช่อง Sakuyako และกฎ retry playhead ก่อน export ภาพนิ่งใน `docs/OPERATING-NOTES.md`
- รวม commit งาน Sakuyako ที่ค้างในเครื่อง (layout A, BGM, render, `backup_drp` absolute path) เข้ากับ `main`
- ข้อจำกัด: pytest ยังมี 5 failed / 12 errors ที่มีอยู่แล้วก่อนงานนี้ (ตรวจเทียบ baseline แล้ว ไม่มีความล้มเหลวใหม่); ไฟล์ปกเป็นงานส่งมอบบน Drive จึงไม่ได้ commit เข้า repo

## v0.16.7 — ภาพประกอบคลิปทำไมถึงมาเป็นวีทูปเบอร์

### รายละเอียด
- เพิ่มภาพประกอบ 21 ช่วงให้คลิป "ทำไมถึงมาเป็นวีทูปเบอร์" บนสำเนา `FirstPass v2_illustrated` (V2 `REACTIONS`): ภาพแฟนตาซีเต็มจอ 4 ช่วง + กราฟิกเคลื่อนไหวมุมซ้ายบน 17 ช่วง จาก reel HyperFrames ProRes 4444 alpha เดียว
- ตรวจแล้ว: ช่วงเฟรมทั้ง 21 ชิ้นอ่านกลับตรงแผน, track วิดีโอ/เสียง/ซับของต้นฉบับตรง baseline, เฟรม Resolve พร้อมซับทุกช่วงไม่ทับหน้า/เขาตัวละครและไม่ชนซับ
- บันทึกโปรไฟล์ช่อง Armigon และกับดักเวลา/ขนาดไฟล์ของ reel alpha ยาวใน OPERATING-NOTES

## v0.16.6 — 9:16 ครบ 85 Timeline และ render ทั้งหมด (Sakuyako)

### รายละเอียด
- สร้าง `_9x16` ครบ 85 Timeline ของ 2026-06-Sakuyako: เกมด้านบน chibi ด้านล่าง (ย่อ chibi ให้ซับอยู่ใต้ตัว) ตรวจภาพ/เสียง/ช่วงเวลา/ซับเทียบต้นฉบับผ่านทุก Timeline
- render 16:9 และ 9:16 ครบอย่างละ 85 ไฟล์ (มีเสียง + burn-in ซับ) ตรวจจำนวนเฟรมและเสียงด้วย ffprobe ผ่านทุกไฟล์ และย้ายไปไว้ใน Google Drive `2026-06/vdo` และ `vdo/9x16`
- บันทึกวิธีทำ 9:16 ที่ไม่ทำให้ Resolve 21.1.0.17 ค้าง (ตั้งขนาดบน Timeline ว่างก่อน, ใส่ซับก่อนภาพ) และกับดักเรื่อง render preset ค้างคิว

## v0.16.5 — VTuber Zoom ครบ 85 Timeline (Sakuyako)

### รายละเอียด
- แก้ VTuber Zoom ที่ใหญ่ผิดปกติใน `ช็อตฮา  โอ้ย-vdo` (Sakuyako) และสร้างคลิปใหม่ให้เหลือ Fusion comp เดียวต่อคลิป
- เพิ่ม VTuber Zoom ให้ครบ 85 Timeline ของ 2026-06-Sakuyako: เลือกจุดซูมจากซับ (Timeline ที่ไม่มีซับใช้ความดังของเสียงแทน) วัดตำแหน่ง chibi แยกตามแต่ละ source และจัด chibi ไว้ทางซ้ายเพื่อไม่ให้ซับตกบนตัว ผลตรวจ: ช่วง/comp/Transform/track เดิมผ่านทุก Timeline และดูภาพ still จาก Resolve ครบทุกคลิป
- `scripts/focus_qc_frames.py` เพิ่มตัวเลือก `--fps` (เดิมใช้ได้เฉพาะ 60 fps)
- บันทึกกับดัก API ของ 21.1.0.17 ใน skill และ OPERATING-NOTES: track enabled อ่านค่าได้เฉพาะ Timeline ปัจจุบัน, ลบ Fusion comp ไม่ได้, ค่า Fusion ถูกปัดเศษหลังเปิดใหม่, ExportProject ต้องใช้ path แบบเต็ม, Google Drive หลุดทำให้ Resolve ค้าง
- รวม commit ที่ push ไว้ก่อนหน้า: ปก Armigon, helper ทำ inventory จุด focus จากซับ และแผน pilot ของ VTuber zoom

## v0.16.4 — ลบ Timeline สำรองและเพิ่มเครื่องมือลบ archive

### รายละเอียด
- เพิ่ม `scripts/delete_archived_timelines.py` สำหรับลบ timeline `<ชื่อ>_archived_vNN` ที่ MCP สร้างอัตโนมัติ: dry-run ก่อน, เทียบคลิปภาพ/เสียงกับ timeline หลัก, สำรอง `.drp` แล้วลบด้วย `--confirm` และอ่านกลับ พร้อม test
- ลบ timeline สำรอง `_archived_v01` 20 อันในโปรเจกต์ `2026-06-Sakuyako` (ภาพ/เสียงตรงกับ timeline หลักทุกอัน) เหลือ timeline หลัก 85 อัน ซับยังตรง SRT 81/85 ตามเดิม

## v0.16.3 — ซับ Typhoon และแก้ชื่อเชอรี่ทั้งโปรเจกต์ Sakuyako

### รายละเอียด
- นำข้อความ Typhoon ที่ตรวจคำแล้วเข้า native Subtitle track 11 Timeline ของ `2026-06-Sakuyako` แทนซับร่างเดิม และอ่านกลับตรงทุก cue
- แก้ชื่อสตรีมเมอร์เป็น "เชอรี่" ใน 16 Timeline ที่ใช้ SRT เดิม (ASR เคยได้ยินเป็น ชนิด/เฉศนิท/ฉลิด/ชะลีด/ชิคกี้พาย) โดยไม่เปลี่ยนเวลา
- ผลรวม: ซับตรงกับ SRT 81/85 Timeline ต้นฉบับ; อีก 4 Timeline ไม่มีเสียงพูดของสตรีมเมอร์ (ไม่มีเสียง, เสียงพากย์เกม, เพลง)
- บันทึกวิธีถอดเสียงคลิปที่เสียงเกมกลบเสียงพูด (demucs + VAD + Whisper/Typhoon) ใน skill `thai-subtitles-resolve` และกฎการแทน subtitle track ใน `docs/OPERATING-NOTES.md`

## v0.16.2 — กู้ Resolve อัตโนมัติเมื่อปิดเองหรือค้าง

### รายละเอียด
- เพิ่ม `scripts/resolve_recover.py` ให้ agent กู้ DaVinci Resolve ที่ปิดเองหรือค้างได้เอง: เปิด Google Drive ใหม่เมื่อไดรฟ์ของ project library หาย, kill เฉพาะเมื่อ Resolve ค้าง, เปิด Resolve ผ่าน Explorer และเปิดโปรเจกต์เดิมให้ (ทดสอบจริงกับ `2026-06-Sakuyako` ได้ `RECOVER_OK`)
- เพิ่ม test `tests/test_resolve_recover.py` (5 ข้อผ่าน) และแถวใน `scripts/INDEX.md`
- บันทึกกฎใน `AGENTS.md`, `docs/OPERATING-NOTES.md` และ skill `resolve-session`: ผู้ใช้อนุญาตให้กู้ Resolve เองแล้ว, ถ้า SaveProject คืนค่า False ให้ตรวจไดรฟ์ library ก่อน, หลังเปิดใหม่ให้ตรวจผลโดยอ่านค่ากลับแทนการเชื่อค่าที่ setter คืนมา
- อัปเดตสถานะช่อง Sakuyako-Cheris: นำ SRT เข้า native Subtitle track แล้ว 78/85 timeline และอ่านกลับตรวจครบทุก cue

## v0.16.1 — วางระบบเรียนรู้และเผยแพร่ให้ทุก agent

### รายละเอียด
- ปรับ `AGENTS.md` และ `.agents/skills/project-learning/SKILL.md` ให้ทุก agent บันทึกบทเรียนลง skill/เอกสารที่ตรงงาน และทำ release หลังตรวจสอบงาน
- เพิ่ม `scripts/release.py` สำหรับ SemVer patch bump โดยปริยาย, ตรวจความสะอาดและซิงก์ของ branch/tag, ตรวจหัว changelog, preview ก่อนเผยแพร่ และเผยแพร่ GitHub Release เมื่อระบุ `--publish`
- ปรับ `refresh_skill_manifest.py` ให้คง checksum ที่ยังถูกต้องเมื่อ checkout แปลง LF/CRLF; บันทึกกฎใน `docs/OPERATING-NOTES.md` เพื่อไม่ให้ refresh เปลี่ยน hash ที่ไม่จำเป็น
- ลงทะเบียนเครื่องมือ release ใน `scripts/INDEX.md` และเพิ่ม unit tests สำหรับ release/preflight และ manifest checksum
- ผลทดสอบเฉพาะทาง: ผ่าน 11 tests; full suite: 236 passed, 23 skipped, 4 failed และ 12 errors จาก references/ไฟล์ QC ที่ขาดใน workspace
- ไม่ได้ทดสอบกับ DaVinci Resolve จริง; งาน Armigon/export ที่ค้าง staged ก่อนเริ่มและ config เฉพาะเครื่องไม่รวมใน release นี้

## v0.16.0

### Added
- เพิ่ม `scripts/drt_rebuild_focus_track.py` แทนที่ทุก clip บน Adjustment Clip track ที่ระบุชื่อใน DRT ด้วย clip ใหม่จาก template ตามช่วงที่กำหนด (`--create` สร้าง track ก่อน) ตรวจช่วงซ้อน, DbId ซ้ำ และเทียบ track อื่นแบบ byte ต่อ byte (ยกมาจากขั้น `rezoom` ของงาน Bunny Girl)
- เพิ่ม `scripts/rebuild_trimmed_zoom_clip.py` สร้าง zoom track ใหม่บน timeline ที่เปิดอยู่หลังตัดหัว timeline (คง Fusion Transform)
- เพิ่มชุดทดสอบ 12 รายการใน `tests/test_drt_rebuild_focus_track.py`

### Fixed
- `scripts/refresh_skill_manifest.py` และ `scripts/verify_skill_bundle.py` ไม่นับไฟล์ที่ gitignore (เช่น `scripts/scratch/*`) เป็นไฟล์ใน bundle อีกต่อไป และลบ skill declaration ที่ไม่มีโฟลเดอร์แล้ว (ก่อนหน้านี้ manifest พังทุกครั้งที่ไฟล์ scratch เปลี่ยน และ checkout ใหม่จะ verify ไม่ผ่าน); เพิ่ม `tests/test_bundle_git_ignored.py`

### Updated
- บทเรียนจากงาน "Bunny Girl คืออะไร" (Katy404, 2026-10-17) ใน `docs/OPERATING-NOTES.md`: ชื่อ timeline หลัง import DRT, endFrame ของ `AppendToTimeline` เป็น exclusive, วิธีต่อ BGM ให้วนที่ช่วงเงียบ, Adjustment Clip ที่ถูกยืดหัวแล้ว render ไม่ได้, InsertGenerator บน 21.1.0.17 และ SFX ทับกันบน track เดียว
- `house-style`: กราฟิก keyword ใน explainer ต้องใหญ่และเปลี่ยนตามคำพูด (ผู้ใช้เลือก Pop Kinetic)
- โปรไฟล์ `docs/channels/katy404.md`: สถานะ day 25 และ Bunny Girl (timeline, ค่า SFX/BGM ที่ผู้ใช้ยืนยัน, backup)
- `resolve-edit` และ `adjustment-focus.md` ชี้ไปที่เครื่องมือใหม่; ลงทะเบียนใน `scripts/INDEX.md`
- `scripts/check_mcp_update.py` รายงาน `BLOCKED` เมื่อ path ใน `.mcp.json` ไม่มี MCP อยู่จริง; `.mcp.json` ชี้ไปที่ `D:\davinci-resolve-mcp`

### Verified
- `python -m pytest -q` ผ่าน 227 passed, 22 skipped, 10 subtests; `python scripts/verify_skill_bundle.py` ผ่าน (errors ว่าง)
- เครื่องมือใหม่ทดสอบแบบ offline กับ DRT จำลองเท่านั้น ยังไม่ได้รันกับ Resolve จริง (logic เดียวกับขั้น `rezoom` ที่ render ผ่านในงาน Bunny Girl)

### Scope
- skill HyperFrames ที่ติดตั้งจาก upstream (`general-video`, `hyperframes*`, `media-use`, `skills-lock.json`) ไม่รวมใน release นี้ เพราะมี local reference ที่ verifier ยังหาไม่เจอ 18 รายการ

## v0.15.0

### Added
- เพิ่ม `scripts/prepare_edit.py` เตรียม offline intake แคชผล ffprobe สร้าง draft edit decisions นำผล caption lint เดิมมาใช้ซ้ำ และสร้าง contact sheet โดยไม่ต่อ Resolve และไม่แก้ footage ต้นฉบับ
- เพิ่ม `scripts/edit_workflow.py` ตรวจ rational frame rates (คำนวณแยกตาม source/record rate), ตรวจ gapless cut และ evaluate acceptance gate เทียบกับ SHA-256 evidence hashes แบบ deterministic
- เพิ่ม schema และสัญญาตรวจรับงานใน `docs/contracts/`: `acceptance-gate.json`, `edit-decisions.schema.json` และ `edit-decisions.example.json`
- เพิ่มเอกสารคู่มือ `docs/EDIT-WORKFLOW.md` อธิบายกระบวนการเตรียมงาน offline การร่างสัญญาตัดต่อ และเกณฑ์ตรวจรับงานตาม house style
- เพิ่มชุดทดสอบ 37 รายการใน `tests/test_edit_workflow.py` ครอบคลุม frame rate parsing, duplicate IDs, cache invalidation, caption linting, SRT validation, contact sheet hashing และการป้องกัน Windows junction

### Updated
- เพิ่มหัวข้อ "เตรียมงานและเกณฑ์ตรวจรับกลาง" ใน `README.md` ชี้ไปที่ `docs/EDIT-WORKFLOW.md`
- บันทึกกฎ offline intake, cache validation และ coverage ใน `docs/OPERATING-NOTES.md`
- ลงทะเบียนเครื่องมือใหม่ทั้งสองรายการใน `scripts/INDEX.md`
- เชื่อมโยงแนวทางการตรวจรับงานและสัญญาเฟรมใน `.agents/skills/resolve-delivery/`, `resolve-edit/`, `resolve-media-analysis/` และ `video-footage-review/`

### Verified
- ทดสอบ unit tests: `python -m pytest tests/test_edit_workflow.py` ผ่านครบ 37 รายการ
- ทดสอบทั้ง repo: `python -m pytest -q` ผ่าน 212 passed, 22 skipped, 10 subtests
- ตรวจสอบความถูกต้องของ skill bundle: `python scripts/verify_skill_bundle.py` ผ่าน 100%

### Scope
- ทุกเครื่องมือทำงานแบบ offline 100% โดยอ่านไฟล์และ JSON เท่านั้น ไม่ต่อ Resolve และไม่มีการดัดแปลง footage ต้นฉบับ

## v0.14.0

### Added
- เพิ่ม `docs/guides/resolve211-agent-guide.md` ให้ agent เลือก API และ MCP สำหรับ Resolve 21.1 โดยอ้างอิง build, schema และหลักฐานการตรวจที่ตรงกัน
- รวมเส้นทาง native สำหรับ speed/fades, transitions, multicam, audio normalization/alignment และ DCTL พร้อมลิงก์ไปยังคู่มือเฉพาะงาน

### Updated
- แก้ข้อความใน skills และคู่มือที่ระบุว่าไม่มี clip-speed API หรือ native multicam API ในทุกเวอร์ชัน ให้แยกข้อจำกัดของรุ่นเก่าจากความสามารถ 21.1
- แยกการสร้าง transition ออกจากการ clone และแยก native multicam creation/flattening ออกจาก stacked-timeline helper
- เพิ่มคำอธิบาย DCTL validation/encryption, Python ในตัว, settings แบบ TypedDict, ผลข้างเคียงของการเขียนหลายคีย์ และขอบเขตการตรวจ subtitle/render
- ตรวจ catalog ของ community MCP 4.13.1 ซึ่งมี 37 compound tools และกำหนดให้ตรวจ action schema ที่แนบในแต่ละ session
- ชี้แจง SHA-256 ของ vendor stub แบบ CRLF และ LF: เนื้อหาตรงกัน ความต่างของ hash ไม่ได้หมายความว่า API เปลี่ยน

### Verified
- ชุดไฟล์ release แยกจาก working tree: `python -m pytest -q` ผ่าน 175 tests, ข้าม 22 รายการ และผ่าน 10 subtests
- Community MCP รายงาน DaVinci Resolve Studio `21.1.0.17` และ MCP `4.13.1`; Studio MCP ยืนยันว่า Resolve `21.1` กำลังรันและเข้าถึงได้
- เปรียบเทียบ vendor stub ใน repo กับไฟล์ที่ Studio MCP ส่งมาได้ตรงกันแบบ byte-for-byte; เมื่อแปลง CRLF เป็น LF ค่า hash ตรงกับ provenance เดิม
- ตรวจลิงก์ภายใน คู่มือ และ manifest/checksums ก่อนเผยแพร่

### Scope
- ปรับ checksum เดิมที่ค้างใน manifest 3 รายการให้ตรงกับไฟล์ที่ติดตามอยู่ใน HEAD ได้แก่ helper subtitle preset และเอกสาร Armigon 2 ไฟล์ โดยไม่แก้เนื้อหาไฟล์เหล่านั้น
- รุ่นนี้ปรับ skills และเอกสาร ไม่ได้ทดลอง setters, แก้ timeline, render หรือเขียนฐานข้อมูล Resolve; หลักฐาน contributor บน macOS Build 14 ยังคงมีขอบเขตตามที่บันทึกไว้
- ไม่รวมงาน offline intake/edit workflow ที่ค้างอยู่ใน working tree ก่อนงานนี้
- เลขเวอร์ชันของ skill bundle แยกจากเวอร์ชัน DaVinci Resolve และ MCP server

## v0.13.0

เน้นให้ agent (Claude Code, Codex, Hermes) เริ่มงานเร็วขึ้นและไม่สร้างเครื่องมือซ้ำนอกโปรเจค

### เพิ่ม
- `CLAUDE.md` เป็นไฟล์ตัวชี้สั้นๆ ไป `AGENTS.md` (`@AGENTS.md`) เพราะ Claude Code อ่าน `CLAUDE.md` ไม่ใช่ `AGENTS.md`; กฎอยู่ที่เดียว Codex และ Hermes อ่าน `AGENTS.md` เหมือนเดิม
- `AGENTS.md` เพิ่มหัวข้อ "Start of task checklist" (ขั้น 0-4) และ "Finish of task: record what you learned" ใช้ได้กับทั้ง 3 agent
  - ขั้น 0: รัน `scripts/check_mcp_update.py` ก่อนเริ่มงาน
  - ขั้น 1: อ่านโปรไฟล์ช่องใน `docs/channels/` เมื่อผู้ใช้พูดถึงช่อง
  - ขั้น 3-4: ค้น `scripts/INDEX.md` ก่อน ห้ามสร้างเครื่องมือนอก repo; ถ้าไม่มีจริงให้เขียนใน `scripts/scratch/` พร้อมบรรทัด `MCP-GAP:`
- `scripts/INDEX.md` ตาราง "งาน -> script -> ขอบเขต" ครบ 115 script จัด 8 หมวด (พื้นฐาน, ซับไทย, VTuber Zoom/Focus, แปลง 9:16, Enrichment, QC/Review, Render/Export, จัดการโปรเจค) ติดป้ายขอบเขต `ใช้ซ้ำ` / `p2` / `armigon` / `sakuyako` / `ครั้งเดียว`
- `scripts/scratch/` (ติดตามเฉพาะ `.gitkeep`) ที่ทิ้ง script ชั่วคราวภายในโปรเจค แก้ `.gitignore` ให้ไม่ถูกกฎ `scratch/` เดิมบัง
- `scripts/check_mcp_update.py` ตรวจเวอร์ชัน MCP ชุมชน ([samuelgursky/davinci-resolve-mcp](https://github.com/samuelgursky/davinci-resolve-mcp)) เทียบ tag ล่าสุดผ่าน `git ls-remote`
  - อ่านโฟลเดอร์ที่ติดตั้งจาก `.mcp.json` ไม่ฝัง path
  - `--apply` ทำ `git fetch --tags`, `git checkout <tag>`, `pip install -r requirements.txt` และปฏิเสธเมื่อมีการแก้ค้างในโฟลเดอร์ MCP
  - สถานะผลลัพธ์: `UP-TO-DATE`, `UPDATE`, `BLOCKED`, `UNKNOWN` (ออฟไลน์)
- skill `project-learning` (`.agents/skills/project-learning/SKILL.md`) ขั้นตอนค้นเครื่องมือเดิมก่อนเขียนใหม่ และตารางว่าจบงานแล้วบันทึกอะไรลงไฟล์ไหน (OPERATING-NOTES, INDEX, house-style, โปรไฟล์ช่อง, AGENTS.md)
- `docs/channels/` โปรไฟล์ช่อง 7 ช่อง + สารบัญ: Katy404, Aomi-mama, Armigon, Tygarina, Sakuyako-Cheris, Laffy, Kael แต่ละไฟล์มี 8 หัวข้อ (ตัวตน, ที่เก็บไฟล์, โปรเจค/timeline, layout, ซับ/เสียง/enrichment, script/skill, กับดัก/งานค้าง, "ยังไม่ทราบ")
  - Laffy และ Kael ยังมีข้อมูลน้อย (ยังไม่พบ timeline หรือ script) ส่วนที่ไม่มีหลักฐานเขียนว่า "ยังไม่ทราบ" ไม่เดา
  - `aomimama.md` มีบทเรียนจากงานเดบิวต์ 30 ก.ย. 2026: เลย์เอาต์แนวตั้ง "Story", ค่า GIF แนวตั้งที่ผู้ใช้ยอมรับ, กฎซับ, ขั้นตอน sample gate
- กฎใหม่ใน `docs/OPERATING-NOTES.md`: audit ฟอนต์ต้องสแกนแบบ UTF-16 และห้ามอ่านค่า Text+ (Fusion) สดผ่านสคริปต์ (เคยทำให้ Resolve ค้าง) ให้อ่านจาก `.drp` ที่ export
- `patches/README.md` ระบุว่า patch เอกสาร MCP เดิมใช้กับ v4.13.x ไม่ได้
- `work/README.md` อธิบายโฟลเดอร์งานจริง
- test ใหม่ 3 ไฟล์: `tests/test_agent_entrypoints.py` (ทุก script ต้องอยู่ใน INDEX, ตรวจจุดเข้าของ agent), `tests/test_channel_profiles.py` (ครบ 7 ช่อง 8 หัวข้อ), `tests/test_check_mcp_update.py` (เรียงเวอร์ชันแบบตัวเลข, อ่านเวอร์ชันที่ติดตั้ง, ตัดสินใจ update/blocked, apply ใน repo ทดลอง)

### เปลี่ยน
- `.mcp.json` ชี้ MCP ที่ติดตั้งจริงที่ `Desktop/davinci-resolve-mcp` (เดิมชี้ `D:\` ที่ไม่มีอยู่) และตัด `PYTHONHOME` ที่ชี้ Python 3.13 ซึ่งไม่ได้ติดตั้งออก
- `AGENTS.md` ตัดรายการ script ยาวออก ชี้ไป `scripts/INDEX.md` และเลิกฝังเลขรุ่น MCP
- ย้าย `PLAN.md`, `PLAN-9x16.md`, `PROJECT.md`, `WORKLOG.md` ไป `work/` พร้อมอัปเดตลิงก์ใน README, OPERATING-NOTES, REVIEW
- `scripts/README.md` ชี้ไป INDEX และ `scratch/`
- รวม v0.12.0 จาก remote (script `sakuyako_*`, `drt_prepend_cover`, `build_9x16_day22/24` ฯลฯ) เข้า INDEX และโปรไฟล์ช่อง

### ลบ / เลิกติดตาม
- ลบโฟลเดอร์ `reference/` และที่เก็บถาวรภาพหนักของงาน Aomi-mama 30 ก.ย. (881MB) หลังสกัดบทเรียนลงโปรไฟล์ช่องแล้ว รายงานรีวิวกับ readback json ไม่มีสำเนา
- เลิกติดตามสำเนาฐานข้อมูลโปรเจค `backups/**/*.sqlite` (14 ไฟล์ ประมาณ 100MB) ใน git ไฟล์ยังอยู่บนดิสก์ และเพิ่มกฎใน `.gitignore`

### ผลการตรวจ
- `pytest`: 175 ผ่าน, 22 ข้าม (test `test_m1_*` ที่ต้องใช้ Resolve จริง ข้ามเมื่อไม่ใส่ `--live`), 197 collected
- `scripts/verify_skill_bundle.py`: `ok: true`, ไม่มี errors; manifest และ checksum อัปเดตด้วย `refresh_skill_manifest.py`
- อัปเดต MCP ชุมชน v4.10.3 -> v4.13.1 บนเครื่อง (ติดตั้ง dependency ผ่าน, import `server` ได้); `check_mcp_update.py` รายงาน `UP-TO-DATE`

### ข้อจำกัด
- ไม่ได้เชื่อมต่อหรือแก้ Resolve ในรุ่นนี้: ยังไม่ได้ทดสอบว่า MCP v4.13.1 คุยกับ Resolve ได้ (`resolve_preflight.py` ตอบ `BLOCKED` เพราะ Resolve ไม่ได้เปิด) ต้อง restart session แล้วลอง `resolve_control get_version`
- ข้อมูลในโปรไฟล์ช่องมาจากหลักฐานใน repo, memory และการดูโฟลเดอร์ต้นทางแบบอ่านอย่างเดียว ไม่ใช่การตรวจ Resolve สด ต้องยืนยันชื่อโปรเจค/timeline จาก Resolve ก่อนเขียนทุกครั้ง
- ป้ายขอบเขตใน INDEX จัดจากชื่อไฟล์และ docstring ไม่ได้อ่านโค้ดทุก script
- หัวข้อรายการ tool ใน skill `resolve-mcp` ยังอ้าง v4.10.4 (ยังไม่ได้ตรวจกับ v4.13.1)
- ไม่ได้ลดขนาด `.git` (ประมาณ 400MB เป็นประวัติเก่า) เพราะต้องเขียนประวัติใหม่และ force-push
- ไม่ได้แยก `scripts/` เป็นโฟลเดอร์ย่อย เพราะ import `scripts.xxx` 150+ จุดและยังไม่มีทางตรวจกับ Resolve จริง

## v0.12.0

### เพิ่ม
- เพิ่ม `scripts/build_9x16_day22.py` และ `scripts/build_9x16_day24.py` สำหรับสร้าง `<ชื่อเดิม>_9x16` (1080x1920) จาก timeline 16:9 ที่มี V1 / V2 Adjustment Clip / V3 GIF: เกมครึ่งบน, VTuber ขยายครึ่งล่าง, ช่วง focus เดิมเป็นหน้า VTuber เต็มจอ, GIF คงเวลาเดิม; dry run เป็นค่าเริ่มต้น และเทียบ subtitle/เสียง/ช่วง V1 กับต้นฉบับก่อนและหลังบันทึก
- บันทึกผลรันจริงวันที่ 24 ลงสกิล `resolve-video-enrichment` (focus zoom, enrichment BGM/SFX/GIF, แปลง 9:16) และ `docs/OPERATING-NOTES.md`: ค่า window ของ avatar มุมขวาล่าง, การคัด GIF ด้วย PIL ก่อนรัน, ผลข้างเคียงเมื่อรัน `apply_enrichment_d22` แล้วหยุดกลางคัน, การ list ไดรฟ์ Drive ด้วย `os.scandir`

### ผลการตรวจ
- ตรวจใน Resolve Studio 21.1.0.17 กับโปรเจกต์วันที่ 24 (1 timeline): แทรก Adjustment Clip 7 ช่วงและอ่านค่ากลับตรงแผน; เพิ่ม SFX 8, BGM 1, GIF 5 พร้อมอ่านค่ากลับ; สร้าง `_9x16` และเทียบ subtitle 105 cue, เสียง และ V1 กับต้นฉบับได้ตรงกัน; ต้นฉบับยังเป็น 1920x1080
- ตรวจภาพ still ที่ Resolve render: 8 จาก 21 เฟรม (focus), 4 เฟรม (GIF), 5 เฟรม (9:16) ไม่พบแถบดำ ใบหน้าและผมส่วนโด่งอยู่ในเฟรม
- ข้อจำกัด: ไม่ได้ฟังเสียงหรือ render ช่วงเต็ม, ภาพ still ไม่มี subtitle จึงยังไม่ยืนยันการทับของ subtitle บนจอแนวตั้ง, ไม่ได้เทียบเปิด/ปิด Adjustment Clip, ไม่ยืนยัน license ของไฟล์ SFX/BGM/GIF
- รวมสคริปต์จากงานอื่นที่ค้างใน working tree ด้วย (`sakuyako_*`, `drt_prepend_cover`, helper subtitle preset, การแก้ `scripts/README.md` และ `p2_export_final.py`) เพื่อให้ manifest ตรงกับไฟล์จริง; มีเฉพาะ `tests/test_drt_prepend_cover.py` (3 เทสต์ผ่าน) ที่ได้รัน ส่วนสคริปต์เหล่านี้ยังไม่ได้ QC ใน Resolve ในรีลีสนี้

## v0.11.0

### เพิ่ม
- เพิ่มกฎใน `house-style` ให้ยึด subject ที่ผู้ใช้ระบุหรือชี้ในภาพอ้างอิงเป็น focus target แทนการสมมติว่าเป็น VTuber เสมอ
- เพิ่มชุด helper สำหรับ pilot/ปรับ layout 9:16 ของ Armigon, retarget/reframe focus, ตรวจ source range/audio/publish แบบอ่านอย่างเดียว และเตรียมแผนแก้ caption แบบ offline พร้อม geometry test
- ปรับ bundle validator ให้ normalize line ending ของไฟล์ Graphviz `.dot` เพื่อให้ checksum ผ่านเหมือนกันข้ามระบบปฏิบัติการ

### ขอบเขต
- สคริปต์ชุดนี้ผูกกับ project/timeline IDs เฉพาะและยังไม่ได้รันหรือ QC ใน Resolve ในการเตรียมรีลีสนี้; ไม่ได้เชื่อมต่อหรือแก้ project, render หรือฐานข้อมูล Resolve

## v0.10.0

### เพิ่ม
- เพิ่มสกิลเสริม 29 ชุดใน `.agents/skills/` (workflow จากโปรไฟล์ 14 ชุด และ Superpowers v7.0.0 จำนวน 15 ชุด) โดยแยก `supporting` ออกจากสกิลตัดต่อหลัก 17 ชุดใน manifest
- เพิ่มคำอธิบายจำนวนสกิลและขอบเขตการเปิดใช้งานใน README/operating notes และปรับคู่มือการเผยแพร่ให้ใช้ tag สูงสุดเป็นฐาน พร้อม release title ภาษาไทย

### ปรับปรุง
- ปรับกฎ Resolve ให้ตรงกับ `AGENTS.md`: ไม่ใช้ FFmpeg แปลงสื่อหรือ API ที่ยังไม่ยืนยัน, ระบุ dependency ภายนอก, ขออนุญาตก่อนส่งภาพ/วิดีโอไปผู้ให้บริการภายนอก และจำกัดการเขียน preset ลงฐานข้อมูลจนกว่าจะรับประกันได้ว่า Resolve ปิดสนิท
- ให้ helper preset ใต้สกิลส่งต่อไปยัง helper กลางของโปรเจกต์ และบล็อกการเขียน Project.db ที่ยังไม่มี shutdown guard
- ทำให้การ resume export เชื่อถือเฉพาะงาน Resolve สถานะ `Complete` ที่ไฟล์ผ่านการตรวจ stream/ขนาด/ระยะเวลา และการเทียบ cover สำหรับแนวตั้ง พร้อมหยุดเมื่อพบไฟล์ output หลายชนิดที่ใช้ชื่อฐานเดียวกัน
- แก้ลิงก์ข้ามสกิล Superpowers ให้สัมพันธ์กับโฟลเดอร์จริง และปรับแนวทางล้าง worktree ให้เก็บหลักฐาน review/ledger ไว้
- อัปเดตแผนผัง community MCP จาก v4.10.3 เป็น v4.10.4 ตามข้อมูลในโปรเจกต์

### ผลการตรวจ
- `scripts/verify_skill_bundle.py` ผ่านโดยไม่มี errors: manifest 559 ไฟล์, ลิงก์ภายใน 90 จุด, สกิล active 17 core + 29 supporting = 46 และ archive 13 ชุด; รายงาน 14 ลิงก์ตัวอย่างจากคู่มือภายนอกเป็น exception ที่บันทึกเหตุผลไว้
- ตัวสแกน Hermes ใช้งานไม่ได้ใน environment นี้ จึงตรวจเฉพาะโครงสร้าง/frontmatter, references และ checksums; ไม่มีการรัน unit tests, เชื่อมต่อ Resolve, แก้ project database หรือทดสอบ render ในการเตรียมรีลีสนี้
- ผล validator ไม่ใช่หลักฐานว่า Resolve scripts หรือภาพที่ render ทำงานถูกต้อง

## v0.9.0

ชุดสกิลและสคริปต์ช่วยงานตัดต่อรุ่นนี้แยกเลขรุ่นจาก DaVinci Resolve และ MCP server

### P2 และการจัดภาพ 9:16
- เพิ่มชุด `p2_9x16_*` สำหรับสำรวจ source, สร้างและแปลง timeline, จัดส่วนเกม/ตัวละคร, ตรวจ cut และตรวจโครงสร้างหลังแปลง รวมถึงการรับสำเนา 1080×1920 ที่ตั้งค่าด้วยมือหรือ MCP และโหมด raster ช้า
- เพิ่มตัวลบ stray copy ตามขอบเขตที่ระบุ และการตรวจทุก timeline หลังเปลี่ยนเพื่อช่วยจับการคลาดเคลื่อนของแทร็กและช่วงภาพ

### ซับไทยและ QC ก่อนเผยแพร่
- เพิ่มเครื่องมือสร้าง cue จากข้อมูลต้นทางและ sample, ใช้ cue กับ native subtitle track, แก้กฎข้อความ/ช่วงเวลา และใช้ซับที่แก้แล้วได้ทั้งแนวตั้งและแนวนอน
- เพิ่ม `p2_publish_qc.py`, การตรวจซับหลังแก้, still และ audio QC เพื่อจัดหลักฐานก่อนเผยแพร่; `caption_lint.py` ตรวจข้อกำหนดซับไทยแบบอ่านอย่างเดียว

### VTuber focus และ QC
- เพิ่มตัววางแผน/ใช้ zoom focus ของ P2 พร้อม rollback, เครื่องมือสร้างและย้ายแทร็ก `Adjustment Clip` ผ่าน DRT, ตัวตรวจเฟรม/โครงสร้าง focus และ pilot Armigon บนสำเนา
- รายงาน QC Armigon ใน Resolve Studio 21.1.0.17 ที่ 1920×1080/60 fps ตรวจ `Adjustment Clip` 48 รายการ พบ `MotionBlur=0` ทั้งหมด; อ่าน `Center`/`Size` รวม 192 input โดยไม่พบ keyframe ใน input ที่ตรวจ
- T74–T77 เป็น VTuber ผมชมพูอีกคน จึงคืนค่าเฉพาะ V2 focus ให้เป็นกลางและอ่านค่ากลับแล้ว; T1 เฟรม 2261 และ T70 เฟรม 1839 มีภาพ still A/B เปิด/ปิด V2 ในเวลาเดียวกัน เขาด้านขวาถูกตัดใน source อยู่แล้ว และสติกเกอร์ผมขาวใน source ของ T70 บังมือ/ลำตัวบางส่วน การลอง `X=-0.06` ไม่แก้เขา จึงคืน T70 เป็น `X=-0.03`
- ภาพ still ที่ตรวจไม่พบขอบดำหรือ blur ที่ zoom เพิ่มขึ้น แต่ไม่ใช่หลักฐานว่า motion ทุกเฟรมไม่มีอาการสั่น และไม่ได้ตรวจวิดีโอ render เต็มช่วง รายละเอียดและขอบเขตหลักฐานอยู่ที่ `docs/superpowers/reports/2026-10-12-armigon-focus-qc-th.md`

### GIF, การตัดท้าย และการส่งออก
- เพิ่มการย้าย GIF บน V2 ให้อยู่ในแผงเกมเหนือรอยต่อ avatar ของ 9:16 โดยคำนึงถึง V3 ที่วาดทับ V2; เพิ่มเครื่องมือตัด GIF ท้ายที่ผิดและสร้าง timeline รุ่น `_150s` โดยลบ cue ที่เลยหรือคร่อมจุดตัดตามนโยบายสคริปต์
- เพิ่มชุด render แนวตั้ง/แนวนอน, ตัวช่วย loudness ของแต่ละสัดส่วน และ `p2_export_final.py` สำหรับเตรียม export หลาย timeline ด้วย `H.264 Master` พร้อม readback/การตรวจผลที่สคริปต์กำหนด; การมีสคริปต์ไม่ใช่หลักฐานว่าไฟล์ส่งออกทุกชิ้นผ่าน QC แล้ว

### ขอบเขตเครื่องมือและสกิล
- ปรับ `AGENTS.md` และสกิล Resolve ให้บังคับใช้ Resolve MCP ก่อน แล้วจึงใช้ Python Scripting API เมื่อมีหลักฐานช่องว่าง; เพิ่มแผนผังเครื่องมือ MCP v4.10.4 และคำแนะนำ subtitle/conform/focus QC ล่าสุด
- เพิ่มกฎ house style และ `adjustment-focus.md` ให้ยืนยันตัว Armigon, อ่าน transform/`MotionBlur`, เทียบเฟรมเดียวกันเมื่อเปิด/ปิด focus และแยกปัญหา source ออกจากผล zoom

### เพิ่มเติม
- `scripts/caption_lint.py`: ตรวจ SRT ภาษาไทยแบบ read-only ตามกฎซับสั้น (ไม่เกิน 14 อักษรไทยและ 1.5 วินาทีต่อ cue, ไม่เว้นวรรคระหว่างอักษรไทย, ไม่เกิน 2 บรรทัด) คืน exit code 1 เมื่อมีข้อผิดกฎ; ชี้จาก `thai-subtitles-resolve`
- `scripts/backup_drp.py`: `export_verified` / `verify_drp` สำหรับ export `.drp` แล้วตรวจว่าไฟล์ไม่ว่างและเป็น zip ที่สมบูรณ์
- `tests/conftest.py`: ข้ามเทสต์ `test_m1_*` ที่ต้องมี Resolve จริง เว้นแต่ใส่ `--live`
- `tests/test_caption_lint.py`, `tests/test_backup_cleanup.py`

### แก้ไข
- `scripts/cleanup_backups.py`: เดิมลบ `.drp` ทุกไฟล์ในโฟลเดอร์ รวมถึงไฟล์ rollback (`pre-enrichment`, `before_promotion_`) เพราะ `KEEP_MARKERS` / `DELETE_PREFIXES` ไม่ถูกใช้และ `--keep-rollback` ไม่ทำอะไร; ตอนนี้ลบเฉพาะชื่อที่ขึ้นต้นด้วย `before_python_batch_` / `before_python_vdo_` เท่านั้น ไฟล์อื่นรายงานเป็น kept / skipped_unmatched (ยังเป็น dry-run ถ้าไม่ใส่ `--confirm`)
- `scripts/promote_drafts_to_originals.py`: เดิมเขียน report ทับก่อนอ่านสถานะรอบก่อน ทำให้ตรวจ "promoted_verified" ไม่เคยได้ผล; ตอนนี้อ่านก่อน, คงรายการ `added` เดิม และ dry-run ไม่ลบบันทึกการ promote ที่ยืนยันแล้ว
- `scripts/focus_apply_batch.py`, `scripts/focus_tune.py`: เพิ่ม bootstrap path ให้รันตรงด้วย `python scripts/<ชื่อ>.py` ได้ (เดิมได้ `ModuleNotFoundError`; `python -m scripts.<ชื่อ>` ใช้ได้อยู่แล้ว)
- `scripts/resolve_common.py`: `preserved_state` คืน Media Pool folder ด้วย และรายงานบน stderr เมื่อคืนค่าขั้นใดไม่สำเร็จ แทนการกลืน exception เงียบๆ
- ลบ import / ตัวแปรที่ไม่ใช้ (pyflakes สะอาด)

### ย้ายออก
- ย้ายออกไป `Desktop/_archive-davinci-cleanup-2026-10-09/scripts-review-2026-10-09/` (ไม่ได้ลบ): สคริปต์งานครั้งเดียว `render_t02_candidate`, `render_lowerleft_16_42`, `render_bottomleft_batch`, `render_headroom_tune`, `apply_focus_candidate`, `apply_bottomleft_candidates`, `tune_focus_headroom`, `focus_set_transform`; ชุดย้าย 9:16 รอบ M2/M3 `m2_convert_pilot`, `m3_convert`, `calibrate_crop`, `calibrate_zoom`, `compare_invariants`, `survey_sources`, `export_source_stills`, `layout9x16`, `split_projects`, `challenger_m2_1_results.json`; และเทสต์ live `test_m2_*`, `test_m3_*`
### การตรวจ
- ในการเตรียมรีลีสครั้งนี้ รัน `python scripts/verify_skill_bundle.py` ได้ `ok: true`, `errors: []`, 449 ไฟล์ใน manifest และ 73 ลิงก์ภายใน; ผลอยู่ใน `docs/validation-report.json` (ตัวสแกน Hermes ไม่พร้อม จึงเป็นการตรวจโครงสร้าง/checksum) รัน `git diff --check` ผ่านด้วย
- รายงาน Armigon ข้างต้นเป็นหลักฐาน QC ที่บันทึกไว้ก่อนหน้านี้ ไม่ใช่การทดสอบสดของสคริปต์ทั้งหมดในรีลีสนี้ ไม่มีการเชื่อมต่อ Resolve หรือตรวจวิดีโอ render เต็มช่วงในการเตรียมรีลีสครั้งนี้

## v0.8.0

### Added
- `scripts/resolve_common.py`: เพิ่ม `require_resolve()` ที่จบโปรแกรมพร้อมข้อความชัดเจนเมื่อเชื่อมต่อ Resolve ไม่ได้ และ `preserved_state(resolve)` ที่คืนโปรเจกต์ ไทม์ไลน์ playhead และเพจให้เหมือนเดิมเมื่อจบงาน (คืนค่าได้แม้เนื้อหาข้างในล้มเหลว)
- `scripts/resolve_preflight.py`: เพิ่มตัวเลือก `--list-tools` สำหรับดูรายชื่อ tool ใน catalog ของ MCP; ไม่ต้องใส่ `--need` เมื่อใช้ตัวนี้
- `scripts/README.md`: จัดกลุ่มเครื่องมือทั้งหมด พร้อมลำดับการใช้งาน (MCP ก่อน แล้ว preflight แล้วค่อยสคริปต์)
- `tests/test_resolve_common.py`: ทดสอบ `preserved_state` และ `require_resolve` ด้วย Resolve จำลอง
- `.agents/skills/resolve-mcp/SKILL.md`: เพิ่มตาราง "Live tool map" ที่บอกว่างานแต่ละอย่างใช้ tool ของ `davinci-resolve` MCP ตัวไหน และขั้นตอนตรวจ MCP ทางการของ Resolve (`get_whats_new`, `search_scripting_api`, `run_script`) ก่อนเขียนสคริปต์เอง

### Updated
- `scripts/resolve_common.py`: ค้นหาโมดูล Resolve จาก `C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules` ด้วย
- `scripts/apply_vdo_preset.py`, `scripts/load_subtitle_preset.py`, `scripts/split_projects.py`: เลิกเขียนตัวเชื่อมต่อเอง ใช้ตัวกลางใน `resolve_common` แทน (คงชื่อ `connect_resolve` ใน `load_subtitle_preset.py` เพราะ `apply_video_style.py` เรียกใช้)
- `scripts/apply_bottomleft_candidates.py`, `render_bottomleft_batch.py`, `render_headroom_tune.py`, `render_lowerleft_16_42.py`, `render_t02_candidate.py`, `tune_focus_headroom.py`: แตกคำสั่งบรรทัดเดียวที่ต่อกันด้วย `;` ให้เป็นบรรทัดแยก ตรรกะเหมือนเดิม (ตรวจโครงสร้างโค้ดตรงกันทุกไฟล์) ยังไม่ได้ทดสอบกับ Resolve จริง
- `scripts/refresh_skill_manifest.py`: `bundle_version` เป็น 0.8.0
- `docs/skills-manifest.json` และ `docs/validation-report.json`: สร้างใหม่หลังจัดระเบียบไฟล์

### Removed
- ย้ายสคริปต์ทดลอง/ใช้ครั้งเดียวที่ไม่มีเอกสาร สกิล หรือเทสต์อ้างถึง 73 ไฟล์ออกจาก repo ไปไว้ที่ `Desktop/_archive-davinci-cleanup-2026-10-09/scripts/` (ไม่ได้ลบทิ้ง) รวมถึงชุด VTuber focus เก่า ไฟล์ `dbg_*`, `diagnose_*`, `probe_*`, `test_v*`, `test_challenger_*` และ `aomimama_*`
- ย้ายสกิลทั่วไปสำหรับงานเขียนโค้ด 38 ตัว (จาก `mattpocock/skills` เช่น `tdd`, `wizard`, `teach`) ออกจาก `.agents/skills/` ไปไว้นอกโปรเจกต์ ทำให้เหลือสกิลของ Resolve, house-style และสกิลภาษาไทย 17 ตัว
- ลบโฟลเดอร์ `scratch/` (ไฟล์ทดลองและภาพนิ่ง ไม่เคยอยู่ใน git)
- ลบ `skills-lock.json` ที่ว่างเปล่า

### Validation
- `python scripts/verify_skill_bundle.py` — `ok: true`
- เทสต์ที่ไม่ต้องใช้ Resolve จริง — ผ่าน 105 รายการ ล้มเหลว 1 รายการ (`test_review_analysis_budget.py` ต้องใช้โมดูล `agent` ของ Hermes ที่ไม่มีในเครื่อง)
- `tests/test_m1_*`, `test_m2_*`, `test_m3_*` ไม่ได้รัน; `test_m1_backup_empirical` และ `test_m1_baseline_validation` ล้มเหลวเพราะไฟล์เก่ากว่า 24 ชั่วโมงและผูกกับโปรเจกต์ KT404
- ยังไม่ได้ทดสอบสคริปต์ที่แก้กับ Resolve จริง

## v0.7.0

### Added
- ชุดเครื่องมือออฟไลน์สำหรับตรวจและเพิ่ม SFX/BGM/GIF ให้ทุก Timeline โดยไม่ใช้ API วิเคราะห์วิดีโอ: `scripts/review_enrichment_readonly.py`, `scripts/build_offline_review.py`, `scripts/build_offline_asset_draft.py`, `scripts/resolve_preflight.py`, `scripts/resolve_common.py`
- `scripts/apply_vdo_python.py`: จับค่าที่เปิดเผยของ GIF ที่โหลด preset `vdo` แล้วด้วย UI แล้วใช้กับ GIF ตาม project/timeline/clip ID; dry-run เป็นค่าเริ่มต้น ต้องมี DRP backup ก่อนเขียน และคืน UI state
- `scripts/enrich_timelines_python.py`: เพิ่ม SFX/BGM/GIF บนสำเนา Timeline ด้วย Resolve Python; dry-run เป็นค่าเริ่มต้น, ไม่มีจุดจากซับที่พอจะเสนอ BGM อย่างเดียวโดยไม่แต่งจังหวะมุกขึ้นเอง, คง GIF เดิมที่ทับช่วงไว้
- `scripts/promote_drafts_to_originals.py`: ย้ายงานที่ตรวจแล้วเข้าต้นฉบับตาม ID จริง ทำซ้ำได้ (นับ (ชื่อ asset, record frame) ที่มีอยู่แล้วเป็นรายการเดิม) และปฏิเสธเมื่อต้นฉบับไม่ตรง baseline
- `scripts/anomaly_sweep.py`: ตรวจความผิดปกติทั้งโปรเจกต์แบบอ่านเท่านั้น (ช่วงเวลา คลิปหลุดขอบ คลิปซ้อน คลิปซ้ำ ไฟล์ต้นทางหาย GIF นานเกิน ค่า `vdo` ความยาว BGM จำนวนซับ)
- `scripts/cleanup_backups.py`: export `.drp` ใหม่ที่ตรวจแล้วหนึ่งไฟล์ก่อนลบ archive
- `scripts/refresh_skill_manifest.py`: สร้าง `docs/skills-manifest.json` ใหม่จากไฟล์จริง (เพิ่ม/ลบ/อัปเดต checksum และเรียก validator ต่อ)
- `scripts/apply_offline_enrichment_pilot.py`, `scripts/render_enrichment_pilot.py`, `scripts/render_review_previews.py`, `scripts/verify_review_resume.py`, `scripts/delete_draft_copies.py`, `scripts/audit_promotion.py`, `scripts/audit_draft_copies.py`, `scripts/export_enrichment_backup.py`, `scripts/finish_timeline1.py`, `scripts/reapply_pilot_original.py`, `scripts/smoke_offline_review.py`, `scripts/smoke_alternative_video.py`, `scripts/run_draft_batches.sh`, `scripts/run_promotion_batches.sh`
- tests ออฟไลน์ 10 ไฟล์ (`tests/test_offline_*.py`, `tests/test_apply_vdo_python.py`, `tests/test_enrich_timelines_python.py`, `tests/test_render_enrichment_pilot.py`, `tests/test_resolve_preflight.py`, `tests/test_review_analysis_*.py`, `tests/test_review_resume_cache.py`)

### Updated
- `.agents/skills/resolve-video-enrichment/references/automation-safety.md`: เพิ่มหัวข้อ draft-then-promote ที่บันทึกจากของจริง 4 ข้อ — ลำดับสำเนาก่อนต้นฉบับ, การย้ายแบบ idempotent, Resolve conform GIF สั้นกว่าที่ขอ 2 เฟรม จึงต้องตรวจช่วงจริงไม่ใช่ค่าที่ขอ, และ native subtitle item ไม่มี Media Pool entry (เคยทำให้ sweep รายงานผิด 960 ครั้ง)
- `resolve-video-enrichment` (SKILL.md + house-style): กฎ native Subtitle-only, ขอบเขต style ที่ผู้ใช้ถือเอง, และ Thai cue cap 1.5 วินาที ตรงกับไฟล์ที่ลงทะเบียนใน manifest
- `docs/OPERATING-NOTES.md`: เพิ่ม 6 กฎที่วัดได้ + ตารางเครื่องมือ + ย้ำว่าเส้นทางออฟไลน์ไม่พึ่ง provider ใด
- `README.md`: เพิ่มขั้นตอน 9 ขั้นพร้อมคำสั่งจริง และข้อจำกัดที่ต้องรายงานเสมอ
- `docs/skills-manifest.json` (237 ไฟล์, bundle_version 0.7.0) และ `docs/validation-report.json` — สร้างใหม่หลังจัดระเบียบไฟล์
- `.gitignore`: เพิ่ม `.hermes/` สำหรับไฟล์งานเฉพาะเครื่อง

### Removed
- ลบ artifact งานภายใน 1,379 ไฟล์ที่เลิกใช้แล้วออกจาก index: `.agents/teamwork/**` (บันทึกประสานงาน/audit), `reference/**` และ `scratch/**` ซึ่ง `.gitignore` กันไว้อยู่แล้ว (`*.drp`, `*.mp4`, `*.mov` ยังคงถูก ignore)

### Validation
- `python scripts/verify_skill_bundle.py` — `ok: true`, `errors: []`, 237 manifest files, 17 core skills, ลิงก์ในโปรเจกต์ 65 จุด
- `python -m unittest tests.test_skill_bundle` — ผ่าน 9 tests
- tests ออฟไลน์ของ helper ใหม่/ที่แก้ — ผ่าน 33 tests
- ตรวจ path ที่อ้างใน `README.md` และ `docs/OPERATING-NOTES.md` ด้วยสคริปต์ — 12/12 มีอยู่จริง
- `git diff --check` — สะอาด

### Scope
- งานนี้คือชุด skills, คู่มือ, เครื่องมือออฟไลน์ และการจัดระเบียบไฟล์ในรีโป ไม่ได้เปลี่ยนซอร์สฟุตเทจหรือโปรเจกต์ Resolve ระหว่างจัดทำ release
- 8 test modules ที่ต้องใช้ `pytest` (`test_enrichment_assets`, `test_enrichment_engine`, ชุด `m1`–`m3`, `test_pilot_readback`) ยัง import ไม่ได้ใน interpreter นี้เพราะไม่มีแพ็กเกจ — เป็นสภาพเดิมก่อนงานนี้ ไม่ได้แก้และไม่ปิดบัง
- `.hermes/` (ผลตรวจ, รายงาน, render, `.drp`) ถูก ignore จึงไม่เข้า bundle
- ยังไม่ผ่านการตรวจภาพ/ฟังเสียงจริงของทั้ง 49 Timeline และยังไม่ได้ยืนยันสิทธิ์ของ asset ที่ใช้

## v0.6.0

### Added
- `scripts/apply_video_style.py`: capture and apply exposed video properties from an approved reference clip to explicit timeline item IDs. Dry-run is the default; writes require a verified DRP backup and include property readback, rollback, protected timeline comparisons, and UI-state restoration. It is not a native named Video Preset loader and makes no Resolve database writes.
- Offline orchestration coverage for project/timeline ID refusal, invalid backup refusal, and successful save/readback/restoration. `docs/guides/video-style-script.md` and a sanitized example at `presets/video/approved-gif-style.json` contain no live project clip ID or filename.
- `.agents/skills/thai-subtitles-resolve/references/srt-insertion-and-presets.md` with SRT insertion, exact saved-preset discovery, database-write boundaries, and post-load verification.

### Updated
- `thai-subtitles-resolve` v0.4.0 now documents reuse of Media Pool SRT items, exact cue/frame readback, failure-safe append recovery, and approved saved font presets.
- House style, `resolve-edit`, `resolve-video-enrichment`, operating notes, and README clarify approved preset use and distinguish native APIs from database workarounds.

### Validation
- `python -m unittest discover -s tests -p test_apply_video_style.py -v` — 10 tests passed.
- The helper was live-verified against explicitly approved GIF items during development; this release preparation did not connect to or modify a Resolve project.

### Scope
- Editing-skill bundle and helper documentation only. No source media, Resolve project, or database was changed for this release. Caption/GIF visual review and listening QC remain separate checks.

## v0.5.0

### Added
- `scripts/apply_vdo_preset.py` + `scripts/video_presets.json`: applies the Inspector Video preset "vdo" to GIF items on the V2 REACTIONS track. Resolve 21.1 has no API for Inspector > Video Presets > Load Preset and `User.db` does not expose the preset body, so the script writes captured property values (Zoom 0.42 gang, Pan 0, Tilt 32.28, others default) with `SetProperty`. Dry run by default; `--apply`, `--timeline`, `--only-originals`, `--track-name`, `--capture NAME` (captures from the clip under the playhead).
- `resolve-video-enrichment/references/horizontal-gif-placement.md`: 16:9 GIF placement, the measured Pan/Tilt-to-pixel model (X shift = Pan*fitted_w/1920, Y shift = Tilt*fitted_h/1080), GIF import timing (Resolve 25 fps normalization, 1.5s minimum), per-timeline loudness-based BGM/SFX levels.

### Updated
- Synced `resolve-video-enrichment` with the live Hermes copy (also brings the previously unsynced `katy404-channel-study.md`, `vertical-9x16-conversion.md`, `assets/` and edits to `asset-library-and-cues.md`, `automation-safety.md`, `illustration-assets.md`).

### Verified
- Live on Resolve Studio 21.1.0.17, project `tygarina_2026-09-30_FreeTalk_1`: preset applied to 63 of 64 GIF items (10 originals + 10 `[ENHANCED]` copies; 1 already matching), 0 failures, repeat dry run reports 0 changes, active timeline/playhead/page restored.
- Enrichment of the same 10 timelines (SFX/BGM/GIF added to originals and copies, protected V1/A1/subtitle ranges unchanged) was read back; a 3-timeline pixel check confirmed GIF bounding boxes before the preset was applied.

### Scope
- Not a real Load Preset: the preset values are a captured clone; re-capture if "vdo" changes. No listening QC, no render, and no per-file license check of the BGM/SFX/GIF assets was done.
- `tests/test_skill_bundle.py::test_bundle_structure_references_and_checksums` was already failing before this release (core skill count 16 vs 18 and an out-of-date file manifest); `docs/skills-manifest.json` was not refreshed here.

## v0.4.0

### Added
- `scripts/load_subtitle_preset.py`: loads a saved Subtitle track preset (Inspector > Load Preset) by script. Resolve 21.1 has no preset API, so it copies the preset bytes (`User.db` `SubtitlePresetsBA`) into each target track's `EffectFiltersBA` in `Project.db`. Dry run by default; `--apply` saves, exports a `.drp`, closes the project, snapshots `Project.db`, writes one transaction, reopens, restores timeline/playhead/page and verifies blobs and cue counts.
- `--orientation horizontal|vertical` selects timelines by resolution (Mitr Font for 16:9, Mitr-short-001 for 9:16 in the user's library).
- `tests/test_load_subtitle_preset.py`: offline tests for blob parsing/round-trip and exact-row database writes.

### Verified
- Applied `Mitr Font` to 10/10 subtitle tracks of project `tygarina_2026-09-30_FreeTalk_1` (8 changed, 2 already matching); cue counts unchanged; repeat dry run reports 0 changes. The vertical path is dry-run tested only.

## v0.2.0

### Added
- `resolve-video-enrichment/references/adjustment-focus.md`: using the user's selected Adjustment Clip as a protected template (selection readback, copy rather than move, per-timeline templates) and a 9-point per-cue VTuber framing checklist (subtitle association, new-track placement, prominence, centering, head-to-chest/hands, headroom, no crop, caption/HUD overlap, scope audit).
- `resolve-video-enrichment/references/illustration-assets.md`: planning, rights, organization, import, placement, and QC of still-image overlays.
- KT404 enrichment tooling: `scripts/enrichment_assets.py`, `scripts/enrichment_engine.py`, `scripts/run_pilot.py`, with tests, plus the design spec and implementation plans under `docs/superpowers/`.
- Working references and QC evidence under `reference/` and `scratch/`.

### Updated
- Synced `resolve-video-enrichment` with the live Hermes copy: per-timeline `timelineFrameRate` for record/source conversions, full-length BGM and 1.5–2.5s GIF holds, and new Thai trigger phrases.
- Bundle manifest checksums and counts refreshed for the release contents.

### Scope
- No claim of live Resolve verification for the new guidance; the pilot tooling's own results are recorded in `WORKLOG.md`.

## v0.1.0

First versioned release of the DaVinci Resolve editing skill bundle. The bundle version is independent of Resolve, the upstream MCP server, and individual archived skill versions.

### Added
- Thai VTuber editorial guidance: selecting self-contained highlights, truthful hooks, comic timing, and preserving the creator's personality.
- On-demand chapters for Resolve editing, Thai captions/audio/framing, YouTube packaging/feedback, and delivery/rights, with primary-source references.
- A reusable edit brief, cutlist, experiment plan, and acceptance-record template.

### Updated
- Expanded `resolve-video-enrichment` into a lean core with 11 reference chapters and one template, retaining the existing enrichment/recovery workflows.
- Clarified native subtitles versus burned-in pixels, evidence-led cue placement, measured audio versus scripting capability, source-frame timebases, and approval-gated repair/cleanup.
- Preserved the project's native Subtitle-track workflow and Thai short-form limits: three short words/about 14 Thai characters, at most 1.5 seconds, and no spaces between Thai words except appropriate Latin boundaries.
- Refreshed bundle provenance/checksums and validation evidence for the release contents.

### Fixed
- Bundle validation now accepts Git's LF/CRLF conversion for UTF-8 text while still rejecting content changes and preserving exact binary checksums; regression tests cover both newline directions and binary changes.

### Scope
- Skills, documentation, and bundle-validation release only: no MCP implementation, Resolve project, source media, or live editing behavior was changed.
- No claim of proven audience growth, channel-specific analytics, or live Resolve verification.
- Unrelated local editing plans, worklogs, scratch reports, media, and project backups are not part of this release change.
