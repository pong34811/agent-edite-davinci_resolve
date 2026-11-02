"""Pass 0: list every video in INPUT_DIR with ffprobe facts -> inventory.json / inventory.md."""
import json, pathlib, subprocess
from fractions import Fraction
import config

def probe(path: pathlib.Path) -> dict:
    out = subprocess.run([config.FFPROBE, "-v", "error", "-show_entries",
                          "format=duration,size:stream=codec_type,codec_name,width,height,r_frame_rate",
                          "-of", "json", str(path)], capture_output=True, check=True).stdout
    info = json.loads(out.decode("utf-8"))
    v = next(s for s in info["streams"] if s["codec_type"] == "video")
    a = next((s for s in info["streams"] if s["codec_type"] == "audio"), {})
    fps = Fraction(v["r_frame_rate"])
    return {"file": str(path), "codec": v["codec_name"], "width": v["width"], "height": v["height"],
            "fps": int(fps) if fps.denominator == 1 else float(fps),
            "duration_s": float(info["format"]["duration"]), "size_bytes": int(info["format"]["size"]),
            "audio_codec": a.get("codec_name")}

def build(input_dir: pathlib.Path | None = None) -> list[dict]:
    input_dir = pathlib.Path(input_dir or config.INPUT_DIR)
    files = sorted(p for p in input_dir.iterdir() if p.is_file() and p.suffix.lower() in config.VIDEO_EXTS)
    rows = []
    for i, p in enumerate(files, 1):
        r = probe(p); r["source_id"] = f"v{i:02d}"; rows.append(r)
    return rows

def _hms(s: float) -> str:
    s = int(s); return f"{s // 3600}:{s % 3600 // 60:02d}:{s % 60:02d}"

def main() -> None:
    rows = build()
    config.WORK_DIR.mkdir(parents=True, exist_ok=True)
    (config.WORK_DIR / "inventory.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = ["| source_id | file | codec | resolution | fps | duration | size GB |", "|---|---|---|---|---|---|---|"]
    for r in rows:
        lines.append(f"| {r['source_id']} | {pathlib.Path(r['file']).name} | {r['codec']} | {r['width']}x{r['height']} | {r['fps']} | {_hms(r['duration_s'])} | {r['size_bytes']/1e9:.2f} |")
    (config.WORK_DIR / "inventory.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))

if __name__ == "__main__":
    main()
