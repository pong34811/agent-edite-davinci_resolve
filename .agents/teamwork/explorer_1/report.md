# DaVinci Resolve Environment, Live Project Status, and Backup Investigation Report

**Date**: 2026-10-01  
**Investigator**: Explorer 1 (`teamwork_preview_explorer`)  
**Target Project**: `KT404_2026-09-29` (Project ID: `7c38045b-c9ae-426c-8b4c-2e2d726d88ff`)  
**Working Directory**: `C:\Users\warit\Desktop\agent-edite-davinci_resolve\.agents\teamwork\explorer_1`

---

## 1. Executive Summary

A comprehensive, non-destructive investigation was conducted on the DaVinci Resolve host environment, active project parameters, backup destination filesystem, `.drp` export mechanisms, and UI state restoration capabilities.

Key findings:
1. **DaVinci Resolve Connection & Project State**:
   - DaVinci Resolve Studio 21.1.0.17 is currently running with GUI active (`headless: false`, 1 instance).
   - Project `KT404_2026-09-29` is open in the active session. Its unique ID `7c38045b-c9ae-426c-8b4c-2e2d726d88ff` exactly matches the project context.
   - The project contains exactly 30 edited 16:9 timelines.
   - Project defaults: 1920x1080 @ 60.0 fps, `timelinePlaybackFrameRate: 60`, `colorScienceMode: davinciYRGB`, Rec.709 color management.
2. **Backup Destination & Export Methods**:
   - Destination folder `G:\My Drive\Projects\Katy404\2026-09-29` exists with 392.6 GB free space.
   - 5 previous `.drp` backups exist in the folder (ranging from 1.26 MB to 1.82 MB), along with source footage and captions.
   - Project export API: `ProjectManager.ExportProject(name, path, withStillsAndLUTs)` via native API or MCP actions (`export_project` or `safe_project_export` with `allow_non_mcp_name=True, require_temp_path=False`).
   - Critical API invariant: `ExportProject` snapshots the **saved database state**. `ProjectManager.SaveProject()` must precede any export to prevent exporting empty tracks.
   - DRP verification: Validated that `.drp` files are standard zip archives containing `project.xml` and `MediaPool` structure. CRC32 validation via `zipfile.ZipFile.testzip()` and header validation confirmed working.
3. **UI State Restoration**:
   - Both MCP (`resolve_control` `save_state` / `restore_state`) and native API (`OpenPage`, `SetCurrentTimeline`, `SetCurrentTimecode`) were verified live. State restoration successfully returned the exact page, active timeline, and playhead position (`01:00:45:41`).

---

## 2. DaVinci Resolve Connection and Project State

### 2.1 Process and Runtime Inspection
- **Application**: DaVinci Resolve Studio
- **Version String**: `21.1.0.17` (Product Version: `[21, 1, 0, 17, ""]`)
- **Process Path**: `C:\Program Files\Blackmagic Design\DaVinci Resolve\Resolve.exe`
- **Runtime Mode**: GUI mode (`running: true`, `headless: false`, `instances: 1`)
- **Database Backend**: Disk database named `"google drive"` (`database_attached: true`)
- **MCP Version**: 4.8.23

### 2.2 Active Project Details
- **Project Name**: `KT404_2026-09-29`
- **Project Unique ID**: `7c38045b-c9ae-426c-8b4c-2e2d726d88ff`
- **Current Active Page**: `edit`
- **Current Active Timeline**: `หนีฝ่าความหนาว_Minecraft-vdo` (Timeline ID: `7dcaea9a-b19f-4fa4-ac24-9a4f8c12f3ff`, Index: 26)
- **Current Active Timecode**: `01:00:45:41`
- **Total Timelines**: 30 (all 16:9 horizontal cuts)
- **Media Pool Statistics**:
  - Folders: 9 bins (including `000_Shorts_2026-09-29`, `Fun`, `Gameplay`, `Meme`, `Archive`, `Enrichment_SFX`, `Enrichment_BGM`, `Enrichment_GIF`)
  - Clips: 139 total (Video + Audio: 7, Subtitle: 2, Video: 82, Timeline: 30, Audio: 18)

### 2.3 Project Settings & Baseline Configuration
Queried live via `project_settings.get_setting`:

| Parameter | Setting Value | Notes |
|---|---|---|
| `timelineResolutionWidth` | `1920` | Base horizontal width |
| `timelineResolutionHeight` | `1080` | Base horizontal height |
| `timelineOutputResolutionWidth` | `1920` | Base output width |
| `timelineOutputResolutionHeight` | `1080` | Base output height |
| `timelineOutputResMatchTimelineRes` | `1` | Timeline output tracks timeline res |
| `timelinePixelAspectRatio` | `square` | Square pixels (1:1) |
| `timelineFrameRate` | `60.0` | 60 fps base frame rate |
| `timelinePlaybackFrameRate` | `60` | 60 fps playback rate |
| `timelineDropFrameTimecode` | `0` | Non-drop frame |
| `timelineSampleRate` | `48000` | 48 kHz standard broadcast audio |
| `colorScienceMode` | `davinciYRGB` | DaVinci YRGB color science |
| `colorSpaceInput` | `Rec.709 Gamma 2.4` | Input color space |
| `colorSpaceTimeline` | `Rec.709 (Scene)` | Timeline working color space |
| `colorSpaceOutput` | `Rec.709 (Scene)` | Output color space |
| `colorSpaceOutputGamma` | `ACEScc` | Output gamma |
| `isAutoColorManage` | `0` (Project default) | Note: Individual timelines have custom settings enabled |

### 2.4 Active Timeline Settings (`หนีฝ่าความหนาว_Minecraft-vdo`)
Queried live via `timeline.get_setting`:
- `useCustomSettings`: `1` (Overrides project defaults)
- `timelineResolutionWidth`: `1920`
- `timelineResolutionHeight`: `1080`
- `timelineFrameRate`: `60.0`
- `isAutoColorManage`: `1`
- `rcmPresetMode`: `SDR`
- `start_frame`: `216000` (`01:00:00:00`)
- `end_frame`: `221880` (`01:01:38:00`, duration: 5880 frames = 98.0 seconds)

### 2.5 Inventory of 30 Existing 16:9 Timelines
1. `ขุดมั่วเจอเหล็กกองใหญ่_Minecraft-vdo` (`67402c28-d713-4383-8e5e-f4a77b782e95`)
2. `คุยกับเพื่อนตั้งนาน ลืมเอาเสียงเข้าไลฟ์_Minecraft-vdo` (`1890f171-5727-4b23-ab56-35a09b1c83aa`)
3. `ลืมเสบียง จนต้องกินเนื้อซอมบี้_Minecraft-vdo` (`f838a8b1-9c7a-46cc-b0b1-f974b56af4ce`)
4. `ครีปเปอร์ระเบิดข้างกรง แต่กรงยังรอด_Minecraft-vdo` (`c69f0411-082d-4c4f-8e07-884e41837676`)
5. `เห็นแร่จนสงสัยว่าตัวเองมีเอกซเรย์_Minecraft-vdo` (`ad24db80-bcd5-4d6e-98e5-04941ffb5ac1`)
6. `ออกหาตัวละคร วนกลับมาบ้านตัวเอง_Minecraft-vdo` (`2a0ede66-757f-456c-8ca9-312e0dcb8779`)
7. `ต้องพายเรือ หรือหิ้วเรือขึ้นเขา_Minecraft-vdo` (`9cc3753a-2112-44ca-ac15-d5a74e982458`)
8. `พาชาวบ้านกลับฐาน รอดมาได้ตัวเดียว_Minecraft-vdo` (`2a240ed1-fe12-42a6-bb77-d8c3824794c6`)
9. `ชวนชาวบ้านเพิ่มประชากร ขนมปังหายครึ่งกอง_Minecraft-vdo` (`0f9c6773-8a5c-4130-ac6b-ea94d3e151a8`)
10. `ทำฟาร์มในหิมะ น้ำแข็งจนต้องทำหลังคา_Minecraft-vdo` (`e3dd6481-3ecf-4cf1-9968-c9df3e92b427`)
11. `ชวนเพื่อนไม่ได้ เพราะเผลอแบล็กลิสต์กัน_Soul Walker-vdo` (`9b5d48f6-b67b-497a-b150-8c363997a396`)
12. `เสียงสะท้อนสยองขวัญ_Soul Walker-vdo` (`6f32a58d-7b2f-482f-b88a-cc6c82de94e4`)
13. `กองทัพโอลด์วัน_Terraria-vdo` (`22b4148e-4a98-487f-8577-9c1deac5cdb0`)
14. `แพ้มูนลอร์ด_Terraria-vdo` (`f6f0bbec-5284-4369-a9c3-30a7de25bbd8`)
15. `ปราบมูนลอร์ดได้ครั้งแรก_Terraria-vdo` (`88805d14-956c-4779-976a-bc32bf38dced`)
16. `ปราบมูนลอร์ดได้ครั้งที่สอง_Terraria-vdo` (`ffb1e33d-7268-415f-a8a8-66618458ff28`)
17. `คืนจันทร์ฟักทอง_Terraria-vdo` (`fbefcba3-de86-4ba3-9d3f-a21568c99b56`)
18. `ตัวละครโผล่ตอนสู้บอส_Terraria-vdo` (`6f1418ba-61c1-4157-9793-7891ff51e050`)
19. `สุ่มปี่สก็อตเหล็ก_Monster Hunter World-vdo` (`0ce22811-d88c-4613-b62c-3c6924e1f6cf`)
20. `เกรตจากราส_Monster Hunter World-vdo` (`e35ac859-8b4a-478c-b74b-8b6dca82c79c`)
21. `คูลูยาคู_Monster Hunter World-vdo` (`f80c2653-4399-434a-a825-7f3d6e0cc33f`)
22. `พูเคพูเค_Monster Hunter World-vdo` (`9cdee07e-9c72-4181-95b9-dab9a2e16d41`)
23. `บาร์รอธ_Monster Hunter World-vdo` (`f37f103f-a3a9-4cec-9dbf-f8637c375efe`)
24. `จูราทอดัส_Monster Hunter World-vdo` (`a593dd7b-bbb2-4c73-a3a8-22dc815c92d5`)
25. `บอสมังกร_Soul Walker-vdo` (`454c59dd-6b7e-4ee4-96fd-c829f001bde1`)
26. `หนีฝ่าความหนาว_Minecraft-vdo` (`7dcaea9a-b19f-4fa4-ac24-9a4f8c12f3ff`)
27. `ปราบโกเล็มสำเร็จ_Soul Walker-vdo` (`d4b0f036-a62f-4afd-ba12-6683acda13fc`)
28. `นับถอยหลังในห้องโล่_Soul Walker-vdo` (`8018e46d-7e6d-496c-9136-965f8d31f66d`)
29. `เคลียร์เมืองนรก_Soul Walker-vdo` (`c76cc38b-a830-46b7-bd12-bb2c256e9c38`)
30. `โดนบอสจับจนต้องใช้ท่าพิเศษสองครั้ง_Soul Walker-vdo` (`98005c12-e4b5-48c7-ae32-f43bdacd3f0a`)

---

## 3. Backup Destination and Export Methods

### 3.1 Filesystem Check
- **Destination Folder**: `G:\My Drive\Projects\Katy404\2026-09-29`
- **Status**: Directory exists, accessible, writable.
- **Drive Free Space**: 392.62 GB available on `G:`.
- **Existing Files & Subdirectories**:
  - `Captions/` (directory)
  - `KT404_2026-09-29_pre_enrichment.drp` (1,262,735 bytes, 2026-09-30 23:40:01)
  - `KT404_2026-09-29_before_main_update_2026-10-01.drp` (1,817,251 bytes, 2026-10-01 13:46:20)
  - `KT404_2026-09-29_before_dragon_alignment_2026-10-01.drp` (1,290,687 bytes, 2026-10-01 14:07:41)
  - `KT404_2026-09-29_pre_gif_trim_2026-10-01.drp` (1,269,182 bytes, 2026-10-01 14:56:03)
  - `KT404_2026-09-29_post_gif_trim_pre_archive_cleanup_2026-10-01.drp` (1,333,123 bytes, 2026-10-01 15:16:44)
  - 7 source MP4 stream recordings (each 3.9 GB - 6.4 GB)
  - `desktop.ini`

### 3.2 Backup Naming Recommendation
Following the existing project convention, the pre-mutation backup should be named:
`KT404_2026-09-29_pre_vertical_conversion_2026-10-01.drp`
or
`KT404_2026-09-29_pre_9x16_conversion_2026-10-01.drp`

### 3.3 Project Export API Commands & Critical Invariant

#### Critical Invariant (`api_truth`):
> `ExportProject` snapshots the **saved database state**. If a project has unsaved changes, an export will reflect the older saved state or export empty tracks.
> **Therefore**: Always execute `ProjectManager.SaveProject()` immediately before calling `ExportProject`.

#### API Methods:
1. **Direct MCP Call** (Recommended):
   ```json
   {
     "server": "davinci-resolve",
     "tool": "project_manager",
     "action": "export_project",
     "params": {
       "name": "KT404_2026-09-29",
       "path": "G:\\My Drive\\Projects\\Katy404\\2026-09-29\\KT404_2026-09-29_pre_9x16_conversion_2026-10-01.drp",
       "with_stills_and_luts": true
     }
   }
   ```
2. **Safe MCP Wrapper Call**:
   ```json
   {
     "server": "davinci-resolve",
     "tool": "project_manager",
     "action": "safe_project_export",
     "params": {
       "name": "KT404_2026-09-29",
       "path": "G:\\My Drive\\Projects\\Katy404\\2026-09-29\\KT404_2026-09-29_pre_9x16_conversion_2026-10-01.drp",
       "allow_non_mcp_name": true,
       "require_temp_path": false,
       "with_stills_and_luts": true
     }
   }
   ```
   *Note: In `server.py`, `_safe_project_export` guards project names (must start with `_mcp_` unless `allow_non_mcp_name=True`) and file paths (must be in temp unless `require_temp_path=False`). Both flags must be explicitly supplied if using `safe_project_export`.*

3. **Native Python Scripting Bridge**:
   ```python
   pm = resolve.GetProjectManager()
   saved = pm.SaveProject()
   assert saved, "SaveProject failed prior to export"
   success = pm.ExportProject(
       "KT404_2026-09-29",
       r"G:\My Drive\Projects\Katy404\2026-09-29\KT404_2026-09-29_pre_9x16_conversion_2026-10-01.drp",
       True
   )
   ```

### 3.4 DRP File Integrity Verification Method
A DaVinci Resolve `.drp` file is a ZIP archive containing XML and metadata records.
We tested real `.drp` archives from the target folder and identified the following verification facts:
- `project.xml` contains hex-serialized `FieldsBlob` records that can fail standard strict XML parsers (`xml.etree.ElementTree.ParseError: not well-formed (invalid token)`).
- The root element header `<SM_Project DbId="...">` is plain text UTF-8 and contains the exact Project ID (`7c38045b-c9ae-426c-8b4c-2e2d726d88ff`).
- `zipfile.ZipFile.testzip()` computes CRC32 checksums of every compressed member and returns `None` if uncorrupted.

#### Automated Integrity Verification Procedure (Python):
```python
import os
import zipfile

def verify_drp_integrity(file_path: str, expected_project_id: str = "7c38045b-c9ae-426c-8b4c-2e2d726d88ff") -> dict:
    if not os.path.exists(file_path):
        return {"valid": False, "error": f"File does not exist: {file_path}"}
    
    size = os.path.getsize(file_path)
    if size < 500_000: # Project has 30 timelines; expected size is 1.2MB - 1.8MB
        return {"valid": False, "error": f"File size unexpectedly small: {size} bytes"}
    
    if not zipfile.is_zipfile(file_path):
        return {"valid": False, "error": "File is not a valid zip archive"}
    
    with zipfile.ZipFile(file_path, 'r') as z:
        bad_file = z.testzip()
        if bad_file:
            return {"valid": False, "error": f"CRC32 checksum mismatch on member: {bad_file}"}
        
        namelist = z.namelist()
        if "project.xml" not in namelist:
            return {"valid": False, "error": "Archive missing project.xml"}
        
        info = z.getinfo("project.xml")
        if info.file_size < 10_000:
            return {"valid": False, "error": f"project.xml uncompressed size too small: {info.file_size} bytes"}
        
        # Read header to confirm Project ID
        header = z.read("project.xml")[:1000].decode("utf-8", errors="ignore")
        if expected_project_id not in header:
            return {"valid": False, "error": f"project.xml DbId mismatch (expected {expected_project_id})"}
        
        # Confirm MediaPool folder structure exists
        has_mediapool = any("MediaPool" in n for n in namelist)
        if not has_mediapool:
            return {"valid": False, "error": "Archive missing MediaPool folder structure"}
            
        return {
            "valid": True,
            "size_bytes": size,
            "total_files": len(namelist),
            "project_xml_bytes": info.file_size,
            "has_mediapool": True
        }
```
*Live validation result on `KT404_2026-09-29_post_gif_trim_pre_archive_cleanup_2026-10-01.drp`:*  
`{'valid': True, 'size_bytes': 1333123, 'total_files': 43, 'project_xml_bytes': 293432, 'has_mediapool': True}`

---

## 4. Project Save and UI State Restoration APIs

### 4.1 Project Save API
- **MCP Tool**: `project_manager(action="save")`
  - Implementation in `server.py`: `return {"success": bool(pm.SaveProject())}`
- **Native Resolve API**:
  - `pm = resolve.GetProjectManager()`
  - `success = pm.SaveProject()`
  - Returns `True` on success. (Note: returns `False` for unsaved default 'Untitled Project', but `KT404_2026-09-29` is an established, named project).

### 4.2 UI State Restoration Procedures
Resolve UI state restoration is critical so that after automated operations, the user returns to the exact same page, timeline, playhead timecode, and media pool bin.

#### Tested MCP State Snapshot Mechanism:
1. **Capture State**:
   - Tool call: `resolve_control(action="save_state")`
   - Output observed:
     - `state_token`: `"ed4c426032bd"`
     - `page`: `"edit"`
     - `current_timeline_id`: `"7dcaea9a-b19f-4fa4-ac24-9a4f8c12f3ff"`
     - `current_timeline_name`: `"หนีฝ่าความหนาว_Minecraft-vdo"`
     - `current_timecode`: `"01:00:45:41"`
     - `current_folder_name`: `"Fun"`
2. **Restore State**:
   - Tool call: `resolve_control(action="restore_state", params={"state_token": "ed4c426032bd"})`
   - Verified live execution time: 276 ms.
   - Result:
     ```json
     {
       "success": true,
       "state_token": "ed4c426032bd",
       "restored": {
         "page": "edit",
         "current_timeline_id": "7dcaea9a-b19f-4fa4-ac24-9a4f8c12f3ff",
         "current_timecode": "01:00:45:41"
       }
     }
     ```

#### Native Python Implementation Reference:
When scripting directly outside the MCP state manager:
```python
# --- CAPTURE ---
saved_page = resolve.GetCurrentPage()
saved_timeline = project.GetCurrentTimeline()
saved_tl_id = saved_timeline.GetUniqueId() if saved_timeline else None
saved_timecode = saved_timeline.GetCurrentTimecode() if saved_timeline else None

# --- RESTORE ---
# 1. Restore Page
resolve.OpenPage(saved_page)
import time
for _ in range(10):
    if resolve.GetCurrentPage() == saved_page:
        break
    time.sleep(0.1)

# 2. Restore Active Timeline
if saved_tl_id:
    count = project.GetTimelineCount()
    for i in range(1, count + 1):
        tl = project.GetTimelineByIndex(i)
        if tl and tl.GetUniqueId() == saved_tl_id:
            project.SetCurrentTimeline(tl)
            break

# 3. Restore Playhead Timecode
if saved_timecode:
    curr_tl = project.GetCurrentTimeline()
    if curr_tl:
        curr_tl.SetCurrentTimecode(saved_timecode)
```

---

## 5. Timeline Duplication & 9:16 Configuration Protocol

For downstream implementation agents, the timeline duplication mechanism was also inspected:
1. `timeline(action="duplicate", params={"name": "<OriginalName>_9x16"})` calls native `tl.DuplicateTimeline(name)`.
   - Duplicates all video tracks (V1 gameplay, V2 GIFs, V3 adjustment clips), native Subtitle track, audio tracks (A1 dialogue, A2 BGM, A3 SFX), and markers.
   - Leaves the original horizontal timeline 100% untouched.
2. Custom settings on duplicated timeline:
   - `timeline.set_setting(name="useCustomSettings", value="1")`
   - `timeline.set_setting(name="timelineResolutionWidth", value="1080")`
   - `timeline.set_setting(name="timelineResolutionHeight", value="1920")`
   - `timeline.set_setting(name="timelineOutputResolutionWidth", value="1080")`
   - `timeline.set_setting(name="timelineOutputResolutionHeight", value="1920")`
   - Matching frame rate: `60.0` (inherits from source timeline).
