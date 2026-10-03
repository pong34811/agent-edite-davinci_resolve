import sys
import re
import json

sys.stdout.reconfigure(encoding='utf-8')

PROPOSED_TITLES = [
    # Untouched 25 files (2 clips each = 50 clips)
    {"file": "After DnD EP.4 ตอน เมื่อไทกะนอนไม่หลับเพราะความรัก.mp4", "game": "DnD", "title": "เล่าเรื่องความรักจนนอนไม่หลับ_DnD-vdo"},
    {"file": "After DnD EP.4 ตอน เมื่อไทกะนอนไม่หลับเพราะความรัก.mp4", "game": "DnD", "title": "สารภาพความในใจสุดเขินกลางตี้_DnD-vdo"},
    {"file": "After DnD ： หลอนครั้งแรกแต่จบดาร์กขั้นสุด.mp4", "game": "DnD", "title": "เปิดประสบการณ์หลอนครั้งแรกในชีวิต_DnD-vdo"},
    {"file": "After DnD ： หลอนครั้งแรกแต่จบดาร์กขั้นสุด.mp4", "game": "DnD", "title": "ตอนจบสุดดาร์กทำเอาเหวอทั้งโต๊ะ_DnD-vdo"},
    {"file": "Free Talk - ปิดคาสิโนแล้วบอสไปทำไรต่อ.mp4", "game": "FreeTalk", "title": "ปิดคาสิโนแล้วไปหาของกินรอบดึก_FreeTalk-vdo"},
    {"file": "Free Talk - ปิดคาสิโนแล้วบอสไปทำไรต่อ.mp4", "game": "FreeTalk", "title": "บ่นเรื่องงานจนลืมเวลาพักผ่อน_FreeTalk-vdo"},
    {"file": "Free Talk ติดเกาะกับเธอ จ้างเท่าไหร่ก็ไม่ออก.mp4", "game": "FreeTalk", "title": "ถ้าต้องติดเกาะขอเลือกนอนเฉยๆดีกว่า_FreeTalk-vdo"},
    {"file": "Free Talk ติดเกาะกับเธอ จ้างเท่าไหร่ก็ไม่ออก.mp4", "game": "FreeTalk", "title": "จ้างร้อยล้านก็ไม่ยอมย้ายไปไหน_FreeTalk-vdo"},
    {"file": "Free Talk ： จีบ 10 ปี แถมฟรีหนี้ 200 ล้าน.mp4", "game": "FreeTalk", "title": "บทเรียนชีวิตจีบสิบปีแต่มีหนี้แถมมา_FreeTalk-vdo"},
    {"file": "Free Talk ： จีบ 10 ปี แถมฟรีหนี้ 200 ล้าน.mp4", "game": "FreeTalk", "title": "เตือนสติคนดูเรื่องความรักสุดพัง_FreeTalk-vdo"},
    {"file": "Free Talk ：สอนไทกะเป็นโจรสลัดที.mp4", "game": "FreeTalk", "title": "ฝึกเป็นกัปตันเรือแต่โดนลูกเรือแซว_FreeTalk-vdo"},
    {"file": "Free Talk ：สอนไทกะเป็นโจรสลัดที.mp4", "game": "FreeTalk", "title": "แผนการออกทะเลล่าขุมทรัพย์สุดเพี้ยน_FreeTalk-vdo"},
    {"file": "Free Talk ：เมื่อได้เป็นตัวโดนประจำตี้.mp4", "game": "FreeTalk", "title": "ตัดพ้อชีวิตทำไมต้องเป็นตัวโดนตลอด_FreeTalk-vdo"},
    {"file": "Free Talk ：เมื่อได้เป็นตัวโดนประจำตี้.mp4", "game": "FreeTalk", "title": "โดนเพื่อนรุมแกงจนแทบอยากปิดไมค์_FreeTalk-vdo"},
    {"file": "Free Talk ：เมื่อไทกะเล่น เกย์กับชายใน DnD โดยไม่รู้ตัว.mp4", "game": "FreeTalk", "title": "สับสนบทบาทจนเพื่อนต้องสะกิดเตือน_FreeTalk-vdo"},
    {"file": "Free Talk ：เมื่อไทกะเล่น เกย์กับชายใน DnD โดยไม่รู้ตัว.mp4", "game": "FreeTalk", "title": "เผลอสร้างตำนานคู่จิ้นกลางวงสนทนา_FreeTalk-vdo"},
    {"file": "Free Talk： ลูกน้องไม่ตอบก็จะคุย!.mp4", "game": "FreeTalk", "title": "เรียกชื่อลูกน้องรัวๆจนต้องยอมเปิดไมค์_FreeTalk-vdo"},
    {"file": "Free Talk： ลูกน้องไม่ตอบก็จะคุย!.mp4", "game": "FreeTalk", "title": "บ่นน้อยใจลูกน้องแกล้งทำเป็นไม่ได้ยิน_FreeTalk-vdo"},
    {"file": "IB - สำรวจโลกภาพวาด P2 @caramellatte710.mp4", "game": "Ib", "title": "กรี๊ดลั่นหอศิลป์เมื่อเจอรูปปั้นขยับได้_Ib-vdo"},
    {"file": "IB - สำรวจโลกภาพวาด P2 @caramellatte710.mp4", "game": "Ib", "title": "พากันวิ่งหนีผีเสื้อยักษ์เกือบไม่รอด_Ib-vdo"},
    {"file": "MEET BOSS ： บอสเราเจอผู้หญิงไม่ได้เลย.mp4", "game": "FreeTalk", "title": "อาการเสียอาการเมื่อต้องคุยกับสาวสวย_FreeTalk-vdo"},
    {"file": "MEET BOSS ： บอสเราเจอผู้หญิงไม่ได้เลย.mp4", "game": "FreeTalk", "title": "โดนแซวเรื่องแพ้ทางผู้หญิงจนหน้าแดง_FreeTalk-vdo"},
    {"file": "R.E.P.O @Luche_Sinclair @Kungphaokung @RahhatemPSM @Salika_SaharasCh.mp4", "game": "REPO", "title": "โดนตัวประหลาดลากเข้าเงามืดต่อหน้าเพื่อน_REPO-vdo"},
    {"file": "R.E.P.O @Luche_Sinclair @Kungphaokung @RahhatemPSM @Salika_SaharasCh.mp4", "game": "REPO", "title": "จังหวะขโมยของหนีออกจากประตูลับ_REPO-vdo"},
    {"file": "R.E.P.O @ballkarozumar1238 @F4RC14  @momomewmoi @Mikhail_Cerise.mp4", "game": "REPO", "title": "เสียงฝีเท้าปริศนาทำเอาสะดุ้งทั้งตี้_REPO-vdo"},
    {"file": "R.E.P.O @ballkarozumar1238 @F4RC14  @momomewmoi @Mikhail_Cerise.mp4", "game": "REPO", "title": "ตะโกนเตือนเพื่อนแต่โดนทิ้งไว้ข้างหลัง_REPO-vdo"},
    {"file": "R.E.P.O @ballkarozumar1238 @F4RC14  @momomewmoi @mitsuki_mayu@NANOZEROO.mp4", "game": "REPO", "title": "เดินตกหลุมกับดักเพราะมัวแต่มองของ_REPO-vdo"},
    {"file": "R.E.P.O @ballkarozumar1238 @F4RC14  @momomewmoi @mitsuki_mayu@NANOZEROO.mp4", "game": "REPO", "title": "แบกของหนักวิ่งหนีตายวินาทีสุดท้าย_REPO-vdo"},
    {"file": "ฉลอง 800 ซับ! วงล้อเสี่ยงท้าย!!.mp4", "game": "FreeTalk", "title": "หมุนวงล้อเสี่ยงทายเจอแต่บทลงโทษสุดกาว_FreeTalk-vdo"},
    {"file": "ฉลอง 800 ซับ! วงล้อเสี่ยงท้าย!!.mp4", "game": "FreeTalk", "title": "กราบขอบคุณคนดูที่ร่วมเดินทางมาด้วยกัน_FreeTalk-vdo"},
    {"file": "บอสทำไรตอนตี 2？？.mp4", "game": "FreeTalk", "title": "เผยพฤติกรรมสุดแปลกตอนดึกสงัด_FreeTalk-vdo"},
    {"file": "บอสทำไรตอนตี 2？？.mp4", "game": "FreeTalk", "title": "นั่งคุยคนเดียวตอนตีสองจนรู้สึกวังเวง_FreeTalk-vdo"},
    {"file": "ฝึกเล่น LoL.mp4", "game": "LoL", "title": "กดสกิลวืดกลางเลนจนโดนป้อมยิงตาย_LoL-vdo"},
    {"file": "ฝึกเล่น LoL.mp4", "game": "LoL", "title": "จังหวะไฟต์ชุลมุนกดมั่วจนได้คิลเฉย_LoL-vdo"},
    {"file": "รายการ ： Q&A คุยกับนกแก้ว.mp4", "game": "FreeTalk", "title": "ตอบคำถามแฟนคลับเรื่องอาหารจานโปรด_FreeTalk-vdo"},
    {"file": "รายการ ： Q&A คุยกับนกแก้ว.mp4", "game": "FreeTalk", "title": "นกแก้วพูดแทรกจังหวะสำคัญจนหลุดขำ_FreeTalk-vdo"},
    {"file": "สอนไทกะเล่น LoL ที.mp4", "game": "LoL", "title": "โดนโค้ชบ่นเรื่องลืมซื้อของตอนเริ่มเกม_LoL-vdo"},
    {"file": "สอนไทกะเล่น LoL ที.mp4", "game": "LoL", "title": "จังหวะลาสบอสใหญ่ขโมยมังกรสุดเทพ_LoL-vdo"},
    {"file": "เสืออยากคุย [VqELVP2u2oU].mp4", "game": "FreeTalk", "title": "เล่าเรื่องวัยเด็กสุดแสบที่ไม่มีใครเคยรู้_FreeTalk-vdo"},
    {"file": "เสืออยากคุย [VqELVP2u2oU].mp4", "game": "FreeTalk", "title": "ร้องเพลงเพี้ยนแต่ใส่อารมณ์เกินร้อย_FreeTalk-vdo"},
    {"file": "เสืออยากคุย [ns0I3EihIUI].mp4", "game": "FreeTalk", "title": "ถกประเด็นของกินข้างทางที่อร่อยที่สุด_FreeTalk-vdo"},
    {"file": "เสืออยากคุย [ns0I3EihIUI].mp4", "game": "FreeTalk", "title": "จังหวะจามเสียงดังจนกล้องสั่น_FreeTalk-vdo"},
    {"file": "เสืออยากคุย [qZVnCXIjfzo].mp4", "game": "FreeTalk", "title": "แชร์ประสบการณ์นอนดึกจนตาเป็นหมีแพนด้า_FreeTalk-vdo"},
    {"file": "เสืออยากคุย [qZVnCXIjfzo].mp4", "game": "FreeTalk", "title": "อ่านแชทคอมเมนต์กวนๆแล้วหลุดขำก๊าก_FreeTalk-vdo"},
    {"file": "ใช้ชีวิตไปกับไทกะ 101 (ไม่ชินกล้องเลย).mp4", "game": "FreeTalk", "title": "เขินกล้องจนทำตัวไม่ถูกในไลฟ์แรกๆ_FreeTalk-vdo"},
    {"file": "ใช้ชีวิตไปกับไทกะ 101 (ไม่ชินกล้องเลย).mp4", "game": "FreeTalk", "title": "สอนวิธีปรับตัวเมื่อต้องเจอกับคนแปลกหน้า_FreeTalk-vdo"},
    {"file": "ไลฟ์คุยไปเรื่อยแบบเสือขี้เบื่อ.mp4", "game": "FreeTalk", "title": "บ่นความเหงาในวันฝนตกชวนง่วงนอน_FreeTalk-vdo"},
    {"file": "ไลฟ์คุยไปเรื่อยแบบเสือขี้เบื่อ.mp4", "game": "FreeTalk", "title": "เล่นมุกแป้กแต่หัวเราะแก้เขินคนเดียว_FreeTalk-vdo"},
    {"file": "ไลฟ์นี้จะเล่น Fallout 4 Nuka-world P1.mp4", "game": "Fallout4", "title": "เจอกับดักระเบิดตู้มเดียวบินขึ้นฟ้า_Fallout4-vdo"},
    {"file": "ไลฟ์นี้จะเล่น Fallout 4 Nuka-world P1.mp4", "game": "Fallout4", "title": "สู้สัตว์ประหลาดในสวนสนุกจนกระสุนหมดเกลี้ยง_Fallout4-vdo"},

    # 10 Peak Highlights across high-action footage (Clips 51 to 60)
    {"file": "Collab R.E.P.O - เก็บของไว้ให้ไกลเสือ.mp4", "game": "REPO", "title": "เสียงกรีดร้องสะท้อนทางเดินใต้ดินสุดหลอน_REPO-vdo"},
    {"file": "ปืนเขาที่เราหมดแรง @KRATOI_26  @Mixzy21PM  @Pleiades_Frontier.mp4", "game": "Climbing", "title": "เชือกตึงเปรี๊ยะห้อยต่องแต่งกลางสายหมอก_Climbing-vdo"},
    {"file": "IB - สำรวจโลกภาพวาด P1.mp4", "game": "Ib", "title": "สะดุ้งตัวโยนเลือดหยดใส่หน้าภาพวาด_Ib-vdo"},
    {"file": "After DnD ： เมื่อบาร์ดด่าจนมังกรตาย!.mp4", "game": "DnD", "title": "รวมพลังด่ามังกรจนบอสสิ้นใจคาที่_DnD-vdo"},
    {"file": "Gartic phone - ไทกะสกิลวาดรูป 999999.mp4", "game": "GarticPhone", "title": "ทายคำตอบผิดจนเนื้อเรื่องออกทะเล_GarticPhone-vdo"},
    {"file": "Free Talk ： หยุดเสือด้วยมือเปล่า？？.mp4", "game": "FreeTalk", "title": "สอนวิชาป้องกันตัวด้วยกำปั้นเปล่าสุดฮา_FreeTalk-vdo"},
    {"file": "เมื่อไทกะคือความชิบหายในครัว!.mp4", "game": "Overcooked", "title": "โยนวัตถุดิบข้ามฝั่งชนหัวเพื่อนเต็มๆ_Overcooked-vdo"},
    {"file": "ไลฟ์นี้จะเล่น Fallout 4 Nuka-world P1.mp4", "game": "Fallout4", "title": "หลงทางในแดนรกร้างเดินวนอยู่ที่เดิม_Fallout4-vdo"},
    {"file": "สอนไทกะเล่น LoL ที.mp4", "game": "LoL", "title": "จังหวะโดนดักซุ่มพุ่มไม้ร้องเสียงหลง_LoL-vdo"},
    {"file": "R.E.P.O @Luche_Sinclair @Kungphaokung @RahhatemPSM @Salika_SaharasCh.mp4", "game": "REPO", "title": "เพื่อนโดนงาบต่อหน้าต่อตาช่วยไม่ทัน_REPO-vdo"}
]

# Existing 28 timelines from current state
with open('.agents/teamwork/explorer_survey_r4_3/current_state.json', encoding='utf-8') as f:
    state = json.load(f)
existing_tl_names = set(tl['name'] for tl in state['timelines'])

print(f"Loaded {len(existing_tl_names)} existing timeline names from project tygarina_2026-09-30.")
print(f"Testing {len(PROPOSED_TITLES)} proposed highlight titles...")

NAMING_REGEX = re.compile(r"^([\u0E00-\u0E7F]+)_([A-Za-z0-9]+)-vdo$")

errors = []
seen_titles = set()

for idx, item in enumerate(PROPOSED_TITLES, 1):
    title = item["title"]
    file = item["file"]
    expected_game = item["game"]

    # 1. Regex match
    m = NAMING_REGEX.match(title)
    if not m:
        errors.append(f"#{idx:02d}: Regex match failed for '{title}'")
        continue

    thai_prefix, game_tag = m.groups()

    # 2. Game tag check
    if game_tag != expected_game:
        errors.append(f"#{idx:02d}: Game tag mismatch '{game_tag}' != '{expected_game}'")

    # 3. Unicode codepoints check for Thai prefix
    for c in thai_prefix:
        cp = ord(c)
        if not (0x0E00 <= cp <= 0x0E7F):
            errors.append(f"#{idx:02d}: Non-Thai char U+{cp:04X} ('{c}') in prefix '{thai_prefix}'")
        if cp < 128:
            errors.append(f"#{idx:02d}: ASCII char U+{cp:04X} ('{c}') in prefix '{thai_prefix}'")

    # 4. Suffix check
    if not title.endswith("-vdo"):
        errors.append(f"#{idx:02d}: Does not end with '-vdo' in '{title}'")

    # 5. Internal Uniqueness
    if title in seen_titles:
        errors.append(f"#{idx:02d}: Duplicate proposed title '{title}'")
    seen_titles.add(title)

    # 6. Uniqueness against 28 existing timelines
    if title in existing_tl_names:
        errors.append(f"#{idx:02d}: Collision with existing timeline '{title}'")

print("\n--- Validation Summary ---")
print(f"Total Proposed: {len(PROPOSED_TITLES)}")
print(f"Unique Titles:  {len(seen_titles)}")
print(f"Total Errors:   {len(errors)}")

if errors:
    print("\nFAILED VALIDATION:")
    for e in errors:
        print(f"  ERROR: {e}")
    sys.exit(1)
else:
    print("\nSUCCESS: 100% OF ALL 60 PROPOSED TITLES PASSED STRICT VALIDATION!")
    print("  - 100% Pure Thai Unicode [\\u0E00-\\u0E7F] (ZERO English/Latin, ZERO control chars)")
    print("  - Exactly matching regex ^([\\u0E00-\\u0E7F]+)_([A-Za-z0-9]+)-vdo$")
    print("  - Zero collisions with all 28 existing timelines")
    print("  - Zero internal duplicates (all 60 titles unique)")
