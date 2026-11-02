import subprocess
from PIL import Image
import config, contact_sheet, packets

def test_make_from_file_is_3x2_grid_960x360(tmp_path):
    src = tmp_path / "t.mp4"
    subprocess.run([config.FFMPEG, "-v", "error", "-y", "-f", "lavfi", "-i", "testsrc=duration=20:size=640x360:rate=30",
                    "-c:v", "libx264", str(src)], check=True)
    out = contact_sheet.make_from_file(src, 2, 18, tmp_path / "s.jpg")
    assert out.exists() and Image.open(out).size == (960, 360)

def test_format_packet_has_range_transcript_and_sheet():
    txt = packets.format_packet("v01", [(3600.0, 3720.0, 0.9)],
                                [{"start": 3590.0, "end": 3595.0, "text": "ฮ่าๆๆ"}, {"start": 9000.0, "end": 9001.0, "text": "นอกช่วง"}],
                                {0: "frames/v01_003600.jpg"})
    assert "v01-w01" in txt and "1:00:00-1:02:00" in txt and "ฮ่าๆๆ" in txt and "นอกช่วง" not in txt
    assert "frames/v01_003600.jpg" in txt

def test_packet_collapses_repeated_chars_and_truncates():
    segs = [{"start": 3600.0, "end": 3601.0, "text": "สวัสดีค่า" + "า" * 500}, {"start": 3602.0, "end": 3603.0, "text": "ก" * 2 + "ข" * 400 + "x y " * 200}]
    txt = packets.format_packet("v01", [(3600.0, 3660.0, 0.5)], segs, {})
    assert "า" * 4 not in txt
    assert max(len(l) for l in txt.splitlines()) <= 260
