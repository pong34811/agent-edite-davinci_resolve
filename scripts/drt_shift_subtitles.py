"""Correct the known timeline-end offset on an SRT-created subtitle track in a DRT.

This is a conservative offline helper for a disposable Resolve timeline copy. It
does not import or modify a Resolve project. The caller must export a DRT, use
this helper, import the patched DRT as a new timeline, and verify the imported
timeline through Resolve before replacing any original.
"""

from __future__ import annotations

import argparse
import copy
import io
import re
import zipfile
import xml.etree.ElementTree as ET
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path


class SubtitleDrtError(ValueError):
    """Raised when a DRT cannot be patched without guessing."""


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
    except (OSError, zipfile.BadZipFile, RuntimeError, EOFError) as exc:
        raise SubtitleDrtError(f"cannot read DRT archive {path}: {exc}") from exc


def _read_varint(data: bytes, pos: int) -> tuple[int, int]:
    value = 0
    shift = 0
    while pos < len(data) and shift <= 63:
        byte = data[pos]
        pos += 1
        value |= (byte & 0x7F) << shift
        if byte < 0x80:
            return value, pos
        shift += 7
    raise SubtitleDrtError("malformed protobuf varint in subtitle FieldsBlob")


def _write_varint(value: int) -> bytes:
    if value < 0:
        raise SubtitleDrtError("negative subtitle start frames are not supported")
    out = bytearray()
    while value >= 0x80:
        out.append((value & 0x7F) | 0x80)
        value >>= 7
    out.append(value)
    return bytes(out)


def _patch_fields_blob(blob_hex: str, old_start: int, new_start: int) -> str:
    try:
        blob = bytes.fromhex(blob_hex)
    except ValueError as exc:
        raise SubtitleDrtError("subtitle FieldsBlob is not valid hexadecimal") from exc
    if len(blob) < 8 or int.from_bytes(blob[:4], "big") != 2:
        raise SubtitleDrtError("unsupported subtitle FieldsBlob envelope")
    payload = blob[8:]
    if int.from_bytes(blob[4:8], "big") != len(payload):
        raise SubtitleDrtError("subtitle FieldsBlob length header does not match")

    out = bytearray()
    pos = 0
    patched = 0
    while pos < len(payload):
        field_start = pos
        key, pos = _read_varint(payload, pos)
        field_number, wire_type = key >> 3, key & 7
        if field_number == 21 and wire_type == 0:
            value, value_end = _read_varint(payload, pos)
            if value != old_start:
                raise SubtitleDrtError(
                    f"FieldsBlob start {value} does not match XML Start {old_start}"
                )
            out.extend(payload[field_start:pos])
            out.extend(_write_varint(new_start))
            pos = value_end
            patched += 1
        elif wire_type == 0:
            _value, pos = _read_varint(payload, pos)
            out.extend(payload[field_start:pos])
        elif wire_type == 1:
            pos += 8
            out.extend(payload[field_start:pos])
        elif wire_type == 2:
            size, data_start = _read_varint(payload, pos)
            pos = data_start + size
            out.extend(payload[field_start:pos])
        elif wire_type == 5:
            pos += 4
            out.extend(payload[field_start:pos])
        else:
            raise SubtitleDrtError(f"unsupported protobuf wire type {wire_type}")
        if pos > len(payload):
            raise SubtitleDrtError("subtitle FieldsBlob field extends past payload")
    if patched != 1:
        raise SubtitleDrtError(f"expected one start field in FieldsBlob, found {patched}")
    new_payload = bytes(out)
    return (blob[:4] + len(new_payload).to_bytes(4, "big") + new_payload).hex()


def _parse_srt(path: Path, fps: Decimal) -> list[tuple[str, int, int]]:
    text = path.read_text(encoding="utf-8-sig")
    blocks = re.split(r"\r?\n\s*\r?\n", text.strip()) if text.strip() else []
    cues = []
    time_re = re.compile(
        r"^(\d{2}):(\d{2}):(\d{2}),(\d{3})\s+-->\s+"
        r"(\d{2}):(\d{2}):(\d{2}),(\d{3})$"
    )
    for expected_index, block in enumerate(blocks, 1):
        lines = block.splitlines()
        if len(lines) < 3 or lines[0].strip() != str(expected_index):
            raise SubtitleDrtError(f"malformed SRT block {expected_index}")
        match = time_re.fullmatch(lines[1].strip())
        if not match:
            raise SubtitleDrtError(f"malformed SRT timecode in block {expected_index}")
        values = [Decimal(x) for x in match.groups()]
        sh, sm, ss, sms, eh, em, es, ems = values
        start_sec = sh * 3600 + sm * 60 + ss + sms / 1000
        end_sec = eh * 3600 + em * 60 + es + ems / 1000
        start = int((start_sec * fps).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
        end = int((end_sec * fps).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
        caption = "\n".join(lines[2:]).strip()
        if not caption or end <= start:
            raise SubtitleDrtError(f"invalid cue content or range in block {expected_index}")
        cues.append((caption, start, end))
    return cues


def _sequence_member(payloads: dict[str, bytes]) -> str:
    matches = [
        name for name in payloads
        if name.startswith("SeqContainer/") and name.lower().endswith(".xml")
    ]
    if len(matches) != 1:
        raise SubtitleDrtError(f"expected one sequence XML, found {len(matches)}")
    return matches[0]


def shift_srt_track(
    source_path: str | Path,
    output_path: str | Path,
    srt_path: str | Path,
    *,
    track_index: int,
    offset_frames: int,
    fps: int = 60,
) -> dict:
    """Shift one SRT-created subtitle track by an exact frame offset.

    Verifies source text, source frame offset, durations, non-overlap with other
    subtitle tracks, unchanged non-target tracks, and DRT archive CRC before
    writing. Output must be a new file.
    """
    source = Path(source_path).resolve()
    output = Path(output_path).resolve()
    srt = Path(srt_path).resolve()
    if source == output or output.exists():
        raise SubtitleDrtError("output must be a new path different from source")
    if not source.is_file() or not srt.is_file() or not output.parent.is_dir():
        raise SubtitleDrtError("source DRT, SRT, or output directory is missing")
    if track_index < 1 or offset_frames <= 0 or fps <= 0:
        raise SubtitleDrtError("track_index, offset_frames, and fps must be positive")

    expected = _parse_srt(srt, Decimal(fps))
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
    if not 1 <= track_index <= len(wrappers):
        raise SubtitleDrtError("subtitle track index is out of range")
    target_track = wrappers[track_index - 1].find("Sm2TiTrack")
    if target_track is None:
        raise SubtitleDrtError("target subtitle track structure is ambiguous")
    target_items = target_track.find("Items")
    if target_items is None:
        raise SubtitleDrtError("target subtitle track has no Items vector")
    item_wrappers = target_items.findall("Element")
    if len(item_wrappers) != len(expected):
        raise SubtitleDrtError(
            f"target track has {len(item_wrappers)} cues; SRT has {len(expected)}"
        )

    before_other_tracks = {}
    for vector_name in ("VideoTrackVec", "AudioTrackVec", "SubtitleTrackVec", "GeometryTrackVec"):
        vector = root.find(vector_name)
        if vector is None:
            raise SubtitleDrtError(f"missing {vector_name}")
        for index, wrapper in enumerate(vector.findall("Element"), 1):
            key = (vector_name, index)
            if key != ("SubtitleTrackVec", track_index):
                before_other_tracks[key] = ET.tostring(wrapper, encoding="utf-8")

    corrected = []
    for index, (wrapper, expected_cue) in enumerate(zip(item_wrappers, expected), 1):
        if len(wrapper) != 1 or wrapper[0].tag != "Sm2TiGenerator":
            raise SubtitleDrtError(f"target item {index} is not a native subtitle generator")
        item = wrapper[0]
        name = item.findtext("Name")
        old_text, expected_start, expected_end = expected_cue
        try:
            old_start = int(item.findtext("Start"))
            duration = int(item.findtext("Duration"))
        except (TypeError, ValueError) as exc:
            raise SubtitleDrtError(f"target item {index} has invalid timing") from exc
        new_start = old_start - offset_frames
        if name != old_text or new_start != expected_start or duration != expected_end - expected_start:
            raise SubtitleDrtError(
                f"target cue {index} does not match SRT after requested offset: "
                f"text={name!r}, old_start={old_start}, duration={duration}, "
                f"expected=({old_text!r}, {expected_start}, {expected_end})"
            )
        fields = item.find("FieldsBlob")
        if fields is None:
            raise SubtitleDrtError(f"target item {index} has no FieldsBlob")
        fields.text = _patch_fields_blob(fields.text or "", old_start, new_start)
        item.find("Start").text = str(new_start)
        corrected.append((name, new_start, new_start + duration))

    # Ensure candidate cues do not collide with captions already present on
    # another native subtitle track.
    for other_index, wrapper in enumerate(wrappers, 1):
        if other_index == track_index:
            continue
        track = wrapper.find("Sm2TiTrack")
        items = track.find("Items") if track is not None else None
        for entry in items.findall("Element") if items is not None else []:
            if len(entry) != 1:
                raise SubtitleDrtError("ambiguous item on existing subtitle track")
            item = entry[0]
            try:
                old_start = int(item.findtext("Start"))
                old_end = old_start + int(item.findtext("Duration"))
            except (TypeError, ValueError):
                raise SubtitleDrtError("invalid timing on existing subtitle track")
            if any(a < old_end and old_start < b for _name, a, b in corrected):
                raise SubtitleDrtError("corrected cue overlaps an existing subtitle")

    # Preserve all non-target tracks and sequence contents exactly.
    for vector_name in ("VideoTrackVec", "AudioTrackVec", "SubtitleTrackVec", "GeometryTrackVec"):
        vector = root.find(vector_name)
        for index, wrapper in enumerate(vector.findall("Element"), 1):
            key = (vector_name, index)
            if key in before_other_tracks and ET.tostring(wrapper, encoding="utf-8") != before_other_tracks[key]:
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
        after_root = ET.fromstring(archive.read(seq_name))
    after_track = after_root.find("SubtitleTrackVec").findall("Element")[track_index - 1].find("Sm2TiTrack")
    after_items = after_track.find("Items").findall("Element")
    readback = []
    for wrapper in after_items:
        item = wrapper[0]
        readback.append((item.findtext("Name"), int(item.findtext("Start")), int(item.findtext("Start")) + int(item.findtext("Duration"))))
    if readback != corrected:
        raise SubtitleDrtError("patched subtitle timing failed archive read-back")

    with output.open("xb") as handle:
        if handle.write(output_bytes) != len(output_bytes):
            output.unlink(missing_ok=True)
            raise SubtitleDrtError("incomplete output write")
    _payloads, _infos, _comment = _read_archive(output)
    return {
        "source": str(source),
        "output": str(output),
        "subtitle_track_index": track_index,
        "offset_frames_removed": offset_frames,
        "fps": fps,
        "cue_count": len(readback),
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
    parser.add_argument("--track-index", type=int, required=True)
    parser.add_argument("--offset-frames", type=int, required=True)
    parser.add_argument("--fps", type=int, default=60)
    args = parser.parse_args()
    import json
    print(json.dumps(shift_srt_track(
        args.source_drt,
        args.output_drt,
        args.srt,
        track_index=args.track_index,
        offset_frames=args.offset_frames,
        fps=args.fps,
    ), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
