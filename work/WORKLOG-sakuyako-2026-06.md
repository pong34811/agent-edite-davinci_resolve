# WORKLOG — ตัดต่อทุก Timeline ของ `2026-06-Sakuyako`

แผน: [PLAN.md](PLAN.md) และ `.hermes/plans/2026-10-25_143444-sakuyako-2026-06-cut-all-timelines.md`
เริ่ม: 25 ตุลาคม 2026

| วันที่ | Timeline | สิ่งที่แก้ + เวลา | อ้างอิงอนุมัติ | ผลเทียบ baseline | ภาพ/พรีวิว | สถานะ/งานค้าง |
|---|---|---|---|---|---|---|

## บันทึก 1 — เตรียมงานและ baseline สภาพแวดล้อม (25 ตุลาคม 2026)

### สิ่งที่ทำจริง

- ขั้น 0: `python scripts/check_mcp_update.py` → `BLOCKED: configured MCP install is missing D:\davinci-resolve-mcp\src\server.py (check .mcp.json)` (exit 1) ตามคาด; `tasklist` พบ `Resolve.exe` ทำงานอยู่; `git status` สะอาด
- baseline การทดสอบ **ก่อนแตะอะไร**: `"C:/Users/pc-server/tools/thumb-venv/Scripts/python.exe" -m pytest -q` → **4 failed, 225 passed, 22 skipped, 8 subtests** (4 ข้อที่ fail คือ `test_skill_bundle.py` 18 ลิงก์ HyperFrames + `test_validation_regressions.py` 3 ข้อ) — มีอยู่ก่อนเริ่ม ไม่ใช่ regression ของงานนี้
- เขียน `scripts/scratch/sakuyako2026_06_baseline.py` (read-only, `preserved_state`, activate ก่อนอ่าน track state) และรัน
- เขียน `scripts/scratch/sakuyako2026_06_backup.py` และ `scripts/scratch/sakuyako2026_06_cutscan.py` (ยังไม่รัน)
- เขียน `scripts/scratch/sakuyako2026_06_plan.py` (ยังไม่รัน)

### ผลที่ได้

- รอบแรกรัน baselineแบบ foreground: ผ่าน `BASE 1/85` … `BASE 30/85` ภายใน 300 วินาที (activation ทุกตัวใช้เวลาประมาณ 10 วินาที) แล้ว command timeout — **ยังไม่ได้ไฟล์ baseline.json**
- รอบสองรันแบบ background (session `proc_17b1d6b69ed5`, PID 15404): รัน 1,233 วินาที ไม่มี output ให้เห็น แล้ว **Resolve scripting API ตอบไม่แล้ว** — probe read-only งานอื่น (`probe16.py`) ค้างจน `timeout 60` ตัด (exit 124) ทั้งที่ก่อนหน้านี้ตอบปกติ
- ฆ่า background session แล้ว (process_manage kill) แต่ probe ยังค้าง → สรุปว่า **Resolve เป็นคนหยุดตอบ scripting** ไม่ใช่แค่สคริปต์ที่ถือ bridge
- เหลือ python.exe 2 ตัวขนาดใหญ่ (PID 21932 = 416 MB, PID 14140 = 231 MB) ที่น่าจะเป็น baseline/probe ที่ค้าง คำสั่ง `taskkill` ถูกบล็อกเพราะไม่ได้รับอนุญาต → **หยุด workflow รอผู้ใช้**

### ข้อควรระวังที่ยืนยันเพิ่ม

- ตาม `OPERATING-NOTES` บรรทัด "Preset apply: Resolve will not close" และ "Resolve launched by the agent": Resolve ที่หยุดตอบ scripting ต้องให้ผู้ใช้ **quit แล้วเปิดใหม่** ไม่ใช่ให้ agent ฆ่า Resolve
- ตาม `resolve-recon-readback`: recon ที่สร้าง `DuplicateTimeline` หรือสลับ track enable ถือเป็นการแตะ session ต้องเปิดเผย — รอบ recon ก่อนหน้านี้แตะ 2 ครั้ง (สร้าง/ลบ `ZZ_probe_dup`, สลับ track enable บน TL1) แล้วคืนสถานะ

### สิ่งที่ยังไม่ได้ทำ

- ไม่มี baseline.json, ไม่มี `.drp` สำรอง, ไม่มีการแก้ timeline ใด ๆ
- ไม่มีการแตะ source media, ไม่มีการเขียน Project.db, ไม่มี render

### สถานะ Resolve ณ หยุดงาน

- `Resolve.exe` PID 12944 ยังรัน (4.4 GB), โปรเจกต์ `2026-06-Sakuyako` ยัง 85 timeline (ตรวจครั้งสุดท้ายก่อนหลุด), หน้า `edit`, Media Pool folder `Master`

## บันทึก 2 — pilot, sidecar subtitles และ batch preflight (26–27 ตุลาคม 2026)

### สิ่งที่ผ่านการอนุมัติและตรวจแล้ว

- ผู้ใช้อนุมัติ cut list ครบ 85 รายการ, pilot และให้ทำต่อทั้งชุดตามขอบเขตในแผน: เก็บไฮไลต์เดิม ตัดเฉพาะช่วงรอ/dead air ที่ชัดเจน, ทำ 16:9 และ `_9x16`, ซับไทยเสียง Sakuyako, ส่งออก H.264 Master แยก `16x9`/`9x16`; ไม่อัปโหลด/เผยแพร่
- Baseline ของโปรเจกต์: ต้นฉบับ 85 timelines, 30 source MP4s; project/timeline format ที่อ่านได้คือ 1920×1080 และ 30 fps. สร้างสำเนาแนวตั้งให้ pilot #84 แล้ว จึงเห็น 86 timelines
- Pilot #84: ตัด source frames `[101323, 101492]`, ระยะหลังตัด 1,649 frames / 54.976 วินาที; มี native subtitle 39 cues และแนวตั้งวางเกมเหนืออวาตาร์จากการวัดสื่อ Sakuyako จริง
- MP4 pilot ที่ส่งไปยังโฟลเดอร์งานและตรวจด้วย ffprobe: 16:9 1920×1080 H.264/AAC 30 fps, 54.976 วินาที, 95,333,157 bytes, SHA-256 `776D2A841BCE34CE81DE7567176706313E255A58AD9520A8547FEC32891EB1AC`; 9:16 1080×1920 H.264/AAC 30 fps, 54.976 วินาที, 91,244,205 bytes, SHA-256 `36F43E10D77724A063FA0997CFD02BCACBEAA9F9EC2632E16870549A6D8878FA`
- ASR แบบ offline เตรียมครบอีก 84 timelines ด้วย `large-v3`/CUDA `int8_float16`; pilot SRT คัดจาก cue ที่อนุมัติแล้ว. มี SRT 85 ไฟล์ในแต่ละโฟลเดอร์ (`G:\My Drive\Projects\Sakuyako-Cheris\2026-06\vdo\16x9` และ `...\9x16`), รวม 1,711 cues; หลังตัด suffix `_9x16` ชื่อคู่ตรงกัน, bytes ตรงกัน และ caption lint ผ่านทุกไฟล์
- 15 timeline ไม่มี cue ที่เชื่อถือได้จาก pass นี้; คิวตรวจอยู่ที่ `.hermes/projects/sakuyako-2026-06/asr/caption-review-queue.tsv` (ordinals 7, 9, 13, 23, 32, 33, 36, 46, 48, 49, 56, 60, 63, 76, 77). นี่เป็นคิวทบทวน ไม่ใช่การยืนยันว่าไม่มีเสียงพูด; ต้องฟัง/ตรวจแยกก่อนสรุป

### ด่านสำรองที่ยังไม่ผ่าน — ห้ามเริ่ม batch ที่เหลือ

- Studio MCP 21.1.1 read-only เห็น project ID `13468e42-44cb-4a8d-9730-85a64df1f425`, 86 timelines, active timeline ID `2b6edc05-cef1-4649-90e2-3f616adb88b7` (pilot `_9x16`) และ Media Pool folder `Master`; หลังการลองสำรอง readback ยังเป็น ID/folder เดิม
- community MCP ยังคง `BLOCKED`: `.mcp.json` ชี้ `D:\davinci-resolve-mcp\src\server.py` ซึ่งไม่มีอยู่; ห้าม force update/ติดตั้ง path ใหม่
- ปรับ one-off `scripts/scratch/sakuyako2026_06_backup.py` ให้ไม่บังคับสลับไป pilot master เพราะ `Project.SetCurrentTimeline()` ไม่ทำงาน; เรียก `SaveProject()` และ `ExportProject()` แล้วยังได้ `None` ทั้งคู่ และไม่มีไฟล์ `2026-10-27-sakuyako-2026-06-post-pilot-pre-batch.drp`; `verify_drp` จึงหยุดด้วย “Backup missing or empty”. `preserved_state` เตือนเรื่อง timeline/folder setter แต่ readback หลังรันยืนยันว่ายังอยู่ pilot `_9x16` และ `Master`
- `.drp` ที่ตรวจแล้วเพียงไฟล์เดียวคือ `backups/2026-10-26-sakuyako-2026-06-pre-pilot.drp` (1,757,886 bytes); เก่ากว่า pilot จึงไม่ผ่าน rollback gate สำหรับ batch
- ไม่มีการแก้ 84 timelines ที่เหลือ; ใน output folders มี MP4 เพียงไฟล์ pilot อย่างละหนึ่งไฟล์. SRT 85 คู่ยังเป็น sidecar ไม่ได้ import เป็น native tracks สำหรับ 84 รายการที่เหลือ
- ต้องให้ผู้ใช้ปิด/เปิด Resolve ใหม่และเปิด `2026-06-Sakuyako`; จากนั้นตรวจ read-only และสร้าง `.drp` ใหม่ที่ผ่าน CRC ก่อนทำงานต่อ

### ผลตรวจ repo รอบนี้

- ก่อน rebase `python -m pytest -q`: **4 failed, 225 passed, 22 skipped, 8 subtests passed** ใน 179.68 วินาที; fail คือ `test_skill_bundle` และ 3 subfailures ใน `test_validation_regressions` จาก 18 references เดิม
- หลัง rebase `scripts/refresh_skill_manifest.py` exit 0, ตรวจ 1,045 ไฟล์ และอัปเดต checksums ที่ไม่ตรงหลังรวม remote; verifier ยังรายงาน `ok: false` จาก local HyperFrames references ที่หาย 18 จุดเดิม และ `live_resolve_tested: false`
- หลัง rebase `python -m pytest -q`: **4 failed, 225 passed, 23 skipped, 12 errors, 8 subtests passed** ใน 181.03 วินาที; 4 failures ยังมาจาก references 18 จุดเดิม ส่วน 12 setup errors มาจาก QC tests ใหม่ที่ต้องใช้ไฟล์ `.agents/teamwork/audio_qc_worker/audio_qc_results.json` และ `.agents/teamwork/subtitle_qc_worker/audit_results.json` ซึ่งไม่มีอยู่ใน checkout
