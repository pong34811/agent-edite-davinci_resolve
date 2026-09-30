import pytest
from unittest.mock import MagicMock, call
from scripts.enrichment_engine import (
    CuePoint,
    PlacementItem,
    EnrichmentPlan,
    analyze_subtitle_cues,
    plan_timeline_enrichment,
    apply_enrichment_plan,
)


def test_analyze_subtitle_cues_punchlines():
    mock_subs = [
        {"name": "เยี่ยมเจอ", "start": 216000, "end": 216085},
        {"name": "55555 ไม่นะ", "start": 216500, "end": 216580},
        {"name": "อ๋อ เข้าใจแล้ว", "start": 217000, "end": 217060},
    ]
    cues = analyze_subtitle_cues(mock_subs)
    assert len(cues) >= 2
    types = [c.cue_type for c in cues]
    assert "shock" in types or "punchline" in types
    assert "cute" in types or "aha" in types


def test_analyze_subtitle_cues_categories():
    mock_subs = [
        {"name": "เห้ย ระเบิดบอสมาแล้ว", "start": 100, "end": 150},
        {"name": "อ้าว แป๊บนะ 555 ตลกจัง", "start": 200, "end": 260},
        {"name": "สวย รอดแล้ว โห", "start": 300, "end": 340},
        {"name": "ข้อความทั่วไป ไม่มีคำสำคัญ", "start": 400, "end": 450},
    ]
    cues = analyze_subtitle_cues(mock_subs)
    assert len(cues) == 3

    types = [c.cue_type for c in cues]
    assert "shock" in types
    assert "punchline" in types
    assert "cute" in types or "win" in types

    # Check suggested assets are populated
    for cue in cues:
        assert cue.suggested_sfx is not None
        assert cue.suggested_gif is not None


def test_plan_timeline_enrichment():
    timeline_info = {
        "name": "ขุดมั่วเจอเหล็กกองใหญ่_Minecraft-vdo",
        "start_frame": 216000,
        "end_frame": 222600,
        "fps": 60.0,
        "subtitles": [
            {"name": "เยี่ยมเจอ", "start": 216100, "end": 216180},
            {"name": "55555 ไม่นะ", "start": 217000, "end": 217080},
            {"name": "เห้ย ช่วยด้วย", "start": 218500, "end": 218580},
            {"name": "อ๋อ เข้าใจแล้ว", "start": 220000, "end": 220060},
        ],
    }

    mock_sfx_item = MagicMock()
    mock_sfx_item.GetName.return_value = "1_ตลกตบมุก_1.mp3"
    mock_bgm_item = MagicMock()
    mock_bgm_item.GetName.return_value = "NCSน่ารัก.mp3"
    mock_gif_item = MagicMock()
    mock_gif_item.GetName.return_value = "Reaction - Iconic Laugh.gif"

    asset_catalog = {
        "Enrichment_SFX": [mock_sfx_item],
        "Enrichment_BGM": [mock_bgm_item],
        "Enrichment_GIF": [mock_gif_item],
    }

    plan = plan_timeline_enrichment(timeline_info, asset_catalog)

    assert isinstance(plan, EnrichmentPlan)
    assert plan.timeline_name == "ขุดมั่วเจอเหล็กกองใหญ่_Minecraft-vdo"
    assert plan.timeline_start == 216000
    assert plan.timeline_end == 222600

    # 1. BGM verification
    assert plan.bgm_item is not None
    assert plan.bgm_item.track_type == "audio"
    assert plan.bgm_item.track_index == 3
    assert plan.bgm_item.start_frame == 216000
    assert plan.bgm_item.end_frame == 222600
    assert plan.bgm_item.properties.get("AudioVolume") == -23.0
    assert plan.bgm_item.fade_in_frames == 30  # 0.5s at 60fps
    assert plan.bgm_item.fade_out_frames == 60  # 1.0s at 60fps

    # 2. SFX verification
    assert len(plan.sfx_items) >= 2
    for sfx in plan.sfx_items:
        assert sfx.track_type == "audio"
        assert sfx.track_index == 2
        assert sfx.properties.get("AudioVolume") == -11.0
        assert sfx.start_frame >= 216000
        assert sfx.end_frame <= 222600

    # 3. GIF verification
    assert len(plan.gif_items) >= 1
    for gif in plan.gif_items:
        assert gif.track_type == "video"
        assert gif.track_index == 2
        assert gif.properties.get("ZoomX") == 0.55
        assert gif.properties.get("ZoomY") == 0.55
        assert gif.properties.get("Pan") == 0.0
        assert gif.properties.get("Tilt") == 0.0
        assert gif.start_frame >= 216000
        assert gif.end_frame <= 222600
        assert (gif.end_frame - gif.start_frame) <= 150  # <= 2.5s


def test_apply_enrichment_plan():
    mock_timeline = MagicMock()
    mock_timeline.GetName.return_value = "Test_Timeline_Minecraft-vdo"
    mock_timeline.GetTrackCount.side_effect = lambda track_type: 1 if track_type == "video" else 1

    mock_media_pool = MagicMock()
    created_clips = []

    def mock_append(clip_infos):
        res = []
        for info in clip_infos:
            item = MagicMock()
            props = {}
            item.SetProperty.side_effect = lambda k, v: props.update({k: v}) or True
            item.GetProperty.side_effect = lambda k: props.get(k)
            item._info = info
            item._props = props
            res.append(item)
            created_clips.append(item)
        return res

    mock_media_pool.AppendToTimeline.side_effect = mock_append

    mock_sfx = MagicMock()
    mock_sfx.GetName.return_value = "1_ตลกตบมุก_1.mp3"
    mock_bgm = MagicMock()
    mock_bgm.GetName.return_value = "NCSน่ารัก.mp3"
    mock_gif = MagicMock()
    mock_gif.GetName.return_value = "Anime - Shocked Reaction.gif"

    plan = EnrichmentPlan(
        timeline_name="Test_Timeline_Minecraft-vdo",
        timeline_start=216000,
        timeline_end=222600,
        bgm_item=PlacementItem(
            track_type="audio",
            track_index=3,
            start_frame=216000,
            end_frame=222600,
            media_pool_item=mock_bgm,
            asset_name="NCSน่ารัก.mp3",
            properties={"AudioVolume": -23.0},
            fade_in_frames=30,
            fade_out_frames=60,
        ),
        sfx_items=[
            PlacementItem(
                track_type="audio",
                track_index=2,
                start_frame=216500,
                end_frame=216600,
                media_pool_item=mock_sfx,
                asset_name="1_ตลกตบมุก_1.mp3",
                properties={"AudioVolume": -11.0},
            )
        ],
        gif_items=[
            PlacementItem(
                track_type="video",
                track_index=2,
                start_frame=216500,
                end_frame=216620,
                media_pool_item=mock_gif,
                asset_name="Anime - Shocked Reaction.gif",
                properties={"ZoomX": 0.55, "ZoomY": 0.55, "Pan": 0.0, "Tilt": 0.0},
            )
        ],
    )

    success = apply_enrichment_plan(
        mock_timeline,
        plan,
        media_pool=mock_media_pool,
        delay_between_mutations=0.0,
    )

    assert success is True

    # Check track creation: video needed track 2 (added 1 track), audio needed track 3 (added 2 tracks)
    assert mock_timeline.AddTrack.call_count == 3
    mock_timeline.AddTrack.assert_has_calls([
        call("video"),
        call("audio"),
        call("audio"),
    ], any_order=True)

    # Check clips appended: 1 BGM + 1 SFX + 1 GIF = 3 clips
    assert mock_media_pool.AppendToTimeline.call_count >= 1
    assert len(created_clips) == 3

    # Check properties applied to clips
    bgm_clip = next(c for c in created_clips if c._info.get("trackIndex") == 3 and c._info.get("mediaType") == 2)
    assert bgm_clip._props.get("AudioVolume") == -23.0

    sfx_clip = next(c for c in created_clips if c._info.get("trackIndex") == 2 and c._info.get("mediaType") == 2)
    assert sfx_clip._props.get("AudioVolume") == -11.0

    gif_clip = next(c for c in created_clips if c._info.get("trackIndex") == 2 and c._info.get("mediaType") == 1)
    assert gif_clip._props.get("ZoomX") == 0.55
    assert gif_clip._props.get("ZoomY") == 0.55
    assert gif_clip._props.get("Pan") == 0.0
    assert gif_clip._props.get("Tilt") == 0.0

    # Verify native fades applied to BGM
    bgm_clip.SetFades.assert_called_once_with({"FadeIn": 30, "FadeOut": 60})


def test_apply_enrichment_plan_mutation_delay(monkeypatch):
    mock_timeline = MagicMock()
    mock_timeline.GetTrackCount.return_value = 5
    mock_media_pool = MagicMock()
    mock_media_pool.AppendToTimeline.return_value = [MagicMock()]

    sleep_calls = []
    monkeypatch.setattr("time.sleep", lambda s: sleep_calls.append(s))

    plan = EnrichmentPlan(
        timeline_name="Delay_Test",
        timeline_start=0,
        timeline_end=100,
        bgm_item=PlacementItem(
            track_type="audio",
            track_index=3,
            start_frame=0,
            end_frame=100,
            media_pool_item=MagicMock(),
            asset_name="bgm.mp3",
        ),
    )

    ok = apply_enrichment_plan(mock_timeline, plan, media_pool=mock_media_pool, delay_between_mutations=1.2)
    assert ok is True
    # Verify that sleep was called with full 1.2s delay, not clamped to 0.35s
    assert 1.2 in sleep_calls


def test_apply_enrichment_plan_save_project_called():
    mock_resolve = MagicMock()
    mock_pm = MagicMock()
    mock_resolve.GetProjectManager.return_value = mock_pm

    mock_timeline = MagicMock()
    mock_timeline.GetTrackCount.return_value = 5
    mock_media_pool = MagicMock()
    mock_media_pool.AppendToTimeline.return_value = [MagicMock()]

    plan = EnrichmentPlan(
        timeline_name="Save_Test",
        timeline_start=0,
        timeline_end=100,
        bgm_item=PlacementItem(
            track_type="audio",
            track_index=3,
            start_frame=0,
            end_frame=100,
            media_pool_item=MagicMock(),
            asset_name="bgm.mp3",
        ),
    )

    ok = apply_enrichment_plan(mock_timeline, plan, media_pool=mock_media_pool, resolve_obj=mock_resolve)
    assert ok is True
    mock_pm.SaveProject.assert_called_once()


def test_apply_enrichment_plan_append_failure():
    mock_timeline = MagicMock()
    mock_timeline.GetTrackCount.return_value = 5
    mock_media_pool = MagicMock()
    # Simulate AppendToTimeline failing and returning empty list
    mock_media_pool.AppendToTimeline.return_value = []

    plan = EnrichmentPlan(
        timeline_name="Failure_Test",
        timeline_start=0,
        timeline_end=100,
        bgm_item=PlacementItem(
            track_type="audio",
            track_index=3,
            start_frame=0,
            end_frame=100,
            media_pool_item=MagicMock(),
            asset_name="bgm.mp3",
        ),
    )

    ok = apply_enrichment_plan(mock_timeline, plan, media_pool=mock_media_pool)
    assert ok is False


def test_empty_catalog_handling():
    from scripts.enrichment_engine import _find_catalog_item
    item, name = _find_catalog_item({}, "Enrichment_SFX", "1_ตลกตบมุก_1.mp3")
    assert item is None
    assert name is None

    empty_catalog = {
        "Enrichment_SFX": [],
        "Enrichment_BGM": [],
        "Enrichment_GIF": [],
    }
    plan = plan_timeline_enrichment(
        {"name": "Empty_Minecraft-vdo", "start": 0, "end": 1000},
        empty_catalog,
    )
    assert plan.bgm_item is None
    assert len(plan.sfx_items) == 0
    assert len(plan.gif_items) == 0

    mock_timeline = MagicMock()
    mock_timeline.GetTrackCount.return_value = 5
    mock_media_pool = MagicMock()

    # Plan with no valid items returns True without appending
    ok = apply_enrichment_plan(mock_timeline, plan, media_pool=mock_media_pool)
    assert ok is True
    mock_media_pool.AppendToTimeline.assert_not_called()



def test_analyze_subtitle_cues_with_objects():
    class MockSubItem:
        def __init__(self, name, start, end):
            self._name = name
            self._start = start
            self._end = end
        def GetName(self):
            return self._name
        def GetStart(self):
            return self._start
        def GetEnd(self):
            return self._end

    subs = [
        MockSubItem("เห้ย ไม่นะ บอสมา", 1000, 1080),
        MockSubItem("555 ตลก", 2000, 2060),
    ]
    cues = analyze_subtitle_cues(subs)
    assert len(cues) == 2
    assert cues[0].cue_type == "shock"
    assert cues[1].cue_type == "punchline"


def test_plan_timeline_enrichment_game_bgm_mapping():
    catalog = {
        "Enrichment_SFX": ["1_ตลกตบมุก_1.mp3"],
        "Enrichment_BGM": [
            "NCSน่ารัก.mp3",
            "Top 50 NoCopyrightSounds Songs 2025 🎧 Best Free EDM & Gaming Music Mix🔥 Best of NCS ✨.mp3",
            "payday.mp3",
            "YEAT - DISRESPECTFUL (PROD. SKY x KEENEX) (slowed+reverb).mp3",
        ],
        "Enrichment_GIF": ["Anime - Shocked Reaction.gif"],
    }

    # Terraria
    plan_t = plan_timeline_enrichment({"name": "บอส_Terraria-vdo", "start": 0, "end": 1000}, catalog)
    assert "Top 50" in plan_t.bgm_item.asset_name

    # Monster Hunter World
    plan_m = plan_timeline_enrichment({"name": "ล่าแย้_Monster Hunter World-vdo", "start": 0, "end": 1000}, catalog)
    assert "payday" in plan_m.bgm_item.asset_name

    # Soul Walker
    plan_s = plan_timeline_enrichment({"name": "ดันเจี้ยน_Soul Walker-vdo", "start": 0, "end": 1000}, catalog)
    assert "YEAT" in plan_s.bgm_item.asset_name


def test_apply_enrichment_plan_tracks_already_exist():
    mock_timeline = MagicMock()
    mock_timeline.GetName.return_value = "Existing_Tracks_Timeline"
    # Tracks already 2 video and 3 audio
    mock_timeline.GetTrackCount.side_effect = lambda track_type: 2 if track_type == "video" else 3

    mock_media_pool = MagicMock()
    mock_media_pool.AppendToTimeline.return_value = [MagicMock()]

    plan = EnrichmentPlan(
        timeline_name="Existing_Tracks_Timeline",
        timeline_start=100,
        timeline_end=1000,
        bgm_item=PlacementItem(
            track_type="audio",
            track_index=3,
            start_frame=100,
            end_frame=1000,
            media_pool_item=MagicMock(),
            asset_name="bgm.mp3",
            properties={"AudioVolume": -23.0},
        ),
    )

    success = apply_enrichment_plan(mock_timeline, plan, media_pool=mock_media_pool)
    assert success is True
    # AddTrack should not be called since tracks already exist
    mock_timeline.AddTrack.assert_not_called()


def test_apply_enrichment_plan_string_lookup_and_missing_error():
    mock_resolve = MagicMock()
    mock_pm = MagicMock()
    mock_project = MagicMock()
    mock_tl = MagicMock()
    mock_tl.GetName.return_value = "Target_Timeline"
    mock_tl.GetTrackCount.return_value = 5
    mock_media_pool = MagicMock()
    mock_media_pool.AppendToTimeline.return_value = [MagicMock()]

    mock_resolve.GetProjectManager.return_value = mock_pm
    mock_pm.GetCurrentProject.return_value = mock_project
    mock_project.GetTimelineCount.return_value = 1
    mock_project.GetTimelineByIndex.return_value = mock_tl
    mock_project.GetMediaPool.return_value = mock_media_pool

    plan = EnrichmentPlan(
        timeline_name="Target_Timeline",
        timeline_start=0,
        timeline_end=100,
        bgm_item=PlacementItem(
            track_type="audio",
            track_index=3,
            start_frame=0,
            end_frame=100,
            media_pool_item="bgm",
            asset_name="bgm.mp3",
        ),
    )

    # Valid name lookup
    ok = apply_enrichment_plan("Target_Timeline", plan, resolve_obj=mock_resolve)
    assert ok is True

    # Missing timeline lookup raises RuntimeError
    with pytest.raises(RuntimeError, match="not found"):
        apply_enrichment_plan("Nonexistent_Timeline", plan, resolve_obj=mock_resolve)

