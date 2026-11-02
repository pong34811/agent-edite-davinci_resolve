import json, math, wave, glob
import numpy as np
import config, snap

def _wav(path, parts, sr=16000):
    out = []
    for secs, amp in parts:
        t = np.arange(int(sr * secs)) / sr
        out.append((amp * np.sin(2 * np.pi * 440 * t) * 32767).astype(np.int16))
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes(np.concatenate(out).tobytes())

def test_snap_in_wav_moves_to_silence_midpoint(tmp_path):
    p = tmp_path / "a.wav"; _wav(p, [(10, 0.5), (1, 0.0), (10, 0.5)])
    assert abs(snap.snap_in_wav(p, 9.4) - 10.5) < 0.2

def test_snap_in_wav_keeps_time_without_silence(tmp_path):
    p = tmp_path / "b.wav"; _wav(p, [(20, 0.5)])
    assert snap.snap_in_wav(p, 9.4) == 9.4

def test_review_files_match_schema():
    inv = {r["source_id"]: r for r in json.loads((config.WORK_DIR / "inventory.json").read_text(encoding="utf-8"))}
    files = sorted(glob.glob(str(config.WORK_DIR / "review" / "v??.json")))
    assert len(files) == len(inv), f"expected one review file per video, found {len(files)}"
    ids = set()
    for f in files:
        sid = f.replace("\\", "/").split("/")[-1][:-5]
        items = json.loads(open(f, encoding="utf-8").read())
        assert 4 <= len(items) <= 8, f"{sid}: {len(items)} clips"
        spans = []
        for c in items:
            assert {"id", "source_id", "start_s", "end_s", "category", "title_th", "reason", "score"} <= set(c)
            assert c["source_id"] == sid and c["id"].startswith(sid + "-") and c["id"] not in ids
            ids.add(c["id"])
            assert c["category"] in config.CATEGORIES
            assert config.CLIP_MIN_S <= c["end_s"] - c["start_s"] <= config.CLIP_MAX_S, c
            assert 0 <= c["start_s"] and c["end_s"] <= inv[sid]["duration_s"], c
            assert c["title_th"].strip() and c["reason"].strip() and 0 <= c["score"] <= 1
            spans.append((c["start_s"], c["end_s"]))
        spans.sort()
        assert all(spans[i][1] <= spans[i + 1][0] for i in range(len(spans) - 1)), f"{sid}: overlapping clips"
