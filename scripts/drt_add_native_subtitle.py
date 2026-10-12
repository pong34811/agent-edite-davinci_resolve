"""Append one native subtitle cue to an empty Subtitle track in a DRT archive.

This is an offline DRT editor. It does not connect to or modify a Resolve
project. The output path must be new; inspect/import the result separately.
"""

from __future__ import annotations

import argparse
import copy
import io
import json
import re
import uuid
import xml.etree.ElementTree as ET
import zipfile
from decimal import Decimal
from pathlib import Path

try:
    from scripts.drt_shift_subtitles import SubtitleDrtError, _parse_srt, _patch_fields_blob
except ModuleNotFoundError as exc:
    # Support both `python -m scripts.drt_add_native_subtitle` from the repo
    # root and direct execution via `python scripts/drt_add_native_subtitle.py`.
    if exc.name not in {"scripts", "scripts.drt_shift_subtitles"}:
        raise
    from drt_shift_subtitles import SubtitleDrtError, _parse_srt, _patch_fields_blob


def _read_archive(path: Path):
    try:
        with zipfile.ZipFile(path, "r") as archive:
            infos = archive.infolist()
            names = [info.filename for info in infos]
            if len(names) != len(set(names)):
                raise SubtitleDrtError("DRT contains duplicate archive members")
            bad = archive.testzip()
            if bad:
                raise SubtitleDrtError(f"DRT CRC check failed for {bad!r}")
            return {name: archive.read(name) for name in names}, infos, archive.comment
    except SubtitleDrtError:
        raise
    except (OSError, zipfile.BadZipFile, RuntimeError, EOFError) as exc:
        raise SubtitleDrtError(f"cannot read DRT archive {path}: {exc}") from exc


def _sequence_member(payloads: dict[str, bytes]) -> str:
    matches = [
        name for name in payloads
        if name.startswith("SeqContainer/") and name.lower().endswith(".xml")
    ]
    if len(matches) != 1:
        raise SubtitleDrtError(f"expected one sequence XML, found {len(matches)}")
    return matches[0]


def _fresh_dbid(used: set[str]) -> str:
    while True:
        candidate = str(uuid.uuid4())
        if candidate not in used:
            used.add(candidate)
            return candidate


def _all_dbids(payloads: dict[str, bytes]) -> set[str]:
    used: set[str] = set()
    for name, payload in payloads.items():
        if name.lower().endswith(".xml"):
            for match in re.finditer(rb"\bDbId\s*=\s*(['\"])(.*?)\1", payload, re.DOTALL):
                try:
                    value = match.group(2).decode("utf-8", errors="strict")
                except UnicodeDecodeError as exc:
                    raise SubtitleDrtError(f"non-UTF-8 DbId attribute in {name!r}") from exc
                if value:
                    used.add(value)
    return used


def _track_items(wrapper: ET.Element, description: str) -> list[ET.Element]:
    if len(wrapper) != 1 or wrapper[0].tag != "Sm2TiTrack":
        raise SubtitleDrtError(f"ambiguous {description} track structure")
    items = wrapper[0].find("Items")
    if items is None:
        raise SubtitleDrtError(f"{description} track has no Items vector")
    return items.findall("Element")


def add_native_subtitle(
    source_path: str | Path,
    output_path: str | Path,
    srt_path: str | Path,
    *,
    target_track_index: int,
    template_track_index: int,
    fps: int,
    timeline_end: int | None = None,
) -> dict:
    """Add the sole cue in ``srt_path`` to an existing empty native track.

    Track indices are 1-based. Cue ranges are half-open ``[start, end)`` and
    SRT milliseconds are converted using nearest-frame, half-up rounding.
    """
    source = Path(source_path).resolve()
    output = Path(output_path).resolve()
    srt = Path(srt_path).resolve()
    if source == output or output.exists():
        raise SubtitleDrtError("output must be a new path different from source")
    if not source.is_file() or not srt.is_file() or not output.parent.is_dir():
        raise SubtitleDrtError("source DRT, SRT, or output directory is missing")
    if target_track_index < 1 or template_track_index < 1 or fps <= 0:
        raise SubtitleDrtError("track indices and fps must be positive")
    if timeline_end is not None and timeline_end <= 0:
        raise SubtitleDrtError("timeline_end must be a positive frame count")

    cues = _parse_srt(srt, Decimal(fps))
    if len(cues) != 1:
        raise SubtitleDrtError(f"expected exactly one SRT cue, found {len(cues)}")
    caption, cue_start, cue_end = cues[0]
    if timeline_end is not None and cue_end > timeline_end:
        raise SubtitleDrtError(
            f"cue ends at frame {cue_end}, beyond timeline_end {timeline_end}"
        )

    payloads, infos, comment = _read_archive(source)
    seq_name = _sequence_member(payloads)
    try:
        root = ET.fromstring(payloads[seq_name])
    except ET.ParseError as exc:
        raise SubtitleDrtError(f"invalid sequence XML: {exc}") from exc
    subtitle_vec = root.find("SubtitleTrackVec")
    if subtitle_vec is None:
        raise SubtitleDrtError("DRT has no SubtitleTrackVec")
    wrappers = subtitle_vec.findall("Element")
    if target_track_index > len(wrappers) or template_track_index > len(wrappers):
        raise SubtitleDrtError("subtitle track index is out of range")

    target_wrapper = wrappers[target_track_index - 1]
    template_wrapper = wrappers[template_track_index - 1]
    target_entries = _track_items(target_wrapper, "target")
    if target_entries:
        raise SubtitleDrtError("target subtitle track is not empty")
    template_entries = _track_items(template_wrapper, "template")
    native_templates = [
        entry[0] for entry in template_entries
        if len(entry) == 1 and entry[0].tag == "Sm2TiGenerator"
    ]
    if not native_templates:
        raise SubtitleDrtError("template subtitle track has no native caption generator")
    template = native_templates[0]
    try:
        old_start = int(template.findtext("Start"))
    except (TypeError, ValueError) as exc:
        raise SubtitleDrtError("template caption has invalid Start") from exc
    if template.find("FieldsBlob") is None or template.find("Duration") is None:
        raise SubtitleDrtError("template caption lacks FieldsBlob or Duration")

    # The cloned item is a new timeline object. Its name and record range come
    # from the single SRT cue; its native styling and other generator fields
    # come from the existing subtitle caption.
    clone = copy.deepcopy(template)
    name_node = clone.find("Name")
    start_node = clone.find("Start")
    duration_node = clone.find("Duration")
    fields_node = clone.find("FieldsBlob")
    if name_node is None or start_node is None or duration_node is None or fields_node is None:
        raise SubtitleDrtError("template caption structure is incomplete")
    name_node.text = caption
    start_node.text = str(cue_start)
    duration_node.text = str(cue_end - cue_start)
    fields_node.text = _patch_fields_blob(fields_node.text or "", old_start, cue_start)
    used_dbids = _all_dbids(payloads)
    if clone.get("DbId") is None:
        raise SubtitleDrtError("template caption has no DbId")
    clone.set("DbId", _fresh_dbid(used_dbids))

    # Reject collisions against all other subtitle tracks, including malformed
    # items whose shape is not a native generator but whose range is readable.
    for other_index, wrapper in enumerate(wrappers, 1):
        if other_index == target_track_index:
            continue
        for entry in _track_items(wrapper, f"subtitle {other_index}"):
            if len(entry) != 1:
                raise SubtitleDrtError("ambiguous item on existing subtitle track")
            item = entry[0]
            try:
                other_start = int(item.findtext("Start"))
                other_end = other_start + int(item.findtext("Duration"))
            except (TypeError, ValueError) as exc:
                raise SubtitleDrtError("invalid timing on existing subtitle track") from exc
            if cue_start < other_end and other_start < cue_end:
                raise SubtitleDrtError(
                    f"cue [{cue_start}, {cue_end}) overlaps subtitle track {other_index}"
                )

    # Snapshot every track other than the target. This also ensures the
    # template track itself remains byte-for-byte equivalent in XML structure.
    snapshots = {}
    for vector_name in ("VideoTrackVec", "AudioTrackVec", "SubtitleTrackVec", "GeometryTrackVec"):
        vector = root.find(vector_name)
        if vector is None:
            raise SubtitleDrtError(f"missing {vector_name}")
        for index, wrapper in enumerate(vector.findall("Element"), 1):
            if (vector_name, index) != ("SubtitleTrackVec", target_track_index):
                snapshots[(vector_name, index)] = ET.tostring(wrapper, encoding="utf-8")

    target_items_node = target_wrapper.find("Sm2TiTrack/Items")
    item_wrapper = ET.Element("Element")
    item_wrapper.append(clone)
    target_items_node.append(item_wrapper)

    for vector_name in ("VideoTrackVec", "AudioTrackVec", "SubtitleTrackVec", "GeometryTrackVec"):
        vector = root.find(vector_name)
        for index, wrapper in enumerate(vector.findall("Element"), 1):
            key = (vector_name, index)
            if key in snapshots and ET.tostring(wrapper, encoding="utf-8") != snapshots[key]:
                raise SubtitleDrtError(f"non-target track changed: {key}")

    changed_xml = ET.tostring(root, encoding="utf-8", xml_declaration=True)
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", allowZip64=True) as archive:
        archive.comment = comment
        for info in infos:
            data = changed_xml if info.filename == seq_name else payloads[info.filename]
            archive.writestr(copy.copy(info), data, compress_type=info.compress_type)
    output_bytes = buffer.getvalue()
    with zipfile.ZipFile(io.BytesIO(output_bytes), "r") as archive:
        bad = archive.testzip()
        if bad:
            raise SubtitleDrtError(f"patched archive CRC check failed for {bad!r}")
        after_payloads = {info.filename: archive.read(info.filename) for info in archive.infolist()}
    after_root = ET.fromstring(after_payloads[seq_name])
    after_track = after_root.find("SubtitleTrackVec").findall("Element")[target_track_index - 1]
    after_entries = _track_items(after_track, "readback target")
    if len(after_entries) != 1 or len(after_entries[0]) != 1:
        raise SubtitleDrtError("patched cue failed archive read-back")
    after_item = after_entries[0][0]
    readback = (
        after_item.findtext("Name"),
        int(after_item.findtext("Start")),
        int(after_item.findtext("Start")) + int(after_item.findtext("Duration")),
    )
    if readback != (caption, cue_start, cue_end):
        raise SubtitleDrtError(f"patched cue read-back mismatch: {readback!r}")
    readback_fields = after_item.findtext("FieldsBlob") or ""
    if _patch_fields_blob(readback_fields, cue_start, cue_start) != readback_fields:
        raise SubtitleDrtError("patched cue FieldsBlob start failed archive read-back")
    if after_item.get("DbId") in _all_dbids(payloads):
        raise SubtitleDrtError("patched cue DbId is not unique")
    for name, payload in payloads.items():
        if name != seq_name and after_payloads[name] != payload:
            raise SubtitleDrtError(f"non-sequence archive member changed: {name!r}")

    try:
        with output.open("xb") as handle:
            if handle.write(output_bytes) != len(output_bytes):
                raise SubtitleDrtError("incomplete output write")
    except OSError as exc:
        output.unlink(missing_ok=True)
        raise SubtitleDrtError(f"cannot write output DRT: {exc}") from exc
    except SubtitleDrtError:
        output.unlink(missing_ok=True)
        raise
    _read_archive(output)
    return {
        "source": str(source),
        "output": str(output),
        "target_track_index": target_track_index,
        "template_track_index": template_track_index,
        "fps": fps,
        "cue_count": 1,
        "readback": readback,
        "non_target_tracks_unchanged": True,
        "archive_crc": "passed",
        "output_bytes": output.stat().st_size,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source_drt")
    parser.add_argument("srt")
    parser.add_argument("output_drt")
    parser.add_argument("--target-track-index", type=int, required=True)
    parser.add_argument("--template-track-index", type=int, required=True)
    parser.add_argument("--fps", type=int, required=True)
    parser.add_argument("--timeline-end", type=int)
    args = parser.parse_args()
    print(json.dumps(add_native_subtitle(
        args.source_drt,
        args.output_drt,
        args.srt,
        target_track_index=args.target_track_index,
        template_track_index=args.template_track_index,
        fps=args.fps,
        timeline_end=args.timeline_end,
    ), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
