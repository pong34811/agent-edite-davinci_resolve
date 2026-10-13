import os, json, subprocess
T = os.environ["TMPDIR"]; W = os.environ["PW"]
FF = os.environ.get("FFMPEG_DIR", ""); G = os.environ.get("GIF_DIR", r"G:\My Drive\Projects.gif"); S = os.environ.get("SFX_DIR", r"G:\My Drive\Projects.1_sfx")
cache = os.path.join(T, "gif_meta.json")
if not os.path.exists(cache):
    meta = {}
    for f in sorted(x for x in os.listdir(G) if x.lower().endswith(".gif")):
        o = json.loads(subprocess.run([os.path.join(FF, "ffprobe"), "-v", "error", "-select_streams", "v:0", "-count_frames", "-show_entries", "stream=width,height,r_frame_rate,nb_read_frames", "-show_entries", "format=duration", "-of", "json", os.path.join(G, f)], capture_output=True, text=True, errors="replace").stdout)
        s = o["streams"][0]; n, d = s["r_frame_rate"].split("/"); meta[f] = dict(w=s["width"], h=s["height"], fps=float(n) / float(d), nb=int(s["nb_read_frames"]), dur=float(o["format"]["duration"]))
    json.dump(meta, open(cache, "w", encoding="utf-8"), ensure_ascii=False)
meta = json.load(open(cache, encoding="utf-8")); good = sorted(f for f, m in meta.items() if m["dur"] >= 1.5 and m["nb"] >= 8)
open(os.path.join(T, "gif_usable.txt"), "w", encoding="utf-8").write("\n".join(good)); print("usable gifs", len(good), "of", len(meta))
sfx = sorted(f for f in os.listdir(S) if f.lower().endswith((".mp3", ".wav", ".m4a", ".ogg"))); open(os.path.join(T, "sfx_all.txt"), "w", encoding="utf-8").write("\n".join(sfx))
tl = json.load(open(os.path.join(W, "timelines.json"), encoding="utf-8"))
for d in tl:
    open(os.path.join(W, "cues_T%d.txt" % d["i"]), "w", encoding="utf-8").write("# Timeline %d %s fps=%s frames 0-%d\n# start_frame end_frame text\n" % (d["i"], d["name"], d["fps"], d["end"]) + "\n".join("%d %d %s" % tuple(c) for c in d["cues"]))
print("cue files", len(tl), [d["end"] for d in tl])
