---
name: davinci-resolve-api
description: >
  Comprehensive guide for scripting DaVinci Resolve Studio via its Python API.
  Covers environment setup, connection, project management, media pool operations,
  timeline building, clip placement, color management, rendering, and export.
  Requires DaVinci Resolve Studio (free version does not include scripting API).
trigger: >
  TRIGGER when: user asks about DaVinci Resolve scripting, automation, API,
  Python integration, timeline building, rendering via script, or programmatic
  Resolve control. Also trigger when code imports DaVinciResolveScript or
  references resolve_api, fusionscript, or Resolve scripting environment variables.
---

# DaVinci Resolve Studio — Python Scripting API Reference

> **Requirement:** DaVinci Resolve **Studio** (paid). The free version does not expose the scripting API. Resolve must be running (or launched in headless `-nogui` mode) for scripts to connect.

---

## 1. Environment Setup

### 1.1 Environment Variables (required)

Scripts running **outside** Resolve's built-in console need three environment variables so Python can find the scripting bridge.

#### macOS

```bash
export RESOLVE_SCRIPT_API="/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting/"
export RESOLVE_SCRIPT_LIB="/Applications/DaVinci Resolve/DaVinci Resolve.app/Contents/Libraries/Fusion/fusionscript.so"
export PYTHONPATH="$PYTHONPATH:$RESOLVE_SCRIPT_API/Modules/"
```

#### Windows

```cmd
set RESOLVE_SCRIPT_API=%PROGRAMDATA%\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\
set RESOLVE_SCRIPT_LIB=C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll
set PYTHONPATH=%PYTHONPATH%;%RESOLVE_SCRIPT_API%\Modules\
```

#### Linux

```bash
export RESOLVE_SCRIPT_API="/opt/resolve/Developer/Scripting/"
export RESOLVE_SCRIPT_LIB="/opt/resolve/libs/Fusion/fusionscript.so"
export PYTHONPATH="$PYTHONPATH:$RESOLVE_SCRIPT_API/Modules/"
```

> For standard ISO Linux installations, paths may use `/home/resolve` instead of `/opt/resolve`.

### 1.2 Programmatic Environment Setup

```python
import os, sys

def setup_resolve_env():
    """Set env vars programmatically (call before importing DaVinciResolveScript)."""
    if sys.platform == "darwin":
        api = "/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting/"
        lib = "/Applications/DaVinci Resolve/DaVinci Resolve.app/Contents/Libraries/Fusion/fusionscript.so"
    elif sys.platform == "win32":
        api = os.path.join(os.environ.get("PROGRAMDATA", ""),
                           "Blackmagic Design", "DaVinci Resolve",
                           "Support", "Developer", "Scripting")
        lib = os.path.join(os.environ.get("PROGRAMFILES", ""),
                           "Blackmagic Design", "DaVinci Resolve", "fusionscript.dll")
    else:  # Linux
        api = "/opt/resolve/Developer/Scripting/"
        lib = "/opt/resolve/libs/Fusion/fusionscript.so"

    os.environ.setdefault("RESOLVE_SCRIPT_API", api)
    os.environ.setdefault("RESOLVE_SCRIPT_LIB", lib)
    modules = os.path.join(os.environ["RESOLVE_SCRIPT_API"], "Modules")
    if modules not in sys.path:
        sys.path.insert(0, modules)
```

### 1.3 Script Locations (menu-invoked scripts)

Place scripts in these directories to have them appear in Resolve's **Workspace > Scripts** menu:

| Platform | All Users | Per User |
|----------|-----------|----------|
| macOS | `/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Scripts` | `~/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Scripts` |
| Windows | `%PROGRAMDATA%\Blackmagic Design\DaVinci Resolve\Fusion\Scripts` | `%APPDATA%\Roaming\Blackmagic Design\DaVinci Resolve\Support\Fusion\Scripts` |
| Linux | `/opt/resolve/Fusion/Scripts` | `~/.local/share/DaVinciResolve/Fusion/Scripts` |

Subdirectories: `Utility/` (all pages), `Edit/`, `Color/`, `Deliver/`, `Comp/`, `Tool/` (Fusion page).

### 1.4 Headless Mode

```bash
# Launch Resolve without UI (API still works)
"/Applications/DaVinci Resolve/DaVinci Resolve.app/Contents/MacOS/Resolve" -nogui
```

---

## 2. Connecting to Resolve

### 2.1 Basic Connection

```python
import DaVinciResolveScript as dvr_script

resolve = dvr_script.scriptapp("Resolve")
if not resolve:
    print("ERROR: Could not connect. Is DaVinci Resolve Studio running?")
    exit(1)

print(f"Connected to Resolve {resolve.GetVersionString()}")
```

### 2.2 macOS Gotcha — LAN IP Binding

On macOS, Resolve often binds to the machine's LAN IP instead of `127.0.0.1`. If `scriptapp("Resolve")` returns `None`:

```python
def connect_resolve():
    """Connect to Resolve, handling macOS LAN IP binding."""
    import DaVinciResolveScript as dvr_script

    # Try default connection first
    resolve = dvr_script.scriptapp("Resolve")
    if resolve:
        return resolve

    # macOS: discover via pinghosts
    if sys.platform == "darwin":
        hosts = dvr_script.pinghosts('')
        if hosts:
            for _id, info in hosts.items():
                ip = info.get('IP', '')
                if ip:
                    resolve = dvr_script.scriptapp("Resolve", ip)
                    if resolve:
                        print(f"Connected via {ip}")
                        return resolve

        # Fallback: try LAN IPs directly
        import subprocess
        result = subprocess.run(["ifconfig"], capture_output=True, text=True, timeout=5)
        for line in result.stdout.split('\n'):
            line = line.strip()
            if line.startswith('inet ') and '127.0.0.1' not in line and '169.254.' not in line:
                ip = line.split()[1]
                resolve = dvr_script.scriptapp("Resolve", ip)
                if resolve:
                    print(f"Connected via LAN IP {ip}")
                    return resolve

    return None
```

### 2.3 Connection with Timeout Protection

Resolve API calls can hang indefinitely if the IPC is unresponsive. Use threading to add timeouts:

```python
import threading

def call_with_timeout(func, timeout=5.0):
    """Run a Resolve API call with a timeout to prevent infinite hangs."""
    result = [None]
    error = [None]

    def run():
        try:
            result[0] = func()
        except Exception as e:
            error[0] = e

    t = threading.Thread(target=run, daemon=True)
    t.start()
    t.join(timeout=timeout)
    if t.is_alive():
        return None  # Timed out
    if error[0]:
        raise error[0]
    return result[0]

# Usage
resolve = call_with_timeout(lambda: dvr_script.scriptapp("Resolve"), timeout=10.0)
```

---

## 3. Object Model

The Resolve API is a hierarchy of objects. Each object exposes methods to query and manipulate its state.

```
Resolve
├── GetMediaStorage()        → MediaStorage
├── GetProjectManager()      → ProjectManager
│   ├── CreateProject()      → Project
│   ├── LoadProject()        → Project
│   └── GetCurrentProject()  → Project
│       ├── GetMediaPool()   → MediaPool
│       │   ├── GetRootFolder()       → Folder
│       │   │   ├── GetClipList()     → [MediaPoolItem]
│       │   │   └── GetSubFolderList()→ [Folder]
│       │   ├── ImportMedia()         → [MediaPoolItem]
│       │   ├── CreateEmptyTimeline() → Timeline
│       │   └── AppendToTimeline()    → [TimelineItem]
│       ├── GetCurrentTimeline()      → Timeline
│       │   ├── GetItemListInTrack()  → [TimelineItem]
│       │   ├── GetTrackCount()       → int
│       │   ├── AddTrack()
│       │   ├── Export()
│       │   └── GetSetting() / SetSetting()
│       ├── GetGallery()              → Gallery
│       ├── AddRenderJob()
│       ├── StartRendering()
│       ├── GetSetting() / SetSetting()
│       └── SetRenderSettings()
└── OpenPage("media"|"cut"|"edit"|"fusion"|"color"|"fairlight"|"deliver")
```

---

## 4. Project Management

### 4.1 Create / Load / Save

```python
project_manager = resolve.GetProjectManager()

# List projects
projects = project_manager.GetProjectListInCurrentFolder()
print(f"Projects: {projects}")

# Create new project
project = project_manager.CreateProject("MyProject")

# Load existing project
project = project_manager.LoadProject("MyProject")

# Get current project
project = project_manager.GetCurrentProject()
print(f"Current project: {project.GetName()}")

# Save
project_manager.SaveProject()

# Close without saving
project_manager.CloseProject(project)

# Delete (must not be the current project)
project_manager.DeleteProject("OldProject")
```

### 4.2 Project Folders

```python
# Navigate project database folders
project_manager.GotoRootFolder()
folders = project_manager.GetFolderListInCurrentFolder()
project_manager.OpenFolder("ClientWork")
project_manager.GotoParentFolder()
project_manager.CreateFolder("NewFolder")
```

### 4.3 Import / Export Projects

```python
# Import .drp file
project_manager.ImportProject("/path/to/project.drp", "ImportedProject")

# Export project (includes stills and LUTs by default)
project_manager.ExportProject("MyProject", "/path/to/export.drp", withStillsAndLUTs=True)

# Archive with media
project_manager.ArchiveProject("MyProject", "/path/to/archive.dra",
                                isArchiveSrcMedia=True,
                                isArchiveRenderCache=False,
                                isArchiveProxyMedia=False)
```

### 4.4 Database Management

```python
# Get current database info
db = project_manager.GetCurrentDatabase()
# Returns: {'DbType': 'Disk', 'DbName': 'Local Database'}

# List all databases
dbs = project_manager.GetDatabaseList()

# Switch database
project_manager.SetCurrentDatabase({
    'DbType': 'PostgreSQL',
    'DbName': 'SharedDB',
    'IpAddress': '192.168.1.100'
})
```

---

## 5. Project Settings

### 5.1 Reading and Writing Settings

```python
# Get ALL settings as a dict (useful for discovery)
all_settings = project.GetSetting()
for key, value in sorted(all_settings.items()):
    print(f"  {key}: {value}")

# Get specific setting
fps = project.GetSetting("timelineFrameRate")
color_science = project.GetSetting("colorScienceMode")

# Set settings (returns True on success)
project.SetSetting("timelineFrameRate", "24")
project.SetSetting("timelineResolutionWidth", "3840")
project.SetSetting("timelineResolutionHeight", "2160")
```

### 5.2 Key Project Settings

| Setting Key | Example Values | Notes |
|-------------|---------------|-------|
| `timelineFrameRate` | `"23.976"`, `"24"`, `"25"`, `"29.97 DF"`, `"30"` | Drop frame: append `" DF"` |
| `timelineResolutionWidth` | `"1920"`, `"3840"`, `"4096"` | |
| `timelineResolutionHeight` | `"1080"`, `"2160"` | |
| `colorScienceMode` | `"davinciYRGB"`, `"davinciYRGBColorManagedv2"`, `"ACEScct"` | Set first for color management |
| `superScale` | `0`=Auto, `1`=None, `2`=2x, `3`=3x, `4`=4x | |

### 5.3 HDR / Color Management Settings

**Critical:** Settings must be applied in a specific order. `colorScienceMode` must be set **first** to enable DaVinci Color Management, then the rest.

```python
# Complete Rec.2020 PQ HDR setup
hdr_settings = [
    # Step 1: Enable DaVinci Color Management (MUST be first)
    ("colorScienceMode",              "davinciYRGBColorManagedv2"),
    ("isAutoColorManage",             "0"),
    ("separateColorSpaceAndGamma",    "1"),
    # Step 2: Color spaces
    ("colorSpaceInput",               "Rec.2020"),
    ("colorSpaceInputGamma",          "ST2084"),
    ("colorSpaceTimeline",            "Rec.2020"),
    ("colorSpaceTimelineGamma",       "Rec.2100 ST2084"),
    ("colorSpaceOutput",              "Rec.2020"),
    ("colorSpaceOutputGamma",         "Rec.2100 ST2084"),
    # Step 3: HDR luminance
    ("timelineWorkingLuminanceMode",  "HDR 4000"),
    ("hdrMasteringLuminanceMax",      "4000"),
    ("hdrMasteringOn",                "1"),
    # Step 4: DRT (Display Rendering Transform)
    ("inputDRT",                      "None"),
    ("outputDRT",                     "None"),
]

import time
for key, value in hdr_settings:
    result = project.SetSetting(key, value)
    status = "OK" if result else "FAILED"
    print(f"  {status}: {key} = {value}")
    # Small delay after critical mode switches
    if key in ("colorScienceMode", "separateColorSpaceAndGamma"):
        time.sleep(0.1)
```

### 5.4 Tagging Clip Input Color Space

Resolve's API doesn't directly expose "Input Gamma" as a settable clip property. The workaround uses a combined/separate mode toggle:

```python
def tag_clip_color_space(project, clips, color_space, gamma):
    """Tag clips with correct Input Color Space + Gamma.

    Uses the combined-then-separate trick:
    1. Switch to combined mode
    2. Set a known combined IDT that carries the correct gamma
    3. Switch to separate mode
    4. Override the gamut — this preserves the gamma from step 2
    """
    # Map gamma to known combined IDTs
    gamma_idt_map = {
        "ST2084": "Rec.2100 ST2084",
        "Rec.2100 ST2084": "Rec.2100 ST2084",
        "HLG": "Rec.2100 HLG",
        "Gamma 2.4": "Rec.709 Gamma 2.4",
    }
    gamma_idt = gamma_idt_map.get(gamma, gamma)

    original_sep = project.GetSetting("separateColorSpaceAndGamma")

    # Step 1: Combined mode — set gamma via combined IDT
    project.SetSetting("separateColorSpaceAndGamma", "0")
    for clip in clips:
        clip.SetClipProperty('Input Color Space', gamma_idt)

    # Step 2: Separate mode — override gamut (preserves gamma)
    project.SetSetting("separateColorSpaceAndGamma", "1")
    tagged = 0
    for clip in clips:
        if clip.SetClipProperty('Input Color Space', color_space):
            tagged += 1

    # Restore original mode
    project.SetSetting("separateColorSpaceAndGamma", original_sep)
    return tagged
```

---

## 6. Media Pool Operations

### 6.1 Import Media

```python
media_pool = project.GetMediaPool()

# Import files (returns list of MediaPoolItems)
clips = media_pool.ImportMedia([
    "/path/to/video1.mov",
    "/path/to/video2.mov",
    "/path/to/audio.wav",
])
print(f"Imported {len(clips)} clips")

# Import image sequence
clips = media_pool.ImportMedia([{
    "FilePath": "/path/to/frames/image_%04d.exr",
    "StartIndex": 1001,
    "EndIndex": 1100,
}])

# Import from MediaStorage (volumes visible in Media page)
media_storage = resolve.GetMediaStorage()
volumes = media_storage.GetMountedVolumeList()
files = media_storage.GetFileList("/Volumes/Media/")
clips = media_storage.AddItemListToMediaPool(files)
```

### 6.2 Organize Media in Bins

```python
root = media_pool.GetRootFolder()
print(f"Root folder: {root.GetName()}")
print(f"Clips in root: {len(root.GetClipList())}")

# Create subfolder (bin)
footage_bin = media_pool.AddSubFolder(root, "Footage")
vfx_bin = media_pool.AddSubFolder(root, "VFX")

# Set current folder before importing
media_pool.SetCurrentFolder(footage_bin)
clips = media_pool.ImportMedia(["/path/to/footage.mov"])

# Move clips between folders
media_pool.MoveClips(clips, vfx_bin)

# List subfolders
for folder in root.GetSubFolderList():
    print(f"  Bin: {folder.GetName()} ({len(folder.GetClipList())} clips)")
```

### 6.3 Clip Properties

```python
clip = clips[0]

# Get all properties (useful for discovery)
all_props = clip.GetClipProperty()
for key, value in sorted(all_props.items()):
    print(f"  {key}: {value}")

# Key properties
print(clip.GetClipProperty("File Path"))
print(clip.GetClipProperty("Resolution"))
print(clip.GetClipProperty("FPS"))
print(clip.GetClipProperty("Frames"))
print(clip.GetClipProperty("Duration"))
print(clip.GetClipProperty("Start TC"))

# Set properties
clip.SetClipProperty("Clip Name", "MyClip")
clip.SetClipProperty("Input Color Space", "Rec.2020")
clip.SetClipProperty("FPS", "25.0")           # Reinterpret frame rate
clip.SetClipProperty("Alpha mode", "None")     # Ignore alpha channel
clip.SetClipProperty("Super Scale", 2)         # 2x upscale

# Metadata
clip.SetMetadata("Scene", "001")
clip.SetMetadata("Shot", "A")
scene = clip.GetMetadata("Scene")
all_meta = clip.GetMetadata()  # Returns dict

# Markers on clip
clip.AddMarker(24, "Green", "Mark1", "Note here", 1)  # frameId, color, name, note, duration
markers = clip.GetMarkers()  # {frameId: {color, name, note, duration, customData}}

# Flags
clip.AddFlag("Blue")
flags = clip.GetFlagList()
clip.ClearFlags("All")
```

### 6.4 Relinking Media

```python
# Relink clips to a new folder (useful when media moves)
media_pool.RelinkClips(clips, "/new/path/to/media/")

# Unlink clips
media_pool.UnlinkClips(clips)

# Replace underlying media for a clip
clip.ReplaceClip("/path/to/replacement.mov")
```

---

## 7. Timeline Operations

### 7.1 Create Timelines

```python
media_pool = project.GetMediaPool()

# Empty timeline
timeline = media_pool.CreateEmptyTimeline("MyTimeline")

# Timeline from clips (auto-appends)
timeline = media_pool.CreateTimelineFromClips("AutoTimeline", clips)

# Timeline from clips with placement info
timeline = media_pool.CreateTimelineFromClips("PlacedTimeline", [{
    "mediaPoolItem": clip,
    "startFrame": 0,
    "endFrame": 100,
    "recordFrame": 0,
}])

# Import timeline from file (XML, AAF, EDL, FCPXML, OTIO)
timeline = media_pool.ImportTimelineFromFile("/path/to/timeline.xml", {
    "timelineName": "ImportedTimeline",
    "importSourceClips": True,
    "sourceClipsPath": "/path/to/media/",  # Fallback search path
})

# Set as current timeline
project.SetCurrentTimeline(timeline)
```

### 7.2 Navigate Timelines

```python
# List all timelines
count = project.GetTimelineCount()
for i in range(1, count + 1):
    tl = project.GetTimelineByIndex(i)
    print(f"  [{i}] {tl.GetName()}")

# Get current
timeline = project.GetCurrentTimeline()
print(f"Current: {timeline.GetName()}")
print(f"Start frame: {timeline.GetStartFrame()}")
print(f"End frame: {timeline.GetEndFrame()}")
print(f"Start timecode: {timeline.GetStartTimecode()}")

# Set start timecode
timeline.SetStartTimecode("01:00:00:00")
```

### 7.3 Timeline Settings

```python
# Get all timeline settings
settings = timeline.GetSetting()

# Key settings
timeline.GetSetting("timelineResolutionWidth")
timeline.GetSetting("timelineResolutionHeight")
timeline.GetSetting("timelineFrameRate")
```

### 7.4 Tracks

```python
# Count tracks
video_tracks = timeline.GetTrackCount("video")
audio_tracks = timeline.GetTrackCount("audio")
subtitle_tracks = timeline.GetTrackCount("subtitle")

# Add tracks
timeline.AddTrack("video")                              # Add video track
timeline.AddTrack("audio", "stereo")                     # Add stereo audio track
timeline.AddTrack("audio", {"audioType": "5.1", "index": 2})  # Insert 5.1 at position 2
timeline.AddTrack("subtitle")

# Track names
for i in range(1, video_tracks + 1):
    name = timeline.GetTrackName("video", i)
    print(f"  V{i}: {name}")

timeline.SetTrackName("video", 1, "Master")
timeline.SetTrackName("video", 2, "Composited Shots")

# Enable/disable, lock/unlock
timeline.SetTrackEnable("video", 2, True)
timeline.SetTrackLock("video", 1, True)
is_enabled = timeline.GetIsTrackEnabled("video", 2)
is_locked = timeline.GetIsTrackLocked("video", 1)

# Delete track
timeline.DeleteTrack("video", 3)
```

### 7.5 Place Clips on Timeline

```python
# Simple append (adds to end of timeline)
items = media_pool.AppendToTimeline(clips)

# Append with specific placement
items = media_pool.AppendToTimeline([{
    "mediaPoolItem": clip,
    "startFrame": 0,             # Source in-point (frame within the clip)
    "endFrame": 100,             # Source out-point
    "trackIndex": 2,             # Video track (1-based)
    "recordFrame": 500,          # Position on timeline (frame number)
    "mediaType": 1,              # 1 = Video only, 2 = Audio only
}])

# Place audio on a specific track
media_pool.AppendToTimeline([{
    "mediaPoolItem": audio_clip,
    "startFrame": 0,
    "endFrame": audio_clip.GetClipProperty("Frames"),
    "trackIndex": 1,             # Audio track index
    "recordFrame": 0,
    "mediaType": 2,              # Audio only
}])
```

### 7.6 Read Timeline Items

```python
# Get all clips on a track
v1_clips = timeline.GetItemListInTrack("video", 1)
a1_clips = timeline.GetItemListInTrack("audio", 1)

for item in v1_clips:
    print(f"  {item.GetName()}")
    print(f"    Start: {item.GetStart()}")
    print(f"    End: {item.GetEnd()}")
    print(f"    Duration: {item.GetDuration()}")

    # Get source media info
    mp_item = item.GetMediaPoolItem()
    if mp_item:
        props = mp_item.GetClipProperty()
        print(f"    File: {props.get('File Path', 'N/A')}")
```

### 7.7 Timeline Item Properties (Transform, Crop, Composite)

```python
item = v1_clips[0]

# Get all properties
all_props = item.GetProperty()

# Transform
item.SetProperty("Pan", 100.0)         # Horizontal position
item.SetProperty("Tilt", -50.0)        # Vertical position
item.SetProperty("ZoomX", 110.0)       # Horizontal scale (100 = 100%)
item.SetProperty("ZoomY", 110.0)       # Vertical scale
item.SetProperty("RotationAngle", 15.0)

# Crop (in pixels)
item.SetProperty("CropTop", 120.0)
item.SetProperty("CropBottom", 120.0)
item.SetProperty("CropLeft", 0.0)
item.SetProperty("CropRight", 0.0)
item.SetProperty("CropSoftness", 0.0)
item.SetProperty("CropRetain", True)   # Retain image position

# Composite
item.SetProperty("Opacity", 80.0)      # 0.0 to 100.0
item.SetProperty("CompositeMode", 0)   # 0 = Normal (see full list below)

# Scaling
item.SetProperty("Scaling", 2)         # 0=Project, 1=Crop, 2=Fit, 3=Fill, 4=Stretch

# Retime
item.SetProperty("RetimeProcess", 3)   # 0=Project, 1=Nearest, 2=Frame Blend, 3=Optical Flow

# Flip
item.SetProperty("FlipX", True)
item.SetProperty("FlipY", False)

# Enable/disable clip
item.SetClipEnabled(False)
print(item.GetClipEnabled())
```

**Composite Mode Constants:**

| Value | Mode | Value | Mode |
|-------|------|-------|------|
| 0 | Normal | 14 | Exclusion |
| 1 | Add | 15 | Hue |
| 2 | Subtract | 16 | Saturate |
| 3 | Difference | 17 | Colorize |
| 4 | Multiply | 18 | Luma Mask |
| 5 | Screen | 19 | Divide |
| 6 | Overlay | 20 | Linear Dodge |
| 7 | Hard Light | 21 | Linear Burn |
| 8 | Soft Light | 22 | Linear Light |
| 9 | Darken | 23 | Vivid Light |
| 10 | Lighten | 24 | Pin Light |
| 11 | Color Dodge | 25 | Hard Mix |
| 12 | Color Burn | 26 | Lighter Color |
| 13 | Exclusion | 27 | Darker Color |

### 7.8 Markers on Timeline

```python
# Add marker (frameId is relative to timeline start)
timeline.AddMarker(100, "Blue", "Scene Start", "Beginning of scene 2", 1)
timeline.AddMarker(200, "Red", "Fix Audio", "Audio sync issue here", 1, "custom_id_123")

# Read markers
markers = timeline.GetMarkers()
# Returns: {100: {'color': 'Blue', 'duration': 1.0, 'note': '...', 'name': '...', 'customData': ''}, ...}

# Find marker by custom data
marker = timeline.GetMarkerByCustomData("custom_id_123")

# Update custom data
timeline.UpdateMarkerCustomData(200, "updated_data")

# Delete markers
timeline.DeleteMarkerAtFrame(100)
timeline.DeleteMarkersByColor("Blue")   # Delete all blue markers
timeline.DeleteMarkersByColor("All")     # Delete ALL markers
```

### 7.9 Delete / Link / Compound Clips

```python
# Delete clips (ripple delete with second arg True)
timeline.DeleteClips([item1, item2], True)

# Link/unlink clips
timeline.SetClipsLinked([video_item, audio_item], True)   # Link
timeline.SetClipsLinked([video_item, audio_item], False)  # Unlink

# Create compound clip
compound = timeline.CreateCompoundClip([item1, item2], {
    "startTimecode": "01:00:00:00",
    "name": "Compound Clip 1"
})

# Duplicate timeline
new_timeline = timeline.DuplicateTimeline("Timeline Copy")
```

---

## 8. Timecode Utilities

```python
def timecode_to_frames(timecode: str, fps: float) -> int:
    """Convert 'HH:MM:SS:FF' timecode to absolute frame number."""
    parts = timecode.split(":")
    if len(parts) != 4:
        raise ValueError(f"Invalid timecode: {timecode}")
    h, m, s, f = map(int, parts)
    return (h * 3600 + m * 60 + s) * round(fps) + f

def frames_to_timecode(frames: int, fps: float) -> str:
    """Convert absolute frame number to 'HH:MM:SS:FF' timecode."""
    nominal_fps = round(fps)
    f = frames % nominal_fps
    total_seconds = frames // nominal_fps
    s = total_seconds % 60
    total_seconds //= 60
    m = total_seconds % 60
    h = total_seconds // 60
    return f"{h:02d}:{m:02d}:{s:02d}:{f:02d}"
```

---

## 9. Rendering

### 9.1 Render Formats and Codecs

```python
# List available formats
formats = project.GetRenderFormats()
# Returns: {'mov': 'mov', 'mp4': 'mp4', 'mxf': 'mxf', ...}

# List codecs for a format
codecs = project.GetRenderCodecs("mov")
# Returns: {'Apple ProRes 422 HQ': 'ProRes422HQ', 'Apple ProRes 4444 XQ': 'ProRes4444XQ', ...}

# Get current format/codec
current = project.GetCurrentRenderFormatAndCodec()
# Returns: {'format': 'mov', 'codec': 'ProRes422HQ'}

# Set format and codec
project.SetCurrentRenderFormatAndCodec("mov", "ProRes4444XQ")
```

### 9.2 Render Settings

```python
project.SetRenderSettings({
    "SelectAllFrames": True,        # Render entire timeline (ignores MarkIn/MarkOut)
    "TargetDir": "/path/to/output",
    "CustomName": "my_render",       # Filename without extension
    "ExportVideo": True,
    "ExportAudio": True,
    "FormatWidth": 3840,
    "FormatHeight": 2160,
    "FrameRate": 24.0,
    "AudioCodec": "aac",
    "AudioBitDepth": 24,
    "AudioSampleRate": 48000,
    "ColorSpaceTag": "Same as Project",
    "GammaTag": "Same as Project",
    "ExportAlpha": False,
    "NetworkOptimization": True,
})

# Render a specific frame range
project.SetRenderSettings({
    "SelectAllFrames": False,
    "MarkIn": 100,                   # Start frame
    "MarkOut": 500,                  # End frame
    "TargetDir": "/path/to/output",
    "CustomName": "shot_001",
})
```

### 9.3 Render Queue Workflow

```python
# 1. Configure render settings
project.SetCurrentRenderFormatAndCodec("mov", "ProRes422HQ")
project.SetRenderSettings({
    "SelectAllFrames": True,
    "TargetDir": "/output/",
    "CustomName": "final_render",
})

# 2. Add to render queue (returns job ID)
job_id = project.AddRenderJob()
print(f"Job ID: {job_id}")

# 3. Start rendering
project.StartRendering([job_id])
# Or start ALL queued jobs:
# project.StartRendering()

# 4. Monitor progress
import time
while project.IsRenderingInProgress():
    status = project.GetRenderJobStatus(job_id)
    pct = status.get("CompletionPercentage", 0)
    job_status = status.get("JobStatus", "Unknown")
    eta = status.get("EstimatedTimeRemainingInMs", 0)
    print(f"  {job_status}: {pct}% (ETA: {eta/1000:.0f}s)", end="\r")
    time.sleep(1.0)

# 5. Check final status
status = project.GetRenderJobStatus(job_id)
if status["JobStatus"] == "Complete":
    ms = status.get("TimeTakenToRenderInMs", 0)
    print(f"Render complete in {ms/1000:.1f}s")
elif status["JobStatus"] == "Failed":
    print(f"Render failed: {status.get('Error', 'Unknown')}")

# 6. Clean up
project.DeleteRenderJob(job_id)
# Or: project.DeleteAllRenderJobs()
```

### 9.4 Batch Rendering Multiple Segments

```python
# Render individual shots from a timeline
shots = [
    {"name": "shot_001", "mark_in": 0,   "mark_out": 100},
    {"name": "shot_002", "mark_in": 101, "mark_out": 250},
    {"name": "shot_003", "mark_in": 251, "mark_out": 400},
]

# Switch to Deliver page
resolve.OpenPage("deliver")
time.sleep(0.5)

# Clear previous jobs
project.DeleteAllRenderJobs()

# Set format once
project.SetCurrentRenderFormatAndCodec("mov", "ProRes4444XQ")

for shot in shots:
    project.SetRenderSettings({
        "SelectAllFrames": False,
        "MarkIn": shot["mark_in"],
        "MarkOut": shot["mark_out"],
        "TargetDir": "/output/shots/",
        "CustomName": shot["name"],
    })
    job_id = project.AddRenderJob()
    if not job_id:
        print(f"  FAILED to queue: {shot['name']}")
        continue

    # Render one at a time (more reliable than batch)
    project.StartRendering([job_id])
    while project.IsRenderingInProgress():
        s = project.GetRenderJobStatus(job_id)
        print(f"  {shot['name']}: {s.get('CompletionPercentage', 0)}%", end="\r")
        time.sleep(0.5)

    status = project.GetRenderJobStatus(job_id)
    if status["JobStatus"] == "Complete":
        print(f"  {shot['name']}: Complete")
    else:
        print(f"  {shot['name']}: FAILED - {status.get('Error', '?')}")

    project.DeleteRenderJob(job_id)
    time.sleep(0.3)  # Give Resolve time to clean up
```

### 9.5 Render Presets

```python
# List presets
presets = project.GetRenderPresetList()
print(presets)  # ['ProRes Master', 'H.264 Master', ...]

# Load a preset
project.LoadRenderPreset("ProRes Master")

# Save current settings as preset
project.SaveAsNewRenderPreset("My HDR Preset")

# Import/export presets
resolve.ImportRenderPreset("/path/to/preset.xml")
resolve.ExportRenderPreset("My HDR Preset", "/path/to/export.xml")
```

### 9.6 Burn-In Presets

```python
# Import a data burn-in preset (timecode, clip name, etc.)
resolve.ImportBurnInPreset("/path/to/Proxy_BurnIn.xml")

# Load burn-in preset for project
project.LoadBurnInPreset("Proxy_BurnIn")

# Load burn-in preset for specific clip
timeline_item.LoadBurnInPreset("Proxy_BurnIn")
```

### 9.7 Quick Export

```python
# List Quick Export presets
presets = project.GetQuickExportRenderPresets()

# Render with Quick Export
result = project.RenderWithQuickExport("YouTube - 1080p", {
    "TargetDir": "/output/",
    "CustomName": "youtube_export",
    "EnableUpload": False,
})
```

---

## 10. Timeline Export

### 10.1 Export Formats

```python
# Export constants (accessed via the resolve object)
# resolve.EXPORT_AAF, resolve.EXPORT_EDL, resolve.EXPORT_FCP_7_XML, etc.

# Export EDL
timeline.Export("/path/to/output.edl", resolve.EXPORT_EDL, resolve.EXPORT_NONE)

# Export FCP 7 XML
timeline.Export("/path/to/output.xml", resolve.EXPORT_FCP_7_XML, resolve.EXPORT_NONE)

# Export FCPXML 1.10
timeline.Export("/path/to/output.fcpxml", resolve.EXPORT_FCPXML_1_10, resolve.EXPORT_NONE)

# Export AAF (new)
timeline.Export("/path/to/output.aaf", resolve.EXPORT_AAF, resolve.EXPORT_AAF_NEW)

# Export CSV
timeline.Export("/path/to/output.csv", resolve.EXPORT_TEXT_CSV, resolve.EXPORT_NONE)

# Export OTIO (OpenTimelineIO)
timeline.Export("/path/to/output.otio", resolve.EXPORT_OTIO, resolve.EXPORT_NONE)
```

**All Export Types:**

| Constant | Format |
|----------|--------|
| `EXPORT_AAF` | AAF (requires subtype: `EXPORT_AAF_NEW` or `EXPORT_AAF_EXISTING`) |
| `EXPORT_DRT` | DaVinci Resolve Timeline |
| `EXPORT_EDL` | Edit Decision List (subtypes: `EXPORT_CDL`, `EXPORT_SDL`, `EXPORT_MISSING_CLIPS`, `EXPORT_NONE`) |
| `EXPORT_FCP_7_XML` | Final Cut Pro 7 XML |
| `EXPORT_FCPXML_1_8` | FCPXML 1.8 |
| `EXPORT_FCPXML_1_9` | FCPXML 1.9 |
| `EXPORT_FCPXML_1_10` | FCPXML 1.10 |
| `EXPORT_TEXT_CSV` | CSV |
| `EXPORT_TEXT_TAB` | Tab-separated |
| `EXPORT_OTIO` | OpenTimelineIO |
| `EXPORT_ALE` | Avid Log Exchange |
| `EXPORT_ALE_CDL` | ALE with CDL |
| `EXPORT_HDR_10_PROFILE_A` | HDR10+ Profile A |
| `EXPORT_HDR_10_PROFILE_B` | HDR10+ Profile B |
| `EXPORT_DOLBY_VISION_VER_2_9` | Dolby Vision 2.9 |
| `EXPORT_DOLBY_VISION_VER_4_0` | Dolby Vision 4.0 |
| `EXPORT_DOLBY_VISION_VER_5_1` | Dolby Vision 5.1 |

---

## 11. Fusion Scripting

```python
# Access Fusion
fusion = resolve.Fusion()

# Create Fusion composition on a timeline item
comp = timeline_item.AddFusionComp()
comp_count = timeline_item.GetFusionCompCount()
comp = timeline_item.GetFusionCompByIndex(1)

# List compositions
comp_names = timeline_item.GetFusionCompNameList()
comp = timeline_item.GetFusionCompByName("Composition 1")

# Import/export compositions
timeline_item.ImportFusionComp("/path/to/comp.setting")
timeline_item.ExportFusionComp("/path/to/export.setting", 1)

# Create Fusion clip from timeline items
fusion_clip = timeline.CreateFusionClip([item1, item2])
```

---

## 12. Color Grading

### 12.1 Node Graph

```python
# Get node graph
graph = timeline_item.GetNodeGraph()
# Or with layer index:
# graph = timeline_item.GetNodeGraph(1)

num_nodes = graph.GetNumNodes()

# Set LUT on a node (1-based index)
graph.SetLUT(1, "/path/to/lut.cube")
lut_path = graph.GetLUT(1)

# Node labels
label = graph.GetNodeLabel(1)

# Enable/disable nodes
graph.SetNodeEnabled(1, True)

# Tools in node
tools = graph.GetToolsInNode(1)

# Apply grade from DRX
graph.ApplyGradeFromDRX("/path/to/grade.drx", 0)  # 0=No keyframes, 1=Timecode, 2=Start
graph.ResetAllGrades()

# Node cache
graph.SetNodeCacheMode(1, -1)  # -1=Auto, 0=Disabled, 1=Enabled
```

### 12.2 CDL (Color Decision List)

```python
timeline_item.SetCDL({
    "NodeIndex": "1",
    "Slope": "0.5 0.4 0.2",
    "Offset": "0.4 0.3 0.2",
    "Power": "0.6 0.7 0.8",
    "Saturation": "0.65"
})
```

### 12.3 Color Versions

```python
# Add version (0=local, 1=remote)
timeline_item.AddVersion("Grade v2", 0)

# List versions
versions = timeline_item.GetVersionNameList(0)  # Local versions

# Load specific version
timeline_item.LoadVersionByName("Grade v2", 0)

# Get current
current = timeline_item.GetCurrentVersion()
# Returns: {'versionName': 'Grade v2', 'versionType': 0}

# Rename
timeline_item.RenameVersionByName("Grade v2", "Final Grade", 0)

# Copy grades to other clips
timeline_item.CopyGrades([other_item1, other_item2])
```

### 12.4 Color Groups

```python
# Create group
group = project.AddColorGroup("VFX Shots")

# List groups
groups = project.GetColorGroupsList()

# Assign clip to group
timeline_item.AssignToColorGroup(group)

# Get group
clip_group = timeline_item.GetColorGroup()

# Get clips in group for this timeline
clips_in_group = group.GetClipsInTimeline()

# Pre/Post clip node graphs
pre_graph = group.GetPreClipNodeGraph()
post_graph = group.GetPostClipNodeGraph()

# Remove from group
timeline_item.RemoveFromColorGroup()
```

---

## 13. Gallery / Stills

```python
gallery = project.GetGallery()

# Albums
albums = gallery.GetGalleryStillAlbums()
current_album = gallery.GetCurrentStillAlbum()
new_album = gallery.CreateGalleryStillAlbum()
gallery.SetAlbumName(new_album, "VFX References")
gallery.SetCurrentStillAlbum(new_album)

# Grab stills from timeline
still = timeline.GrabStill()
all_stills = timeline.GrabAllStills(1)  # 1=First frame, 2=Middle frame

# Import/export stills
current_album.ImportStills(["/path/to/still.dpx"])
current_album.ExportStills(
    current_album.GetStills(),
    "/output/folder/",
    "still_",           # Filename prefix
    "png"               # Format: dpx, cin, tif, jpg, png, ppm, bmp, xpm, drx
)

# Labels
still = current_album.GetStills()[0]
current_album.SetLabel(still, "Hero Shot Reference")
label = current_album.GetLabel(still)

# Delete
current_album.DeleteStills([still])

# PowerGrade albums
pg_albums = gallery.GetGalleryPowerGradeAlbums()
new_pg = gallery.CreateGalleryPowerGradeAlbum()
```

---

## 14. Audio Features

### 14.1 Audio Sync

```python
# Auto-sync audio to video (requires at least 1 video + 1 audio clip)
media_pool.AutoSyncAudio([video_clip, audio_clip], {
    resolve.AUDIO_SYNC_MODE: resolve.AUDIO_SYNC_WAVEFORM,
    resolve.AUDIO_SYNC_CHANNEL_NUMBER: resolve.AUDIO_SYNC_CHANNEL_AUTOMATIC,
    resolve.AUDIO_SYNC_RETAIN_EMBEDDED_AUDIO: True,
    resolve.AUDIO_SYNC_RETAIN_VIDEO_METADATA: True,
})
```

### 14.2 Voice Isolation

```python
# Get voice isolation state for audio track
state = timeline.GetVoiceIsolationState(1)  # Track index
# Returns: {'isEnabled': True, 'amount': 50}

# Set voice isolation
timeline.SetVoiceIsolationState(1, {'isEnabled': True, 'amount': 75})

# Per timeline item
item_state = timeline_item.GetVoiceIsolationState()
```

### 14.3 Audio Mapping

```python
# Get audio channel mapping info
mapping_json = clip.GetAudioMapping()
import json
mapping = json.loads(mapping_json)
print(f"Embedded channels: {mapping['embedded_audio_channels']}")
print(f"Linked audio: {mapping.get('linked_audio', {})}")
print(f"Track mapping: {mapping.get('track_mapping', {})}")
```

### 14.4 Fairlight

```python
# Get Fairlight presets
presets = resolve.GetFairlightPresets()

# Apply to current timeline
project.ApplyFairlightPresetToCurrentTimeline("Dialog Cleanup")

# Insert audio at playhead (Fairlight page)
project.InsertAudioToCurrentTrackAtPlayhead(
    "/path/to/audio.wav",
    startOffsetInSamples=0,
    durationInSamples=48000 * 10  # 10 seconds at 48kHz
)
```

---

## 15. Subtitles / Auto Caption

```python
# Create subtitles from audio
timeline.CreateSubtitlesFromAudio({
    resolve.SUBTITLE_LANGUAGE: resolve.AUTO_CAPTION_ENGLISH,
    resolve.SUBTITLE_CAPTION_PRESET: resolve.AUTO_CAPTION_SUBTITLE_DEFAULT,
    resolve.SUBTITLE_CHARS_PER_LINE: 42,
    resolve.SUBTITLE_LINE_BREAK: resolve.AUTO_CAPTION_LINE_SINGLE,
    resolve.SUBTITLE_GAP: 0,
})

# Available languages:
# AUTO_CAPTION_AUTO, AUTO_CAPTION_ENGLISH, AUTO_CAPTION_FRENCH, AUTO_CAPTION_GERMAN,
# AUTO_CAPTION_SPANISH, AUTO_CAPTION_ITALIAN, AUTO_CAPTION_JAPANESE, AUTO_CAPTION_KOREAN,
# AUTO_CAPTION_MANDARIN_SIMPLIFIED, AUTO_CAPTION_MANDARIN_TRADITIONAL,
# AUTO_CAPTION_PORTUGUESE, AUTO_CAPTION_RUSSIAN, AUTO_CAPTION_DANISH,
# AUTO_CAPTION_DUTCH, AUTO_CAPTION_NORWEGIAN, AUTO_CAPTION_SWEDISH

# Presets: AUTO_CAPTION_SUBTITLE_DEFAULT, AUTO_CAPTION_TELETEXT, AUTO_CAPTION_NETFLIX
```

---

## 16. Scene Detection

```python
# Detect scene cuts along the timeline
success = timeline.DetectSceneCuts()
```

---

## 17. Practical Patterns

### 17.1 Build a Multi-Track Timeline from Scratch

```python
def build_timeline(project, name, master_video, overlay_clips, audio_stems, fps=24.0):
    """Build a timeline: V1=master, V2=overlay clips at timecodes, A1+=audio stems."""
    media_pool = project.GetMediaPool()

    # Import all media
    all_paths = [str(master_video)]
    all_paths.extend(str(c['path']) for c in overlay_clips)
    all_paths.extend(str(s) for s in audio_stems)

    imported = media_pool.ImportMedia(all_paths)
    if not imported:
        raise RuntimeError("Failed to import media")

    # Build clip lookup by filename
    clip_lookup = {}
    for clip in imported:
        props = clip.GetClipProperty()
        if props:
            from pathlib import Path
            clip_lookup[Path(props["File Path"]).name] = clip

    # Create empty timeline
    timeline = media_pool.CreateEmptyTimeline(name)
    project.SetCurrentTimeline(timeline)
    timeline.SetStartTimecode("00:00:00:00")

    # V1: Master video (full length)
    master_clip = clip_lookup[master_video.name]
    media_pool.AppendToTimeline([{
        "mediaPoolItem": master_clip,
        "startFrame": 0,
        "endFrame": int(master_clip.GetClipProperty("Frames")) - 1,
        "trackIndex": 1,
        "recordFrame": timeline.GetStartFrame(),
        "mediaType": 1,
    }])

    # Ensure V2 exists
    if timeline.GetTrackCount("video") < 2:
        timeline.AddTrack("video")

    # V2: Overlay clips at specific timecodes
    for clip_info in overlay_clips:
        clip = clip_lookup.get(clip_info['path'].name)
        if not clip:
            continue
        start_frame = timecode_to_frames(clip_info['timecode'], fps)
        frames = int(clip.GetClipProperty("Frames"))
        media_pool.AppendToTimeline([{
            "mediaPoolItem": clip,
            "startFrame": 0,
            "endFrame": frames - 1,
            "trackIndex": 2,
            "recordFrame": timeline.GetStartFrame() + start_frame,
            "mediaType": 1,
        }])

    # Audio stems
    for i, stem in enumerate(audio_stems, 1):
        stem_clip = clip_lookup.get(stem.name)
        if not stem_clip:
            continue
        if i > timeline.GetTrackCount("audio"):
            timeline.AddTrack("audio", "stereo")
        frames = int(stem_clip.GetClipProperty("Frames"))
        media_pool.AppendToTimeline([{
            "mediaPoolItem": stem_clip,
            "startFrame": 0,
            "endFrame": frames - 1,
            "trackIndex": i,
            "recordFrame": timeline.GetStartFrame(),
            "mediaType": 2,
        }])

    return timeline
```

### 17.2 Detect Offline Media

```python
def check_offline_media(timeline):
    """Check for offline/missing clips in timeline."""
    from pathlib import Path
    problems = []
    total = 0
    for track_idx in range(1, timeline.GetTrackCount("video") + 1):
        items = timeline.GetItemListInTrack("video", track_idx)
        if not items:
            continue
        for item in items:
            total += 1
            mp_item = item.GetMediaPoolItem()
            if not mp_item:
                problems.append((item.GetName(), "No media pool item"))
                continue
            props = mp_item.GetClipProperty()
            if not props:
                problems.append((item.GetName(), "No properties"))
                continue
            file_path = props.get("File Path", "")
            if not file_path or not Path(file_path).exists():
                problems.append((item.GetName(), f"Missing: {file_path}"))

    return {"total": total, "offline": problems}
```

### 17.3 Strip Alpha Channels

Some clips (e.g., VFX renders from Nuke) have alpha channels that Resolve composites as transparent. Set alpha mode to None after import:

```python
def strip_alpha(clips):
    """Set alpha mode to None on all clips to prevent transparency issues."""
    count = 0
    for clip in clips:
        if clip.SetClipProperty('Alpha mode', 'None'):
            count += 1
    return count
```

### 17.4 Conform Clip FPS

When clips have a different FPS than the timeline, Resolve stretches/compresses them. Reinterpret to match:

```python
def conform_fps(clips, target_fps):
    """Reinterpret clips to match timeline FPS."""
    target = f"{target_fps:.1f}"
    count = 0
    for clip in clips:
        props = clip.GetClipProperty()
        if props and str(props.get('FPS', '')) != target:
            if clip.SetClipProperty('FPS', target):
                count += 1
    return count
```

### 17.5 Letterbox Crop

Apply a letterbox crop to clips on upper tracks:

```python
def apply_letterbox(timeline, target_aspect_ratio, tracks=None):
    """Crop V2+ clips for letterbox at target AR (e.g., 2.39 for scope)."""
    tl_w = int(timeline.GetSetting("timelineResolutionWidth"))
    tl_h = int(timeline.GetSetting("timelineResolutionHeight"))

    target_h = tl_w / target_aspect_ratio
    crop_total = tl_h - target_h
    if crop_total <= 0:
        return 0

    crop_px = round(crop_total / 2)

    if tracks is None:
        tracks = range(2, timeline.GetTrackCount("video") + 1)

    count = 0
    for t in tracks:
        items = timeline.GetItemListInTrack("video", t) or []
        for item in items:
            top = item.SetProperty('CropTop', float(crop_px))
            bot = item.SetProperty('CropBottom', float(crop_px))
            if top and bot:
                count += 1

    return count
```

### 17.6 Export LUT from Timeline Item

```python
# Export LUT (17pt, 33pt, or 65pt cube, or Panasonic VLUT)
timeline_item.ExportLUT(resolve.EXPORT_LUT_33PTCUBE, "/path/to/output.cube")

# Constants:
# resolve.EXPORT_LUT_17PTCUBE
# resolve.EXPORT_LUT_33PTCUBE
# resolve.EXPORT_LUT_65PTCUBE
# resolve.EXPORT_LUT_PANASONICVLUT
```

---

## 18. Complete Example: End-to-End Workflow

```python
#!/usr/bin/env python3
"""Example: Create project, import media, build timeline, render."""
import os, sys, time
from pathlib import Path

# Setup environment
def setup():
    if sys.platform == "darwin":
        api = "/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting/"
        lib = "/Applications/DaVinci Resolve/DaVinci Resolve.app/Contents/Libraries/Fusion/fusionscript.so"
    elif sys.platform == "win32":
        api = os.path.join(os.environ.get("PROGRAMDATA", ""), "Blackmagic Design", "DaVinci Resolve", "Support", "Developer", "Scripting")
        lib = os.path.join(os.environ.get("PROGRAMFILES", ""), "Blackmagic Design", "DaVinci Resolve", "fusionscript.dll")
    else:
        api = "/opt/resolve/Developer/Scripting/"
        lib = "/opt/resolve/libs/Fusion/fusionscript.so"
    os.environ.setdefault("RESOLVE_SCRIPT_API", api)
    os.environ.setdefault("RESOLVE_SCRIPT_LIB", lib)
    modules = os.path.join(os.environ["RESOLVE_SCRIPT_API"], "Modules")
    if modules not in sys.path:
        sys.path.insert(0, modules)

setup()
import DaVinciResolveScript as dvr_script

# Connect
resolve = dvr_script.scriptapp("Resolve")
if not resolve:
    print("ERROR: Cannot connect to Resolve. Is it running?")
    sys.exit(1)

pm = resolve.GetProjectManager()

# Create or load project
project_name = "AutomatedProject"
project = pm.LoadProject(project_name) or pm.CreateProject(project_name)
if not project:
    print(f"ERROR: Cannot create/load project '{project_name}'")
    sys.exit(1)

# Set project settings
project.SetSetting("timelineFrameRate", "24")
project.SetSetting("timelineResolutionWidth", "1920")
project.SetSetting("timelineResolutionHeight", "1080")

# Import media
media_pool = project.GetMediaPool()
media_pool.SetCurrentFolder(media_pool.GetRootFolder())
clips = media_pool.ImportMedia([
    "/path/to/video.mov",
    "/path/to/audio.wav",
])

if not clips:
    print("ERROR: No clips imported")
    sys.exit(1)

# Create timeline
timeline = media_pool.CreateEmptyTimeline("Main Timeline")
project.SetCurrentTimeline(timeline)

# Add video to V1
video_clip = clips[0]
media_pool.AppendToTimeline([{
    "mediaPoolItem": video_clip,
    "startFrame": 0,
    "endFrame": int(video_clip.GetClipProperty("Frames")) - 1,
    "trackIndex": 1,
    "recordFrame": timeline.GetStartFrame(),
    "mediaType": 1,
}])

# Add audio to A1
audio_clip = clips[1]
media_pool.AppendToTimeline([{
    "mediaPoolItem": audio_clip,
    "startFrame": 0,
    "endFrame": int(audio_clip.GetClipProperty("Frames")) - 1,
    "trackIndex": 1,
    "recordFrame": timeline.GetStartFrame(),
    "mediaType": 2,
}])

# Render
resolve.OpenPage("deliver")
time.sleep(0.5)

project.SetCurrentRenderFormatAndCodec("mov", "ProRes422HQ")
project.SetRenderSettings({
    "SelectAllFrames": True,
    "TargetDir": "/path/to/output/",
    "CustomName": "final_output",
    "ExportVideo": True,
    "ExportAudio": True,
})

job_id = project.AddRenderJob()
project.StartRendering([job_id])

while project.IsRenderingInProgress():
    s = project.GetRenderJobStatus(job_id)
    print(f"  Rendering: {s.get('CompletionPercentage', 0)}%", end="\r")
    time.sleep(1.0)

status = project.GetRenderJobStatus(job_id)
print(f"\nResult: {status['JobStatus']}")

project.DeleteRenderJob(job_id)
pm.SaveProject()
print("Done!")
```

---

## 19. Troubleshooting

| Problem | Solution |
|---------|----------|
| `scriptapp("Resolve")` returns `None` | Ensure Resolve **Studio** is running. Check env vars. On macOS, try LAN IP connection (section 2.2). |
| `SetSetting()` returns `False` | Setting may be read-only when timelines exist, or the value string is wrong. Use `GetSetting()` with no args to dump all valid keys. |
| `CreateEmptyTimeline()` returns `None` | Timeline name may already exist. Check `GetTimelineCount()` / iterate. |
| `ImportMedia()` returns empty list | File path may be wrong, or format unsupported. Check path exists. |
| `AppendToTimeline()` doesn't place at recordFrame | Ensure the timeline is set as current (`SetCurrentTimeline`). The `recordFrame` is an absolute frame position from the timeline start. |
| `SetClipProperty('Input Color Space', ...)` fails | Value must match exactly what Resolve shows in the dropdown. Use combined/separate mode trick for gamma (section 5.4). |
| Render fails silently | Switch to Deliver page (`OpenPage("deliver")`) before configuring renders. Add a `time.sleep(0.5)` after page switch. |
| Clips appear stretched/compressed | FPS mismatch — reinterpret clip FPS to match timeline (section 17.4). |
| VFX clips appear transparent | Alpha channel — set `'Alpha mode'` to `'None'` after import (section 17.3). |
| HDR settings don't apply | Apply `colorScienceMode` **first**, wait 100ms, then apply the rest in order (section 5.3). |
| API calls hang forever | Use threaded timeout wrapper (section 2.3). Common on macOS when Resolve's IPC is unresponsive. |

---

## 20. API Version Notes

- **v16.2+**: Node indices are 1-based (not 0-based).
- **v18.1+**: FCPXML versions 1.3–1.7 are no longer supported for export.
- **v20.3**: Current API version. Adds `GetTimelineByName()` (may not be available in all builds — use index iteration as fallback).
- **Studio only**: The scripting API is **not available** in the free version of DaVinci Resolve.

---

## Appendix: Quick Reference Card

### Connection Boilerplate
```python
import DaVinciResolveScript as dvr_script
resolve = dvr_script.scriptapp("Resolve")
pm = resolve.GetProjectManager()
project = pm.GetCurrentProject()
media_pool = project.GetMediaPool()
timeline = project.GetCurrentTimeline()
```

### Common One-Liners
```python
# Current project name
project.GetName()

# Timeline duration in frames
timeline.GetEndFrame() - timeline.GetStartFrame()

# Number of clips on V1
len(timeline.GetItemListInTrack("video", 1) or [])

# Import single file
media_pool.ImportMedia(["/path/to/file.mov"])

# Switch page
resolve.OpenPage("color")

# Export EDL
timeline.Export("/out.edl", resolve.EXPORT_EDL, resolve.EXPORT_NONE)

# Resolve version
resolve.GetVersionString()
```
