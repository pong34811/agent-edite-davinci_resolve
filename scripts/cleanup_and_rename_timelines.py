"""Clean up backup timelines and rename main focus timelines to proper Thai titles.

Authorised explicitly by user: "อัปเดต Timelineหลัก เเละ ลบ Timeline สำรองทั้งหมด"
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.resolve_common import require_resolve

TARGET_MAP = [
    ("01_แกลงเพอนตงแตจดสตารท_Climbing-vdo", "แกล้งเพื่อนตั้งแต่จุดสตาร์ท_Climbing-vdo"),
    ("02_เชอกตงเปรยะหอยตองแตงกลางสายหมอก_Climbing-vdo", "เชือกตึงเปรี๊ยะห้อยต่องแต่งกลางสายหมอก_Climbing-vdo"),
    ("03_เหลอสองชวตเกาะหนาผาไว_Climbing-vdo", "เหลือสองชีวิตเกาะหน้าผาไว้_Climbing-vdo"),
    ("04_จงหวะกระโดดขามหบเหวสดเสยว_Climbing-vdo", "จังหวะกระโดดข้ามหุบเหวสุดเสียว_Climbing-vdo"),
    ("05_Highlight_Gaming_Climbing_Clutch", "Highlight_Gaming_Climbing_Clutch"),
    ("06_แกลงเพอนตงแตจดสตารท_Climbing-vdo_9x16", "แกล้งเพื่อนตั้งแต่จุดสตาร์ท_Climbing-vdo_9x16"),
    ("07_เชอกตงเปรยะหอยตองแตงกลางสายหมอก_Climbing-vdo_9x16", "เชือกตึงเปรี๊ยะห้อยต่องแต่งกลางสายหมอก_Climbing-vdo_9x16"),
    ("08_เหลอสองชวตเกาะหนาผาไว_Climbing-vdo_9x16", "เหลือสองชีวิตเกาะหน้าผาไว้_Climbing-vdo_9x16"),
    ("09_จงหวะกระโดดขามหบเหวสดเสยว_Climbing-vdo_9x16", "จังหวะกระโดดข้ามหุบเหวสุดเสียว_Climbing-vdo_9x16"),
    ("10_Highlight_Gaming_Climbing_Clutch_9x16", "Highlight_Gaming_Climbing_Clutch_9x16"),
]


def main():
    r = require_resolve()
    pm = r.GetProjectManager()
    proj = pm.GetCurrentProject()
    if proj.GetName() != "tygarina_2026-09-30_Climbing":
        proj = pm.LoadProject("tygarina_2026-09-30_Climbing")
    mp = proj.GetMediaPool()

    print(f"=== Project: {proj.GetName()} ===")
    
    # 1. Identify and delete backup timelines (_original_bak)
    bak_tls = []
    for i in range(1, proj.GetTimelineCount() + 1):
        tl = proj.GetTimelineByIndex(i)
        if tl.GetName().endswith("_original_bak"):
            bak_tls.append(tl)

    print(f"Found {len(bak_tls)} backup timelines to delete.")
    for tl in bak_tls:
        print(f"  Deleting backup: {tl.GetName()}")
    
    if bak_tls:
        ok = mp.DeleteTimelines(bak_tls)
        print(f"DeleteTimelines returned: {ok}")
        time.sleep(1.0)

    # 2. Rename remaining main timelines
    print("\nRenaming focus timelines to clean original Thai titles...")
    for old_prefix, new_name in TARGET_MAP:
        found = False
        for i in range(1, proj.GetTimelineCount() + 1):
            tl = proj.GetTimelineByIndex(i)
            if tl.GetName() == old_prefix:
                tl.SetName(new_name)
                print(f"  Renamed: {old_prefix} -> {new_name}")
                found = True
                break
        if not found:
            print(f"  Warning: Timeline with name {old_prefix} not found (may already be renamed)")

    time.sleep(1.0)
    pm.SaveProject()
    print("\nProject saved successfully.")

    # 3. Read back and verify final timelines
    print(f"\nFinal Timeline Count: {proj.GetTimelineCount()}")
    for i in range(1, proj.GetTimelineCount() + 1):
        tl = proj.GetTimelineByIndex(i)
        v_names = [tl.GetTrackName("video", v) for v in range(1, tl.GetTrackCount("video") + 1)]
        print(f"  [{i}] {tl.GetName()} -> video tracks: {v_names}")


if __name__ == "__main__":
    main()
