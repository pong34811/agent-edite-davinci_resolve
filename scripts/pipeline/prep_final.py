import sys, json, os, time, subprocess, re
sys.path.insert(0, os.environ["TMPDIR"])
from rlib import *
T = os.environ["TMPDIR"]
FF = os.environ.get("FFMPEG_DIR", "")
tl = {d["i"]: d for d in json.load(open(os.path.join(W, "timelines.json"), encoding="utf-8"))}
gm = json.load(open(os.path.join(T, "gif_meta.json"), encoding="utf-8"))
def cache(name):
    f = os.path.join(T, name); return (json.load(open(f, encoding="utf-8")) if os.path.exists(f) else {}), f
def lufs(path, ss=0, t=60):
    o = subprocess.run([os.path.join(FF, "ffmpeg"), "-hide_banner", "-nostats", "-ss", str(ss), "-t", str(t), "-i", path, "-vn", "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True, errors="replace").stderr
    m = re.findall(r"I:\s+(-?[\d.]+) LUFS", o); return float(m[-1]) if m else None
def loud(path):
    o = subprocess.run([os.path.join(FF, "ffmpeg"), "-hide_banner", "-i", path, "-vn", "-af", "loudnorm=print_format=json", "-f", "null", "-"], capture_output=True, text=True, errors="replace").stderr
    m = re.search(r'"input_i"\s*:\s*"(-?[\d.]+)"', o); return float(m.group(1)) if m else None
def dur(path):
    return float(subprocess.run([os.path.join(FF, "ffprobe"), "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path], capture_output=True, text=True).stdout.strip())
bgc, bgf = cache("bgm_cache.json"); sfc, sff = cache("sfx_cache.json")
allbg = [f for f in os.listdir(B) if f.lower().endswith((".mp3", ".wav", ".m4a")) and "10292" not in f]
for f in allbg:
    if f not in bgc: pth = os.path.join(B, f); bgc[f] = dict(dur=dur(pth), lufs=loud(pth) if dur(pth) < 400 else None)
json.dump(bgc, open(bgf, "w", encoding="utf-8"), ensure_ascii=False)
cands = sorted([f for f, m in bgc.items() if m["lufs"] is not None and m["dur"] > 0]);
pref = ["NCSน่ารัก.mp3", "2025-02-04_-_Wishing_Well_-_www.FesliyanStudios.com_.mp3", "FREE BGM 4 LOOP.wav", "payday.mp3", "[no copyright music] -.mp3", "aphextwin.m4a"]
pref = [f for f in pref if f in bgc]; off = int(sys.argv[1]) if len(sys.argv) > 1 else 0
bad = []
for N in sorted(tl):
    pl = json.load(open(os.path.join(W, "plan_T%d.json" % N), encoding="utf-8")); end = tl[N]["end"]; secs = (end - tl[N]["start"]) / tl[N]["fps"]
    cues = {c[0] for c in tl[N]["cues"]}; sf = sorted(pl["sfx"], key=lambda x: x["frame"]); gf = sorted(pl["gif"], key=lambda x: x["frame"])
    for x in sf + gf:
        if x["frame"] not in cues: bad.append(f"T{N} frame {x['frame']} not cue")
    for x in sf:
        if not os.path.exists(os.path.join(S, x["file"])): bad.append("nosfx " + x["file"])
    for x in gf:
        if x["file"] not in gm: bad.append("nogif " + x["file"])
        elif not (gm[x["file"]]["dur"] >= 1.5 and gm[x["file"]]["nb"] >= 8): bad.append(f"T{N} short gif {x['file']}")
    if any(b["frame"] - a["frame"] < 420 for a, b in zip(sf, sf[1:])) or any(b["frame"] - a["frame"] < 600 for a, b in zip(gf, gf[1:])): bad.append(f"T{N} spacing")
    if (sf and (sf[0]["frame"] <= 120 or sf[-1]["frame"] > end - 150)) or (gf and (gf[0]["frame"] <= 200 or gf[-1]["frame"] >= end - 300)): bad.append(f"T{N} range")
    if len({x["file"] for x in sf}) != len(sf) or len({x["file"] for x in gf}) != len(gf): bad.append(f"T{N} dup")
    t = tl_by_id(tl[N]["id"]); it = t.GetItemListInTrack("video", 1)[0]; mpi = it.GetMediaPoolItem(); spath = mpi.GetClipProperty("File Path")
    sp = lufs(spath, it.GetLeftOffset() / tl[N]["fps"], secs)
    for x in sf:
        if x["file"] not in sfc: pth = os.path.join(S, x["file"]); sfc[x["file"]] = dict(dur=dur(pth), lufs=loud(pth))
        x["dur"] = sfc[x["file"]]["dur"]; x["lufs"] = sfc[x["file"]]["lufs"]
        x["gain"] = round(max(-40, min(6, (sp - 3) - x["lufs"])), 1) if x["lufs"] is not None else -12.0
    for x in gf: m = gm[x["file"]]; x["w"], x["h"], x["fps"], x["nb"] = m["w"], m["h"], m["fps"], m["nb"]
    ok = [f for f in pref if bgc[f]["dur"] >= secs + 1] or [f for f in cands if bgc[f]["dur"] >= secs + 1]
    pl["bgm"] = ok[(N - 1 + off) % len(ok)]; pl["bgm_lufs"] = bgc[pl["bgm"]]["lufs"]; pl["speech_lufs"] = sp
    pl["bgm_gain"] = round(max(-60, min(0, (sp - 20) - pl["bgm_lufs"])), 1)
    json.dump(pl, open(os.path.join(W, "final_T%d.json" % N), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(N, "secs", secs, "speech", sp, "bgm", pl["bgm"][:14], pl["bgm_gain"], "sfx", [x["gain"] for x in sf], "gifs", [x["file"][:14] for x in gf], flush=True)
json.dump(sfc, open(sff, "w", encoding="utf-8"), ensure_ascii=False)
print("PROBLEMS:", bad or "none")
