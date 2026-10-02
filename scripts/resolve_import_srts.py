"""Import curated SRTs into Resolve subtitle tracks (unstyled) and verify.

Designed to be exec'd inside the Resolve MCP `run_script_unsafe` sandbox, where
`resolve` is pre-injected:

    JOB = 1; PHASE = "import"   # or "verify" / "rollback" / "snapshot" / "baseline"
    exec(open(r".../scripts/resolve_import_srts.py", encoding="utf-8").read())

Rules (thai-subtitles-resolve skill): AddTrack("subtitle") first, bare
{"mediaPoolItem": item} payload, >=1.2 s between structural mutations, never
append twice, stale pool item for the same path removed before ImportMedia.
Results are MERGED into import-results.json (atomic temp + replace).

Safety: a nonempty backup .drp must exist before any mutation; AddTrack False or
an empty AppendToTimeline result aborts/fails the job; rollback deletes only the
subtitle track this script recorded adding; PHASE="snapshot" records a post-state
(video/audio items, active timeline, page, folder) and diffs it against
baseline.json.
"""
import json
import os
import re
import time

_G = globals()
# Workspace / backup / expected project can be preset by the caller before exec
# (WS_DIR, BACKUP_NAME, EXPECTED_PROJECT); defaults target the FreeTalk_2 run.
W = _G.get("WS_DIR") or r"C:\Users\warit\Desktop\agent-edite-davinci_resolve\.claude\worktrees\video-transcription-subtitles-d559c9\.superpowers\sdd\2026-10-02-freetalk2-subtitles"
BACKUP = os.path.join(W, "backup", _G.get("BACKUP_NAME") or "FreeTalk_2_before_subs.drp")
EXPECTED_PROJECT = _G.get("EXPECTED_PROJECT") or "tygarina_2026-09-30_FreeTalk_2"
SPACING = 1.3
TOL = 1

_TIMING_RE = re.compile(r"(\d+):(\d+):(\d+)[,.](\d+)\s*-->\s*(\d+):(\d+):(\d+)[,.](\d+)")


def _parse_srt(path):
    raw = open(path, encoding="utf-8").read().replace("\r\n", "\n").lstrip("\ufeff")
    cues = []
    for block in re.split(r"\n\s*\n", raw.strip()):
        lines = block.split("\n")
        for i, line in enumerate(lines):
            m = _TIMING_RE.search(line)
            if m:
                break
        else:
            continue  # no timing line in this block
        a = int(m[1]) * 3600 + int(m[2]) * 60 + int(m[3]) + int(m[4]) / 1000
        b = int(m[5]) * 3600 + int(m[6]) * 60 + int(m[7]) + int(m[8]) / 1000
        cues.append({"start_s": a, "end_s": b, "text": "\n".join(lines[i + 1:])})
    return cues


def _jobs():
    return {j["job"]: j for j in json.load(open(os.path.join(W, "jobs.json"), encoding="utf-8"))}


def _load_results():
    p = os.path.join(W, "import-results.json")
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}


def _atomic_write_json(p, data):
    tmp = p + ".tmp"
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=1)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, p)
    except BaseException:
        if os.path.exists(tmp):
            os.remove(tmp)
        raise


def _merge(job, rec):
    p = os.path.join(W, "import-results.json")
    data = _load_results()
    data.setdefault(str(job), {}).update(rec)
    _atomic_write_json(p, data)


def _backup_error():
    """None if the pre-change backup .drp exists and is nonempty, else a message."""
    try:
        if os.path.isfile(BACKUP) and os.path.getsize(BACKUP) > 0:
            return None
    except OSError:
        pass
    return "ABORT: backup .drp missing or empty (%s)" % BACKUP


def _project_error(proj):
    """None if the loaded project is EXPECTED_PROJECT (or an unnamed fake), else a message."""
    name = proj.GetName() if hasattr(proj, "GetName") else None
    if EXPECTED_PROJECT and name is not None and name != EXPECTED_PROJECT:
        return "ABORT: loaded project %r is not %r" % (name, EXPECTED_PROJECT)
    return None


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
    rec = {"timeline_id": ji["timeline_id"]}
    err = _backup_error()  # before ANY Resolve call or mutation
    if err:
        rec["status"] = err
        _merge(job, rec)
        return rec
    pm = resolve.GetProjectManager()
    proj = pm.GetCurrentProject()
    err = _project_error(proj)
    if err:
        rec["status"] = err
        _merge(job, rec)
        return rec
    mp = proj.GetMediaPool()
    srt_path = os.path.join(W, "srt", "job%d.srt" % job)
    rec["srt"] = srt_path
    tl = _timeline(proj, ji)
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
    n_after = tl.GetTrackCount("subtitle")
    if not ok_add:
        rec["subtitle_tracks_after_add"] = n_after
        rec["status"] = "ABORT: AddTrack('subtitle') returned False (no import/append)"
        _merge(job, rec)
        return rec
    if n_after != n_sub + 1:
        rec["subtitle_tracks_after_add"] = n_after
        rec["status"] = "ABORT: subtitle track count %d after AddTrack, expected %d" % (n_after, n_sub + 1)
        _merge(job, rec)
        return rec
    # Record the added track now so a rollback can delete exactly this one.
    rec["added_subtitle_track_index"] = n_after
    _merge(job, rec)
    items = mp.ImportMedia([srt_path])
    rec["ImportMedia_n"] = len(items) if items else 0
    if not items:
        rec["status"] = "FAILED: ImportMedia returned nothing (empty subtitle track left in place; rollback to remove)"
        _merge(job, rec)
        return rec
    time.sleep(SPACING)
    ret = mp.AppendToTimeline([{"mediaPoolItem": items[0]}])
    rec["Append_returned"] = len(ret) if ret else 0
    time.sleep(SPACING)
    if not ret:
        rec["status"] = "FAILED: AppendToTimeline returned nothing (not saved; rollback to remove empty track)"
        _merge(job, rec)
        return rec
    rec["saved"] = bool(pm.SaveProject())
    time.sleep(SPACING)  # spacing before the caller moves to the next timeline
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
    """Undo only what do_import added: the recorded subtitle track and stale SRT pool items.

    Never deletes a subtitle track this script did not add. Requires the import
    record (added_subtitle_track_index, subtitle_tracks_before == 0) and that the
    track to delete is the last one. Reads back after every deletion.
    """
    ji = _jobs()[job]
    rec = {"rolled_back": False}
    err = _backup_error()
    if err:
        rec["status"] = err
        _merge(job, rec)
        return rec
    prior = _load_results().get(str(job), {})
    idx = prior.get("added_subtitle_track_index")
    if prior.get("subtitle_tracks_before") != 0 or not idx:
        rec["status"] = "ABORT: no record that this script added a subtitle track; nothing deleted"
        _merge(job, rec)
        return rec
    pm = resolve.GetProjectManager()
    proj = pm.GetCurrentProject()
    err = _project_error(proj)
    if err:
        rec["status"] = err
        _merge(job, rec)
        return rec
    tl = _timeline(proj, ji)
    if tl is None:
        rec["status"] = "ABORT: timeline not found"
        _merge(job, rec)
        return rec
    if not proj.SetCurrentTimeline(tl):
        rec["status"] = "ABORT: SetCurrentTimeline False"
        _merge(job, rec)
        return rec
    time.sleep(SPACING)
    n = tl.GetTrackCount("subtitle")
    if n != idx:
        rec["status"] = "ABORT: subtitle track count %d != recorded added index %d; nothing deleted" % (n, idx)
        _merge(job, rec)
        return rec
    ok_del = tl.DeleteTrack("subtitle", idx)
    time.sleep(SPACING)
    now = tl.GetTrackCount("subtitle")
    rec["DeleteTrack"] = bool(ok_del)
    rec["subtitle_tracks_now"] = now
    if now != idx - 1:
        rec["status"] = "FAILED: subtitle track count %d after DeleteTrack, expected %d" % (now, idx - 1)
        _merge(job, rec)
        return rec
    mp = proj.GetMediaPool()
    srt_path = os.path.join(W, "srt", "job%d.srt" % job)
    stale = _stale_items(mp, srt_path)
    if stale:
        mp.DeleteClips(stale)
        time.sleep(SPACING)
        left = len(_stale_items(mp, srt_path))
        rec["stale_pool_items_left"] = left
        if left:
            rec["status"] = "FAILED: %d stale SRT pool item(s) remain after DeleteClips" % left
            _merge(job, rec)
            return rec
    rec["saved"] = bool(pm.SaveProject())
    time.sleep(SPACING)
    rec["rolled_back"] = True
    rec["status"] = "ROLLED BACK"
    rec["added_subtitle_track_index"] = None  # consumed; a second rollback aborts
    _merge(job, rec)
    return rec


def snapshot_state(res):
    """Capture page, active timeline, media pool folder and per-timeline track items.

    Same shape as baseline.json (sub/v/a counts, videoN/audioN = [start, end, name]).
    Read-only: never changes the current timeline or page.
    """
    proj = res.GetProjectManager().GetCurrentProject()
    cur = proj.GetCurrentTimeline()
    snap = {
        "project": proj.GetName(),
        "page": res.GetCurrentPage(),
        "cur_tl_id": cur.GetUniqueId() if cur else None,
        "folder": proj.GetMediaPool().GetCurrentFolder().GetName(),
        "tls": {},
    }
    for i in range(1, proj.GetTimelineCount() + 1):
        t = proj.GetTimelineByIndex(i)
        d = {"sub": t.GetTrackCount("subtitle"), "v": t.GetTrackCount("video"),
             "a": t.GetTrackCount("audio")}
        for kind, n in (("video", d["v"]), ("audio", d["a"])):
            for k in range(1, n + 1):
                d["%s%d" % (kind, k)] = [[it.GetStart(), it.GetEnd(), it.GetName()]
                                         for it in (t.GetItemListInTrack(kind, k) or [])]
        snap["tls"][t.GetUniqueId()] = d
    return snap


def diff_snapshot(base, post):
    """List differences, ignoring only the subtitle track count (the expected change)."""
    diffs = []
    for k in ("project", "page", "cur_tl_id", "folder"):
        if k in base and base.get(k) != post.get(k):
            diffs.append("%s: %r -> %r" % (k, base.get(k), post.get(k)))
    bt, pt = base.get("tls", {}), post.get("tls", {})
    for tid in sorted(set(bt) | set(pt)):
        if tid not in pt:
            diffs.append("timeline %s missing after" % tid)
            continue
        if tid not in bt:
            diffs.append("timeline %s new after" % tid)
            continue
        b, p = bt[tid], pt[tid]
        for key in sorted((set(b) | set(p)) - {"sub"}):
            if b.get(key) != p.get(key):
                diffs.append("timeline %s %s: %r -> %r" % (tid, key, b.get(key), p.get(key)))
    return diffs


def do_baseline(job=None):
    """Write baseline.json (refuses to overwrite an existing one). Read-only on Resolve."""
    err = _project_error(resolve.GetProjectManager().GetCurrentProject())
    if err:
        return {"status": err}
    p = os.path.join(W, "baseline.json")
    if os.path.exists(p):
        return {"status": "ABORT: baseline.json already exists"}
    snap = snapshot_state(resolve)
    _atomic_write_json(p, snap)
    return {"status": "baseline written", "project": snap["project"], "page": snap["page"],
            "cur_tl_id": snap["cur_tl_id"], "folder": snap["folder"],
            "subtitle_tracks": {t: d["sub"] for t, d in snap["tls"].items()}}


def do_snapshot(job=None):
    """Write post-state.json and diff it against baseline.json (read-only on Resolve)."""
    post = snapshot_state(resolve)
    _atomic_write_json(os.path.join(W, "post-state.json"), post)
    base = json.load(open(os.path.join(W, "baseline.json"), encoding="utf-8"))
    diffs = diff_snapshot(base, post)
    rec = {"snapshot_file": "post-state.json", "diffs_vs_baseline": diffs,
           "matches_baseline": not diffs,
           "subtitle_tracks_per_timeline": {t: d["sub"] for t, d in post["tls"].items()}}
    _atomic_write_json(os.path.join(W, "post-state-diff.json"), rec)
    return rec


if "PHASE" in globals():
    result = {"import": do_import, "verify": do_verify, "rollback": do_rollback,
              "snapshot": do_snapshot, "baseline": do_baseline}[PHASE](globals().get("JOB"))
