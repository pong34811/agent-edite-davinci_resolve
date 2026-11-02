"""Snap a cut time to the nearest silence in the level-untouched wav: python snap.py <source_id> <seconds> [<seconds> ...]"""
import pathlib, re, subprocess, sys
import config
from features import wav_path
from windows import snap_to_silence

def silences_near(wav: pathlib.Path, t: float, radius: float = 3.0):
    start = max(0.0, t - radius - 2)
    p = subprocess.run([config.FFMPEG, "-hide_banner", "-ss", f"{start:.3f}", "-t", f"{2 * radius + 4:.3f}", "-i", str(wav),
                        "-af", "silencedetect=n=-35dB:d=0.4", "-f", "null", "-"], capture_output=True, text=True)
    s = [float(x) + start for x in re.findall(r"silence_start: (-?[\d.]+)", p.stderr)]
    e = [float(x) + start for x in re.findall(r"silence_end: ([\d.]+)", p.stderr)]
    return list(zip(s, e))

def snap_in_wav(wav: pathlib.Path, t: float, radius: float = 3.0) -> float:
    return round(snap_to_silence(t, silences_near(pathlib.Path(wav), t, radius), radius), 2)

if __name__ == "__main__":
    sid = sys.argv[1]
    for t in sys.argv[2:]:
        print(t, "->", snap_in_wav(wav_path(sid), float(t)))
