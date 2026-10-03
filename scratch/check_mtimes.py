import os
import sys
import datetime

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

files = [
    'Collab R.E.P.O - เก็บของไว้ให้ไกลเสือ.mp4',
    'ปืนเขาที่เราหมดแรง @KRATOI_26  @Mixzy21PM  @Pleiades_Frontier.mp4',
    'IB - สำรวจโลกภาพวาด P1.mp4',
    'After DnD ： เมื่อบาร์ดด่าจนมังกรตาย!.mp4',
    'Gartic phone - ไทกะสกิลวาดรูป 999999.mp4',
    'Free Talk ： หยุดเสือด้วยมือเปล่า？？.mp4',
    'เมื่อไทกะคือความชิบหายในครัว!.mp4'
]
d = r'C:\Users\warit\SynologyDrive\Tygarina\2026-09-30'
for f in files:
    p = os.path.join(d, f)
    mtime = datetime.datetime.fromtimestamp(os.path.getmtime(p))
    size = os.path.getsize(p)
    print(f"{f}: {mtime} ({size:,} bytes)")
