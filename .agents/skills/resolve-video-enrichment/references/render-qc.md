# Resolve render and deliverable QC

## Windows ResolvePython connection

Use the bundled interpreter and module path:

```bash
"C:/Program Files/Blackmagic Design/DaVinci Resolve/ResolvePython/ResolvePython.exe" -c "import sys; sys.path.append(r'C:/Program Files/Blackmagic Design/DaVinci Resolve/ResolvePython/lib/modules'); import DaVinciResolveScript as d; r=d.scriptapp('Resolve'); print(r.GetProductName(), r.GetVersionString())"
```

## Pin and queue a web MP4

Probe first:

```python
formats = project.GetRenderFormats() or {}
mp4_id = formats.get("MP4", formats.get("mp4", "mp4"))
codecs = project.GetRenderCodecs(mp4_id) or {}
```

Then pin state instead of relying on the Deliver page:

```python
project.LoadRenderPreset("H.264 Master")
project.SetCurrentRenderFormatAndCodec("mp4", "H264")
project.SetRenderSettings({
    "TargetDir": output_dir,
    "CustomName": output_basename,
    "SelectAllFrames": True,
    "ExportVideo": True,
    "ExportAudio": True,
    "FormatWidth": 1920,
    "FormatHeight": 1080,
    "FrameRate": 60.0,
})
job_id = project.AddRenderJob()
project.StartRendering([job_id], False)
```

Check every return value. If `SetRenderSettings` refuses a payload, probe the keys in small groups and remove the rejected key rather than silently falling back to inherited state.

## Output checks

```bash
ffprobe -v error -print_format json -show_format -show_streams \
  "<rendered-file>.mp4"
ffmpeg -y -ss <overlay-time> -i "<rendered-file>.mp4" \
  -frames:v 1 -q:v 2 "<scratch>/render-check.jpg" -hide_banner -loglevel error
```

Assert:

- Resolve render job status is `Complete`.
- The file exists and is non-empty.
- There is an H.264 video stream at the intended raster and frame rate.
- There is an AAC or project-approved audio stream.
- Duration and frame count match the target timeline within normal container rounding.
- The extracted frame visibly contains both the base footage and the inserted overlay.

Do not claim a render is verified from the queue status alone; the output file and a visual frame are the authoritative checks.

## Batch visual proof

For a batch, keep one reviewed overlay timestamp per timeline. Extract one frame from each output at its own cue, then assemble a numbered contact sheet and inspect it before declaring the batch complete. Every cell must show base footage plus the intended overlay, with no `Media Offline` composite; a single successful render is not evidence for the other timelines.
