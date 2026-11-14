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

## ปกคลิป (2026-11-14, งาน 2026-09-01)
- รูปโมเดล: `Z:\CreamSoda\Hoshi_1489\png_live2d` (ผู้ใช้ระบุเอง; อ่านไฟล์อย่างเดียว ไม่เกี่ยวกับ Resolve library บน Drive Z) — VTube Studio PNG 1920x1009 RGBA 10 ท่า: มีหู+หาง (1,3,6,7,9) กว้าง ~1250 px ต้องครอปบัสต์ ±420 px รอบกึ่งกลาง; 8/9 ตาดำข้างเดียว, 0/1 มีเครื่องหมายโกรธ
- ไฟล์ใน `Final/`: `vdo-*` และ `shot-*` เป็น 1920x1080 30 fps ความยาวเท่ากัน (shot ยังไม่ใช่แนวตั้ง) จึงทำปกต่อชื่อคลิป: แนวนอน + แนวตั้ง อย่างละใบ ส่งที่ `<วัน>/Thumbnails/Horizontal_16x9` และ `Vertical_9x16`
- เฟรมมีซับฝังที่ y≥880 และโมเดลสตรีมมุมขวาล่าง: ครอปพื้นหลัง (0,0,1564,880); คลิปคุยที่โมเดลสตรีมเต็มจอใช้เบลอ 46 เพื่อไม่ให้มี Hoshi สองตัว; เลี่ยงเฟรมที่มีวงกลม/ลูกศรแดงที่ editor ใส่ไว้ เพราะไปอยู่หลังโมเดล
- สคริปต์ตัวอย่างอยู่ใน scratch (gitignored) โฟลเดอร์ hoshi_covers_20260901: sample.py, build_covers.py --copy
- ผู้ใช้ย้าย/ลบไฟล์ใน `Final/` ระหว่างทำงานได้ (คลิปมะพร้าวหายไประหว่างงาน): ผูกปกกับชื่อคลิป ไม่ใช่ลำดับไฟล์

## ยังไม่ทราบ (ถามผู้ใช้ก่อนเดา)
- Preset ซับและสีที่ชอบ
- แผนการแปลงเป็นคลิปแนวตั้ง (Shorts/TikTok) ในอนาคต
