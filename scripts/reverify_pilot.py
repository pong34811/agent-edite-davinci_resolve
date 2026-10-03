"""Re-verify the existing pilot _9x16 with the same checks the batch uses (read-mostly: exports 3 stills)."""
import json
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import m2_convert_pilot as m2  # noqa: E402
import m3_convert as m3  # noqa: E402


def main():
    resolve = m2.get_resolve()
    proj = resolve.GetProjectManager().GetCurrentProject()
    orig = m2.find_timeline_by_name(proj, m2.PILOT_NAME)
    new = m2.find_timeline_by_name(proj, m2.TARGET_NAME)
    pre = m3.snapshot_original(orig)
    res = m3.verify(orig, new, pre, m3.gif_infos(orig))
    entry_tc = new.GetCurrentTimecode()
    assert proj.GetCurrentTimeline().GetUniqueId() == new.GetUniqueId()
    stills = m3.export_stills(proj, new, "pilot", 60.0)
    res["stills"] = {k: m3.pixel_check(p) for k, p in stills.items()}
    new.SetCurrentTimecode(entry_tc)
    print(json.dumps(res, ensure_ascii=False, default=str, indent=1))


if __name__ == "__main__":
    main()
