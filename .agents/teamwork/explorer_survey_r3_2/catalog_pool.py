import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\warit\Desktop\agent-edite-davinci_resolve\.agents\teamwork\explorer_survey_r3_2\resolve_survey_data.json', encoding='utf-8') as f:
    data = json.load(f)

clips = data['media_pool_clips']
timelines = data['timelines']

tl_names = {t['name'] for t in timelines}
vdo_clips = [c for c in clips if c['name'] not in tl_names]
tl_clips = [c for c in clips if c['name'] in tl_names]

print(f"Total items in Master: {len(clips)}")
print(f"Timeline items in Master: {len(tl_clips)}")
print(f"Video file clips in Master: {len(vdo_clips)}")

processed_files = {
    'Highlight_Gaming_REPO_Jumpscare': 'Collab R.E.P.O - เก็บของไว้ให้ไกลเสือ.mp4',
    'Highlight_Gaming_Climbing_Clutch': 'ปืนเขาที่เราหมดแรง @KRATOI_26  @Mixzy21PM  @Pleiades_Frontier.mp4',
    'Highlight_Gaming_Ib_Horror': 'IB - สำรวจโลกภาพวาด P1.mp4',
    'Highlight_Fun_DnD_Bard': 'After DnD ： เมื่อบาร์ดด่าจนมังกรตาย!.mp4',
    'Highlight_Meme_GarticPhone_Art': 'Gartic phone - ไทกะสกิลวาดรูป 999999.mp4',
    'Highlight_Meme_FreeTalk_Tiger': 'Free Talk ： หยุดเสือด้วยมือเปล่า？？.mp4',
    'Highlight_Fun_Overcooked_KitchenFire': 'เมื่อไทกะคือความชิบหายในครัว!.mp4'
}

print("\n=== The 7 Processed Video Files & Pool IDs ===")
vdo_map = {c['name']: c for c in vdo_clips}
for tl_name, vdo_name in processed_files.items():
    c = vdo_map.get(vdo_name)
    if c:
        print(f"Timeline: {tl_name}")
        print(f"  Source File: {vdo_name}")
        print(f"  MediaPoolItem ID: {c['id']}")
        print(f"  FPS: {c['fps']} | Dur: {c['duration']} | Res: {c['resolution']} | Codec: {c['video_codec']}")
    else:
        print(f"Timeline: {tl_name} -> Source File: {vdo_name} NOT FOUND!")

print("\n=== All 32 Video Files in Media Pool ===")
for i, c in enumerate(vdo_clips):
    is_proc = c['name'] in processed_files.values()
    marker = "[PRIOR RUN PROCESSED]" if is_proc else "[UNPROCESSED CANDIDATE]"
    print(f"{i+1:2d}. {marker} {c['name']} (ID: {c['id']}, FPS: {c['fps']}, Dur: {c['duration']}, Res: {c['resolution']})")
