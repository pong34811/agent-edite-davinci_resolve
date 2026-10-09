"""Shared helpers for the p2 9:16 pilot (aomimama-2026-09-p2).

MCP-GAP: project_manager.snapshot / timeline.* read only the CURRENT timeline and give no single
comparable signature (subtitle text + per-item GetProperty + Fusion inputs) for a non-active
timeline -> read-only signature code through scripts/resolve_common.connect_resolve.

Usage (read-only):
  python -m scripts.p2_9x16_common baseline   # writes exports/9x16-pilot/baseline_original.json
  python -m scripts.p2_9x16_common compare    # re-reads the original and diffs it against the baseline
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from scripts.resolve_common import connect_resolve  # noqa: E402

PROJECT = "aomimama-2026-09-p2"
ORIG_ID = "63c54485-8b68-4b57-9f24-3cf21b70fc46"
ORIG_NAME = "ชนะรอบแล้วบ่นเหนื่อย-strinova-vdo"
TARGET_NAME = ORIG_NAME + "_9x16"
OUT = ROOT / "exports" / "9x16-pilot"
SETTINGS = ["useCustomSettings", "timelineResolutionWidth", "timelineResolutionHeight",
            "timelineFrameRate", "timelinePlaybackFrameRate", "timelineOutputResMatchTimelineRes",
            "timelineOutputResolutionWidth", "timelineOutputResolutionHeight", "timelinePixelAspectRatio",
            "timelineInputResMismatchBehavior", "timelineOutputResMismatchBehavior"]


def check(v, msg):
    if not v:
        raise RuntimeError(msg)


def project_and_timeline(tid=ORIG_ID, name=ORIG_NAME):
    r = connect_resolve()
    check(r is not None, "Resolve unavailable")
    pm = r.GetProjectManager()
    p = pm.GetCurrentProject()
    check(p and p.GetName() == PROJECT, "wrong project loaded")
    tl = find(p, tid, name)
    return r, pm, p, tl


def find(p, tid=None, name=None):
    for i in range(1, p.GetTimelineCount() + 1):
        t = p.GetTimelineByIndex(i)
        if (tid is None or t.GetUniqueId() == tid) and (name is None or t.GetName() == name):
            return t
    return None


def fusion_sig(it):
    out = []
    try:
        n = it.GetFusionCompCount() or 0
    except Exception:
        return None
    for ci in range(1, n + 1):
        comp = it.GetFusionCompByIndex(ci)
        tools = []
        if comp:
            for t in (comp.GetToolList() or {}).values():
                reg = t.GetAttrs().get("TOOLS_RegID")
                d = {"reg": reg}
                if reg == "Transform":
                    d.update({k: t.GetInput(k) for k in ("Size", "Center", "Pivot", "Edges")})
                tools.append(d)
        out.append(sorted(tools, key=lambda d: json.dumps(d, sort_keys=True, default=str)))
    return out


def item_sig(it, kind, fusion=True):
    d = {"id": it.GetUniqueId(), "name": it.GetName(), "start": it.GetStart(), "end": it.GetEnd()}
    if kind != "subtitle":
        try:
            d["src"] = [it.GetSourceStartFrame(), it.GetSourceEndFrame()]
        except Exception:
            d["src"] = None
        d["props"] = it.GetProperty()
        mpi = it.GetMediaPoolItem()
        d["mpi"] = mpi.GetName() if mpi else None
        try:
            d["enabled"] = it.GetClipEnabled()
        except Exception:
            pass
    if kind == "video" and fusion:
        d["fusion"] = fusion_sig(it)
    return d


def signature(tl, fusion=True):
    sig = {"id": tl.GetUniqueId(), "name": tl.GetName(), "start": tl.GetStartFrame(), "end": tl.GetEndFrame(),
           "settings": {k: tl.GetSetting(k) for k in SETTINGS}, "tracks": {}}
    for kind in ("video", "audio", "subtitle"):
        sig["tracks"][kind] = []
        for i in range(1, tl.GetTrackCount(kind) + 1):
            sig["tracks"][kind].append({
                "index": i, "name": tl.GetTrackName(kind, i), "enabled": tl.GetIsTrackEnabled(kind, i),
                "locked": tl.GetIsTrackLocked(kind, i),
                "items": [item_sig(x, kind, fusion) for x in (tl.GetItemListInTrack(kind, i) or [])]})
    return json.loads(json.dumps(sig, ensure_ascii=False, default=str))


def diff(a, b, path=""):
    out = []
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b)):
            out += diff(a.get(k, "<missing>"), b.get(k, "<missing>"), f"{path}.{k}")
    elif isinstance(a, list) and isinstance(b, list) and len(a) == len(b):
        for i, (x, y) in enumerate(zip(a, b)):
            out += diff(x, y, f"{path}[{i}]")
    elif a != b:
        out.append(f"{path}: {str(a)[:120]} != {str(b)[:120]}")
    return out


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "baseline"
    _, _, _, tl = project_and_timeline()
    check(tl is not None, "original not found by id+name")
    OUT.mkdir(parents=True, exist_ok=True)
    base = OUT / "baseline_original.json"
    sig = signature(tl)
    if cmd == "baseline":
        check(not base.exists(), "baseline already exists; refusing to overwrite")
        base.write_text(json.dumps(sig, ensure_ascii=False, indent=1), encoding="utf-8")
        counts = {k: [len(t["items"]) for t in v] for k, v in sig["tracks"].items()}
        print("BASELINE", base, sig["start"], sig["end"], sig["settings"], counts)
    elif cmd == "compare":
        d = diff(json.loads(base.read_text(encoding="utf-8")), sig)
        print("ORIGINAL_DIFFS", len(d))
        for x in d[:50]:
            print(" ", x)
        return 1 if d else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
