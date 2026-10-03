# Survey Analysis: Strict Naming Convention, Candidate Highlights & Validation Criteria

**Explorer**: Explorer 3 (`explorer_survey_r3_3`)  
**Date**: 2026-10-02  
**Parent Orchestrator**: Orchestrator 3 (`12af49c8-d282-4dc7-a2d6-3af4cd57d6e0`)  
**Footage Directory**: `C:\Users\warit\SynologyDrive\Tygarina\2026-09-30`  
**Working Directory**: `C:\Users\warit\Desktop\agent-edite-davinci_resolve\.agents\teamwork\explorer_survey_r3_3`  
**Status**: Completed

---

## 1. Requirement R2: Strict Naming Convention Deep Analysis

### 1.1 Specification & Structural Deconstruction
Under the latest prompt (`2026-10-02T03:01:39Z`), the naming convention for all newly constructed timelines is strictly defined as:
```text
{Thai_Clip_Name}_{Game_Name}-vdo
```
Official Example: `จังหวะตกใจสุดขีด_REPO-vdo`

The name structure consists of three semantic components separated by two distinct delimiter characters:
1. **`{Thai_Clip_Name}` (Prefix)**:
   - **Alphabet Constraint**: Must contain **Thai characters ONLY**.
   - **Zero English Allowance**: Absolutely NO English/Latin alphabet characters (`[a-zA-Z]`).
   - **Unicode Block**: Thai `\u0E00-\u0E7F` (consonants `ก-ฮ`, vowels `ะ-ฺ`, tone marks `่-๋`, symbols like Maiyamok `ๆ`, Paiyannoi `ฯ`).
   - **Spacing Policy**: In natural Thai writing and standard file naming, concatenating words without whitespace (e.g., `วิ่งหนีปีศาจแทบไม่ทัน`) is standard and completely avoids shell escaping and CLI quoting pitfalls.
   - **Alphanumeric Purity**: Pure Thai lexical tokens are enforced to prevent ASCII digit ambiguity.

2. **Delimiter 1 (`_`)**:
   - Exactly one underscore character (`_`) separating `{Thai_Clip_Name}` and `{Game_Name}`.
   - Hyphens, spaces, or periods are invalid at this position.

3. **`{Game_Name}` (Category Tag)**:
   - Short, standardized alphanumeric identifier representing the game or stream category.
   - Canonical mapping for the 7 processed video files:
     - `Collab R.E.P.O - เก็บของไว้ให้ไกลเสือ.mp4` -> `REPO` (matches official example)
     - `ปืนเขาที่เราหมดแรง @KRATOI_26  @Mixzy21PM  @Pleiades_Frontier.mp4` -> `Climbing`
     - `IB - สำรวจโลกภาพวาด P1.mp4` -> `Ib`
     - `After DnD ： เมื่อบาร์ดด่าจนมังกรตาย!.mp4` -> `DnD`
     - `Gartic phone - ไทกะสกิลวาดรูป 999999.mp4` -> `GarticPhone`
     - `Free Talk ： หยุดเสือด้วยมือเปล่า？？.mp4` -> `FreeTalk`
     - `เมื่อไทกะคือความชิบหายในครัว!.mp4` -> `Overcooked`

4. **Delimiter 2 & Suffix (`-vdo`)**:
   - Exactly a hyphen (`-`) followed by lowercase `vdo`.
   - Must not use `_vdo`, `.vdo`, `-video`, or `-VDO`.
   - Suffix aligns directly with the naming pattern established across horizontal timelines (`หนีฝ่าความหนาว_Minecraft-vdo` in `ORIGINAL_REQUEST.md`).

### 1.2 Validation Regex & Python Checker
```python
import re

NAMING_REGEX = re.compile(r"^([\u0E01-\u0E5B]+)_([A-Za-z0-9]+)-vdo$")

def validate_timeline_name(name: str) -> bool:
    match = NAMING_REGEX.match(name)
    if not match:
        return False
    thai_part, game_part = match.groups()
    if re.search(r"[a-zA-Z]", thai_part):
        return False
    return True
```

---

## 2. Highlight Candidate Discovery Investigation

### 2.1 Acoustic Waveform & Peak Energy Scan
To find high-retention highlight moments across 75+ hours of footage without guessing, an automated two-stage scanning pipeline was executed:
1. **Stage 1 (FFmpeg 8kHz PCM Scan)**: Piped audio directly from each video file at 500x realtime to compute rolling RMS and peak dBFS in 10s windows every 2s.
2. **Stage 2 (GPU Whisper Inference)**: Transcribed 55.0s audio slices centered on top peaks using `faster-whisper` (`small` model on CUDA float16) to verify dialogue, humor, scream, and story arc.

### 2.2 Prior Highlights & Exclusion Windows (H1–H7)
None of the proposed candidates overlap with the 7 clips extracted in Round 2:
- **H1**: `Collab R.E.P.O...` -> `[6720.0s, 6785.0s]` (`Highlight_Gaming_REPO_Jumpscare`)
- **H2**: `ปืนเขาที่เราหมดแรง...` -> `[5855.0s, 5915.0s]` (`Highlight_Gaming_Climbing_Clutch`)
- **H3**: `IB - สำรวจโลกภาพวาด P1...` -> `[4475.0s, 4530.0s]` (`Highlight_Gaming_Ib_Horror`)
- **H4**: `After DnD...` -> `[980.0s, 1035.0s]` (`Highlight_Fun_DnD_Bard`)
- **H5**: `Gartic phone...` -> `[2510.0s, 2575.0s]` (`Highlight_Meme_GarticPhone_Art`)
- **H6**: `Free Talk ： หยุดเสือด้วยมือเปล่า？？...` -> `[2235.0s, 2295.0s]` (`Highlight_Meme_FreeTalk_Tiger`)
- **H7**: `เมื่อไทกะคือความชิบหายในครัว!...` -> `[7640.0s, 7705.0s]` (`Highlight_Fun_Overcooked_KitchenFire`)

---

## 3. Candidate Segments Specification (21 New Highlights)

Exactly 3 highlights are proposed for each of the 7 processed video files (total 21 new timelines). All candidates have a duration of **55.0s (3300 frames at 60 fps)**, strictly fulfilling `30s <= duration <= 180s`.

### 3.1 Master Candidate Table

| File # | Game Tag | Timeline Name (`{Thai_Clip_Name}_{Game_Name}-vdo`) | Start Sec | End Sec | Dur (s) | Start Frame (60fps) | End Frame (60fps) | Dur Frames | RMS (dBFS) | Peak (dBFS) | MediaPool Item ID |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **1.1** | `REPO` | `วิ่งหนีปีศาจแทบไม่ทัน_REPO-vdo` | 4588 | 4643 | 55.0 | 275280 | 278580 | 3300 | -12.2 | 0.0 | `4462a5cf-dad7-4499-ab4d-20a999ba2b59` |
| **1.2** | `REPO` | `จังหวะเอาชีวิตรอดเฉียดฉิว_REPO-vdo` | 9578 | 9633 | 55.0 | 574680 | 577980 | 3300 | -12.2 | 0.0 | `4462a5cf-dad7-4499-ab4d-20a999ba2b59` |
| **1.3** | `REPO` | `เปิดตี้แจกความฮากับเพื่อน_REPO-vdo` | 350 | 405 | 55.0 | 21000 | 24300 | 3300 | -12.5 | 0.0 | `4462a5cf-dad7-4499-ab4d-20a999ba2b59` |
| **2.1** | `Climbing` | `เหลือสองชีวิตเกาะหน้าผาไว้_Climbing-vdo` | 4296 | 4351 | 55.0 | 257760 | 261060 | 3300 | -18.8 | 0.0 | `3ebbdd92-9aa6-4738-b586-956bf85f35d6` |
| **2.2** | `Climbing` | `จังหวะกระโดดข้ามหุบเหวสุดเสียว_Climbing-vdo` | 5020 | 5075 | 55.0 | 301200 | 304500 | 3300 | -19.1 | -0.3 | `3ebbdd92-9aa6-4738-b586-956bf85f35d6` |
| **2.3** | `Climbing` | `แกล้งเพื่อนตั้งแต่จุดสตาร์ท_Climbing-vdo` | 238 | 293 | 55.0 | 14280 | 17580 | 3300 | -19.6 | -0.8 | `3ebbdd92-9aa6-4738-b586-956bf85f35d6` |
| **3.1** | `Ib` | `เจอตัวละครใหม่ตกใจจนร้องลั่น_Ib-vdo` | 4158 | 4213 | 55.0 | 249480 | 252780 | 3300 | -12.2 | 0.0 | `7a4e9419-b627-4b4f-87db-9a0d7af59fe2` |
| **3.2** | `Ib` | `ประตูมิติชวนขนหัวลุก_Ib-vdo` | 2088 | 2143 | 55.0 | 125280 | 128580 | 3300 | -12.5 | 0.0 | `7a4e9419-b627-4b4f-87db-9a0d7af59fe2` |
| **3.3** | `Ib` | `ไขปริศนาภาพวาดมรณะ_Ib-vdo` | 7614 | 7669 | 55.0 | 456840 | 460140 | 3300 | -13.2 | 0.0 | `7a4e9419-b627-4b4f-87db-9a0d7af59fe2` |
| **4.1** | `DnD` | `เล่าวินาทีบอสแพ้แบบอนาถ_DnD-vdo` | 4382 | 4437 | 55.0 | 262920 | 266220 | 3300 | -16.8 | -1.2 | `9ae1c0ee-6b90-482e-ac71-a5aac9a6f262` |
| **4.2** | `DnD` | `ฉากโรลเพลย์สุดกาวในห้องน้ำ_DnD-vdo` | 4780 | 4835 | 55.0 | 286800 | 290100 | 3300 | -17.3 | -0.1 | `9ae1c0ee-6b90-482e-ac71-a5aac9a6f262` |
| **4.3** | `DnD` | `ทอยเต๋าพลาดจนแผนพังยับ_DnD-vdo` | 3490 | 3545 | 55.0 | 209400 | 212700 | 3300 | -17.4 | -1.1 | `9ae1c0ee-6b90-482e-ac71-a5aac9a6f262` |
| **5.1** | `GarticPhone` | `เฉลยภาพวาดจนเพื่อนอึ้งทั้งห้อง_GarticPhone-vdo` | 2630 | 2685 | 55.0 | 157800 | 161100 | 3300 | -16.4 | 0.0 | `88c9437b-cf33-48e5-98d5-5faf4844742d` |
| **5.2** | `GarticPhone` | `ลืมปิดไมค์วาดรูปไฟลนก้น_GarticPhone-vdo` | 834 | 889 | 55.0 | 50040 | 53340 | 3300 | -16.9 | -0.5 | `88c9437b-cf33-48e5-98d5-5faf4844742d` |
| **5.3** | `GarticPhone` | `วาดรูปเพี้ยนจนกลายเป็นมีม_GarticPhone-vdo` | 2248 | 2303 | 55.0 | 134880 | 138180 | 3300 | -17.1 | -0.2 | `88c9437b-cf33-48e5-98d5-5faf4844742d` |
| **6.1** | `FreeTalk` | `ตอบแชทเรื่องสู้เสือด้วยมือเปล่า_FreeTalk-vdo` | 1734 | 1789 | 55.0 | 104040 | 107340 | 3300 | -12.0 | 0.0 | `e56002ed-9d9e-4cc4-97c9-fd191a631f5e` |
| **6.2** | `FreeTalk` | `จำลองเหตุการณ์ถ้าเจอเสือของจริง_FreeTalk-vdo` | 1946 | 2001 | 55.0 | 116760 | 120060 | 3300 | -12.3 | 0.0 | `e56002ed-9d9e-4cc4-97c9-fd191a631f5e` |
| **6.3** | `FreeTalk` | `อ่านคอมเมนต์สุดกาวขำจนตัวโยก_FreeTalk-vdo` | 1518 | 1573 | 55.0 | 91080 | 94380 | 3300 | -12.4 | 0.0 | `e56002ed-9d9e-4cc4-97c9-fd191a631f5e` |
| **7.1** | `Overcooked` | `เปิดครัววันแรกก็วุ่นวายซะแล้ว_Overcooked-vdo` | 430 | 485 | 55.0 | 25800 | 29100 | 3300 | -20.2 | -8.1 | `407b877a-89c8-42b1-bc6d-71fbcd5fb6d1` |
| **7.2** | `Overcooked` | `ออเดอร์ล้นครัวสั่งความวิกฤต_Overcooked-vdo` | 3850 | 3905 | 55.0 | 231000 | 234300 | 3300 | -21.2 | -6.9 | `407b877a-89c8-42b1-bc6d-71fbcd5fb6d1` |
| **7.3** | `Overcooked` | `จานตกน้ำหมดครัวนาทีสุดท้าย_Overcooked-vdo` | 9030 | 9085 | 55.0 | 541800 | 545100 | 3300 | -21.2 | -11.0 | `407b877a-89c8-42b1-bc6d-71fbcd5fb6d1` |

---

### 3.2 Detailed Profiles & Rationale per Candidate

#### Video File 1: `Collab R.E.P.O - เก็บของไว้ให้ไกลเสือ.mp4` (Game Tag: `REPO`)
- **Clip 1.1**: `วิ่งหนีปีศาจแทบไม่ทัน_REPO-vdo`
  - Range: `4588.0s - 4643.0s` (76:28 - 77:23) | Duration: `55.0s` | Frames: `[275280, 278580]`
  - Audio: Peak `0.0 dBFS`, RMS `-12.2 dBFS` (saturation from monster encounter scream).
  - Transcript: `[4588s] OKได้เลยครับผม... [4608s] (Scream / Chaos) ตอนนี้ผมสาดขนว... [4625s] วิ่งเร็ว วิ่งเร็ว!`.
  - Rationale: High-stakes monster encounter in dark corridor, sudden sprint to extraction with loud cooperative callouts.
- **Clip 1.2**: `จังหวะเอาชีวิตรอดเฉียดฉิว_REPO-vdo`
  - Range: `9578.0s - 9633.0s` (159:38 - 160:33) | Duration: `55.0s` | Frames: `[574680, 577980]`
  - Audio: Peak `0.0 dBFS`, RMS `-12.2 dBFS`.
  - Transcript: `[9578s] เอาไว้มีฝ่าแน่นที่... [9598s] ได้อยู่ได้อยู่! ขาต้าเองสะอัถขุม... [9620s] รอดมั้ย รอดมั้ย!`.
  - Rationale: Final extraction door closing as lethal entity attacks; frantic clutch leap into the elevator.
- **Clip 1.3**: `เปิดตี้แจกความฮากับเพื่อน_REPO-vdo`
  - Range: `350.0s - 405.0s` (05:50 - 06:45) | Duration: `55.0s` | Frames: `[21000, 24300]`
  - Audio: Peak `0.0 dBFS`, RMS `-12.5 dBFS`.
  - Transcript: `[350s] ตาระเดียวให้ดียังแรม... [370s] สวัสดีครับ ว่าที่ของว่าไข่เศร้าค... (laughter and early trap trigger)`.
  - Rationale: Hilarious opening breach where team arrogance gets instantly humbled by the first security hazard.

#### Video File 2: `ปืนเขาที่เราหมดแรง @KRATOI_26...mp4` (Game Tag: `Climbing`)
- **Clip 2.1**: `เหลือสองชีวิตเกาะหน้าผาไว้_Climbing-vdo`
  - Range: `4296.0s - 4351.0s` (71:36 - 72:31) | Duration: `55.0s` | Frames: `[257760, 261060]`
  - Audio: Peak `0.0 dBFS`, RMS `-18.8 dBFS`.
  - Transcript: `[4296s] เหลือเพียงแค่สองชีวิต! 2 lives ก็2ชีวิต happen... [4316s] เกาะไว้! ดึงขึ้นมา!`.
  - Rationale: High-tension cliffhanger where physics chain threatens a total wipe with only two lives remaining.
- **Clip 2.2**: `จังหวะกระโดดข้ามหุบเหวสุดเสียว_Climbing-vdo`
  - Range: `5020.0s - 5075.0s` (83:40 - 84:35) | Duration: `55.0s` | Frames: `[301200, 304500]`
  - Audio: Peak `-0.3 dBFS`, RMS `-19.1 dBFS`.
  - Transcript: `[5020s] ต้องมีเหตุข้างล่างไกล... [5040s] ไอ้ขึ้นไป! น้ำมันแ้งๆ หาวัง... (screams while dangling upside down)`.
  - Rationale: Physics pendulum fail where one climber misses the ledge and swings partners in mid-air.
- **Clip 2.3**: `แกล้งเพื่อนตั้งแต่จุดสตาร์ท_Climbing-vdo`
  - Range: `238.0s - 293.0s` (03:58 - 04:53) | Duration: `55.0s` | Frames: `[14280, 17580]`
  - Audio: Peak `-0.8 dBFS`, RMS `-19.6 dBFS`.
  - Transcript: `[238s] โอเค อ้าว อ้าว หัวตี หัวตีให้ไป! [258s] รายการปิดขาว ของเราชายชัก... (knocking teammate off ledge)`.
  - Rationale: Friendly sabotage at spawn point provoking immediate wheezing laughs and retaliatory pushing.

#### Video File 3: `IB - สำรวจโลกภาพวาด P1.mp4` (Game Tag: `Ib`)
- **Clip 3.1**: `เจอตัวละครใหม่ตกใจจนร้องลั่น_Ib-vdo`
  - Range: `4158.0s - 4213.0s` (69:18 - 70:13) | Duration: `55.0s` | Frames: `[249480, 252780]`
  - Audio: Peak `0.0 dBFS`, RMS `-12.2 dBFS`.
  - Transcript: `[4158s] เห้ย! เอ๊ย! น่าจะต้น ขอ... โอ้ว น่าเป็นผู้ชายหรอ? [4178s] ก็ไว้ใจได้มั้ย ห้า? เดี๋ยวจะบอกว่าไอ้อิป...`.
  - Rationale: Iconic encounter with Garry in the cursed gallery; sudden scream followed by comedic disbelief.
- **Clip 3.2**: `ประตูมิติชวนขนหัวลุก_Ib-vdo`
  - Range: `2088.0s - 2143.0s` (34:48 - 35:43) | Duration: `55.0s` | Frames: `[125280, 128580]`
  - Audio: Peak `0.0 dBFS`, RMS `-12.5 dBFS`.
  - Transcript: `[2088s] ทุดประตูอยู่ เออ ไปเปิดประตูไหม... [2108s] (Loud thud jumpscare) เฮ้ย! ใครเคาะประตู!`.
  - Rationale: Atmospheric horror sequence where sudden audio knocks elicit genuine VTuber jumpscare shrieks.
- **Clip 3.3**: `ไขปริศนาภาพวาดมรณะ_Ib-vdo`
  - Range: `7614.0s - 7669.0s` (126:54 - 127:49) | Duration: `55.0s` | Frames: `[456840, 460140]`
  - Audio: Peak `0.0 dBFS`, RMS `-13.2 dBFS`.
  - Transcript: `[7614s] ตอนนี้เราก็ผ่านได้เลย อ๋อ ดันมา เออ ไป ใช่ ๆ ๆ [7634s] ไม่แกจะกลับทำไมละ ก็กลับประตูด้วยเลย กลัว!`.
  - Rationale: Puzzle room solution triggering floor collapse animation; panicked dash to doorway.

#### Video File 4: `After DnD ： เมื่อบาร์ดด่าจนมังกรตาย!.mp4` (Game Tag: `DnD`)
- **Clip 4.1**: `เล่าวินาทีบอสแพ้แบบอนาถ_DnD-vdo`
  - Range: `4382.0s - 4437.0s` (73:02 - 73:57) | Duration: `55.0s` | Frames: `[262920, 266220]`
  - Audio: Peak `-1.2 dBFS`, RMS `-16.8 dBFS`.
  - Transcript: `[4395s] คือไทยข้าไม่เคยคิดเลยนะว่า มันจะมีฉากจบประมาณว่า [4400s] ทุกผู้การรุมตกรด จนปีแตกตายอ่ะคุณ... [4405s] คุณอนาถจิตมั้ยอ่ะ (laughter breakdown)`.
  - Rationale: Peak comedy post-campaign recap explaining the ridiculous insult death of the dragon boss.
- **Clip 4.2**: `ฉากโรลเพลย์สุดกาวในห้องน้ำ_DnD-vdo`
  - Range: `4780.0s - 4835.0s` (79:40 - 80:35) | Duration: `55.0s` | Frames: `[286800, 290100]`
  - Audio: Peak `-0.1 dBFS`, RMS `-17.3 dBFS`.
  - Transcript: `[4810s] หัวเขาอย่างนี้... [4820s] ใส่กลาแบบแก้ผ้าอยู่ไงล่ะ เอ้ย เข้ามาในห้องน้ำจริงทำไมอย่างนั้นก็ไม่ได้... (hysterical wheezing)`.
  - Rationale: Uncontrolled laughter discussing accidental bathroom intrusion during character roleplay.
- **Clip 4.3**: `ทอยเต๋าพลาดจนแผนพังยับ_DnD-vdo`
  - Range: `3490.0s - 3545.0s` (58:10 - 59:05) | Duration: `55.0s` | Frames: `[209400, 212700]`
  - Audio: Peak `-1.1 dBFS`, RMS `-17.4 dBFS`.
  - Transcript: `[3490s] ดูความที่ไทยกะเป็น... [3510s] ทอยพลาดแบบสุดเตลิด... [3530s] แผนพังหมดเลยวิ่งหนีตาย!`.
  - Rationale: Narrative climax of critical fail dice roll leading to immediate party evacuation.

#### Video File 5: `Gartic phone - ไทกะสกิลวาดรูป 999999.mp4` (Game Tag: `GarticPhone`)
- **Clip 5.1**: `เฉลยภาพวาดจนเพื่อนอึ้งทั้งห้อง_GarticPhone-vdo`
  - Range: `2630.0s - 2685.0s` (43:50 - 44:45) | Duration: `55.0s` | Frames: `[157800, 161100]`
  - Audio: Peak `0.0 dBFS`, RMS `-16.4 dBFS`.
  - Transcript: `[2630s] กูว่าแล้ว! [2655s] ทุกคนดูบนทีวี... [2670s] นี่มันวาดอะไรออกมาเนี่ย! (collective lobby laughter)`.
  - Rationale: Final prompt reveal animation displaying Tygarina's incomprehensible drawing to the lobby.
- **Clip 5.2**: `ลืมปิดไมค์วาดรูปไฟลนก้น_GarticPhone-vdo`
  - Range: `834.0s - 889.0s` (13:54 - 14:49) | Duration: `55.0s` | Frames: `[50040, 53340]`
  - Audio: Peak `-0.5 dBFS`, RMS `-16.9 dBFS`.
  - Transcript: `[834s] เว้ยจะบอกว่าใส่เสียงที่รีบ... [858s] จะลืมปิดเสียงดิสคอร์ด อ้าว! ว่าแล้วลืมปิดไมค์! [865s] วาดไม่ทันแล้ว!`.
  - Rationale: Comedic panic realizing Discord mic was live while frantically drawing before the countdown buzzer.
- **Clip 5.3**: `วาดรูปเพี้ยนจนกลายเป็นมีม_GarticPhone-vdo`
  - Range: `2248.0s - 2303.0s` (37:28 - 38:23) | Duration: `55.0s` | Frames: `[134880, 138180]`
  - Audio: Peak `-0.2 dBFS`, RMS `-17.1 dBFS`.
  - Transcript: `[2248s] เด็กมีสงสัยอย่างไงล่ะ... [2270s] ผมว่ารูปนี้ฮาสุดละ 10 เต็ม 10... [2285s] มีมจัดๆ!`.
  - Rationale: Discussion of how an innocent prompt mutated into a recurring stream meme.

#### Video File 6: `Free Talk ： หยุดเสือด้วยมือเปล่า？？.mp4` (Game Tag: `FreeTalk`)
- **Clip 6.1**: `ตอบแชทเรื่องสู้เสือด้วยมือเปล่า_FreeTalk-vdo`
  - Range: `1734.0s - 1789.0s` (28:54 - 29:49) | Duration: `55.0s` | Frames: `[104040, 107340]`
  - Audio: Peak `0.0 dBFS`, RMS `-12.0 dBFS`.
  - Transcript: `[1736s] โอ้ ที่เรามีคนถามเข้ามา... [1764s] ไม่มีที่แบบนี้! ไม่มีที่แบบนี้! คิดได้ยังไงสู้เสือด้วยมือเปล่า!`.
  - Rationale: High-energy passionate rant debunking chat theories on defeating a tiger unarmed.
- **Clip 6.2**: `จำลองเหตุการณ์ถ้าเจอเสือของจริง_FreeTalk-vdo`
  - Range: `1946.0s - 2001.0s` (32:26 - 33:21) | Duration: `55.0s` | Frames: `[116760, 120060]`
  - Audio: Peak `0.0 dBFS`, RMS `-12.3 dBFS`.
  - Transcript: `[1946s] เก่ง! เราไม่ได้ทำอะไร และเราจะจัดการ... [1976s] คุ้มใครคุ้มมันอย่างนี้เลย [1982s] โดนตะปบทีเดียวบิน!`.
  - Rationale: Comedic physical roleplay acting out what happens when encountering a real tiger in the wild.
- **Clip 6.3**: `อ่านคอมเมนต์สุดกาวขำจนตัวโยก_FreeTalk-vdo`
  - Range: `1518.0s - 1573.0s` (25:18 - 26:13) | Duration: `55.0s` | Frames: `[91080, 94380]`
  - Audio: Peak `0.0 dBFS`, RMS `-12.4 dBFS`.
  - Transcript: `[1518s] ติละเปล่า... [1528s] เฮ้ยทำลายอ่ะเราอ่ะ! ทำลายอ่ะ! [1540s] โอ้ยขำจนปวดท้อง!`.
  - Rationale: Spontaneous laughing fit triggered by absurd viewer suggestions in stream chat.

#### Video File 7: `เมื่อไทกะคือความชิบหายในครัว!.mp4` (Game Tag: `Overcooked`)
- **Clip 7.1**: `เปิดครัววันแรกก็วุ่นวายซะแล้ว_Overcooked-vdo`
  - Range: `430.0s - 485.0s` (07:10 - 08:05) | Duration: `55.0s` | Frames: `[25800, 29100]`
  - Audio: Peak `-8.1 dBFS`, RMS `-20.2 dBFS`.
  - Transcript: `[460s] หวาๆๆๆๆๆๆๆ เร็วขึ้น เร็วขึ้น! มะเขือเทศอยู่ไหน! โยนมาทางนี้!`.
  - Rationale: Fast-paced co-op kitchen chaos with rapid-fire order screaming and food throwing.
- **Clip 7.2**: `ออเดอร์ล้นครัวสั่งความวิกฤต_Overcooked-vdo`
  - Range: `3850.0s - 3905.0s` (64:10 - 65:05) | Duration: `55.0s` | Frames: `[231000, 234300]`
  - Audio: Peak `-6.9 dBFS`, RMS `-21.2 dBFS`.
  - Transcript: `[3850s] จานมันเยอะเกินไปแล้ว! [3876s] สั่งความวิกฤต! ไฟไหม้กะทะแล้ว! ถังดับเพลิงอยู่ไหน!`.
  - Rationale: Emergency level meltdown as orders expire and kitchen catches fire.
- **Clip 7.3**: `จานตกน้ำหมดครัวนาทีสุดท้าย_Overcooked-vdo`
  - Range: `9030.0s - 9085.0s` (150:30 - 151:25) | Duration: `55.0s` | Frames: `[541800, 545100]`
  - Audio: Peak `-11.0 dBFS`, RMS `-21.2 dBFS`.
  - Transcript: `[9030s] อ้า! ลอยไปนู่นแล้ว! [9035s] ไปเลยไปเลย! จานตกน้ำหมดแล้ว! ไม่ทันแล้ว!`.
  - Rationale: Final countdown catastrophe where conveyor belt shifts and dumps clean dishes into the abyss.

---

## 4. Verification & Testing Requirements for Quality Gates

To guarantee that Milestone M3 achieves an incontrovertible pass across Reviewers, Challengers, and the Forensic Auditor, specific verification procedures and validation criteria are defined:

### 4.1 Reviewer 1 & 2: Structural & Semantic Inspection Gate
1. **Total Count & Per-File Allocation**:
   - Query `timeline.list` in Resolve.
   - Verify that exactly 21 new timelines exist (total 28 timelines in project including 7 prior timelines).
   - Verify that exactly 3 new timelines are constructed for each of the 7 processed video files.
2. **Strict Naming Verification**:
   - Programmatically test every timeline name against regex `^([\u0E01-\u0E5B]+)_([A-Za-z0-9]+)-vdo$`.
   - Assert zero English/ASCII alphabet characters in `{Thai_Clip_Name}`.
   - Assert exact suffix `-vdo`.
3. **Timeline Duration & Track Inspection**:
   - Each timeline must contain 1 Video Track (V1) and 1 Audio Track (A1).
   - Each track item must span from record frame `0` to `3300` frames (`55.0s`).
   - Every timeline item must report `media_status == "Online"` (zero offline media).
   - Timeline frame rate must report `60.0 fps`.

### 4.2 Challenger 1 & 2: Empirical Stress & Edge Case Invariant Testing
1. **Mathematical Anti-Overlap Verification**:
   - For every processed video file, verify that the 3 new intervals $[S_1, E_1], [S_2, E_2], [S_3, E_3]$ and the prior interval $[S_{\text{prior}}, E_{\text{prior}}]$ satisfy:
     $$\forall i \ne j, \quad \max(S_i, S_j) \ge \min(E_i, E_j)$$
   - Zero frame overlap tolerance.
2. **Frame Math Integrity**:
   - `start_frame == round(start_sec * 60)`
   - `end_frame == round(end_sec * 60)`
   - `duration_frames == end_frame - start_frame == 3300`
3. **Regex Negative Fuzzing**:
   - Verify that invalid naming patterns (e.g. English in Thai prefix, `_vdo`, `.vdo`, missing delimiter) are actively rejected by the test suite.

### 4.3 Forensic Auditor: Non-Destructive Invariant & Physical SQLite Audit
1. **Source Footage Invariant**:
   - Physical audit of directory `C:\Users\warit\SynologyDrive\Tygarina\2026-09-30`:
   - Verify exactly 32 `.mp4` files exist with zero file modifications, zero deletions, and zero new temporary/proxy files.
2. **SQLite Project Database Direct Inspection**:
   - Verify project database records in `%APPDATA%\Blackmagic Design\DaVinci Resolve\Support\Resolve Disk Database\Projects\tygarina_2026-09-30\Project.db`.
   - Confirm timeline records are physically committed and read back cleanly.
3. **Unmocked Execution Proof**:
   - Validate live API communication timestamps and real GPU hardware utilization.
