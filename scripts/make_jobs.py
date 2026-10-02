"""Build per-project SDD workspaces (jobs.json) from read-only discovery JSON."""
import json, os, sys
ROOT = ".superpowers/sdd"
def build(slug):
    d = json.load(open(f"{ROOT}/discovery/{slug}.json", encoding="utf-8"))
    W = f"{ROOT}/2026-10-02-{slug}-subtitles"
    new = not os.path.exists(f"{W}/jobs.json")
    for sub in ("audio", "asr", "srt", "backup"):
        os.makedirs(f"{W}/{sub}", exist_ok=True)
    jobs = []
    for t in d["timelines"]:
        v = [i for i in t["items"] if i["track_type"] == "video"]
        assert len(v) == 1 and t["start_frame"] == 0 and t["tracks"]["subtitle"] == 0, t["name"]
        c = v[0]; n = t["end_frame"] - t["start_frame"]
        jobs.append(dict(job=t["index"], timeline_index=t["index"], timeline_name=t["name"], timeline_id=t["id"],
                         source=c["path"], source_start_frame=c["src_start"], source_start_s=c["src_start"] / 60,
                         duration_frames=n, duration_s=n / 60, fps=60))
    json.dump(jobs, open(f"{W}/jobs.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    if new and not os.path.exists(f"{W}/subtitle_rules.json"):
        # NEW workspaces opt in to the ๆ-repeat word count (subtitle_srt.job_rules); existing
        # workspaces are never touched, so an in-progress project keeps its rules.
        json.dump({"count_maiyamok": True}, open(f"{W}/subtitle_rules.json", "w", encoding="utf-8"), indent=1)
    hdr = f"# SDD ledger — plan: docs/superpowers/plans/2026-10-02-remaining-projects-subtitles.md\nProject: {d['project']}; original active timeline {d['active_timeline'].get('id')}\n"
    if not os.path.exists(f"{W}/progress.md"):
        open(f"{W}/progress.md", "w", encoding="utf-8").write(hdr)
    return W, len(jobs)
if __name__ == "__main__":
    for s in sys.argv[1:]:
        print(s, *build(s))
