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

def inspect_v3(tl_name):
    for i in range(1, p.GetTimelineCount()+1):
        tl = p.GetTimelineByIndex(i)
        if tl.GetName() == tl_name:
            print(f"=== Timeline: {tl_name} ===")
            v3_items = tl.GetItemListInTrack("video", 3) or []
            print(f"V3 items count: {len(v3_items)}")
            for idx, item in enumerate(v3_items):
                print(f"Item {idx}: start={item.GetStart()}, end={item.GetEnd()}, dur={item.GetDuration()}")
                comp = item.GetFusionCompByIndex(1)
                if comp:
                    tools = comp.GetToolList()
                    for t in tools.values():
                        name = t.GetAttrs().get("TOOLS_Name", "")
                        if "Transform" in name:
                            print(f"  Tool: {name}")
                            print(f"    Center: {t.GetInput('Center')}")
                            print(f"    Size: {t.GetInput('Size')}")
                            print(f"    Edges: {t.GetInput('Edges')}")

inspect_v3('หนีฝ่าความหนาว_Minecraft-vdo')
inspect_v3('หนีฝ่าความหนาว_Minecraft-vdo_9x16')
