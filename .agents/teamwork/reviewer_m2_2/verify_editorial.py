import sys, os, json
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

os.environ['RESOLVE_SCRIPT_LIB'] = r'C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll'
sys.path.append(r'C:\Program Files\Blackmagic Design\DaVinci Resolve\ResolvePython\lib\modules')
import DaVinciResolveScript as dvr

r = dvr.scriptapp('Resolve')
p = r.GetProjectManager().GetCurrentProject()

baseline_path = r"C:\Users\warit\Desktop\agent-edite-davinci_resolve\.agents\teamwork\worker_m1\baseline_30_timelines.json"
with open(baseline_path, 'r', encoding='utf-8') as f:
    base_data = json.load(f)

pilot_base = None
for tl in base_data.get('timelines', []):
    if tl.get('timeline_name') == 'หนีฝ่าความหนาว_Minecraft-vdo':
        pilot_base = tl
        break

print("=== VERIFYING STRICT LOCKED EDITORIAL PRESERVATION ===")
# Find target timeline
target_tl = None
orig_tl = None
for i in range(1, p.GetTimelineCount()+1):
    tl = p.GetTimelineByIndex(i)
    if tl.GetName() == 'หนีฝ่าความหนาว_Minecraft-vdo_9x16':
        target_tl = tl
    elif tl.GetName() == 'หนีฝ่าความหนาว_Minecraft-vdo':
        orig_tl = tl

print("Target timeline found:", target_tl is not None)
print("Original timeline found:", orig_tl is not None)

# Check Subtitles on target
sub_items = target_tl.GetItemListInTrack("subtitle", 1) or []
base_cues = pilot_base['subtitle_track']['cues']
print(f"Subtitle cues count: target={len(sub_items)}, baseline={len(base_cues)}")

cue_mismatches = []
for idx, (it, bc) in enumerate(zip(sub_items, base_cues)):
    t_text = it.GetName()
    t_start = it.GetStart()
    t_end = it.GetEnd()
    b_text = bc['text']
    b_start = bc['start_frame']
    b_end = bc['end_frame']
    if t_text != b_text or t_start != b_start or t_end != b_end:
        cue_mismatches.append((idx+1, t_text, b_text, t_start, b_start, t_end, b_end))

print(f"Subtitle cue mismatches: {len(cue_mismatches)}")

# Check Audio on target
a_tracks = target_tl.GetTrackCount("audio")
base_audio = pilot_base['audio_tracks']
print(f"Audio tracks count: target={a_tracks}, baseline={len(base_audio)}")

audio_mismatches = []
for a_idx in range(1, a_tracks+1):
    items = target_tl.GetItemListInTrack("audio", a_idx) or []
    b_items = base_audio[a_idx-1]['items']
    if len(items) != len(b_items):
        audio_mismatches.append(f"Track A{a_idx} item count mismatch: {len(items)} vs {len(b_items)}")
    for it, bit in zip(items, b_items):
        vol = it.GetProperty("AudioVolume")
        b_vol = bit.get("volume_db", 0.0)
        start = it.GetStart()
        b_start = bit.get("start_frame")
        end = it.GetEnd()
        b_end = bit.get("end_frame")
        if start != b_start or end != b_end:
            audio_mismatches.append(f"Track A{a_idx} item timing mismatch: {start}..{end} vs {b_start}..{b_end}")

print(f"Audio mismatches: {len(audio_mismatches)}")

# Check duration
dur = target_tl.GetEndFrame() - target_tl.GetStartFrame()
base_dur = pilot_base['duration_frames']
print(f"Duration: target={dur}, baseline={base_dur} -> diff = {dur - base_dur}")

# Check original timeline
orig_dur = orig_tl.GetEndFrame() - orig_tl.GetStartFrame()
orig_subs = len(orig_tl.GetItemListInTrack("subtitle", 1) or [])
orig_v = orig_tl.GetTrackCount("video")
orig_a = orig_tl.GetTrackCount("audio")
print(f"Original timeline: dur={orig_dur}, subs={orig_subs}, V tracks={orig_v}, A tracks={orig_a}")
