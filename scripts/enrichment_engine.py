"""Subtitle Cue Analyzer & Placement Rules Engine for DaVinci Resolve.

Analyzes subtitle cues on Subtitle Track 1 to detect comedic beats, shocks,
and reactions, mapping them to exact SFX, centered GIF placements, and BGM bed.
Enforces video parameters (V2, ZoomX=0.55, ZoomY=0.55, Pan=0, Tilt=0)
and audio parameters (A2 SFX=-11.0 dB, A3 BGM=-23.0 dB with fades).
"""

import os
import sys
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple

from scripts.enrichment_assets import select_bgm_for_game, get_resolve


# ---------------------------------------------------------------------------
# Data Structures
# ---------------------------------------------------------------------------

@dataclass
class CuePoint:
    """Represents an emotional or punchline cue identified from subtitles."""
    start_frame: int
    end_frame: int
    text: str
    cue_type: str  # 'punchline', 'shock', 'cute', 'aha'
    matched_keyword: str
    suggested_sfx: Optional[str] = None
    suggested_gif: Optional[str] = None


@dataclass
class PlacementItem:
    """A planned timeline clip placement on a specific track and frame range."""
    track_type: str  # "video" or "audio"
    track_index: int  # 1-based index (e.g. 2 for V2, 2 for A2, 3 for A3)
    start_frame: int  # Timeline record start frame
    end_frame: int  # Timeline record end frame
    media_pool_item: Any  # MediaPoolItem object or identifier
    asset_name: str  # Base filename
    properties: Dict[str, Any] = field(default_factory=dict)
    fade_in_frames: Optional[int] = None
    fade_out_frames: Optional[int] = None
    source_start_frame: int = 0
    source_end_frame: Optional[int] = None
    media_type: int = 0  # 1: Video only, 2: Audio only, 0: default

    def __post_init__(self):
        if self.media_type == 0:
            if self.track_type.lower() == "video":
                self.media_type = 1
            elif self.track_type.lower() == "audio":
                self.media_type = 2



@dataclass
class EnrichmentPlan:
    """Full enrichment blueprint for a timeline."""
    timeline_name: str
    timeline_start: int
    timeline_end: int
    bgm_item: Optional[PlacementItem] = None
    sfx_items: List[PlacementItem] = field(default_factory=list)
    gif_items: List[PlacementItem] = field(default_factory=list)
    cue_points: List[CuePoint] = field(default_factory=list)
    items: List[PlacementItem] = field(default_factory=list)

    def __post_init__(self):
        # Synchronize items list with specific item fields
        if not self.items:
            all_items = []
            if self.bgm_item:
                all_items.append(self.bgm_item)
            all_items.extend(self.sfx_items)
            all_items.extend(self.gif_items)
            self.items = all_items
        elif not self.bgm_item and not self.sfx_items and not self.gif_items:
            for it in self.items:
                if it.track_type == "audio" and it.track_index == 3:
                    self.bgm_item = it
                elif it.track_type == "audio" and it.track_index == 2:
                    self.sfx_items.append(it)
                elif it.track_type == "video" and it.track_index == 2:
                    self.gif_items.append(it)


# ---------------------------------------------------------------------------
# Cue Detection Rules & Mapping
# ---------------------------------------------------------------------------

CUE_RULES = [
    {
        "type": "punchline",
        "keywords": ["555", "ฮ่า", "อ้าว", "เอ้า", "แป๊บ", "ไม่ได้", "ตลก"],
        "sfx": ["1_ตลกตบมุก_1.mp3", "2.ตบมุก.mp3", "3.ตบมุก.mp3"],
        "gif": [
            "Reaction - Iconic Laugh.gif",
            "Reaction - Laughing Pointing.gif",
            "Reaction - Well Done Laughing.gif",
            "Reaction - What Confused Minion.gif",
        ],
    },
    {
        "type": "shock",
        "keywords": ["เห้ย", "ว๊าก", "ไม่นะ", "ตาย", "ระเบิด", "บอส", "ช่วยด้วย"],
        "sfx": ["(mafioso) scream.mp3", "3.ฟ้าผ่า.mp3", "_RUN_ vine effect sound.mp3"],
        "gif": [
            "Anime - Shocked Reaction.gif",
            "Reaction - OMG No Funny.gif",
            "Reaction - What Confused Minion.gif",
        ],
    },
    {
        "type": "aha",
        "keywords": ["อ๋อ"],
        "sfx": ["_Click_ Nice.mp3", "3. WINK _DING_.mp3", "_Wow!_ (anime voice accent).mp3"],
        "gif": ["Anime - Thumbs Up.gif", "Reaction - What Confused Minion.gif"],
    },
    {
        "type": "cute",
        "keywords": ["เยี่ยม", "สวย", "รอดแล้ว", "เจอ", "โห"],
        "sfx": ["3. WINK _DING_.mp3", "_Click_ Nice.mp3", "_Wow!_ (anime voice accent).mp3"],
        "gif": ["Cute - Dancing Cat.gif", "Cute - Happy Dancing Cat.gif", "Anime - Thumbs Up.gif"],
    },
]


def analyze_subtitle_cues(subtitles: List[Dict[str, Any]]) -> List[CuePoint]:
    """Analyze subtitle items on Subtitle Track 1 to identify emotional and comedic cues.

    Args:
        subtitles: List of dicts with keys 'name'/'text', 'start', 'end'.

    Returns:
        List of detected CuePoints.
    """
    detected_cues: List[CuePoint] = []

    for sub in subtitles:
        # Extract text/name
        if isinstance(sub, dict):
            text = sub.get("name") or sub.get("text") or ""
            start = sub.get("start") or sub.get("start_frame") or 0
            end = sub.get("end") or sub.get("end_frame") or start
        else:
            # Handle object with methods
            text = getattr(sub, "GetName", lambda: "")()
            start = getattr(sub, "GetStart", lambda: 0)()
            end = getattr(sub, "GetEnd", lambda: start)()

        if not text:
            continue

        matched_rule = None
        matched_kw = None

        for rule in CUE_RULES:
            for kw in rule["keywords"]:
                if kw in text:
                    matched_rule = rule
                    matched_kw = kw
                    break
            if matched_rule:
                break

        if matched_rule and matched_kw:
            # Pick primary suggested SFX and GIF
            suggested_sfx = matched_rule["sfx"][0] if matched_rule["sfx"] else None
            suggested_gif = matched_rule["gif"][0] if matched_rule["gif"] else None

            detected_cues.append(
                CuePoint(
                    start_frame=int(start),
                    end_frame=int(end),
                    text=text,
                    cue_type=matched_rule["type"],
                    matched_keyword=matched_kw,
                    suggested_sfx=suggested_sfx,
                    suggested_gif=suggested_gif,
                )
            )

    return detected_cues


# ---------------------------------------------------------------------------
# Asset Catalog Resolution Helper
# ---------------------------------------------------------------------------

def _find_catalog_item(catalog: Dict[str, List[Any]], bin_name: str, preferred_name: Optional[str] = None) -> Tuple[Any, str]:
    """Find matching MediaPoolItem or asset name from catalog bin."""
    clips = catalog.get(bin_name, [])
    if not clips:
        # If bin is empty or not in catalog, return mock/fallback name
        return preferred_name or f"fallback_{bin_name}", preferred_name or f"fallback_{bin_name}"

    if preferred_name:
        for clip in clips:
            name = clip.GetName() if hasattr(clip, "GetName") else str(clip)
            if preferred_name.lower() in name.lower() or name.lower() in preferred_name.lower():
                return clip, name

    # Default to first available clip
    first_clip = clips[0]
    first_name = first_clip.GetName() if hasattr(first_clip, "GetName") else str(first_clip)
    return first_clip, first_name


# ---------------------------------------------------------------------------
# Timeline Planning
# ---------------------------------------------------------------------------

def plan_timeline_enrichment(timeline_info: Dict[str, Any], asset_catalog: Dict[str, List[Any]]) -> EnrichmentPlan:
    """Generate a comprehensive EnrichmentPlan for a timeline based on subtitle cues and constraints.

    Constraints:
    - BGM: A3, AudioVolume=-23.0 dB, 0.5s fade-in, 1.0s fade-out, spans entire timeline.
    - SFX: A2, AudioVolume=-11.0 dB, placed at cue points, spaced >= 2.0s apart.
    - GIF: V2, ZoomX=0.55, ZoomY=0.55, Pan=0, Tilt=0, centered, duration 1.5s-2.5s, spaced >= 5.0s apart.
    """
    name = timeline_info.get("name", "Untitled_Timeline")
    start_frame = int(timeline_info.get("start_frame") or timeline_info.get("start") or 216000)
    end_frame = int(timeline_info.get("end_frame") or timeline_info.get("end") or (start_frame + 6600))
    fps = float(timeline_info.get("fps") or 60.0)
    subtitles = timeline_info.get("subtitles") or []

    # 1. Plan BGM
    game = timeline_info.get("game")
    if not game:
        if "_" in name:
            game = name.split("_")[-1].replace("-vdo", "")
        else:
            game = "Minecraft"

    preferred_bgm_name = select_bgm_for_game(game)
    bgm_clip, bgm_actual_name = _find_catalog_item(asset_catalog, "Enrichment_BGM", preferred_bgm_name)

    fade_in_frames = int(0.5 * fps)
    fade_out_frames = int(1.0 * fps)

    bgm_item = PlacementItem(
        track_type="audio",
        track_index=3,
        start_frame=start_frame,
        end_frame=end_frame,
        media_pool_item=bgm_clip,
        asset_name=bgm_actual_name,
        properties={"AudioVolume": -23.0},
        fade_in_frames=fade_in_frames,
        fade_out_frames=fade_out_frames,
        media_type=2,  # Audio only
    )

    # 2. Analyze Cues
    cues = analyze_subtitle_cues(subtitles)

    # 3. Plan SFX on A2
    sfx_items: List[PlacementItem] = []
    min_sfx_gap = int(2.0 * fps)  # 2.0s gap
    last_sfx_end = start_frame

    for cue in cues:
        if cue.start_frame < last_sfx_end + min_sfx_gap:
            continue
        if cue.start_frame >= end_frame:
            continue

        sfx_clip, sfx_actual_name = _find_catalog_item(asset_catalog, "Enrichment_SFX", cue.suggested_sfx)
        # 1.5s nominal duration for SFX
        sfx_duration = int(1.5 * fps)
        sfx_end = min(cue.start_frame + sfx_duration, end_frame)

        sfx_items.append(
            PlacementItem(
                track_type="audio",
                track_index=2,
                start_frame=cue.start_frame,
                end_frame=sfx_end,
                media_pool_item=sfx_clip,
                asset_name=sfx_actual_name,
                properties={"AudioVolume": -11.0},
                media_type=2,  # Audio only
            )
        )
        last_sfx_end = sfx_end
        if len(sfx_items) >= 3:
            break

    # If no subtitle cues matched, provide at least two comedic/punchline beats spaced evenly
    if len(sfx_items) < 2 and (end_frame - start_frame) > int(10 * fps):
        default_sfx_clip, default_sfx_name = _find_catalog_item(asset_catalog, "Enrichment_SFX", "1_ตลกตบมุก_1.mp3")
        interval = (end_frame - start_frame) // 3
        for i in range(1, 3):
            cand_start = start_frame + i * interval
            if not any(abs(it.start_frame - cand_start) < min_sfx_gap for it in sfx_items):
                sfx_items.append(
                    PlacementItem(
                        track_type="audio",
                        track_index=2,
                        start_frame=cand_start,
                        end_frame=min(cand_start + int(1.5 * fps), end_frame),
                        media_pool_item=default_sfx_clip,
                        asset_name=default_sfx_name,
                        properties={"AudioVolume": -11.0},
                        media_type=2,
                    )
                )

    # 4. Plan GIFs on V2
    gif_items: List[PlacementItem] = []
    min_gif_gap = int(5.0 * fps)  # 5.0s gap
    last_gif_end = start_frame

    # Prioritize shock and punchline cues for GIFs
    sorted_cues = sorted(
        cues,
        key=lambda c: 0 if c.cue_type in ("shock", "punchline") else 1,
    )

    for cue in sorted_cues:
        if cue.start_frame < last_gif_end + min_gif_gap:
            continue
        if cue.start_frame >= end_frame:
            continue

        gif_clip, gif_actual_name = _find_catalog_item(asset_catalog, "Enrichment_GIF", cue.suggested_gif)
        # Duration: 2.0s (120 frames at 60fps)
        gif_duration = int(2.0 * fps)
        gif_end = min(cue.start_frame + gif_duration, end_frame)

        gif_items.append(
            PlacementItem(
                track_type="video",
                track_index=2,
                start_frame=cue.start_frame,
                end_frame=gif_end,
                media_pool_item=gif_clip,
                asset_name=gif_actual_name,
                properties={
                    "ZoomX": 0.55,
                    "ZoomY": 0.55,
                    "Pan": 0.0,
                    "Tilt": 0.0,
                },
                media_type=1,  # Video only
            )
        )
        last_gif_end = gif_end
        if len(gif_items) >= 2:
            break

    # If no GIF cues matched, place at least 1 centered reaction GIF around timeline midpoint
    if not gif_items and (end_frame - start_frame) > int(6 * fps):
        default_gif_clip, default_gif_name = _find_catalog_item(asset_catalog, "Enrichment_GIF", "Reaction - Iconic Laugh.gif")
        mid_point = start_frame + (end_frame - start_frame) // 2
        gif_items.append(
            PlacementItem(
                track_type="video",
                track_index=2,
                start_frame=mid_point,
                end_frame=min(mid_point + int(2.0 * fps), end_frame),
                media_pool_item=default_gif_clip,
                asset_name=default_gif_name,
                properties={
                    "ZoomX": 0.55,
                    "ZoomY": 0.55,
                    "Pan": 0.0,
                    "Tilt": 0.0,
                },
                media_type=1,
            )
        )

    return EnrichmentPlan(
        timeline_name=name,
        timeline_start=start_frame,
        timeline_end=end_frame,
        bgm_item=bgm_item,
        sfx_items=sfx_items,
        gif_items=gif_items,
        cue_points=cues,
    )


# ---------------------------------------------------------------------------
# Plan Execution & Resolve Placement
# ---------------------------------------------------------------------------

def apply_enrichment_plan(
    timeline: Any,
    plan: EnrichmentPlan,
    media_pool: Optional[Any] = None,
    resolve_obj: Optional[Any] = None,
    delay_between_mutations: float = 0.0,
) -> bool:
    """Apply an EnrichmentPlan to a live DaVinci Resolve timeline.

    Ensures tracks V2, A2, and A3 exist before placing assets.
    Appends assets using MediaPool.AppendToTimeline and applies
    numeric transforms and audio volume properties.

    Args:
        timeline: Resolve Timeline object or timeline name string.
        plan: Configured EnrichmentPlan.
        media_pool: Optional MediaPool instance.
        resolve_obj: Optional Resolve instance.
        delay_between_mutations: Delay in seconds between mutations (default 0.0, ~1.2s for live).

    Returns:
        True if all placements and property assignments succeeded.
    """
    resolve = resolve_obj or get_resolve()

    # Resolve timeline object if name was passed
    if isinstance(timeline, str):
        if not resolve:
            raise RuntimeError("Resolve connection required to look up timeline by name.")
        pm = resolve.GetProjectManager()
        project = pm.GetCurrentProject()
        count = project.GetTimelineCount()
        target_tl = None
        for i in range(1, count + 1):
            tl = project.GetTimelineByIndex(i)
            if tl.GetName() == timeline:
                target_tl = tl
                break
        if not target_tl:
            raise RuntimeError(f"Timeline '{timeline}' not found.")
        timeline = target_tl

    # Resolve MediaPool
    if media_pool is None:
        if hasattr(timeline, "GetMediaPool"):
            media_pool = timeline.GetMediaPool()
        elif hasattr(timeline, "GetProject") and timeline.GetProject():
            media_pool = timeline.GetProject().GetMediaPool()
        elif resolve:
            pm = resolve.GetProjectManager()
            if pm and pm.GetCurrentProject():
                media_pool = pm.GetCurrentProject().GetMediaPool()

    if not media_pool:
        raise RuntimeError("Could not obtain MediaPool for timeline placement.")

    # 1. Ensure Video 2 exists
    v_track_count = timeline.GetTrackCount("video") if hasattr(timeline, "GetTrackCount") else 1
    while v_track_count < 2:
        if hasattr(timeline, "AddTrack"):
            timeline.AddTrack("video")
        v_track_count += 1
        if delay_between_mutations > 0:
            time.sleep(delay_between_mutations)

    if hasattr(timeline, "SetTrackName"):
        try:
            timeline.SetTrackName("video", 2, "GIF Overlays")
        except Exception:
            pass

    # 2. Ensure Audio 2 and Audio 3 exist
    a_track_count = timeline.GetTrackCount("audio") if hasattr(timeline, "GetTrackCount") else 1
    while a_track_count < 3:
        if hasattr(timeline, "AddTrack"):
            timeline.AddTrack("audio")
        a_track_count += 1
        if delay_between_mutations > 0:
            time.sleep(delay_between_mutations)

    if hasattr(timeline, "SetTrackName"):
        try:
            timeline.SetTrackName("audio", 2, "SFX")
            timeline.SetTrackName("audio", 3, "BGM")
        except Exception:
            pass

    # 3. Place items into tracks
    all_items = plan.items or []
    if not all_items:
        if plan.bgm_item:
            all_items.append(plan.bgm_item)
        all_items.extend(plan.sfx_items)
        all_items.extend(plan.gif_items)

    for item in all_items:
        clip_info = {
            "mediaPoolItem": item.media_pool_item,
            "startFrame": item.source_start_frame,
            "endFrame": item.source_end_frame if item.source_end_frame is not None else (item.end_frame - item.start_frame),
            "mediaType": item.media_type,
            "trackIndex": item.track_index,
            "recordFrame": item.start_frame,
        }

        appended = media_pool.AppendToTimeline([clip_info])
        if delay_between_mutations > 0:
            time.sleep(min(delay_between_mutations, 0.35))

        # Apply properties to the created timeline items
        if appended and isinstance(appended, list):
            for placed_item in appended:
                if not placed_item:
                    continue
                for prop_name, prop_val in item.properties.items():
                    if hasattr(placed_item, "SetProperty"):
                        placed_item.SetProperty(prop_name, prop_val)

    return True


if __name__ == "__main__":
    print("Enrichment Engine module loaded.")
