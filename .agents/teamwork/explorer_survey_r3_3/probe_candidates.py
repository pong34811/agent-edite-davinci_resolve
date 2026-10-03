import os
import sys
import subprocess
import json

sys.stdout.reconfigure(encoding='utf-8')

folder = r"C:\Users\warit\SynologyDrive\Tygarina\2026-09-30"
files_map = {
    "REPO": "Collab R.E.P.O - เก็บของไว้ให้ไกลเสือ.mp4",
    "Climbing": "ปืนเขาที่เราหมดแรง @KRATOI_26  @Mixzy21PM  @Pleiades_Frontier.mp4",
    "Ib": "IB - สำรวจโลกภาพวาด P1.mp4",
    "DnD": "After DnD ： เมื่อบาร์ดด่าจนมังกรตาย!.mp4",
    "GarticPhone": "Gartic phone - ไทกะสกิลวาดรูป 999999.mp4",
    "FreeTalk": "Free Talk ： หยุดเสือด้วยมือเปล่า？？.mp4",
    "Overcooked": "เมื่อไทกะคือความชิบหายในครัว!.mp4"
}

ffprobe = r"C:\Users\warit\AppData\Local\Microsoft\WinGet\Links\ffprobe.exe"
for tag, filename in files_map.items():
    filepath = os.path.join(folder, filename)
    cmd = [ffprobe, "-v", "quiet", "-print_format", "json", "-show_format", "-show_streams", filepath]
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    data = json.loads(res.stdout)
    dur = float(data["format"]["duration"])
    vstream = [s for s in data["streams"] if s["codec_type"] == "video"][0]
    astream = [s for s in data["streams"] if s["codec_type"] == "audio"][0]
    fps_eval = eval(vstream["r_frame_rate"])
    nb_frames = int(vstream.get("nb_frames", int(dur * fps_eval)))
    print(f"[{tag}] {filename}")
    print(f"  Duration: {dur:.2f}s ({dur/60:.1f}m) | FPS: {fps_eval} | Video: {vstream['width']}x{vstream['height']} {vstream['codec_name']} | Audio: {astream['codec_name']} {astream['sample_rate']}Hz")
