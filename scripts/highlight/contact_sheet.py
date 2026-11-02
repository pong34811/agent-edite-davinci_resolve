"""6-frame (3x2) contact sheet per time range; fast input-seek, 320x180 tiles with timestamp burned in."""
import io, json, pathlib, subprocess
from concurrent.futures import ThreadPoolExecutor
from PIL import Image, ImageDraw
import config

TW, TH = 320, 180

def _hms(s: float) -> str:
    s = int(s); return f"{s // 3600}:{s % 3600 // 60:02d}:{s % 60:02d}"

def _frame(src: pathlib.Path, t: float) -> Image.Image:
    p = subprocess.run([config.FFMPEG, "-v", "error", "-ss", f"{t:.2f}", "-i", str(src), "-frames:v", "1",
                        "-vf", f"scale={TW}:{TH}", "-f", "image2pipe", "-vcodec", "png", "-"], capture_output=True)
    return Image.open(io.BytesIO(p.stdout)).convert("RGB") if p.stdout else Image.new("RGB", (TW, TH), "black")

def make_from_file(src, start_s: float, end_s: float, out: pathlib.Path, n: int = 6) -> pathlib.Path:
    src = pathlib.Path(src); out = pathlib.Path(out); out.parent.mkdir(parents=True, exist_ok=True)
    sheet = Image.new("RGB", (TW * 3, TH * 2))
    for i in range(n):
        t = start_s + (end_s - start_s) * (i + 0.5) / n
        tile = _frame(src, t); ImageDraw.Draw(tile).text((4, 4), _hms(t), fill="yellow")
        sheet.paste(tile, ((i % 3) * TW, (i // 3) * TH))
    sheet.save(out, quality=80)
    return out

def make(source_id: str, start_s: float, end_s: float, n: int = 6) -> pathlib.Path:
    inv = {r["source_id"]: r for r in json.loads((config.WORK_DIR / "inventory.json").read_text(encoding="utf-8"))}
    out = config.WORK_DIR / "frames" / f"{source_id}_{int(start_s):06d}.jpg"
    return out if out.exists() else make_from_file(inv[source_id]["file"], start_s, end_s, out, n)

def run_all() -> None:
    jobs = []
    for sc in sorted((config.WORK_DIR / "scores").glob("*.top.json")):
        sid = sc.name.split(".")[0]
        jobs += [(sid, w[0], w[1]) for w in json.loads(sc.read_text(encoding="utf-8"))]
    with ThreadPoolExecutor(8) as ex:
        list(ex.map(lambda j: make(*j), jobs))
    print(len(jobs), "sheets", flush=True)
