# Hoshi_1489

## ตัวตนและคอนเทนต์
- สตรีมเมอร์เกม / VTuber เน้นการเล่นเกมร่วมกับกลุ่มเพื่อน (เช่น โนว่า, คุณอาม) บรรยากาศตลก โบ๊ะบ๊ะ และโวยวาย
- คอนเทนต์และเกมที่พบ:
  - 2026-09: Backrooms
  - 2026-10-1: Halloween, Backrooms, Examination, Peak, Don't Scream Together (แบ่งไฮไลต์เป็น 3 หมวด: ช่วงเล่นเกม, ช่วงสนุกสนาน, ช่วง meme)

## ที่เก็บไฟล์
- Google Drive: `G:/My Drive/Projects/Hoshi_1489/` (เช่น `2026-10-1/`)
- ฟุตเทจดิบ: 1080p60 (H.264 High หรือ AV1)
- ไฮไลต์ pipeline work folder: `work/highlight/hoshi_1489/`

## โปรเจคและ timeline ใน Resolve
- Project Library: `Google_drive`
- โฟลเดอร์ใน Project Manager: `hoshi_1489`
- โปรเจกต์ที่รู้จัก: `hoshi-2026-09`, `hoshi-2026-10-1`
- Timeline naming convention: `{ชื่อคลิป}-{ชื่อเกม}-vdo` (เช่น `โมเดลแม่งด้วนแล้วยังเล็กอีก-Halloween-vdo`)

## รูปแบบและ layout
- 16:9 แนวนอน (1920x1080, 60 fps)
- สเตจแรกเป็น Assembly เท่านั้น (ไม่มีการใส่ effect หรือ overlay)

## ซับ เสียง และ enrichment
- ใช้กฎกลางใน `AGENTS.md` และ `house-style` จนกว่าผู้ใช้จะบอกเป็นอย่างอื่น

## Script และ skill ที่เกี่ยวข้อง
- Skill: `highlight`, `long-video-highlight-clipping`, `new-channel-job-setup`, `timeline-naming-convention`
- Script: `scripts/resolve_common.py` สำหรับเชื่อมต่อ Resolve API

## กับดักและงานค้าง
- Google Drive I/O: การอ่านและดึงเสียงผ่าน Google Drive มี latency สูง ให้ใช้ `DEMUX_WORKERS: 2`
- Resolve 21.1 Sub-frame Rounding: การสร้าง timeline อาจมี source start เลื่อน 1 frame เล็กน้อยตาม Rule 55 ซึ่งเป็นพฤติกรรมปกติของ API ไม่ต้องสร้างใหม่

## ยังไม่ทราบ (ถามผู้ใช้ก่อนเดา)
- Preset ซับและสีที่ชอบ
- แผนการแปลงเป็นคลิปแนวตั้ง (Shorts/TikTok) ในอนาคต
