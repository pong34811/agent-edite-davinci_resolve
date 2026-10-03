import sys
import os
import json

sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(r'C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules')
import DaVinciResolveScript as dvr

def inspect():
    resolve = dvr.scriptapp('Resolve')
    if not resolve:
        print("ERROR: Cannot connect to DaVinci Resolve")
        sys.exit(1)

    version = resolve.GetVersion()
    product_name = resolve.GetProductName()
    
    pm = resolve.GetProjectManager()
    proj = pm.GetCurrentProject()
    if not proj:
        print("ERROR: No active project")
        sys.exit(1)

    proj_name = proj.GetName()
    proj_id = proj.GetUniqueId()
    timeline_count = proj.GetTimelineCount()
    timeline_fps = proj.GetSetting('timelineFrameRate')
    playback_fps = proj.GetSetting('timelinePlaybackFrameRate')
    res_w = proj.GetSetting('timelineResolutionWidth')
    res_h = proj.GetSetting('timelineResolutionHeight')

    report = {
        "resolve": {
            "product_name": product_name,
            "version": version
        },
        "project": {
            "name": proj_name,
            "id": proj_id,
            "timeline_count": timeline_count,
            "timeline_frame_rate": timeline_fps,
            "playback_frame_rate": playback_fps,
            "resolution_width": res_w,
            "resolution_height": res_h
        },
        "timelines": [],
        "media_pool_clips": []
    }

    # Inspect all timelines
    for i in range(1, timeline_count + 1):
        tl = proj.GetTimelineByIndex(i)
        tl_name = tl.GetName()
        tl_id = tl.GetUniqueId()
        start_frame = tl.GetStartFrame()
        end_frame = tl.GetEndFrame()
        dur_frames = end_frame - start_frame
        dur_sec = dur_frames / float(timeline_fps) if timeline_fps else None

        v_tracks = tl.GetTrackCount("video")
        a_tracks = tl.GetTrackCount("audio")
        sub_tracks = tl.GetTrackCount("subtitle")

        v_items = tl.GetItemListInTrack("video", 1) or []
        a_items = tl.GetItemListInTrack("audio", 1) or []

        v_info = []
        for v in v_items:
            mpi = v.GetMediaPoolItem()
            v_info.append({
                "item_name": v.GetName(),
                "start": v.GetStart(),
                "end": v.GetEnd(),
                "duration": v.GetDuration(),
                "source_start": v.GetSourceStartFrame(),
                "source_end": v.GetSourceEndFrame(),
                "media_pool_item_id": mpi.GetUniqueId() if mpi else None,
                "media_pool_item_name": mpi.GetName() if mpi else None
            })

        a_info = []
        for a in a_items:
            mpi = a.GetMediaPoolItem()
            a_info.append({
                "item_name": a.GetName(),
                "start": a.GetStart(),
                "end": a.GetEnd(),
                "duration": a.GetDuration(),
                "source_start": a.GetSourceStartFrame(),
                "source_end": a.GetSourceEndFrame(),
                "media_pool_item_id": mpi.GetUniqueId() if mpi else None
            })

        report["timelines"].append({
            "index": i,
            "name": tl_name,
            "id": tl_id,
            "start_frame": start_frame,
            "end_frame": end_frame,
            "duration_frames": dur_frames,
            "duration_seconds": dur_sec,
            "video_tracks": v_tracks,
            "audio_tracks": a_tracks,
            "subtitle_tracks": sub_tracks,
            "video_items_track_1": v_info,
            "audio_items_track_1": a_info
        })

    # Inspect Media Pool Master Folder
    mp = proj.GetMediaPool()
    root = mp.GetRootFolder()
    clips = root.GetClipList() or []
    for c in clips:
        c_name = c.GetName()
        c_id = c.GetUniqueId()
        props = c.GetClipProperty()
        report["media_pool_clips"].append({
            "name": c_name,
            "id": c_id,
            "file_path": props.get("File Path"),
            "fps": props.get("FPS"),
            "duration": props.get("Duration"),
            "resolution": props.get("Resolution"),
            "video_codec": props.get("Video Codec"),
            "audio_channels": props.get("Audio Channels"),
            "start_tc": props.get("Start TC")
        })

    out_file = r'C:\Users\warit\Desktop\agent-edite-davinci_resolve\.agents\teamwork\explorer_survey_r3_2\resolve_survey_data.json'
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"Inspection complete. Found {len(report['timelines'])} timelines and {len(report['media_pool_clips'])} media pool items.")

if __name__ == '__main__':
    inspect()
