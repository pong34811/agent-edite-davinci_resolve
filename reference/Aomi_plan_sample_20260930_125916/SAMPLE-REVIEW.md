# ตัวอย่าง Aomi-mama — รอปิดงานฟอนต์และอนุมัติ

**Timeline:** `ทำไมน้ำหน้กน่ายกจังครับ_9x16`  
**ID:** `f53c5134-d753-4f8b-b6f6-c91138f62c65`  
**สถานะ:** ปรับ GIF และตรวจพรีวิวแล้ว ไม่ใช่ verdict พร้อมเผยแพร่หรือทำครบทั้งชุด

## เปิดดู

- `after_9x16.mp4` — ตัวอย่างหลังแก้เต็ม 1080×1920, 60 fps, H.264/AAC พร้อม burn-in subtitles
- `sample-before-after.mp4` — ซ้ายก่อน / ขวาหลัง ใช้เสียงจากพรีวิวหลัง; 1080×960, 60 fps สำหรับเทียบ ไม่ใช่ export ส่งมอบ
- `sample-before-after.jpg` — เทียบ 0 / 3.8 / 7.8 / 12.2 วินาที
- `before_16x9.mp4`, `after_16x9.mp4` — ต้นฉบับแนวนอนที่ไม่ได้แก้ ภาพเหมือนกันทั้ง 976 decoded frames

## เปลี่ยนอะไร

แก้เฉพาะ V4 GIF หก items ในแนวตั้ง:

| GIF / ช่วงเฟรม [start,end) | ขนาดและตำแหน่งหลังแก้ | เหตุผล |
|---|---|---|
| 83WGh1ge.gif / [0,133) | Zoom 0.666667, Pan 0, Tilt 2178.300654 | เดิม Zoom 2 crop หนักและบังใบหน้า; คืนภาพครบ กึ่งกลางด้านบน |
| Cute - Happy Cat.gif / [205,248) | Zoom 0.284722, Pan 0, Tilt 779 | เดิม Zoom 2 ทำให้เห็นแต่จมูก/ลำตัว; รักษาสัดส่วนภาพสูงให้เห็นแมวครบ |
| Anime - Angry Chibi.gif / [443,459), [459,475), [475,491), [491,507) | Zoom 0.65 เดิม, Pan 0, Tilt 1214.310112 | เดิมขอบบนหลุดเฟรม; เลื่อนลงให้เห็นขอบครบ ไม่เปลี่ยนความยาวหรือ loop |

ค่าขนาดคำนวณจาก source raster ของแต่ละรายการ ไม่ใช้ Zoom/Tilt เดียวกันทั้งชุด ภาพทั้งหมดวางให้ขอบบนอยู่ประมาณ y=36 ใน canvas ตา/ใบหน้าเห็นชัดในเฟรมที่ตรวจ แต่บางภาพยังทับหู/ผม หากต้องการสงวนศีรษะทั้งหมด ต้องตกลงเลย์เอาต์/พื้นที่ด้านบนเพิ่มก่อน ไม่ปรับภาพหลักเอง

ไม่แก้ V1/V2, ต้นฉบับแนวนอน, cuts, retime, caption text/time/style, audio mix, source files หรืออีก 7 คู่; ไม่สร้าง/ลบ Timeline และไม่ patch Project.db

## ผลตรวจจริง

- ก่อน/หลัง native previews สองสัดส่วน: Render Complete, H.264/AAC, 60/1 fps, **976 video frames**, video duration **16.266667 s**, audio sample rate 48000; decode ทั้งไฟล์ผ่าน
- ภาพ contact ก่อน 125 และหลัง 125 ภาพรวมทั้งสองสัดส่วน: cut boundaries, caption midpoint ทุก cue, GIF first/middle/last ทุก item, จุด 7.8/12.2 s และท้ายคลิป ไม่ใช่การดูทุกเฟรม
- Live readback ทั้ง **17 Timeline** เทียบ baseline: ไม่เปลี่ยน properties/เวลา/media/text/audio/track/settings นอก whitelist transforms ของ GIF หก items
- Exported subtitle blocks ทุก sequence เหมือน backup ก่อนแก้; **593 serialized subtitle items** และ **2206 nonapproved effect blobs** ไม่เปลี่ยน (เป็นจำนวนทั้งโปรเจกต์รวม archive ไม่ใช่จำนวน sample cues)
- ภาพแนวนอน decoded ทั้ง 976 frames เหมือนก่อน; decoded PCM ก่อน/หลัง SHA-256 เหมือนกันทั้งแนวนอนและแนวตั้ง **การเทียบ hash ไม่เท่ากับการฟังครบจริง**
- SaveProject และคืน active Timeline / timecode / page / Media Pool folder สำเร็จ; queue ของผู้ใช้เหมือน baseline ลบเฉพาะงาน render ที่สร้างเอง

## งานค้าง / รอผู้ใช้

1. **ฟอนต์:** Track descriptor เป็น Mitr Bold แต่พบ UTF-16 Open Sans metadata ใน 6 cues ต่อ Timeline: น่ายกอ่อ, ตัวเบาแล้วก็ตัวเล็ก, มันทำให้, รอดชีวิตได้, แล้วก็มันจวงแทง และ 555+ ยังไม่พิสูจน์ว่าเป็น font ที่แสดงจริงหรือข้อมูลค้าง หน้าต่างหลัก Resolve ซ่อนอยู่ (Win32 visible=false และ CUA ไม่พบหน้าต่าง) ต้องเปิดหน้าต่างให้ตรวจ Inspector/UI ได้ ไม่เดาหรือเปลี่ยน binary
2. **ตัวอย่าง:** ให้ผู้ใช้ดูตำแหน่ง/ขนาด GIF และฟังพรีวิวก่อนอนุมัติอีก 7 คู่ รอบนี้ยังไม่เริ่มส่วนที่เหลือ
3. **แนวนอน:** GIF บังหน้าตาม baseline เดิม ไม่แก้เพราะคำอนุญาตครอบคลุมแนวนอนเฉพาะ font
4. **สไตล์ซับ:** ไม่พบล้นเฟรม sample ที่ตรวจ แต่บาง cue ยาวตามต้นฉบับ ไม่มีคำอนุญาตเปลี่ยนข้อความ เวลา ขนาด สี ขอบ ตำแหน่ง หรือ line break
5. **Backup:** ตรวจไฟล์ ZIP/hash แล้ว ยังไม่ทดสอบ import/restore จึงไม่อ้างว่าเปิดกลับทดสอบแล้ว

## สถานะต่างจากเอกสารส่งต่อ

16 target Timeline ยังตรง manifest แต่ live มี archive เดิมเพิ่ม `ทำไมน้ำหน้กน่ายกจังครับ_9x16_archived_v02` อีกหนึ่งรายการ เก็บไว้ ไม่ลบเอง Source A/V ที่มี path ไม่พบไฟล์ขาด; original SRT import เก่าใน Media Pool หาย 11 รายการ แต่ captions ของ sample burn-in ได้ ไม่มี reimport/relink/cleanup

## หลักฐาน

- `baseline.json`, `preflight-summary.json`
- `backup-verification.json` → `Aomi-mama_pre_sample_20260930_130245.drp`
- `sample-transform-changelog.json`, `after-baseline-readback.json`
- `sample-font-audit-v02.json` — ฉบับ UTF-16-aware ใช้แทน `sample-font-audit.json` ซึ่งตรวจ ASCII-only ไม่ครบ
- `before-render-report-20260930_131906.json`, `after-render-report-20260930_133302.json`
- `before-qc_20260930_132131/qc-report.json`, `after-qc_20260930_133350/qc-report.json`
- `comparison-verification.json`
- `final-verification.json` → `Aomi-mama_post_sample_20260930_134413.drp`
