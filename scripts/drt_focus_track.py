"""Insert a native Adjustment Clip track into an exported Resolve .drt archive.

Example::

    python scripts/drt_focus_track.py source.drt adjustment-template.drt patched.drt \
        --start-frame 1200 --end-frame 1320

Add ``--dry-run`` to validate and print the summary without writing an archive.
The frame range is half-open: ``[start_frame, end_frame)``.

This utility edits exported DRT files offline. It does not connect to Resolve.
"""

from __future__ import annotations

import argparse
import copy
import io
import json
import os
import re
import uuid
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path
from typing import Any


TRACK_VECTORS = {
    "VideoTrackVec": 0,
    "AudioTrackVec": 1,
    "SubtitleTrackVec": 2,
    "GeometryTrackVec": 3,
}


class DrtPatchError(ValueError):
    """Raised when a DRT cannot be patched without guessing."""


def _read_archive(path: Path) -> tuple[dict[str, bytes], list[zipfile.ZipInfo], bytes]:
    try:
        with zipfile.ZipFile(path, "r") as archive:
            infos = archive.infolist()
            names = [info.filename for info in infos]
            if len(names) != len(set(names)):
                raise DrtPatchError(f"archive contains duplicate member names: {path}")
            bad_member = archive.testzip()
            if bad_member is not None:
                raise DrtPatchError(f"archive CRC check failed for {bad_member!r}: {path}")
            payloads = {info.filename: archive.read(info.filename) for info in infos}
            return payloads, infos, archive.comment
    except DrtPatchError:
        raise
    except (OSError, zipfile.BadZipFile, RuntimeError, EOFError) as exc:
        raise DrtPatchError(f"cannot read DRT archive {path}: {exc}") from exc


def _sequence_member(payloads: dict[str, bytes], archive_path: Path) -> str:
    members = [
        name
        for name in payloads
        if name.startswith("SeqContainer/") and name.lower().endswith(".xml")
    ]
    if len(members) != 1:
        raise DrtPatchError(
            f"expected exactly one SeqContainer XML in {archive_path}, found {len(members)}"
        )
    return members[0]


def _parse_xml(payload: bytes, description: str) -> ET.Element:
    try:
        return ET.fromstring(payload)
    except ET.ParseError as exc:
        raise DrtPatchError(f"invalid XML in {description}: {exc}") from exc


def _all_archive_dbids(payloads: dict[str, bytes], archive_path: Path) -> set[str]:
    ids: set[str] = set()
    for name, payload in payloads.items():
        if not name.lower().endswith(".xml"):
            continue
        # Resolve exports can contain application-specific names such as
        # ``ListMgt::LmPowerNodeList`` in project.xml, which ElementTree rejects
        # as an unbound namespace prefix. Scan the actual attribute syntax so
        # IDs in every XML member still participate in uniqueness checks.
        for match in re.finditer(rb"\bDbId\s*=\s*(['\"])(.*?)\1", payload, re.DOTALL):
            try:
                value = match.group(2).decode("utf-8", errors="strict")
            except UnicodeDecodeError as exc:
                raise DrtPatchError(
                    f"non-UTF-8 DbId attribute in {archive_path}!/{name}"
                ) from exc
            if value:
                ids.add(value)
    return ids


def _fresh_dbid(used: set[str]) -> str:
    while True:
        candidate = str(uuid.uuid4())
        if candidate not in used:
            used.add(candidate)
            return candidate


def _video_sequence_id(root: ET.Element, vector_name: str, archive_path: Path) -> str:
    sequence_ids: set[str] = set()
    for vector, track in _iter_tracks(root, archive_path):
        sequence = track.findtext("Sequence")
        if not sequence:
            raise DrtPatchError(f"track {track.get('DbId')!r} has no sequence ID in {archive_path}")
        sequence_ids.add(sequence)
    if len(sequence_ids) != 1:
        raise DrtPatchError(f"tracks in {archive_path} do not share one sequence ID")
    if not root.find(vector_name).findall("Element"):
        raise DrtPatchError(f"{archive_path} has no video tracks to identify its sequence")
    return next(iter(sequence_ids))


def _iter_tracks(root: ET.Element, archive_path: Path):
    for vector_name, expected_type in TRACK_VECTORS.items():
        vector = root.find(vector_name)
        if vector is None:
            raise DrtPatchError(f"missing {vector_name} in {archive_path}")
        for index, wrapper in enumerate(vector.findall("Element")):
            if len(wrapper) != 1 or wrapper[0].tag != "Sm2TiTrack":
                raise DrtPatchError(
                    f"ambiguous {vector_name} entry {index} in {archive_path}"
                )
            track = wrapper[0]
            dbid = track.get("DbId")
            if not dbid:
                raise DrtPatchError(f"track without DbId in {vector_name} of {archive_path}")
            actual_type = track.findtext("Type")
            if actual_type != str(expected_type):
                raise DrtPatchError(
                    f"track {dbid} in {vector_name} has unexpected Type {actual_type!r}"
                )
            items = track.find("Items")
            if items is None:
                raise DrtPatchError(f"track {dbid} has no Items vector in {archive_path}")
            yield vector_name, track


def _sequence_extent(root: ET.Element, archive_path: Path) -> int:
    ends: list[int] = []
    for _vector_name, track in _iter_tracks(root, archive_path):
        for index, wrapper in enumerate(track.find("Items").findall("Element")):
            if len(wrapper) != 1:
                raise DrtPatchError(
                    f"ambiguous item {index} on track {track.get('DbId')} in {archive_path}"
                )
            item = wrapper[0]
            start_text = item.findtext("Start")
            duration_text = item.findtext("Duration")
            try:
                start = int(start_text)
                duration = int(duration_text)
            except (TypeError, ValueError) as exc:
                raise DrtPatchError(
                    f"item {item.get('DbId')!r} on track {track.get('DbId')} has a non-integer start or duration"
                ) from exc
            if start < 0 or duration <= 0:
                raise DrtPatchError(
                    f"item {item.get('DbId')!r} on track {track.get('DbId')} has an invalid range"
                )
            ends.append(start + duration)
    if not ends:
        raise DrtPatchError(f"cannot determine sequence extent from empty tracks in {archive_path}")
    return max(ends)


def _item_signatures(root: ET.Element) -> dict[str, tuple[bytes, ...]]:
    signatures: dict[str, tuple[bytes, ...]] = {}
    for vector_name in TRACK_VECTORS:
        vector = root.find(vector_name)
        for wrapper in vector.findall("Element"):
            track = wrapper.find("Sm2TiTrack")
            items = track.find("Items")
            track_id = track.get("DbId")
            if track_id in signatures:
                raise DrtPatchError(f"duplicate track DbId in sequence: {track_id}")
            signatures[track_id] = tuple(
                ET.tostring(item, encoding="utf-8") for item in items.findall("Element")
            )
    return signatures


def _video_track_order(root: ET.Element) -> list[tuple[str, str]]:
    order = []
    seen_ids = set()
    for wrapper in root.find("VideoTrackVec").findall("Element"):
        track = wrapper.find("Sm2TiTrack")
        track_id = track.get("DbId")
        if not track_id or track_id in seen_ids:
            raise DrtPatchError(f"missing or duplicate video track DbId: {track_id!r}")
        seen_ids.add(track_id)
        order.append((track_id, track.findtext("UserDefinedName") or ""))
    return order


def _select_adjustment_template(root: ET.Element, archive_path: Path):
    vector = root.find("VideoTrackVec")
    candidates = []
    for wrapper in vector.findall("Element"):
        track = wrapper.find("Sm2TiTrack")
        item_wrappers = track.find("Items").findall("Element")
        if len(item_wrappers) != 1 or len(item_wrappers[0]) != 1:
            continue
        clip = item_wrappers[0][0]
        if clip.tag == "Sm2TiGenerator" and clip.findtext("PrettyType") == "Adjustment Clip":
            candidates.append((wrapper, track, item_wrappers[0], clip))
    if len(candidates) != 1:
        raise DrtPatchError(
            "ambiguous Adjustment Clip template: expected exactly one isolated native "
            f"Adjustment Clip item in {archive_path}, found {len(candidates)}"
        )
    wrapper, track, item_wrapper, clip = candidates[0]
    if track.findtext("Type") != "0":
        raise DrtPatchError(f"Adjustment Clip template is not on a video track in {archive_path}")
    for required in ("PrettyType", "Name", "Start", "Duration"):
        if clip.find(required) is None:
            raise DrtPatchError(f"Adjustment Clip template is missing {required} in {archive_path}")
    try:
        if int(clip.findtext("Duration")) <= 0:
            raise ValueError
    except (TypeError, ValueError) as exc:
        raise DrtPatchError(f"Adjustment Clip template has an invalid duration in {archive_path}") from exc
    return wrapper, track, item_wrapper, clip


def _serialize_xml(root: ET.Element) -> bytes:
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def _build_archive(
    payloads: dict[str, bytes], infos: list[zipfile.ZipInfo], archive_comment: bytes, changed_name: str, changed_payload: bytes
) -> bytes:
    buffer = io.BytesIO()
    try:
        with zipfile.ZipFile(buffer, "w", allowZip64=True) as output_zip:
            output_zip.comment = archive_comment
            for info in infos:
                data = changed_payload if info.filename == changed_name else payloads[info.filename]
                output_zip.writestr(copy.copy(info), data, compress_type=info.compress_type)
        return buffer.getvalue()
    except (OSError, zipfile.BadZipFile, RuntimeError) as exc:
        raise DrtPatchError(f"could not build output DRT archive: {exc}") from exc


def _verify_archive_bytes(
    archive_bytes: bytes,
    source_signatures: dict[str, tuple[bytes, ...]],
    source_track_counts: dict[str, int],
    source_video_order: list[tuple[str, str]],
    sequence_member: str,
    sequence_id: str,
    track_name: str,
    track_index: int,
    start_frame: int,
    end_frame: int,
    sequence_extent: int,
) -> tuple[str, str]:
    try:
        with zipfile.ZipFile(io.BytesIO(archive_bytes), "r") as archive:
            bad_member = archive.testzip()
            if bad_member is not None:
                raise DrtPatchError(f"output CRC check failed for {bad_member!r}")
            root = ET.fromstring(archive.read(sequence_member))
    except DrtPatchError:
        raise
    except (zipfile.BadZipFile, ET.ParseError, OSError) as exc:
        raise DrtPatchError(f"output archive could not be read back: {exc}") from exc

    video_vector = root.find("VideoTrackVec")
    video_entries = video_vector.findall("Element")
    if len(video_entries) != source_track_counts["VideoTrackVec"] + 1:
        raise DrtPatchError("output video track count did not increase by exactly one")
    for vector_name, original_count in source_track_counts.items():
        vector = root.find(vector_name)
        actual_count = len(vector.findall("Element"))
        expected = original_count + (1 if vector_name == "VideoTrackVec" else 0)
        if actual_count != expected:
            raise DrtPatchError(
                f"output {vector_name} count is {actual_count}; expected {expected}"
            )

    after_signatures = _item_signatures(root)
    for track_id, signature in source_signatures.items():
        if after_signatures.get(track_id) != signature:
            raise DrtPatchError(f"source track items changed on track {track_id}")

    insertion_offset = track_index - 1
    if not 0 <= insertion_offset < len(video_entries):
        raise DrtPatchError(f"output does not contain video track index {track_index}")
    new_track = video_entries[insertion_offset].find("Sm2TiTrack")
    new_track_id = new_track.get("DbId")
    actual_video_order = _video_track_order(root)
    expected_video_order = (
        source_video_order[:insertion_offset]
        + [(new_track_id, track_name)]
        + source_video_order[insertion_offset:]
    )
    if actual_video_order != expected_video_order:
        raise DrtPatchError("source video track order or names changed during insertion")
    if new_track.findtext("UserDefinedName") != track_name:
        raise DrtPatchError("output adjustment track name failed read-back")
    if new_track.findtext("Sequence") != sequence_id:
        raise DrtPatchError("output adjustment track references the wrong sequence")
    item_wrappers = new_track.find("Items").findall("Element")
    if len(item_wrappers) != 1 or len(item_wrappers[0]) != 1:
        raise DrtPatchError("output adjustment track does not contain exactly one item")
    clip = item_wrappers[0][0]
    if clip.tag != "Sm2TiGenerator" or clip.findtext("PrettyType") != "Adjustment Clip":
        raise DrtPatchError("output item is not a native Adjustment Clip generator")
    if clip.findtext("Start") != str(start_frame) or clip.findtext("Duration") != str(end_frame - start_frame):
        raise DrtPatchError("output Adjustment Clip range failed read-back")
    if _sequence_extent(root, Path("output.drt")) != sequence_extent:
        raise DrtPatchError("output sequence extent changed")
    return new_track_id, clip.get("DbId")


def patch_drt(
    source_path: str | os.PathLike[str],
    template_path: str | os.PathLike[str],
    output_path: str | os.PathLike[str],
    start_frame: int,
    end_frame: int,
    *,
    track_name: str = "ZOOM FOCUS",
    track_index: int = 2,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Build a DRT with one Adjustment Clip on a newly inserted video track.

    ``start_frame`` is inclusive and ``end_frame`` is exclusive. The function
    inserts at the one-based ``track_index`` (default V2); ``track_index`` may
    be one past the current final track to append. The function
    returns a JSON-serializable summary and raises :class:`DrtPatchError` if any
    input is ambiguous or fails read-back validation.
    """
    source = Path(source_path).expanduser().resolve()
    template = Path(template_path).expanduser().resolve()
    output = Path(output_path).expanduser().resolve()
    if isinstance(start_frame, bool) or not isinstance(start_frame, int):
        raise DrtPatchError("start_frame must be an integer frame number")
    if isinstance(end_frame, bool) or not isinstance(end_frame, int):
        raise DrtPatchError("end_frame must be an integer frame number")
    if start_frame < 0 or end_frame <= start_frame:
        raise DrtPatchError("range must satisfy 0 <= start_frame < end_frame")
    if not track_name or track_name != track_name.strip():
        raise DrtPatchError("track_name must be non-empty and have no leading or trailing spaces")
    if isinstance(track_index, bool) or not isinstance(track_index, int):
        raise DrtPatchError("track_index must be a one-based integer video track index")
    if track_index < 1:
        raise DrtPatchError("track_index must be at least 1")
    if output in (source, template):
        raise DrtPatchError("output path must differ from both input paths")
    if output.exists():
        raise DrtPatchError(f"output path already exists: {output}")
    if not source.is_file():
        raise DrtPatchError(f"source DRT does not exist or is not a file: {source}")
    if not template.is_file():
        raise DrtPatchError(f"template DRT does not exist or is not a file: {template}")
    if not output.parent.is_dir():
        raise DrtPatchError(f"output directory does not exist: {output.parent}")

    source_payloads, source_infos, source_comment = _read_archive(source)
    template_payloads, _template_infos, _template_comment = _read_archive(template)
    source_seq_member = _sequence_member(source_payloads, source)
    template_seq_member = _sequence_member(template_payloads, template)
    source_root = _parse_xml(source_payloads[source_seq_member], f"{source}!/{source_seq_member}")
    template_root = _parse_xml(
        template_payloads[template_seq_member], f"{template}!/{template_seq_member}"
    )
    if source_root.tag != "Sm2SequenceContainer" or template_root.tag != "Sm2SequenceContainer":
        raise DrtPatchError("sequence XML root is not a Sm2SequenceContainer")

    source_sequence_id = _video_sequence_id(source_root, "VideoTrackVec", source)
    _video_sequence_id(template_root, "VideoTrackVec", template)
    source_extent = _sequence_extent(source_root, source)
    if end_frame > source_extent:
        raise DrtPatchError(
            f"requested end frame {end_frame} exceeds sequence extent {source_extent}"
        )

    source_video_vector = source_root.find("VideoTrackVec")
    source_video_entries = source_video_vector.findall("Element")
    source_video_order = _video_track_order(source_root)
    source_track_counts = {
        vector_name: len(source_root.find(vector_name).findall("Element"))
        for vector_name in TRACK_VECTORS
    }
    if source_track_counts["VideoTrackVec"] == 0:
        raise DrtPatchError(f"source has no video tracks: {source}")
    if track_index > source_track_counts["VideoTrackVec"] + 1:
        raise DrtPatchError(
            f"track_index {track_index} is out of range; choose 1 through "
            f"{source_track_counts['VideoTrackVec'] + 1}"
        )
    for wrapper in source_video_entries:
        track = wrapper.find("Sm2TiTrack")
        existing_name = track.findtext("UserDefinedName") or ""
        if existing_name.casefold() == track_name.casefold():
            raise DrtPatchError(
                f"source already has a video track named {track_name!r}; refusing duplicate track name"
            )

    template_wrapper, _template_track, _template_item_wrapper, _template_clip = (
        _select_adjustment_template(template_root, template)
    )
    source_signatures = _item_signatures(source_root)
    used_ids = _all_archive_dbids(source_payloads, source) | _all_archive_dbids(
        template_payloads, template
    )
    new_wrapper = copy.deepcopy(template_wrapper)
    new_track = new_wrapper.find("Sm2TiTrack")
    new_track.find("Sequence").text = source_sequence_id
    new_track.find("UserDefinedName").text = track_name
    new_items = new_track.find("Items").findall("Element")
    if len(new_items) != 1 or len(new_items[0]) != 1:
        raise DrtPatchError("selected template track is not isolated to one item")
    new_clip = new_items[0][0]
    new_clip.find("Start").text = str(start_frame)
    new_clip.find("Duration").text = str(end_frame - start_frame)
    for element in new_track.iter():
        if element.get("DbId"):
            element.set("DbId", _fresh_dbid(used_ids))
    insertion_offset = track_index - 1
    if insertion_offset < len(source_video_vector):
        new_wrapper.tail = source_video_vector[insertion_offset].tail
    elif len(source_video_vector):
        new_wrapper.tail = source_video_vector[-1].tail
    source_video_vector.insert(insertion_offset, new_wrapper)

    changed_sequence = _serialize_xml(source_root)
    output_payloads = dict(source_payloads)
    output_payloads[source_seq_member] = changed_sequence
    archive_bytes = _build_archive(
        output_payloads, source_infos, source_comment, source_seq_member, changed_sequence
    )
    new_track_id, new_clip_id = _verify_archive_bytes(
        archive_bytes,
        source_signatures,
        source_track_counts,
        source_video_order,
        source_seq_member,
        source_sequence_id,
        track_name,
        track_index,
        start_frame,
        end_frame,
        source_extent,
    )
    dry_summary = {
        "source_path": str(source),
        "template_path": str(template),
        "output_path": str(output),
        "dry_run": bool(dry_run),
        "sequence_id": source_sequence_id,
        "sequence_end_frame": source_extent,
        "inserted_range": [start_frame, end_frame],
        "inserted_duration_frames": end_frame - start_frame,
        "track_name": track_name,
        "track_index": track_index,
        "inserted_track_id": new_track_id,
        "inserted_clip_id": new_clip_id,
        "source_video_tracks": source_track_counts["VideoTrackVec"],
        "output_video_tracks": source_track_counts["VideoTrackVec"] + 1,
        "source_track_counts": source_track_counts,
        "output_track_counts": {
            vector_name: count + (1 if vector_name == "VideoTrackVec" else 0)
            for vector_name, count in source_track_counts.items()
        },
        "validation": {
            "archive_crc": "passed",
            "source_track_items": "unchanged",
            "sequence_extent": "unchanged",
            "track_counts": "passed",
        },
    }
    if not dry_run:
        created_output = False
        try:
            with output.open("xb") as handle:
                created_output = True
                written_size = handle.write(archive_bytes)
            if written_size != len(archive_bytes):
                raise DrtPatchError(
                    f"incomplete write to output DRT {output}: {written_size} of {len(archive_bytes)} bytes"
                )
            written_payloads, _written_infos, _written_comment = _read_archive(output)
            if written_payloads.get(source_seq_member) != changed_sequence:
                raise DrtPatchError(f"output sequence failed disk read-back: {output}")
            _verify_archive_bytes(
                output.read_bytes(),
                source_signatures,
                source_track_counts,
                source_video_order,
                source_seq_member,
                source_sequence_id,
                track_name,
                track_index,
                start_frame,
                end_frame,
                source_extent,
            )
        except FileExistsError as exc:
            raise DrtPatchError(f"output path already exists: {output}") from exc
        except (DrtPatchError, OSError) as exc:
            if created_output:
                output.unlink(missing_ok=True)
            if isinstance(exc, DrtPatchError):
                raise
            raise DrtPatchError(f"cannot write output DRT {output}: {exc}") from exc
    return dry_summary


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Insert a native Adjustment Clip into an exported Resolve .drt offline.",
        epilog=(
            "Example: python scripts/drt_focus_track.py source.drt template.drt output.drt "
            "--start-frame 1200 --end-frame 1320 --dry-run"
        ),
    )
    parser.add_argument("source", help="source timeline .drt export")
    parser.add_argument("template", help=".drt export containing one isolated native Adjustment Clip")
    parser.add_argument("output", help="new output .drt path; must not already exist")
    parser.add_argument("--start-frame", type=int, required=True, help="inclusive start frame")
    parser.add_argument("--end-frame", type=int, required=True, help="exclusive end frame")
    parser.add_argument("--track-name", default="ZOOM FOCUS", help="name for the new video track")
    parser.add_argument(
        "--track-index",
        type=int,
        default=2,
        help="one-based insertion position (default: 2/V2; use current count + 1 to append)",
    )
    parser.add_argument("--dry-run", action="store_true", help="validate and print summary without writing")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    try:
        summary = patch_drt(
            args.source,
            args.template,
            args.output,
            args.start_frame,
            args.end_frame,
            track_name=args.track_name,
            track_index=args.track_index,
            dry_run=args.dry_run,
        )
    except DrtPatchError as exc:
        parser.exit(2, f"error: {exc}\n")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
