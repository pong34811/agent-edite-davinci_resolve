"""Final export of every p2 timeline (horizontal + vertical) to the Drive `vdo` folder with the user's render preset.

MCP-GAP: MCP `render` works one timeline per call and cannot duplicate a timeline + drop a cover on it; the batch needs
a loop -> Resolve Python scripting API (same pattern as p2_render_vertical.py). The render settings are NOT hardcoded:
`LoadRenderPreset("H.264 Master")` is loaded before every job and only SelectAllFrames/TargetDir/CustomName are overridden.
Vertical (`_9x16`) timelines are duplicated to a temporary `<name>__cover_tmp`, the matching `<name>.jpg` from the vdo
folder is laid on a new top video track for COVER_FRAMES at the first frame (nothing is shifted), the copy is rendered and
deleted once the job completes. Originals are never modified. `<name>_150s` variants replace their original (output keeps
the original name). Starts ONLY the jobs it creates (the project queue holds old jobs).

Run from repo root (dry-run by default):
  python -m scripts.p2_export_final [--project NAME] [--covers DIR] [--out DIR] [--preset NAME] [--require-cover]
                                    [--apply] [--only "out_name,out_name"] [--limit N] [--verify]
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

VDO = "G:/My Drive/Projects/Aomi-mama/2026-09-aomimama/vdo"
PROJECT = "aomimama-2026-09-p2"
PRESET = "H.264 Master"
COVER_FRAMES = 1
GAP = 1.3
OUT = ROOT / "exports" / "final-export"
VARIANT = "_150s"
TMP = "__cover_tmp"
# User requirement: Deliver > File > Export Subtitle checked, Format = "Burn into video" (the preset alone left it as a
# separate .ttml sidecar file).
SUBTITLE_BURN_IN = {"ExportSubtitle": True, "SubtitleFormat": "BurnIn"}


BAD_GIF = "Anime - Shocked Reaction.gif"
GIF_TRIM = 5


def _bad_gifs(tl):
    return [(n, x) for n in range(1, tl.GetTrackCount("video") + 1)
            for x in tl.GetItemListInTrack("video", n) or [] if x.GetName() == BAD_GIF]


def _trim_gif_tails(p, mp, tl):
    """Resolve cannot decode the last frames of this GIF at render time (same fix as p2_trim_bad_gif_tail.py),
    applied to the temporary copy only."""
    keys = ("ZoomX", "ZoomY", "ZoomGang", "Pan", "Tilt", "Opacity", "Pitch", "Yaw", "RotationAngle", "AnchorPointX",
            "AnchorPointY", "FlipX", "FlipY", "CropLeft", "CropRight", "CropTop", "CropBottom", "CropSoftness",
            "CropRetain", "Distortion", "CompositeMode")
    for n, x in _bad_gifs(tl):
        s, e, ss, se, pool = x.GetStart(), x.GetEnd(), x.GetSourceStartFrame(), x.GetSourceEndFrame(), x.GetMediaPoolItem()
        before = {k: x.GetProperty(k) for k in keys if x.GetProperty(k) is not None}
        assert tl.DeleteClips([x], False), "gif DeleteClips failed"
        time.sleep(GAP)
        assert mp.AppendToTimeline([{"mediaPoolItem": pool, "startFrame": ss, "endFrame": se - GIF_TRIM,
                                     "mediaType": 1, "trackIndex": n, "recordFrame": s}]), "gif append failed"
        time.sleep(GAP)
        y = [i for i in tl.GetItemListInTrack("video", n) or [] if i.GetName() == BAD_GIF and i.GetStart() == s]
        assert len(y) == 1 and y[0].GetEnd() < e, "gif re-append wrong"
        for k, v in before.items():
            if y[0].GetProperty(k) != v:
                y[0].SetProperty(k, v)
                time.sleep(0.2)
        assert all(y[0].GetProperty(k) == v for k, v in before.items()), "gif props differ"


def _find_timeline(p, name):
    """Timeline by name, or None. `GetTimelineCount()` transiently returns None right after a long render batch, so
    never use it as an arithmetic operand without a guard (that crash aborted the __cover_tmp cleanup once)."""
    try:
        n = p.GetTimelineCount() or 0
    except TypeError:
        n = 0
    for i in range(1, n + 1):
        t = p.GetTimelineByIndex(i)
        if t is not None and t.GetName() == name:
            return t
    return None


def safe(name: str) -> str:
    return re.sub(r'[\\/:*?"<>|]', "", name).strip()


def cover_path_for(timeline_name: str, vdo: str = VDO) -> str:
    return f"{vdo}/{timeline_name}.jpg"


def plan_jobs(names, prefer_variant=True):
    names = [n for n in names if "archived" not in n and TMP not in n]
    have = set(names)
    jobs, seen = [], set()
    for n in names:
        base = n[: -len(VARIANT)] if n.endswith(VARIANT) else n
        if base in seen:
            continue
        seen.add(base)
        tl = base + VARIANT if prefer_variant and (base + VARIANT) in have else (base if base in have else n)
        jobs.append({"timeline": tl, "out_name": safe(base), "vertical": base.endswith("_9x16")})
    return jobs


def select_jobs(names, cover_files, prefer_variant=True):
    """Jobs whose out_name has a matching <out_name>.jpg; second value lists timelines skipped for lack of a cover."""
    jobs = plan_jobs(names, prefer_variant)
    have = set(cover_files)
    return ([j for j in jobs if j["out_name"] + ".jpg" in have],
            [j["out_name"] for j in jobs if j["out_name"] + ".jpg" not in have])


def assert_unique_out_names(per_project):
    seen = {}
    for proj, jobs in per_project.items():
        for j in jobs:
            if j["out_name"] in seen:
                raise ValueError(f"duplicate output name {j['out_name']!r}: {seen[j['out_name']]} and {proj}")
            seen[j["out_name"]] = proj


def _arg(argv, flag, default=None):
    return argv[argv.index(flag) + 1] if flag in argv else default


def ensure_project(pm, name):
    cur = pm.GetCurrentProject()
    if cur is not None and cur.GetName() == name:
        return cur
    if cur is not None and not cur.GetName().startswith("Untitled"):  # untitled: nothing to save, avoid name dialog
        assert pm.SaveProject(), "SaveProject failed before switching"
        assert pm.CloseProject(cur), "CloseProject failed"
        time.sleep(GAP * 2)
    cur = pm.LoadProject(name)
    assert cur is not None, f"LoadProject({name!r}) failed - open Projects/Tygarina/2026-09-30 in Project Manager first"
    time.sleep(GAP * 3)
    assert cur.GetName() == name
    return cur


def _probe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                          "stream=codec_type,codec_name,width,height,r_frame_rate:format=duration",
                          "-of", "json", str(path)], capture_output=True, text=True, encoding="utf-8")
    return json.loads(out.stdout)


def _output_matches(out_name):
    return sorted(p for p in Path(VDO).glob(out_name + ".*")
                  if p.is_file() and p.suffix.lower() not in (".jpg", ".ini", ".db"))


def _find_output(out_name):
    hits = _output_matches(out_name)
    return hits[0] if len(hits) == 1 else None


def verify_one(j, covers=VDO, scratch=None):
    """Return read-only output-QC errors for one planned export."""
    hits = _output_matches(j["out_name"])
    if not hits:
        return ["missing/empty"]
    if len(hits) > 1:
        return ["ambiguous outputs: " + ", ".join(p.name for p in hits)]
    f = hits[0]
    if f.stat().st_size == 0:
        return ["missing/empty"]
    try:
        info = _probe(f)
        kinds = {s["codec_type"] for s in info["streams"]}
        v = next((s for s in info["streams"] if s["codec_type"] == "video"), {})
        dims = (v.get("width"), v.get("height"))
        want = (1080, 1920) if j["vertical"] else (1920, 1080)
        dur = float(info["format"]["duration"])
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        return [f"ffprobe failed: {exc}"]
    errs = []
    if not {"video", "audio"} <= kinds:  # .mov also carries a "data" timecode stream
        errs.append(f"streams {kinds}")
    if dims != want:
        errs.append(f"dims {dims} != {want}")
    if abs(dur - j["dur_s"]) > 0.15:
        errs.append(f"dur {dur:.2f} != {j['dur_s']:.2f}")
    if j["vertical"] and not errs:
        cover = Path(cover_path_for(j["out_name"], covers))
        if not cover.is_file():
            return ["cover missing"]
        scratch = Path(scratch or OUT / "verify")
        scratch.mkdir(parents=True, exist_ok=True)
        png = scratch / f"{safe(j['out_name'])}_first.png"
        try:
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(f), "-map", "0:v:0", "-frames:v", "1", str(png)],
                           check=True, capture_output=True)
            r = subprocess.run(["ffmpeg", "-i", str(png), "-i", str(cover), "-lavfi",
                                "[0:v]scale=1080:1920[a];[1:v]scale=1080:1920[b];[a][b]ssim", "-f", "null", "-"],
                               capture_output=True, text=True, encoding="utf-8", check=True)
        except (OSError, subprocess.CalledProcessError) as exc:
            return [f"cover comparison failed: {exc}"]
        m = re.search(r"All:([\d.]+)", r.stderr)
        ssim = float(m.group(1)) if m else 0.0
        if ssim < 0.9:
            errs.append(f"cover ssim {ssim:.3f}")
    return errs


def verified_completed_names(done_file, jobs, covers=VDO):
    """Only trust an output when its recorded Resolve job completed and its media passes QC."""
    completed = set()
    if not done_file.is_file():
        return set()
    for line in done_file.read_text(encoding="utf-8").splitlines():
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        if record.get("status") == "Complete" and record.get("out_name"):
            completed.add(record["out_name"])
    scratch = OUT / "verify"
    verified = set()
    for job in jobs:
        if job["out_name"] in completed and not verify_one(job, covers, scratch):
            verified.add(job["out_name"])
    return verified


def verify(jobs_file, covers=VDO):
    jobs = json.loads(jobs_file.read_text(encoding="utf-8"))
    scratch = OUT / "verify"
    bad = 0
    for j in jobs:
        errs = verify_one(j, covers, scratch)
        print(("PASS " if not errs else "FAIL ") + j["out_name"], errs or "", flush=True)
        bad += bool(errs)
    print(f"{len(jobs) - bad}/{len(jobs)} pass")
    return bad == 0


def main():
    global VDO, PROJECT, PRESET, OUT
    argv = sys.argv[1:]
    covers = _arg(argv, "--covers", VDO)  # folder holding the <timeline>.jpg covers
    VDO = _arg(argv, "--out", covers)  # render destination (default: same folder as the covers)
    PROJECT = _arg(argv, "--project", PROJECT)
    PRESET = _arg(argv, "--preset", PRESET)
    OUT = ROOT / "exports" / "final-export" / safe(PROJECT)
    if "--verify" in argv:
        sys.exit(0 if verify(OUT / "jobs.json", covers) else 1)

    from scripts.resolve_common import connect_resolve, preserved_state

    r = connect_resolve()
    with preserved_state(r):  # hands the user's original project/timeline/page back at the end
        _run(r, argv, covers)


def _run(r, argv, covers):
    from scripts.backup_drp import export_verified

    apply = "--apply" in argv
    limit = int(_arg(argv, "--limit")) if "--limit" in argv else None
    only = set(_arg(argv, "--only").split(",")) if "--only" in argv else None
    jobs_file = OUT / "jobs.json"
    pm = r.GetProjectManager()
    p = ensure_project(pm, PROJECT)
    mp = p.GetMediaPool()
    tls = {p.GetTimelineByIndex(i).GetName(): p.GetTimelineByIndex(i) for i in range(1, p.GetTimelineCount() + 1)}
    if "--require-cover" in argv:
        cover_files = {f.name for f in Path(covers).glob("*.jpg")}
        jobs, no_cover = select_jobs(list(tls), cover_files)
        print(f"{len(no_cover)} timelines without cover (skipped):", no_cover, flush=True)
        OUT.mkdir(parents=True, exist_ok=True)
        (OUT / "no_cover.json").write_text(json.dumps(no_cover, ensure_ascii=False, indent=1), encoding="utf-8")
    else:
        jobs = plan_jobs(list(tls))
    if only:
        jobs = [j for j in jobs if j["out_name"] in only]
    if limit:
        jobs = jobs[:limit]
    print(f"{len(jobs)} jobs ({sum(j['vertical'] for j in jobs)} vertical)", flush=True)
    prev = {x["out_name"]: x for x in json.loads(jobs_file.read_text(encoding="utf-8"))} if jobs_file.exists() else {}
    completed = verified_completed_names(OUT / "done.jsonl", jobs, covers)
    ambiguous = [j["out_name"] for j in jobs if len(_output_matches(j["out_name"])) > 1]
    if ambiguous:
        raise RuntimeError("Multiple output files share a planned stem; resolve the ambiguity manually before rerunning: "
                           + ", ".join(ambiguous))
    existing = [j for j in jobs if _output_matches(j["out_name"])]
    unverified = [j["out_name"] for j in existing if j["out_name"] not in completed]
    if unverified:
        raise RuntimeError("Existing output(s) lack a recorded Complete job or failed QC; inspect and move/delete them manually before rerunning: "
                           + ", ".join(unverified))
    skipped = [j["out_name"] for j in existing if j["out_name"] in completed]
    jobs = [j for j in jobs if j["out_name"] not in skipped]  # already rendered earlier (resume)
    print("skipping existing outputs:", len(skipped), flush=True)
    for j in jobs:
        if j["vertical"]:
            assert Path(cover_path_for(j["out_name"], covers)).is_file(), f"cover missing: {j['out_name']}"
    if not jobs:
        print("nothing to do", flush=True)
        return
    if not apply:
        for j in jobs[:8]:
            print(" ", j)
        OUT.mkdir(parents=True, exist_ok=True)
        (OUT / "plan.json").write_text(json.dumps([x["out_name"] for x in jobs], ensure_ascii=False, indent=1),
                                       encoding="utf-8")
        return
    assert PRESET in (p.GetRenderPresetList() or []), f"preset {PRESET} missing"
    OUT.mkdir(parents=True, exist_ok=True)
    bk = ROOT / "backups" / f"2026-10-10-before-final-export-{safe(PROJECT)}.drp"
    if not bk.exists():
        print("backup bytes:", export_verified(pm, p, bk), flush=True)

    queued = []
    pool_covers = {}
    vert = [j for j in jobs if j["vertical"]]
    if vert:
        root = mp.GetRootFolder()
        folder = next((f for f in root.GetSubFolderList() if f.GetName() == "P2 Covers"), None) \
            or mp.AddSubFolder(root, "P2 Covers")
        assert folder, "cannot create bin"
        mp.SetCurrentFolder(folder)
        time.sleep(GAP)
        have = {c.GetName(): c for c in folder.GetClipList() or []}
        need = [cover_path_for(j["out_name"], covers) for j in vert if (j["out_name"] + ".jpg") not in have]
        if need:
            assert mp.ImportMedia(need), "ImportMedia failed"
            time.sleep(GAP)
            have = {c.GetName(): c for c in folder.GetClipList() or []}
        for j in vert:
            assert (j["out_name"] + ".jpg") in have, f"cover not in pool: {j['out_name']}"
            pool_covers[j["out_name"]] = have[j["out_name"] + ".jpg"]
    src_keep = tls[jobs[0]["timeline"]]
    cur = {}
    try:
      for j in jobs:
        cur = j
        src = tls[j["timeline"]]
        tl = src
        j["dur_s"] = (src.GetEndFrame() - src.GetStartFrame()) / float(src.GetSetting("timelineFrameRate"))
        p.SetCurrentTimeline(src)
        time.sleep(GAP)
        bad = _bad_gifs(src)
        if j["vertical"] or bad:
            tl = src.DuplicateTimeline(j["out_name"] + TMP)
            assert tl, "DuplicateTimeline failed"
            time.sleep(GAP)
            p.SetCurrentTimeline(tl)
            time.sleep(GAP)
            j["tmp"] = tl.GetName()
            if bad:
                _trim_gif_tails(p, mp, tl)
        if j["vertical"]:
            before = {n: len(tl.GetItemListInTrack("video", n) or []) for n in range(1, tl.GetTrackCount("video") + 1)}
            assert tl.AddTrack("video"), "AddTrack failed"
            time.sleep(GAP)
            top = tl.GetTrackCount("video")
            start = tl.GetStartFrame()
            # stills ignore startFrame/endFrame (land as 300 frames); pool mark in/out sets the real length
            cov = pool_covers[j["out_name"]]
            assert cov.SetMarkInOut(0, COVER_FRAMES - 1, "video"), "SetMarkInOut failed"
            assert mp.AppendToTimeline([{"mediaPoolItem": cov, "mediaType": 1, "trackIndex": top,
                                         "recordFrame": start}]), "cover append failed"
            cov.ClearMarkInOut("all")
            time.sleep(GAP)
            it = tl.GetItemListInTrack("video", top) or []
            assert len(it) == 1 and it[0].GetStart() == start and it[0].GetEnd() == start + COVER_FRAMES, \
                f"cover placement wrong: {[(x.GetStart(), x.GetEnd()) for x in it]}"
            after = {n: len(tl.GetItemListInTrack("video", n) or []) for n in before}
            assert after == before, "existing video tracks changed"
        assert p.GetCurrentTimeline().GetUniqueId() == tl.GetUniqueId(), "activate failed"
        assert p.LoadRenderPreset(PRESET), "LoadRenderPreset failed"
        assert p.SetRenderSettings({"SelectAllFrames": True, "TargetDir": VDO, "CustomName": j["out_name"],
                                    **SUBTITLE_BURN_IN}), "SetRenderSettings failed"
        jid = p.AddRenderJob()
        assert jid, f"AddRenderJob failed {j['out_name']}"
        j["job"] = jid
        queued.append(j)
        jobs_file.write_text(json.dumps(list({**prev, **{q["out_name"]: q for q in queued}}.values()),
                                             ensure_ascii=False, indent=1), encoding="utf-8")
        print("JOB", j["out_name"], jid, flush=True)
        time.sleep(0.5)
    except Exception:
        for jj in queued + [cur]:
            if jj.get("job"):
                p.DeleteRenderJob(jj["job"])
            if jj.get("tmp"):
                t = next((p.GetTimelineByIndex(i) for i in range(1, p.GetTimelineCount() + 1)
                          if p.GetTimelineByIndex(i).GetName() == jj["tmp"]), None)
                if t:
                    p.SetCurrentTimeline(src_keep)
                    time.sleep(GAP)
                    mp.DeleteTimelines([t])
        raise
    assert p.StartRendering([j["job"] for j in queued]), "StartRendering failed"
    pending = {j["job"]: j for j in queued}
    done = OUT / "done.jsonl"
    while pending:
        time.sleep(6)
        for jid in list(pending):
            st = p.GetRenderJobStatus(jid) or {}
            s = st.get("JobStatus")
            if s in ("Complete", "Failed", "Cancelled"):
                j = pending.pop(jid)
                j["status"] = s
                with done.open("a", encoding="utf-8") as fh:
                    fh.write(json.dumps(j, ensure_ascii=False) + "\n")
                print("DONE", j["out_name"], s, flush=True)
    for j in queued:
        if j.get("tmp") and j["status"] == "Complete":
            t = _find_timeline(p, j["tmp"])
            if t:
                mp.DeleteTimelines([t])
                time.sleep(GAP)
    assert pm.SaveProject(), "SaveProject failed"
    print("ALL DONE", len(queued), flush=True)


if __name__ == "__main__":
    main()
