"""Replace every clip on a named Adjustment Clip track in an exported .drt with fresh template clips.

Example::

    python scripts/drt_rebuild_focus_track.py source.drt adjustment-template.drt rebuilt.drt \
        --track-name "VTuber Zoom" --ranges "[[0,229],[5104,5352]]"

Use it to put N zoom clips on a track in one import (InsertGeneratorIntoTimeline lands on V1 on
21.1.0.17), or to rebuild a track whose clips had their heads dragged earlier (those keep a Fusion
comp sized to the old length and fail to render the added head). Ranges are half-open
``[start, end)``. Every other track is byte-compared against the source. Add ``--create`` to insert
the track first (via ``drt_focus_track.patch_drt``) when the source does not have it yet.

Fusion Transform values are not carried in the template: set them after import (for example with
``retune_vtuber_zoom.py``) and read them back. This utility edits DRT files offline and does not
connect to Resolve.
"""

from __future__ import annotations

import argparse
import copy
import io
import json
import os
import sys
import tempfile
import zipfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from scripts import drt_focus_track as d  # noqa: E402
from scripts.drt_focus_track import DrtPatchError  # noqa: E402


def validate_ranges(ranges: Any) -> list[tuple[int, int]]:
    """Return ranges as int pairs, sorted input required, no overlap (touching is allowed)."""
    out = []
    for r in ranges:
        if len(r) != 2 or any(isinstance(v, bool) or not isinstance(v, int) for v in r):
            raise DrtPatchError(f"range must be two integer frames: {r!r}")
        s, e = r
        if s < 0 or e <= s:
            raise DrtPatchError(f"range must satisfy 0 <= start < end: {r!r}")
        out.append((s, e))
    if not out:
        raise DrtPatchError("at least one range is required")
    for (_, e), (s2, _) in zip(out, out[1:]):
        if s2 < e:
            raise DrtPatchError("ranges must be in time order and must not overlap")
    return out


def _named_tracks(root, name):
    return [w.find("Sm2TiTrack") for w in root.find("VideoTrackVec").findall("Element")
            if (w.find("Sm2TiTrack").findtext("UserDefinedName") or "") == name]


def _track_ranges(track) -> list[tuple[int, int]]:
    got = []
    for el in track.find("Items").findall("Element"):
        s = int(el[0].findtext("Start"))
        got.append((s, s + int(el[0].findtext("Duration"))))
    return got


def rebuild_track(
    source_path: str | os.PathLike[str],
    template_path: str | os.PathLike[str],
    output_path: str | os.PathLike[str],
    ranges,
    *,
    track_name: str = "VTuber Zoom",
    create: bool = False,
    track_index: int = 2,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Write ``output_path`` with the named track holding exactly one fresh Adjustment Clip per range."""
    source = Path(source_path).expanduser().resolve()
    template = Path(template_path).expanduser().resolve()
    output = Path(output_path).expanduser().resolve()
    ranges = validate_ranges(ranges)
    if output in (source, template):
        raise DrtPatchError("output path must differ from both input paths")
    if output.exists() and not dry_run:
        raise DrtPatchError(f"output already exists: {output}")

    with tempfile.TemporaryDirectory() as tmp:
        base = source
        if create:
            base = Path(tmp) / "stage1.drt"
            d.patch_drt(source, template, base, ranges[0][0], ranges[0][1],
                        track_name=track_name, track_index=track_index)
        payloads, infos, comment = d._read_archive(base)
        member = d._sequence_member(payloads, base)
        root = d._parse_xml(payloads[member], str(base))

    src_payloads = d._read_archive(source)[0]
    src_root = d._parse_xml(src_payloads[d._sequence_member(src_payloads, source)], str(source))
    tpay = d._read_archive(template)[0]
    troot = d._parse_xml(tpay[d._sequence_member(tpay, template)], str(template))
    _, _, titem, _ = d._select_adjustment_template(troot, template)

    tracks = _named_tracks(root, track_name)
    if len(tracks) != 1:
        hint = " (use --create to add it)" if not tracks and not create else ""
        raise DrtPatchError(f"expected exactly one video track named {track_name!r}, found {len(tracks)}{hint}")
    track = tracks[0]
    items = track.find("Items")
    olds = items.findall("Element")
    if create and len(olds) != 1:
        raise DrtPatchError("created track should hold one clip")
    for el in olds:
        if el[0].tag != "Sm2TiGenerator" or el[0].findtext("PrettyType") != "Adjustment Clip":
            raise DrtPatchError(f"track {track_name!r} holds a non-Adjustment Clip item; refusing to replace it")
    previous = [] if create else _track_ranges(track)

    used = d._all_archive_dbids(payloads, base) | d._all_archive_dbids(tpay, template)
    tail = olds[0].tail if olds else titem.tail
    for el in olds:
        items.remove(el)
    for s, e in ranges:
        el = copy.deepcopy(titem)
        el[0].find("Start").text = str(s)
        el[0].find("Duration").text = str(e - s)
        for x in el.iter():
            if x.get("DbId"):
                x.set("DbId", d._fresh_dbid(used))
        el.tail = tail
        items.append(el)

    data = d._build_archive(payloads, infos, comment, member, d._serialize_xml(root))

    # Read back from the bytes we are about to write.
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        check_root = d._parse_xml(z.read(member), "output")
    got = _track_ranges(_named_tracks(check_root, track_name)[0])
    if got != ranges:
        raise DrtPatchError(f"read-back ranges {got} != wanted {ranges}")
    rebuilt_id = track.get("DbId")
    before = d._item_signatures(src_root)
    after = d._item_signatures(check_root)
    for tid, sig in before.items():
        if tid != rebuilt_id and after.get(tid) != sig:
            raise DrtPatchError(f"track {tid} changed")
    ids = [x.get("DbId") for x in check_root.iter() if x.get("DbId")]
    if len(ids) != len(set(ids)):
        raise DrtPatchError("duplicate DbId in output")
    if d._sequence_extent(check_root, output) > max(d._sequence_extent(src_root, source), ranges[-1][1]):
        raise DrtPatchError("output sequence is longer than expected")

    if not dry_run:
        output.write_bytes(data)
    return {
        "track_name": track_name,
        "created": create,
        "previous_ranges": [list(r) for r in previous],
        "ranges": [list(r) for r in ranges],
        "output": None if dry_run else str(output),
        "dry_run": dry_run,
    }


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Replace all clips on a named Adjustment Clip track in a .drt offline.")
    p.add_argument("source", help="source timeline .drt export")
    p.add_argument("template", help=".drt export containing one isolated native Adjustment Clip")
    p.add_argument("output", help="new output .drt path; must not already exist")
    p.add_argument("--ranges", required=True, help='JSON [[start,end],...] (end exclusive), in time order')
    p.add_argument("--track-name", default="VTuber Zoom")
    p.add_argument("--create", action="store_true", help="insert the track first when the source lacks it")
    p.add_argument("--track-index", type=int, default=2, help="one-based position for --create (default V2)")
    p.add_argument("--dry-run", action="store_true")
    a = p.parse_args(argv)
    try:
        summary = rebuild_track(a.source, a.template, a.output, json.loads(a.ranges), track_name=a.track_name,
                                create=a.create, track_index=a.track_index, dry_run=a.dry_run)
    except (DrtPatchError, json.JSONDecodeError) as exc:
        p.exit(2, f"error: {exc}\n")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
