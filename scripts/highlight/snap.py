"""Snap cut times: python snap.py <source_id> <t|in:t|out:t> ...
`in:`/`out:` move a cut that falls inside a sentence to that sentence's start/end (needs `pipeline.py fulltext`);
otherwise, and for plain seconds, snap to the nearest silence in the level-untouched wav."""
import pathlib, re, subprocess, sys
import config
from features import wav_path
from windows import snap_to_sentence, snap_to_silence

def silences_near(wav: pathlib.Path, t: float, radius: float = 3.0):
    start = max(0.0, t - radius - 2)
    p = subprocess.run([config.FFMPEG, "-hide_banner", "-ss", f"{start:.3f}", "-t", f"{2 * radius + 4:.3f}", "-i", str(wav),
                        "-af", "silencedetect=n=-35dB:d=0.4", "-f", "null", "-"], capture_output=True, text=True)
    s = [float(x) + start for x in re.findall(r"silence_start: (-?[\d.]+)", p.stderr)]
    e = [float(x) + start for x in re.findall(r"silence_end: ([\d.]+)", p.stderr)]
    return list(zip(s, e))

def snap_in_wav(wav: pathlib.Path, t: float, radius: float = 3.0) -> float:
    return round(snap_to_silence(t, silences_near(pathlib.Path(wav), t, radius), radius), 2)

def snap_arg(arg: str, sentences, wav) -> tuple[float, str]:
    """-> (snapped seconds, how): 'sentence' when moved to a sentence edge, else 'silence'."""
    edge, _, num = arg.rpartition(":")
    t = float(num)
    if edge in ("in", "out") and sentences:
        s = snap_to_sentence(t, sentences, edge)
        if s is not None:
            return s, "sentence"
    return snap_in_wav(wav, t), "silence"

if __name__ == "__main__":
    import fulltext
    sid = sys.argv[1]
    sents = fulltext.load_sentences(sid)
    if any(":" in a for a in sys.argv[2:]) and not sents:
        print(f"note: no transcripts/{sid}.sentences.json; run `pipeline.py fulltext` for sentence snapping")
    for a in sys.argv[2:]:
        t, how = snap_arg(a, sents, wav_path(sid))
        print(a, "->", t, f"({how})")
