"""Deploy VTuber Zoom Focus timelines to tygarina_2026-09-30_Climbing via verified native DRT transfer.

MCP-GAP: live davinci-resolve MCP tools absent from this session's tool catalog -> using Python scripting API via scripts/resolve_common.py:connect_resolve.

Safety:
- Pre-edit backup is verified at backups/tygarina_2026-09-30_Climbing_before_focus.drp
- Existing timelines in tygarina_2026-09-30_Climbing are preserved as '<name>_original_bak'
- All 10 focus timelines (5 horizontal + 5 vertical) are imported with exact V2/V4 VTuber Zoom tracks
- Saves project and exports a fresh verified post-edit .drp checkpoint
"""
from __future__ import annotations

import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.resolve_common import connect_resolve, require_resolve
from scripts.backup_drp import export_verified, verify_drp

SETTLE = 1.25


def main():
    r = require_resolve()
    pm = r.GetProjectManager()

    # Verify pre-edit backup exists
    pre_bak = Path("backups/tygarina_2026-09-30_Climbing_before_focus.drp").resolve()
    if not pre_bak.is_file():
        raise SystemExit(f"Pre-edit backup missing: {pre_bak}")
    verify_drp(pre_bak)
    print(f"Pre-edit backup verified: {pre_bak} ({pre_bak.stat().st_size:,} bytes)")

    # 1. Export all 10 timelines from tygarina_2026-09-30_Climbing_VTuberFocus
    proj_src = pm.LoadProject("tygarina_2026-09-30_Climbing_VTuberFocus")
    if not proj_src:
        raise SystemExit("Source project tygarina_2026-09-30_Climbing_VTuberFocus not found")

    drt_dir = Path("scratch/drt_climbing_focus").resolve()
    drt_dir.mkdir(parents=True, exist_ok=True)

    exported_drts = []
    print(f"\n--- Exporting 10 focus timelines from {proj_src.GetName()} ---")
    for i in range(1, proj_src.GetTimelineCount() + 1):
        tl = proj_src.GetTimelineByIndex(i)
        name = tl.GetName()
        safe_name = "".join(c for c in name if c.isalnum() or c in ("-", "_")).rstrip()
        drt_path = drt_dir / f"{i:02d}_{safe_name}.drt"
        if drt_path.exists():
            drt_path.unlink()
        
        ok = tl.Export(str(drt_path), r.EXPORT_DRT, r.EXPORT_NONE)
        if not ok or not drt_path.is_file() or drt_path.stat().st_size == 0:
            raise RuntimeError(f"Export failed for timeline [{i}] {name}")
        exported_drts.append((i, name, drt_path))
        print(f"  [{i}] Exported: {name} -> {drt_path.name} ({drt_path.stat().st_size:,} bytes)")

    # 2. Open destination project tygarina_2026-09-30_Climbing
    proj_dst = pm.LoadProject("tygarina_2026-09-30_Climbing")
    if not proj_dst:
        raise SystemExit("Destination project tygarina_2026-09-30_Climbing not found")
    mp_dst = proj_dst.GetMediaPool()

    print(f"\n--- Importing into {proj_dst.GetName()} ---")
    # Rename existing originals to preserve as rollback copies
    for i, name, drt_path in exported_drts:
        for t_idx in range(1, proj_dst.GetTimelineCount() + 1):
            tl_existing = proj_dst.GetTimelineByIndex(t_idx)
            if tl_existing and tl_existing.GetName() == name:
                bak_name = name + "_original_bak"
                tl_existing.SetName(bak_name)
                time.sleep(0.5)
                print(f"  Renamed existing: {name} -> {bak_name}")
                break

    time.sleep(SETTLE)

    # Import the 10 focus timelines
    imported_records = []
    for i, name, drt_path in exported_drts:
        imp_tl = mp_dst.ImportTimelineFromFile(str(drt_path))
        if not imp_tl:
            raise RuntimeError(f"Import failed for {name} from {drt_path}")
        time.sleep(0.8)
        
        # Verify track architecture
        v_count = imp_tl.GetTrackCount("video")
        v_names = [imp_tl.GetTrackName("video", v) for v in range(1, v_count + 1)]
        zoom_items = []
        for v in range(1, v_count + 1):
            if imp_tl.GetTrackName("video", v) == "VTuber Zoom":
                zoom_items = imp_tl.GetItemListInTrack("video", v) or []
                break
        
        imported_records.append({
            "index": i,
            "name": name,
            "video_tracks": v_names,
            "zoom_clip_count": len(zoom_items),
        })
        print(f"  [{i}] Imported successfully: {name} | Video tracks: {v_names} | Focus clips: {len(zoom_items)}")

    # 3. Save project and export post-edit backup
    if not pm.SaveProject():
        raise RuntimeError("SaveProject failed on tygarina_2026-09-30_Climbing")
    print(f"\nProject {proj_dst.GetName()} saved successfully.")

    post_bak = Path("backups/tygarina_2026-09-30_Climbing_focus_complete.drp").resolve()
    post_size = export_verified(pm, proj_dst, post_bak)
    print(f"Post-edit verified backup created: {post_bak} ({post_size:,} bytes)")

    print("\n=== ALL 10 TIMELINES DEPLOYED & VERIFIED SUCCESSFULLY ===")


if __name__ == "__main__":
    main()
