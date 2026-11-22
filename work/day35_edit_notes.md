# day 35 — โน้ตเตรียมตัด (opencode, 2026-11-22)

ตรวจแบบ read-only ทั้งหมด ยังไม่ได้แก้ timeline

## โปรเจค/ไทม์ไลน์ (baseline ก่อนแก้)
- โปรเจค `วันที่ 35 ปลูกข้าวจนกว่าจะ 10K ผู้ติดตาม - Katy404` id `7437e343-d6b1-4f4c-9dd8-bb9ed2bdb3ef`
- `Timeline 1` id `b6b0e906-5936-475f-b940-b10f778bca62`: 1920x1080@60, 48 kHz, 3,760 เฟรม (62.667 วิ), start TC 00:00:00:00
- V1/A1 = คลิปเดียว `2026-11-22 22-28-34.mp4` record 0-3760 = source 0-3760 (ใช้เต็มไฟล์) — ยังไม่มี Subtitle track, ไม่มี V2/V3, ไม่มี marker

## ไฟล์ต้นทาง
- `G:\My Drive\Projects\Katy404\Mincecraft_100_day\วันที่ 35 ปลูกข้าวจนกว่าจะ 10K ผู้ติดตาม - Katy404\2026-11-22 22-28-34.mp4` (Online)
- 2560x1440@60 h264 + AAC 48k stereo, 62.667 วิ, 283,335,284 ไบต์ (~36 Mbps) — ตรงสเปกช่อง (day 31 ก็ 2560x1440@60 บน 1080p60)

## เสียง (ffmpeg loudnorm วัดจากไฟล์ต้นทาง)
- input_i **-29.41 LUFS**, true peak **-8.23 dBTP**, LRA 6.80, thresh -39.86
- ต้นทางเงียบกว่าเป้า YouTube (~-14 LUFS) เกือบ 15 dB → ตอนมิกซ์ใช้สูตร day 31: Dialogue Leveler (ReduceLoud + LiftSoft) + AudioVolume แล้ววัดซ้ำตอน render QC (เป้า ~-14 LUFS, TP <= -1 dBFS)

## จุดเงียบ (silencedetect noise=-35dB d>=0.35 วิ) — ใช้เป็นตัวเลือกจุดตัด ยังไม่ได้ดูภาพ/ฟังเสียง
- หัวคลิป: 0.00-0.95 | 1.93-2.61 | 3.40-4.27 | 4.67-5.35 | 7.06-7.76 (ช่วง 0-8 วิ เงียบถี่ — เกริ่น/เมนู ตามสไตล์ day 30 ที่ตัดหัว 2.8 วิ)
- กลางคลิป: 10.77-11.22 | 17.90-18.27 | 19.57-20.03 | 21.13-21.50 | **28.26-29.68 (ยาวสุด 1.42 วิ)** | 36.18-36.55 | 37.08-37.64 | 39.74-40.13 | 42.01-42.71 | 48.85-49.20 | 56.56-57.09 | 59.28-60.20
- ท้ายคลิป: 61.24-62.63 (1.39 วิ)

## สำรองก่อนแก้
- `backups/day35_pre_edit_20261122.drp` — 36,669 ไบต์, zip test ผ่าน (4 members) export ผ่าน MCP `project_manager export_project`

## คิว Resolve
- ตอนตรวจ: antigravity (editor หลัก) สถานะ working → opencode ไม่แตะ timeline เพื่อไม่ให้เขียนชนกัน
- opencode พร้อมรับช่วงตัด (backup editor) หรือรัน render + ffprobe QC ทันทีที่ timeline พร้อม

## สถานะ MCP
- `scripts/check_mcp_update.py` = **BLOCKED** (install มี local changes ที่ `D:\davinci-resolve-mcp`) — รายงานตาม AGENTS.md ไม่บังคับอัปเดต
- MCP server ตอบได้: Resolve Studio 21.1.0.17, MCP 5.3.1 (มี 5.4.0 แต่ยังอัปเดตไม่ได้เพราะ BLOCKED ข้างต้น)
