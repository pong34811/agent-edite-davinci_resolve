import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.drt_clone_subtitle_style import clone_styled_subtitle_track


def _varint(value):
    out = bytearray()
    while value >= 0x80:
        out.append((value & 0x7F) | 0x80)
        value >>= 7
    out.append(value)
    return bytes(out)


def _fields_blob(start):
    payload = _varint((21 << 3) | 0) + _varint(start)
    return ((2).to_bytes(4, "big") + len(payload).to_bytes(4, "big") + payload).hex()


def _caption(dbid, start, duration, name):
    item = ET.Element("Sm2TiGenerator", {"DbId": dbid})
    ET.SubElement(item, "FieldsBlob").text = _fields_blob(start)
    ET.SubElement(item, "Name").text = name
    ET.SubElement(item, "Start").text = str(start)
    ET.SubElement(item, "Duration").text = str(duration)
    return item


def _track(dbid, seq, style, items=()):
    track = ET.Element("Sm2TiTrack", {"DbId": dbid})
    ET.SubElement(track, "FieldsBlob").text = style
    ET.SubElement(track, "Sequence").text = seq
    vec = ET.SubElement(track, "Items")
    for item in items:
        ET.SubElement(vec, "Element").append(item)
    return track


def _drt(path, seq, sub_style, captions):
    root = ET.Element("Sm2SequenceContainer", {"DbId": seq})
    ET.SubElement(ET.SubElement(root, "VideoTrackVec"), "Element").append(_track(seq + "-v1", seq, "video"))
    ET.SubElement(root, "AudioTrackVec")
    ET.SubElement(ET.SubElement(root, "SubtitleTrackVec"), "Element").append(_track(seq + "-s1", seq, sub_style, captions))
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("project.xml", b"<Project DbId='p'/>")
        z.writestr("assets/opaque.bin", b"keep")
        z.writestr("SeqContainer/sequence.xml", ET.tostring(root, encoding="utf-8", xml_declaration=True))
    return path


def _subtitle_track(path):
    with zipfile.ZipFile(path) as z:
        root = ET.fromstring(z.read("SeqContainer/sequence.xml"))
        assert z.read("assets/opaque.bin") == b"keep"
    tracks = root.find("SubtitleTrackVec").findall("Element")
    assert len(tracks) == 1
    return tracks[0].find("Sm2TiTrack")


def test_cues_move_into_the_styled_track(tmp_path):
    src = _drt(tmp_path / "src.drt", "seq-src", "default-style", [_caption("c1", 10, 5, "old")])
    styled = _drt(tmp_path / "styled.drt", "seq-ref", "mitr-style", [_caption("t1", 100, 20, "template")])
    out = tmp_path / "out.drt"
    cues = [(0, 50, "ทุกคน"), (82, 120, "นี่เป็นวันแรก")]
    assert clone_styled_subtitle_track(src, styled, out, cues) == 2
    track = _subtitle_track(out)
    assert track.findtext("FieldsBlob") == "mitr-style"
    assert track.findtext("Sequence") == "seq-src"
    items = [e[0] for e in track.find("Items").findall("Element")]
    assert [(int(g.findtext("Start")), int(g.findtext("Start")) + int(g.findtext("Duration")), g.findtext("Name")) for g in items] == cues
    assert [g.findtext("FieldsBlob") for g in items] == [_fields_blob(0), _fields_blob(82)]
    ids = [x.get("DbId") for x in track.iter() if x.get("DbId")]
    assert len(ids) == len(set(ids)) and not {"t1", "seq-ref-s1"} & set(ids)


def test_refuses_to_overwrite_and_bad_cues(tmp_path):
    src = _drt(tmp_path / "src.drt", "seq-src", "default-style", [])
    styled = _drt(tmp_path / "styled.drt", "seq-ref", "mitr-style", [_caption("t1", 0, 20, "template")])
    out = tmp_path / "out.drt"
    out.write_bytes(b"x")
    with pytest.raises(FileExistsError):
        clone_styled_subtitle_track(src, styled, out, [(0, 10, "a")])
    with pytest.raises(ValueError):
        clone_styled_subtitle_track(src, styled, tmp_path / "o2.drt", [(10, 10, "zero length")])


def test_styled_track_needs_a_template_cue(tmp_path):
    src = _drt(tmp_path / "src.drt", "seq-src", "default-style", [])
    styled = _drt(tmp_path / "styled.drt", "seq-ref", "mitr-style", [])
    with pytest.raises(ValueError, match="template"):
        clone_styled_subtitle_track(src, styled, tmp_path / "out.drt", [(0, 10, "a")])
