import sys, os, time
os.environ['RESOLVE_SCRIPT_LIB'] = r'C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll'
sys.path.append(r'C:\Program Files\Blackmagic Design\DaVinci Resolve\ResolvePython\lib\modules')
import DaVinciResolveScript as dvr

def frame_to_timecode(frame_number: int, fps: float = 60.0) -> str:
    total_seconds = int(frame_number // fps)
    rem_frames = int(round(frame_number % fps))
    hours = total_seconds // 3600
    rem_seconds = total_seconds % 3600
    minutes = rem_seconds // 60
    seconds = rem_seconds % 60
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}:{rem_frames:02d}"

r = dvr.scriptapp('Resolve')
pm = r.GetProjectManager()
p = pm.GetCurrentProject()

orig_tl = None
for i in range(1, p.GetTimelineCount()+1):
    tl = p.GetTimelineByIndex(i)
    if tl.GetName() == 'หนีฝ่าความหนาว_Minecraft-vdo':
        orig_tl = tl
        break

if orig_tl:
    p.SetCurrentTimeline(orig_tl)
    time.sleep(0.5)
    tc = frame_to_timecode(219300, 60.0)
    orig_tl.SetCurrentTimecode(tc)
    time.sleep(0.5)
    out_path = r"C:\Users\warit\Desktop\agent-edite-davinci_resolve\.agents\teamwork\reviewer_m2_2\orig_still_219300.png"
    res = p.ExportCurrentFrameAsStill(out_path)
    print("Exported original still 219300:", res)
