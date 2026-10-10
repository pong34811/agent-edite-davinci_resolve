#!/usr/bin/env python3
"""Create an offline contact sheet and metadata report for VTuber focus stills.

The helper reads PNGs from one folder and writes exactly two caller-selected
outputs. Pixel measurements are simple brightness heuristics; they do not
recognize a face, head, avatar, hands, captions, or gameplay. Optional manifest
annotations can provide expected subject bounds for geometric crop/headroom
checks, but those checks only evaluate the supplied annotation.

Manifest example::

    {
      "stills": [
        {"file": "before_001.png", "phase": "before", "cue": "hello",
         "frame": 120,
         "subject_bbox_norm": [0.2, 0.04, 0.8, 0.9],
         "min_headroom_ratio": 0.03}
      ]
    }

`subject_bbox_norm` is [left, top, right, bottom] relative to the image; values
outside 0..1 can represent the expected full subject box crossing the frame.

Example::

    python scripts/focus_frame_qc.py ./qc-stills \
        --contact-sheet ./qc-output/focus-contact-sheet.png \
        --report ./qc-output/focus-report.json \
        --manifest ./qc-stills/cues.json

Output paths must be explicit, have existing parent folders, and must not
already exist. The contact sheet must be outside the input folder.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
from io import BytesIO
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

try:
    from PIL import Image, ImageDraw, ImageFont, ImageOps
except ImportError:  # pragma: no cover - dependency guidance only
    raise SystemExit("Pillow is required and must already be installed.")


SCHEMA_VERSION = "1.0"
LUMINANCE_DARK_THRESHOLD = 12
TILE_WIDTH = 420
IMAGE_BOX_HEIGHT = 330
LABEL_HEIGHT = 110
TILE_HEIGHT = IMAGE_BOX_HEIGHT + LABEL_HEIGHT
FONT_CANDIDATES = (
    "C:/Windows/Fonts/tahoma.ttf",
    "C:/Windows/Fonts/arial.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/Library/Fonts/Arial.ttf",
)


def _natural_key(value: str) -> List[Any]:
    return [
        (1, int(part)) if part.isdigit() else (0, part.casefold())
        for part in re.split(r"(\d+)", value)
    ]


def _infer_phase(filename: str) -> Optional[str]:
    match = re.search(r"(?:^|[^A-Za-z0-9])(before|after)(?=$|[^A-Za-z0-9])",
                      Path(filename).stem, re.IGNORECASE)
    return match.group(1).lower() if match else None


def _validate_bbox(value: Any, filename: str) -> Tuple[float, float, float, float]:
    if not isinstance(value, (list, tuple)) or len(value) != 4:
        raise ValueError(
            "subject_bbox_norm for %s must be [left, top, right, bottom]" % filename
        )
    coords: List[float] = []
    for coord in value:
        if isinstance(coord, bool) or not isinstance(coord, (int, float)):
            raise ValueError("subject_bbox_norm values for %s must be numbers" % filename)
        number = float(coord)
        if not math.isfinite(number):
            raise ValueError("subject_bbox_norm values for %s must be finite" % filename)
        coords.append(number)
    left, top, right, bottom = coords
    if right <= left or bottom <= top:
        raise ValueError("subject_bbox_norm for %s must have positive area" % filename)
    return left, top, right, bottom


def _read_manifest(path: Optional[Path], filenames: Sequence[str]) -> Dict[str, Dict[str, Any]]:
    if path is None:
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("cannot read manifest %s: %s" % (path, exc)) from exc
    if not isinstance(data, dict) or not isinstance(data.get("stills"), list):
        raise ValueError("manifest must be a JSON object with a 'stills' array")

    known = set(filenames)
    result: Dict[str, Dict[str, Any]] = {}
    for index, entry in enumerate(data["stills"]):
        if not isinstance(entry, dict):
            raise ValueError("manifest still %d must be an object" % index)
        filename = entry.get("file")
        if not isinstance(filename, str) or not filename or Path(filename).name != filename:
            raise ValueError("manifest still %d needs a basename in 'file'" % index)
        if filename not in known:
            raise ValueError("manifest references a PNG not found in the folder: %s" % filename)
        if filename in result:
            raise ValueError("manifest contains duplicate entries for %s" % filename)

        normalized: Dict[str, Any] = {}
        phase = entry.get("phase")
        if phase is not None:
            if not isinstance(phase, str) or phase.lower() not in ("before", "after"):
                raise ValueError("phase for %s must be 'before' or 'after'" % filename)
            normalized["phase"] = phase.lower()
        cue = entry.get("cue")
        if cue is not None:
            if not isinstance(cue, str):
                raise ValueError("cue for %s must be text" % filename)
            normalized["cue"] = cue
        frame = entry.get("frame")
        if frame is not None:
            if isinstance(frame, bool) or not isinstance(frame, (int, str)):
                raise ValueError("frame for %s must be an integer or text timecode" % filename)
            normalized["frame"] = frame
        if "subject_bbox_norm" in entry:
            normalized["subject_bbox_norm"] = _validate_bbox(
                entry["subject_bbox_norm"], filename
            )
        minimum = entry.get("min_headroom_ratio")
        if minimum is not None:
            if (isinstance(minimum, bool) or not isinstance(minimum, (int, float))
                    or not math.isfinite(float(minimum)) or not 0 <= float(minimum) <= 1):
                raise ValueError("min_headroom_ratio for %s must be between 0 and 1" % filename)
            if "subject_bbox_norm" not in normalized:
                raise ValueError("min_headroom_ratio for %s needs subject_bbox_norm" % filename)
            normalized["min_headroom_ratio"] = float(minimum)
        result[filename] = normalized
    return result


def _hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _dark_fraction(gray: Image.Image) -> float:
    histogram = gray.histogram()
    return sum(histogram[:LUMINANCE_DARK_THRESHOLD + 1]) / float(gray.width * gray.height)


def _pixel_heuristics(rgb: Image.Image) -> Dict[str, Any]:
    """Measure brightness only; these are not subject or crop detectors."""
    gray = rgb.convert("L")
    width, height = gray.size
    x_band = max(1, round(width * 0.03))
    y_band = max(1, round(height * 0.03))
    total_dark = _dark_fraction(gray)
    return {
        "method": "Pillow grayscale luminance histogram",
        "dark_pixel_threshold_luminance_0_255": LUMINANCE_DARK_THRESHOLD,
        "dark_pixel_fraction": round(total_dark, 6),
        "non_dark_pixel_fraction": round(1.0 - total_dark, 6),
        "edge_dark_pixel_fraction": {
            "top_3_percent": round(_dark_fraction(gray.crop((0, 0, width, y_band))), 6),
            "bottom_3_percent": round(_dark_fraction(gray.crop((0, height - y_band, width, height))), 6),
            "left_3_percent": round(_dark_fraction(gray.crop((0, 0, x_band, height))), 6),
            "right_3_percent": round(_dark_fraction(gray.crop((width - x_band, 0, width, height))), 6),
        },
        "interpretation": "Brightness-only heuristic. Dark edges or pixels do not identify empty space or a crop.",
        "status": "heuristic_unverified",
    }


def _annotation_checks(entry: Dict[str, Any]) -> Dict[str, Any]:
    bbox = entry.get("subject_bbox_norm")
    if bbox is None:
        return {
            "status": "unverified",
            "basis": None,
            "reason": "No subject detector or manifest subject bounds were provided.",
        }
    left, top, right, bottom = bbox
    crossings = []
    if left < 0:
        crossings.append("left")
    if top < 0:
        crossings.append("top")
    if right > 1:
        crossings.append("right")
    if bottom > 1:
        crossings.append("bottom")
    minimum = entry.get("min_headroom_ratio")
    return {
        "status": "measured_from_manifest_annotation",
        "basis": "user_supplied_subject_bbox_norm; no image recognition performed",
        "subject_bbox_norm": [round(value, 6) for value in bbox],
        "top_margin_ratio": round(top, 6),
        "frame_boundary_crossings": crossings,
        "min_headroom_ratio": minimum,
        "headroom_check": (
            "pass" if top >= minimum else "fail"
        ) if minimum is not None else "not_evaluated",
        "limitations": "The annotation is treated as the full expected subject box; its accuracy is not verified.",
    }


def _phase_sort(phase: Optional[str]) -> int:
    return {"before": 0, "after": 1}.get(phase, 2)


def _pair_key(filename: str) -> str:
    stem = Path(filename).stem
    key = re.sub(r"(^|[^A-Za-z0-9])(before|after)(?=$|[^A-Za-z0-9])", r"\1", stem,
                 flags=re.IGNORECASE)
    return key.casefold()


def _font(size: int):
    for candidate in FONT_CANDIDATES:
        if os.path.isfile(candidate):
            try:
                return ImageFont.truetype(candidate, size)
            except OSError:
                pass
    return ImageFont.load_default()


def _fit_label(draw: ImageDraw.ImageDraw, text: str, font: Any, max_width: int) -> str:
    if draw.textbbox((0, 0), text, font=font)[2] <= max_width:
        return text
    ellipsis = "…"
    clipped = text
    while clipped and draw.textbbox((0, 0), clipped + ellipsis, font=font)[2] > max_width:
        clipped = clipped[:-1]
    return clipped + ellipsis


def _contact_sheet(records: Sequence[Dict[str, Any]], columns: int = 2) -> Image.Image:
    if columns <= 0:
        raise ValueError("columns must be positive")
    columns = min(columns, len(records))
    rows = (len(records) + columns - 1) // columns
    sheet = Image.new("RGB", (columns * TILE_WIDTH, rows * TILE_HEIGHT), (24, 24, 28))
    draw = ImageDraw.Draw(sheet)
    font = _font(17)
    for index, record in enumerate(records):
        row, column = divmod(index, columns)
        x, y = column * TILE_WIDTH, row * TILE_HEIGHT
        tile = record["_display_image"]
        scale = min((TILE_WIDTH - 20) / tile.width, (IMAGE_BOX_HEIGHT - 16) / tile.height)
        size = (max(1, round(tile.width * scale)), max(1, round(tile.height * scale)))
        preview = tile.resize(size, Image.Resampling.LANCZOS)
        px = x + (TILE_WIDTH - preview.width) // 2
        py = y + 8 + (IMAGE_BOX_HEIGHT - 16 - preview.height) // 2
        sheet.paste(preview, (px, py))

        phase = (record.get("phase") or "unspecified").upper()
        cue = record.get("cue") or "—"
        frame = record.get("frame")
        frame_text = str(frame) if frame is not None else "—"
        labels = [
            "%s | %s" % (phase, record["file"]),
            "cue: %s" % cue,
            "frame: %s | %s × %s" % (
                frame_text,
                record["dimensions"]["width"],
                record["dimensions"]["height"],
            ),
        ]
        label_y = y + IMAGE_BOX_HEIGHT + 6
        for label in labels:
            rendered = _fit_label(draw, label, font, TILE_WIDTH - 18)
            draw.text((x + 9, label_y), rendered, fill=(246, 228, 150), font=font)
            label_y += 26
        draw.rectangle((x, y, x + TILE_WIDTH - 1, y + TILE_HEIGHT - 1),
                       outline=(82, 82, 88), width=1)
    return sheet


def _resolved_path(path: Path) -> Path:
    return path.expanduser().resolve(strict=False)


def _preflight_outputs(input_dir: Path, sheet_path: Path, report_path: Path) -> Tuple[Path, Path]:
    for raw_output in (sheet_path.expanduser(), report_path.expanduser()):
        if raw_output.exists() or raw_output.is_symlink():
            raise FileExistsError("refusing to overwrite existing output: %s" % raw_output)
    sheet = _resolved_path(sheet_path)
    report = _resolved_path(report_path)
    if sheet == report:
        raise ValueError("contact-sheet and report paths must be different")
    if sheet.suffix.lower() != ".png":
        raise ValueError("contact-sheet output must use the .png extension")
    if report.suffix.lower() != ".json":
        raise ValueError("report output must use the .json extension")
    for output in (sheet, report):
        if not output.parent.is_dir():
            raise ValueError("output parent folder does not exist: %s" % output.parent)
        if output.exists() or output.is_symlink():
            raise FileExistsError("refusing to overwrite existing output: %s" % output)
    resolved_input = _resolved_path(input_dir)
    try:
        sheet.relative_to(resolved_input)
    except ValueError:
        pass
    else:
        raise ValueError("contact-sheet output must be outside the input folder")
    return sheet, report


def _sort_records(records: List[Dict[str, Any]]) -> None:
    def key(record: Dict[str, Any]):
        cue = record.get("cue")
        group = cue.casefold() if isinstance(cue, str) and cue else _pair_key(record["file"])
        frame = record.get("frame")
        frame_key = (0, frame) if isinstance(frame, int) else (1, str(frame or ""))
        return group, frame_key, _phase_sort(record.get("phase")), _natural_key(record["file"])
    records.sort(key=key)


def analyze_folder(
    input_dir: Path,
    manifest_path: Optional[Path] = None,
) -> Tuple[List[Dict[str, Any]], Image.Image]:
    if not input_dir.is_dir():
        raise ValueError("input folder does not exist: %s" % input_dir)
    paths = sorted((path for path in input_dir.iterdir()
                    if path.is_file() and path.suffix.lower() == ".png"),
                   key=lambda path: _natural_key(path.name))
    if not paths:
        raise ValueError("input folder contains no PNG stills: %s" % input_dir)
    manifest = _read_manifest(manifest_path, [path.name for path in paths])
    records: List[Dict[str, Any]] = []

    for path in paths:
        try:
            before = path.stat()
            with Image.open(path) as image:
                image.load()
                stored_width, stored_height = image.size
                image_format = image.format
                mode = image.mode
                if image_format != "PNG":
                    raise ValueError("file has %s content, expected PNG" % image_format)
                display = ImageOps.exif_transpose(image).convert("RGB")
            after = path.stat()
        except (OSError, ValueError) as exc:
            raise ValueError("cannot decode PNG %s: %s" % (path.name, exc)) from exc
        if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
            raise ValueError("input changed while it was being analyzed: %s" % path)

        metadata = manifest.get(path.name, {})
        phase = metadata.get("phase", _infer_phase(path.name))
        record: Dict[str, Any] = {
            "file": path.name,
            "phase": phase,
            "cue": metadata.get("cue"),
            "frame": metadata.get("frame"),
            "dimensions": {"width": display.width, "height": display.height},
            "stored_dimensions": {"width": stored_width, "height": stored_height},
            "aspect_ratio": round(display.width / display.height, 6),
            "image_mode": mode,
            "format": image_format,
            "file_size_bytes": after.st_size,
            "sha256": _hash_file(path),
            "pixel_heuristics": _pixel_heuristics(display),
            "crop_headroom": _annotation_checks(metadata),
            "subject_presence": {
                "status": "unverified",
                "method": None,
                "reason": "No face/head/subject recognition dependency or model was used.",
            },
            "_display_image": display,
        }
        records.append(record)

    _sort_records(records)
    sheet = _contact_sheet(records)
    return records, sheet


def _report_payload(input_dir: Path, sheet_path: Path, records: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    public_records = [{key: value for key, value in record.items() if not key.startswith("_")}
                      for record in records]
    return {
        "schema_version": SCHEMA_VERSION,
        "input_folder": str(_resolved_path(input_dir)),
        "contact_sheet": str(sheet_path),
        "analysis_scope": "offline PNG metadata and brightness heuristics",
        "automatic_verdict": "none; visual review is required",
        "limitations": [
            "No face, head, avatar, hand, caption, gameplay, or subject recognition was performed.",
            "Dark-pixel and edge-brightness fractions are descriptive heuristics, not crop detection.",
            "Crop/headroom geometry is evaluated only when supplied as a manifest annotation.",
            "A manifest subject box is trusted as caller-provided data and is not image-verified.",
        ],
        "stills": public_records,
    }


def create_qc_outputs(
    input_dir: Path,
    contact_sheet_path: Path,
    report_path: Path,
    manifest_path: Optional[Path] = None,
) -> Dict[str, Any]:
    sheet_path, report_out = _preflight_outputs(input_dir, contact_sheet_path, report_path)
    records, sheet = analyze_folder(input_dir, manifest_path)
    payload = _report_payload(input_dir, sheet_path, records)
    image_buffer = BytesIO()
    sheet.save(image_buffer, format="PNG", optimize=True)
    report_bytes = (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode("utf-8")

    created: List[Path] = []
    open_fds: List[int] = []
    try:
        sheet_fd = os.open(str(sheet_path), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o666)
        open_fds.append(sheet_fd)
        created.append(sheet_path)
        report_fd = os.open(str(report_out), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o666)
        open_fds.append(report_fd)
        created.append(report_out)
        with os.fdopen(sheet_fd, "wb") as handle:
            open_fds.remove(sheet_fd)
            handle.write(image_buffer.getvalue())
        with os.fdopen(report_fd, "wb") as handle:
            open_fds.remove(report_fd)
            handle.write(report_bytes)
    except Exception:
        for fd in open_fds:
            try:
                os.close(fd)
            except OSError:
                pass
        for path in created:
            try:
                path.unlink()
            except OSError:
                pass
        raise
    finally:
        sheet.close()
        for record in records:
            record["_display_image"].close()
    return payload


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("input_folder", help="folder containing before/after PNG stills")
    parser.add_argument("--contact-sheet", required=True, help="new .png output path")
    parser.add_argument("--report", required=True, help="new .json output path")
    parser.add_argument("--manifest", help="optional JSON cue/frame annotation manifest")
    args = parser.parse_args(argv)
    try:
        payload = create_qc_outputs(
            Path(args.input_folder),
            Path(args.contact_sheet),
            Path(args.report),
            Path(args.manifest) if args.manifest else None,
        )
    except (FileExistsError, ValueError, OSError) as exc:
        parser.error(str(exc))
    print("stills=%d" % len(payload["stills"]))
    print("contact_sheet=%s" % payload["contact_sheet"])
    print("report=%s" % Path(args.report).expanduser().resolve(strict=False))
    print("subject_presence=unverified; visual review required")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
