import subprocess
import config, inventory

def _make(path, secs):
    subprocess.run([config.FFMPEG, "-v", "error", "-y", "-f", "lavfi", "-i", f"testsrc=duration={secs}:size=320x180:rate=30",
                    "-f", "lavfi", "-i", f"sine=frequency=440:duration={secs}", "-shortest", "-c:v", "libx264", "-c:a", "aac", str(path)], check=True)

def test_build_assigns_sorted_ids_and_probes(tmp_path):
    _make(tmp_path / "【ทดสอบ】b.mp4", 2)
    _make(tmp_path / "a เสียง.mp4", 3)
    (tmp_path / "notes.txt").write_text("x")
    rows = inventory.build(tmp_path)
    assert [r["source_id"] for r in rows] == ["v01", "v02"]
    assert rows[0]["file"].endswith("a เสียง.mp4")
    assert all(r["fps"] == 30 and r["duration_s"] > 1.5 and r["codec"] == "h264" for r in rows)
    assert rows[0]["width"] == 320

def test_build_empty_dir_returns_empty(tmp_path):
    assert inventory.build(tmp_path) == []
