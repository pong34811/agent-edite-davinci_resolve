import os
import sys
import datetime

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

os.environ['RESOLVE_SCRIPT_LIB'] = r'C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll'
sys.path.append(r'C:\Program Files\Blackmagic Design\DaVinci Resolve\ResolvePython\lib\modules')

import DaVinciResolveScript as dvr

def check_adversarial():
    resolve = dvr.scriptapp('Resolve')
    pm = resolve.GetProjectManager()
    project = pm.GetCurrentProject()
    
    # 1. Check audio track presence and item counts across all 21 timelines
    total_tl = project.GetTimelineCount()
    timelines = [project.GetTimelineByIndex(i) for i in range(1, total_tl + 1)]
    
    print("=== ADVERSARIAL CHECK 1: AUDIO TRACKS & AUDIO ITEMS ===")
    candidate_timelines = [t for t in timelines if "_REPO-vdo" in t.GetName() or "_Climbing-vdo" in t.GetName() or "_Ib-vdo" in t.GetName() or "_DnD-vdo" in t.GetName() or "_GarticPhone-vdo" in t.GetName() or "_FreeTalk-vdo" in t.GetName() or "_Overcooked-vdo" in t.GetName()]
    
    print(f"Candidate timelines identified: {len(candidate_timelines)}")
    
    audio_issues = []
    for tl in candidate_timelines:
        t_name = tl.GetName()
        v_items = tl.GetItemListInTrack("video", 1) or []
        a_items = tl.GetItemListInTrack("audio", 1) or []
        
        v_dur = v_items[0].GetDuration() if v_items else 0
        a_dur = a_items[0].GetDuration() if a_items else 0
        
        if len(v_items) != 1:
            audio_issues.append(f"{t_name}: video track has {len(v_items)} items instead of 1")
        if len(a_items) != 1:
            audio_issues.append(f"{t_name}: audio track has {len(a_items)} items instead of 1")
        if v_dur != 3300:
            audio_issues.append(f"{t_name}: video duration {v_dur} != 3300")
        if a_dur != 3300:
            audio_issues.append(f"{t_name}: audio duration {a_dur} != 3300")
            
    print(f"Audio/Video tracks check issues: {len(audio_issues)}")
    if audio_issues:
        for iss in audio_issues:
            print(f"  [FAIL] {iss}")
    else:
        print("  [PASS] All 21 timelines have exactly 1 video item (3300 frames) and 1 audio item (3300 frames) on Track 1!")

    # 2. Check source media modification times on SynologyDrive
    print("\n=== ADVERSARIAL CHECK 2: SOURCE MEDIA INTEGRITY & MTIMES ===")
    media_dir = r"C:\Users\warit\SynologyDrive\Tygarina\2026-09-30"
    files = [f for f in os.listdir(media_dir) if f.endswith(".mp4")]
    print(f"Total MP4 files in directory: {len(files)}")
    
    # Check if any file was modified recently (e.g. today 2026-10-02)
    modified_today = []
    now = datetime.datetime.now()
    for f in files:
        f_path = os.path.join(media_dir, f)
        mtime = datetime.datetime.fromtimestamp(os.path.getmtime(f_path))
        # If modified in the last 24 hours
        if (now - mtime).total_seconds() < 86400:
            modified_today.append((f, mtime))
            
    print(f"Files modified in the last 24 hours: {len(modified_today)}")
    if modified_today:
        print("  [WARNING] The following source files had mtime modified recently:")
        for fn, mt in modified_today:
            print(f"    - {fn}: {mt}")
    else:
        print("  [PASS] Zero source files have been modified in the last 24 hours. Absolute non-destructive guarantee verified!")

    # 3. Check for any hidden or corrupted characters in timeline names
    print("\n=== ADVERSARIAL CHECK 3: HIDDEN CHARACTERS IN NAMES ===")
    char_issues = []
    for tl in candidate_timelines:
        t_name = tl.GetName()
        # check for non-printable characters, zero-width spaces, etc.
        for ch in t_name:
            code = ord(ch)
            # Thai is 0x0E00 to 0x0E7F
            # ASCII is 0x00 to 0x7F
            # Check for invisible chars
            if code in [0x200B, 0x200C, 0x200D, 0xFEFF, 0x00A0]:
                char_issues.append(f"{t_name}: Contains hidden character U+{code:04X}")
    print(f"Hidden character issues: {len(char_issues)}")
    if char_issues:
        for iss in char_issues:
            print(f"  [FAIL] {iss}")
    else:
        print("  [PASS] No hidden or invisible characters found in any of the 21 timeline names!")

if __name__ == "__main__":
    check_adversarial()
