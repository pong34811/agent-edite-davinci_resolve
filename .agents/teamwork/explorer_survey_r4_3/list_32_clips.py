import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('.agents/teamwork/explorer_survey_r4_3/current_state.json', encoding='utf-8') as f:
    data = json.load(f)

clips = data['media_pool_clips']
touched_names = {
    'Collab R.E.P.O - เก็บของไว้ให้ไกลเสือ.mp4',
    'ปืนเขาที่เราหมดแรง @KRATOI_26  @Mixzy21PM  @Pleiades_Frontier.mp4',
    'IB - สำรวจโลกภาพวาด P1.mp4',
    'After DnD ： เมื่อบาร์ดด่าจนมังกรตาย!.mp4',
    'Gartic phone - ไทกะสกิลวาดรูป 999999.mp4',
    'Free Talk ： หยุดเสือด้วยมือเปล่า？？.mp4',
    'เมื่อไทกะคือความชิบหายในครัว!.mp4'
}

print(f"Total clips in media pool: {len(clips)}")
for i, c in enumerate(sorted(clips, key=lambda x: x['name']), 1):
    is_touched = c['name'] in touched_names
    status = 'TOUCHED' if is_touched else 'UNTOUCHED'
    name = c['name']
    cid = c['id']
    dur = c.get('duration', 'N/A')
    res = c.get('resolution', 'N/A')
    print(f"{i:02d}. [{status:9s}] {name} | ID: {cid} | Dur: {dur} | Res: {res}")
