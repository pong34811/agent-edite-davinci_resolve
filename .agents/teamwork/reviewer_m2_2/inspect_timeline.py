import sys, os
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

os.environ['RESOLVE_SCRIPT_LIB'] = r'C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll'
sys.path.append(r'C:\Program Files\Blackmagic Design\DaVinci Resolve\ResolvePython\lib\modules')
import DaVinciResolveScript as dvr

r = dvr.scriptapp('Resolve')
p = r.GetProjectManager().GetCurrentProject()
print('Timelines count:', p.GetTimelineCount())
for i in range(1, p.GetTimelineCount()+1):
    tl = p.GetTimelineByIndex(i)
    name = tl.GetName()
    if 'หนีฝ่าความหนาว' in name:
        res_w = tl.GetSetting("timelineResolutionWidth")
        res_h = tl.GetSetting("timelineResolutionHeight")
        custom = tl.GetSetting("useCustomSettings")
        fps = tl.GetSetting("timelineFrameRate")
        dur = tl.GetEndFrame() - tl.GetStartFrame()
        print(f"Timeline: {name} (ID: {tl.GetUniqueId()})")
        print(f"  Res: {res_w}x{res_h} (custom={custom}), FPS: {fps}, Duration: {dur}")
        print(f"  Tracks: V={tl.GetTrackCount('video')}, A={tl.GetTrackCount('audio')}, Sub={tl.GetTrackCount('subtitle')}")
