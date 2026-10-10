import copy
import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.drt_focus_track import DrtPatchError, patch_drt


def _timeline_item(tag, dbid, start, duration, name=""):
    item = ET.Element(tag, {"DbId": dbid})
    ET.SubElement(item, "FieldsBlob").text = "0000"
    ET.SubElement(item, "PrettyType").text = "Adjustment Clip" if tag == "Sm2TiGenerator" else ""
    ET.SubElement(item, "Name").text = name
    ET.SubElement(item, "Start").text = str(start)
    ET.SubElement(item, "Duration").text = str(duration)
    ET.SubElement(item, "LinkedItemSync")
    ET.SubElement(item, "WasDisbanded").text = "false"
    if tag == "Sm2TiGenerator":
        ET.SubElement(item, "In")
    return item


def _track(dbid, sequence_id, track_type, name, items):
    track = ET.Element("Sm2TiTrack", {"DbId": dbid})
    ET.SubElement(track, "FieldsBlob").text = "0000"
    ET.SubElement(track, "Type").text = str(track_type)
    ET.SubElement(track, "SubType").text = "0"
    ET.SubElement(track, "Flags").text = "0"
    ET.SubElement(track, "Sequence").text = sequence_id
    item_vec = ET.SubElement(track, "Items")
    for item in items:
        wrapper = ET.SubElement(item_vec, "Element")
        wrapper.append(item)
    ET.SubElement(track, "FusionCompHolderItems")
    ET.SubElement(track, "UserDefinedName").text = name
    ET.SubElement(track, "LayersVec")
    return track


def _sequence_xml(sequence_id, video_tracks, audio_tracks=(), subtitle_tracks=()):
    root = ET.Element("Sm2SequenceContainer", {"DbId": f"container-{sequence_id}"})
    ET.SubElement(root, "FieldsBlob").text = "0000"
    for vector_name, tracks in (
        ("VideoTrackVec", video_tracks),
        ("AudioTrackVec", audio_tracks),
        ("SubtitleTrackVec", subtitle_tracks),
        ("GeometryTrackVec", ()),
    ):
        vector = ET.SubElement(root, vector_name)
        for track in tracks:
            wrapper = ET.SubElement(vector, "Element")
            wrapper.append(copy.deepcopy(track))
    ET.SubElement(root, "DbSavedTime").text = "0"
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def _write_drt(path, sequence_id, video_tracks, audio_tracks=(), subtitle_tracks=()):
    path = Path(path)
    seq_name = f"SeqContainer/{sequence_id}.xml"
    with zipfile.ZipFile(path, "w") as archive:
        for name, payload in (
            ("project.xml", b"<Project DbId='project-id'/>"),
            ("MediaPool/Master/MpFolder.xml", b"<Folder DbId='folder-id'/>") ,
            (
                seq_name,
                _sequence_xml(sequence_id, video_tracks, audio_tracks, subtitle_tracks),
            ),
        ):
            info = zipfile.ZipInfo(name, date_time=(2025, 1, 2, 3, 4, 6))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o600 << 16
            archive.writestr(info, payload)
    return path


@pytest.fixture
def drt_pair(tmp_path):
    source_sequence = "source-sequence"
    template_sequence = "template-sequence"
    source = _write_drt(
        tmp_path / "source.drt",
        source_sequence,
        [
            _track(
                "source-video-track",
                source_sequence,
                0,
                "",
                [_timeline_item("Sm2TiVideoClip", "source-video-item", 0, 200, "clip")],
            ),
            _track("source-reaction-track", source_sequence, 0, "REACTIONS", []),
        ],
        audio_tracks=[
            _track(
                "source-audio-track",
                source_sequence,
                1,
                "SFX",
                [_timeline_item("Sm2TiAudioClip", "source-audio-item", 100, 100, "audio")],
            )
        ],
        subtitle_tracks=[
            _track(
                "source-subtitle-track",
                source_sequence,
                2,
                "",
                [_timeline_item("Sm2TiGenerator", "source-sub-item", 40, 30, "subtitle")],
            )
        ],
    )
    template = _write_drt(
        tmp_path / "template.drt",
        template_sequence,
        [
            _track(
                "template-focus-track",
                template_sequence,
                0,
                "ZOOM FOCUS",
                [_timeline_item("Sm2TiGenerator", "template-adjustment", 5, 20, "Adjustment Clip")],
            )
        ],
    )
    return source, template


def _read_sequence(path):
    with zipfile.ZipFile(path) as archive:
        name = next(name for name in archive.namelist() if name.startswith("SeqContainer/"))
        return ET.fromstring(archive.read(name))


def _item_signatures(root):
    signatures = {}
    for vector_name in ("VideoTrackVec", "AudioTrackVec", "SubtitleTrackVec", "GeometryTrackVec"):
        vector = root.find(vector_name)
        for wrapper in vector.findall("Element"):
            track = wrapper.find("Sm2TiTrack")
            items = track.find("Items")
            signatures[track.get("DbId")] = tuple(
                ET.tostring(item, encoding="utf-8") for item in items.findall("Element")
            )
    return signatures


def _video_track_order(root):
    return [
        (
            entry.find("Sm2TiTrack").get("DbId"),
            entry.findtext("Sm2TiTrack/UserDefinedName") or "",
        )
        for entry in root.find("VideoTrackVec").findall("Element")
    ]


def _all_dbids(root):
    return [element.get("DbId") for element in root.iter() if element.get("DbId")]


def test_inserts_native_adjustment_clip_on_new_track_and_preserves_source(drt_pair, tmp_path):
    source, template = drt_pair
    output = tmp_path / "patched.drt"
    before = _read_sequence(source)
    before_signatures = _item_signatures(before)
    before_order = _video_track_order(before)

    summary = patch_drt(source, template, output, start_frame=60, end_frame=91)

    after = _read_sequence(output)
    video_vector = after.find("VideoTrackVec")
    assert len(video_vector.findall("Element")) == 3
    new_track = video_vector.findall("Element")[1].find("Sm2TiTrack")
    assert new_track.findtext("UserDefinedName") == "ZOOM FOCUS"
    assert _video_track_order(after) == [before_order[0], (new_track.get("DbId"), "ZOOM FOCUS"), before_order[1]]
    assert new_track.findtext("Sequence") == before.find("VideoTrackVec/Element/Sm2TiTrack/Sequence").text
    clip = new_track.find("Items/Element/Sm2TiGenerator")
    assert clip is not None
    assert clip.findtext("PrettyType") == "Adjustment Clip"
    assert clip.findtext("Start") == "60"
    assert clip.findtext("Duration") == "31"
    assert {key: value for key, value in _item_signatures(after).items() if key in before_signatures} == before_signatures
    assert _all_dbids(after).count(new_track.get("DbId")) == 1
    assert _all_dbids(after).count(clip.get("DbId")) == 1
    assert len(_all_dbids(after)) == len(set(_all_dbids(after)))
    assert summary["source_video_tracks"] == 2
    assert summary["output_video_tracks"] == 3
    assert summary["track_index"] == 2
    assert summary["sequence_end_frame"] == 200
    assert summary["inserted_range"] == [60, 91]

    with zipfile.ZipFile(source) as source_zip, zipfile.ZipFile(output) as output_zip:
        assert output_zip.testzip() is None
        assert output_zip.namelist() == source_zip.namelist()
        original_info = source_zip.getinfo("project.xml")
        copied_info = output_zip.getinfo("project.xml")
        assert copied_info.date_time == original_info.date_time
        assert copied_info.compress_type == original_info.compress_type
        assert copied_info.external_attr == original_info.external_attr
        for name in source_zip.namelist():
            if name != next(name for name in source_zip.namelist() if name.startswith("SeqContainer/")):
                assert output_zip.read(name) == source_zip.read(name)


def test_can_append_at_current_track_count_plus_one(drt_pair, tmp_path):
    source, template = drt_pair
    before_order = _video_track_order(_read_sequence(source))
    output = tmp_path / "appended.drt"

    summary = patch_drt(source, template, output, 60, 91, track_index=3)

    after = _read_sequence(output)
    new_track = after.find("VideoTrackVec").findall("Element")[-1].find("Sm2TiTrack")
    assert _video_track_order(after) == before_order + [(new_track.get("DbId"), "ZOOM FOCUS")]
    assert new_track.find("Items/Element/Sm2TiGenerator").findtext("PrettyType") == "Adjustment Clip"
    assert summary["track_index"] == 3


def test_dry_run_validates_without_creating_output(drt_pair, tmp_path):
    source, template = drt_pair
    output = tmp_path / "not-created.drt"

    summary = patch_drt(source, template, output, 0, 200, dry_run=True)

    assert summary["dry_run"] is True
    assert summary["sequence_end_frame"] == 200
    assert not output.exists()


@pytest.mark.parametrize("track_index", [0, 4])
def test_rejects_track_index_outside_insertable_range(drt_pair, tmp_path, track_index):
    source, template = drt_pair
    with pytest.raises(DrtPatchError, match="track_index"):
        patch_drt(source, template, tmp_path / "bad-index.drt", 0, 20, track_index=track_index)


@pytest.mark.parametrize("start_frame,end_frame", [(-1, 1), (10, 10), (20, 19), (0, 201)])
def test_rejects_invalid_or_out_of_sequence_ranges(drt_pair, tmp_path, start_frame, end_frame):
    source, template = drt_pair
    with pytest.raises(DrtPatchError):
        patch_drt(source, template, tmp_path / "bad.drt", start_frame, end_frame)


def test_rejects_existing_output_without_overwriting_it(drt_pair, tmp_path):
    source, template = drt_pair
    output = tmp_path / "existing.drt"
    output.write_bytes(b"keep this")

    with pytest.raises(DrtPatchError, match="already exists"):
        patch_drt(source, template, output, 0, 20)
    assert output.read_bytes() == b"keep this"


def test_rejects_existing_track_name_collision(drt_pair, tmp_path):
    source, template = drt_pair
    root = _read_sequence(source)
    video = root.find("VideoTrackVec")
    collision = _track("existing-focus", "source-sequence", 0, "zoom focus", [])
    wrapper = ET.SubElement(video, "Element")
    wrapper.append(collision)
    altered_source = tmp_path / "collision.drt"
    with zipfile.ZipFile(source) as original, zipfile.ZipFile(altered_source, "w") as changed:
        seq_name = next(name for name in original.namelist() if name.startswith("SeqContainer/"))
        for info in original.infolist():
            payload = original.read(info.filename)
            if info.filename == seq_name:
                payload = ET.tostring(root, encoding="utf-8", xml_declaration=True)
            changed.writestr(copy.copy(info), payload)

    with pytest.raises(DrtPatchError, match="track name"):
        patch_drt(altered_source, template, tmp_path / "collision-out.drt", 0, 20)


def test_rejects_ambiguous_adjustment_clip_template(drt_pair, tmp_path):
    source, template = drt_pair
    root = _read_sequence(template)
    video = root.find("VideoTrackVec")
    duplicate = copy.deepcopy(video.findall("Element")[0])
    track = duplicate.find("Sm2TiTrack")
    track.set("DbId", "template-focus-track-2")
    track.find("Items/Element/Sm2TiGenerator").set("DbId", "template-adjustment-2")
    video.append(duplicate)
    ambiguous = tmp_path / "ambiguous-template.drt"
    with zipfile.ZipFile(template) as original, zipfile.ZipFile(ambiguous, "w") as changed:
        seq_name = next(name for name in original.namelist() if name.startswith("SeqContainer/"))
        for info in original.infolist():
            payload = original.read(info.filename)
            if info.filename == seq_name:
                payload = ET.tostring(root, encoding="utf-8", xml_declaration=True)
            changed.writestr(copy.copy(info), payload)

    with pytest.raises(DrtPatchError, match="ambiguous"):
        patch_drt(source, ambiguous, tmp_path / "ambiguous-out.drt", 0, 20)
