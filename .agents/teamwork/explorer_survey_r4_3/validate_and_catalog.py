import sys
import re
import json

sys.stdout.reconfigure(encoding='utf-8')

# 1. 32-File Mapping Table
FILE_MAPPING = [
    {
        "index": 1,
        "filename": "After DnD EP.4 ตอน เมื่อไทกะนอนไม่หลับเพราะความรัก.mp4",
        "mediapool_id": "33bd05cc-6238-469a-acf1-74e6bac5270e",
        "game_tag": "DnD",
        "category": "Talk / D&D After",
        "status": "UNTOUCHED",
        "duration_sec": 5012.15,
        "frames_60fps": 300729,
        "resolution": "1280x720"
    },
    {
        "index": 2,
        "filename": "After DnD ： หลอนครั้งแรกแต่จบดาร์กขั้นสุด.mp4",
        "mediapool_id": "4d96b4b6-8a58-4182-bb68-308f7a2dae3d",
        "game_tag": "DnD",
        "category": "Talk / D&D After",
        "status": "UNTOUCHED",
        "duration_sec": 8630.29,
        "frames_60fps": 517818,
        "resolution": "1280x720"
    },
    {
        "index": 3,
        "filename": "After DnD ： เมื่อบาร์ดด่าจนมังกรตาย!.mp4",
        "mediapool_id": "9ae1c0ee-6b90-482e-ac71-a5aac9a6f262",
        "game_tag": "DnD",
        "category": "Talk / D&D Comedy",
        "status": "PROCESSED",
        "duration_sec": 9053.43,
        "frames_60fps": 543206,
        "resolution": "1280x720"
    },
    {
        "index": 4,
        "filename": "Collab R.E.P.O - เก็บของไว้ให้ไกลเสือ.mp4",
        "mediapool_id": "4462a5cf-dad7-4499-ab4d-20a999ba2b59",
        "game_tag": "REPO",
        "category": "Gaming / R.E.P.O Co-op",
        "status": "PROCESSED",
        "duration_sec": 10259.33,
        "frames_60fps": 615560,
        "resolution": "1920x1080"
    },
    {
        "index": 5,
        "filename": "Free Talk - ปิดคาสิโนแล้วบอสไปทำไรต่อ.mp4",
        "mediapool_id": "b3931d4e-7ce5-452b-9cc9-2a667e5607fd",
        "game_tag": "FreeTalk",
        "category": "Free Talk",
        "status": "UNTOUCHED",
        "duration_sec": 4398.05,
        "frames_60fps": 263883,
        "resolution": "1280x720"
    },
    {
        "index": 6,
        "filename": "Free Talk ติดเกาะกับเธอ จ้างเท่าไหร่ก็ไม่ออก.mp4",
        "mediapool_id": "6d94e629-b683-43ee-894a-ac94c805c736",
        "game_tag": "FreeTalk",
        "category": "Free Talk",
        "status": "UNTOUCHED",
        "duration_sec": 17002.73,
        "frames_60fps": 1020164,
        "resolution": "1280x720"
    },
    {
        "index": 7,
        "filename": "Free Talk ： จีบ 10 ปี แถมฟรีหนี้ 200 ล้าน.mp4",
        "mediapool_id": "99bf4a6d-245e-4a9a-8889-10b1d6b40203",
        "game_tag": "FreeTalk",
        "category": "Free Talk / Story",
        "status": "UNTOUCHED",
        "duration_sec": 8230.11,
        "frames_60fps": 493807,
        "resolution": "1280x720"
    },
    {
        "index": 8,
        "filename": "Free Talk ： หยุดเสือด้วยมือเปล่า？？.mp4",
        "mediapool_id": "e56002ed-9d9e-4cc4-97c9-fd191a631f5e",
        "game_tag": "FreeTalk",
        "category": "Free Talk / Meme",
        "status": "PROCESSED",
        "duration_sec": 7704.02,
        "frames_60fps": 462241,
        "resolution": "1280x720"
    },
    {
        "index": 9,
        "filename": "Free Talk ：สอนไทกะเป็นโจรสลัดที.mp4",
        "mediapool_id": "58c86277-78be-4d93-9ecc-258f9a8723b5",
        "game_tag": "FreeTalk",
        "category": "Free Talk",
        "status": "UNTOUCHED",
        "duration_sec": 5386.01,
        "frames_60fps": 323161,
        "resolution": "1280x720"
    },
    {
        "index": 10,
        "filename": "Free Talk ：เมื่อได้เป็นตัวโดนประจำตี้.mp4",
        "mediapool_id": "aa7e9833-0b07-4cad-9951-b7dd0b15c607",
        "game_tag": "FreeTalk",
        "category": "Free Talk / Banter",
        "status": "UNTOUCHED",
        "duration_sec": 6232.01,
        "frames_60fps": 373921,
        "resolution": "1920x1080"
    },
    {
        "index": 11,
        "filename": "Free Talk ：เมื่อไทกะเล่น เกย์กับชายใน DnD โดยไม่รู้ตัว.mp4",
        "mediapool_id": "b4196bbd-e94a-401b-abe3-eca5d6e056f4",
        "game_tag": "FreeTalk",
        "category": "Free Talk / DnD Meme",
        "status": "UNTOUCHED",
        "duration_sec": 8127.29,
        "frames_60fps": 487638,
        "resolution": "1280x720"
    },
    {
        "index": 12,
        "filename": "Free Talk： ลูกน้องไม่ตอบก็จะคุย!.mp4",
        "mediapool_id": "c483d870-8c4f-494a-9ca7-61631f47608c",
        "game_tag": "FreeTalk",
        "category": "Free Talk",
        "status": "UNTOUCHED",
        "duration_sec": 5201.11,
        "frames_60fps": 312067,
        "resolution": "1280x720"
    },
    {
        "index": 13,
        "filename": "Gartic phone - ไทกะสกิลวาดรูป 999999.mp4",
        "mediapool_id": "88c9437b-cf33-48e5-98d5-5faf4844742d",
        "game_tag": "GarticPhone",
        "category": "Party Game / Meme",
        "status": "PROCESSED",
        "duration_sec": 8435.23,
        "frames_60fps": 506114,
        "resolution": "1280x720"
    },
    {
        "index": 14,
        "filename": "IB - สำรวจโลกภาพวาด P1.mp4",
        "mediapool_id": "7a4e9419-b627-4b4f-87db-9a0d7af59fe2",
        "game_tag": "Ib",
        "category": "Gaming / Horror",
        "status": "PROCESSED",
        "duration_sec": 8768.33,
        "frames_60fps": 526100,
        "resolution": "1280x720"
    },
    {
        "index": 15,
        "filename": "IB - สำรวจโลกภาพวาด P2 @caramellatte710.mp4",
        "mediapool_id": "dcb04276-39a9-41f0-9cdd-53b1bafc5752",
        "game_tag": "Ib",
        "category": "Gaming / Horror Collab",
        "status": "UNTOUCHED",
        "duration_sec": 14345.69,
        "frames_60fps": 860742,
        "resolution": "1280x720"
    },
    {
        "index": 16,
        "filename": "MEET BOSS ： บอสเราเจอผู้หญิงไม่ได้เลย.mp4",
        "mediapool_id": "4600079c-dfb7-41ca-9ce8-284f1d9161c7",
        "game_tag": "FreeTalk",
        "category": "Banter / Fun Collab",
        "status": "UNTOUCHED",
        "duration_sec": 11176.42,
        "frames_60fps": 670585,
        "resolution": "1280x720"
    },
    {
        "index": 17,
        "filename": "R.E.P.O @Luche_Sinclair @Kungphaokung @RahhatemPSM @Salika_SaharasCh.mp4",
        "mediapool_id": "b3fdb6ac-e495-45b7-9bce-5ff92b809fd7",
        "game_tag": "REPO",
        "category": "Gaming / R.E.P.O Collab",
        "status": "UNTOUCHED",
        "duration_sec": 7240.29,
        "frames_60fps": 434418,
        "resolution": "1280x720"
    },
    {
        "index": 18,
        "filename": "R.E.P.O @ballkarozumar1238 @F4RC14  @momomewmoi @Mikhail_Cerise.mp4",
        "mediapool_id": "a1af7fdd-bf9d-4166-b15a-7108d7a3ece7",
        "game_tag": "REPO",
        "category": "Gaming / R.E.P.O Collab",
        "status": "UNTOUCHED",
        "duration_sec": 11278.75,
        "frames_60fps": 676725,
        "resolution": "1280x720"
    },
    {
        "index": 19,
        "filename": "R.E.P.O @ballkarozumar1238 @F4RC14  @momomewmoi @mitsuki_mayu@NANOZEROO.mp4",
        "mediapool_id": "56e2c71f-976c-4cbd-9d23-b4d2834c19df",
        "game_tag": "REPO",
        "category": "Gaming / R.E.P.O Collab",
        "status": "UNTOUCHED",
        "duration_sec": 11150.41,
        "frames_60fps": 669025,
        "resolution": "1280x720"
    },
    {
        "index": 20,
        "filename": "ฉลอง 800 ซับ! วงล้อเสี่ยงท้าย!!.mp4",
        "mediapool_id": "03273e5a-487f-4a23-a3fb-a56ba1ce4a3f",
        "game_tag": "FreeTalk",
        "category": "Celebration / Fun",
        "status": "UNTOUCHED",
        "duration_sec": 5040.23,
        "frames_60fps": 302414,
        "resolution": "1280x720"
    },
    {
        "index": 21,
        "filename": "บอสทำไรตอนตี 2？？.mp4",
        "mediapool_id": "68b3833d-61bf-4b7c-b8eb-95c2b970ab8a",
        "game_tag": "FreeTalk",
        "category": "Free Talk / Meme",
        "status": "UNTOUCHED",
        "duration_sec": 3346.73,
        "frames_60fps": 200804,
        "resolution": "1920x1080"
    },
    {
        "index": 22,
        "filename": "ปืนเขาที่เราหมดแรง @KRATOI_26  @Mixzy21PM  @Pleiades_Frontier.mp4",
        "mediapool_id": "3ebbdd92-9aa6-4738-b586-956bf85f35d6",
        "game_tag": "Climbing",
        "category": "Gaming / Climbing Collab",
        "status": "PROCESSED",
        "duration_sec": 6945.09,
        "frames_60fps": 416706,
        "resolution": "1920x1080"
    },
    {
        "index": 23,
        "filename": "ฝึกเล่น LoL.mp4",
        "mediapool_id": "12a09f5f-b6b0-47fc-8e1f-41ba5c009ab4",
        "game_tag": "LoL",
        "category": "Gaming / LoL",
        "status": "UNTOUCHED",
        "duration_sec": 6210.17,
        "frames_60fps": 372610,
        "resolution": "1280x720"
    },
    {
        "index": 24,
        "filename": "รายการ ： Q&A คุยกับนกแก้ว.mp4",
        "mediapool_id": "fc777b1b-0b4c-4176-8805-05a65110b206",
        "game_tag": "FreeTalk",
        "category": "Free Talk / Q&A",
        "status": "UNTOUCHED",
        "duration_sec": 6450.21,
        "frames_60fps": 387013,
        "resolution": "1280x720"
    },
    {
        "index": 25,
        "filename": "สอนไทกะเล่น LoL ที.mp4",
        "mediapool_id": "35d91ae8-0efc-474b-8034-21b09eb5cc3a",
        "game_tag": "LoL",
        "category": "Gaming / LoL Collab",
        "status": "UNTOUCHED",
        "duration_sec": 9091.17,
        "frames_60fps": 545470,
        "resolution": "1280x720"
    },
    {
        "index": 26,
        "filename": "เมื่อไทกะคือความชิบหายในครัว!.mp4",
        "mediapool_id": "407b877a-89c8-42b1-bc6d-71fbcd5fb6d1",
        "game_tag": "Overcooked",
        "category": "Gaming / Overcooked Chaos",
        "status": "PROCESSED",
        "duration_sec": 12215.17,
        "frames_60fps": 732910,
        "resolution": "1280x720"
    },
    {
        "index": 27,
        "filename": "เสืออยากคุย [VqELVP2u2oU].mp4",
        "mediapool_id": "d9d8a666-c3f9-4dc8-b037-68d887eab4dd",
        "game_tag": "FreeTalk",
        "category": "Free Talk",
        "status": "UNTOUCHED",
        "duration_sec": 8243.05,
        "frames_60fps": 494583,
        "resolution": "1920x1080"
    },
    {
        "index": 28,
        "filename": "เสืออยากคุย [ns0I3EihIUI].mp4",
        "mediapool_id": "b04b6312-022f-44a4-be57-9ff9e0c14661",
        "game_tag": "FreeTalk",
        "category": "Free Talk",
        "status": "UNTOUCHED",
        "duration_sec": 11841.67,
        "frames_60fps": 710500,
        "resolution": "1920x1080"
    },
    {
        "index": 29,
        "filename": "เสืออยากคุย [qZVnCXIjfzo].mp4",
        "mediapool_id": "00cc01c1-f3cc-4666-a40c-197214ba162e",
        "game_tag": "FreeTalk",
        "category": "Free Talk",
        "status": "UNTOUCHED",
        "duration_sec": 7969.05,
        "frames_60fps": 478143,
        "resolution": "1920x1080"
    },
    {
        "index": 30,
        "filename": "ใช้ชีวิตไปกับไทกะ 101 (ไม่ชินกล้องเลย).mp4",
        "mediapool_id": "12371e44-432d-45d1-b9d2-fe3c1017b2f8",
        "game_tag": "FreeTalk",
        "category": "Free Talk / Debut",
        "status": "UNTOUCHED",
        "duration_sec": 7529.19,
        "frames_60fps": 451752,
        "resolution": "1920x1080"
    },
    {
        "index": 31,
        "filename": "ไลฟ์คุยไปเรื่อยแบบเสือขี้เบื่อ.mp4",
        "mediapool_id": "1e4a373c-80b2-41f3-840b-9a04b12ae218",
        "game_tag": "FreeTalk",
        "category": "Free Talk",
        "status": "UNTOUCHED",
        "duration_sec": 7653.21,
        "frames_60fps": 459193,
        "resolution": "1920x1080"
    },
    {
        "index": 32,
        "filename": "ไลฟ์นี้จะเล่น Fallout 4 Nuka-world P1.mp4",
        "mediapool_id": "8d711ef7-b6fc-444e-8f07-281d928da30d",
        "game_tag": "Fallout4",
        "category": "Gaming / Fallout 4",
        "status": "UNTOUCHED",
        "duration_sec": 23696.78,
        "frames_60fps": 1421807,
        "resolution": "1920x1080"
    }
]

# 2. 60 Proposed Primary Highlight Titles
PRIMARY_60_TITLES = [
    # Untouched File 1 (DnD)
    {"id": 1, "file": "After DnD EP.4 ตอน เมื่อไทกะนอนไม่หลับเพราะความรัก.mp4", "game": "DnD", "title": "เล่าเรื่องความรักจนนอนไม่หลับ_DnD-vdo", "type": "Untouched Coverage"},
    {"id": 2, "file": "After DnD EP.4 ตอน เมื่อไทกะนอนไม่หลับเพราะความรัก.mp4", "game": "DnD", "title": "สารภาพความในใจสุดเขินกลางตี้_DnD-vdo", "type": "Untouched Coverage"},
    # Untouched File 2 (DnD)
    {"id": 3, "file": "After DnD ： หลอนครั้งแรกแต่จบดาร์กขั้นสุด.mp4", "game": "DnD", "title": "เปิดประสบการณ์หลอนครั้งแรกในชีวิต_DnD-vdo", "type": "Untouched Coverage"},
    {"id": 4, "file": "After DnD ： หลอนครั้งแรกแต่จบดาร์กขั้นสุด.mp4", "game": "DnD", "title": "ตอนจบสุดดาร์กทำเอาเหวอทั้งโต๊ะ_DnD-vdo", "type": "Untouched Coverage"},
    # Untouched File 5 (FreeTalk)
    {"id": 5, "file": "Free Talk - ปิดคาสิโนแล้วบอสไปทำไรต่อ.mp4", "game": "FreeTalk", "title": "ปิดคาสิโนแล้วไปหาของกินรอบดึก_FreeTalk-vdo", "type": "Untouched Coverage"},
    {"id": 6, "file": "Free Talk - ปิดคาสิโนแล้วบอสไปทำไรต่อ.mp4", "game": "FreeTalk", "title": "บ่นเรื่องงานจนลืมเวลาพักผ่อน_FreeTalk-vdo", "type": "Untouched Coverage"},
    # Untouched File 6 (FreeTalk)
    {"id": 7, "file": "Free Talk ติดเกาะกับเธอ จ้างเท่าไหร่ก็ไม่ออก.mp4", "game": "FreeTalk", "title": "ถ้าต้องติดเกาะขอเลือกนอนเฉยๆดีกว่า_FreeTalk-vdo", "type": "Untouched Coverage"},
    {"id": 8, "file": "Free Talk ติดเกาะกับเธอ จ้างเท่าไหร่ก็ไม่ออก.mp4", "game": "FreeTalk", "title": "จ้างร้อยล้านก็ไม่ยอมย้ายไปไหน_FreeTalk-vdo", "type": "Untouched Coverage"},
    # Untouched File 7 (FreeTalk)
    {"id": 9, "file": "Free Talk ： จีบ 10 ปี แถมฟรีหนี้ 200 ล้าน.mp4", "game": "FreeTalk", "title": "บทเรียนชีวิตจีบสิบปีแต่มีหนี้แถมมา_FreeTalk-vdo", "type": "Untouched Coverage"},
    {"id": 10, "file": "Free Talk ： จีบ 10 ปี แถมฟรีหนี้ 200 ล้าน.mp4", "game": "FreeTalk", "title": "เตือนสติคนดูเรื่องความรักสุดพัง_FreeTalk-vdo", "type": "Untouched Coverage"},
    # Untouched File 9 (FreeTalk)
    {"id": 11, "file": "Free Talk ：สอนไทกะเป็นโจรสลัดที.mp4", "game": "FreeTalk", "title": "ฝึกเป็นกัปตันเรือแต่โดนลูกเรือแซว_FreeTalk-vdo", "type": "Untouched Coverage"},
    {"id": 12, "file": "Free Talk ：สอนไทกะเป็นโจรสลัดที.mp4", "game": "FreeTalk", "title": "แผนการออกทะเลล่าขุมทรัพย์สุดเพี้ยน_FreeTalk-vdo", "type": "Untouched Coverage"},
    # Untouched File 10 (FreeTalk)
    {"id": 13, "file": "Free Talk ：เมื่อได้เป็นตัวโดนประจำตี้.mp4", "game": "FreeTalk", "title": "ตัดพ้อชีวิตทำไมต้องเป็นตัวโดนตลอด_FreeTalk-vdo", "type": "Untouched Coverage"},
    {"id": 14, "file": "Free Talk ：เมื่อได้เป็นตัวโดนประจำตี้.mp4", "game": "FreeTalk", "title": "โดนเพื่อนรุมแกงจนแทบอยากปิดไมค์_FreeTalk-vdo", "type": "Untouched Coverage"},
    # Untouched File 11 (FreeTalk)
    {"id": 15, "file": "Free Talk ：เมื่อไทกะเล่น เกย์กับชายใน DnD โดยไม่รู้ตัว.mp4", "game": "FreeTalk", "title": "สับสนบทบาทจนเพื่อนต้องสะกิดเตือน_FreeTalk-vdo", "type": "Untouched Coverage"},
    {"id": 16, "file": "Free Talk ：เมื่อไทกะเล่น เกย์กับชายใน DnD โดยไม่รู้ตัว.mp4", "game": "FreeTalk", "title": "เผลอสร้างตำนานคู่จิ้นกลางวงสนทนา_FreeTalk-vdo", "type": "Untouched Coverage"},
    # Untouched File 12 (FreeTalk)
    {"id": 17, "file": "Free Talk： ลูกน้องไม่ตอบก็จะคุย!.mp4", "game": "FreeTalk", "title": "เรียกชื่อลูกน้องรัวๆจนต้องยอมเปิดไมค์_FreeTalk-vdo", "type": "Untouched Coverage"},
    {"id": 18, "file": "Free Talk： ลูกน้องไม่ตอบก็จะคุย!.mp4", "game": "FreeTalk", "title": "บ่นน้อยใจลูกน้องแกล้งทำเป็นไม่ได้ยิน_FreeTalk-vdo", "type": "Untouched Coverage"},
    # Untouched File 15 (Ib)
    {"id": 19, "file": "IB - สำรวจโลกภาพวาด P2 @caramellatte710.mp4", "game": "Ib", "title": "กรี๊ดลั่นหอศิลป์เมื่อเจอรูปปั้นขยับได้_Ib-vdo", "type": "Untouched Coverage"},
    {"id": 20, "file": "IB - สำรวจโลกภาพวาด P2 @caramellatte710.mp4", "game": "Ib", "title": "พากันวิ่งหนีผีเสื้อยักษ์เกือบไม่รอด_Ib-vdo", "type": "Untouched Coverage"},
    # Untouched File 16 (FreeTalk)
    {"id": 21, "file": "MEET BOSS ： บอสเราเจอผู้หญิงไม่ได้เลย.mp4", "game": "FreeTalk", "title": "อาการเสียอาการเมื่อต้องคุยกับสาวสวย_FreeTalk-vdo", "type": "Untouched Coverage"},
    {"id": 22, "file": "MEET BOSS ： บอสเราเจอผู้หญิงไม่ได้เลย.mp4", "game": "FreeTalk", "title": "โดนแซวเรื่องแพ้ทางผู้หญิงจนหน้าแดง_FreeTalk-vdo", "type": "Untouched Coverage"},
    # Untouched File 17 (REPO)
    {"id": 23, "file": "R.E.P.O @Luche_Sinclair @Kungphaokung @RahhatemPSM @Salika_SaharasCh.mp4", "game": "REPO", "title": "โดนตัวประหลาดลากเข้าเงามืดต่อหน้าเพื่อน_REPO-vdo", "type": "Untouched Coverage"},
    {"id": 24, "file": "R.E.P.O @Luche_Sinclair @Kungphaokung @RahhatemPSM @Salika_SaharasCh.mp4", "game": "REPO", "title": "จังหวะขโมยของหนีออกจากประตูลับ_REPO-vdo", "type": "Untouched Coverage"},
    # Untouched File 18 (REPO)
    {"id": 25, "file": "R.E.P.O @ballkarozumar1238 @F4RC14  @momomewmoi @Mikhail_Cerise.mp4", "game": "REPO", "title": "เสียงฝีเท้าปริศนาทำเอาสะดุ้งทั้งตี้_REPO-vdo", "type": "Untouched Coverage"},
    {"id": 26, "file": "R.E.P.O @ballkarozumar1238 @F4RC14  @momomewmoi @Mikhail_Cerise.mp4", "game": "REPO", "title": "ตะโกนเตือนเพื่อนแต่โดนทิ้งไว้ข้างหลัง_REPO-vdo", "type": "Untouched Coverage"},
    # Untouched File 19 (REPO)
    {"id": 27, "file": "R.E.P.O @ballkarozumar1238 @F4RC14  @momomewmoi @mitsuki_mayu@NANOZEROO.mp4", "game": "REPO", "title": "เดินตกหลุมกับดักเพราะมัวแต่มองของ_REPO-vdo", "type": "Untouched Coverage"},
    {"id": 28, "file": "R.E.P.O @ballkarozumar1238 @F4RC14  @momomewmoi @mitsuki_mayu@NANOZEROO.mp4", "game": "REPO", "title": "แบกของหนักวิ่งหนีตายวินาทีสุดท้าย_REPO-vdo", "type": "Untouched Coverage"},
    # Untouched File 20 (FreeTalk)
    {"id": 29, "file": "ฉลอง 800 ซับ! วงล้อเสี่ยงท้าย!!.mp4", "game": "FreeTalk", "title": "หมุนวงล้อเสี่ยงทายเจอแต่บทลงโทษสุดกาว_FreeTalk-vdo", "type": "Untouched Coverage"},
    {"id": 30, "file": "ฉลอง 800 ซับ! วงล้อเสี่ยงท้าย!!.mp4", "game": "FreeTalk", "title": "กราบขอบคุณคนดูที่ร่วมเดินทางมาด้วยกัน_FreeTalk-vdo", "type": "Untouched Coverage"},
    # Untouched File 21 (FreeTalk)
    {"id": 31, "file": "บอสทำไรตอนตี 2？？.mp4", "game": "FreeTalk", "title": "เผยพฤติกรรมสุดแปลกตอนดึกสงัด_FreeTalk-vdo", "type": "Untouched Coverage"},
    {"id": 32, "file": "บอสทำไรตอนตี 2？？.mp4", "game": "FreeTalk", "title": "นั่งคุยคนเดียวตอนตีสองจนรู้สึกวังเวง_FreeTalk-vdo", "type": "Untouched Coverage"},
    # Untouched File 23 (LoL)
    {"id": 33, "file": "ฝึกเล่น LoL.mp4", "game": "LoL", "title": "กดสกิลวืดกลางเลนจนโดนป้อมยิงตาย_LoL-vdo", "type": "Untouched Coverage"},
    {"id": 34, "file": "ฝึกเล่น LoL.mp4", "game": "LoL", "title": "จังหวะไฟต์ชุลมุนกดมั่วจนได้คิลเฉย_LoL-vdo", "type": "Untouched Coverage"},
    # Untouched File 24 (FreeTalk)
    {"id": 35, "file": "รายการ ： Q&A คุยกับนกแก้ว.mp4", "game": "FreeTalk", "title": "ตอบคำถามแฟนคลับเรื่องอาหารจานโปรด_FreeTalk-vdo", "type": "Untouched Coverage"},
    {"id": 36, "file": "รายการ ： Q&A คุยกับนกแก้ว.mp4", "game": "FreeTalk", "title": "นกแก้วพูดแทรกจังหวะสำคัญจนหลุดขำ_FreeTalk-vdo", "type": "Untouched Coverage"},
    # Untouched File 25 (LoL)
    {"id": 37, "file": "สอนไทกะเล่น LoL ที.mp4", "game": "LoL", "title": "โดนโค้ชบ่นเรื่องลืมซื้อของตอนเริ่มเกม_LoL-vdo", "type": "Untouched Coverage"},
    {"id": 38, "file": "สอนไทกะเล่น LoL ที.mp4", "game": "LoL", "title": "จังหวะลาสบอสใหญ่ขโมยมังกรสุดเทพ_LoL-vdo", "type": "Untouched Coverage"},
    # Untouched File 27 (FreeTalk)
    {"id": 39, "file": "เสืออยากคุย [VqELVP2u2oU].mp4", "game": "FreeTalk", "title": "เล่าเรื่องวัยเด็กสุดแสบที่ไม่มีใครเคยรู้_FreeTalk-vdo", "type": "Untouched Coverage"},
    {"id": 40, "file": "เสืออยากคุย [VqELVP2u2oU].mp4", "game": "FreeTalk", "title": "ร้องเพลงเพี้ยนแต่ใส่อารมณ์เกินร้อย_FreeTalk-vdo", "type": "Untouched Coverage"},
    # Untouched File 28 (FreeTalk)
    {"id": 41, "file": "เสืออยากคุย [ns0I3EihIUI].mp4", "game": "FreeTalk", "title": "ถกประเด็นของกินข้างทางที่อร่อยที่สุด_FreeTalk-vdo", "type": "Untouched Coverage"},
    {"id": 42, "file": "เสืออยากคุย [ns0I3EihIUI].mp4", "game": "FreeTalk", "title": "จังหวะจามเสียงดังจนกล้องสั่น_FreeTalk-vdo", "type": "Untouched Coverage"},
    # Untouched File 29 (FreeTalk)
    {"id": 43, "file": "เสืออยากคุย [qZVnCXIjfzo].mp4", "game": "FreeTalk", "title": "แชร์ประสบการณ์นอนดึกจนตาเป็นหมีแพนด้า_FreeTalk-vdo", "type": "Untouched Coverage"},
    {"id": 44, "file": "เสืออยากคุย [qZVnCXIjfzo].mp4", "game": "FreeTalk", "title": "อ่านแชทคอมเมนต์กวนๆแล้วหลุดขำก๊าก_FreeTalk-vdo", "type": "Untouched Coverage"},
    # Untouched File 30 (FreeTalk)
    {"id": 45, "file": "ใช้ชีวิตไปกับไทกะ 101 (ไม่ชินกล้องเลย).mp4", "game": "FreeTalk", "title": "เขินกล้องจนทำตัวไม่ถูกในไลฟ์แรกๆ_FreeTalk-vdo", "type": "Untouched Coverage"},
    {"id": 46, "file": "ใช้ชีวิตไปกับไทกะ 101 (ไม่ชินกล้องเลย).mp4", "game": "FreeTalk", "title": "สอนวิธีปรับตัวเมื่อต้องเจอกับคนแปลกหน้า_FreeTalk-vdo", "type": "Untouched Coverage"},
    # Untouched File 31 (FreeTalk)
    {"id": 47, "file": "ไลฟ์คุยไปเรื่อยแบบเสือขี้เบื่อ.mp4", "game": "FreeTalk", "title": "บ่นความเหงาในวันฝนตกชวนง่วงนอน_FreeTalk-vdo", "type": "Untouched Coverage"},
    {"id": 48, "file": "ไลฟ์คุยไปเรื่อยแบบเสือขี้เบื่อ.mp4", "game": "FreeTalk", "title": "เล่นมุกแป้กแต่หัวเราะแก้เขินคนเดียว_FreeTalk-vdo", "type": "Untouched Coverage"},
    # Untouched File 32 (Fallout4)
    {"id": 49, "file": "ไลฟ์นี้จะเล่น Fallout 4 Nuka-world P1.mp4", "game": "Fallout4", "title": "เจอกับดักระเบิดตู้มเดียวบินขึ้นฟ้า_Fallout4-vdo", "type": "Untouched Coverage"},
    {"id": 50, "file": "ไลฟ์นี้จะเล่น Fallout 4 Nuka-world P1.mp4", "game": "Fallout4", "title": "สู้สัตว์ประหลาดในสวนสนุกจนกระสุนหมดเกลี้ยง_Fallout4-vdo", "type": "Untouched Coverage"},

    # 10 Peak Highlights across high-action footage
    {"id": 51, "file": "Collab R.E.P.O - เก็บของไว้ให้ไกลเสือ.mp4", "game": "REPO", "title": "เสียงกรีดร้องสะท้อนทางเดินใต้ดินสุดหลอน_REPO-vdo", "type": "Peak Highlight"},
    {"id": 52, "file": "ปืนเขาที่เราหมดแรง @KRATOI_26  @Mixzy21PM  @Pleiades_Frontier.mp4", "game": "Climbing", "title": "เชือกตึงเปรี๊ยะห้อยต่องแต่งกลางสายหมอก_Climbing-vdo", "type": "Peak Highlight"},
    {"id": 53, "file": "IB - สำรวจโลกภาพวาด P1.mp4", "game": "Ib", "title": "สะดุ้งตัวโยนเลือดหยดใส่หน้าภาพวาด_Ib-vdo", "type": "Peak Highlight"},
    {"id": 54, "file": "After DnD ： เมื่อบาร์ดด่าจนมังกรตาย!.mp4", "game": "DnD", "title": "รวมพลังด่ามังกรจนบอสสิ้นใจคาที่_DnD-vdo", "type": "Peak Highlight"},
    {"id": 55, "file": "Gartic phone - ไทกะสกิลวาดรูป 999999.mp4", "game": "GarticPhone", "title": "ทายคำตอบผิดจนเนื้อเรื่องออกทะเล_GarticPhone-vdo", "type": "Peak Highlight"},
    {"id": 56, "file": "Free Talk ： หยุดเสือด้วยมือเปล่า？？.mp4", "game": "FreeTalk", "title": "สอนวิชาป้องกันตัวด้วยกำปั้นเปล่าสุดฮา_FreeTalk-vdo", "type": "Peak Highlight"},
    {"id": 57, "file": "เมื่อไทกะคือความชิบหายในครัว!.mp4", "game": "Overcooked", "title": "โยนวัตถุดิบข้ามฝั่งชนหัวเพื่อนเต็มๆ_Overcooked-vdo", "type": "Peak Highlight"},
    {"id": 58, "file": "ไลฟ์นี้จะเล่น Fallout 4 Nuka-world P1.mp4", "game": "Fallout4", "title": "หลงทางในแดนรกร้างเดินวนอยู่ที่เดิม_Fallout4-vdo", "type": "Peak Highlight"},
    {"id": 59, "file": "สอนไทกะเล่น LoL ที.mp4", "game": "LoL", "title": "จังหวะโดนดักซุ่มพุ่มไม้ร้องเสียงหลง_LoL-vdo", "type": "Peak Highlight"},
    {"id": 60, "file": "R.E.P.O @Luche_Sinclair @Kungphaokung @RahhatemPSM @Salika_SaharasCh.mp4", "game": "REPO", "title": "เพื่อนโดนงาบต่อหน้าต่อตาช่วยไม่ทัน_REPO-vdo", "type": "Peak Highlight"}
]

# 3. Reserve / Expansion Pool (30 Additional Validated Titles)
RESERVE_TITLES = [
    {"file": "Collab R.E.P.O - เก็บของไว้ให้ไกลเสือ.mp4", "game": "REPO", "title": "วิ่งฝ่าความมืดแทบขาดใจ_REPO-vdo"},
    {"file": "Collab R.E.P.O - เก็บของไว้ให้ไกลเสือ.mp4", "game": "REPO", "title": "หยิบของผิดชิ้นจนโดนเพื่อนบ่น_REPO-vdo"},
    {"file": "ปืนเขาที่เราหมดแรง @KRATOI_26  @Mixzy21PM  @Pleiades_Frontier.mp4", "game": "Climbing", "title": "จังหวะเกือบตกเขาแต่คว้าทันเฉียดฉิว_Climbing-vdo"},
    {"file": "ปืนเขาที่เราหมดแรง @KRATOI_26  @Mixzy21PM  @Pleiades_Frontier.mp4", "game": "Climbing", "title": "แกล้งดึงเชือกเพื่อนจนร้องกรี๊ด_Climbing-vdo"},
    {"file": "IB - สำรวจโลกภาพวาด P1.mp4", "game": "Ib", "title": "อ่านข้อความปริศนาบนผนังห้อง_Ib-vdo"},
    {"file": "IB - สำรวจโลกภาพวาด P1.mp4", "game": "Ib", "title": "เดินสะดุดกับดักจนตกใจกระโดด_Ib-vdo"},
    {"file": "After DnD ： เมื่อบาร์ดด่าจนมังกรตาย!.mp4", "game": "DnD", "title": "เล่าเรื่องตอนจบแคมเปญสุดซึ้ง_DnD-vdo"},
    {"file": "After DnD ： เมื่อบาร์ดด่าจนมังกรตาย!.mp4", "game": "DnD", "title": "ความลับของตัวละครถูกเปิดเผย_DnD-vdo"},
    {"file": "Gartic phone - ไทกะสกิลวาดรูป 999999.mp4", "game": "GarticPhone", "title": "วาดรูปแมวแต่เพื่อนทายว่าเป็นเสือ_GarticPhone-vdo"},
    {"file": "Gartic phone - ไทกะสกิลวาดรูป 999999.mp4", "game": "GarticPhone", "title": "หัวเราะจนปวดกรามกับลายเส้นเพื่อน_GarticPhone-vdo"},
    {"file": "เมื่อไทกะคือความชิบหายในครัว!.mp4", "game": "Overcooked", "title": "ส่งอาหารผิดโต๊ะจนคะแนนติดลบ_Overcooked-vdo"},
    {"file": "เมื่อไทกะคือความชิบหายในครัว!.mp4", "game": "Overcooked", "title": "ดับไฟในครัวไม่ทันไฟไหม้วอด_Overcooked-vdo"},
    {"file": "ฝึกเล่น LoL.mp4", "game": "LoL", "title": "คิลแรกของเกมดีใจจนร้องลั่น_LoL-vdo"},
    {"file": "ฝึกเล่น LoL.mp4", "game": "LoL", "title": "โดนเพื่อนร่วมทีมเตือนสติให้อยู่ในเลน_LoL-vdo"},
    {"file": "สอนไทกะเล่น LoL ที.mp4", "game": "LoL", "title": "จังหวะบวกยับกลางแม่น้ำชนะเฉย_LoL-vdo"},
    {"file": "สอนไทกะเล่น LoL ที.mp4", "game": "LoL", "title": "สอนวิธีออกของแก้ทางศัตรู_LoL-vdo"},
    {"file": "ไลฟ์นี้จะเล่น Fallout 4 Nuka-world P1.mp4", "game": "Fallout4", "title": "สร้างฐานทัพสุดอลังการแต่ของหมด_Fallout4-vdo"},
    {"file": "ไลฟ์นี้จะเล่น Fallout 4 Nuka-world P1.mp4", "game": "Fallout4", "title": "บุกรังศัตรูถล่มด้วยปืนกลหนัก_Fallout4-vdo"},
    {"file": "Free Talk ： หยุดเสือด้วยมือเปล่า？？.mp4", "game": "FreeTalk", "title": "เล่าเรื่องเจอสัตว์ดุร้ายในป่าใหญ่_FreeTalk-vdo"},
    {"file": "Free Talk ： หยุดเสือด้วยมือเปล่า？？.mp4", "game": "FreeTalk", "title": "ตอบคำถามแชทเรื่องความฝันแปลกๆ_FreeTalk-vdo"},
    {"file": "Free Talk - ปิดคาสิโนแล้วบอสไปทำไรต่อ.mp4", "game": "FreeTalk", "title": "แอบหนีเที่ยวกลางดึกคนเดียว_FreeTalk-vdo"},
    {"file": "Free Talk ติดเกาะกับเธอ จ้างเท่าไหร่ก็ไม่ออก.mp4", "game": "FreeTalk", "title": "จำลองชีวิตชาวเกาะหาปลาประทังชีวิต_FreeTalk-vdo"},
    {"file": "Free Talk ： จีบ 10 ปี แถมฟรีหนี้ 200 ล้าน.mp4", "game": "FreeTalk", "title": "วิเคราะห์ความสัมพันธ์ชวนปวดหัว_FreeTalk-vdo"},
    {"file": "Free Talk ：สอนไทกะเป็นโจรสลัดที.mp4", "game": "FreeTalk", "title": "ตั้งชื่อเรือโจรสลัดสุดเกรงขาม_FreeTalk-vdo"},
    {"file": "Free Talk ：เมื่อได้เป็นตัวโดนประจำตี้.mp4", "game": "FreeTalk", "title": "หาพวกช่วยเถียงแต่ไม่มีใครเข้าข้าง_FreeTalk-vdo"},
    {"file": "Free Talk： ลูกน้องไม่ตอบก็จะคุย!.mp4", "game": "FreeTalk", "title": "แซวลูกน้องจนยอมสารภาพความจริง_FreeTalk-vdo"},
    {"file": "บอสทำไรตอนตี 2？？.mp4", "game": "FreeTalk", "title": "เปิดตู้เย็นหาของหวานกินรอบดึก_FreeTalk-vdo"},
    {"file": "รายการ ： Q&A คุยกับนกแก้ว.mp4", "game": "FreeTalk", "title": "นกแก้วเลียนเสียงหัวเราะเป๊ะเวอร์_FreeTalk-vdo"},
    {"file": "เสืออยากคุย [ns0I3EihIUI].mp4", "game": "FreeTalk", "title": "รีวิวเมนูโปรดที่ไม่ว่าใครก็ต้องชอบ_FreeTalk-vdo"},
    {"file": "ไลฟ์คุยไปเรื่อยแบบเสือขี้เบื่อ.mp4", "game": "FreeTalk", "title": "นั่งดูคลิปตลกแล้วขำจนสำลักน้ำ_FreeTalk-vdo"}
]

# Validation
with open('.agents/teamwork/explorer_survey_r4_3/current_state.json', encoding='utf-8') as f:
    state = json.load(f)
existing_tl_names = set(tl['name'] for tl in state['timelines'])

NAMING_REGEX = re.compile(r"^([\u0E00-\u0E7F]+)_([A-Za-z0-9]+)-vdo$")

all_titles_to_check = [("PRIMARY", item) for item in PRIMARY_60_TITLES] + [("RESERVE", item) for item in RESERVE_TITLES]
errors = []
seen = set()

validation_details = []

for pool_type, item in all_titles_to_check:
    title = item["title"]
    m = NAMING_REGEX.match(title)
    if not m:
        errors.append(f"[{pool_type}] Regex fail: '{title}'")
        continue
    prefix, game_tag = m.groups()
    if game_tag != item["game"]:
        errors.append(f"[{pool_type}] Tag mismatch '{game_tag}' != '{item['game']}'")
    
    char_codepoints = []
    for c in prefix:
        cp = ord(c)
        char_codepoints.append(f"U+{cp:04X}")
        if not (0x0E00 <= cp <= 0x0E7F):
            errors.append(f"[{pool_type}] Non-Thai char '{c}' (U+{cp:04X}) in '{prefix}'")
        if cp < 128:
            errors.append(f"[{pool_type}] ASCII char '{c}' (U+{cp:04X}) in '{prefix}'")
            
    if title in seen:
        errors.append(f"[{pool_type}] Duplicate title: '{title}'")
    seen.add(title)
    
    if title in existing_tl_names:
        errors.append(f"[{pool_type}] Collision with existing timeline: '{title}'")

    if pool_type == "PRIMARY":
        validation_details.append({
            "id": item["id"],
            "title": title,
            "thai_prefix": prefix,
            "game_tag": game_tag,
            "prefix_length": len(prefix),
            "codepoints_sample": char_codepoints[:5],
            "pure_thai": True,
            "regex_valid": True,
            "source_file": item["file"],
            "status": "PASS"
        })

print(f"Validation of {len(all_titles_to_check)} titles completed with {len(errors)} errors.")
if errors:
    for e in errors:
        print(" ", e)
    sys.exit(1)

# Dump full catalog JSON
catalog = {
    "summary": {
        "total_source_files": len(FILE_MAPPING),
        "untouched_files": len([f for f in FILE_MAPPING if f["status"] == "UNTOUCHED"]),
        "processed_files": len([f for f in FILE_MAPPING if f["status"] == "PROCESSED"]),
        "existing_timelines": len(existing_tl_names),
        "primary_60_titles_count": len(PRIMARY_60_TITLES),
        "reserve_titles_count": len(RESERVE_TITLES),
        "total_validated_titles": len(all_titles_to_check),
        "regex_format": r"^([\u0E00-\u0E7F]+)_([A-Za-z0-9]+)-vdo$",
        "pure_thai_unicode_block": r"U+0E00 - U+0E7F",
        "ascii_characters_in_thai_part": 0,
        "collision_count": 0
    },
    "file_mapping": FILE_MAPPING,
    "primary_60_titles": PRIMARY_60_TITLES,
    "reserve_titles": RESERVE_TITLES,
    "validation_details": validation_details
}

out_path = r"C:\Users\warit\Desktop\agent-edite-davinci_resolve\.agents\teamwork\explorer_survey_r4_3\highlight_titles_catalog.json"
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(catalog, f, ensure_ascii=False, indent=2)

print(f"Successfully generated {out_path} with all metadata and validation records.")
