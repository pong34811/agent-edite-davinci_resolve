"""Test and inspect framing live on target timeline in DaVinci Resolve."""
import os
import sys
import time
from PIL import Image
import numpy as np

# Ensure resolve module can be imported
sys.path.append(os.path.abspath("scripts"))
import m2_convert_pilot as m2

resolve = m2.get_resolve()
if not resolve:
    print("Cannot connect to Resolve")
    sys.exit(1)

pm = resolve.GetProjectManager()
proj = pm.GetCurrentProject()
print("Project:", proj.GetName())

tl = m2.find_timeline_by_name(proj, m2.TARGET_NAME)
if not tl:
    print("Target timeline not found:", m2.TARGET_NAME)
    sys.exit(1)

proj.SetCurrentTimeline(tl)
time.sleep(0.5)

print("Timeline:", tl.GetName())
print("Track count video:", tl.GetTrackCount("video"))

v1_items = tl.GetItemListInTrack("video", 1) or []
v2_items = tl.GetItemListInTrack("video", 2) or []
v3_items = tl.GetItemListInTrack("video", 3) or []
v4_items = tl.GetItemListInTrack("video", 4) or []

print(f"V1 count: {len(v1_items)}, V2 count: {len(v2_items)}, V3 count: {len(v3_items)}, V4 count: {len(v4_items)}")

if v4_items:
    v4_mpi = v4_items[0].GetMediaPoolItem()
    if v4_mpi:
        print("V4 Clip Property:", v4_mpi.GetClipProperty())

# Check V3 Transform tool inputs
if v3_items:
    comp = v3_items[0].GetFusionCompByIndex(1)
    if comp:
        tools = comp.GetToolList()
        for t in tools.values():
            if "Transform" in t.GetAttrs().get("TOOLS_Name", ""):
                print("Transform inputs:")
                for inp_name in ["Center", "Pivot", "Size", "Aspect", "Angle"]:
                    print(f"  {inp_name}:", t.GetInput(inp_name))
