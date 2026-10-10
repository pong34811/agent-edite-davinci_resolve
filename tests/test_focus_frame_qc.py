"""Synthetic-only tests for the offline focus still QC helper."""

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

from PIL import Image
import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "focus_frame_qc.py"
sys.path.insert(0, str(ROOT))

from scripts import focus_frame_qc as qc  # noqa: E402


@pytest.fixture
def scratch_dir():
    home = Path(os.environ.get("HERMES_HOME") or Path.home() / (
        "AppData/Local/hermes" if os.name == "nt" else ".hermes"
    ))
    scratch = Path(os.environ.get("TMPDIR") or home / "cache/scratch")
    scratch.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=scratch) as directory:
        yield Path(directory)


def _synthetic_png(path: Path, color, size=(80, 120)) -> Path:
    Image.new("RGB", size, color).save(path, format="PNG")
    return path


def _manifest(folder: Path, entries) -> Path:
    path = folder / "cues.json"
    path.write_text(json.dumps({"stills": entries}), encoding="utf-8")
    return path


def test_report_contains_metadata_brightness_heuristics_and_unverified_subject(scratch_dir):
    source_dir = scratch_dir / "input"
    source_dir.mkdir()
    source = _synthetic_png(source_dir / "before_001.png", (240, 90, 60))
    _synthetic_png(source_dir / "after_001.png", (0, 0, 0))
    manifest = _manifest(source_dir, [
        {"file": "before_001.png", "phase": "before", "cue": "ทดสอบ", "frame": 100,
         "subject_bbox_norm": [0.2, 0.02, 0.8, 0.9], "min_headroom_ratio": 0.04},
        {"file": "after_001.png", "phase": "after", "cue": "ทดสอบ", "frame": 120,
         "subject_bbox_norm": [0.2, 0.08, 0.8, 0.9], "min_headroom_ratio": 0.04},
    ])
    output_dir = scratch_dir / "output"
    output_dir.mkdir()
    sheet_path = output_dir / "focus-sheet-test.png"
    report_path = output_dir / "focus-report-test.json"

    payload = qc.create_qc_outputs(source_dir, sheet_path, report_path, manifest)

    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert [item["phase"] for item in report["stills"]] == ["before", "after"]
    before, after = report["stills"]
    assert before["cue"] == "ทดสอบ"
    assert before["frame"] == 100
    assert before["dimensions"] == {"width": 80, "height": 120}
    assert before["file_size_bytes"] == source.stat().st_size
    assert before["sha256"] == hashlib.sha256(source.read_bytes()).hexdigest()
    assert before["pixel_heuristics"]["status"] == "heuristic_unverified"
    assert before["pixel_heuristics"]["non_dark_pixel_fraction"] == 1.0
    assert after["pixel_heuristics"]["dark_pixel_fraction"] == 1.0
    assert before["subject_presence"]["status"] == "unverified"
    assert before["subject_presence"]["method"] is None
    assert before["crop_headroom"]["headroom_check"] == "fail"
    assert after["crop_headroom"]["headroom_check"] == "pass"
    assert payload["automatic_verdict"] == "none; visual review is required"
    with Image.open(sheet_path) as sheet:
        assert sheet.size == (qc.TILE_WIDTH * 2, qc.TILE_HEIGHT)


def test_missing_annotation_leaves_crop_headroom_unverified(scratch_dir):
    _synthetic_png(scratch_dir / "focus.png", (80, 100, 120))
    records, sheet = qc.analyze_folder(scratch_dir)
    try:
        assert records[0]["crop_headroom"]["status"] == "unverified"
        assert records[0]["subject_presence"]["status"] == "unverified"
    finally:
        sheet.close()
        records[0]["_display_image"].close()


def test_manifest_reference_and_geometry_are_validated_before_outputs(scratch_dir):
    _synthetic_png(scratch_dir / "before_001.png", (220, 80, 30))
    manifest = _manifest(scratch_dir, [
        {"file": "before_001.png", "subject_bbox_norm": [0.5, 0.4, 0.2, 0.9]}
    ])
    with pytest.raises(ValueError, match="positive area"):
        qc.analyze_folder(scratch_dir, manifest)

    missing = _manifest(scratch_dir, [{"file": "missing.png", "frame": 1}])
    with pytest.raises(ValueError, match="not found"):
        qc.analyze_folder(scratch_dir, missing)


def test_outputs_are_explicit_and_existing_paths_are_never_overwritten(scratch_dir):
    source_dir = scratch_dir / "stills"
    source_dir.mkdir()
    source = _synthetic_png(source_dir / "before_001.png", (220, 80, 30))
    sheet = scratch_dir / "sheet.png"
    report = scratch_dir / "report.json"
    report.write_text("keep me", encoding="utf-8")
    result = subprocess.run([
        sys.executable, str(SCRIPT), str(source_dir),
        "--contact-sheet", str(sheet), "--report", str(report),
    ], capture_output=True, text=True, check=False)
    assert result.returncode == 2
    assert "refusing to overwrite" in result.stderr
    assert not sheet.exists()
    assert report.read_text(encoding="utf-8") == "keep me"
    assert source.exists()


def test_cli_creates_both_outputs_and_does_not_change_source_pngs(scratch_dir):
    source_dir = scratch_dir / "stills"
    source_dir.mkdir()
    source = _synthetic_png(source_dir / "after_02.png", (20, 40, 220), (50, 70))
    source_bytes = source.read_bytes()
    output_dir = scratch_dir / "out"
    output_dir.mkdir()
    sheet = output_dir / "contact.png"
    report = output_dir / "report.json"
    result = subprocess.run([
        sys.executable, str(SCRIPT), str(source_dir),
        "--contact-sheet", str(sheet), "--report", str(report),
    ], capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stderr
    assert "stills=1" in result.stdout
    assert "subject_presence=unverified" in result.stdout
    assert sheet.is_file() and report.is_file()
    assert source.read_bytes() == source_bytes
    assert json.loads(report.read_text(encoding="utf-8"))["stills"][0]["file"] == "after_02.png"


def test_contact_sheet_cannot_be_written_inside_input_folder(scratch_dir):
    source_dir = scratch_dir / "stills"
    source_dir.mkdir()
    _synthetic_png(source_dir / "before_001.png", (220, 80, 30))
    with pytest.raises(ValueError, match="outside the input folder"):
        qc.create_qc_outputs(source_dir, source_dir / "sheet.png", scratch_dir / "report.json")

