"""Import curated SRTs into Resolve subtitle tracks (unstyled) and verify.

Designed to be exec'd inside the Resolve MCP `run_script_unsafe` sandbox, where
`resolve` is pre-injected:

    JOB = 1; PHASE = "import"   # or "verify" / "rollback"
    exec(open(r".../scripts/resolve_import_srts.py", encoding="utf-8").read())

Rules (thai-subtitles-resolve skill): AddTrack("subtitle") first, bare
{"mediaPoolItem": item} payload, >=1.2 s between structural mutations, never
append twice, stale pool item for the same path removed before ImportMedia.
Results are MERGED into import-results.json.
"""
import json
import os
import re
import time

W = r"C:\Users\warit\Desktop\agent-edite-davinci_resolve\.claude\worktrees\video-transcription-subtitles-d559c9\.superpowers\sdd\2026-10-02-freetalk1-subtitles"
SPACING = 1.3
TOL = 1


def _parse_srt(path):
    raw = open(path, encoding="utf-8").read().replace("\r\n", "\n").lstrip("\ufeff")
    cues = []
    for block in re.split(r"\n\s*\n", raw.strip()):
        lines = block.split("\n")
        m = re.match(r"(\d+):(\d+):(\d+)[,.](\d+)\s*-->\s*(\d+):(\d+):(\d+)[,.](\d+)", lines[1])
        a = int(m[1]) * 3600 + int(m[2]) * 60 + int(m[3]) + int(m[4]) / 1000
        b = int(m[5]) * 3600 + int(m[6]) * 60 + int(m[7]) + int(m[8]) / 1000
        cues.append({"start_s": a, "end_s": b, "text": "\n".join(lines[2:])})
    return cues


def _jobs():
    return {j["job"]: j for j in json.load(open(os.path.join(W, "jobs.json"), encoding="utf-8"))}


def _merge(job, rec):
    p = os.path.join(W, "import-results.json")
    data = json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}
    data.setdefault(str(job), {}).update(rec)
    json.dump(data, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def _timeline(proj, job_info):
    for i in range(1, proj.GetTimelineCount() + 1):
        t = proj.GetTimelineByIndex(i)
        if t.GetUniqueId() == job_info["timeline_id"]:
            return t
    return None


def _stale_items(mp, srt_path):
    out = []

    def walk(f):
        for c in f.GetClipList():
            if (c.GetClipProperty("File Path") or "") == srt_path:
                out.append(c)
        for s in f.GetSubFolderList():
            walk(s)

    walk(mp.GetRootFolder())
    return out


def do_import(job):
    ji = _jobs()[job]
    pm = resolve.GetProjectManager()
    proj = pm.GetCurrentProject()
    mp = proj.GetMediaPool()
    srt_path = os.path.join(W, "srt", "job%d.srt" % job)
    tl = _timeline(proj, ji)
    rec = {"timeline_id": ji["timeline_id"], "srt": srt_path}
    if tl is None:
        rec["status"] = "ABORT: timeline not found"
        _merge(job, rec)
        return rec
    if not proj.SetCurrentTimeline(tl):
        rec["status"] = "ABORT: SetCurrentTimeline False"
        _merge(job, rec)
        return rec
    time.sleep(SPACING)
    n_sub = tl.GetTrackCount("subtitle")
    rec["subtitle_tracks_before"] = n_sub
    if n_sub != 0:
        rec["status"] = "ABORT: timeline already has %d subtitle track(s)" % n_sub
        _merge(job, rec)
        return rec
    stale = _stale_items(mp, srt_path)
    if stale:
        rec["stale_pool_items_deleted"] = len(stale)
        mp.DeleteClips(stale)
        time.sleep(SPACING)
    ok_add = tl.AddTrack("subtitle")
    rec["AddTrack"] = bool(ok_add)
    time.sleep(SPACING)
    items = mp.ImportMedia([srt_path])
    rec["ImportMedia_n"] = len(items) if items else 0
    if not items:
        rec["status"] = "ABORT: ImportMedia returned nothing (empty subtitle track left in place)"
        _merge(job, rec)
        return rec
    time.sleep(SPACING)
    ret = mp.AppendToTimeline([{"mediaPoolItem": items[0]}])
    rec["Append_returned"] = len(ret) if ret else 0
    time.sleep(SPACING)
    rec["saved"] = bool(pm.SaveProject())
    rec["status"] = "imported (unverified)"
    _merge(job, rec)
    return rec


def do_verify(job):
    ji = _jobs()[job]
    pm = resolve.GetProjectManager()
    proj = pm.GetCurrentProject()
    tl = _timeline(proj, ji)
    srt = _parse_srt(os.path.join(W, "srt", "job%d.srt" % job))
    fps = float(ji["fps"])
    rec = {"verify_cues_expected": len(srt)}
    ntr = tl.GetTrackCount("subtitle")
    rec["subtitle_tracks_after"] = ntr
    items = tl.GetItemListInTrack("subtitle", 1) or []
    rec["cues_found"] = len(items)
    problems = []
    if ntr != 1:
        problems.append("subtitle track count %d" % ntr)
    if len(items) != len(srt):
        problems.append("count %d != %d" % (len(items), len(srt)))
    max_ds = max_de = 0
    text_mismatch = 0
    samples = []
    for k, (it, cue) in enumerate(zip(items, srt)):
        es = round(cue["start_s"] * fps)
        ee = round(cue["end_s"] * fps)
        gs, ge = it.GetStart(), it.GetEnd()
        name = it.GetName()
        ds, de = gs - es, ge - ee
        max_ds, max_de = max(max_ds, abs(ds)), max(max_de, abs(de))
        if abs(ds) > TOL:
            problems.append("cue %d start %d != %d" % (k + 1, gs, es))
        if abs(de) > TOL:
            problems.append("cue %d end %d != %d" % (k + 1, ge, ee))
        if name != cue["text"]:
            text_mismatch += 1
            if len(samples) < 5:
                samples.append({"cue": k + 1, "got": name, "want": cue["text"]})
    rec["max_start_delta_frames"] = max_ds
    rec["max_end_delta_frames"] = max_de
    rec["text_mismatches"] = text_mismatch
    if text_mismatch:
        problems.append("%d text mismatches" % text_mismatch)
        rec["text_mismatch_samples"] = samples
    rec["problems"] = problems[:20]
    rec["verified"] = not problems
    rec["status"] = "VERIFIED" if not problems else "MISMATCH"
    _merge(job, rec)
    return rec


def do_rollback(job):
    """Remove the subtitle track(s) of a timeline (for a retry after mismatch)."""
    ji = _jobs()[job]
    pm = resolve.GetProjectManager()
    proj = pm.GetCurrentProject()
    tl = _timeline(proj, ji)
    proj.SetCurrentTimeline(tl)
    time.sleep(SPACING)
    for idx in range(tl.GetTrackCount("subtitle"), 0, -1):
        tl.DeleteTrack("subtitle", idx)
        time.sleep(SPACING)
    mp = proj.GetMediaPool()
    stale = _stale_items(mp, os.path.join(W, "srt", "job%d.srt" % job))
    if stale:
        mp.DeleteClips(stale)
        time.sleep(SPACING)
    pm.SaveProject()
    rec = {"rolled_back": True, "subtitle_tracks_now": tl.GetTrackCount("subtitle")}
    _merge(job, rec)
    return rec


if "PHASE" in globals() and "JOB" in globals():
    result = {"import": do_import, "verify": do_verify, "rollback": do_rollback}[PHASE](JOB)
