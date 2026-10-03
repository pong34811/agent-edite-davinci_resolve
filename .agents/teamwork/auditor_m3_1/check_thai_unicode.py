import sys
import unicodedata

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

names = [
    'วิ่งหนีปีศาจแทบไม่ทัน_REPO-vdo',
    'จังหวะเอาชีวิตรอดเฉียดฉิว_REPO-vdo',
    'เปิดตี้แจกความฮากับเพื่อน_REPO-vdo',
    'เหลือสองชีวิตเกาะหน้าผาไว้_Climbing-vdo',
    'จังหวะกระโดดข้ามหุบเหวสุดเสียว_Climbing-vdo',
    'แกล้งเพื่อนตั้งแต่จุดสตาร์ท_Climbing-vdo',
    'เจอตัวละครใหม่ตกใจจนร้องลั่น_Ib-vdo',
    'ประตูมิติชวนขนหัวลุก_Ib-vdo',
    'ไขปริศนาภาพวาดมรณะ_Ib-vdo',
    'เล่าวินาทีบอสแพ้แบบอนาถ_DnD-vdo',
    'ฉากโรลเพลย์สุดกาวในห้องน้ำ_DnD-vdo',
    'ทอยเต๋าพลาดจนแผนพังยับ_DnD-vdo',
    'เฉลยภาพวาดจนเพื่อนอึ้งทั้งห้อง_GarticPhone-vdo',
    'ลืมปิดไมค์วาดรูปไฟลนก้น_GarticPhone-vdo',
    'วาดรูปเพี้ยนจนกลายเป็นมีม_GarticPhone-vdo',
    'ตอบแชทเรื่องสู้เสือด้วยมือเปล่า_FreeTalk-vdo',
    'จำลองเหตุการณ์ถ้าเจอเสือของจริง_FreeTalk-vdo',
    'อ่านคอมเมนต์สุดกาวขำจนตัวโยก_FreeTalk-vdo',
    'เปิดครัววันแรกก็วุ่นวายซะแล้ว_Overcooked-vdo',
    'ออเดอร์ล้นครัวสั่งความวิกฤต_Overcooked-vdo',
    'จานตกน้ำหมดครัวนาทีสุดท้าย_Overcooked-vdo'
]

print("Verifying 21 Timeline Thai prefixes character by character:")
all_passed = True
for idx, name in enumerate(names, 1):
    parts = name.split('_')
    thai_part = parts[0]
    game_and_suffix = '_'.join(parts[1:])
    
    # Check ASCII
    ascii_chars = [c for c in thai_part if ord(c) < 128]
    # Check Thai block: 0x0E00 to 0x0E7F
    non_thai_block = [c for c in thai_part if not (0x0E00 <= ord(c) <= 0x0E7F)]
    
    print(f"#{idx:02d}: '{thai_part}' (len={len(thai_part)})")
    if ascii_chars:
        print(f"  [FAIL] Contains ASCII characters: {ascii_chars}")
        all_passed = False
    if non_thai_block:
        print(f"  [FAIL] Contains non-Thai Unicode characters: {non_thai_block}")
        all_passed = False
    if not ascii_chars and not non_thai_block:
        print(f"  [PASS] 100% pure Thai Unicode characters.")

if all_passed:
    print("\nALL 21 THAI PREFIXES CONFIRMED STRICTLY PURE THAI (0 ASCII CHARACTERS)!")
else:
    print("\nVIOLATION DETECTED!")
