"""Offline DRT patch: one new video track holding several native Adjustment Clips.

Builds on ``drt_focus_track.patch_drt`` (one clip on one new track, source tracks verified unchanged) and
clones that clip for every further range. Ranges are half-open ``[start, end)`` frames and must not overlap.

    python -m scripts.drt_focus_multi source.drt template.drt output.drt --ranges 600:759,792:1043 --track-name "VTuber Zoom"

Does not connect to Resolve. The output is only a candidate: import it and read the track back before trusting it.
"""
from __future__ import annotations

import argparse
import copy
import json
import tempfile
from pathlib import Path

from scripts.drt_focus_track import (
    DrtPatchError, _all_archive_dbids, _build_archive, _fresh_dbid, _item_signatures,
    _parse_xml, _read_archive, _sequence_member, _serialize_xml, patch_drt,
)


def patch_multi(source, template, output, ranges, *, track_name="VTuber Zoom"):
    ranges = [(int(s), int(e)) for s, e in ranges]
    if not ranges:
        raise DrtPatchError("no ranges given")
    for (s, e), (s2, _) in zip(ranges, ranges[1:] + [(10**12, 0)]):
        if not (0 <= s < e <= s2):
            raise DrtPatchError(f"bad or overlapping range {s}-{e}")
    source, template, output = (Path(p).expanduser().resolve() for p in (source, template, output))
    if output.exists():
        raise DrtPatchError(f"output path already exists: {output}")

    src_payloads, _, _ = _read_archive(source)
    src_member = _sequence_member(src_payloads, source)
    src_root = _parse_xml(src_payloads[src_member], str(source))
    src_sigs = _item_signatures(src_root)
    n_video = len(src_root.find("VideoTrackVec").findall("Element"))

    with tempfile.TemporaryDirectory() as tmp:
        stage = Path(tmp) / "stage.drt"
        patch_drt(source, template, stage, ranges[0][0], ranges[0][1], track_name=track_name, track_index=n_video + 1)
        payloads, infos, comment = _read_archive(stage)
        member = _sequence_member(payloads, stage)
        root = _parse_xml(payloads[member], str(stage))
        used = _all_archive_dbids(payloads, stage)
        wrapper = next(w for w in root.find("VideoTrackVec").findall("Element")
                       if w.find("Sm2TiTrack").findtext("UserDefinedName") == track_name)
        items = wrapper.find("Sm2TiTrack").find("Items")
        first = items.findall("Element")
        if len(first) != 1:
            raise DrtPatchError("staged track does not hold exactly one clip")
        for s, e in ranges[1:]:
            clone = copy.deepcopy(first[0])
            clip = clone[0]
            clip.find("Start").text = str(s)
            clip.find("Duration").text = str(e - s)
            for el in clone.iter():
                if el.get("DbId"):
                    el.set("DbId", _fresh_dbid(used))
            clone.tail = first[0].tail
            items.append(clone)

        new_track = wrapper.find("Sm2TiTrack")
        got = [(int(x[0].findtext("Start")), int(x[0].findtext("Start")) + int(x[0].findtext("Duration")))
               for x in new_track.find("Items").findall("Element")]
        if got != ranges:
            raise DrtPatchError(f"range readback {got} != {ranges}")
        sigs = _item_signatures(root)
        for tid, sig in src_sigs.items():
            if sigs.get(tid) != sig:
                raise DrtPatchError(f"source track {tid} changed")

        data = _serialize_xml(root)
        archive = _build_archive(payloads, infos, comment, member, data)
        output.write_bytes(archive)
    return {"output": str(output), "ranges": got, "track_name": track_name, "track_index": n_video + 1}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("source")
    ap.add_argument("template")
    ap.add_argument("output")
    ap.add_argument("--ranges", required=True, help="start:end,start:end (half-open frames)")
    ap.add_argument("--track-name", default="VTuber Zoom")
    a = ap.parse_args(argv)
    rng = [tuple(int(v) for v in part.split(":")) for part in a.ranges.split(",")]
    print(json.dumps(patch_multi(a.source, a.template, a.output, rng, track_name=a.track_name), ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
