import sys
sys.stdout.reconfigure(encoding='utf-8')
from scripts.enrichment_assets import get_resolve

r = get_resolve()
pm = r.GetProjectManager()
proj = pm.GetCurrentProject()

t20 = proj.GetTimelineByIndex(20)
print(f"Timeline 20 Name: {t20.GetName()}")

sub_track_count = t20.GetTrackCount("subtitle")
print(f"Subtitle track count: {sub_track_count}")

# Check subtitle cues
items = t20.GetItemListInTrack("subtitle", 1)
print(f"Total subtitle items: {len(items)}")

if len(items) >= 31:
    cue31 = items[30] # 0-indexed 30 is cue 31
    print(f"Cue 31 name: {cue31.GetName()!r}")
    print(f"Cue 31 start: {cue31.GetStart()}, end: {cue31.GetEnd()}, duration: {cue31.GetDuration()}")
    # Let's inspect all items around cue 31
    for i in range(28, min(33, len(items))):
        print(f"Cue {i+1}: {items[i].GetName()!r}")
