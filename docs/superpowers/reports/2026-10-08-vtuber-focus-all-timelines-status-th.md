# รายงานตรวจ Zoom Focus ทุก Timeline — 2026-10-08

## สถานะ

ตรวจโครงสร้างสดครบ 49 canonical timelines ในโปรเจกต์หลัก aomimama-2026-09-p1 รวม 963 subtitle cues แยก temporary _MOVE_ERROR_ และ archived timelines ออกจากรายการ แล้วจัดลำดับผลใหม่ตาม live inventory จาก Resolve

ตรวจภาพ representative source/composite และ candidate stills ครบทุก timeline; จากนั้น render ตัวอย่าง 1 วินาทีที่ cue/จุดตัวแทนของแต่ละ timeline รวม 49 ไฟล์พร้อม subtitle burn-in. Resolve รายงานทุกงาน Complete และ MCP verify_output ผ่าน; ffprobe ยืนยันไฟล์ไม่ว่าง, H.264/AAC, ระยะ 1.002667 วินาทีครบ 49/49. ตรวจ contact sheet 49 ภาพ: เห็น VTuber/overlay และ subtitle ในตัวอย่างครบ โดยยังคง no-op เพิ่มเติม 48 Timeline เพราะ avatar เด่นอยู่แล้วหรือการครอปจะตัดเกม/UI/บริบทของมุก. นี่เป็น QC ภาพ ณ ตัวอย่างเดียวต่อ Timeline ไม่ใช่การตรวจ motion ตลอด cue หรือ subtitle ทั้ง 963 รายการ และไม่ได้ฟังเสียง.

### ผลตรวจเพิ่มเติม T44 หลังเริ่ม apply (11:08)

ทดลองวาง Adjustment Clip บน V2 เฉพาะ cue 4105–4163 (“ตายแล้ว”) ตามตัวอย่างภาพ representative แต่ render cue จริง 58 เฟรมที่ 1920×1080 แสดงเฉพาะเกม/HUD และ subtitle โดยไม่มี VTuber ในเฟรม จึงไม่ผ่านเงื่อนไข Zoom Focus และลบ Adjustment Clip ทดลองนั้นออกแล้ว (เก็บ V2 ว่างชื่อ `VTUBER_FOCUS_T44` และคง GIF เดิมบน V3 ที่ 3384–3504). อ่านกลับแล้ว V1/audio/subtitle เดิมยังอยู่; บันทึกโปรเจกต์เรียบร้อย. Render QC Complete, 2,619,792 bytes, H.264/AAC, 0.981333 s; เฟรม start/mid/end ตรวจพบว่าไม่มี VTuber ให้โฟกัส. ไฟล์หลักฐานอยู่ใน `.hermes/artifacts/vtuber-focus-review-2026-10-07/T44-QC-after-apply/`. สาเหตุคือภาพ representative เดิมมาจากคนละเวลาใน Timeline จึงใช้ยืนยันความเหมาะสมของ cue นี้ไม่ได้.

MCP timeline_frame.capture ล้มเหลวด้วย RENDER_FORMAT_REFUSED และ Gallery export ใช้ไม่ได้ขณะ Gallery panel ปิด จึงใช้ MCP render jobs พร้อม subtitle burn-in เป็น preview. รายงาน QC เพิ่มเติมอยู่ใน all-timeline-previews (manifest MCP, ffprobe-manifest และ contact sheets).

### บันทึกการลองแทรก T06 และการกู้คืน (2026-10-08)

ตรวจ source render cue 4452–4590 (“ฮ่าๆๆ”) แล้วพบ VTuber อยู่ด้านซ้ายล่าง จึงทดลองผ่าน Resolve Python API ตาม MCP-GAP ที่บันทึกไว้ แต่ `InsertGeneratorIntoTimeline("Adjustment Clip")` ทำ ripple แทนการวางเฉพาะ V2: V1, audio และ subtitle หลังจุดแทรกเลื่อน/แบ่ง 138 เฟรม และรายการ Adjustment Clip ไม่ปรากฏบน V2. หยุดการแก้ทันทีและกู้จาก archived v01 ที่อ่านกลับยืนยันเนื้อหาเดิมครบ; เก็บ Timeline ที่เกิด ripple ไว้ในชื่อ `T06_FAILED_RIPPLE_RETAINED_20261008` เพื่อไม่ทิ้งหลักฐาน. Timeline ชื่อหลักปัจจุบันกู้กลับเป็น 5497 เฟรม, V1 เต็มช่วงเดิม, subtitle transcript 8 cues และ GIF เดิมอยู่ V3 หลังเพิ่ม V2 ว่าง. บันทึกโปรเจกต์แล้ว; ยังไม่มี Focus Clip ใหม่บน T06. API นี้ไม่รองรับการแทรก generator ลง track/record frame เป้าหมายโดยไม่ ripple จึงไม่ทำซ้ำกับ Timeline อื่น.

## สิ่งที่ยืนยันได้

- Resolve Studio 21.1.0.17; MCP 4.9.0; โปรเจกต์หลัก ID 64b5d527-99d4-4a20-850d-7e127a226256; 1920×1080, 16:9, 60 fps.
- Adjustment Clip ที่ยืนยันมีเฉพาะ T07: frames 2880–3000, Size 1.75, Center X=0.85, Y=0.82, Edges=0. Preview เดิม Complete, 120 frames/2.005333s, H.264/AAC; sampled head/face, border และ subtitle clearance ผ่านตามหลักฐานเดิม.
- T06 reviewer แนะนำ No-op เพราะ crop ตัดตัวละครเกม/เมนูและส่วนล่างอวตาร. T46 reviewer แนะนำ No-op เพราะ crop ซ่อน LoL fight/HUD/UI (ตรวจได้เพียงภาพกลาง).
- การลอง T06 เพิ่มและกู้คืน track ตามบันทึกท้ายรายงาน; ไม่มี Adjustment Clip ใหม่ที่ผ่าน QC ในรอบนี้.
- Backup ก่อนแก้ไขที่ตรวจ zip/project.xml แล้ว: backups/aomimama-2026-09-p1-before-vtuber-focus-batch2-20261008.drp.
- UI ต้นทางรอบตรวจนี้: page Color, timeline เริ่มเกมแล้วเจอไฟต์-League of Legends-vdo, playhead 00:00:58:24, folder Archive; token c557858ca073. ระหว่าง render มีการเปลี่ยน active timeline/page ชั่วคราว และคืน state token นี้หลังตรวจเสร็จ.
- ใช้ MCP สำหรับ live inventory, track, render jobs และตรวจ output; ใช้ Python/ffmpeg สำหรับการเชื่อม Resolve, สกัดภาพ และ ffprobe. การแทรก Adjustment Clip ใช้ Resolve Python API หลังบันทึก MCP-GAP แต่การลอง T06 ไม่ผ่านเพราะเกิด ripple; ดูบันทึกท้ายรายงาน.

## บัญชี 49 Timeline

ตารางนี้แสดง live inventory, candidate cues และ visual disposition จาก stills; No-op คือเว้นภาพกว้างเมื่ออวตารเด่นอยู่แล้วหรือเกม/UI เป็นบริบทสำคัญ

| # | Timeline | Live ID | Subtitle cues | Adjustment Clip | Candidate subtitle cues (frame range) | Visual decision |
|---:|---|---|---:|---|---|---|
| 1 | เปิดสตรีมทักทายก่อนเริ่มเกม-alien shooter last hope-vdo | 772b4c2e-758d-4d1d-9899-1f894630f00d | 14 | 0; ต้องตรวจภาพเฟรมก่อนเลือกจังหวะ | 630–750: ฮัลโหล<br>780–930: ฮัลโหล | No-op; อวตารกินพื้นที่ด้านขวาเกือบครึ่งเฟรม; ซูมเพิ่มจะตัดฉากและแชต |
| 2 | ตามหาห้องที่หายไป-alien shooter last hope-vdo | 35228b83-310f-47e2-bccc-2fb8e8f66d46 | 16 | 0; ต้องตรวจภาพเฟรมก่อนเลือกจังหวะ | — | No-op; crop adds little or removes gameplay/UI context |
| 3 | ฝูงเอเลี่ยนบุกจนร้องลั่น-alien shooter last hope-vdo | ac6ef68b-8b3b-454e-bf04-59335d5e6ef3 | 15 | 0; ต้องตรวจภาพเฟรมก่อนเลือกจังหวะ | — | No-op; crop adds little or removes gameplay/UI context |
| 4 | คุยเรื่องอายุและเด็กรุ่นหลาน-alien shooter last hope-vdo | edd47d49-696d-46db-bbf3-f06cf293aadd | 18 | 0; ต้องตรวจภาพเฟรมก่อนเลือกจังหวะ | — | No-op; crop adds little or removes gameplay/UI context |
| 5 | ซื้อปืนไม่พอเงินขาดไปพันเดียว-alien shooter last hope-vdo | 631c31c1-592b-4190-89f1-f0ecb88d4961 | 17 | 0; ต้องตรวจภาพเฟรมก่อนเลือกจังหวะ | 1020–1197: โอ้โหงกจัดเลยอ่ะเงินขาดเท่าไหร่คะ | No-op; VTuber เด่นอยู่แล้ว; เมนูร้านอาวุธเป็นแกนของมุก |
| 6 | เตรียมป้อมสู้ศึกใหญ่-alien shooter last hope-vdo | c38ec787-755c-4179-93e2-f4ad51288746 | 8 | 0; ต้องตรวจภาพเฟรมก่อนเลือกจังหวะ | 4452–4590: ฮ่าๆๆ | No-op; Reviewer พบ crop ตัดตัวละครเกม/เมนูและส่วนล่างของอวตาร |
| 7 | ล่อบอสตัวเหนียวจนเหนื่อย-alien shooter last hope-vdo | a4d799e9-600b-46df-a812-e13cbe820285 | 11 | 1 Adjustment Clip (มีอยู่ก่อน; T07 QC ผ่าน) | 4620–4919: เพิ่งทำเองโหคลิปมันเยอะอ่ะไม่ถึงไม่ไหวอ่ะ | Existing Focus; คง Adjustment Clip เดิม 2880–3000; preview 120 frames ผ่าน QC |
| 8 | จบเกมในครั้งเดียว-alien shooter last hope-vdo | 17d7f65e-9d3a-49c5-bca4-2df5b31329c8 | 13 | 0; ต้องตรวจภาพเฟรมก่อนเลือกจังหวะ | 1552–1660: ฮะโหลเออฮัลโหลพี่ | No-op; crop adds little or removes gameplay/UI context |
| 9 | คุยกับแชทช่วงต้นไลฟ์ เล่าว่าเล่นเกมนี้มาหล-alien shooter-vdo | ffe3411b-d215-4b25-9f09-03a4fcd2856d | 19 | 0; ต้องตรวจภาพเฟรมก่อนเลือกจังหวะ | 180–300: ฮัลโหลเทส 1 2 3 4<br>1200–1500: โอ๊ยปวด... เมื่อยวันนี้วิ่งเยอะไปหน่อย | No-op; VTuber ครองพื้นที่ฝั่งขวาอยู่แล้ว; punch-in เพิ่มไม่ได้ประโยชน์ |
| 10 | ตั้งค่าหน้าจอไลฟ์ เจอวิธีใหม่-alien shooter-vdo | ccd044da-b172-4b63-8e1c-600481ce50ce | 21 | 0; ต้องตรวจภาพเฟรมก่อนเลือกจังหวะ | — | No-op; crop adds little or removes gameplay/UI context |
| 11 | กวาดห้องจนจบภารกิจ-alien shooter-vdo | d4791fb3-26e3-4594-bd07-2b8b3637b809 | 1 | 0; ต้องตรวจภาพเฟรมก่อนเลือกจังหวะ | — | No-op; crop adds little or removes gameplay/UI context |
| 12 | ตอบแชทว่าเกมยากไหมระหว่างเล่น-alien shooter-vdo | b8418b0b-0db3-4396-b51a-43853bfcfc92 | 9 | 0; ต้องตรวจภาพเฟรมก่อนเลือกจังหวะ | 2880–3130: อืมอันนี้เล่นโหมดฮาร์ดนะแต่ว่าด้วยความที่เคย | No-op; crop adds little or removes gameplay/UI context |
| 13 | ด่านเขียวสุดท้ายก่อนจอดับ-alien shooter-vdo | 1ed937ce-eda6-4c6b-a04f-b89250222102 | 8 | 0; ต้องตรวจภาพเฟรมก่อนเลือกจังหวะ | — | No-op; crop adds little or removes gameplay/UI context |
| 14 | คุยสรุปเกมหลังเล่นจบ ก่อนปิดไลฟ์-alien shooter-vdo | c6b55364-8cd2-4302-ac4c-0aa0cba0d902 | 37 | 0; ต้องตรวจภาพเฟรมก่อนเลือกจังหวะ | 660–1017: ฮ่าๆๆๆๆๆ<br>4200–4437: ฮ่าๆๆๆๆๆ | No-op; ช่วงหัวเราะมี VTuber ขนาดใหญ่และเห็นสีหน้าชัดอยู่แล้ว |
| 15 | ลืมแชร์จอ จบของวีทูปเบอร์ที่ไม่เตรียมตัว-Minecraft-vdo | 173308df-3d72-4e6b-87b8-934c3f1636b1 | 24 | 0; ต้องตรวจภาพเฟรมก่อนเลือกจังหวะ | — | No-op; crop adds little or removes gameplay/UI context |
| 16 | หนาวติดลบ 16 ต้องถือลาวา-Minecraft-vdo | 6a763b2d-6b4c-425e-9e58-e056164acb07 | 48 | 0; ต้องตรวจภาพเฟรมก่อนเลือกจังหวะ | 30–54: โห<br>594–751: แม่งจะหนาวตายของแท้เลยติดลบ 12<br>810–960: โอ้โหเหี้ยบ้านพี่นี่แม่งจนสมชื่อจริงๆ | No-op; inventory/lava และตัวบอกอุณหภูมิเล่าเหตุการณ์; avatar มีขนาดเด่น |
| 17 | ถือถังลาวาไว้กันหนาว-Minecraft-vdo | 9f5efe15-abf1-429f-a21f-d44f943ce72f | 33 | 0; ต้องตรวจภาพเฟรมก่อนเลือกจังหวะ | — | No-op; reaction GIF ขนาดใหญ่ทับภาพ; crop จะชิงจุดสนใจ |
| 18 | พี่น้องไม่เคยช่วยอะไรเลย-Minecraft-vdo | c7d46560-0c62-4d3b-b944-e2514c205c05 | 26 | 0; ต้องตรวจภาพเฟรมก่อนเลือกจังหวะ | 383–511: ซอมบี้เสร็จแล้วโอ้โหรักฉิบหายเลย<br>954–1088: ไม่เอาไม่เอาดาบมาไอ้เหี้ยลืมคราฟต์ดาบมา<br>1398–1543: แม่งก็ต้องมีอะโอ้โหไม่งั้นไม่มานั่งร้องหาพี่ | No-op; ซอมบี้/การลืมดาบและ HUD เป็นแกนของมุก; avatar ชัดล่างซ้าย |
| 19 | อย่าใส่ร้ายผม เกือบจมลาวา-Minecraft-vdo | 2916d238-8951-4b71-8b22-0289e314e79f | 47 | 0; ต้องตรวจภาพเฟรมก่อนเลือกจังหวะ | 847–885: ชนะทั้งหมด<br>2118–2238: อุ้ยใช้ได้แล้วเนี่ยตรงนี้เต็มเลยพี่<br>2394–2542: เฮ้ยอย่าใส่ร้ายผมนะโอ้โหผมผมผม | No-op; ฉากลาวาและเพื่อนร่วมฉากเป็นบริบท; avatar ชัดพอแล้ว |
| 20 | เจอเพชรแล้ว! ยิส!-Minecraft-vdo | cfceaef3-9594-4243-8a11-67fd3b0f7f54 | 36 | 0; ต้องตรวจภาพเฟรมก่อนเลือกจังหวะ | 1158–1259: โหพี่จ๋าสุดยอดมากเลยแม่งอยู่ขุด<br>2250–2343: ไม่งั้นเพื่อชีวิตอันโหดร้ายในการมา<br>4632–4733: ถ้าผมตายแล้วผมจะเอาพี่ไปลงนรก | No-op; ผู้เล่นอื่น/การขุดและ debug text สำคัญ; avatar เด่นอยู่แล้ว |
| 21 | เจอทางกลับบ้านแต่เพื่อนไปห้องน้ำ-Minecraft-vdo | d863d8e5-f21e-4ff3-9224-5a54f8de6edb | 39 | 0; ต้องตรวจภาพเฟรมก่อนเลือกจังหวะ | 90–132: โอ้โหน่าจะ<br>1208–1325: นะโอ้โหร้อยวันพันปีไอ้เหี้ยไม่คิดจะ | No-op; crop adds little or removes gameplay/UI context |
| 22 | ลุยฐานใต้ดิน เข้าได้สองทาง-alien shooter 2-vdo | 11d79353-7379-4799-bc59-8427f6991b37 | 20 | 0; ต้องตรวจภาพเฟรมก่อนเลือกจังหวะ | — | No-op; crop adds little or removes gameplay/UI context |
| 23 | กวาดศัตรูในฐานมืด-alien shooter 2-vdo | 280dfcd8-933a-4188-b2f5-7bff7591f706 | 3 | 0; ต้องตรวจภาพเฟรมก่อนเลือกจังหวะ | — | No-op; crop adds little or removes gameplay/UI context |
| 24 | เช็กของ เซฟยัง แล้วลุยต่อ-alien shooter 2-vdo | cae89ca0-3c45-4186-b876-91ff8b44ee3b | 10 | 0; ต้องตรวจภาพเฟรมก่อนเลือกจังหวะ | — | No-op; crop adds little or removes gameplay/UI context |
| 25 | Windows XP  Vista  8  ลองหมด-alien shooter 2-vdo | ff8546d6-362e-41a5-a433-7b2b4fc3755d | 31 | 0; ต้องตรวจภาพเฟรมก่อนเลือกจังหวะ | 69–112: ไม่ได้ใช้ไม่ได้ใช้ไม่ได้ใช้ DG กูดูการนะเนี่ยเฮ้ย Windows 8 ยังไม่ลองเลยนะพี่ไล่ไปเหี้ยอันกด Play เลยพี่กด Play เลยนี่น่าจะเกมเด้งเป็นไงผมรู้ผมผมนี่โคตรเก่งเลยไอ้เหี้ยคลิกขวา Windows 8 พี่ Windows 8 รอบนี้ Windows 8 อือจิ้มไปไอ้เหี้ยนําไปใช้ตกลงปื๊ดไม่ได้ไอ้เหี้ยไอ้นี่เด้ง [หัวเราะ] การแสดงผลเกมนั่งคําคุณสมบัติ<br>3125–3264: Windows โหมดเปิดเกมได้โคตรเหี้ยเลย | No-op; properties dialog คือมุก; VTuber ชัดที่มุมล่างขวา |
| 26 | ในที่สุดแชร์จอเหมือนคนปกติได้แล้ว-alien shooter 2-vdo | 5f7ae05a-b35d-4c0f-bf9f-570f9f73b862 | 24 | 0; ต้องตรวจภาพเฟรมก่อนเลือกจังหวะ | 780–870: โหเราน่าจะใช้วิธีนี้แต่แรก<br>1650–1800: เอาไว้ตรงโห | No-op; ภาพ desktop/หน้าจอเปิดเกมคือบริบทของมุก |
| 27 | ปรับความละเอียด 1024x768 ไอ้เฮีย-alien shooter 2-vdo | 182c76c6-10fd-4d13-bf3c-928845f1fe2d | 37 | 0; ต้องตรวจภาพเฟรมก่อนเลือกจังหวะ | 720–1077: เฮ้ยเฮ้ยเฮ้ยโอ๊ยไม่รอดอ่ะพี่<br>2880–3135: โหพี่นี่ไม่ผ่านเลยแม่งต้องคุยต้องบอกเลขทีละ<br>4440–4617: อุ๊ยผมไม่โกหกพี่หรอกโหรู้จักกันมาตั้งนาน | No-op; เมนู resolution เป็นใจความ; crop จะซ่อนตัวเลือก |
| 28 | ไฟต์ใหญ่ในอารีนา-League of Legends-vdo | 1fd9051c-555d-405a-8764-11335d900aa2 | 2 | 0; ต้องตรวจภาพเฟรมก่อนเลือกจังหวะ | — | No-op; crop adds little or removes gameplay/UI context |
| 29 | เสียงร้องโอ๊ยๆ-League of Legends-vdo | d782d9e5-becf-4d19-85ac-393722b5d8d2 | 15 | 0; ต้องตรวจภาพเฟรมก่อนเลือกจังหวะ | — | No-op; ภาพต้นทางช่วง cue ไม่มี VTuber; GIF อยู่คนละช่วง |
| 30 | ดับเบิลคิลแล้วโดนฝัง-League of Legends-vdo | 741c0758-51c3-4cc7-993e-fd8e55bf95e4 | 7 | 0; ต้องตรวจภาพเฟรมก่อนเลือกจังหวะ | 1140–1377: มึงน่าจะรู้ว่าหนูแพ้วันมีโครอยู่ตลอดเวลา | No-op; การต่อสู้และ death feed เป็นแกนของช็อต |
| 31 | ไฟต์หน้าป้อม-League of Legends-vdo | 706d3f08-13b3-4e44-9275-13aa4887aed8 | 21 | 0; ต้องตรวจภาพเฟรมก่อนเลือกจังหวะ | 1020–1183: โอ๊ยเหี้ยเหี้ยอะไรวะเนี่ยไอ้เหี้ยเหี้ยอะไร | No-op; fight และ health/HUD ต้องเห็นครบ |
| 32 | เมาท์เรื่องสายเล่นเกม-League of Legends-vdo | 1da6d7df-f272-4c21-a8d6-f76a6b546712 | 2 | 0; ต้องตรวจภาพเฟรมก่อนเลือกจังหวะ | 4680–5040: โอ้โหนะนะคะช่วยเยอะสุดบอกเลยนะฮะ | No-op; scoreboard/tooltip เป็นข้อมูลที่กำลังพูดถึง |
| 33 | เพนตาคิลแล้วพ่ายแพ้-League of Legends-vdo | 8771077c-cb83-4ae2-a63e-f51f31a2ae6c | 2 | 0; ต้องตรวจภาพเฟรมก่อนเลือกจังหวะ | — | No-op; scoreboard แสดงผลแพ้ชนะและเป็นบริบทของเรื่อง |
| 34 | ไฟต์ท้ายเกมสุดมัน-League of Legends-vdo | 81aaa8d4-171a-44f3-a7eb-ae122252e9ed | 4 | 0; ต้องตรวจภาพเฟรมก่อนเลือกจังหวะ | 360–540: โอ๊ยเหี้ยไม่ได้ขยับเลย | No-op; ทีมไฟต์และ HUD เป็นจุดสนใจ; avatar ชัดล่างซ้าย |
| 35 | ลืมเปิดเสียงเพื่อน คุยกับผีมาตั้งนาน-Minecraft-vdo | 39fcd2b4-edcf-40f4-9d8a-a2b7d9fd2674 | 15 | 0; ต้องตรวจภาพเฟรมก่อนเลือกจังหวะ | 0–133: โอ้จบการไลฟ์โม้กับพี่จ๋าตั้งนานแม่งลืมเอา<br>600–777: โอ้โหเหมือนผีเลยดิอย่างงั้นน่ะ<br>2160–2337: โอ้พี่ก็เหมือนกันแหละโอ้โห | No-op; ภาพตัวอย่าง source ไม่มี VTuber ให้โฟกัส |
| 36 | ลืมเอาอาหาร ต้องกินเนื้อซอมบี้-Minecraft-vdo | d4183dd8-dc9a-4a9f-b572-28f5be9be9ff | 31 | 0; ต้องตรวจภาพเฟรมก่อนเลือกจังหวะ | 1818–1998: ชิบหายแม่งลืมเอาของกินมาอู๊หูย<br>2010–2172: อะไรก็ได้โอ้โหแม่งไม่มีของกิน | No-op; avatar เด่นแล้ว; การหาอาหาร/กินเป็น visual gag |
| 37 | ซอมบี้มาได้ไงวะ!-Minecraft-vdo | af798c11-61ea-4818-b2af-25e492ed52c7 | 20 | 0; ต้องตรวจภาพเฟรมก่อนเลือกจังหวะ | — | No-op; crop adds little or removes gameplay/UI context |
| 38 | อยากเปลี่ยนร่าง เอาคนไม่มีเสียงในหัวมาเล่นแทน-Minecraft-vdo | 3307a9de-30fb-4655-87be-265a79ebc98e | 10 | 0; ต้องตรวจภาพเฟรมก่อนเลือกจังหวะ | 1560–1737: กูไปเอากูไปเอากูไปเอาเซฟแป๊บนึงไม่ไหวละ | No-op; reaction GIF เป็นจุดสนใจ; crop จะชน overlay |
| 39 | พี่จ๋าช่วยด้วย เรือไปไหนวะ-Minecraft-vdo | 5ec86ac2-b9b7-4308-b00e-88e6eeb82248 | 22 | 0; ต้องตรวจภาพเฟรมก่อนเลือกจังหวะ | 705–750: ฮัลโหลยังไม่ได้ทำอะไรเลยเคมึงอ่ะมึงมึงทำตัวมึงเองอ่ะกด Shift ขวานั่งหน้าแล้วพายพายไอ้เหี้ยเอ๊ยเกือบละ<br>789–813: โอ้โหแม่งทางแม่งโคตรไม่สมประกอบอ่ะ<br>1740–1917: พี่ตาช่วยด้วย | No-op; Reviewer คงภาพกว้างเพื่อรักษาฉากหิมะและบริบทการหาเรือ |
| 40 | วิ่งหนีมอนตอนมืดจนเห็นบ้าน-Minecraft-vdo | 25c0438d-de3a-4ce6-a9e9-e828f2f2b783 | 40 | 0; ต้องตรวจภาพเฟรมก่อนเลือกจังหวะ | 5195–5335: แต่ว่าด้วยความที่ทางไม่ไหวอย่าง | No-op; เส้นทาง/หมู่บ้านเป็นบริบท; หน้า VTuber ไม่ได้แสดงปฏิกิริยาชัด |
| 41 | ออกไม่ได้เลยวะ ฮ่าๆๆ-Minecraft-vdo | 82a34a3d-835b-4ebd-9d05-af70c9f47635 | 23 | 0; ต้องตรวจภาพเฟรมก่อนเลือกจังหวะ | 2560–3004: ฮ่าๆๆพี่เนี่ยมันเอาไม่ได้เล่ห์ฮ่าๆๆ<br>3260–3390: เอ้อเหี้ยเหลือเหลือครับวกทำไมมัน | No-op; VTuber หัวเราะแต่ interaction Minecraft ยังสำคัญ |
| 42 | ไฟต์ในเลนกับเสียงร้องเฮ้ย-League of Legends-vdo | 7039875a-bdbf-446d-961e-46115836f1e9 | 13 | 0; ต้องตรวจภาพเฟรมก่อนเลือกจังหวะ | 780–955: ไอ้เหี้ยทำไมอารมณ์เปลี่ยนได้ไงวะป่าแม่มก็<br>1740–1964: ไอ้เหี้ยทำไมกูต้องมาซ่อมด้วยวะซ่อมเพื่อมาเนี่ย | No-op; ภาพต้นทางไม่เห็น VTuber และมี reaction GIF ตรง cue |
| 43 | ทีมไฟต์ถูกชัตดาวน์-League of Legends-vdo | aa07a8e3-36e2-422b-bb5b-79f679e6546c | 16 | 0; ต้องตรวจภาพเฟรมก่อนเลือกจังหวะ | 781–1050: โอ๊ยเหี้ยหมากvanguardเมื่อกี้นี้ถ้าหมาไม่โดน<br>1771–1953: สกิล 2 ทีไปกอดแล้วก็ตายกันไปแพ้เกม | No-op; LoL fight และ interface อธิบาย shutdown |
| 44 | เริ่มเกมแล้วเจอไฟต์-League of Legends-vdo | 59c29caf-6222-4c52-af3b-40cf74d61143 | 22 | 0 Adjustment Clip; V2 ว่าง `VTUBER_FOCUS_T44`, GIF เดิมบน V3 | 4105–4163: ตายแล้ว | No-op; render cue จริงไม่พบ VTuber ในภาพ จึงไม่มีตัวละครให้ Zoom Focus; คงเกม/HUD และ subtitle เดิม |
| 45 | หัวยังไม่ฟู ตายก่อนเลย-League of Legends-vdo | abbb0657-7187-4d31-b7e0-646512cc04d2 | 35 | 0; ต้องตรวจภาพเฟรมก่อนเลือกจังหวะ | 5940–6000: แวะไปโหลด<br>6060–6120: ดิลโหลดดิ<br>7560–7761: เข้าไปมันก็นะฮ่าๆๆอะไรอ่ะไม่น่า | No-op; Reviewer เห็น fight/HUD จะหายไปหาก crop |
| 46 | ออกเมื่อไหร่มีตายเมื่อนั้น-League of Legends-vdo | 827878be-8522-4164-9634-4aa9a68f7392 | 18 | 0; ต้องตรวจภาพเฟรมก่อนเลือกจังหวะ | — | No-op; death/scoreboard คือบริบทของมุก |
| 47 | ด่าทีมรัวๆ ไอ้เชี่ยทีมตาก-League of Legends-vdo | a7ef2e35-5d01-4cc2-8e2f-ec91f669f08f | 10 | 0; ต้องตรวจภาพเฟรมก่อนเลือกจังหวะ | — | No-op; gameplay ที่กำลังวิจารณ์เป็นบริบท; avatar ชัดแล้ว |
| 48 | ลาสตรีม ขอบคุณทุกคน-League of Legends-vdo | 11db333c-d4be-4a44-873d-bcc4f13836fe | 22 | 0; ต้องตรวจภาพเฟรมก่อนเลือกจังหวะ | — | No-op; ภาพปิดสตรีมมี VTuber ใหญ่ชัด |
| 49 | กดเล่นแล้วเกมเด้ง ลบโหลดใหม่เลย-alien shooter 2-vdo | 4a06230e-9c8b-48d5-842f-ec97aa31e7fd | 28 | 0; ต้องตรวจภาพเฟรมก่อนเลือกจังหวะ | 623–814: มาแล้วเป็นไงโหพี่อย่างหรูดูน้องดูน้องอ้าว<br>990–1170: ลบเกมลบเกมโหลดใหม่แม่งเลยพี่ | No-op; Steam/window และ reaction meme อธิบายมุก |
## ข้อสรุป

ผลตรวจ: 49/49 visual framing decisions; 49/49 preview renders Complete และผ่าน verify_output/ffprobe; contact sheet แสดงภาพ composite พร้อม subtitle burn-in ณ จุดตัวอย่างของทุก Timeline. T07 มี Adjustment Clip เดิมคงไว้และผ่าน preview QC แบบต้น/กลาง/ท้าย; อีก 48 Timeline ไม่มีการเพิ่ม Adjustment Clip เพราะภาพกว้างรักษาเกม/desktop/UI หรือ avatar เด่นอยู่แล้ว. No-op หมายถึงไม่เพิ่ม Adjustment Clip ไม่ได้หมายความว่าเคยสร้าง Zoom แล้ว.

ข้อจำกัด: preview ใหม่แต่ละไฟล์ครอบคลุมประมาณ 1 วินาทีที่จุดตัวอย่างเดียว ไม่ได้ตรวจ motion ต่อเนื่องของทั้ง cue หรือ overlay ของ subtitle ทั้ง 963 cues. ไม่ได้ฟังเสียงด้วย. ไม่มีการเปลี่ยนโครงสร้างโปรเจกต์ในรอบ render; คืน Resolve ไปยัง page/timeline/playhead/folder เดิมหลังตรวจ.
