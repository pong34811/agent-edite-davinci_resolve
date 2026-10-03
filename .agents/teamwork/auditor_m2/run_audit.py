import os
import sys
import json

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

os.environ['RESOLVE_SCRIPT_LIB'] = r'C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll'
sys.path.append(r'C:\Program Files\Blackmagic Design\DaVinci Resolve\ResolvePython\lib\modules')
import DaVinciResolveScript as dvr_script

resolve = dvr_script.scriptapp('Resolve')
if not resolve:
    print("FATAL: Could not connect to Resolve")
    sys.exit(1)

pm = resolve.GetProjectManager()
proj = pm.GetCurrentProject()
print(f"[AUDIT] Project: {proj.GetName()} ({proj.GetUniqueId()})")

baseline_path = r'C:\Users\warit\Desktop\agent-edite-davinci_resolve\.agents\teamwork\worker_m1\baseline_30_timelines.json'
with open(baseline_path, 'r', encoding='utf-8') as f:
    baseline_data = json.load(f)

baseline_timelines = {t['timeline_name']: t for t in baseline_data['timelines']}
print(f"[AUDIT] Loaded {len(baseline_timelines)} timelines from baseline JSON")

tl_count = proj.GetTimelineCount()
project_timelines = {}
for i in range(1, tl_count + 1):
    tl = proj.GetTimelineByIndex(i)
    project_timelines[tl.GetName()] = tl

print(f"[AUDIT] Total timelines in project: {tl_count}")

# 1. Verify Original Pilot Timeline
orig_name = "หนีฝ่าความหนาว_Minecraft-vdo"
if orig_name not in project_timelines:
    print(f"[FAIL] Original timeline '{orig_name}' missing!")
else:
    orig_tl = project_timelines[orig_name]
    orig_base = baseline_timelines.get(orig_name, {})
    w = orig_tl.GetSetting("timelineResolutionWidth")
    h = orig_tl.GetSetting("timelineResolutionHeight")
    fps = float(orig_tl.GetSetting("timelineFrameRate") or 0.0)
    dur = orig_tl.GetEndFrame() - orig_tl.GetStartFrame()
    v_cnt = orig_tl.GetTrackCount("video")
    a_cnt = orig_tl.GetTrackCount("audio")
    s_cues = len(orig_tl.GetItemListInTrack("subtitle", 1) or [])
    
    print(f"\n[ORIGINAL PILOT] {orig_name}:")
    print(f"  Resolution: {w}x{h} (baseline: {orig_base.get('resolution_width')}x{orig_base.get('resolution_height')})")
    print(f"  FPS: {fps} (baseline: {orig_base.get('frame_rate')})")
    print(f"  Duration: {dur} (baseline: {orig_base.get('duration_frames')})")
    print(f"  Video Tracks: {v_cnt} (baseline: {orig_base.get('track_counts', {}).get('video')})")
    print(f"  Audio Tracks: {a_cnt} (baseline: {orig_base.get('track_counts', {}).get('audio')})")
    print(f"  Subtitle Cues: {s_cues} (baseline: {len(orig_base.get('subtitle_track', {}).get('cues', []))})")

# 2. Verify Target 9:16 Timeline
target_name = "หนีฝ่าความหนาว_Minecraft-vdo_9x16"
if target_name not in project_timelines:
    print(f"[FAIL] Target timeline '{target_name}' missing!")
else:
    target_tl = project_timelines[target_name]
    orig_base = baseline_timelines.get(orig_name, {})
    tw = target_tl.GetSetting("timelineResolutionWidth")
    th = target_tl.GetSetting("timelineResolutionHeight")
    tcustom = target_tl.GetSetting("useCustomSettings")
    tfps = float(target_tl.GetSetting("timelineFrameRate") or 0.0)
    tdur = target_tl.GetEndFrame() - target_tl.GetStartFrame()
    tv_cnt = target_tl.GetTrackCount("video")
    ta_cnt = target_tl.GetTrackCount("audio")
    ts_items = target_tl.GetItemListInTrack("subtitle", 1) or []
    
    print(f"\n[TARGET PILOT 9x16] {target_name}:")
    print(f"  Resolution: {tw}x{th} (useCustomSettings={tcustom})")
    print(f"  FPS: {tfps}")
    print(f"  Duration: {tdur} (Start: {target_tl.GetStartFrame()}, End: {target_tl.GetEndFrame()})")
    print(f"  Video Tracks: {tv_cnt}")
    print(f"  Audio Tracks: {ta_cnt}")
    print(f"  Subtitle Cues: {len(ts_items)}")

    # Subtitle verification
    base_cues = orig_base.get("subtitle_track", {}).get("cues", [])
    sub_mismatches = 0
    for idx, (sub, bc) in enumerate(zip(ts_items, base_cues)):
        if sub.GetName() != bc['text'] or sub.GetStart() != bc['start_frame'] or sub.GetEnd() != bc['end_frame']:
            sub_mismatches += 1
            if sub_mismatches <= 3:
                print(f"    Subtitle mismatch at #{idx}: '{sub.GetName()}' [{sub.GetStart()}..{sub.GetEnd()}] vs '{bc['text']}' [{bc['start_frame']}..{bc['end_frame']}]")
    print(f"  Subtitle 1:1 match: {'PASS (0 mismatches)' if sub_mismatches == 0 else f'FAIL ({sub_mismatches} mismatches)'}")

    # Video track items
    v1_items = target_tl.GetItemListInTrack("video", 1) or []
    v2_items = target_tl.GetItemListInTrack("video", 2) or []
    v3_items = target_tl.GetItemListInTrack("video", 3) or []
    v4_items = target_tl.GetItemListInTrack("video", 4) or []
    
    print(f"  V1 item count: {len(v1_items)}, V2 item count: {len(v2_items)}, V3 item count: {len(v3_items)}, V4 item count: {len(v4_items)}")
    
    if v1_items:
        v1 = v1_items[0]
        print(f"  V1 Game: name='{v1.GetName()}', ZoomX={v1.GetProperty('ZoomX')}, Pan={v1.GetProperty('Pan')}, Tilt={v1.GetProperty('Tilt')}, CropBottom={v1.GetProperty('CropBottom')}")
    if v2_items:
        v2 = v2_items[0]
        print(f"  V2 VTuber: name='{v2.GetName()}', ZoomX={v2.GetProperty('ZoomX')}, Pan={v2.GetProperty('Pan')}, Tilt={v2.GetProperty('Tilt')}, CropTop={v2.GetProperty('CropTop')}")
    if v4_items:
        v4 = v4_items[0]
        print(f"  V4 Reaction GIF: name='{v4.GetName()}', ZoomX={v4.GetProperty('ZoomX')}, Pan={v4.GetProperty('Pan')}, Tilt={v4.GetProperty('Tilt')}")

    print(f"  V3 Adjustment Clips ({len(v3_items)}):")
    for idx, adj in enumerate(v3_items):
        comp = adj.GetFusionCompByIndex(1)
        if comp:
            tools = comp.GetToolList()
            t_names = [t.GetAttrs().get('TOOLS_Name') for t in tools.values()]
            t_details = []
            for t in tools.values():
                name = t.GetAttrs().get('TOOLS_Name')
                if 'Transform' in name:
                    center = t.GetInput('Center')
                    size = t.GetInput('Size')
                    t_details.append(f"{name}: Center={center}, Size={size}")
            print(f"    Adj {idx+1} [{adj.GetStart()}..{adj.GetEnd()}]: tools={t_names} -> {t_details}")
        else:
            print(f"    Adj {idx+1}: NO FUSION COMP FOUND")

    # Offline items check
    offline_items = []
    for v in range(1, tv_cnt + 1):
        for it in target_tl.GetItemListInTrack("video", v) or []:
            mpi = it.GetMediaPoolItem()
            if mpi:
                path = mpi.GetClipProperty("File Path")
                if path and not os.path.exists(path):
                    offline_items.append((f"V{v}", it.GetName(), path))
    for a in range(1, ta_cnt + 1):
        for it in target_tl.GetItemListInTrack("audio", a) or []:
            mpi = it.GetMediaPoolItem()
            if mpi:
                path = mpi.GetClipProperty("File Path")
                if path and not os.path.exists(path):
                    offline_items.append((f"A{a}", it.GetName(), path))
    print(f"  Offline media items: {len(offline_items)} ({offline_items})")

# 3. Check All Other 29 Baseline Timelines
print(f"\n[AUDIT] Checking preservation of all 30 baseline timelines...")
all_30_pass = True
for name, base in baseline_timelines.items():
    if name not in project_timelines:
        print(f"  [FAIL] Baseline timeline '{name}' missing from project!")
        all_30_pass = False
        continue
    tl = project_timelines[name]
    bw = str(base['resolution_width'])
    bh = str(base['resolution_height'])
    w = str(tl.GetSetting("timelineResolutionWidth"))
    h = str(tl.GetSetting("timelineResolutionHeight"))
    dur = tl.GetEndFrame() - tl.GetStartFrame()
    bdur = base['duration_frames']
    vcnt = tl.GetTrackCount("video")
    bvcnt = base.get("track_counts", {}).get("video", len(base.get("video_tracks", [])))
    acnt = tl.GetTrackCount("audio")
    bacnt = base.get("track_counts", {}).get("audio", len(base.get("audio_tracks", [])))
    scnt = len(tl.GetItemListInTrack("subtitle", 1) or [])
    bscnt = len(base.get("subtitle_track", {}).get("cues", []))
    
    if w != bw or h != bh or dur != bdur or vcnt != bvcnt or acnt != bacnt or scnt != bscnt:
        print(f"  [ALTERED] {name}: w={w} (base {bw}), h={h} (base {bh}), dur={dur} (base {bdur}), v={vcnt} (base {bvcnt}), a={acnt} (base {bacnt}), s={scnt} (base {bscnt})")
        all_30_pass = False

if all_30_pass:
    print(f"  [PASS] All 30 original baseline timelines are completely UNTOUCHED!")
