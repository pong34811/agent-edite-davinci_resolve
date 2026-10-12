import copy
import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.drt_add_native_subtitle import SubtitleDrtError, add_native_subtitle


def _varint(value):
    result = bytearray()
    while value >= 0x80:
        result.append((value & 0x7F) | 0x80)
        value >>= 7
    result.append(value)
    return bytes(result)


def _fields_blob(start):
    # Protobuf field 21, varint wire type, in the known Resolve envelope.
    payload = _varint((21 << 3) | 0) + _varint(start)
    return (2).to_bytes(4, "big") + len(payload).to_bytes(4, "big") + payload


def _caption(dbid, start, duration, name):
    item = ET.Element("Sm2TiGenerator", {"DbId": dbid})
    ET.SubElement(item, "FieldsBlob").text = _fields_blob(start).hex()
    ET.SubElement(item, "PrettyType").text = "Subtitle"
    ET.SubElement(item, "Name").text = name
    ET.SubElement(item, "Start").text = str(start)
    ET.SubElement(item, "Duration").text = str(duration)
    ET.SubElement(item, "In").text = "0"
    return item


def _track(dbid, items=()):
    track = ET.Element("Sm2TiTrack", {"DbId": dbid})
    ET.SubElement(track, "FieldsBlob").text = "track-fields"
    ET.SubElement(track, "Type").text = "2"
    item_vec = ET.SubElement(track, "Items")
    for item in items:
        wrapper = ET.SubElement(item_vec, "Element")
        wrapper.append(item)
    ET.SubElement(track, "FusionCompHolderItems")
    ET.SubElement(track, "UserDefinedName").text = ""
    return track


def _write_fixture(path, target_items=(), other_items=()):
    root = ET.Element("Sm2SequenceContainer", {"DbId": "sequence-id"})
    for vector_name in ("VideoTrackVec", "AudioTrackVec", "SubtitleTrackVec", "GeometryTrackVec"):
        vector = ET.SubElement(root, vector_name)
        if vector_name == "SubtitleTrackVec":
            for track in (
                _track("template-track", [_caption("template-caption", 5, 8, "เดิม")]),
                _track("empty-target", target_items),
                _track("other-track", other_items),
            ):
                wrapper = ET.SubElement(vector, "Element")
                wrapper.append(track)
    ET.SubElement(root, "DbSavedTime").text = "0"
    seq = ET.tostring(root, encoding="utf-8", xml_declaration=True)
    with zipfile.ZipFile(path, "w") as archive:
        archive.comment = b"fixture-comment"
        archive.writestr("project.xml", b"<Project DbId='project-id'/>")
        archive.writestr("assets/opaque.bin", b"preserve this member")
        archive.writestr("SeqContainer/sequence.xml", seq)
    return path


def _write_srt(path, cue="1\n00:00:01,000 --> 00:00:02,000\nใหม่\n"):
    path.write_text(cue, encoding="utf-8")
    return path


def _read_root(path):
    with zipfile.ZipFile(path) as archive:
        return ET.fromstring(archive.read("SeqContainer/sequence.xml"))


def test_adds_one_native_cue_and_preserves_other_tracks_and_archive_members(tmp_path):
    source = _write_fixture(tmp_path / "source.drt")
    srt = _write_srt(tmp_path / "cue.srt")
    output = tmp_path / "output.drt"
    before = _read_root(source)
    before_tracks = [
        ET.tostring(wrapper, encoding="utf-8")
        for vector_name in ("VideoTrackVec", "AudioTrackVec", "SubtitleTrackVec", "GeometryTrackVec")
        for index, wrapper in enumerate(before.find(vector_name).findall("Element"), 1)
        if (vector_name, index) != ("SubtitleTrackVec", 2)
    ]

    result = add_native_subtitle(
        source, output, srt,
        target_track_index=2, template_track_index=1, fps=25, timeline_end=60,
    )

    root = _read_root(output)
    target = root.find("SubtitleTrackVec").findall("Element")[1].find("Sm2TiTrack")
    item = target.find("Items/Element/Sm2TiGenerator")
    assert (item.findtext("Name"), item.findtext("Start"), item.findtext("Duration")) == ("ใหม่", "25", "25")
    assert item.get("DbId") not in {element.get("DbId") for element in before.iter()}
    after_tracks = [
        ET.tostring(wrapper, encoding="utf-8")
        for vector_name in ("VideoTrackVec", "AudioTrackVec", "SubtitleTrackVec", "GeometryTrackVec")
        for index, wrapper in enumerate(root.find(vector_name).findall("Element"), 1)
        if (vector_name, index) != ("SubtitleTrackVec", 2)
    ]
    assert before_tracks == after_tracks
    with zipfile.ZipFile(source) as src, zipfile.ZipFile(output) as out:
        assert out.testzip() is None
        assert out.comment == b"fixture-comment"
        assert out.namelist() == src.namelist()
        assert out.read("project.xml") == src.read("project.xml")
        assert out.read("assets/opaque.bin") == src.read("assets/opaque.bin")
    assert result["readback"] == ("ใหม่", 25, 50)
    assert result["archive_crc"] == "passed"


@pytest.mark.parametrize(
    ("kwargs", "other_items", "target_items", "srt_text", "message"),
    [
        ({"timeline_end": 49}, (), (), None, "beyond timeline_end"),
        ({}, [_caption("collision", 30, 10, "ชน")], (), None, "overlaps subtitle track 3"),
        ({}, (), [_caption("occupied", 1, 2, "occupied")], None, "not empty"),
        ({}, (), (), "1\n00:00:01,000 --> 00:00:02,000\nหนึ่ง\n\n2\n00:00:03,000 --> 00:00:04,000\nสอง\n", "exactly one SRT cue"),
    ],
)
def test_rejects_invalid_addition_without_creating_output(
    tmp_path, kwargs, other_items, target_items, srt_text, message
):
    source = _write_fixture(tmp_path / "source.drt", target_items, other_items)
    srt = _write_srt(tmp_path / "cue.srt", srt_text or "1\n00:00:01,000 --> 00:00:02,000\nใหม่\n")
    output = tmp_path / "output.drt"
    with pytest.raises(SubtitleDrtError, match=message):
        add_native_subtitle(
            source, output, srt,
            target_track_index=2, template_track_index=1, fps=25, **kwargs,
        )
    assert not output.exists()


def test_rejects_existing_output_and_source_as_output(tmp_path):
    source = _write_fixture(tmp_path / "source.drt")
    srt = _write_srt(tmp_path / "cue.srt")
    with pytest.raises(SubtitleDrtError, match="new path"):
        add_native_subtitle(
            source, source, srt,
            target_track_index=2, template_track_index=1, fps=25,
        )
    output = tmp_path / "existing.drt"
    output.write_bytes(b"keep")
    with pytest.raises(SubtitleDrtError, match="new path"):
        add_native_subtitle(
            source, output, srt,
            target_track_index=2, template_track_index=1, fps=25,
        )
    assert output.read_bytes() == b"keep"
